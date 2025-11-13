# CodinGLM Debugging Progress Tracker

**Last Updated**: 2025-11-12
**Total Issues**: 213
**Completed**: 17 (8.0%)
**In Progress**: 13
**Blocked**: 0

**Master Plan**: [DEBUGGING_PLAN.md](./DEBUGGING_PLAN.md)

---

## Quick Stats by Phase

| Phase | Total | Complete | % Done | Status |
|-------|-------|----------|--------|--------|
| Phase 0: Quick Wins | 11 | 11 | 100% | ✅ COMPLETED |
| Phase 1: CRITICAL Security | 19 | 0 | 0% | Not Started |
| Phase 2: HIGH Priority Bugs | 61 | 0 | 0% | Not Started |
| Phase 3: MEDIUM & Testing | 87 | 0 | 0% | Not Started |
| Phase 4: SRP Refactoring | 15 | 0 | 0% | Not Started |
| Phase 5: LOW Priority | 50 | 0 | 0% | Not Started |

---

## Phase 0: Quick Wins (Target: Week 1, Days 1-2)

**Goal**: 11 simple fixes for momentum
**Status**: ✅ COMPLETED (2025-11-12)
**Progress**: 11/11 (100%)

### Day 1 Morning (2 hours)
- [x] Fix ctrlD timer cleanup typo (`AppContainer.tsx:963`) - [HIGH-006 C5] - 5min ✅
- [x] Remove duplicate isAuthDialogOpen check (`AppContainer.tsx:1224`) - [LOW-004 C5] - 1min ✅
- [x] Change "private" to boolean (`package.json:11`) - [HIGH-002 C1] - 1min ✅
- [x] Remove duplicate esbuild alias (`esbuild.config.js:92-96`) - [HIGH-001 C1] - 5min ✅
- [x] Remove commented license header (`esbuild.config.js:7-18`) - [MED-005 C1] - 1min ✅ (Already fixed)

### Day 1 Afternoon (2 hours)
- [x] Fix initialPromptSubmitted race (`AppContainer.tsx:816`) - [MED-004 C5] - 5min ✅
- [x] Add escape timer cleanup (`InputPrompt.tsx:184`) - [MED-008 C5] - 5min ✅ (Already implemented)
- [x] Add paste timer cleanup (`InputPrompt.tsx:130`) - [MED-009 C5] - 5min ✅ (Already implemented)
- [x] Make queue error cleanup explicit (`AppContainer.tsx:891`) - [MED-010 C5] - 2min ✅

### Day 2 (4 hours)
- [x] Document terminal layout magic numbers (`AppContainer.tsx:133-139`) - [MED-002 C1] - 30min ✅
- [x] Add Error Boundary to App (`App.tsx:14-27`) - [HIGH-005 C5] - 4h ✅
  - [x] Create ErrorBoundary component ✅
  - [x] Add error logging ✅
  - [x] Add fallback UI ✅
  - [x] Test error scenarios ✅

**Acceptance**: ✅ Build passing, all changes complete

**Summary of Changes**:
- Fixed 4 actual bugs (timer cleanup, race condition, duplicate check, queue cleanup)
- Fixed 2 code quality issues (duplicate alias, private field type)
- Added 1 major feature (Error Boundary with comprehensive tests)
- Improved documentation (magic numbers)
- Found 3 issues already resolved (timer cleanups, license header)

---

## Phase 1: CRITICAL Security (Target: Week 1-3)

**Goal**: Zero critical vulnerabilities
**Status**: 🔄 In Progress
**Progress**: 6/19 (32%)

### 1.1 Token & Auth Security (Week 1)

- [ ] **[CRIT-002 C4]** Enable encrypted token storage by default - 4 days
  - File: `packages/core/src/mcp/oauth-token-storage.ts:99-106`
  - [ ] Change default to useEncryptedFile = true
  - [ ] Implement plaintext→encrypted migration
  - [ ] Add warning when encryption unavailable
  - [ ] Update documentation
  - [ ] Test on Linux/macOS/Windows
  - [ ] Add rollback mechanism
  - [ ] Verify: Security audit passed

