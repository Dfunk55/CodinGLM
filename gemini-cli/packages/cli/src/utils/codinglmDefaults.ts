/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { AuthType } from '@codinglm/core';

const DEFAULT_Z_AI_BASE_URL = 'https://api.z.ai/api/coding/paas/v4';
const DEFAULT_CODINGLM_MODEL = 'glm-4.6';

export function configureCodinglmEnvironment(): void {
  process.env['CODINGLM'] = '1';

  if (!process.env['Z_AI_BASE_URL'] && !process.env['ZAI_BASE_URL']) {
    process.env['Z_AI_BASE_URL'] = DEFAULT_Z_AI_BASE_URL;
  }

  if (!process.env['GEMINI_MODEL']) {
    process.env['GEMINI_MODEL'] =
      process.env['CODINGLM_MODEL'] ?? DEFAULT_CODINGLM_MODEL;
  }

  if (!process.env['GEMINI_DEFAULT_AUTH_TYPE']) {
    process.env['GEMINI_DEFAULT_AUTH_TYPE'] = AuthType.USE_Z_AI;
  }

  if (!process.env['Z_AI_API_KEY'] && process.env['ZAI_API_KEY']) {
    process.env['Z_AI_API_KEY'] = process.env['ZAI_API_KEY']!;
  }
}
