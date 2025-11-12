# Audit Chunk 4: Configuration, Policy & Security

**Duration**: 2-3 days
**Priority**: Critical

## Objectives

Understand the configuration system, execution policies, security boundaries, OAuth handling, and extension loading. This chunk focuses on how the system protects itself and users.

## Key Questions to Answer

1. How is configuration loaded and validated?
2. How do execution policies work?
3. What are the security boundaries?
4. How is OAuth handled for MCP servers?
5. How are extensions loaded and isolated?
6. What validation exists for user settings?
7. How are trusted folders managed?
8. How are secrets stored securely?

## Files to Audit

### Priority 1: Core Configuration
- [ ] `packages/cli/src/config/config.ts` ⭐ **CRITICAL**
- [ ] `packages/cli/src/config/settings.ts`
- [ ] `packages/cli/src/config/settingsSchema.ts` (validation)
- [ ] `packages/core/src/config/config.ts`
- [ ] `packages/core/src/config/settings.ts`
- [ ] `packages/core/src/config/schema.ts`

### Priority 2: Policy Engine
- [ ] `packages/core/src/policy/policy-engine.ts` ⭐ **SECURITY CRITICAL**
- [ ] `packages/core/src/policy/types.ts`
- [ ] `packages/core/src/policy/config.ts`
- [ ] `packages/core/src/policy/toml-loader.ts`
- [ ] `packages/cli/src/config/policy.ts`

### Priority 3: Policy Definitions
- [ ] `packages/cli/src/config/policies/read-only.toml`
- [ ] `packages/cli/src/config/policies/write.toml`
- [ ] `packages/cli/src/config/policies/yolo.toml`
- [ ] `packages/core/src/policy/policies/` (any TOML files)

### Priority 4: Trusted Folders & Permissions
- [ ] `packages/cli/src/config/trustedFolders.ts` ⭐ **SECURITY CRITICAL**
- [ ] `packages/cli/src/config/sandboxConfig.ts`

### Priority 5: Extension System
- [ ] `packages/cli/src/config/extension-manager.ts` ⭐ **SECURITY CRITICAL**
- [ ] `packages/cli/src/config/extensions/extensionSettings.ts`
- [ ] `packages/cli/src/config/extensions/extensionEnablement.ts`
- [ ] `packages/cli/src/config/extensions/storage.ts`
- [ ] `packages/cli/src/config/extensions/variables.ts`
- [ ] `packages/cli/src/config/extensions/github.ts`

### Priority 6: Authentication
- [ ] `packages/cli/src/config/auth.ts` ⭐ **SECURITY CRITICAL**
- [ ] `packages/core/src/mcp/oauth-provider.ts`
- [ ] `packages/core/src/mcp/google-auth-provider.ts`
- [ ] `packages/core/src/mcp/sa-impersonation-provider.ts`
- [ ] `packages/core/src/mcp/oauth-utils.ts`

### Priority 7: Token Storage
- [ ] `packages/core/src/mcp/token-storage/base-token-storage.ts`
- [ ] `packages/core/src/mcp/token-storage/file-token-storage.ts` ⭐ **SECURITY CRITICAL**
- [ ] `packages/core/src/mcp/token-storage/keychain-token-storage.ts`
- [ ] `packages/core/src/mcp/token-storage/hybrid-token-storage.ts`

### Priority 8: Related Services
- [ ] `packages/core/src/services/fileSystemService.ts` (permission checks)
- [ ] `packages/core/src/utils/userAccountManager.ts`
- [ ] `packages/core/src/utils/installationManager.ts`

### Priority 9: Test Files
- [ ] All files in `packages/cli/src/config/__tests__/`
- [ ] All files in `packages/core/src/policy/__tests__/`
- [ ] All files in `packages/core/src/mcp/__tests__/`
- [ ] `integration-tests/extensions-*.test.ts`

### Priority 10: Documentation
- [ ] `gemini-cli/docs/core/policy-engine.md`
- [ ] `gemini-cli/docs/cli/trusted-folders.md`
- [ ] `gemini-cli/docs/cli/sandbox.md`
- [ ] `gemini-cli/docs/extensions/`

## Specific Audit Checklist

