# Audit Chunk 3: Tool System & Execution

**Duration**: 2-3 days
**Priority**: Critical

## Objectives

Understand how tools are registered, discovered, executed, and integrated with the LLM. This includes file operations, shell execution, web tools, and MCP integration. Security is paramount here.

## Key Questions to Answer

1. How are tools registered and discovered?
2. How is tool calling handled from the API?
3. How are tool results formatted and returned?
4. What security measures protect tool execution?
5. How does MCP integration work?
6. How are tool errors handled?
7. What sandboxing exists?
8. How are tool permissions managed?

## Files to Audit

### Priority 1: Tool Framework
- [ ] `packages/core/src/tools/tool-registry.ts` ⭐ **CRITICAL**
- [ ] `packages/core/src/tools/tools.ts` (execution engine)
- [ ] `packages/core/src/tools/modifiable-tool.ts` (tool composition)
- [ ] `packages/core/src/tools/tool-list.ts`
- [ ] `packages/core/src/tools/tool-names.ts` (constants)

### Priority 2: File System Tools
- [ ] `packages/core/src/tools/read-file.ts`
- [ ] `packages/core/src/tools/write-file.ts`
- [ ] `packages/core/src/tools/edit.ts`
- [ ] `packages/core/src/tools/smart-edit.ts`
- [ ] `packages/core/src/tools/ls.ts`
- [ ] `packages/core/src/tools/glob.ts`
- [ ] `packages/core/src/tools/read-many-files.ts`

### Priority 3: Execution Tools
- [ ] `packages/core/src/tools/shell.ts` ⭐ **SECURITY CRITICAL**
- [ ] `packages/core/src/services/shellExecutionService.ts`
- [ ] `packages/core/src/tools/diffOptions.ts`

### Priority 4: Search & Web Tools
- [ ] `packages/core/src/tools/ripGrep.ts`
- [ ] `packages/core/src/tools/web-search.ts`
- [ ] `packages/core/src/tools/web-fetch.ts`

### Priority 5: Context & Memory Tools
- [ ] `packages/core/src/tools/memoryTool.ts`
- [ ] `packages/core/src/tools/todos.ts`

### Priority 6: MCP Integration
- [ ] `packages/core/src/tools/mcp-client.ts` ⭐ **CRITICAL**
- [ ] `packages/core/src/tools/mcp-server.ts`
- [ ] `packages/core/src/mcp/client.ts`
- [ ] `packages/core/src/mcp/oauth-provider.ts`
- [ ] `packages/core/src/mcp/google-auth-provider.ts`

### Priority 7: File System Service
- [ ] `packages/core/src/services/fileSystemService.ts`
- [ ] `packages/core/src/services/fileDiscoveryService.ts`
- [ ] `packages/core/src/services/gitService.ts`

### Priority 8: Test Files
- [ ] All files in `packages/core/src/tools/__tests__/`
- [ ] `integration-tests/file-system.test.ts`
- [ ] `integration-tests/run_shell_command.test.ts`
- [ ] `integration-tests/write_file.test.ts`
- [ ] `integration-tests/read_many_files.test.ts`

### Priority 9: Documentation
- [ ] `gemini-cli/docs/core/tools-api.md`
- [ ] `gemini-cli/docs/tools/file-system.md`
- [ ] `gemini-cli/docs/tools/shell.md`
- [ ] `gemini-cli/docs/tools/mcp-server.md`

## Specific Audit Checklist

### Tool Registration
- [ ] Verify all tools are properly registered
- [ ] Check for duplicate tool names
- [ ] Review tool discovery mechanism
- [ ] Verify tool metadata is complete
- [ ] Check tool versioning
- [ ] Review tool dependency resolution

### Tool Execution
- [ ] Review execution flow from API to tool
- [ ] Check parameter validation
- [ ] Verify result formatting
- [ ] Look for execution timeouts
- [ ] Check for proper async/await usage
- [ ] Review error propagation

### File System Security
- [ ] **Path Traversal**: Check for `../` attacks
- [ ] **Absolute Paths**: Verify proper handling
- [ ] **Symlink Following**: Check for symlink attacks
- [ ] **Permission Checks**: Verify before operations
- [ ] **File Size Limits**: Check for DoS via large files
- [ ] **Extension Validation**: Verify safe file types
- [ ] **Overwrite Protection**: Check for accidental overwrites

### Shell Execution Security
- [ ] **Command Injection**: Critical - check for unsanitized input
- [ ] **Environment Variables**: Verify safe handling
- [ ] **Shell Escaping**: Check for proper escaping
- [ ] **Whitelist**: Verify command whitelisting if exists
- [ ] **Sandboxing**: Check sandbox effectiveness
- [ ] **Output Capture**: Verify stdout/stderr handling
- [ ] **Timeout**: Check for runaway process protection
- [ ] **Resource Limits**: Verify CPU/memory limits

### Web Tools Security
- [ ] **SSRF**: Check for Server-Side Request Forgery
- [ ] **URL Validation**: Verify proper URL parsing
- [ ] **Redirect Handling**: Check for malicious redirects
- [ ] **Content Type**: Verify proper MIME type handling
- [ ] **Size Limits**: Check for DoS via large downloads
- [ ] **Timeout**: Verify request timeouts

### MCP Integration Security
- [ ] **OAuth Token Storage**: Verify secure storage
- [ ] **Token Refresh**: Check for proper refresh logic
- [ ] **Scope Validation**: Verify proper scopes
- [ ] **MCP Server Trust**: Check for server validation
- [ ] **Protocol Security**: Verify MCP protocol implementation

