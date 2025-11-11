#!/usr/bin/env node

/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { debugLogger, FatalError } from '@codinglm/core';
import { configureCodinglmEnvironment } from './src/utils/codinglmDefaults.js';

configureCodinglmEnvironment();

// Note: API key validation is now handled by validateNonInteractiveAuth()
// when actually needed, allowing users to run --help, --version, etc.
// without requiring authentication first.

import('./src/gemini.js')
  .then(({ main }) =>
    main().catch((error) => {
      if (error instanceof FatalError) {
        let errorMessage = error.message;
        if (!process.env['NO_COLOR']) {
          errorMessage = `\x1b[31m${errorMessage}\x1b[0m`;
        }
        debugLogger.error(errorMessage);
        process.exit(error.exitCode);
      }
      debugLogger.error('An unexpected critical error occurred:');
      if (error instanceof Error) {
        debugLogger.error(error.stack);
      } else {
        debugLogger.error(String(error));
      }
      process.exit(1);
    }),
  )
  .catch((error) => {
    debugLogger.error('Failed to initialize CodingLM CLI:');
    if (error instanceof Error) {
      debugLogger.error(error.stack);
    } else {
      debugLogger.error(String(error));
    }
    process.exit(1);
  });
