# CodinGLM CLI Authentication Setup

CodinGLM CLI authenticates against the Zhipu AI CodinGLM platform. To run the
agent you only need to supply an API key via the `Z_AI_API_KEY` environment
variable (or the compatibility alias `ZAI_API_KEY`). Unlike the upstream Gemini
CLI, the CodinGLM build does **not** expose Google account login or Vertex AI
workflows—the GLM-4.6 API key path is the single, secure authentication method.

## Supported authentication modes

| Mode | When to use it | How it works |
| ---- | -------------- | ------------ |
| Z.AI API key (interactive) | Daily workflows on your laptop or workstation | The CLI reads `Z_AI_API_KEY` from your shell or `.env` file before launching the REPL. |
| Z.AI API key (headless / CI) | Scripts, cron jobs, GitHub Actions, or remote servers | Provide the same environment variable via secret management and run `codinglm -p ...`. |

> Legacy Gemini account login, Gemini API keys, and Vertex AI credentials remain
> available only when you run the upstream Google-branded CLI. If you need those
> flows, install `@google/gemini-cli` separately.

## Step 1: Generate a CodinGLM API key

1. Sign in to your CodinGLM / Zhipu AI account in the customer console.
2. Create (or copy) an API key scoped to the GLM-4.6 model.
3. Store the key in a secret manager or password vault—you will treat it like a
   production credential.

Each account can create multiple keys; rotate them regularly and delete unused
keys in the console if they are compromised.

## Step 2: Provide the key to the CLI

CodinGLM CLI looks for `Z_AI_API_KEY` first and falls back to `ZAI_API_KEY` for
compatibility with older scripts. Set either variable before running the CLI.

### Temporary export for the current shell

```bash
export Z_AI_API_KEY="your-secret-key"
# optional alias if you use legacy scripts
export ZAI_API_KEY="$Z_AI_API_KEY"
codinglm
```

The export lasts until you close the shell session.

### Persistent export in your shell profile

Add the export to `~/.zshrc`, `~/.bashrc`, or the profile your shell loads:

```bash
echo 'export Z_AI_API_KEY="your-secret-key"' >> ~/.zshrc
source ~/.zshrc
```

This ensures new terminals inherit the variable automatically.

### Using `.env` files

CodinGLM CLI automatically loads environment variables in the following order:

1. `.env` in the current working directory.
2. The nearest `.env` file up the directory tree until the repo root (identified
   by `.git`) or your home directory.
3. `~/.env`.
4. Project-specific `.gemini/.env` when present. (The CLI still uses the
   upstream `.gemini` directory structure for compatibility.)

A minimal `.env` entry looks like:

```
Z_AI_API_KEY=your-secret-key
```

Place secret `.env` files under `.gitignore` or use the `.gemini/.env` helper so
keys never leave your machine.

## Headless and CI/CD usage

For scripts or automation, make sure the environment variable is available to
that process before invoking the CLI:

```bash
Z_AI_API_KEY="$CI_ZAI_KEY" codinglm -p "Summarize PR #123"
```

Recommended practices:

- Store the key in your CI secret manager (GitHub Actions secrets, Cloud Build
  substitutions, etc.).
- Pass it to the workflow as an environment variable rather than committing it
  to files.
- Combine `--output-format json` or `--output-format stream-json` with prompts
  for structured automation results.

## Verifying authentication

Run `codinglm --auth-check` (or start the CLI normally). If the CLI cannot find
`Z_AI_API_KEY`, it emits an error similar to:

```
Error: Z_AI_API_KEY is required when using the Z.AI provider.
```

Double-check that the `Z_AI_API_KEY` export is in scope, and confirm there are no
extra quotes or spaces. You can also run `env | grep Z_AI` to ensure the value is
visible to the current shell.

## Troubleshooting

- **"Z_AI_API_KEY is required"** – The variable is unset. Export it or create a
  project `.env` file.
- **Multiple keys in the same session** – The CLI uses the first non-empty
  variable it finds. Clear duplicates with `unset Z_AI_API_KEY ZAI_API_KEY` and
  re-export the one you intend to use.
- **Running both CodinGLM and Gemini CLI** – Keep keys in separate `.env`
  files. For example, use `.gemini/.env` for CodinGLM and `.env` for Gemini to
  avoid mixing credentials.

## Legacy authentication flows

If you still need to sign in with a Google account, a Gemini API key, or Vertex
AI credentials, install the upstream package:

```bash
npm install -g @google/gemini-cli
```

Launch that binary with the `gemini` command and follow the original
[Gemini authentication guide](https://github.com/google-gemini/gemini-cli). Keep
those profiles completely separate from your `codinglm` configuration to avoid
confusing the CLI about which provider to use.