- [ ] **[CRIT-003 C4]** Fix path traversal with symlinks - 2 days
  - File: `packages/cli/src/config/trustedFolders.ts:79-113`
  - [ ] Add fs.realpathSync() for canonicalization
  - [ ] Handle ENOENT errors
  - [ ] Add symlink detection warnings
  - [ ] Create symlink attack tests
  - [ ] Document security model
  - [ ] Verify: Penetration test passed

- [ ] **[CRIT-001 C4]** Sanitize environment variables - 5 days
  - File: `packages/cli/src/config/settings.ts:534-558`
  - [ ] Create sensitive variable pattern list
  - [ ] Implement redaction in serialization
  - [ ] Filter before telemetry/logging
  - [ ] Create SecureConfig wrapper
  - [ ] Add exposure prevention tests
  - [ ] Audit all logging call sites
  - [ ] Verify: No secrets in logs/telemetry

### 1.2 Extension Security (Week 2-3)

- [ ] **[CRIT-001 C10]** Extension sandboxing - 2 weeks
  - File: `packages/cli/src/config/extension-manager.ts:1-716`
  - [ ] Research sandbox options (vm2/isolated-vm/process)
  - [ ] Design permission system
  - [ ] Implement sandbox runtime
  - [ ] Add user consent mechanism
  - [ ] Create code signing/verification
  - [ ] Add runtime monitoring
  - [ ] Migrate existing extensions
  - [ ] Update documentation
  - [ ] Verify: Security audit passed

- [ ] **[CRIT-002 C10]** MCP command validation - 1 week
  - File: `packages/core/src/tools/mcp-client.ts:1297-1318`
  - [ ] Implement command whitelist
  - [ ] Add argument validation
  - [ ] Restrict env variable inheritance
  - [ ] Add user confirmation for new servers
  - [ ] Document security requirements
  - [ ] Test malicious command attempts
  - [ ] Verify: Penetration test passed

- [ ] **[CRIT-004 C10]** A2A server authentication - 1 week
  - [ ] Design auth scheme (API key/JWT/OAuth)
  - [ ] Implement auth middleware
  - [ ] Add authorization layer
  - [ ] Create key management system
  - [ ] Add rate limiting
  - [ ] Update documentation
  - [ ] Verify: All endpoints require auth

- [ ] **[CRIT-003 C10]** Encrypt OAuth tokens - 1 week (overlaps with CRIT-002 C4)
- [ ] **[CRIT-005 C10]** Enforce extension consent - 2 weeks (overlaps with CRIT-001 C10)
- [ ] **[CRIT-006 C10]** Sanitize extension variables - 1 week
- [ ] **[CRIT-007 C10]** Reduce OAuth callback timeout - 1 day
- [ ] **[CRIT-008 C10]** Prevent GitHub token injection - 3 days

### 1.3 Non-Interactive & Streaming (Days distributed)

- [x] **[CRIT-001 C6]** Fix buffer overflow in stdin - 2h ✅
  - File: `packages/cli/src/utils/readStdin.ts:32-40`
  - [x] Properly drain stream after truncation
  - [x] Call onEnd() after destroy
  - [x] Add test for size limit (2 comprehensive tests added)
  - [x] Add user-visible warning
  - [x] Verify: No hangs on large input (all 6 tests passing)

- [x] **[CRIT-002 C6]** Fix abort signal race - 3h ✅
  - File: `packages/cli/src/nonInteractiveCli.ts:280-283`
  - [x] Register abort listener before stream processing
  - [x] Set abort flag immediately
  - [x] Check flag before event processing
  - [x] Ensure cleanup on abort (finally block added)
  - [x] Verify: Clean cancellation (all 26 tests passing)

- [x] **[CRIT-003 C6]** Add JSON output size limits - 4h ✅
  - File: `packages/cli/src/nonInteractiveCli.ts`
  - [x] Added 32MB limit for JSON output
  - [x] Truncation with user warning
  - [x] Verify: All 26 tests passing

- [x] **[CRIT-004 C6]** Fix shell processor cleanup - 3h ✅
  - File: `packages/cli/src/services/prompt-processors/shellProcessor.ts`
  - [x] Added try-finally block for AbortController
  - [x] Ensures proper cleanup even on errors
  - [x] Verify: All 33 tests passing

