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
export interface FunctionDeclaration {
    name?: string;
    description?: string;
    parameters?: unknown;
    parametersJsonSchema?: unknown;
}
export interface Tool {
    functionDeclarations?: FunctionDeclaration[];
}
export declare enum FinishReason {
    STOP = "STOP",
    MAX_TOKENS = "MAX_TOKENS",
    SAFETY = "SAFETY",
    FINISH_REASON_UNSPECIFIED = "FINISH_REASON_UNSPECIFIED"
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
}
export interface GenerateContentParameters {
    model: string;
    contents: Content | Content[] | Array<Content | Part | string>;
    tools?: Tool[] | undefined;
    toolConfig?: GenerateContentConfig['toolConfig'];
    config?: GenerateContentConfig;
}
export declare class GenerateContentResponse {
    responseId?: string;
    modelVersion?: string;
    candidates: Candidate[];
    usageMetadata?: {
        promptTokenCount?: number;
        candidatesTokenCount?: number;
        totalTokenCount?: number;
        toolUsePromptTokenCount?: number;
        thoughtsTokenCount?: number;
    };
}
export type PartListUnion = Part[];
export type PartUnion = Part;
