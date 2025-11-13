/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { writeFileSync } from 'node:fs';
import { wasmLoader } from 'esbuild-plugin-wasm';

let esbuild;
try {
  esbuild = (await import('esbuild')).default;
} catch (_error) {
  console.warn('esbuild not available, skipping bundle step');
  process.exit(0);
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const require = createRequire(import.meta.url);
const pkg = require(path.resolve(__dirname, 'package.json'));
const punycodeModule = require.resolve('punycode/', { paths: [__dirname] });

function createWasmPlugins() {
  const wasmBinaryPlugin = {
    name: 'wasm-binary',
    setup(build) {
      build.onResolve({ filter: /\.wasm\?binary$/ }, (args) => {
        const specifier = args.path.replace(/\?binary$/, '');
        const resolveDir = args.resolveDir || '';
        const isBareSpecifier =
          !path.isAbsolute(specifier) &&
          !specifier.startsWith('./') &&
          !specifier.startsWith('../');

        let resolvedPath;
        if (isBareSpecifier) {
          resolvedPath = require.resolve(specifier, {
            paths: resolveDir ? [resolveDir, __dirname] : [__dirname],
          });
        } else {
          resolvedPath = path.isAbsolute(specifier)
            ? specifier
            : path.join(resolveDir, specifier);
        }

        return { path: resolvedPath, namespace: 'wasm-embedded' };
      });
    },
  };

  return [wasmBinaryPlugin, wasmLoader({ mode: 'embedded' })];
}

const external = [
  '@lydell/node-pty',
  'node-pty',
  '@lydell/node-pty-darwin-arm64',
  '@lydell/node-pty-darwin-x64',
  '@lydell/node-pty-linux-x64',
  '@lydell/node-pty-win32-arm64',
  '@lydell/node-pty-win32-x64',
];

const baseConfig = {
  bundle: true,
  platform: 'node',
  format: 'esm',
  external,
  loader: { '.node': 'file' },
  write: true,
};

// Removed the legacy Google-specific bundle; CodinGLM bundles only codinglm.

const codinglmConfig = {
  ...baseConfig,
  banner: {
    js: `import { createRequire } from 'module'; const require = createRequire(import.meta.url); globalThis.__filename = require('url').fileURLToPath(import.meta.url); globalThis.__dirname = require('path').dirname(globalThis.__filename);`,
  },
  entryPoints: ['packages/cli/index-codinglm.ts'],
  outfile: 'bundle/codinglm.js',
  define: {
    'process.env.CLI_VERSION': JSON.stringify(pkg.version),
  },
  plugins: createWasmPlugins(),
  alias: {
    'is-in-ci': path.resolve(__dirname, 'packages/cli/src/patches/is-in-ci.ts'),
    '@codinglm/core': path.resolve(
      __dirname,
      'packages/core/index.ts',
    ),
    '@codinglm/core/llm': path.resolve(__dirname, 'packages/core/src/llm'),
    '@codinglm/genai': path.resolve(
      __dirname,
      'packages/core/src/shim/genai.ts',
    ),
    punycode: punycodeModule,
  },
  metafile: true,
};

const a2aServerConfig = {
  ...baseConfig,
  banner: {
    js: `const require = (await import('module')).createRequire(import.meta.url); globalThis.__filename = require('url').fileURLToPath(import.meta.url); globalThis.__dirname = require('path').dirname(globalThis.__filename);`,
  },
  entryPoints: ['packages/a2a-server/src/http/server.ts'],
  outfile: 'packages/a2a-server/dist/a2a-server.mjs',
  define: {
    'process.env.CLI_VERSION': JSON.stringify(pkg.version),
  },
  plugins: createWasmPlugins(),
  alias: {
    '@codinglm/genai': path.resolve(
      __dirname,
      'packages/core/src/shim/genai.ts',
    ),
    '@codinglm/core': path.resolve(__dirname, 'packages/core/index.ts'),
    punycode: punycodeModule,
  },
};

Promise.allSettled([
  esbuild.build(codinglmConfig).then(({ metafile }) => {
    if (process.env.DEV === 'true') {
      writeFileSync(
        './bundle/esbuild-codinglm.json',
        JSON.stringify(metafile, null, 2),
      );
    }
  }),
  esbuild.build(a2aServerConfig),
]).then((results) => {
  const [codinglmResult, a2aResult] = results;
  if (codinglmResult.status === 'rejected') {
    console.error('codinglm.js build failed:', codinglmResult.reason);
    process.exit(1);
  }
  // error in a2a-server bundling will not stop gemini.js bundling process
  if (a2aResult.status === 'rejected') {
    console.warn('a2a-server build failed:', a2aResult.reason);
  }
});
