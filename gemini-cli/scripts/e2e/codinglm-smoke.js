#!/usr/bin/env node
/**
 * Simple CodinGLM CLI smoke test
 *
 * Usage:
 *   npm run e2e:smoke
 *
 * Requirements:
 *   - Build the CLI first (`npm run build --workspace @codinglm/cli`)
 *   - Export Z_AI_API_KEY (or compatible env var) pointing at a valid token
 */

import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const repoRoot = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..');
const cliDist = path.resolve(repoRoot, 'packages/cli/dist/index.js');

if (!existsSync(cliDist)) {
  console.error('❌ Build artifacts not found.');
  console.error('Run `npm run build --workspace @codinglm/cli` before running the smoke test.');
  process.exit(1);
}

const apiKey =
  process.env['Z_AI_API_KEY'] ||
  process.env['ZAI_API_KEY'] ||
  process.env['CODINGLM_API_KEY'];

if (!apiKey) {
  console.error('❌ Missing Z_AI_API_KEY (or compatible) environment variable.');
  process.exit(1);
}

const prompt =
  process.env['CODINGLM_SMOKE_PROMPT'] ||
  'Reply with the exact text "SMOKE_OK" and nothing else.';
const expected = 'SMOKE_OK';
const modelFlag = process.env['CODINGLM_SMOKE_MODEL']
  ? ['--model', process.env['CODINGLM_SMOKE_MODEL']]
  : [];

const args = [
  cliDist,
  '--non-interactive',
  prompt,
  '--output',
  'text',
  ...modelFlag,
];

console.log(`🚀 Running CodinGLM CLI smoke test (${path.relative(repoRoot, cliDist)})`);

const child = spawn('node', args, {
  cwd: repoRoot,
  env: {
    ...process.env,
    Z_AI_API_KEY: apiKey,
  },
  stdio: ['ignore', 'pipe', 'pipe'],
});

let stdout = '';
child.stdout.on('data', (chunk) => {
  stdout += chunk.toString();
  process.stdout.write(chunk);
});
child.stderr.on('data', (chunk) => process.stderr.write(chunk));

child.on('close', (code) => {
  if (code !== 0) {
    console.error(`❌ CLI exited with status ${code}`);
    process.exit(code ?? 1);
  }

  const normalized = stdout.trim();
  if (!normalized.includes(expected)) {
    console.error('❌ Smoke assertion failed. Expected response not found.');
    process.exit(1);
  }

  const hash = createHash('sha256').update(normalized).digest('hex').slice(0, 8);
  console.log(`✅ CodinGLM CLI responded as expected (hash ${hash})`);
  process.exit(0);
});
