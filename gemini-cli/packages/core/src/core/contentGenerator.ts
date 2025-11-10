/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import type {
  CountTokensResponse,
  GenerateContentResponse,
  GenerateContentParameters,
  CountTokensParameters,
  EmbedContentResponse,
  EmbedContentParameters,
} from '@google/genai';
// Google/Vertex providers are not supported in CodinGLM.
import type { Config } from '../config/config.js';

import type { UserTierId } from '../code_assist/types.js';
import { LoggingContentGenerator } from './loggingContentGenerator.js';
import { FakeContentGenerator } from './fakeContentGenerator.js';
import { RecordingContentGenerator } from './recordingContentGenerator.js';
import { ZaiContentGenerator } from './zaiContentGenerator.js';

const CODINGLM_ONLY_MESSAGE =
  'CodinGLM CLI only supports the Z.AI GLM API key authentication method.';
const isCodinGLM = () => process.env['CODINGLM'] === '1';
function assertCodinGlmAuth(authType?: AuthType) {
  if (!isCodinGLM()) {
    return;
  }
  if (authType !== AuthType.USE_Z_AI) {
    throw new Error(CODINGLM_ONLY_MESSAGE);
  }
}

/**
 * Interface abstracting the core functionalities for generating content and counting tokens.
 */
export interface ContentGenerator {
  generateContent(
    request: GenerateContentParameters,
    userPromptId: string,
  ): Promise<GenerateContentResponse>;

  generateContentStream(
    request: GenerateContentParameters,
    userPromptId: string,
  ): Promise<AsyncGenerator<GenerateContentResponse>>;

  countTokens(request: CountTokensParameters): Promise<CountTokensResponse>;

  embedContent(request: EmbedContentParameters): Promise<EmbedContentResponse>;

  userTier?: UserTierId;
}

export enum AuthType {
  LOGIN_WITH_GOOGLE = 'oauth-personal',
  USE_GEMINI = 'gemini-api-key',
  USE_VERTEX_AI = 'vertex-ai',
  CLOUD_SHELL = 'cloud-shell',
  USE_Z_AI = 'z-ai-api-key',
}

export type ContentGeneratorConfig = {
  apiKey?: string;
  vertexai?: boolean;
  authType?: AuthType;
  proxy?: string;
  baseUrl?: string;
  organization?: string;
};

export async function createContentGeneratorConfig(
  config: Config,
  authType: AuthType | undefined,
): Promise<ContentGeneratorConfig> {
  assertCodinGlmAuth(authType);
  // Only Z.AI API is supported in CodinGLM.
  const zaiApiKey =
    process.env['Z_AI_API_KEY'] || process.env['ZAI_API_KEY'] || undefined;

  const contentGeneratorConfig: ContentGeneratorConfig = {
    authType,
    proxy: config?.getProxy(),
  };

  if (authType === AuthType.USE_Z_AI) {
    if (!zaiApiKey) {
      throw new Error(
        'Z_AI_API_KEY environment variable is required when using the Z.AI provider.',
      );
    }
    contentGeneratorConfig.apiKey = zaiApiKey;
    contentGeneratorConfig.vertexai = false;
    contentGeneratorConfig.baseUrl =
      process.env['Z_AI_BASE_URL'] || process.env['ZAI_BASE_URL'] || undefined;
    contentGeneratorConfig.organization =
      process.env['Z_AI_ORGANIZATION'] ||
      process.env['ZAI_ORGANIZATION'] ||
      undefined;

    return contentGeneratorConfig;
  }
  throw new Error('CodinGLM only supports Z.AI authentication.');
}

export async function createContentGenerator(
  config: ContentGeneratorConfig,
  gcConfig: Config,
  sessionId?: string,
): Promise<ContentGenerator> {
  assertCodinGlmAuth(config.authType);
  const generator = await (async () => {
    if (gcConfig.fakeResponses) {
      return FakeContentGenerator.fromFile(gcConfig.fakeResponses);
    }
    const version = process.env['CLI_VERSION'] || process.version;
    const userAgent = `CodinGLM/${version} (${process.platform}; ${process.arch})`;
    // User-Agent propagated to Z.AI client
    if (config.authType === AuthType.USE_Z_AI) {
      const zaiGenerator = new ZaiContentGenerator({
        apiKey: config.apiKey ?? '',
        baseUrl: config.baseUrl,
        organization: config.organization,
        userAgent,
      });
      return new LoggingContentGenerator(zaiGenerator, gcConfig);
    }
    throw new Error(
      `Error creating contentGenerator: Unsupported authType: ${config.authType}`,
    );
  })();

  if (gcConfig.recordResponses) {
    return new RecordingContentGenerator(generator, gcConfig.recordResponses);
  }

  return generator;
}
