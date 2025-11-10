/**
 * Internal LLM type definitions replacing @google/genai usage.
 * Only includes shapes used by CodinGLM.
 */

export type Role = 'user' | 'model' | 'tool' | 'system' | 'assistant';

export interface PartText {
  text: string;
  thought?: boolean;
}

export interface PartFunctionCall {
  functionCall: {
    id?: string;
    name?: string;
    args?: Record<string, unknown>;
  };
}

export interface PartFunctionResponse {
  functionResponse: {
    id?: string;
    name?: string;
    response?: Record<string, unknown>;
  };
}

export type Part = PartText | PartFunctionCall | PartFunctionResponse;

export interface Content {
  role: Role;
  parts: Part[];
}

// Unions compatible with prior GenAI SDK type usage
export type PartUnion = Part | string;
export type PartListUnion = PartUnion[];
export type ContentUnion = Content | PartListUnion | string;
export type ContentListUnion = ContentUnion | ContentUnion[];

export interface FunctionDeclaration {
  name?: string;
  description?: string;
  // Allow unknown JSON schema shape
  parameters?: unknown;
  parametersJsonSchema?: unknown;
}

export interface Tool {
  functionDeclarations?: FunctionDeclaration[];
}

export type ToolListUnion = Tool[];

export enum FinishReason {
  STOP = 'STOP',
  MAX_TOKENS = 'MAX_TOKENS',
  SAFETY = 'SAFETY',
  FINISH_REASON_UNSPECIFIED = 'FINISH_REASON_UNSPECIFIED',
}

export interface Candidate {
  index?: number;
  content: Content;
  finishReason?: FinishReason;
  finishMessage?: string;
  logprobsResult?: unknown;
}

export interface GenerateContentConfig {
  temperature?: number;
  topP?: number;
  topK?: number;
  maxOutputTokens?: number;
  stopSequences?: string[];
  thinkingConfig?: unknown;
  abortSignal?: AbortSignal;
  systemInstruction?: string;
  toolConfig?: {
    functionCallingConfig?: {
      mode?: string;
      allowedFunctionNames?: string[];
    };
  };
  // Additional fields used in various parts of the codebase; optional for compatibility
  candidateCount?: number;
  responseLogprobs?: boolean;
  logprobs?: number;
  presencePenalty?: number;
  frequencyPenalty?: number;
  seed?: number;
  responseMimeType?: string;
  responseJsonSchema?: unknown;
  responseSchema?: unknown;
  routingConfig?: unknown;
  modelSelectionConfig?: unknown;
  responseModalities?: string[];
  mediaResolution?: unknown;
  speechConfig?: unknown;
  audioTimestamp?: boolean;
}

export interface GenerateContentParameters {
  model: string;
  contents: ContentListUnion;
  tools?: ToolListUnion | undefined;
  toolConfig?: GenerateContentConfig['toolConfig'];
  config?: GenerateContentConfig;
}

export class GenerateContentResponse {
  // Convenience text (not always present)
  text?: string;
  responseId?: string;
  modelVersion?: string;
  candidates: Candidate[] = [];
  usageMetadata?: {
    promptTokenCount?: number;
    candidatesTokenCount?: number;
    totalTokenCount?: number;
    toolUsePromptTokenCount?: number;
    thoughtsTokenCount?: number;
  };
}

// Named alias widely used across code
export type GenerateContentResponseUsageMetadata = NonNullable<
  GenerateContentResponse['usageMetadata']
>;

export interface CountTokensParameters {
  model: string;
  contents: ContentListUnion;
}

export interface CountTokensResponse {
  totalTokens: number;
}

export interface EmbedContentParameters {
  // Placeholder for compatibility; Z.AI provider doesn't implement embeddings here
  model?: string;
  content?: unknown;
}

export interface EmbedContentResponse {
  // Placeholder shape
  embeddings?: unknown;
}

export interface FunctionCall {
  id?: string;
  name?: string;
  args?: Record<string, unknown>;
}

export interface ToolConfig {
  functionCallingConfig?: FunctionCallingConfig;
}

export interface FunctionCallingConfig {
  mode?: string;
  allowedFunctionNames?: string[];
}
