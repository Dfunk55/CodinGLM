/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import * as path from 'node:path';
import * as os from 'node:os';
import * as crypto from 'node:crypto';
import * as fs from 'node:fs';
import { GEMINI_DIR } from '../utils/paths.js';

export const GOOGLE_ACCOUNTS_FILENAME = 'google_accounts.json';
export const OAUTH_FILE = 'oauth_creds.json';
const TMP_DIR_NAME = 'tmp';
const BIN_DIR_NAME = 'bin';

export class Storage {
  private readonly targetDir: string;

  constructor(targetDir: string) {
    this.targetDir = targetDir;
  }

  static getGlobalAgentDataDir(): string {
    const homeDir = os.homedir();
    if (!homeDir) {
      return path.join(os.tmpdir(), GEMINI_DIR);
    }
    return path.join(homeDir, GEMINI_DIR);
  }

  static getMcpOAuthTokensPath(): string {
    return path.join(Storage.getGlobalAgentDataDir(), 'mcp-oauth-tokens.json');
  }

  static getGlobalSettingsPath(): string {
    return path.join(Storage.getGlobalAgentDataDir(), 'settings.json');
  }

  static getInstallationIdPath(): string {
    return path.join(Storage.getGlobalAgentDataDir(), 'installation_id');
  }

  static getGoogleAccountsPath(): string {
    return path.join(Storage.getGlobalAgentDataDir(), GOOGLE_ACCOUNTS_FILENAME);
  }

  static getUserCommandsDir(): string {
    return path.join(Storage.getGlobalAgentDataDir(), 'commands');
  }

  static getGlobalMemoryFilePath(): string {
    return path.join(Storage.getGlobalAgentDataDir(), 'memory.md');
  }

  static getUserPoliciesDir(): string {
    return path.join(Storage.getGlobalAgentDataDir(), 'policies');
  }

  static getSystemSettingsPath(): string {
    if (process.env['GEMINI_CLI_SYSTEM_SETTINGS_PATH']) {
      return process.env['GEMINI_CLI_SYSTEM_SETTINGS_PATH'];
    }
    if (os.platform() === 'darwin') {
      return '/Library/Application Support/CodinGLMCli/settings.json';
    } else if (os.platform() === 'win32') {
      return 'C:\\ProgramData\\gemini-cli\\settings.json';
    } else {
      return '/etc/gemini-cli/settings.json';
    }
  }

  static getSystemPoliciesDir(): string {
    return path.join(path.dirname(Storage.getSystemSettingsPath()), 'policies');
  }

  static getGlobalTempDir(): string {
    return path.join(Storage.getGlobalAgentDataDir(), TMP_DIR_NAME);
  }

  static getGlobalBinDir(): string {
    return path.join(Storage.getGlobalTempDir(), BIN_DIR_NAME);
  }

  getAgentDataDir(): string {
    return path.join(this.targetDir, GEMINI_DIR);
  }

  getProjectTempDir(): string {
    const hash = this.getFilePathHash(this.getProjectRoot());
    const tempDir = Storage.getGlobalTempDir();
    return path.join(tempDir, hash);
  }

  ensureProjectTempDirExists(): void {
    fs.mkdirSync(this.getProjectTempDir(), { recursive: true });
  }

  static getOAuthCredsPath(): string {
    return path.join(Storage.getGlobalAgentDataDir(), OAUTH_FILE);
  }

  getProjectRoot(): string {
    return this.targetDir;
  }

  private getFilePathHash(filePath: string): string {
    return crypto.createHash('sha256').update(filePath).digest('hex');
  }

  getHistoryDir(): string {
    const hash = this.getFilePathHash(this.getProjectRoot());
    const historyDir = path.join(Storage.getGlobalAgentDataDir(), 'history');
    return path.join(historyDir, hash);
  }

  getWorkspaceSettingsPath(): string {
    return path.join(this.getAgentDataDir(), 'settings.json');
  }

  getProjectCommandsDir(): string {
    return path.join(this.getAgentDataDir(), 'commands');
  }

  getProjectTempCheckpointsDir(): string {
    return path.join(this.getProjectTempDir(), 'checkpoints');
  }

  getExtensionsDir(): string {
    return path.join(this.getAgentDataDir(), 'extensions');
  }

  getExtensionsConfigPath(): string {
    return path.join(this.getExtensionsDir(), 'gemini-extension.json');
  }

  getHistoryFilePath(): string {
    return path.join(this.getProjectTempDir(), 'shell_history');
  }
}
