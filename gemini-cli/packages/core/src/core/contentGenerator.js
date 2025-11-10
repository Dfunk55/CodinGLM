/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
import { LoggingContentGenerator } from './loggingContentGenerator.js';
import { FakeContentGenerator } from './fakeContentGenerator.js';
import { RecordingContentGenerator } from './recordingContentGenerator.js';
import { ZaiContentGenerator } from './zaiContentGenerator.js';
const CODINGLM_ONLY_MESSAGE = 'CodinGLM CLI only supports the Z.AI GLM API key authentication method.';
const isCodinGLM = () => process.env['CODINGLM'] === '1';
function assertCodinGlmAuth(authType) {
    if (!isCodinGLM()) {
        return;
    }
    if (authType !== AuthType.USE_Z_AI) {
        throw new Error(CODINGLM_ONLY_MESSAGE);
    }
}
export var AuthType;
(function (AuthType) {
    AuthType["LOGIN_WITH_GOOGLE"] = "oauth-personal";
    AuthType["USE_GEMINI"] = "gemini-api-key";
    AuthType["USE_VERTEX_AI"] = "vertex-ai";
    AuthType["CLOUD_SHELL"] = "cloud-shell";
    AuthType["USE_Z_AI"] = "z-ai-api-key";
})(AuthType || (AuthType = {}));
export async function createContentGeneratorConfig(config, authType) {
    assertCodinGlmAuth(authType);
    // Only Z.AI API is supported in CodinGLM.
    const zaiApiKey = process.env['Z_AI_API_KEY'] || process.env['ZAI_API_KEY'] || undefined;
    const contentGeneratorConfig = {
        authType,
        proxy: config?.getProxy(),
    };
    if (authType === AuthType.USE_Z_AI) {
        if (!zaiApiKey) {
            throw new Error('Z_AI_API_KEY environment variable is required when using the Z.AI provider.');
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
export async function createContentGenerator(config, gcConfig, sessionId) {
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
        throw new Error(`Error creating contentGenerator: Unsupported authType: ${config.authType}`);
    })();
    if (gcConfig.recordResponses) {
        return new RecordingContentGenerator(generator, gcConfig.recordResponses);
    }
    return generator;
}
//# sourceMappingURL=contentGenerator.js.map