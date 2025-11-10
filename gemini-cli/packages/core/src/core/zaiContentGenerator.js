/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
import { GenerateContentResponse, FinishReason, FunctionCallingConfigMode, } from '@google/genai';
import { toContents } from '../code_assist/converter.js';
import { partToString } from '../utils/partUtils.js';
const DEFAULT_BASE_URL = 'https://api.z.ai/api/coding/paas/v4';
const CHAT_COMPLETIONS_PATH = '/chat/completions';
export class ZaiContentGenerator {
    apiKey;
    baseUrl;
    organization;
    userAgent;
    constructor(options) {
        if (!options.apiKey) {
            throw new Error('Z_AI_API_KEY is required when using the Z.AI provider.');
        }
        this.apiKey = options.apiKey;
        this.baseUrl = trimTrailingSlash(options.baseUrl ?? DEFAULT_BASE_URL);
        this.organization = options.organization;
        this.userAgent = options.userAgent;
    }
    async generateContent(request, userPromptId) {
        return this.invokeChatCompletion(request, userPromptId);
    }
    async generateContentStream(request, userPromptId) {
        return this.invokeChatCompletionStream(request, userPromptId);
    }
    async countTokens(request) {
        const contents = toContents(request.contents);
        const totalCharacters = contents
            .map((content) => collectTextFromContent(content).length)
            .reduce((acc, count) => acc + count, 0);
        const estimatedTokens = Math.max(1, Math.ceil(totalCharacters / 4));
        return {
            totalTokens: estimatedTokens,
        };
    }
    async embedContent(_request) {
        throw new Error('Z.AI provider does not support embedContent.');
    }
    async invokeChatCompletion(request, userPromptId) {
        const body = this.buildRequestBody(request, userPromptId, false);
        const response = await fetch(this.buildEndpointUrl(), {
            method: 'POST',
            headers: this.buildHeaders(),
            body: JSON.stringify(body),
            signal: request.config?.abortSignal,
        });
        if (!response.ok) {
            const errorPayload = await safeReadJson(response);
            const errorMessage = typeof errorPayload?.error?.message === 'string'
                ? errorPayload.error.message
                : await response.text();
            throw new Error(`Z.AI API error (${response.status} ${response.statusText}): ${errorMessage}`);
        }
        const json = (await response.json());
        return this.toGenerateContentResponse(json, request.model);
    }
    async invokeChatCompletionStream(request, userPromptId) {
        const body = this.buildRequestBody(request, userPromptId, true);
        const response = await fetch(this.buildEndpointUrl(), {
            method: 'POST',
            headers: this.buildHeaders(),
            body: JSON.stringify(body),
            signal: request.config?.abortSignal,
        });
        if (!response.ok) {
            const errorPayload = await safeReadJson(response);
            const errorMessage = typeof errorPayload?.error?.message === 'string'
                ? errorPayload.error.message
                : await response.text();
            throw new Error(`Z.AI API error (${response.status} ${response.statusText}): ${errorMessage}`);
        }
        const contentType = response.headers.get('content-type') ?? '';
        if (!contentType.includes('text/event-stream') || !response.body) {
            const json = (await response.json());
            const initial = this.toGenerateContentResponse(json, request.model);
            return (async function* () {
                yield initial;
            })();
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        const streamingState = new ZaiStreamingState();
        const toGenerateResponse = this.toGenerateContentResponse.bind(this);
        return (async function* () {
            let buffer = '';
            let streamClosed = false;
            while (!streamClosed) {
                const { value, done } = await reader.read();
                if (done) {
                    buffer += decoder.decode();
                    streamClosed = true;
                }
                else if (value) {
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
                    let parsedChunk;
                    try {
                        parsedChunk = JSON.parse(trimmedPayload);
                    }
                    catch (_error) {
                        eventEnd = buffer.indexOf('\n\n');
                        continue;
                    }
                    const aggregatedResponse = streamingState.applyChunk(parsedChunk, request.model);
                    yield toGenerateResponse(aggregatedResponse, request.model);
                    eventEnd = buffer.indexOf('\n\n');
                }
                if (streamClosed) {
                    const remainingData = buffer.trim();
                    if (remainingData.length > 0) {
                        const payload = extractSseData(`${remainingData}\n`);
                        if (payload && payload.trim() !== '[DONE]') {
                            try {
                                const parsedChunk = JSON.parse(payload.trim());
                                const aggregatedResponse = streamingState.applyChunk(parsedChunk, request.model);
                                yield toGenerateResponse(aggregatedResponse, request.model);
                            }
                            catch (_error) {
                                // Ignore trailing parse issues.
                            }
                        }
                    }
                }
            }
        })();
    }
    buildHeaders() {
        const headers = {
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
    buildEndpointUrl() {
        return `${this.baseUrl}${CHAT_COMPLETIONS_PATH}`;
    }
    buildRequestBody(request, userPromptId, stream) {
        const contents = toContents(request.contents);
        const messages = [
            ...this.convertSystemInstruction(request.config),
            ...this.convertContents(contents),
        ];
        const config = request.config ?? {};
        const body = {
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
        if (Array.isArray(config.stopSequences) &&
            config.stopSequences.length > 0) {
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
    convertSystemInstruction(config) {
        if (!config?.systemInstruction) {
            return [];
        }
        const text = convertContentUnionToText(config.systemInstruction);
        if (!text) {
            return [];
        }
        return [{ role: 'system', content: text }];
    }
    convertContents(contents) {
        const messages = [];
        for (const content of contents) {
            if (!content?.parts || content.parts.length === 0) {
                continue;
            }
            const role = mapRole(content.role);
            const textParts = content.parts.filter((part) => typeof part.text === 'string' && part.text.trim() !== '');
            const functionCalls = content.parts.filter((part) => !!part.functionCall);
            const functionResponses = content.parts.filter((part) => !!part.functionResponse);
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
                        const id = (part.functionCall?.id ?? part.functionCall?.name)
                            ? `${part.functionCall?.name}-${index}`
                            : undefined;
                        const args = part.functionCall?.args !== undefined
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
                        tool_call_id: response?.id ??
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
    convertTools(toolList) {
        if (!toolList || !Array.isArray(toolList)) {
            return [];
        }
        const tools = toolList.filter((tool) => 'functionDeclarations' in tool);
        const declarations = tools.flatMap((tool) => tool.functionDeclarations ?? []);
        return declarations.map((fn) => ({
            type: 'function',
            function: {
                name: fn.name,
                description: fn.description,
                parameters: fn.parametersJsonSchema ?? fn.parameters,
            },
        }));
    }
    convertToolChoice(toolConfig) {
        const config = toolConfig?.functionCallingConfig;
        if (!config) {
            return undefined;
        }
        if (config.mode === FunctionCallingConfigMode.NONE) {
            return 'none';
        }
        if (config.mode === FunctionCallingConfigMode.ANY ||
            config.mode === FunctionCallingConfigMode.VALIDATED ||
            config.mode === FunctionCallingConfigMode.AUTO ||
            config.mode === undefined) {
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
    toGenerateContentResponse(payload, requestedModel) {
        const response = new GenerateContentResponse();
        response.responseId = payload.id;
        response.modelVersion = payload.model ?? requestedModel;
        response.candidates = payload.choices.map((choice) => {
            const candidate = {
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
    buildCandidateContent(choice) {
        const parts = [];
        const message = choice.message;
        if (message) {
            const content = message.content;
            if (typeof content === 'string') {
                if (content) {
                    parts.push({ text: content });
                }
            }
            else if (Array.isArray(content)) {
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
                    let parsedArgs = undefined;
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
class ZaiStreamingState {
    id;
    model;
    usage;
    choices = new Map();
    applyChunk(chunk, requestedModel) {
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
                state.reasoning.push(...normalizeChunkContent(choice.delta.reasoning_content));
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
        const aggregatedChoices = Array.from(this.choices.values()).map((state) => ({
            index: state.index,
            message: {
                role: state.role,
                content: state.content.length === 0
                    ? ''
                    : state.content.map((item) => ({ ...item })),
                reasoning_content: state.reasoning.length > 0
                    ? state.reasoning.map((item) => ({ ...item }))
                    : undefined,
                tool_calls: state.toolCalls.length > 0
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
function extractSseData(eventChunk) {
    const lines = eventChunk.split('\n');
    const dataPayload = [];
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
function trimTrailingSlash(url) {
    return url.endsWith('/') ? url.slice(0, -1) : url;
}
function mapRole(role) {
    if (role === 'model' || role === 'assistant') {
        return 'assistant';
    }
    return 'user';
}
function convertContentUnionToText(content) {
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
function collectTextFromContent(content) {
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
function stringifyArguments(value) {
    if (value === undefined) {
        return '{}';
    }
    if (typeof value === 'string') {
        return value;
    }
    try {
        return JSON.stringify(value);
    }
    catch (_error) {
        return '{}';
    }
}
function normalizeChunkContent(content) {
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
        .filter((item) => item !== undefined);
}
function normalizeMessageItem(item) {
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
function mergeToolCalls(target, incoming) {
    incoming.forEach((call, index) => {
        if (!call) {
            return;
        }
        const existing = target[index] ??
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
function cloneToolCall(call) {
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
function safeParseJson(raw) {
    try {
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
            return parsed;
        }
    }
    catch (_error) {
        // ignore
    }
    return undefined;
}
async function safeReadJson(response) {
    try {
        return (await response.clone().json());
    }
    catch (_error) {
        const text = await response.clone().text();
        return { error: { message: text } };
    }
}
function deriveToolCallId(id) {
    if (!id) {
        return undefined;
    }
    return id;
}
function mapFinishReason(finish) {
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
//# sourceMappingURL=zaiContentGenerator.js.map