### Configuration Loading
- [ ] Review config file discovery logic
- [ ] Check for proper path resolution
- [ ] Verify default values are secure
- [ ] Look for race conditions in loading
- [ ] Check for proper error handling
- [ ] Verify config merging logic
- [ ] Review environment variable precedence

### Configuration Validation
- [ ] Review schema validation implementation
- [ ] Check for missing validations
- [ ] Verify all user inputs are validated
- [ ] Look for type coercion issues
- [ ] Check for proper error messages
- [ ] Review custom validators
- [ ] Verify enum/constant validation

### Policy Engine Security
- [ ] **Authorization Checks**: Verify every tool execution checks policy
- [ ] **Policy Bypass**: Look for ways to bypass policies
- [ ] **Default Policy**: Verify safe default (most restrictive)
- [ ] **Policy Loading**: Check for tampering protection
- [ ] **Policy Evaluation**: Verify correct logic
- [ ] **Trusted Folder Logic**: Check for path traversal in trust checks
- [ ] **Policy Caching**: Verify cache invalidation

### TOML Policy Files
- [ ] Review read-only policy completeness
- [ ] Check write policy restrictions
- [ ] Verify yolo policy warnings
- [ ] Look for missing tool restrictions
- [ ] Check for syntax errors
- [ ] Verify policy documentation

### Trusted Folders
- [ ] **Path Canonicalization**: Verify proper path normalization
- [ ] **Symlink Handling**: Check for symlink attacks
- [ ] **Parent Directory Checks**: Verify proper containment checks
- [ ] **Race Conditions**: Check for TOCTOU issues
- [ ] **Permission Inheritance**: Verify sub-folder handling
- [ ] **Trust Escalation**: Look for ways to escalate trust

### Extension Security
- [ ] **Extension Loading**: Verify safe loading mechanism
- [ ] **Extension Isolation**: Check for proper isolation
- [ ] **Extension Validation**: Verify extension integrity
- [ ] **Extension Permissions**: Check permission boundaries
- [ ] **Malicious Extensions**: Consider attack vectors
- [ ] **Extension Updates**: Verify secure update mechanism
- [ ] **Extension Removal**: Check for complete cleanup

### OAuth & Token Security
- [ ] **Token Storage**: Verify secure storage (encrypted?)
- [ ] **Token Access**: Check for proper access controls
- [ ] **Token Exposure**: Look for token leaks in logs
- [ ] **Token Refresh**: Verify secure refresh flow
- [ ] **Token Revocation**: Check for proper revocation
- [ ] **Scope Validation**: Verify minimal scopes requested
- [ ] **State Parameter**: Check for CSRF protection
- [ ] **Redirect URI**: Verify proper validation

### File Token Storage (Critical)
- [ ] **File Permissions**: Verify 0600 (owner read/write only)
- [ ] **File Location**: Check for secure default location
- [ ] **Encryption**: Verify tokens are encrypted at rest
- [ ] **Access Controls**: Check for proper access restrictions
- [ ] **Temp Files**: Look for insecure temporary storage
- [ ] **Error Handling**: Verify no token leaks in errors

### Keychain Storage
- [ ] **OS Keychain Integration**: Verify proper API usage
- [ ] **Fallback Behavior**: Check secure fallback
- [ ] **Error Handling**: Verify proper error messages
- [ ] **Access Controls**: Check for proper keychain ACLs

### Secrets Management
- [ ] **API Keys**: Verify never logged or exposed
- [ ] **Environment Variables**: Check for secure handling
- [ ] **Configuration Files**: Verify no secrets in examples
- [ ] **Error Messages**: Check for secret exposure in errors
- [ ] **Debugging**: Verify debug output doesn't leak secrets
- [ ] **Telemetry**: Check telemetry doesn't send secrets

## SRP Focus Areas

### Look for:
- Config loading mixed with validation
- Policy engine mixed with policy storage
- Auth handling mixed with token storage
- Extension loading mixed with execution

### Expected Responsibilities:
- Loader: Only loads configuration
- Validator: Only validates configuration
- Policy Engine: Only evaluates policies
- Token Storage: Only stores/retrieves tokens
- Auth Provider: Only handles authentication

## Bug Hunting Areas