### 1.4 Services (Days distributed)

- [ ] **[CRIT-001 C9]** Harden shell execution - 2-3 days
  - File: `packages/core/src/services/shellExecutionService.ts:210-211`
  - [ ] Add command whitelist/validation
  - [ ] Verify sandbox enforcement
  - [ ] Review all call sites
  - [ ] Document security expectations
  - [ ] Implement safe command builder
  - [ ] Verify: Command injection tests pass

- [ ] **[CRIT-002 C9]** Fix PTY process leak - 1-2 days
  - File: `packages/core/src/services/shellExecutionService.ts:126-127`
  - [ ] Fix race conditions in cleanup
  - [ ] Add periodic cleanup
  - [ ] Add timeout mechanism
  - [ ] Test orphaned entries
  - [ ] Verify: No memory leaks

- [ ] **[CRIT-003 C9]** Add PII protection to telemetry - 3-4 days

### 1.5 Build System (Days distributed)

- [x] **[CRIT-001 C8]** Fix silent sandbox build failure - 1h ✅
  - File: `scripts/build.js:39-55`
  - [x] Replace silent catch with error handling
  - [x] Add REQUIRE_SANDBOX_BUILD flag
  - [x] Log warnings appropriately
  - [x] Verify: Build fails when expected

- [x] **[CRIT-002 C8]** Extract hardcoded Docker URI - 4h ✅
  - Files: `.github/workflows/eval.yml`, `.github/workflows/gemini-automated-issue-dedup.yml`, `.github/workflows/gemini-scheduled-issue-dedup.yml`, `.github/actions/push-docker/action.yml`
  - [x] Centralized all Docker image references
  - [x] Registry and images now configurable via environment variables
  - [x] Added docker-registry input parameter to push-docker action

- [ ] **[CRIT-003 C8]** Fix release race condition - 8h
- [ ] **[CRIT-004 C8]** Add release rollback - 12h

**Phase 1 Gate**:
- [ ] All 19 critical issues resolved
- [ ] External security audit passed
- [ ] Penetration testing passed
- [ ] Documentation updated
- [ ] Team sign-off

---

## Phase 2: HIGH Priority Bugs (Target: Week 4-6)

**Goal**: Fix all high-priority bugs
**Status**: ⬜ Not Started
**Progress**: 0/61 (0%)

### 2.1 LLM Streaming (Week 4) - 12 issues

- [ ] **[HIGH-001 C2]** Fix token counting accuracy - 4h
- [ ] **[HIGH-003 C2]** Implement backpressure - 6h
- [ ] **[HIGH-004 C2]** Make retry configurable - 2h
- [ ] **[HIGH-005 C2]** Add Zod validation for responses - 4h
- [ ] **[HIGH-006 C2]** Fix tool call ID generation - 2h
- [ ] **[HIGH-007 C2]** Add request timeouts - 3h
- [ ] **[HIGH-008 C2]** Fix memory leak in streaming - 4h
- [ ] **[HIGH-009 C2]** Improve URL normalization - 1h
- [ ] **[HIGH-010 C2]** Fix retry loop reset - 2h
- [ ] **[HIGH-011 C2]** Fix history mutation risk - 3h
- [ ] **[HIGH-012 C2]** Improve compression strategies - 6h

### 2.2 OAuth & Policy (Week 5) - 5 issues

- [ ] **[HIGH-001 C4]** Add OAuth state replay protection - 1 day
- [ ] **[HIGH-002 C4]** Enforce mandatory admin policies - 2-3 days
- [ ] **[HIGH-003 C4]** Strict redirect URI validation - 1 day
- [ ] **[HIGH-004 C4]** Enforce security baseline in merge - 2 days
- [ ] **[HIGH-005 C4]** Sanitize OAuth errors - 1 day

### 2.3 UI Components (Week 6) - 6 issues

