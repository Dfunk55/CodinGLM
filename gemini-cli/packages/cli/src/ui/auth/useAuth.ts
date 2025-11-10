/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect, useCallback } from 'react';
import type { LoadedSettings } from '../../config/settings.js';
import {
  AuthType,
  type Config,
  loadApiKey,
  debugLogger,
} from '@codinglm/core';
import { getErrorMessage } from '@codinglm/core';
import { AuthState } from '../types.js';
import {
  resolveAuthTypeFromEnvironment,
  validateAuthMethod,
} from '../../config/auth.js';

const isCodinGLM = () => process.env['CODINGLM'] === '1';

export function validateAuthMethodWithSettings(
  authType: AuthType,
  settings: LoadedSettings,
): string | null {
  const enforcedType = settings.merged.security?.auth?.enforcedType;
  if (enforcedType && enforcedType !== authType) {
    return `Authentication is enforced to be ${enforcedType}, but you are currently using ${authType}.`;
  }
  if (settings.merged.security?.auth?.useExternal) {
    return null;
  }
  if (isCodinGLM()) {
    if (authType === AuthType.USE_Z_AI) {
      return null;
    }
    return 'CodinGLM CLI only supports the Z.AI GLM API key authentication method.';
  }
  // If using Gemini API key, we don't validate it here as we might need to prompt for it.
  if (authType === AuthType.USE_GEMINI || authType === AuthType.USE_Z_AI) {
    return null;
  }
  return validateAuthMethod(authType);
}

export const useAuthCommand = (settings: LoadedSettings, config: Config) => {
  const [authState, setAuthState] = useState<AuthState>(
    AuthState.Unauthenticated,
  );

  const [authError, setAuthError] = useState<string | null>(null);
  const [apiKeyDefaultValue, setApiKeyDefaultValue] = useState<
    string | undefined
  >(undefined);

  const onAuthError = useCallback(
    (error: string | null) => {
      setAuthError(error);
      if (error) {
        setAuthState(AuthState.Updating);
      }
    },
    [setAuthError, setAuthState],
  );

  const reloadApiKey = useCallback(async () => {
    const storedKey = (await loadApiKey()) ?? '';
    const envKey = isCodinGLM()
      ? process.env['Z_AI_API_KEY'] ?? process.env['ZAI_API_KEY'] ?? ''
      : process.env['GEMINI_API_KEY'] ?? '';
    const key = storedKey || envKey;
    setApiKeyDefaultValue(key);
    return key; // Return the key for immediate use
  }, []);

  useEffect(() => {
    (async () => {
      if (authState !== AuthState.Unauthenticated) {
        return;
      }

      const configuredType =
        settings.merged.security?.auth?.selectedType ?? undefined;
      const envAuthType = resolveAuthTypeFromEnvironment();
      const effectiveAuthType = configuredType ?? envAuthType;

      if (!effectiveAuthType) {
        if (isCodinGLM()) {
          if (process.env['Z_AI_API_KEY'] || process.env['ZAI_API_KEY']) {
            onAuthError(
              'Existing API key detected (Z_AI_API_KEY). Select "Z.AI API Key" option to use it.',
            );
          } else {
            onAuthError('No authentication method selected.');
          }
        } else if (process.env['GEMINI_API_KEY']) {
          onAuthError(
            'Existing API key detected (GEMINI_API_KEY). Select "Gemini API Key" option to use it.',
          );
        } else {
          onAuthError('No authentication method selected.');
        }
        return;
      }

      if (!isCodinGLM() && effectiveAuthType === AuthType.USE_GEMINI) {
        const key = await reloadApiKey(); // Use the unified function
        if (!key) {
          setAuthState(AuthState.AwaitingApiKeyInput);
          return;
        }
      }

      const error = validateAuthMethodWithSettings(effectiveAuthType, settings);
      if (error) {
        onAuthError(error);
        return;
      }

      const defaultAuthType = process.env['GEMINI_DEFAULT_AUTH_TYPE'];
      if (
        defaultAuthType &&
        !Object.values(AuthType).includes(defaultAuthType as AuthType)
      ) {
        onAuthError(
          `Invalid value for GEMINI_DEFAULT_AUTH_TYPE: "${defaultAuthType}". ` +
            `Valid values are: ${Object.values(AuthType).join(', ')}.`,
        );
        return;
      }

      try {
        await config.refreshAuth(effectiveAuthType);

        debugLogger.log(`Authenticated via "${effectiveAuthType}".`);
        setAuthError(null);
        setAuthState(AuthState.Authenticated);
      } catch (e) {
        onAuthError(`Failed to login. Message: ${getErrorMessage(e)}`);
      }
    })();
  }, [
    settings,
    config,
    authState,
    setAuthState,
    setAuthError,
    onAuthError,
    reloadApiKey,
  ]);

  return {
    authState,
    setAuthState,
    authError,
    onAuthError,
    apiKeyDefaultValue,
    reloadApiKey,
  };
};
