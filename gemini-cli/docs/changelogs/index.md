# CodinGLM CLI Changelog

Wondering what's new in CodinGLM CLI? This document provides key highlights and
notable changes to CodinGLM CLI.

## v0.11.0 - CodinGLM CLI weekly update - 2025-10-20

![CodinGLM CLI and Jules](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Jules_Extension_-_Blog_Header_O346JNt.original.png)

- 🎉 **CodinGLM CLI Jules Extension:** Use CodinGLM CLI to orchestrate Jules. Spawn
  remote workers, delegate tedious tasks, or check in on running jobs!
  - Install:
    `gemini extensions install https://github.com/gemini-cli-extensions/jules`
  - Announcement:
    [https://developers.googleblog.com/en/introducing-the-jules-extension-for-gemini-cli/](https://developers.googleblog.com/en/introducing-the-jules-extension-for-gemini-cli/)
- **Stream JSON output:** Stream real-time JSONL events with
  `--output-format stream-json` to monitor AI agent progress when run
  headlessly. ([gif](https://imgur.com/a/0UCE81X),
  [pr](https://github.com/Dfunk55/CodinGLM/pull/10883) by
  [@anj-s](https://github.com/anj-s))
- **Markdown toggle:** Users can now switch between rendered and raw markdown
  display using `alt+m `or` ctrl+m`. ([gif](https://imgur.com/a/lDNdLqr),
  [pr](https://github.com/Dfunk55/CodinGLM/pull/10383) by
  [@srivatsj](https://github.com/srivatsj))
- **Queued message editing:** Users can now quickly edit queued messages by
  pressing the up arrow key when the input is empty.
  ([gif](https://imgur.com/a/ioRslLd),
  [pr](https://github.com/Dfunk55/CodinGLM/pull/10392) by
  [@akhil29](https://github.com/akhil29))
- **JSON web fetch**: Non-HTML content like JSON APIs or raw source code are now
  properly shown to the model (previously only supported HTML)
  ([gif](https://imgur.com/a/Q58U4qJ),
  [pr](https://github.com/Dfunk55/CodinGLM/pull/11284) by
  [@abhipatel12](https://github.com/abhipatel12))
- **Non-interactive MCP commands:** Users can now run MCP slash commands in
  non-interactive mode `gemini "/some-mcp-prompt"`.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/10194) by
  [@capachino](https://github.com/capachino))
- **Removal of deprecated flags:** We’ve finally removed a number of deprecated
  flags to cleanup CodinGLM CLI’s invocation profile:
  - `--all-files` / `-a` in favor of `@` from within CodinGLM CLI.
    ([pr](https://github.com/Dfunk55/CodinGLM/pull/11228) by
    [@allenhutchison](https://github.com/allenhutchison))
  - `--telemetry-*` flags in favor of
    [environment variables](https://github.com/Dfunk55/CodinGLM/pull/11318)
    ([pr](https://github.com/Dfunk55/CodinGLM/pull/11318) by
    [@allenhutchison](https://github.com/allenhutchison))

## v0.10.0 - CodinGLM CLI weekly update - 2025-10-13

- **Polish:** The team has been heads down bug fixing and investing heavily into
  polishing existing flows, tools, and interactions.
- **Interactive Shell Tool calling:** CodinGLM CLI can now also execute
  interactive tools if needed
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/11225) by
  [@galz10](https://github.com/galz10)).
- **Alt+Key support:** Enables broader support for Alt+Key keyboard shortcuts
  across different terminals.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/10767) by
  [@srivatsj](https://github.com/srivatsj)).
- **Telemetry Diff stats:** Track line changes made by the model and user during
  file operations via OTEL.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/10819) by
  [@jerop](https://github.com/jerop)).

## v0.9.0 - CodinGLM CLI weekly update - 2025-10-06

- 🎉 **Interactive Shell:** Run interactive commands like `vim`, `rebase -i`, or
  even `gemini` 😎 directly in CodinGLM CLI:
  - Blog:
    [https://developers.googleblog.com/en/say-hello-to-a-new-level-of-interactivity-in-gemini-cli/](https://developers.googleblog.com/en/say-hello-to-a-new-level-of-interactivity-in-gemini-cli/)
- **Install pre-release extensions:** Install the latest `--pre-release`
  versions of extensions. Used for when an extension’s release hasn’t been
  marked as "latest".
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/10752) by
  [@jakemac53](https://github.com/jakemac53))
- **Simplified extension creation:** Create a new, empty extension. Templates
  are no longer required.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/10629) by
  [@chrstnb](https://github.com/chrstnb))
- **OpenTelemetry GenAI metrics:** Aligns telemetry with industry-standard
  semantic conventions for improved interoperability.
  ([spec](https://opentelemetry.io/docs/concepts/semantic-conventions/),
  [pr](https://github.com/Dfunk55/CodinGLM/pull/10343) by
  [@jerop](https://github.com/jerop))
- **List memory files:** Quickly find the location of your long-term memory
  files with `/memory list`.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/10108) by
  [@sgnagnarella](https://github.com/sgnagnarella))

## v0.8.0 - CodinGLM CLI weekly update - 2025-09-29

- 🎉 **Announcing CodinGLM CLI Extensions** 🎉
  - Completely customize your CodinGLM CLI experience to fit your workflow.
  - Build and share your own CodinGLM CLI extensions with the world.
  - Launching with a growing catalog of community- and partner-built
    extensions.
    - Browse the [extensions gallery](../extensions/index.md) for examples.
  - Easy install:
    - `gemini extensions install <github url|folder path>`
  - Easy management:
    - `gemini extensions install|uninstall|link`
    - `gemini extensions enable|disable`
    - `gemini extensions list|update|new`
  - Or use commands while running with `/extensions list|update`.
  - Everything you need to know:
    [Extensions guide](../extensions/getting-started-extensions.md).
- 🎉 **Our New Home Page & Better Documentation** 🎉
  - Check out our new home page for better getting started material, reference
    documentation, extensions and more!
  - _Homepage:_ [https://geminicli.com](https://geminicli.com)
  - ‼️*NEW documentation:*
    [https://geminicli.com/docs](https://geminicli.com/docs) (Have any
    [suggestions](https://github.com/Dfunk55/CodinGLM/discussions/8722)?)
  - _Extensions:_
    [https://geminicli.com/extensions](https://geminicli.com/extensions)
- **Non-Interactive Allowed Tools:** `--allowed-tools` will now also work in
  non-interactive mode.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/9114) by
  [@mistergarrison](https://github.com/mistergarrison))
- **Terminal Title Status:** See the CLI's real-time status and thoughts
  directly in the terminal window's title by setting `showStatusInTitle: true`.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/4386) by
  [@Fridayxiao](https://github.com/Fridayxiao))
- **Small features, polish, reliability & bug fixes:** A large amount of
  changes, smaller features, UI updates, reliability and bug fixes + general
  polish made it in this week!

## v0.7.0 - CodinGLM CLI weekly update - 2025-09-22

- 🎉**Build your own CodinGLM CLI IDE plugin:** We've published a spec for
  creating IDE plugins to enable rich context-aware experiences and native
  in-editor diffing in your IDE of choice.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/8479) by
  [@skeshive](https://github.com/skeshive))
- 🎉 **CodinGLM CLI extensions**
  - **Flutter:** An early version to help you create, build, test, and run
    Flutter apps with CodinGLM CLI
    ([extension](https://github.com/gemini-cli-extensions/flutter))
  - **nanobanana:** Integrate nanobanana into CodinGLM CLI
    ([extension](https://github.com/gemini-cli-extensions/nanobanana))
- **Telemetry config via environment:** Manage telemetry settings using
  environment variables for a more flexible setup.
  ([docs](https://github.com/Dfunk55/CodinGLM/blob/main/docs/cli/telemetry.md#configuration),
  [pr](https://github.com/Dfunk55/CodinGLM/pull/9113) by
  [@jerop](https://github.com/jerop))
- **​​Experimental todos:** Track and display progress on complex tasks with a
  managed checklist. Off by default but can be enabled via
  `"useWriteTodos": true`
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/8761) by
  [@anj-s](https://github.com/anj-s))
- **Share chat support for tools:** Using `/chat share` will now also render
  function calls and responses in the final markdown file.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/8693) by
  [@rramkumar1](https://github.com/rramkumar1))
- **Citations:** Now enabled for all users
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/8570) by
  [@scidomino](https://github.com/scidomino))
- **Custom commands in Headless Mode:** Run custom slash commands directly from
  the command line in non-interactive mode: `gemini "/joke Chuck Norris"`
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/8305) by
  [@capachino](https://github.com/capachino))
- **Small features, polish, reliability & bug fixes:** A large amount of
  changes, smaller features, UI updates, reliability and bug fixes + general
  polish made it in this week!

## v0.6.0 - CodinGLM CLI weekly update - 2025-09-15

- 🎉 **Higher limits for GLM Coding Plan subscribers:** We’re psyched to
  announce that the $3/month Z.AI Coding Plan now unlocks the full GLM-4.6 quota
  envelope inside CodinGLM CLI.
- 🎉**CodinGLM CLI Databases and BigQuery Extensions:** Connect CodinGLM CLI to all
  of your cloud data with CodinGLM CLI.
  - Announcement and how to get started with each of the below extensions:
    [https://cloud.google.com/blog/products/databases/gemini-cli-extensions-for-google-data-cloud?e=48754805](https://cloud.google.com/blog/products/databases/gemini-cli-extensions-for-google-data-cloud?e=48754805)
  - **AlloyDB:** Interact, manage and observe AlloyDB for PostgreSQL databases
    ([manage](https://github.com/gemini-cli-extensions/alloydb#configuration),
    [observe](https://github.com/gemini-cli-extensions/alloydb-observability#configuration))
  - **BigQuery:** Connect and query your BigQuery datasets or utilize a
    sub-agent for contextual insights
    ([query](https://github.com/gemini-cli-extensions/bigquery-data-analytics#configuration),
    [sub-agent](https://github.com/gemini-cli-extensions/bigquery-conversational-analytics))
  - **Cloud SQL:** Interact, manage and observe Cloud SQL for PostgreSQL
    ([manage](https://github.com/gemini-cli-extensions/cloud-sql-postgresql#configuration),[ observe](https://github.com/gemini-cli-extensions/cloud-sql-postgresql-observability#configuration)),
    Cloud SQL for MySQL
    ([manage](https://github.com/gemini-cli-extensions/cloud-sql-mysql#configuration),[ observe](https://github.com/gemini-cli-extensions/cloud-sql-mysql-observability#configuration))
    and Cloud SQL for SQL Server
    ([manage](https://github.com/gemini-cli-extensions/cloud-sql-sqlserver#configuration),[ observe](https://github.com/gemini-cli-extensions/cloud-sql-sqlserver-observability#configuration))
    databases.
  - **Dataplex:** Discover, manage, and govern data and AI artifacts
    ([extension](https://github.com/gemini-cli-extensions/dataplex#configuration))
  - **Firestore:** Interact with Firestore databases, collections and documents
    ([extension](https://github.com/gemini-cli-extensions/firestore-native#configuration))
  - **Looker:** Query data, run Looks and create dashboards
    ([extension](https://github.com/gemini-cli-extensions/looker#configuration))
  - **MySQL:** Interact with MySQL databases
    ([extension](https://github.com/gemini-cli-extensions/mysql#configuration))
  - **Postgres:** Interact with PostgreSQL databases
    ([extension](https://github.com/gemini-cli-extensions/postgres#configuration))
  - **Spanner:** Interact with Spanner databases
    ([extension](https://github.com/gemini-cli-extensions/spanner#configuration))
  - **SQL Server:** Interact with SQL Server databases
    ([extension](https://github.com/gemini-cli-extensions/sql-server#configuration))
  - **MCP Toolbox:** Configure and load custom tools for more than 30+ data
    sources
    ([extension](https://github.com/gemini-cli-extensions/mcp-toolbox#configuration))
- **JSON output mode:** Have CodinGLM CLI output JSON with `--output-format json`
  when invoked headlessly for easy parsing and post-processing. Includes
  response, stats and errors.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/8119) by
  [@jerop](https://github.com/jerop))
- **Keybinding triggered approvals:** When you use shortcuts (`shift+y` or
  `shift+tab`) to activate YOLO/auto-edit modes any pending confirmation dialogs
  will now approve. ([pr](https://github.com/Dfunk55/CodinGLM/pull/6665)
  by [@bulkypanda](https://github.com/bulkypanda))
- **Chat sharing:** Convert the current conversation to a Markdown or JSON file
  with _/chat share &lt;file.md|file.json>_
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/8139) by
  [@rramkumar1](https://github.com/rramkumar1))
- **Prompt search:** Search your prompt history using `ctrl+r`.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/5539) by
  [@Aisha630](https://github.com/Aisha630))
- **Input undo/redo:** Recover accidentally deleted text in the input prompt
  using `ctrl+z` (undo) and `ctrl+shift+z` (redo).
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/4625) by
  [@masiafrest](https://github.com/masiafrest))
- **Loop detection confirmation:** When loops are detected you are now presented
  with a dialog to disable detection for the current session.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/8231) by
  [@SandyTao520](https://github.com/SandyTao520))
- **Remote OTLP Telemetry:** Send telemetry directly to your preferred OTLP
  backend for a streamlined setup.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/8541) by
  [@jerop](https://github.com/jerop))
- **Visual Mode Indicator Revamp:** ‘shell’, 'accept edits' and 'yolo' modes now
  have colors to match their impact / usage. Input box now also updates.
  ([shell](https://imgur.com/a/DovpVF1),
  [accept-edits](https://imgur.com/a/33KDz3J),
  [yolo](https://imgur.com/a/tbFwIWp),
  [pr](https://github.com/Dfunk55/CodinGLM/pull/8200) by
  [@miguelsolorio](https://github.com/miguelsolorio))
- **Small features, polish, reliability & bug fixes:** A large amount of
  changes, smaller features, UI updates, reliability and bug fixes + general
  polish made it in this week!

## v0.5.0 - CodinGLM CLI weekly update - 2025-09-08

- 🎉**FastMCP + CodinGLM CLI**🎉: Quickly install and manage your CodinGLM CLI MCP
  servers with FastMCP ([video](https://imgur.com/a/m8QdCPh),
  [pr](https://github.com/jlowin/fastmcp/pull/1709) by
  [@jackwotherspoon](https://github.com/jackwotherspoon)**)**
  - Getting started:
    [https://gofastmcp.com/integrations/gemini-cli](https://gofastmcp.com/integrations/gemini-cli)
- **Positional Prompt for Non-Interactive:** Seamlessly invoke CodinGLM CLI
  headlessly via `gemini "Hello"`. Synonymous with passing `-p`.
  ([gif](https://imgur.com/a/hcBznpB),
  [pr](https://github.com/Dfunk55/CodinGLM/pull/7668) by
  [@allenhutchison](https://github.com/allenhutchison))
- **Experimental Tool output truncation:** Enable truncating shell tool outputs
  and saving full output to a file by setting
  `"enableToolOutputTruncation": true `([pr](https://github.com/Dfunk55/CodinGLM/pull/8039)
  by [@SandyTao520](https://github.com/SandyTao520))
- **Edit Tool improvements:** CodinGLM CLI’s ability to edit files should now be
  far more capable. ([pr](https://github.com/Dfunk55/CodinGLM/pull/7679)
  by [@silviojr](https://github.com/silviojr))
- **Custom witty messages:** The feature you’ve all been waiting for…
  Personalized witty loading messages via
  `"ui": { "customWittyPhrases": ["YOLO"]}` in `settings.json`.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/7641) by
  [@JayadityaGit](https://github.com/JayadityaGit))
- **Nested .gitignore File Handling:** Nested `.gitignore` files are now
  respected. ([pr](https://github.com/Dfunk55/CodinGLM/pull/7645) by
  [@gsquared94](https://github.com/gsquared94))
- **Enforced authentication:** System administrators can now mandate a specific
  authentication method via
  `"enforcedAuthType": "oauth-personal|gemini-api-key|…"`in `settings.json`.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/6564) by
  [@chrstnb](https://github.com/chrstnb))
- **A2A development-tool extension:** An RFC for an Agent2Agent
  ([A2A](https://a2a-protocol.org/latest/)) powered extension for developer tool
  use cases.
  ([feedback](https://github.com/Dfunk55/CodinGLM/discussions/7822),
  [pr](https://github.com/Dfunk55/CodinGLM/pull/7817) by
  [@skeshive](https://github.com/skeshive))
- **Hands on Codelab:
  **[https://codelabs.developers.google.com/gemini-cli-hands-on](https://codelabs.developers.google.com/gemini-cli-hands-on)
- **Small features, polish, reliability & bug fixes:** A large amount of
  changes, smaller features, UI updates, reliability and bug fixes + general
  polish made it in this week!

## v0.4.0 - CodinGLM CLI weekly update - 2025-09-01

- 🎉**CodinGLM CLI CloudRun and Security Integrations**🎉: Automate app deployment
  and security analysis with CloudRun and Security extension integrations. Once
  installed deploy your app to the cloud with `/deploy` and find and fix
  security vulnerabilities with `/security:analyze`.
  - Announcement and how to get started:
    [https://cloud.google.com/blog/products/ai-machine-learning/automate-app-deployment-and-security-analysis-with-new-gemini-cli-extensions](https://cloud.google.com/blog/products/ai-machine-learning/automate-app-deployment-and-security-analysis-with-new-gemini-cli-extensions)
- **Experimental**
  - **Edit Tool:** Give our new edit tool a try by setting
    `"useSmartEdit": true` in `settings.json`!
    ([feedback](https://github.com/Dfunk55/CodinGLM/discussions/7758),
    [pr](https://github.com/Dfunk55/CodinGLM/pull/6823) by
    [@silviojr](https://github.com/silviojr))
  - **Model talking to itself fix:** We’ve removed a model workaround that would
    encourage CodinGLM CLI to continue conversations on your behalf. This may be
    disruptive and can be disabled via `"skipNextSpeakerCheck": false` in your
    `settings.json`
    ([feedback](https://github.com/Dfunk55/CodinGLM/discussions/6666),
    [pr](https://github.com/Dfunk55/CodinGLM/pull/7614) by
    [@SandyTao520](https://github.com/SandyTao520))
  - **Prompt completion:** Get real-time AI suggestions to complete your prompts
    as you type. Enable it with `"general": { "enablePromptCompletion": true }`
    and share your feedback!
    ([gif](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*hvegW7YXOg6N_beUWhTdxA.gif),
    [pr](https://github.com/Dfunk55/CodinGLM/pull/4691) by
    [@3ks](https://github.com/3ks))
- **Footer visibility configuration:** Customize the CLI's footer look and feel
  in `settings.json`
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/7419) by
  [@miguelsolorio](https://github.com/miguelsolorio))
  - `hideCWD`: hide current working directory.
  - `hideSandboxStatus`: hide sandbox status.
  - `hideModelInfo`: hide current model information.
  - `hideContextSummary`: hide request context summary.
- **Citations:** For enterprise Code Assist licenses users will now see
  citations in their responses by default. Enable this yourself with
  `"showCitations": true`
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/7350) by
  [@scidomino](https://github.com/scidomino))
- **Pro Quota Dialog:** Handle daily Pro model usage limits with an interactive
  dialog that lets you immediately switch auth or fallback.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/7094) by
  [@JayadityaGit](https://github.com/JayadityaGit))
- **Custom commands @:** Embed local file or directory content directly into
  your custom command prompts using `@{path}` syntax
  ([gif](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*GosBAo2SjMfFffAnzT7ZMg.gif),
  [pr](https://github.com/Dfunk55/CodinGLM/pull/6716) by
  [@abhipatel12](https://github.com/abhipatel12))
- **2.5 Flash Lite support:** You can now use the `gemini-2.5-flash-lite` model
  for CodinGLM CLI via `gemini -m …`.
  ([gif](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*P4SKwnrsyBuULoHrFqsFKQ.gif),
  [pr](https://github.com/Dfunk55/CodinGLM/pull/4652) by
  [@psinha40898](https://github.com/psinha40898))
- **CLI streamlining:** We have deprecated a number of command line arguments in
  favor of `settings.json` alternatives. We will remove these arguments in a
  future release. See the PR for the full list of deprecations.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/7360) by
  [@allenhutchison](https://github.com/allenhutchison))
- **JSON session summary:** Track and save detailed CLI session statistics to a
  JSON file for performance analysis with `--session-summary <path>`
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/7347) by
  [@leehagoodjames](https://github.com/leehagoodjames))
- **Robust keyboard handling:** More reliable and consistent behavior for arrow
  keys, special keys (Home, End, etc.), and modifier combinations across various
  terminals. ([pr](https://github.com/Dfunk55/CodinGLM/pull/7118) by
  [@deepankarsharma](https://github.com/deepankarsharma))
- **MCP loading indicator:** Provides visual feedback during CLI initialization
  when connecting to multiple servers.
  ([pr](https://github.com/Dfunk55/CodinGLM/pull/6923) by
  [@swissspidy](https://github.com/swissspidy))
- **Small features, polish, reliability & bug fixes:** A large amount of
  changes, smaller features, UI updates, reliability and bug fixes + general
  polish made it in this week!
