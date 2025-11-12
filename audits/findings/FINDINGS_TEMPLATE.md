# Audit Findings Template

Use this template to document findings for each chunk. Copy this template for each chunk (e.g., `chunk-01-findings.md`, `chunk-02-findings.md`, etc.).

---

# Chunk [N] Findings: [Chunk Name]

**Auditor**: [Name]
**Date Started**: [YYYY-MM-DD]
**Date Completed**: [YYYY-MM-DD]
**Time Spent**: [Hours]

## Executive Summary

[2-3 paragraph overview of what was audited and key takeaways]

### Quick Stats
- **Files Audited**: [Number]
- **Total Findings**: [Number]
- **Critical Issues**: [Number]
- **High Priority Issues**: [Number]
- **Medium Priority Issues**: [Number]
- **Low Priority Issues**: [Number]

---

## Critical Issues ⚠️

### [CRIT-001] Brief Title

**Severity**: Critical
**Category**: [SRP / Bug / Debt / Quality / Testing / Security]
**File**: `path/to/file.ts:123-145`

**Description**:
[Detailed description of the issue, why it's critical, and the potential impact]

**Evidence**:
```typescript
// Problematic code snippet with line numbers
// Show the actual code that demonstrates the problem
```

**Impact**:
- [Specific impact point 1]
- [Specific impact point 2]
- [Specific impact point 3]

**Recommendation**:
[Specific, actionable recommendation for fixing the issue]

**Suggested Fix** (if applicable):
```typescript
// Proposed code fix
```

**Priority**: Immediate / High / Medium / Low
**Effort**: [Hours/Days estimate]

---

### [CRIT-002] [Next Critical Issue]

[Repeat above format for each critical issue]

---

## High Priority Issues 🔴

### [HIGH-001] Brief Title

**Severity**: High
**Category**: [SRP / Bug / Debt / Quality / Testing / Security]
**File**: `path/to/file.ts:123-145`

**Description**:
[Description of the issue]

**Evidence**:
```typescript
// Code snippet
```

**Recommendation**:
[How to fix it]

**Priority**: High
**Effort**: [Estimate]

---

## Medium Priority Issues 🟡

### [MED-001] Brief Title

**Severity**: Medium
**Category**: [SRP / Bug / Debt / Quality / Testing / Security]
**File**: `path/to/file.ts:123-145`

**Description**:
[Description of the issue]

**Evidence**:
```typescript
// Code snippet
```

**Recommendation**:
[How to fix it]

**Priority**: Medium
**Effort**: [Estimate]

---

## Low Priority Issues 🟢

### [LOW-001] Brief Title

**Severity**: Low
**Category**: [SRP / Bug / Debt / Quality / Testing / Security]
**File**: `path/to/file.ts:123-145`

**Description**:
[Description of the issue]

**Recommendation**:
[How to fix it]

**Priority**: Low
**Effort**: [Estimate]

---

## Positive Patterns ✅

Document good practices and patterns observed:

### Pattern 1: [Name]
- **Location**: [Files/components]
- **Description**: [What makes this good]
- **Why it works**: [Explanation]
- **Recommendation**: [Should be replicated elsewhere?]

### Pattern 2: [Name]
[...]

---

## Technical Debt Summary

### TODO/FIXME Comments Found
| File | Line | Comment | Priority |
|------|------|---------|----------|
| path/to/file.ts | 123 | "TODO: Fix this later" | High |
| path/to/file2.ts | 456 | "FIXME: Handle error" | Medium |

### Commented-Out Code
| File | Lines | Reason (if noted) | Action |
|------|-------|-------------------|--------|
| path/to/file.ts | 100-120 | Old implementation | Remove |

### Code Duplication
| Pattern | Locations | Recommendation |
|---------|-----------|----------------|
| [Description] | file1.ts, file2.ts | Extract to utility |

---

## Testing Gaps

### Missing Tests
| Component | Type Needed | Priority | Effort |
|-----------|-------------|----------|--------|
| ComponentName | Unit | High | 2h |
| ServiceName | Integration | High | 4h |

### Inadequate Tests
| Test File | Issue | Recommendation |
|-----------|-------|----------------|
| file.test.ts | No edge cases | Add tests for null, empty, large inputs |

### Flaky Tests
| Test | Failure Rate | Root Cause | Fix |
|------|--------------|------------|-----|
| test name | 10% | Race condition | Add proper awaits |

---

## Security Findings

### Vulnerabilities
| ID | Type | Severity | File | Description |
|----|------|----------|------|-------------|
| SEC-001 | Command Injection | Critical | shell.ts:45 | User input not sanitized |

### Security Improvements
| ID | Type | Priority | Description |
|----|------|----------|-------------|
| SEC-IMP-001 | Hardening | High | Add rate limiting to API |

---

## Performance Findings

### Performance Issues
| Issue | Location | Impact | Recommendation |
|-------|----------|--------|----------------|
| Blocking I/O | file.ts:123 | UI lag | Make async |

### Optimization Opportunities
| Opportunity | Location | Potential Gain | Effort |
|-------------|----------|----------------|--------|
| Caching | service.ts | 50% faster | 4h |

---

## SRP Violations

### Classes/Functions Doing Too Much
| Component | File | Responsibilities | Recommendation |
|-----------|------|------------------|----------------|
| GodClass | god.ts:10-500 | 1. X, 2. Y, 3. Z | Split into 3 classes |

### Mixed Concerns
| Location | Concern 1 | Concern 2 | Recommendation |
|----------|-----------|-----------|----------------|
| file.ts:50 | Business logic | UI rendering | Separate |

---

## Code Quality Issues

### Naming Issues
| Location | Current Name | Issue | Suggested Name |
|----------|--------------|-------|----------------|
| file.ts:10 | x | Unclear | userCount |

### Complexity Issues
| Function | Cyclomatic Complexity | Lines | Recommendation |
|----------|----------------------|-------|----------------|
| doThings() | 25 | 150 | Refactor into smaller functions |

### Magic Numbers/Strings
| Location | Value | Should Be |
|----------|-------|-----------|
| file.ts:50 | 86400 | SECONDS_PER_DAY |

---

## Integration Points Documented

### Component Interactions
```
[Component A] ---> [Component B] (via interface X)
        |
        +--------> [Component C] (via event Y)
```

### Data Flows
1. [Source] → [Processing] → [Destination]
2. [...]

### Dependencies
- [Component A] depends on [Component B] for [reason]
- [...]

---

## Recommendations Summary

### Immediate Actions (Do First)
1. [Action 1] - [Reason] - [Effort: Xh]
2. [Action 2] - [Reason] - [Effort: Xh]

### Short Term (Within 1 week)
1. [Action] - [Reason] - [Effort: Xh]

### Medium Term (Within 1 month)
1. [Action] - [Reason] - [Effort: Xd]

### Long Term (Backlog)
1. [Action] - [Reason] - [Effort: Xw]

---

## Metrics

### Code Metrics
- **Total Lines Audited**: [Number]
- **Average File Size**: [Lines]
- **Largest File**: [File] ([Lines] lines)
- **Cyclomatic Complexity**: Avg [X], Max [Y]

### Test Metrics
- **Test Coverage**: [%] (if measurable)
- **Test Files**: [Number]
- **Missing Tests**: [Number]

### Issue Breakdown
| Category | Count | % of Total |
|----------|-------|------------|
| SRP | X | Y% |
| Bug | X | Y% |
| Debt | X | Y% |
| Quality | X | Y% |
| Testing | X | Y% |
| Security | X | Y% |
| **Total** | **X** | **100%** |

---

## Questions & Clarifications Needed

1. [Question about specific code/architecture]
2. [Need clarification on intended behavior]
3. [...]

---

## Notes

### Observations
- [General observation 1]
- [General observation 2]

### Patterns Noticed
- [Pattern across multiple files]

### Things to Watch in Future Chunks
- [Something that might be relevant later]

---

## Appendix

### Files Audited (Complete List)
- [ ] `path/to/file1.ts`
- [ ] `path/to/file2.ts`
- [ ] `path/to/file3.ts`
- [...]

### Test Files Reviewed
- [ ] `path/to/test1.test.ts`
- [ ] `path/to/test2.test.ts`
- [...]

### Time Log
| Date | Hours | Focus Area |
|------|-------|------------|
| 2025-01-15 | 4h | Files 1-5 |
| 2025-01-16 | 4h | Files 6-10 |
| 2025-01-17 | 3h | Tests & Documentation |

---

**Audit Completed**: [Yes/No]
**Ready for Review**: [Yes/No]
**Reviewed By**: [Name]
**Review Date**: [YYYY-MM-DD]
