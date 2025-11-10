#!/usr/bin/env node
import { promises as fs } from 'node:fs';
import { join } from 'node:path';

const root = process.argv[2] ?? process.cwd();
const patterns = [
  // [searchRegex, replacement]
  [/from\s+['"]@google\/gemini-cli-core['"]/g, "from '@codinglm/core'"],
  [/from\s+['"]@google\/genai['"]/g, "from '@codinglm/genai'"],
];

const includeDirs = [
  'packages/cli/src',
  'packages/a2a-server/src',
  'packages/vscode-ide-companion/src',
  'packages/core/src',
];

async function* walk(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  for (const e of entries) {
    const full = join(dir, e.name);
    if (e.isDirectory()) {
      if (e.name === '__snapshots__') continue;
      if (e.name === 'dist') continue;
      if (e.name === 'generated') continue;
      yield* walk(full);
    } else if (e.isFile()) {
      if (!/\.(ts|tsx|js|mjs)$/.test(e.name)) continue;
      if (/\.test\.(ts|tsx|js)$/.test(e.name)) continue;
      yield full;
    }
  }
}

async function processFile(file) {
  let text = await fs.readFile(file, 'utf8');
  let changed = false;
  for (const [re, repl] of patterns) {
    const newText = text.replace(re, repl);
    if (newText !== text) {
      text = newText;
      changed = true;
    }
  }
  if (changed) {
    await fs.writeFile(file, text, 'utf8');
    console.log('updated', file);
  }
}

const targets = includeDirs.map((d) => join(root, d));
for (const dir of targets) {
  for await (const file of walk(dir)) {
    await processFile(file);
  }
}

