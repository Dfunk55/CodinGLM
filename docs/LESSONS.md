# Lessons Learned: Tool Reliability Improvements

This note captures the issues discovered while porting Claude Code to the Z.ai
GLM stack and the fixes that keep tool calls reliable across future updates.

## Tool Streaming

- The Z.ai SSE stream emits `input_json_delta` fragments while a tool call is
  being constructed. If these fragments are ignored, the CLI dispatches tools
  with empty `{}` arguments and shells like `Bash` reject the request.
- We now buffer every partial JSON fragment until the SDK raises
  `content_block_stop`, then emit the fully‑formed argument string. See
  `codinglm/api/client.py`.
- A regression test (`tests/unit/test_api_client.py::test_parse_event_stream_accumulates_tool_arguments`)
  simulates the stream so future SDK or API tweaks can be caught automatically.

## Tool Prompting

- The system primer now renders directly from the registered tool schemas, so
  new tools and aliases show up automatically in both the prompt and CLI help.
- The `/tools` command renders the same schemas straight from the registry. When
  adding aliases or required parameters, double check the output to make sure
  the wording matches expectations.

## Operational Tips

- Always launch via `Launch CodinGLM.command` (or an equivalent real TTY) so
  prompt-toolkit dialogs, model streaming, and ESC interruption work reliably.
- Smoke-test new builds by asking the assistant to inspect a directory; this
  exercises `Glob` and `Bash` together, which previously surfaced the empty
  argument bug.
- When introducing new tools, add lightweight fixtures to `tests/unit/tool_*` to
  lock down core behaviors and rely on the auto-generated primer to educate the
  model about parameter requirements.
- A pseudo-terminal smoke test (`tests/integration/test_cli_pty.py`) now boots
  the CLI end-to-end, exercises `/tools`, and runs a sample `Bash` tool call to
  ensure streaming + execution remain healthy.

## Context Compression & Memory

- CodinGLM now auto-summarises earlier turns whenever the estimated context
  budget drifts past `context.compression.maxContextTokens` (defaults: 12k max /
  9k target tokens). A synthetic assistant message tagged `context_summary`
  replaces the oldest chunk while the most recent
  `context.compression.preserveRecentMessages` turns stay verbatim.
- Summaries are generated with the active GLM model by default. To force a
  cheaper summariser, set `context.compression.summaryModel` in
  `.codinglm.json`. If the API call fails, a deterministic local fallback still
  keeps key headlines so the assistant has something to ground on.
- The CLI surfaces compression events in-dash (`Context compressed ...`) so you
  can tell when a summary landed. A `/clear` resets the in-memory history and
  wipes any accumulated summaries.
- Behavioural knobs live under `context.compression` in the config: tweak
  `preserveRecentMessages` for longer verbatim trails, `summaryMaxTokens` to
  tighten/loosen the summary budget, or disable the system entirely for e2e test
  fixtures that need raw transcripts.

## Future Work Ideas

- Extend the pseudo-terminal harness to cover the interactive `/models`
  selector once a stable keystroke script is available.
- Consider persisting model/tool usage telemetry (opt-in) to spot regressions
  automatically when API behavior changes.
