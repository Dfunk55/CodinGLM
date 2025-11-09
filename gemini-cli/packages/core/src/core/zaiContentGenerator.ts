/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  GenerateContentResponse,
  type Candidate,
  type Content,
  type ContentUnion,
  type CountTokensParameters,
  type CountTokensResponse,
  type EmbedContentParameters,
  type EmbedContentResponse,
  FinishReason,
  FunctionCallingConfigMode,
  type GenerateContentConfig,
  type GenerateContentParameters,
  type Part,
  type Tool,
  type ToolListUnion,
} from '@google/genai';
import { toContents } from '../code_assist/converter.js';
import { partToString } from '../utils/partUtils.js';
import type { ContentGenerator } from './contentGenerator.js';

const DEFAULT_BASE_URL = 'https://api.z.ai/api/paas/v4';
const CHAT_COMPLETIONS_PATH = '/chat/completions';

type ZaiMessageContentItem = {
  type?: string;
  text?: string;
  content?: string;
};

type ZaiToolCall = {
  id?: string;
  type?: string;
  function?: {
    name?: string;
    arguments?: string;
  };
};

type OpenAIChatMessage =
  | {
      role: 'system' | 'user' | 'assistant';
      content: string | Array<{ type: string; text?: string }>;
      tool_calls?: OpenAIToolCall[];
    }
  | {
      role: 'tool';
      tool_call_id?: string;
      name?: string;
      content: string;
    };

interface OpenAIToolCall {
  id?: string;
  type: 'function';
  function?: {
    name?: string;
    arguments?: string;
  };
}

interface ZaiChatCompletionResponse {
  id?: string;
  model?: string;
  created?: number;
  choices: ZaiChatCompletionChoice[];
  usage?: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
    tool_prompt_tokens?: number;
    thoughts_tokens?: number;
  };
}

interface ZaiChatCompletionChoice {
  index?: number;
  message?: {
    role?: string;
    content?: string | ZaiMessageContentItem[];
    reasoning_content?: ZaiMessageContentItem[];
    tool_calls?: ZaiToolCall[];
  };
  finish_reason?: string | null;
  logprobs?: Candidate['logprobsResult'];
}

interface ZaiChatCompletionChunkChoice {
  index?: number;
  delta?: {
    role?: string;
    content?: string | ZaiMessageContentItem[];
    reasoning_content?: ZaiMessageContentItem[];
    tool_calls?: ZaiToolCall[];
  };
  finish_reason?: string | null;
  logprobs?: Candidate['logprobsResult'];
}

interface ZaiChatCompletionChunk {
  id?: string;
  model?: string;
  created?: number;
  choices: ZaiChatCompletionChunkChoice[];
  usage?: ZaiChatCompletionResponse['usage'];
}

interface ZaiErrorResponse {
  error?: {
    message?: unknown;
  };
}

export interface ZaiContentGeneratorOptions {
  apiKey: string;
  baseUrl?: string;
  organization?: string;
  userAgent?: string;
}

export class ZaiContentGenerator implements ContentGenerator {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly organization?: string;
  private readonly userAgent?: string;

  constructor(options: ZaiContentGeneratorOptions) {
    if (!options.apiKey) {
      throw new Error('Z_AI_API_KEY is required when using the Z.AI provider.');
    }
    this.apiKey = options.apiKey;
    this.baseUrl = trimTrailingSlash(options.baseUrl ?? DEFAULT_BASE_URL);
    this.organization = options.organization;
    this.userAgent = options.userAgent;
  }

  async generateContent(
    request: GenerateContentParameters,
    userPromptId: string,
  ): Promise<GenerateContentResponse> {
    return this.invokeChatCompletion(request, userPromptId);
  }

  async generateContentStream(
    request: GenerateContentParameters,
    userPromptId: string,
  ): Promise<AsyncGenerator<GenerateContentResponse>> {
    return this.invokeChatCompletionStream(request, userPromptId);
  }

