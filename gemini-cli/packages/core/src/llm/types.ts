/**
 * Internal LLM type definitions replacing @codinglm/genai usage.
 * Only includes shapes used by CodinGLM.
 */

// Relax role typing to accommodate call sites that construct Content with string roles
export type Role = string;

// Broad, SDK-compatible Part shape with optional properties.
// This mirrors the flexible structure used previously so callers can
// safely access fields like `text` without excessive narrowing.
export interface Part {
  text?: string;
  thought?: boolean;
  // Optional execution-related fields used in telemetry
  executableCode?: { code?: string; language?: string } | null;
  codeExecutionResult?: { outcome?: string; output?: string } | null;
  functionCall?: {
    id?: string;
    name?: string;
    args?: Record<string, unknown>;
  };
  functionResponse?: {
    id?: string;
    name?: string;
    response?: Record<string, unknown>;
  };
  inlineData?: { mimeType?: string; data?: string | Uint8Array } | null;
  fileData?: { mimeType?: string; [key: string]: unknown } | null;
}

export interface Content {
  role: Role;
  parts: Part[];
}

// Unions compatible with prior GenAI SDK type usage
export type PartUnion = Part | string;
export type PartListUnion = PartUnion[] | string;
export type ContentUnion = Content | PartListUnion | string;
export type ContentListUnion = ContentUnion | ContentUnion[];

export interface FunctionDeclaration {
  name?: string;
  description?: string;
  // Minimal JSON schema-like structure for tool parameters
  parameters?: {
    type?: string;
    properties?: Record<string, unknown>;
    required?: string[];
    [key: string]: unknown;
  };
  parametersJsonSchema?: unknown;
}

export interface Tool {
  functionDeclarations?: FunctionDeclaration[];
  [key: string]: unknown;
}

export type ToolListUnion = Tool[];

export enum FinishReason {
  STOP = 'STOP',
  MAX_TOKENS = 'MAX_TOKENS',
  SAFETY = 'SAFETY',
  FINISH_REASON_UNSPECIFIED = 'FINISH_REASON_UNSPECIFIED',
  RECITATION = 'RECITATION',
  LANGUAGE = 'LANGUAGE',
  OTHER = 'OTHER',
  BLOCKLIST = 'BLOCKLIST',
  PROHIBITED_CONTENT = 'PROHIBITED_CONTENT',
  SPII = 'SPII',
  MALFORMED_FUNCTION_CALL = 'MALFORMED_FUNCTION_CALL',
  IMAGE_SAFETY = 'IMAGE_SAFETY',
  UNEXPECTED_TOOL_CALL = 'UNEXPECTED_TOOL_CALL',
}

export interface Candidate {
  index?: number;
  content: Content;
  finishReason?: FinishReason;
  finishMessage?: string;
  logprobsResult?: unknown;
  citationMetadata?: { citations?: { uri?: string; title?: string }[] };
  urlContextMetadata?: any;
  groundingMetadata?: any;
  safetyRatings?: any[];
}

export interface GenerateContentConfig {
  temperature?: number;
  topP?: number;
  topK?: number;
  maxOutputTokens?: number;
  stopSequences?: string[];
  thinkingConfig?: unknown;
  abortSignal?: AbortSignal;
  // Accept the system instruction in multiple forms
  systemInstruction?: string | Part | Part[] | Content;
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
  // Compatibility fields referenced in converter and elsewhere
  cachedContent?: string | Content[];
  tools?: ToolListUnion;
  labels?: Record<string, string>;
  safetySettings?: SafetySetting[];
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
    cachedContentTokenCount?: number;
  };
  // Additional compatibility fields
  promptFeedback?: unknown;
  automaticFunctionCallingHistory?: Content[];
  functionCalls?: FunctionCall[];
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
  // Accept both legacy 'contents' and 'content' shapes used in tests/code
  contents?: string[];
  content?: unknown;
}

export interface EmbedContentResponse {
  embeddings?: { values: number[] }[];
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

// Minimal safety shapes for compatibility with prior code paths
export interface SafetySetting {
  category?: string;
  threshold?: string;
}