- [ ] **[HIGH-001 C5]** Split KeypressContext (1,001→<200 lines) - 1 week
  - [ ] Extract useKeypressParser
  - [ ] Extract useKittyProtocol
  - [ ] Extract useMouseParser
  - [ ] Extract usePasteMode
  - [ ] Extract useDragHandler
  - [ ] Integration tests

- [ ] **[HIGH-003 C5]** Split slashCommandProcessor - 1 week
  - [ ] Extract useCommandRegistry
  - [ ] Extract useCommandExecutor
  - [ ] Extract useCommandConfirmation
  - [ ] Extract useShellAllowlist
  - [ ] Integration tests

### 2.4 Build & Configuration (Distributed) - 8 issues

- [ ] **[HIGH-003 C1]** Add error handling to esbuild config - 4h
- [ ] **[HIGH-004 C1]** Document bundle splitting strategy - 30min
- [ ] **[HIGH-001 C8]** Add version consistency check - 8h
- [ ] **[HIGH-002 C8]** Remove duplicate package.json entries - 2h
- [ ] **[HIGH-003 C8]** Add lockfile integrity check - 6h
- [ ] **[HIGH-004 C8]** Standardize error handling in build - 4h
- [ ] **[HIGH-005 C8]** Generate bundle metafile in prod - 2h
- [ ] **[HIGH-006 C8]** Simplify release version logic - 12h

### 2.5 Testing (Week distributed) - 6 issues

- [ ] **[HIGH-001 C7]** Document all 19 skipped tests - 4h
  - [ ] Create GitHub issues
  - [ ] Link in test files
  - [ ] Add CI check for new skips
  - [ ] Create tracking dashboard

- [ ] **[HIGH-002 C7]** Enforce coverage thresholds - 1 day
- [ ] **[HIGH-003 C7]** Reduce LLM test brittleness - 1 week
- [ ] **[HIGH-004 C7]** Add security test suite - 1 week
- [ ] **[HIGH-005 C7]** Add performance testing - 1 week
- [ ] **[HIGH-006 C7]** Fix flaky test infrastructure - 1 week

### 2.6 Non-Interactive (Distributed) - 11 issues

- [ ] **[HIGH-001 C6]** Add stdin read timeout - 2h
- [ ] **[HIGH-002 C6]** Validate shell output size - 2h
- [ ] **[HIGH-003 C6]** Validate @file content type - 3h
- [ ] **[HIGH-004 C6]** Standardize error codes - 4h
- [ ] **[HIGH-005 C6]** Handle partial stream writes - 4h
- [ ] **[HIGH-006 C6]** Validate command name length - 2h
- [ ] **[HIGH-007 C6]** Fix stdin cancellation cleanup - 3h
- [ ] **[HIGH-008 C6]** Fix prompt mutation - 2h
- [ ] **[HIGH-009 C6]** Add shell injection tests - 3h
- [ ] **[HIGH-010 C6]** Validate stats object - 2h
- [ ] **[HIGH-011 C6]** Add session context to streams - 2h

### 2.7 Services (Distributed) - 6 issues

- [ ] **[HIGH-001 C9]** Split LoopDetectionService (506→<300) - 1 week
- [ ] **[HIGH-002 C9]** Split ShellExecutionService (813→<400) - 1 week
- [ ] **[HIGH-003 C9]** Make ChatRecordingService async - 2 days
- [ ] **[HIGH-004 C9]** Add telemetry error boundaries - 3 days
- [ ] **[HIGH-005 C9]** Fix chat compression race - 2 days
- [ ] **[HIGH-006 C9]** Add GitService validation - 2 days

### 2.8 Extensions & MCP (Distributed) - 10 issues

- [ ] **[HIGH-001 C10]** Validate MCP server URLs - 1 day
- [ ] **[HIGH-002 C10]** Add extension integrity verification - 1 week
- [ ] **[HIGH-003 C10]** Fix OAuth PKCE timing attack - 3 days
- [ ] **[HIGH-004 C10]** Verify VS Code extension fetches - 1 week
- [ ] **[HIGH-005 C10]** Encrypt extension settings - 3 days
- [ ] **[HIGH-006 C10]** Prevent workspace trust bypass - 2 days
- [ ] **[HIGH-007 C10]** Validate MCP tool schemas - 3 days
- [ ] **[HIGH-008 C10]** Fix token file permissions race - 1 day
- [ ] **[HIGH-009 C10]** Sanitize MCP server errors - 2 days
- [ ] **[HIGH-010 C10]** Preserve security attrs in copy - 1 day

