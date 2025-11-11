# CodinGLM CLI: Quotas and Pricing

CodinGLM CLI talks to the GLM-4.6 Coding Plan hosted by Zhipu AI (Z.AI). This
guide explains the available quota tiers, how to upgrade when you outgrow the
free allocation, and how to avoid surprise costs when running large workloads.

Always consult the [official Z.AI pricing page](https://open.bigmodel.cn/pricing)
for the latest numbers—this document summarizes the current defaults.

## Plan types at a glance

| Plan Type            | Ideal For                         | Billing Model                      | Notes                                     |
| -------------------- | --------------------------------- | ---------------------------------- | ----------------------------------------- |
| Free Coding Plan     | Exploration, hobby projects       | Included with every Z.AI account   | Light usage allowance resets daily       |
| Coding Plan Subscription | Individual devs, small teams     | $3/month (USD)                     | Unlimited within fair-use envelope       |
| Pay-as-you-go (API Platform) | Production workloads with strict monitoring | Per-token (input + output)          | Fine-grained control and custom limits   |
| Legacy upstream providers | Migration scenarios only           | Governed by original provider      | `GEMINI_*` env vars retained for parity   |

## Free usage

- Included with every Z.AI account.
- Designed for experimentation and short tasks.
- Daily allowance is published in the console; limits reset automatically.
- When you approach the limit, the CLI surfaces `429 Resource exhausted`
  messages—switch to a paid plan or pause heavy automation until limits reset.

## Coding Plan subscription ($3/month)

- Flat monthly price charged through the [Z.AI console](https://open.bigmodel.cn/).
- Gives you “always-on” access to GLM-4.6 with generous fair-use policies.
- Ideal for developers who want predictable spend without per-token surprises.
- Manage seats, invoices, and payment methods under **Account → Plans**.

## Pay-as-you-go via the API Platform

- Best for production automation, batch jobs, or large agent fleets.
- Billed per token (input + output). Pricing varies by model tier and is listed
  on the [GLM API pricing page](https://open.bigmodel.cn/pricing).
- Lets you configure multiple API keys with different budgets and rate limits.
- Pair with your own observability/alerts to watch usage in real time.

### Tips for managing per-token costs

- Reuse context: store reference material in files or memory instead of pasting
  the same text every turn.
- Prefer `glm-4-flash` when you need fast, lightweight interactions.
- Set `maxOutputTokens` in `.gemini/settings.json` for long-running tasks.
- Use `/stats` to inspect consumption before ending a session.

## Legacy providers (compatibility mode)

CodinGLM CLI still honors `.gemini` directories and `GEMINI_*` environment
variables so teams migrating from the upstream gemini-cli can reuse existing
configs. When you operate in that mode, the quotas and pricing from the
original provider apply. CodinGLM does **not** bundle credentials or manage
those agreements—refer to your original contract for details.

## Monitoring your usage

- Run `/stats` inside the CLI to view per-session token totals.
- Enable telemetry (see [Observability](./cli/telemetry.md)) to push metrics to
  your monitoring stack.
- Review the **Usage Analytics** page in the Z.AI console for organization-wide
  reporting and to export invoices.

## Avoiding throttling

- Batch file scans with `read_many_files` instead of issuing dozens of single
  requests.
- Use `/restore` to resume conversations instead of restarting from scratch.
- If a long-running workflow might exceed quotas, break it into smaller prompts
  or upgrade to the subscription/pay-as-you-go tier before running it.

Have more questions? See the [FAQ](./faq.md) or contact your Z.AI account team.
