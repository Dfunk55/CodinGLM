# Welcome to the CodinGLM CLI documentation

This site is the home for everything you need to install, configure, extend,
and operate CodinGLM CLI. The CLI layers CodinGLM defaults, tooling, and guard
rails on top of the open-source CodinGLM CLI runtime so you can work with the
GLM-4.6 model from Zhipu AI directly inside your terminal.

## Overview

CodinGLM CLI brings GLM-4.6's coding-focused capabilities to an interactive
Read-Eval-Print Loop (REPL). The user-facing CLI (`packages/cli`) communicates
with a local core service (`packages/core`) that manages requests to the Z.AI
CodinGLM API and orchestrates tools such as shell access, filesystem helpers,
MCP servers, and web utilities.

## Navigating the documentation

This documentation is organized into the following sections:

### Get started

- **[CodinGLM CLI Quickstart](./get-started/index.md):** Install, authenticate,
  and run CodinGLM CLI in a few minutes.
- **[Installation](./get-started/installation.md):** All supported
  installation / execution paths.
- **[Authentication](./get-started/authentication.md):** Configure CodinGLM CLI
  with your `Z_AI_API_KEY` (or compatible env vars).
- **[Configuration](./get-started/configuration.md):** Understand config layers
  and available settings.
- **[Examples](./get-started/examples.md):** Real-world prompts and workflows to
  try inside CodinGLM CLI.

### CLI

- **[CLI overview](./cli/index.md):** Learn the high-level surface area of the
  terminal app.
- **[Commands](./cli/commands.md):** Detailed reference for every CLI flag and
  sub-command.
- **[Enterprise](./cli/enterprise.md):** Guidance for rolling CodinGLM CLI out
  across larger orgs.
- **[Themes](./cli/themes.md):** Theme gallery and customization options.
- **[Token Caching](./cli/token-caching.md):** Keep CodinGLM tokens fresh and
  avoid unnecessary prompts.
- **[Tutorials](./cli/tutorials.md):** Step-by-step walkthroughs for common
  tasks.
- **[Checkpointing](./cli/checkpointing.md):** Save and resume complex
  conversations.
- **[Telemetry](./cli/telemetry.md):** Observe what data the CLI emits and how
  to control it.
- **[Trusted Folders](./cli/trusted-folders.md):** Protect sensitive directories
  when granting tool access.

### Core

- **[CodinGLM CLI core overview](./core/index.md):** Explore how the backend
  service processes requests.
- **[Memport](./core/memport.md):** Use the Memory Import Processor to preload
  large contexts.
- **[Tools API](./core/tools-api.md):** Build and register new tools.
- **[Policy Engine](./core/policy-engine.md):** Enforce guard rails around tool
  execution.

### Tools

- **[CodinGLM CLI tools overview](./tools/index.md):** Inventory of built-in
  tools.
- **[File System Tools](./tools/file-system.md):** `read_file`, `write_file`,
  and other filesystem helpers.
- **[MCP servers](./tools/mcp-server.md):** Extend CodinGLM CLI with MCP.
- **[Multi-File Read Tool](./tools/multi-file.md):** Drive `read_many_files` for
  larger reviews.
- **[Shell Tool](./tools/shell.md):** Run commands via `run_shell_command`.
- **[Web Fetch Tool](./tools/web-fetch.md):** Pull remote content into the
  session.
- **[Web Search Tool](./tools/web-search.md):** Query search APIs from the CLI.
- **[Memory Tool](./tools/memory.md):** Persist workspace memories.
- **[Todo Tool](./tools/todos.md):** Capture and edit TODO lists inline.

### Extensions

- **[Extensions](./extensions/index.md):** Add extra functionality.
- **[Get Started with Extensions](./extensions/getting-started-extensions.md):**
  Build your first extension.
- **[Extension Releasing](./extensions/extension-releasing.md):** Ship CodinGLM
  CLI extensions to other users.

### IDE integration

- **[IDE Integration](./ide-integration/index.md):** Connect CodinGLM CLI to VS
  Code and other editors.
- **[IDE Companion Extension Spec](./ide-integration/ide-companion-spec.md):**
  Protocol reference for building IDE companions.

### About the CodinGLM CLI project

- **[Architecture Overview](./architecture.md):** High-level design of the CLI
  runtime and how the pieces fit together.
- **[Contributing & Development Guide](../CONTRIBUTING.md):** Setup, build, test,
  and coding conventions.
- **[NPM](./npm.md):** How packages inside the monorepo are structured.
- **[Troubleshooting Guide](./troubleshooting.md):** Solutions to common
  problems.
- **[FAQ](./faq.md):** Frequently asked questions.
- **[Terms of Service and Privacy Notice](./tos-privacy.md):** Policies covering
  CodinGLM CLI usage.
- **[Releases](./releases.md):** Track versions and release cadence.

We hope these docs help you get the most from CodinGLM CLI!