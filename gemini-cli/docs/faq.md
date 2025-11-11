# Frequently Asked Questions (FAQ)

This page provides answers to common questions and solutions to frequent
problems encountered while using CodinGLM CLI.

## General issues

### Why am I getting an `API error: 429 - Resource exhausted`?

This error indicates that you have exceeded your API request limit. The GLM
endpoints enforce rate limits to prevent abuse and ensure fair usage.

To resolve this, you can:

- **Check your usage:** Review your API usage inside the
  [Zhipu AI console](https://open.bigmodel.cn/) or your internal billing
  dashboard.
- **Optimize your prompts:** If you are making many requests in a short period,
  try to batch your prompts or introduce delays between requests.
- **Request a quota increase:** If you consistently need a higher limit, contact
  your Z.AI account team or submit a ticket through the console.

### Why am I getting an `ERR_REQUIRE_ESM` error when running `npm run start`?

This error typically occurs in Node.js projects when there is a mismatch between
CommonJS and ES Modules.

This is often due to a misconfiguration in your `package.json` or
`tsconfig.json`. Ensure that:

1.  Your `package.json` has `"type": "module"`.
2.  Your `tsconfig.json` has `"module": "NodeNext"` or a compatible setting in
    the `compilerOptions`.

If the problem persists, try deleting your `node_modules` directory and
`package-lock.json` file, and then run `npm install` again.

### Why don't I see cached token counts in my stats output?

Cached token information is only displayed when cached tokens are being used.
This capability is available for API-key flows (GLM 4.x over Z.AI or compatible
gateways) but not for legacy OAuth connectors. Some upstream providers simply do
not expose cached content information. You can always view total token usage via
the `/stats` command or by querying your Z.AI billing dashboard.

## Installation and updates

### How do I update CodinGLM CLI to the latest version?

If you installed it globally via `npm`, update it using the command
`npm install -g @codinglm/cli@latest`. If you compiled it from source, pull
the latest changes from the repository, and then rebuild using the command
`npm run build`.

## Platform-specific issues

### Why does the CLI crash on Windows when I run a command like `chmod +x`?

Commands like `chmod` are specific to Unix-like operating systems (Linux,
macOS). They are not available on Windows by default.

To resolve this, you can:

- **Use Windows-equivalent commands:** Instead of `chmod`, you can use `icacls`
  to modify file permissions on Windows.
- **Use a compatibility layer:** Tools like Git Bash or Windows Subsystem for
  Linux (WSL) provide a Unix-like environment on Windows where these commands
  will work.

## Configuration

### How do I change the GLM endpoint CodinGLM CLI uses?

Most users can stick with the default GLM-4.6 endpoint, but enterprise tenants
can override it by updating `.gemini/settings.json`:

```json
{
  "llm": {
    "baseUrl": "https://your-proxy.example.com/v1beta",
    "model": "glm-4.6"
  }
}
```

You can also set `Z_AI_BASE_URL` in the environment for quick testing. This lets
you point CodinGLM CLI at self-hosted proxies or staging gateways.

To make this setting permanent, add this line to your shell's startup file
(e.g., `~/.bashrc`, `~/.zshrc`).

### What is the best way to store my API keys securely?

Exposing API keys in scripts or checking them into source control is a security
risk.

To store your API keys securely, you can:

- **Use a `.env` file:** Create a `.env` file in your project's `.gemini`
  directory (`.gemini/.env`) and store your keys there. CodinGLM CLI will
  automatically load these variables.
- **Use your system's keyring:** For the most secure storage, use your operating
  system's secret management tool (like macOS Keychain, Windows Credential
  Manager, or a secret manager on Linux). You can then have your scripts or
  environment load the key from the secure storage at runtime.

### Where are the CodinGLM CLI configuration and settings files stored?

The CodinGLM CLI configuration is stored in two `settings.json` files:

1.  In your home directory: `~/.gemini/settings.json`.
2.  In your project's root directory: `./.gemini/settings.json`.

Refer to [CodinGLM CLI Configuration](./get-started/configuration.md) for more
details.

## Z.AI subscription and billing FAQs

### Where can I review my GLM-4.6 subscription details?

Visit the [Zhipu AI console](https://open.bigmodel.cn/) and open **Account →
Plans**. The page lists your current Coding Plan tier, renewal date, and any
consumption-based limits your organization negotiated.

### How do I confirm that higher limits are active?

CodinGLM CLI automatically detects quota upgrades after you restart the CLI and
refresh credentials. If you recently upgraded, restart the CLI or run
`/auth reload` to pull the new entitlements from Z.AI. You can also verify your
token pool inside the console under **Usage Analytics**.

### What terms and privacy policy apply when I use CodinGLM CLI with Z.AI?

Your prompts and files are governed by the
[Zhipu AI API Service Terms](https://open.bigmodel.cn/usercenter/protocol) and
[privacy notice](https://open.bigmodel.cn/usercenter/privacy). CodinGLM CLI does
not collect or process your data beyond what is necessary to fulfill each API
call. See [Terms & Privacy](./tos-privacy.md) for more detail.

### I upgraded but still hit quota errors. What should I do?

Double-check that the CLI is using the API key attached to the upgraded
subscription. If you manage multiple tenants, confirm that the key matches the
plan with the higher quota. If the issue persists, open a ticket with Z.AI and
include your request ID from the CLI logs so they can trace it.

### Does Z.AI train on my CodinGLM CLI data?

The Z.AI privacy notice describes how prompts and files are handled. Paid Coding
Plan tiers default to **no** training on your data unless you explicitly opt in.
Confirm the setting for your organization inside the console or with your
account team before sharing sensitive information.

## Not seeing your question?

Search the
[CodinGLM CLI Q&A discussions on GitHub](https://github.com/Dfunk55/CodinGLM/discussions/categories/q-a)
or
[start a new discussion on GitHub](https://github.com/Dfunk55/CodinGLM/discussions/new?category=q-a)
