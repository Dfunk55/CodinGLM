/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import fs from 'node:fs';
import path from 'node:path';

const rootDir = process.cwd();

function updatePackageJson(packagePath, updateFn) {
  const packageJsonPath = path.resolve(rootDir, packagePath);
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
  updateFn(packageJson);
  fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
}

// Copy bundle directory into packages/cli
const sourceBundleDir = path.resolve(rootDir, 'bundle');
const destBundleDir = path.resolve(rootDir, 'packages/cli/bundle');

if (fs.existsSync(sourceBundleDir)) {
  fs.rmSync(destBundleDir, { recursive: true, force: true });
  fs.cpSync(sourceBundleDir, destBundleDir, { recursive: true });
  console.log('Copied bundle/ directory to packages/cli/');
} else {
  console.error(
    'Error: bundle/ directory not found at project root. Please run `npm run bundle` first.',
  );
  process.exit(1);
}

// Overwrite the .npmrc in the core package to point to the GitHub registry.
const coreNpmrcPath = path.resolve(rootDir, 'packages/core/.npmrc');
fs.writeFileSync(
  coreNpmrcPath,
  '@codinglm:registry=https://npm.pkg.github.com/',
);
console.log('Wrote .npmrc for @codinglm scope to packages/core/');

// Update @codinglm/cli
updatePackageJson('packages/cli/package.json', (pkg) => {
  pkg.name = '@codinglm/cli';
  pkg.files = ['bundle/'];
  pkg.bin = {
    codinglm: 'bundle/codinglm.js',
  };

  // Remove fields that are not relevant to the bundled package.
  delete pkg.dependencies;
  delete pkg.devDependencies;
  delete pkg.scripts;
  delete pkg.main;
  delete pkg.config; // Deletes the sandboxImageUri
});

// Update @codinglm/a2a-server
updatePackageJson('packages/a2a-server/package.json', (pkg) => {
  pkg.name = '@codinglm/a2a-server';
});

// Update @codinglm/core
updatePackageJson('packages/core/package.json', (pkg) => {
  pkg.name = '@codinglm/core';
});

console.log('Successfully prepared packages for GitHub release.');
