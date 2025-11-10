/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import type { ContentGenerator } from './contentGenerator.js';
import {
  createContentGenerator,
  AuthType,
  createContentGeneratorConfig,
} from './contentGenerator.js';
import type { Config } from '../config/config.js';
import { LoggingContentGenerator } from './loggingContentGenerator.js';
import { FakeContentGenerator } from './fakeContentGenerator.js';
import { RecordingContentGenerator } from './recordingContentGenerator.js';
import { ZaiContentGenerator } from './zaiContentGenerator.js';

vi.mock('./fakeContentGenerator.js');

const mockConfig = {} as unknown as Config;

describe('createContentGenerator', () => {
  it('should create a FakeContentGenerator', async () => {
    const mockGenerator = {} as unknown as ContentGenerator;
    vi.mocked(FakeContentGenerator.fromFile).mockResolvedValue(
      mockGenerator as never,
    );
    const fakeResponsesFile = 'fake/responses.yaml';
    const mockConfigWithFake = {
      fakeResponses: fakeResponsesFile,
    } as unknown as Config;
    const generator = await createContentGenerator(
      {
        authType: AuthType.USE_Z_AI,
      },
      mockConfigWithFake,
    );
    expect(FakeContentGenerator.fromFile).toHaveBeenCalledWith(
      fakeResponsesFile,
    );
    expect(generator).toEqual(mockGenerator);
  });

  it('should create a RecordingContentGenerator', async () => {
    const fakeResponsesFile = 'fake/responses.yaml';
    const recordResponsesFile = 'record/responses.yaml';
    const mockConfigWithRecordResponses = {
      fakeResponses: fakeResponsesFile,
      recordResponses: recordResponsesFile,
    } as unknown as Config;
    const generator = await createContentGenerator(
      {
        authType: AuthType.USE_Z_AI,
      },
      mockConfigWithRecordResponses,
    );
    expect(generator).toBeInstanceOf(RecordingContentGenerator);
  });

  it('should create a ZaiContentGenerator wrapped in LoggingContentGenerator', async () => {
    const mockConfig = {
      getUsageStatisticsEnabled: () => true,
    } as unknown as Config;
    const generator = await createContentGenerator(
      {
        apiKey: 'test-api-key',
        authType: AuthType.USE_Z_AI,
      },
      mockConfig,
    );
    expect(generator).toBeInstanceOf(LoggingContentGenerator);
    expect((generator as LoggingContentGenerator).getWrapped()).toBeInstanceOf(
      ZaiContentGenerator,
    );
  });
});

describe('CodinGLM enforcement', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('throws in createContentGenerator when non Z.AI auth is used while CODINGLM is set', async () => {
    vi.stubEnv('CODINGLM', '1');
    await expect(
      createContentGenerator(
        {
          authType: AuthType.USE_GEMINI,
        },
        mockConfig,
      ),
    ).rejects.toThrow(
      'CodinGLM CLI only supports the Z.AI GLM API key authentication method.',
    );
  });

  it('throws in createContentGeneratorConfig when non Z.AI auth is requested while CODINGLM is set', async () => {
    vi.stubEnv('CODINGLM', '1');
    await expect(
      createContentGeneratorConfig(mockConfig as Config, AuthType.USE_GEMINI),
    ).rejects.toThrow(
      'CodinGLM CLI only supports the Z.AI GLM API key authentication method.',
    );
  });
});

describe('createContentGeneratorConfig', () => {
  const mockConfig = {
    getProxy: vi.fn(),
  } as unknown as Config;

  beforeEach(() => {
    vi.resetModules();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('should configure for Z.AI using Z_AI_API_KEY when set', async () => {
    vi.stubEnv('Z_AI_API_KEY', 'env-zai-key');
    const config = await createContentGeneratorConfig(
      mockConfig,
      AuthType.USE_Z_AI,
    );
    expect(config.apiKey).toBe('env-zai-key');
    expect(config.vertexai).toBe(false);
  });

  it('should include baseUrl and organization when provided', async () => {
    vi.stubEnv('Z_AI_API_KEY', 'env-zai-key');
    vi.stubEnv('Z_AI_BASE_URL', 'https://api.z.ai/api/coding/paas/v4');
    vi.stubEnv('Z_AI_ORGANIZATION', 'org-123');
    const config = await createContentGeneratorConfig(
      mockConfig,
      AuthType.USE_Z_AI,
    );
    expect(config.baseUrl).toBe('https://api.z.ai/api/coding/paas/v4');
    expect(config.organization).toBe('org-123');
  });

  it('should throw if Z_AI_API_KEY is not set for Z.AI', async () => {
    vi.stubEnv('Z_AI_API_KEY', '');
    await expect(
      createContentGeneratorConfig(mockConfig, AuthType.USE_Z_AI),
    ).rejects.toThrow();
  });
});