  async countTokens(
    request: CountTokensParameters,
  ): Promise<CountTokensResponse> {
    const contents = toContents(request.contents);
    const totalCharacters = contents
      .map((content) => collectTextFromContent(content).length)
      .reduce((acc, count) => acc + count, 0);
    const estimatedTokens = Math.max(1, Math.ceil(totalCharacters / 4));
    return {
      totalTokens: estimatedTokens,
    };
  }

  async embedContent(
    _request: EmbedContentParameters,
  ): Promise<EmbedContentResponse> {
    throw new Error('Z.AI provider does not support embedContent.');
  }

  private async invokeChatCompletion(
    request: GenerateContentParameters,
    userPromptId: string,
  ): Promise<GenerateContentResponse> {
    const body = this.buildRequestBody(request, userPromptId, false);
    const response = await fetch(this.buildEndpointUrl(), {
      method: 'POST',
      headers: this.buildHeaders(),
      body: JSON.stringify(body),
      signal: request.config?.abortSignal,
    });

    if (!response.ok) {
      const errorPayload = await safeReadJson(response);
      const errorMessage =
        typeof errorPayload?.error?.message === 'string'
          ? errorPayload.error.message
          : await response.text();
      throw new Error(
        `Z.AI API error (${response.status} ${response.statusText}): ${errorMessage}`,
      );
    }

    const json = (await response.json()) as ZaiChatCompletionResponse;
    return this.toGenerateContentResponse(json, request.model);
  }

