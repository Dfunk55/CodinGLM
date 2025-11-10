/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
import { GenerateContentResponse, type CountTokensParameters, type CountTokensResponse, type EmbedContentParameters, type EmbedContentResponse, type GenerateContentParameters } from '@google/genai';
import type { ContentGenerator } from './contentGenerator.js';
export interface ZaiContentGeneratorOptions {
    apiKey: string;
    baseUrl?: string;
    organization?: string;
    userAgent?: string;
}
export declare class ZaiContentGenerator implements ContentGenerator {
    private readonly apiKey;
    private readonly baseUrl;
    private readonly organization?;
    private readonly userAgent?;
    constructor(options: ZaiContentGeneratorOptions);
    generateContent(request: GenerateContentParameters, userPromptId: string): Promise<GenerateContentResponse>;
    generateContentStream(request: GenerateContentParameters, userPromptId: string): Promise<AsyncGenerator<GenerateContentResponse>>;
    countTokens(request: CountTokensParameters): Promise<CountTokensResponse>;
    embedContent(_request: EmbedContentParameters): Promise<EmbedContentResponse>;
    private invokeChatCompletion;
    private invokeChatCompletionStream;
    private buildHeaders;
    private buildEndpointUrl;
    private buildRequestBody;
    private convertSystemInstruction;
    private convertContents;
    private convertTools;
    private convertToolChoice;
    private toGenerateContentResponse;
    private buildCandidateContent;
}