### 2.9 Tool System (Distributed) - 2 issues

- [ ] **[HIGH-001 C3]** Add private IP restriction - 6h
- [ ] **[HIGH-002 C3]** Fix UTF-8 truncation - 4h

**Phase 2 Gate**:
- [ ] All 61 high-priority bugs resolved
- [ ] Streaming stable under load
- [ ] Configuration system secure
- [ ] Integration tests passing

---

## Phase 3: MEDIUM Priority & Testing (Target: Week 7-10)

**Goal**: Address medium issues and fill testing gaps
**Status**: ⬜ Not Started
**Progress**: 0/87 (0%)

### 3.1 Security Hardening (Week 7) - ~30 issues

**Config & Policy** (12 issues from C4):
- [ ] [MED-001 C4] Validate MCP server names - 4h
- [ ] [MED-002 C4] Validate security settings migration - 1 day
- [ ] [MED-003 C4] Add policy decision logging - 1-2 days
- [ ] [MED-004 C4] Make OAuth timeout configurable - 2h
- [ ] [MED-005 C4] Validate regex patterns - 1 day
- [ ] [MED-006 C4] Add OAuth rate limiting - 4h
- [ ] [MED-007 C4] Verify config file permissions - 4h
- [ ] [MED-008 C4] Make TOML errors fatal for admin - 1 day
- [ ] [MED-009 C4] Separate client secret storage - 2 days
- [ ] [MED-010 C4] Validate MCP server URLs - 1 day
- [ ] [MED-011 C4] Make token expiration buffer configurable - 2h
- [ ] [MED-012 C4] Verify trusted folders permissions - 4h

**Extensions & MCP** (7 issues from C10):
- [ ] [MED-001 C10] Prevent MCP URL protocol confusion
- [ ] [MED-002 C10] Prevent extension update tampering
- [ ] [MED-003 C10] Fix file chooser security
- [ ] [MED-004 C10] Validate MCP server responses
- [ ] [MED-005 C10] Add OAuth cache security
- [ ] [MED-006 C10] Document MCP server security
- [ ] [MED-007 C10] Add extension load monitoring

**Other Medium Security Issues** (~11 remaining):
- Various input validation
- Error sanitization
- Logging improvements
- Rate limiting

### 3.2 Testing Infrastructure (Week 8-9)

**Security Testing**:
- [ ] Command injection test suite
- [ ] Path traversal test suite
- [ ] SSRF test suite
- [ ] Token exposure tests
- [ ] Policy bypass tests
- [ ] Extension security tests

**Coverage & Quality**:
- [ ] Achieve >80% coverage across all packages
- [ ] Fix all 19 skipped tests
- [ ] Add performance benchmarks
- [ ] Add load testing
- [ ] Improve flaky test tracking

### 3.3 Code Quality (Week 10) - ~18 issues

**Non-Interactive** (18 issues from C6):
- [ ] [MED-001 C6] Add concurrency limit - 6h
- [ ] [MED-002 C6] Add SSE validation - 4h
- [ ] [MED-003 C6] Make stream buffer configurable - 2h
- [ ] [MED-004 C6] Add @file size limit - 2h
- [ ] [MED-005 C6] Move output formatting - 4h
- [ ] [MED-006 C6] Add file path validation - 4h
- [ ] [MED-007 C6] Add stdin metrics - 2h
- [ ] [MED-008 C6] Document defaultArgs behavior - 1h
- [ ] [MED-009 C6] Add cancellation tests - 6h
- [ ] [MED-010 C6] Add resume state validation - 3h
- [ ] [MED-011 C6] Add stop reason enum - 2h
- [ ] [MED-012 C6] Document message schema - 3h
- [ ] [MED-013 C6] Add schema validation - 4h
- [ ] [MED-014 C6] Add explicit @file limits - 2h
- [ ] [MED-015 C6] Decouple output formatters - 1 day
- [ ] [MED-016 C6] Add continuation docs - 2h
- [ ] [MED-017 C6] Handle shell allowlist edge cases - 4h
- [ ] [MED-018 C6] Add error message tests - 3h

