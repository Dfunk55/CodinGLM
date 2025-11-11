/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import * as fs from 'node:fs';
import * as path from 'node:path';
import { homedir } from 'node:os';
import * as dotenv from 'dotenv';

import type { TelemetryTarget } from '@codinglm/core';
import {
  AuthType,
  Config,
  type ConfigParameters,
  FileDiscoveryService,
  ApprovalMode,
  loadServerHierarchicalMemory,
  GEMINI_DIR,
  DEFAULT_GLM_EMBEDDING_MODEL,
  DEFAULT_GLM_MODEL,
  type ExtensionLoader,
} from '@codinglm/core';

import { logger } from '../utils/logger.js';
import type { Settings } from './settings.js';
import { type AgentSettings, CoderAgentEvent } from '../types.js';

export async function loadConfig(
  settings: Settings,
  extensionLoader: ExtensionLoader,
  taskId: string,
): Promise<Config> {
  const workspaceDir = process.cwd();
  const adcFilePath = process.env['GOOGLE_APPLICATION_CREDENTIALS'];

  const configParams: ConfigParameters = {
    sessionId: taskId,
    model: DEFAULT_GLM_MODEL,
    embeddingModel: DEFAULT_GLM_EMBEDDING_MODEL,
    sandbox: undefined, // Sandbox might not be relevant for a server-side agent
    targetDir: workspaceDir, // Or a specific directory the agent operates on
    debugMode: process.env['DEBUG'] === 'true' || false,
    question: '', // Not used in server mode directly like CLI

    coreTools: settings.coreTools || undefined,
    excludeTools: settings.excludeTools || undefined,
    showMemoryUsage: settings.showMemoryUsage || false,
    approvalMode:
      process.env['GEMINI_YOLO_MODE'] === 'true'
        ? ApprovalMode.YOLO
        : ApprovalMode.DEFAULT,
    mcpServers: settings.mcpServers,
    cwd: workspaceDir,
    telemetry: {
      enabled: settings.telemetry?.enabled,
      target: settings.telemetry?.target as TelemetryTarget,
      otlpEndpoint:
        process.env['OTEL_EXPORTER_OTLP_ENDPOINT'] ??
        settings.telemetry?.otlpEndpoint,
      logPrompts: settings.telemetry?.logPrompts,
    },
    // Git-aware file filtering settings
    fileFiltering: {
      respectGitIgnore: settings.fileFiltering?.respectGitIgnore,
      enableRecursiveFileSearch:
        settings.fileFiltering?.enableRecursiveFileSearch,
    },
    ideMode: false,
    folderTrust: settings.folderTrust === true,
    extensionLoader,
  };

  const fileService = new FileDiscoveryService(workspaceDir);
  const { memoryContent, fileCount } = await loadServerHierarchicalMemory(
    workspaceDir,
    [workspaceDir],
    false,
    fileService,
    extensionLoader,
    settings.folderTrust === true,
  );
  configParams.userMemory = memoryContent;
  configParams.contextFileCount = fileCount;
  const config = new Config({
    ...configParams,
  });
  // Needed to initialize ToolRegistry, and git checkpointing if enabled
  await config.initialize();

  if (process.env['USE_CCPA']) {
    logger.info('[Config] Using CCPA Auth:');
    try {
      if (adcFilePath) {
        path.resolve(adcFilePath);
      }
    } catch (e) {
      logger.error(
        `[Config] USE_CCPA env var is true but unable to resolve GOOGLE_APPLICATION_CREDENTIALS file path ${adcFilePath}. Error ${e}`,
      );
    }
    await config.refreshAuth(AuthType.LOGIN_WITH_GOOGLE);
    logger.info(
      `[Config] GOOGLE_CLOUD_PROJECT: ${process.env['GOOGLE_CLOUD_PROJECT']}`,
    );
  } else {
    const zaiApiKey =
      process.env['Z_AI_API_KEY'] || process.env['ZAI_API_KEY'] || undefined;
    const legacyApiKey =
      process.env['GEMINI_API_KEY'] || process.env['LEGACY_GEMINI_API_KEY'];

    if (zaiApiKey) {
      logger.info('[Config] Using Z.AI API key');
      process.env['Z_AI_API_KEY'] = zaiApiKey;
      await config.refreshAuth(AuthType.USE_Z_AI);
    } else if (legacyApiKey) {
      logger.warn(
        '[Config] Using legacy GEMINI_API_KEY for compatibility; prefer Z_AI_API_KEY instead.',
      );
      process.env['Z_AI_API_KEY'] = legacyApiKey;
      await config.refreshAuth(AuthType.USE_Z_AI);
    } else {
      const errorMessage =
        '[Config] Unable to set GeneratorConfig. Please provide a Z_AI_API_KEY (or legacy GEMINI_API_KEY) or set USE_CCPA.';
      logger.error(errorMessage);
      throw new Error(errorMessage);
    }
  }

  return config;
}

export function setTargetDir(agentSettings: AgentSettings | undefined): string {
  const originalCWD = process.cwd();
  const targetDir =
    process.env['CODER_AGENT_WORKSPACE_PATH'] ??
    (agentSettings?.kind === CoderAgentEvent.StateAgentSettingsEvent
      ? agentSettings.workspacePath
      : undefined);

  if (!targetDir) {
    return originalCWD;
  }

  logger.info(
    `[CoderAgentExecutor] Overriding workspace path to: ${targetDir}`,
  );

  try {
    const resolvedPath = path.resolve(targetDir);
    process.chdir(resolvedPath);
    return resolvedPath;
  } catch (e) {
    logger.error(
      `[CoderAgentExecutor] Error resolving workspace path: ${e}, returning original os.cwd()`,
    );
    return originalCWD;
  }
}

export function loadEnvironment(): void {
  const envFilePath = findEnvFile(process.cwd());
  if (envFilePath) {
    dotenv.config({ path: envFilePath, override: true });
  }
}

function findEnvFile(startDir: string): string | null {
  let currentDir = path.resolve(startDir);
  while (true) {
    // prefer gemini-specific .env under GEMINI_DIR
    const geminiEnvPath = path.join(currentDir, GEMINI_DIR, '.env');
    if (fs.existsSync(geminiEnvPath)) {
      return geminiEnvPath;
    }
    const envPath = path.join(currentDir, '.env');
    if (fs.existsSync(envPath)) {
      return envPath;
    }
    const parentDir = path.dirname(currentDir);
    if (parentDir === currentDir || !parentDir) {
      // check .env under home as fallback, again preferring gemini-specific .env
      const homeAgentEnvPath = path.join(process.cwd(), GEMINI_DIR, '.env');
      if (fs.existsSync(homeAgentEnvPath)) {
        return homeAgentEnvPath;
      }
      const homeEnvPath = path.join(homedir(), '.env');
      if (fs.existsSync(homeEnvPath)) {
        return homeEnvPath;
      }
      return null;
    }
    currentDir = parentDir;
  }
}
