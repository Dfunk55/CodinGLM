# CodinGLM Installation, Execution, and Deployment

Install and run CodinGLM. This document provides an overview of CodinGLM's
installation methods and deployment architecture.

## How to install and/or run CodinGLM

There are several ways to run CodinGLM depending on your needs:

- Standard installation (recommended)
- Optional sandbox container
- From source (for contributors)

### 1. Standard installation (recommended for standard users)

This is the recommended way for end-users to install CodinGLM from the NPM registry.

- **Global install:**

  ```bash
  npm install -g @codinglm/cli
  ```

  Then, run the CLI from anywhere:

  ```bash
  codinglm
  ```

- **NPX execution:**

  ```bash
  # Execute without a global install
  npx @codinglm/cli
  ```

### 2. Run in a sandbox (Docker/Podman)

For security and isolation, CodinGLM can be run inside a container. This is
the default way that the CLI executes tools that might have side effects.

- **Directly from the Registry:** You can run the published sandbox image
  directly. This is useful for environments where you only have Docker and want
  to run the CLI.
  ```bash
  # Example: run a sandbox image you’ve prepared
  docker run --rm -it codinglm/sandbox:latest
  ```
- **Using the `--sandbox` flag:** If you have Gemini CLI installed locally
  (using the standard installation described above), you can instruct it to run
  inside the sandbox container.
  ```bash
  codinglm --sandbox -y -p "your prompt here"
  ```

### 3. Run from source (recommended for CodinGLM contributors)

Contributors to the project will want to run the CLI directly from the source
code.

- **Development Mode:** This method provides hot-reloading and is useful for
  active development.
  ```bash
  # From the root of the repository
  npm run start
  ```
- **Production-like mode (Linked package):** This method simulates a global
  installation by linking your local package. It's useful for testing a local
  build in a production workflow.

  ```bash
  # Link the local cli package to your global node_modules
  npm link packages/cli

  # Now you can run your local version using the `codinglm` command
  codinglm
  ```

---

### 4. Running the latest CodinGLM commit from GitHub

You can run the most recently committed version of CodinGLM directly from the
GitHub repository.

```bash
# Execute the CLI directly from the main branch on GitHub
npx https://github.com/Dfunk55/CodinGLM
```

## Deployment architecture

The execution methods described above are made possible by the following
architectural components and processes:

**NPM packages**

CodinGLM is a monorepo that publishes two core packages to the NPM
registry:

- `@codinglm/core`: The backend, handling logic and tool execution.
- `@codinglm/cli`: The user-facing frontend.

These packages are used when performing the standard installation and when
running Gemini CLI from the source.

**Build and packaging processes**

There are two distinct build processes used, depending on the distribution
channel:

- **NPM publication:** For publishing to the NPM registry, the TypeScript source
  code in `@codinglm/core` and `@codinglm/cli` is transpiled into
  standard JavaScript using the TypeScript Compiler (`tsc`). The resulting
  `dist/` directory is what gets published in the NPM package. This is a
  standard approach for TypeScript libraries.

- **GitHub `npx` execution:** When running the latest version of CodinGLM
  directly from GitHub, a different process is triggered by the `prepare` script
  in `package.json`. This script uses `esbuild` to bundle the entire application
  and its dependencies into a single, self-contained JavaScript file. This
  bundle is created on-the-fly on the user's machine and is not checked into the
  repository.

**Docker sandbox image**

The Docker-based execution method is supported by a `codinglm-sandbox`
container image. This image is published to a container registry and contains a
pre-installed, global version of CodinGLM.

## Release process

The release process is automated through GitHub Actions. The release workflow
performs the following actions:

1.  Build the NPM packages using `tsc`.
2.  Publish the NPM packages to the artifact registry.
3.  Create GitHub releases with bundled assets.