**Build System** (11 issues from C8):
- [ ] [MED-001 C8] Fix bundle metafile output - 2h
- [ ] [MED-002 C8] Document esbuild targets - 30min
- [ ] [MED-003 C8] Add CommonJS export warning - 1h
- [ ] [MED-004 C8] Make platform dynamic - 2h
- [ ] [MED-005 C8] Extract sandbox config - 4h
- [ ] [MED-006 C8] Add version validation - 8h
- [ ] [MED-007 C8] Standardize quiet flag - 2h
- [ ] [MED-008 C8] Create comprehensive test - 1 day
- [ ] [MED-009 C8] Add dependency checksums - 8h
- [ ] [MED-010 C8] Add version format schema - 4h
- [ ] [MED-011 C8] Improve smoke test - 4h

**Services** (10 issues from C9):
- [ ] [MED-001 C9] Document loop detection limits
- [ ] [MED-002 C9] Add shell command validation
- [ ] [MED-003 C9] Extract chat sync logic
- [ ] [MED-004 C9] Add telemetry sampling
- [ ] [MED-005 C9] Standardize cleanup
- [ ] [MED-006 C9] Make timeouts configurable
- [ ] [MED-007 C9] Add metrics caching
- [ ] [MED-008 C9] Add path validation
- [ ] [MED-009 C9] Document trust security
- [ ] [MED-010 C9] Add explicit git validation

**Testing** (13 issues from C7):
- [ ] [MED-001 C7] Add smoke tests - 1 week
- [ ] [MED-002 C7] Improve error messages in tests - 3 days
- [ ] [MED-003 C7] Add TestRig timeout config - 2h
- [ ] [MED-004 C7] Reduce test duplication - 1 week
- [ ] [MED-005 C7] Document testing patterns - 3 days
- [ ] [MED-006 C7] Test IDE integration - 1 week
- [ ] [MED-007 C7] Test input edge cases - 3 days
- [ ] [MED-008 C7] Add network failure tests - 2 days
- [ ] [MED-009 C7] Test streaming robustness - 3 days
- [ ] [MED-010 C7] Standardize mocking - 1 week
- [ ] [MED-011 C7] Add accessibility tests - 1 week
- [ ] [MED-012 C7] Test concurrent requests - 2 days
- [ ] [MED-013 C7] Add auth flow tests - 3 days

**UI** (10 issues from C5):
- [ ] [MED-001 C5] Split UIActions (19→5 actions) - 1 week
- [ ] [MED-002 C5] Document layout calculations - 30min
- [ ] [MED-003 C5] Extract keyboard shortcuts - 1 week
- [ ] [MED-005 C5] Standardize auth error handling - 2h
- [ ] [MED-006 C5] Optimize useMemo dependencies - included in Phase 4
- [ ] [MED-007 C5] Extract dialogsVisible hook - 4h

**Foundation** (11 issues from C1):
- [ ] [MED-001 C1] Add import validation - 1 day
- [ ] [MED-002 C1] Add OpenRouter error codes - 6h
- [ ] [MED-003 C1] Make timeouts configurable - 1 day
- [ ] [MED-004 C1] Validate model identifiers - 4h
- [ ] [MED-006 C1] Add health check API - 1 week
- [ ] [MED-007 C1] Make port configurable - 2h
- [ ] [MED-008 C1] Add stream recovery - 1 week
- [ ] [MED-009 C1] Validate function call format - 6h
- [ ] [MED-010 C1] Extract compression logic - 1 day
- [ ] [MED-011 C1] Add response size limits - 4h