  private async invokeChatCompletionStream(
    request: GenerateContentParameters,
    userPromptId: string,
  ): Promise<AsyncGenerator<GenerateContentResponse>> {
    const body = this.buildRequestBody(request, userPromptId, true);
    const response = await fetch(this.buildEndpointUrl(), {
      method: 'POST',
      headers: this.buildHeaders(),
      body: JSON.stringify(body),
      signal: request.config?.abortSignal,
    });

    if (!response.ok) {
      const errorPayload = await safeReadJson(response);
      const errorMessage =
        typeof errorPayload?.error?.message === 'string'
          ? errorPayload.error.message
          : await response.text();
      throw new Error(
        `Z.AI API error (${response.status} ${response.statusText}): ${errorMessage}`,
      );
    }

    const contentType = response.headers.get('content-type') ?? '';
    if (!contentType.includes('text/event-stream') || !response.body) {
      const json = (await response.json()) as ZaiChatCompletionResponse;
      const initial = this.toGenerateContentResponse(json, request.model);
      return (async function* (): AsyncGenerator<GenerateContentResponse> {
        yield initial;
      })();
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    const streamingState = new ZaiStreamingState();
    const toGenerateResponse = this.toGenerateContentResponse.bind(this);

    return (async function* (): AsyncGenerator<GenerateContentResponse> {
      let buffer = '';
      let streamClosed = false;
      while (!streamClosed) {
        const { value, done } = await reader.read();
        if (done) {
          buffer += decoder.decode();
          streamClosed = true;
        } else if (value) {
          buffer += decoder.decode(value, { stream: true });
        }

        let eventEnd = buffer.indexOf('\n\n');
        while (eventEnd !== -1) {
          const rawEvent = buffer.slice(0, eventEnd);
          buffer = buffer.slice(eventEnd + 2);
          const dataPayload = extractSseData(rawEvent);
          if (!dataPayload) {
            eventEnd = buffer.indexOf('\n\n');
            continue;
          }
          const trimmedPayload = dataPayload.trim();
          if (trimmedPayload === '[DONE]') {
            return;
          }

          let parsedChunk: ZaiChatCompletionChunk;
          try {
            parsedChunk = JSON.parse(trimmedPayload) as ZaiChatCompletionChunk;
          } catch (_error) {
            eventEnd = buffer.indexOf('\n\n');
            continue;
          }

          const aggregatedResponse = streamingState.applyChunk(
            parsedChunk,
            request.model,
          );
          yield toGenerateResponse(aggregatedResponse, request.model);

          eventEnd = buffer.indexOf('\n\n');
        }

        if (streamClosed) {
          const remainingData = buffer.trim();
          if (remainingData.length > 0) {
            const payload = extractSseData(`${remainingData}\n`);
            if (payload && payload.trim() !== '[DONE]') {
              try {
                const parsedChunk = JSON.parse(
                  payload.trim(),
                ) as ZaiChatCompletionChunk;
                const aggregatedResponse = streamingState.applyChunk(
                  parsedChunk,
                  request.model,
                );
                yield toGenerateResponse(aggregatedResponse, request.model);
              } catch (_error) {
                // Ignore trailing parse issues.
              }
            }
          }
        }
      }
    })();
  }

  private buildHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.apiKey}`,
    };

    if (this.organization) {
      headers['X-Organization'] = this.organization;
    }

    if (this.userAgent) {
      headers['User-Agent'] = this.userAgent;
    }

    return headers;
  }

  private buildEndpointUrl(): string {
    return `${this.baseUrl}${CHAT_COMPLETIONS_PATH}`;
  }

  private buildRequestBody(
    request: GenerateContentParameters,
    userPromptId: string,
    stream: boolean,
  ): Record<string, unknown> {
    const contents = toContents(request.contents);
    const messages: OpenAIChatMessage[] = [
      ...this.convertSystemInstruction(request.config),
      ...this.convertContents(contents),
    ];

    const config = request.config ?? {};
    const body: Record<string, unknown> = {
      model: request.model,
      messages,
      stream,
      user: userPromptId,
    };

    if (typeof config.temperature === 'number') {
      body['temperature'] = config.temperature;
    }
    if (typeof config.topP === 'number') {
      body['top_p'] = config.topP;
    }
    if (typeof config.topK === 'number') {
      body['top_k'] = config.topK;
    }
    if (typeof config.maxOutputTokens === 'number') {
      body['max_tokens'] = config.maxOutputTokens;
    }
    if (
      Array.isArray(config.stopSequences) &&
      config.stopSequences.length > 0
    ) {
      body['stop'] = config.stopSequences;
    }
    if (config.thinkingConfig) {
      body['thinking'] = config.thinkingConfig;
    }

    const tools = this.convertTools(config.tools);
    if (tools.length > 0) {
      body['tools'] = tools;
      const toolChoice = this.convertToolChoice(config.toolConfig);
      if (toolChoice) {
        body['tool_choice'] = toolChoice;
      }
    }

    return body;
  }

  private convertSystemInstruction(
    config?: GenerateContentConfig,
  ): OpenAIChatMessage[] {
    if (!config?.systemInstruction) {
      return [];
    }
    const text = convertContentUnionToText(config.systemInstruction);
    if (!text) {
      return [];
    }
    return [{ role: 'system', content: text }];
  }

  private convertContents(contents: Content[]): OpenAIChatMessage[] {
    const messages: OpenAIChatMessage[] = [];

    for (const content of contents) {
      if (!content?.parts || content.parts.length === 0) {
        continue;
      }

      const role = mapRole(content.role);
      const textParts = content.parts.filter(
        (part) => typeof part.text === 'string' && part.text.trim() !== '',
      );
      const functionCalls = content.parts.filter((part) => !!part.functionCall);
      const functionResponses = content.parts.filter(
        (part) => !!part.functionResponse,
      );

      if (textParts.length > 0) {
        messages.push({
          role,
          content: textParts.map((part) => ({ type: 'text', text: part.text })),
        });
      }

      if (functionCalls.length > 0) {
        messages.push({
          role: 'assistant',
          content: '',
          tool_calls: functionCalls.map((part, index) => {
            const id =
              (part.functionCall?.id ?? part.functionCall?.name)
                ? `${part.functionCall?.name}-${index}`
                : undefined;
            const args =
              part.functionCall?.args !== undefined
                ? stringifyArguments(part.functionCall.args)
                : '{}';
            return {
              id,
              type: 'function',
              function: {
                name: part.functionCall?.name,
                arguments: args,
              },
            };
          }),
        });
      }

      if (functionResponses.length > 0) {
        for (const responsePart of functionResponses) {
          const response = responsePart.functionResponse;
          messages.push({
            role: 'tool',
            tool_call_id:
              response?.id ??
              response?.name ??
              deriveToolCallId(functionCalls[0]?.functionCall?.id),
            name: response?.name,
            content: stringifyArguments(response?.response ?? {}),
          });
        }
      }
    }

    return messages;
  }

  private convertTools(toolList?: ToolListUnion): Array<{
    type: 'function';
    function: {
      name?: string;
      description?: string;
      parameters?: unknown;
    };
  }> {
    if (!toolList || !Array.isArray(toolList)) {
      return [];
    }

    const tools: Tool[] = toolList.filter(
      (tool): tool is Tool => 'functionDeclarations' in tool,
    );

    const declarations = tools.flatMap(
      (tool) => tool.functionDeclarations ?? [],
    );

    return declarations.map((fn) => ({
      type: 'function',
      function: {
        name: fn.name,
        description: fn.description,
        parameters: fn.parametersJsonSchema ?? fn.parameters,
      },
    }));
  }

  private convertToolChoice(
    toolConfig: GenerateContentConfig['toolConfig'],
  ): unknown {
    const config = toolConfig?.functionCallingConfig;
    if (!config) {
      return undefined;
    }

    if (config.mode === FunctionCallingConfigMode.NONE) {
      return 'none';
    }

    if (
      config.mode === FunctionCallingConfigMode.ANY ||
      config.mode === FunctionCallingConfigMode.VALIDATED ||
      config.mode === FunctionCallingConfigMode.AUTO ||
      config.mode === undefined
    ) {
      if (config.allowedFunctionNames && config.allowedFunctionNames.length) {
        if (config.allowedFunctionNames.length === 1) {
          return {
            type: 'function',
            function: { name: config.allowedFunctionNames[0] },
          };
        }
      }
      return 'auto';
    }

    return undefined;
  }

  private toGenerateContentResponse(
    payload: ZaiChatCompletionResponse,
    requestedModel: string,
  ): GenerateContentResponse {
    const response = new GenerateContentResponse();
    response.responseId = payload.id;
    response.modelVersion = payload.model ?? requestedModel;

    response.candidates = payload.choices.map((choice) => {
      const candidate: Candidate = {
        content: this.buildCandidateContent(choice),
        finishReason: mapFinishReason(choice.finish_reason),
        finishMessage: choice.finish_reason ?? undefined,
        index: choice.index,
        logprobsResult: choice.logprobs,
      };
      return candidate;
    });

    if (payload.usage) {
      response.usageMetadata = {
        promptTokenCount: payload.usage.prompt_tokens,
        candidatesTokenCount: payload.usage.completion_tokens,
        totalTokenCount: payload.usage.total_tokens,
        toolUsePromptTokenCount: payload.usage.tool_prompt_tokens,
        thoughtsTokenCount: payload.usage.thoughts_tokens,
      };
    }

    return response;
  }

  private buildCandidateContent(choice: ZaiChatCompletionChoice): Content {
    const parts: Part[] = [];
    const message = choice.message;
    if (message) {
      const content = message.content;
      if (typeof content === 'string') {
        if (content) {
          parts.push({ text: content });
        }
      } else if (Array.isArray(content)) {
        for (const item of content) {
          const text = item?.text ?? item?.content;
          if (text) {
            parts.push({ text });
          }
        }
      }

      if (Array.isArray(message.reasoning_content)) {
        for (const reasoning of message.reasoning_content) {
          const text = reasoning?.text ?? reasoning?.content;
          if (text) {
            parts.push({ text, thought: true });
          }
        }
      }

      if (Array.isArray(message.tool_calls)) {
        for (const call of message.tool_calls) {
          if (call?.type !== 'function') {
            continue;
          }
          let parsedArgs: Record<string, unknown> | undefined = undefined;
          if (call.function?.arguments) {
            parsedArgs = safeParseJson(call.function.arguments);
          }
          parts.push({
            functionCall: {
              id: call.id,
              name: call.function?.name,
              args: parsedArgs,
            },
          });
        }
      }
    }

    if (parts.length === 0) {
      parts.push({ text: '' });
    }

    return {
      role: 'model',
      parts,
    };
  }
}

interface StreamingChoiceState {
  index: number;
  role: string;
  content: ZaiMessageContentItem[];
  reasoning: ZaiMessageContentItem[];
  toolCalls: ZaiToolCall[];
  finishReason?: string | null;
  logprobs?: Candidate['logprobsResult'];
}

class ZaiStreamingState {
  private id?: string;
  private model?: string;
  private usage?: ZaiChatCompletionResponse['usage'];
  private readonly choices = new Map<number, StreamingChoiceState>();

  applyChunk(
    chunk: ZaiChatCompletionChunk,
    requestedModel: string,
  ): ZaiChatCompletionResponse {
    if (chunk.id) {
      this.id = chunk.id;
    }
    if (chunk.model) {
      this.model = chunk.model;
    }
    if (chunk.usage) {
      this.usage = chunk.usage;
    }

    for (const choice of chunk.choices ?? []) {
      const index = choice.index ?? 0;
      let state = this.choices.get(index);
      if (!state) {
        state = {
          index,
          role: 'assistant',
          content: [],
          reasoning: [],
          toolCalls: [],
        };
        this.choices.set(index, state);
      }

      if (choice.delta?.role) {
        state.role = choice.delta.role;
      }

      if (choice.delta?.content !== undefined) {
        state.content.push(...normalizeChunkContent(choice.delta.content));
      }

      if (choice.delta?.reasoning_content) {
        state.reasoning.push(
          ...normalizeChunkContent(choice.delta.reasoning_content),
        );
      }

      if (choice.delta?.tool_calls) {
        mergeToolCalls(state.toolCalls, choice.delta.tool_calls);
      }

      if (choice.finish_reason !== undefined) {
        state.finishReason = choice.finish_reason;
      }

      if (choice.logprobs) {
        state.logprobs = choice.logprobs;
      }
    }

    const aggregatedChoices: ZaiChatCompletionChoice[] = Array.from(
      this.choices.values(),
    ).map((state) => ({
      index: state.index,
      message: {
        role: state.role,
        content:
          state.content.length === 0
            ? ''
            : state.content.map((item) => ({ ...item })),
        reasoning_content:
          state.reasoning.length > 0
            ? state.reasoning.map((item) => ({ ...item }))
            : undefined,
        tool_calls:
          state.toolCalls.length > 0
            ? state.toolCalls.map((call) => cloneToolCall(call))
            : undefined,
      },
      finish_reason: state.finishReason ?? null,
      logprobs: state.logprobs,
    }));

    return {
      id: this.id,
      model: this.model ?? requestedModel,
      choices: aggregatedChoices,
      usage: this.usage,
    };
  }
}

function extractSseData(eventChunk: string): string | null {
  const lines = eventChunk.split('\n');
  const dataPayload: string[] = [];

  for (const line of lines) {
    if (line.startsWith(':') || line.trim() === '') {
      continue;
    }
    if (line.startsWith('data:')) {
      dataPayload.push(line.slice(5).trimStart());
    }
  }

  if (dataPayload.length === 0) {
    return null;
  }

  return dataPayload.join('\n');
}

function trimTrailingSlash(url: string): string {
  return url.endsWith('/') ? url.slice(0, -1) : url;
}

function mapRole(role?: string): 'user' | 'assistant' {
  if (role === 'model' || role === 'assistant') {
    return 'assistant';
  }
  return 'user';
}

function convertContentUnionToText(content: ContentUnion): string {
  if (typeof content === 'string') {
    return content;
  }
  if (Array.isArray(content)) {
    return partToString(content);
  }
  if ('parts' in content && Array.isArray(content.parts)) {
    return partToString(content.parts);
  }
  return '';
}

function collectTextFromContent(content: Content): string {
  if (!content.parts || content.parts.length === 0) {
    return '';
  }
  return content.parts
    .map((part) => {
      if (part.text) {
        return part.text;
      }
      if (part.functionCall) {
        return JSON.stringify(part.functionCall.args ?? {});
      }
      if (part.functionResponse) {
        return JSON.stringify(part.functionResponse.response ?? {});
      }
      return '';
    })
    .join('');
}

function stringifyArguments(value: unknown): string {
  if (value === undefined) {
    return '{}';
  }
  if (typeof value === 'string') {
    return value;
  }
  try {
    return JSON.stringify(value);
  } catch (_error) {
    return '{}';
  }
}

function normalizeChunkContent(
  content: string | ZaiMessageContentItem[],
): ZaiMessageContentItem[] {
  if (typeof content === 'string') {
    return content === ''
      ? []
      : [
          {
            type: 'text',
            text: content,
          },
        ];
  }

  return content
    .map((item) => normalizeMessageItem(item))
    .filter((item): item is ZaiMessageContentItem => item !== undefined);
}

function normalizeMessageItem(
  item?: ZaiMessageContentItem,
): ZaiMessageContentItem | undefined {
  if (!item) {
    return undefined;
  }
  if (typeof item.text === 'string' && item.text !== '') {
    return {
      type: item.type ?? 'text',
      text: item.text,
    };
  }
  if (typeof item.content === 'string' && item.content !== '') {
    return {
      type: item.type ?? 'text',
      text: item.content,
    };
  }
  return undefined;
}

function mergeToolCalls(target: ZaiToolCall[], incoming: ZaiToolCall[]): void {
  incoming.forEach((call, index) => {
    if (!call) {
      return;
    }
    const existing =
      target[index] ??
      (target[index] = {
        type: call.type ?? 'function',
      });

    if (call.id) {
      existing.id = call.id;
    }
    if (call.type) {
      existing.type = call.type;
    }
    if (call.function?.name) {
      existing.function = existing.function ?? {};
      existing.function.name = call.function.name;
    }
    if (call.function?.arguments) {
      existing.function = existing.function ?? {};
      existing.function.arguments =
        (existing.function.arguments ?? '') + call.function.arguments;
    }
  });
}

function cloneToolCall(call: ZaiToolCall): ZaiToolCall {
  return {
    id: call.id,
    type: call.type,
    function: call.function
      ? {
          name: call.function.name,
          arguments: call.function.arguments,
        }
      : undefined,
  };
}

function safeParseJson(raw: string): Record<string, unknown> | undefined {
  try {
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      return parsed as Record<string, unknown>;
    }
  } catch (_error) {
    // ignore
  }
  return undefined;
}

async function safeReadJson(response: Response): Promise<ZaiErrorResponse> {
  try {
    return (await response.clone().json()) as ZaiErrorResponse;
  } catch (_error) {
    const text = await response.clone().text();
    return { error: { message: text } };
  }
}

function deriveToolCallId(id?: string): string | undefined {
  if (!id) {
    return undefined;
  }
  return id;
}

function mapFinishReason(
  finish: string | null | undefined,
): Candidate['finishReason'] {
  switch (finish) {
    case 'stop':
      return FinishReason.STOP;
    case 'length':
      return FinishReason.MAX_TOKENS;
    case 'content_filter':
      return FinishReason.SAFETY;
    case 'tool_calls':
      return FinishReason.FINISH_REASON_UNSPECIFIED;
    default:
      return undefined;
  }
}
