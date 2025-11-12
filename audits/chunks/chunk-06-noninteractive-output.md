# Audit Chunk 6: Non-Interactive & Output Modes

**Duration**: 1-2 days
**Priority**: Medium

## Objectives

Understand scripting mode, JSON output, streaming output, and how the application works in headless/non-interactive scenarios. This is crucial for automation and CI/CD integration.

## Key Questions to Answer

1. How does non-interactive mode work?
2. How is JSON output formatted?
3. How is stream output handled?
4. What are the input processing pipelines?
5. How are prompt variables substituted?
6. How are errors formatted in non-interactive mode?
7. What exit codes are used?
8. How is stdin/stdout handled?

## Files to Audit

### Priority 1: Non-Interactive Mode
- [ ] `packages/cli/src/ui/noninteractive/` (15+ files) ⭐
  - jsonOutput.ts
  - streamOutput.ts
  - etc.

### Priority 2: Mode Selection
- [ ] `packages/cli/src/gemini.ts` (mode detection logic)

### Priority 3: Prompt Processing
- [ ] `packages/cli/src/services/prompt-processors/` ⭐
  - argumentProcessor.ts
  - atFileProcessor.ts
  - shellProcessor.ts
  - injectionParser.ts

### Priority 4: Output Formatting
- [ ] `packages/core/src/output/outputFormatter.ts`
- [ ] `packages/core/src/output/streamFormatter.ts`
- [ ] All files in `packages/core/src/output/` (10+ files)

### Priority 5: Command Loading
- [ ] `packages/cli/src/services/FileCommandLoader.ts`
- [ ] `packages/cli/src/services/BuiltinCommandLoader.ts`
- [ ] `packages/cli/src/services/McpPromptLoader.ts`

### Priority 6: Test Files
- [ ] `integration-tests/json-output.test.ts`
- [ ] `integration-tests/stdin-context.test.ts`
- [ ] `integration-tests/mixed-input-crash.test.ts`
- [ ] Any other non-interactive tests

### Priority 7: Documentation
- [ ] `gemini-cli/docs/cli/headless.md`
- [ ] Examples of non-interactive usage

## Specific Audit Checklist

### Mode Detection
- [ ] Review interactive vs non-interactive detection
- [ ] Check for proper TTY detection
- [ ] Verify stdin/stdout handling
- [ ] Look for edge cases (pipes, redirects)
- [ ] Check for proper mode switching

### JSON Output
- [ ] Review JSON schema
- [ ] Check for proper escaping
- [ ] Verify error formatting
- [ ] Look for incomplete JSON
- [ ] Check for streaming JSON
- [ ] Verify JSON validation

### Stream Output
- [ ] Review streaming format
- [ ] Check for buffering issues
- [ ] Verify proper line endings
- [ ] Look for race conditions
- [ ] Check for backpressure handling

### Prompt Processing
- [ ] **@file syntax**: Verify proper file reading
- [ ] **Variable substitution**: Check for injection
- [ ] **Shell substitution**: **SECURITY CRITICAL** - check for command injection
- [ ] **Argument parsing**: Verify proper parsing
- [ ] **Error handling**: Check for proper errors

### Input Validation
- [ ] Review all input sources
- [ ] Check for proper sanitization
- [ ] Verify injection protection
- [ ] Look for buffer overflows
- [ ] Check for size limits

### Exit Codes
- [ ] Review exit code usage
- [ ] Verify proper error codes
- [ ] Check for consistent codes
- [ ] Look for missing exit codes

### Error Handling
- [ ] Review non-interactive error format
- [ ] Check for stack trace exposure
- [ ] Verify error messages are helpful
- [ ] Look for proper error logging
- [ ] Check for error recovery

## SRP Focus Areas

### Look for:
- Output formatting mixed with business logic
- Prompt processing mixed with execution
- Mode detection mixed with rendering
- Input reading mixed with validation

### Expected Responsibilities:
- Formatter: Only format output
- Processor: Only process prompts
- Reader: Only read input
- Validator: Only validate input

## Bug Hunting Areas

### Critical Bugs to Find:
- **Command Injection**: Shell substitution vulnerabilities
- **File Injection**: @file syntax vulnerabilities
- **JSON Injection**: Improper escaping
- **Buffer Issues**: Large input handling
- **Stream Issues**: Incomplete output
- **Exit Code Bugs**: Wrong exit codes
- **Encoding Issues**: Character encoding problems

### Edge Cases:
- Empty stdin
- Very large stdin
- Binary stdin
- Partial JSON
- Stream interruption
- Concurrent output
- Invalid UTF-8
- Special characters
- File not found (@file)
- Permission denied (@file)

## Technical Debt Indicators

### Watch for:
- TODO comments about output format
- Commented-out formatting code
- Hard-coded JSON structure
- Temporary error handling
- Missing validation "for now"
- Hard-coded paths in @file

## Testing Gaps

### Critical Tests Needed:
- [ ] **Security Tests**:
  - Shell injection in substitution
  - Path traversal in @file
  - JSON injection attempts
- [ ] **Edge Cases**:
  - Empty input
  - Large input
  - Binary input
  - Malformed JSON
  - Stream interruption
- [ ] **Error Handling**:
  - File not found
  - Permission denied
  - Invalid input
  - Network errors

### Integration Tests:
- [ ] End-to-end non-interactive flow
- [ ] JSON output validation
- [ ] Stream output validation
- [ ] Error formatting

## Code Quality Checks

### Prompt Processors:
- [ ] Clear purpose each processor
- [ ] Proper input validation
- [ ] Security considerations documented
- [ ] Error handling comprehensive
- [ ] Test coverage adequate
- [ ] No code duplication

### Output Formatters:
- [ ] Consistent formatting
- [ ] Proper escaping everywhere
- [ ] Clear separation of concerns
- [ ] Streaming support
- [ ] Error handling

## Security Focus

### Shell Processor (CRITICAL):
- [ ] No eval() or similar
- [ ] Proper shell escaping
- [ ] Input validation
- [ ] Whitelist if possible
- [ ] Clear security warnings
- [ ] Comprehensive tests

### @file Processor:
- [ ] Path validation
- [ ] No path traversal
- [ ] Permission checks
- [ ] Size limits
- [ ] Error handling
- [ ] No binary files

## Performance Considerations

- [ ] Check for blocking I/O
- [ ] Review buffering strategy
- [ ] Look for memory issues
- [ ] Check streaming efficiency
- [ ] Review large input handling

## Integration Points

Document:
1. CLI Args → Prompt Processors
2. Stdin → Input Reader
3. Core → Output Formatter
4. Output → Stdout/File
5. Errors → Stderr

## Red Flags to Watch For

🚩 **CRITICAL**: Command injection in shell substitution
🚩 **CRITICAL**: Path traversal in @file
🚩 No input validation
🚩 Improper JSON escaping
🚩 Missing exit codes
🚩 Stack traces in production output
🚩 No size limits on input
🚩 Blocking operations
🚩 Missing error handling
🚩 Hard-coded file paths

## Success Criteria

✅ Complete understanding of non-interactive mode
✅ All security issues identified
✅ Output formats verified
✅ Input processing audited
✅ All findings documented

## Notes Section

Document:
- Automation use cases
- Output format clarity
- Error handling quality
- Security measures

---

## Next Steps

After completing this chunk:
1. Test non-interactive mode
2. Verify JSON output format
3. Proceed to Chunk 7: Testing & Quality Infrastructure