**Tool System** (12 issues from C3):
- [ ] [MED-001 C3] Add web fetch timeout
- [ ] [MED-002 C3] Validate HTML sanitization
- [ ] [MED-003 C3] Split ShellTool
- [ ] [MED-004 C3] Add file size validation
- [ ] [MED-005 C3] Limit search results
- [ ] [MED-006 C3] Add caching for web fetches
- [ ] [MED-007 C3] Document web fetch risks
- [ ] [MED-008 C3] Add tool execution metrics
- [ ] [MED-009 C3] Validate tool response schema
- [ ] [MED-010 C3] Add file operation tests
- [ ] [MED-011 C3] Limit regex complexity
- [ ] [MED-012 C3] Add permission checks

**Phase 3 Gate**:
- [ ] Test coverage >80%
- [ ] All security tests passing
- [ ] Medium issues <20 remaining
- [ ] CI/CD reliable

---

## Phase 4: Major Refactoring (Target: Week 11-18)

**Goal**: Eliminate god components
**Status**: ⬜ Not Started
**Progress**: 0/15 (0%)

### Week 11-13: UI Container Refactoring

- [ ] **[CRIT-001 C5]** AppContainer.tsx (1,488→<300 lines) - 3 weeks
  - **Week 11: Extract Contexts**
    - [ ] Create AuthStateContext + useAuthActions
    - [ ] Create ThemeStateContext + useThemeActions
    - [ ] Create DialogStateContext + useDialogActions
    - [ ] Move auth hooks to AuthContainer
    - [ ] Move theme hooks to ThemeContainer
    - [ ] Tests for each context

  - **Week 12: Extract Input & Layout**
    - [ ] Create InputStateContext + useInputActions
    - [ ] Create LayoutStateContext + useLayoutActions
    - [ ] Extract to InputContainer
    - [ ] Extract to LayoutContainer
    - [ ] Tests for containers

  - **Week 13: Extract Streaming & Compose**
    - [ ] Create StreamingStateContext
    - [ ] Create SettingsStateContext
    - [ ] Extract to StreamingContainer
    - [ ] Extract to SettingsContainer
    - [ ] Compose final AppContainer
    - [ ] Integration tests
    - [ ] Performance verification

### Week 14-15: Streaming Hook Refactoring

- [ ] **[CRIT-002 C5]** useCodinGLMStream (1,290→<200 lines each) - 2 weeks
  - **Week 14: Core Extraction**
    - [ ] Extract useStreamProcessor (raw events)
    - [ ] Extract useToolOrchestrator (tools)
    - [ ] Extract useStreamCancellation (abort)
    - [ ] Tests for each hook

  - **Week 15: Polish & Integration**
    - [ ] Extract useStreamErrorHandler (errors)
    - [ ] Extract useLoopDetection (loops)
    - [ ] Extract useThoughtTracking (thoughts)
    - [ ] Extract useStreamState (state)
    - [ ] Integrate all hooks
    - [ ] Comprehensive tests
    - [ ] Performance benchmarks

### Week 16: Input Component Refactoring

- [ ] **[CRIT-003 C5]** InputPrompt.tsx (1,166→<150 lines each) - 1 week
  - [ ] Extract TextInput (core editing)
  - [ ] Extract CompletionEngine (completions)
  - [ ] Extract SyntaxHighlighter (syntax)
  - [ ] Extract ClipboardHandler (paste)
  - [ ] Extract KeyboardShortcuts (shortcuts)
  - [ ] Extract CursorRenderer (cursor)
  - [ ] Compose InputPrompt
  - [ ] Integration tests

### Week 17: LLM Service Refactoring

- [ ] **[HIGH-002 C2]** ZaiContentGenerator (1,351→<300 lines each) - 1 week
  - [ ] Extract ZaiHttpClient
  - [ ] Extract ZaiRequestFormatter
  - [ ] Extract ZaiResponseParser
  - [ ] Extract SseStreamParser
  - [ ] Integration tests

### Week 18: Shell & Tool Services

- [ ] **[HIGH-004 C5]** text-buffer (2,431→<400 lines) - 1 week
  - [ ] Create TextEditor class
  - [ ] Extract CursorManager
  - [ ] Extract SelectionManager
  - [ ] Extract UndoManager
  - [ ] Extract CompletionEngine
  - [ ] Extract VimIntegration
  - [ ] Integration tests

