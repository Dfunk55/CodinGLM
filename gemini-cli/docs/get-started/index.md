# Get Started with CodinGLM CLI

Welcome to CodinGLM CLI! This guide walks you through the fastest way to
install, authenticate, configure, and start collaborating with the
GLM-4.6-powered agent in your terminal.

## Quickstart: install, authenticate, configure, and run CodinGLM CLI

1. Install the CLI:
   ```bash
   npm install -g @codinglm/cli
   ```
2. Export your Zhipu AI key (or define it in `.env`):
   ```bash
   export Z_AI_API_KEY="your-secret-key"
   ```
3. Launch the agent:
   ```bash
   codinglm
   ```
4. Follow the on-screen prompts to pick a workspace and start chatting.

CodinGLM CLI keeps the battle-tested CodinGLM CLI runtime under the hood, but all
defaults (models, tooling, telemetry, wording) point to CodinGLM and Z.AI.

## Install

The recommended install path is the global `npm` package. You can also run the
CLI through `npx`, from source, or inside the sandbox container. See the
[Installation guide](./installation.md) for every supported option.

## Authenticate

CodinGLM CLI authenticates with the Zhipu AI CodinGLM platform via
`Z_AI_API_KEY` (or the compatible fallback `ZAI_API_KEY`). Head over to the
[Authentication guide](./authentication.md) for instructions on generating a
key, storing it securely, and loading it for both interactive and CI runs.

## Configure

Configuration layers mirror the upstream runtime: defaults, system files,
user/project overrides, environment variables, and CLI flags. Review the
[Configuration reference](./configuration.md) to see every setting, schema, and
recommended layout for the `.gemini` directory that still backs CodinGLM CLI.

## Use

Once the CLI is running, issue natural-language prompts such as
`codinglm -p "Refactor the parser"` or explore the REPL to browse files,
edit code, and invoke tools. The [Examples catalog](./examples.md) collects
popular workflows you can copy and adapt.

## What's next?

- Dive into [CodinGLM CLI tools](../tools/index.md) to learn what the agent can
  execute on your behalf.
- Review the [commands reference](../cli/commands.md) for every flag and
  advanced option.
- Wire up MCP servers via [Tools → MCP Server guide](../tools/mcp-server.md).
