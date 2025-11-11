# CodinGLM CLI: License, Terms of Service, and Privacy Notices

CodinGLM CLI is an open-source workspace agent that connects directly to Zhipu
AI's GLM models. This document explains how licensing works for the CLI itself,
which service agreements apply when you call GLM endpoints, and how to control
telemetry emitted by the tool.

## License

- **Code license:** [Apache 2.0](../LICENSE). You can modify and redistribute
  the CLI under the terms of that license.
- **Model & API usage:** When you supply a `Z_AI_API_KEY` (or the alias
  `ZAI_API_KEY`), your prompts are processed by Zhipu AI (Z.AI). Your use of
  those APIs is covered by your agreement with Z.AI, not by the CodinGLM
  license.

## Applicable service terms

CodinGLM CLI supports multiple authentication flows. Make sure you follow the
terms that match the credentials you configure.

| Authentication Method     | Service(s)                              | Terms of Service                                                                 | Privacy Notice                                                                    |
| :------------------------ | :-------------------------------------- | :------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------- |
| `Z_AI_API_KEY` / `ZAI_API_KEY` | GLM-4.6 Coding Plan (default)          | [Zhipu AI API Service Terms](https://open.bigmodel.cn/usercenter/protocol)       | [Zhipu AI Privacy Notice](https://open.bigmodel.cn/usercenter/privacy)            |
| `GEMINI_*` env vars (legacy)   | Upstream gemini-cli compatibility mode | Refer to your original provider agreement. CodinGLM does **not** bundle third-party credentials. | Refer to the privacy notice for the provider you configured.                      |

> **Note:** Legacy `.gemini` directories, schemas, and `GEMINI_*` environment
> variables remain for compatibility with upstream workflows. They will continue
> to function, but CodinGLM does not broker access to the original CodinGLM
> service providers.

## Enterprise usage

Organizations can point CodinGLM CLI at private Z.AI gateways or self-hosted
proxies. In those cases, your internal contract with Z.AI (or your proxy
provider) governs data handling. Confirm with your legal team which agreement
covers each environment before rolling the CLI out broadly.

## Usage statistics & telemetry

CodinGLM CLI can emit local telemetry for debugging or ship OpenTelemetry data
to your own collector. By default the CLI **does not** send usage statistics to
CodinGLM or Z.AI.

To opt in or opt out, edit `telemetry` in `.gemini/settings.json` and review the
[telemetry guide](./cli/telemetry.md). You can also set
`GEMINI_TELEMETRY_ENABLED=false` (legacy name retained for compatibility) to
disable telemetry entirely.

## Questions?

- [Quota & Pricing](./quota-and-pricing.md) describes cost controls for GLM-4.6.
- [Authentication](./get-started/authentication.md) covers how to provide keys
  and rotate them safely.
- [Security Policy](../SECURITY.md) explains how to report issues privately.

Always defer to your Z.AI contract and privacy notice for the final word on data
usage. If you are unsure which agreement applies, pause usage until you receive
guidance from your account team or legal counsel.
