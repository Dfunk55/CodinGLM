/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

// Export config
export * from './config/config.ts';
export * from './output/types.ts';
export * from './output/json-formatter.ts';
export * from './output/stream-json-formatter.ts';
export * from './policy/types.ts';
export * from './policy/policy-engine.ts';
export * from './policy/toml-loader.ts';
export * from './policy/config.ts';
export * from './confirmation-bus/types.ts';
export * from './confirmation-bus/message-bus.ts';

// Export Commands logic
export * from './commands/extensions.ts';

// Export Core Logic
export * from './core/client.ts';
export * from './core/contentGenerator.ts';
export * from './core/loggingContentGenerator.ts';
export * from './core/chatSession.ts';
export * from './core/logger.ts';
export * from './core/prompts.ts';
export * from './core/tokenLimits.ts';
export * from './core/turn.ts';
export * from './core/llmRequest.ts';
export * from './core/coreToolScheduler.ts';
export * from './core/nonInteractiveToolExecutor.ts';
export * from './core/recordingContentGenerator.ts';

export * from './fallback/types.ts';

export * from './code_assist/codeAssist.ts';
export * from './code_assist/oauth2.ts';
export * from './code_assist/server.ts';
export * from './code_assist/types.ts';
export * from './core/apiKeyCredentialStorage.ts';

// Export utilities
export * from './utils/paths.ts';
export * from './utils/schemaValidator.ts';
export * from './utils/errors.ts';
export * from './utils/getFolderStructure.ts';
export * from './utils/memoryDiscovery.ts';
export * from './utils/getPty.ts';
export * from './utils/gitIgnoreParser.ts';
export * from './utils/gitUtils.ts';
export * from './utils/editor.ts';
export * from './utils/quotaErrorDetection.ts';
export * from './utils/googleQuotaErrors.ts';
export * from './utils/fileUtils.ts';
export * from './utils/retry.ts';
export * from './utils/shell-utils.ts';
export * from './utils/terminalSerializer.ts';
export * from './utils/systemEncoding.ts';
export * from './utils/textUtils.ts';
export * from './utils/formatters.ts';
export * from './utils/generateContentResponseUtilities.ts';
export * from './utils/filesearch/fileSearch.ts';
export * from './utils/errorParsing.ts';
export * from './utils/workspaceContext.ts';
export * from './utils/ignorePatterns.ts';
export * from './utils/partUtils.ts';
export * from './utils/promptIdContext.ts';
export * from './utils/thoughtUtils.ts';
export * from './utils/debugLogger.ts';
export * from './utils/events.ts';
export * from './utils/extensionLoader.ts';
export * from './utils/package.ts';
export * from './config/models.ts';

// Export services
export * from './services/fileDiscoveryService.ts';
export * from './services/gitService.ts';
export * from './services/chatRecordingService.ts';
export * from './services/fileSystemService.ts';

// Export IDE specific logic
export * from './ide/ide-client.ts';
export * from './ide/ideContext.ts';
export * from './ide/ide-installer.ts';
export { IDE_DEFINITIONS, type IdeInfo } from './ide/detect-ide.ts';
export * from './ide/constants.ts';
export * from './ide/types.ts';

// Export Shell Execution Service
export * from './services/shellExecutionService.ts';

// Export base tool definitions
export * from './tools/tools.ts';
export * from './tools/tool-error.ts';
export * from './tools/tool-registry.ts';
export * from './tools/tool-names.ts';

// Export prompt logic
export * from './prompts/mcp-prompts.ts';

// Export specific tool logic
export * from './tools/read-file.ts';
export * from './tools/ls.ts';
export * from './tools/grep.ts';
export * from './tools/ripGrep.ts';
export * from './tools/glob.ts';
export * from './tools/edit.ts';
export * from './tools/write-file.ts';
export * from './tools/web-fetch.ts';
export * from './tools/memoryTool.ts';
export * from './tools/shell.ts';
export * from './tools/web-search.ts';
export * from './tools/read-many-files.ts';
export * from './tools/mcp-client.ts';
export * from './tools/mcp-tool.ts';
export * from './tools/write-todos.ts';

// MCP OAuth
export { MCPOAuthProvider } from './mcp/oauth-provider.ts';
export type { OAuthToken, OAuthCredentials } from './mcp/token-storage/types.ts';
export { MCPOAuthTokenStorage } from './mcp/oauth-token-storage.ts';
export type { MCPOAuthConfig } from './mcp/oauth-provider.ts';
export type {
  OAuthAuthorizationServerMetadata,
  OAuthProtectedResourceMetadata,
} from './mcp/oauth-utils.ts';
export { OAuthUtils } from './mcp/oauth-utils.ts';

// Export telemetry functions
export * from './telemetry/index.ts';
export { sessionId } from './utils/session.ts';
export * from './utils/browser.ts';
export { Storage } from './config/storage.ts';

// Export test utils
export * from './test-utils/index.ts';

// Export hook types
export * from './hooks/types.ts';
