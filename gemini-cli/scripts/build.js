/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { execSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, '..');

// npm install if node_modules was removed (e.g. via npm run clean or scripts/clean.js)
if (!existsSync(join(root, 'node_modules'))) {
  execSync('npm install', { stdio: 'inherit', cwd: root });
}

// build all workspaces/packages
execSync('npm run generate', { stdio: 'inherit', cwd: root });
execSync('npm run build --workspaces', { stdio: 'inherit', cwd: root });

// also build container image if sandboxing is enabled
// skip (-s) npm install + build since we did that above
const requireSandboxBuild =
  process.env.REQUIRE_SANDBOX_BUILD === '1' ||
  process.env.REQUIRE_SANDBOX_BUILD === 'true';

try {
  execSync('node scripts/sandbox_command.js -q', {
    stdio: 'inherit',
    cwd: root,
  });
  if (
    process.env.BUILD_SANDBOX === '1' ||
    process.env.BUILD_SANDBOX === 'true'
  ) {
    execSync('node scripts/build_sandbox.js -s', {
      stdio: 'inherit',
      cwd: root,
    });
  }
} catch (error) {
  // Properly handle sandbox build failures
  const errorMessage = error instanceof Error ? error.message : String(error);

  if (requireSandboxBuild) {
    // Fail the build if sandbox is required
    console.error('❌ FATAL: Sandbox build failed and REQUIRE_SANDBOX_BUILD is set');
    console.error('Error:', errorMessage);
    process.exit(1);
  } else {
    // Log warning but continue if sandbox is optional
    console.warn('⚠️  Warning: Sandbox build failed (skipping)');
    console.warn('Set REQUIRE_SANDBOX_BUILD=1 to make this error fatal');
    console.warn('Error details:', errorMessage);
  }
}