## SRP Focus Areas

### Look for:
- Tool files mixing execution with validation
- Tool registry handling both registration and execution
- Tools mixing business logic with I/O
- Shell service mixing command building with execution

### Expected Responsibilities:
- Registry: Only registration and lookup
- Executor: Only execution orchestration
- Validator: Only parameter validation
- Formatter: Only result formatting
- Tool: Only tool-specific logic

## Bug Hunting Areas

### Critical Bugs to Find:
- **Security Vulnerabilities**: Command injection, path traversal
- **Race Conditions**: Concurrent file access, tool execution
- **Resource Leaks**: Unclosed files, zombie processes
- **Error Handling**: Unhandled exceptions in tools
- **Type Safety**: Missing parameter validation
- **Edge Cases**: Empty files, missing files, permission denied
- **Async Issues**: Promise rejections, await missing
- **Memory Leaks**: Large file handling, streaming issues

### Edge Cases:
- Empty file paths
- Non-existent files
- Permission denied
- Disk full
- Very large files
- Binary files
- Special characters in paths
- Concurrent tool execution
- Tool execution during streaming
- Network failures (web tools)
- Invalid URLs
- Malicious file content

## Technical Debt Indicators

### Watch for:
- TODO comments about security
- Commented-out validation
- Hard-coded paths or commands
- Missing error handling "for later"
- Temporary permission bypasses
- Incomplete sandboxing
- Hard-coded timeouts
- Missing input sanitization

## Testing Gaps

### Critical Tests Needed:
- [ ] **Security Tests**:
  - Path traversal attempts
  - Command injection attempts
  - SSRF attempts
  - Large file handling
  - Permission boundary tests
  - Malicious input tests
- [ ] **Edge Cases**:
  - Empty inputs
  - Missing files
  - Permission denied
  - Concurrent access
  - Resource exhaustion
- [ ] **Error Handling**:
  - Tool execution failures
  - Invalid parameters
  - Network failures
  - Timeout scenarios

### Integration Tests:
- [ ] End-to-end tool execution
- [ ] Tool chaining scenarios
- [ ] Error recovery flows
- [ ] MCP server integration

## Code Quality Checks

### Shell.ts Specific (Security Critical):
- [ ] No `eval()` or `Function()` usage
- [ ] Proper shell escaping everywhere
- [ ] Input validation before execution
- [ ] Whitelist of allowed commands (if applicable)
- [ ] Proper error handling
- [ ] Timeout enforcement
- [ ] Output size limits
- [ ] Clear security comments

### File Operation Tools:
- [ ] Path validation before every operation
- [ ] Permission checks before operations
- [ ] Proper error messages
- [ ] Resource cleanup (file handles)
- [ ] Encoding handling (UTF-8, etc.)
- [ ] File size checks
- [ ] Atomic operations where needed

## Integration Points

Document how these integrate:
1. LLM API → Tool Registry (tool discovery)
2. Tool Registry → Tool Executor (execution)
3. Tool → File System Service (I/O)
4. Tool → Shell Service (command execution)
5. Tool → MCP Client (external tools)
6. Tool Result → LLM API (result formatting)
7. Policy Engine → Tool Execution (permission checks)

## Performance Considerations

- [ ] Check for blocking file operations
- [ ] Review large file handling
- [ ] Look for unnecessary file reads
- [ ] Check for efficient glob patterns
- [ ] Review shell command efficiency
- [ ] Look for parallel execution opportunities
- [ ] Check for memory-efficient streaming

## Tool Validation Checklist

For each tool, verify:
- [ ] Clear purpose and documentation
- [ ] Proper parameter schema
- [ ] Input validation
- [ ] Security considerations addressed
- [ ] Error handling implemented
- [ ] Test coverage adequate
- [ ] Performance acceptable
- [ ] Result format consistent

## Red Flags to Watch For

🚩 **CRITICAL**: Command injection vulnerabilities
🚩 **CRITICAL**: Path traversal vulnerabilities
🚩 **CRITICAL**: Missing input sanitization
🚩 Unvalidated user input in shell commands
🚩 Unclosed file handles
🚩 Missing permission checks
🚩 No timeout on tool execution
🚩 Missing error handling
🚩 `eval()` or similar dangerous functions
🚩 Hard-coded credentials in tools
🚩 Missing OAuth token security
🚩 SSRF vulnerabilities in web tools
🚩 No resource limits (CPU, memory, disk)

## Success Criteria

✅ Complete understanding of tool system
✅ All security vulnerabilities identified
✅ All tools audited for bugs and quality
✅ Integration points documented
✅ Test gaps identified
✅ Critical issues flagged immediately
✅ Recommendations documented

## Security Severity Assessment

For any security finding, use:
- **Critical**: Allows arbitrary code execution or data exfiltration
- **High**: Allows unauthorized file access or privilege escalation
- **Medium**: Information disclosure or DoS
- **Low**: Minor security improvement

## Notes Section

Document:
- Clever security measures found
- Areas of concern
- Tools that need immediate attention
- Patterns across multiple tools
- Integration complexities

---

## Next Steps

After completing this chunk:
1. **IMMEDIATE**: Report any critical security vulnerabilities
2. Test suspected security issues
3. Review findings with security focus
4. Proceed to Chunk 4: Configuration, Policy & Security