### Critical Bugs to Find:
- **Security Bypass**: Ways to bypass security policies
- **Token Leakage**: Tokens exposed in logs or errors
- **Path Traversal**: Escape trusted folder boundaries
- **Race Conditions**: TOCTOU in permission checks
- **Injection**: Config injection vulnerabilities
- **Default Insecure**: Unsafe default settings
- **Missing Validation**: User input not validated
- **Weak Permissions**: File permissions too permissive

### Edge Cases:
- Empty configuration
- Missing configuration files
- Corrupted TOML files
- Circular policy references
- Very long file paths
- Special characters in paths
- Concurrent config reloads
- Token refresh during operation
- Extension conflicts
- Invalid OAuth responses

## Technical Debt Indicators

### Watch for:
- TODO comments about security
- "Fix later" comments on validation
- Commented-out security checks
- Hard-coded paths or secrets
- Temporary permission bypasses
- Incomplete policy implementations
- Missing OAuth error handling
- Weak default policies

## Testing Gaps

### Critical Tests Needed:
- [ ] **Security Tests**:
  - Policy bypass attempts
  - Path traversal in trusted folders
  - Token exposure in logs
  - Invalid TOML parsing
  - Malicious extension loading
  - OAuth CSRF attacks
  - Token storage security
- [ ] **Edge Cases**:
  - Missing config files
  - Corrupted config
  - Concurrent access
  - Invalid schema
- [ ] **Error Handling**:
  - Config load failures
  - Policy evaluation errors
  - OAuth failures
  - Token storage failures

### Integration Tests:
- [ ] End-to-end policy enforcement
- [ ] OAuth flow completion
- [ ] Extension installation and loading
- [ ] Config reload scenarios

## Code Quality Checks

### Policy Engine Specific:
- [ ] Clear, readable policy evaluation logic
- [ ] Comprehensive logging (without secrets)
- [ ] Proper error messages
- [ ] No magic strings
- [ ] Fail-secure defaults
- [ ] Complete test coverage

### Token Storage Specific:
- [ ] Proper encryption implementation
- [ ] Secure key derivation
- [ ] Safe file operations
- [ ] Proper cleanup on errors
- [ ] No token exposure in any path

## Integration Points

Document how these integrate:
1. Config System → All Components (settings)
2. Policy Engine → Tool Execution (authorization)
3. Trusted Folders → File Operations (permission checks)
4. Extension Manager → Tool Registry (extension tools)
5. OAuth Provider → MCP Client (authentication)
6. Token Storage → OAuth Provider (token persistence)

## Security Checklist

For each security-critical component:
- [ ] Threat model documented
- [ ] Attack vectors considered
- [ ] Defense in depth implemented
- [ ] Fail-secure behavior
- [ ] Audit logging present
- [ ] Security tests comprehensive
- [ ] Penetration testing performed

## Red Flags to Watch For

🚩 **CRITICAL**: Tokens stored in plaintext
🚩 **CRITICAL**: Policy bypass possible
🚩 **CRITICAL**: Default settings are insecure
🚩 Secrets in log files or error messages
🚩 Missing input validation
🚩 Unsafe default policies
🚩 No encryption for stored secrets
🚩 Weak file permissions
🚩 Path traversal in trusted folders
🚩 Missing CSRF protection in OAuth
🚩 No token expiration handling
🚩 Extension code not validated
🚩 Environment variables exposed
🚩 Race conditions in permission checks

## Success Criteria

✅ Complete understanding of security model
✅ All security vulnerabilities identified
✅ Policy engine fully audited
✅ Token storage verified secure
✅ Extension security assessed
✅ OAuth implementation reviewed
✅ All findings documented with severity

## Security Severity Assessment

- **Critical**: Allows unauthorized access, secret exposure, or system compromise
- **High**: Weakens security boundaries, potential privilege escalation
- **Medium**: Security best practice violation, defense-in-depth gap
- **Low**: Minor security improvement, hardening opportunity

## Notes Section

Document:
- Security architecture strengths
- Areas of concern
- Defense-in-depth layers
- Security assumptions
- Recommendations for hardening

---

## Next Steps

After completing this chunk:
1. **IMMEDIATE**: Report critical security vulnerabilities
2. Verify security issues with proof-of-concept
3. Review OAuth implementation carefully
4. Proceed to Chunk 5: Terminal UI & Interactive Mode
