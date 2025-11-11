# Troubleshooting guide

This guide provides solutions to common issues and debugging tips, including
topics on:

- Authentication or login errors
- Frequently asked questions (FAQs)
- Debugging tips
- Existing GitHub Issues similar to yours or creating new Issues

## Authentication or login errors

- **Error: `Failed to login. Message: Request contains an invalid argument`**
  - This typically happens when attempting an OAuth flow that CodinGLM CLI no
    longer exposes. Switch to an API-key flow (`Z_AI_API_KEY` or `ZAI_API_KEY`).
  - Generate a key from the [Z.AI console](https://open.bigmodel.cn/) and export
    it before launching the CLI.
  - If you must keep a legacy `.gemini` configuration, confirm that the `auth`
    block points to `apiKey` rather than `oauth`.

- **Error: `UNABLE_TO_GET_ISSUER_CERT_LOCALLY` or
  `unable to get local issuer certificate`**
  - **Cause:** You may be on a corporate network with a firewall that intercepts
    and inspects SSL/TLS traffic. This often requires a custom root CA
    certificate to be trusted by Node.js.
  - **Solution:** Set the `NODE_EXTRA_CA_CERTS` environment variable to the
    absolute path of your corporate root CA certificate file.
    - Example: `export NODE_EXTRA_CA_CERTS=/path/to/your/corporate-ca.crt`

## Common error messages and solutions

- **Error: `EADDRINUSE` (Address already in use) when starting an MCP server.**
  - **Cause:** Another process is already using the port that the MCP server is
    trying to bind to.
  - **Solution:** Either stop the other process that is using the port or
    configure the MCP server to use a different port.

- **Error: Command not found (when attempting to run CodinGLM CLI with
  `gemini`).**
  - **Cause:** CodinGLM CLI is not correctly installed or it is not in your
    system's `PATH`.
  - **Solution:** The update depends on how you installed CodinGLM CLI:
    - If you installed `gemini` globally, check that your `npm` global binary
      directory is in your `PATH`. You can update CodinGLM CLI using the command
      `npm install -g @codinglm/cli@latest`.
    - If you are running `gemini` from source, ensure you are using the correct
      command to invoke it (e.g., `node packages/cli/dist/index.js ...`). To
      update CodinGLM CLI, pull the latest changes from the repository, and then
      rebuild using the command `npm run build`.

- **Error: `MODULE_NOT_FOUND` or import errors.**
  - **Cause:** Dependencies are not installed correctly, or the project hasn't
    been built.
  - **Solution:**
    1.  Run `npm install` to ensure all dependencies are present.
    2.  Run `npm run build` to compile the project.
    3.  Verify that the build completed successfully with `npm run start`.

- **Error: "Operation not permitted", "Permission denied", or similar.**
  - **Cause:** When sandboxing is enabled, CodinGLM CLI may attempt operations
    that are restricted by your sandbox configuration, such as writing outside
    the project directory or system temp directory.
  - **Solution:** Refer to the [Configuration: Sandboxing](./cli/sandbox.md)
    documentation for more information, including how to customize your sandbox
    configuration.

- **CodinGLM CLI is not running in interactive mode in "CI" environments**
  - **Issue:** The CodinGLM CLI does not enter interactive mode (no prompt
    appears) if an environment variable starting with `CI_` (e.g., `CI_TOKEN`)
    is set. This is because the `is-in-ci` package, used by the underlying UI
    framework, detects these variables and assumes a non-interactive CI
    environment.
  - **Cause:** The `is-in-ci` package checks for the presence of `CI`,
    `CONTINUOUS_INTEGRATION`, or any environment variable with a `CI_` prefix.
    When any of these are found, it signals that the environment is
    non-interactive, which prevents the CodinGLM CLI from starting in its
    interactive mode.
  - **Solution:** If the `CI_` prefixed variable is not needed for the CLI to
    function, you can temporarily unset it for the command. e.g.,
    `env -u CI_TOKEN gemini`

- **DEBUG mode not working from project .env file**
  - **Issue:** Setting `DEBUG=true` in a project's `.env` file doesn't enable
    debug mode for gemini-cli.
  - **Cause:** The `DEBUG` and `DEBUG_MODE` variables are automatically excluded
    from project `.env` files to prevent interference with gemini-cli behavior.
  - **Solution:** Use a `.gemini/.env` file instead, or configure the
    `advanced.excludedEnvVars` setting in your `settings.json` to exclude fewer
    variables.

## Exit Codes

The CodinGLM CLI uses specific exit codes to indicate the reason for termination.
This is especially useful for scripting and automation.

| Exit Code | Error Type                 | Description                                                                                         |
| --------- | -------------------------- | --------------------------------------------------------------------------------------------------- |
| 41        | `FatalAuthenticationError` | An error occurred during the authentication process.                                                |
| 42        | `FatalInputError`          | Invalid or missing input was provided to the CLI. (non-interactive mode only)                       |
| 44        | `FatalSandboxError`        | An error occurred with the sandboxing environment (e.g., Docker, Podman, or Seatbelt).              |
| 52        | `FatalConfigError`         | A configuration file (`settings.json`) is invalid or contains errors.                               |
| 53        | `FatalTurnLimitedError`    | The maximum number of conversational turns for the session was reached. (non-interactive mode only) |

## Debugging Tips

- **CLI debugging:**
  - Use the `--verbose` flag (if available) with CLI commands for more detailed
    output.
  - Check the CLI logs, often found in a user-specific configuration or cache
    directory.

- **Core debugging:**
  - Check the server console output for error messages or stack traces.
  - Increase log verbosity if configurable.
  - Use Node.js debugging tools (e.g., `node --inspect`) if you need to step
    through server-side code.

- **Tool issues:**
  - If a specific tool is failing, try to isolate the issue by running the
    simplest possible version of the command or operation the tool performs.
  - For `run_shell_command`, check that the command works directly in your shell
    first.
  - For _file system tools_, verify that paths are correct and check the
    permissions.

- **Pre-flight checks:**
  - Always run `npm run preflight` before committing code. This can catch many
    common issues related to formatting, linting, and type errors.

## Existing GitHub Issues similar to yours or creating new Issues

If you encounter an issue that was not covered here in this _Troubleshooting
guide_, consider searching the CodinGLM CLI
[Issue tracker on GitHub](https://github.com/Dfunk55/CodinGLM/issues).
If you can't find an issue similar to yours, consider creating a new GitHub
Issue with a detailed description. Pull requests are also welcome!