- [ ] **Service Refactoring** (Distributed)
  - [ ] [HIGH-001 C9] LoopDetectionService (506→<300)
  - [ ] [HIGH-002 C9] ShellExecutionService (813→<400)
  - [ ] [MED-003 C3] ShellTool split

**Phase 4 Acceptance**:
- [ ] No files >500 lines
- [ ] Clear SRP compliance
- [ ] Tests maintained/improved
- [ ] Performance unchanged

---

## Phase 5: LOW Priority & Polish (Target: Week 19-20)

**Goal**: Clean up technical debt
**Status**: ⬜ Not Started
**Progress**: 0/50 (0%)

### Week 19: Documentation & Constants

**Documentation** (~8 issues from C1):
- [ ] [LOW-001 C1] Add package.json description - 5min
- [ ] [LOW-002 C1] Document esbuild config - 1h
- [ ] [LOW-003 C1] Add bundle size docs - 30min
- [ ] [LOW-004 C1] Add server startup docs - 30min
- [ ] [LOW-005 C1] Document OpenRouter integration - 2h
- [ ] [LOW-006 C1] Add API error examples - 1h
- [ ] [LOW-007 C1] Document compression - 30min
- [ ] [LOW-008 C1] Add model config docs - 1h

**Magic Numbers** (~50 total across all chunks):
- [ ] Extract all magic numbers to constants
- [ ] Document rationale for each value
- [ ] Make configurable where appropriate
- [ ] Update tests

**Other LOW Issues**:
- [ ] [LOW-001 C3] Document allowlist format - 30min
- [ ] [LOW-002 C3] Document URL validation - 30min
- [ ] [LOW-003 C3] Improve tool error messages - 2h
- [ ] All LOW issues from C4 (8 total)
- [ ] All LOW issues from C5 (4 total)
- [ ] All LOW issues from C6 (9 total)
- [ ] All LOW issues from C7 (5 total)
- [ ] All LOW issues from C8 (5 total)
- [ ] All LOW issues from C9 (4 total)
- [ ] All LOW issues from C10 (3 total)

### Week 20: Technical Debt

**TODO/FIXME Resolution**:
- [ ] `run_shell_command.test.ts:311` - Flaky test
- [ ] `run_shell_command.test.ts:430` - Deflake test
- [ ] `gemini.tsx:321` - Refactor loadCliConfig
- [ ] `publish-release/action.yml:134` - Refactor publishing
- [ ] `InputPrompt.tsx` - Remove obsolete TODO
- [ ] `types.ts` - Ensure config never null
- [ ] `types.ts` - Remove deprecated args
- [ ] All other TODOs reviewed and tracked

**Skipped Tests**:
- [ ] Fix or document all 19 skipped tests
- [ ] Create tracking issues
- [ ] Add CI enforcement

**Final Cleanup**:
- [ ] Remove all commented code
- [ ] Standardize error handling
- [ ] Consistent naming conventions
- [ ] Final linting pass
- [ ] Update all documentation

**Phase 5 Acceptance**:
- [ ] All low-priority issues resolved
- [ ] Zero commented code
- [ ] All TODOs tracked
- [ ] Documentation complete

---

## Continuous Verification

### Daily
- [ ] Run full test suite
- [ ] Check build status
- [ ] Review PR queue

### Weekly
- [ ] Integration testing
- [ ] Performance benchmarks
- [ ] Coverage report
- [ ] Update this checklist
- [ ] Team standup

### Phase Gates
- [ ] Phase 0 complete + reviewed
- [ ] Phase 1 security audit passed
- [ ] Phase 2 stability verified
- [ ] Phase 3 coverage achieved
- [ ] Phase 4 architecture approved
- [ ] Phase 5 polish complete

---

## Notes & Blockers

### Blockers
*Document any blockers here with date and description*

---

### Deferred Items
*Items postponed to future releases*

---

### Decisions Made
*Key architectural or process decisions*

---

**How to Use This Checklist**:
1. Check off items as completed
2. Update progress percentages weekly
3. Document blockers immediately
4. Link PRs next to completed items
5. Review and adjust priorities as needed

**Last Review**: 2025-11-12
**Next Review**: TBD
**Maintained By**: Engineering Team
