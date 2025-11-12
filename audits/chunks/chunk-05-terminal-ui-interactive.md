# Audit Chunk 5: Terminal UI & Interactive Mode

**Duration**: 2-3 days
**Priority**: High

## Objectives

Understand the React/Ink terminal UI implementation, state management, interactive features, slash commands, and user experience. This is the primary user interface for the application.

## Key Questions to Answer

1. How does React/Ink rendering work?
2. How is state managed across components?
3. How do slash commands integrate?
4. How is the thinking mode visualized?
5. How are errors displayed to users?
6. What are the performance characteristics?
7. How is keyboard input handled?
8. How are themes applied?

## Files to Audit

### Priority 1: Root Component
- [ ] `packages/cli/src/ui/gemini.tsx` ⭐ **CRITICAL**
- [ ] `packages/cli/src/gemini.ts` (mode selection)

### Priority 2: State Management
- [ ] `packages/cli/src/ui/state/stateManager.ts`
- [ ] All files in `packages/cli/src/ui/state/` (~20 files)
- [ ] `packages/cli/src/ui/contexts/` (10+ files)
  - ChatContext.tsx
  - SettingsContext.tsx
  - etc.

### Priority 3: Hooks
- [ ] `packages/cli/src/ui/hooks/useChat.ts` ⭐
- [ ] `packages/cli/src/ui/hooks/useSettings.ts` ⭐
- [ ] `packages/cli/src/ui/hooks/useHistory.ts`
- [ ] `packages/cli/src/ui/hooks/useTelemetry.ts`
- [ ] All other hooks in `packages/cli/src/ui/hooks/` (~30 files)

### Priority 4: Message Rendering
- [ ] `packages/cli/src/ui/components/messages/` (50+ files)
  - AssistantMessage.tsx
  - UserMessage.tsx
  - ToolCall.tsx
  - ToolResult.tsx
  - ReasoningMessage.tsx (thinking mode)
  - ErrorMessage.tsx
  - etc.

### Priority 5: Slash Commands
- [ ] All files in `packages/cli/src/ui/commands/` (50+ files)
  - aboutCommand.ts, authCommand.ts
  - chatCommand.ts, clearCommand.ts
  - compressCommand.ts, copyCommand.ts
  - editCommand.ts, exitCommand.ts
  - helpCommand.ts, modelCommand.ts
  - settingsCommand.ts, themeCommand.ts
  - etc.

### Priority 6: Shared Components
- [ ] `packages/cli/src/ui/components/shared/` (30+ files)
  - Input.tsx, Button.tsx
  - Spinner.tsx, ErrorBoundary.tsx
  - etc.

### Priority 7: Views
- [ ] `packages/cli/src/ui/components/views/` (20+ files)
  - ChatView.tsx
  - HistoryView.tsx
  - SettingsView.tsx
  - etc.

### Priority 8: Layouts & Themes
- [ ] `packages/cli/src/ui/layouts/` (10+ files)
- [ ] `packages/cli/src/ui/themes/` (20+ files)
  - defaultTheme.ts
  - darkTheme.ts
  - lightTheme.ts

### Priority 9: UI Services
- [ ] `packages/cli/src/services/CommandService.ts`
- [ ] `packages/cli/src/services/FileCommandLoader.ts`
- [ ] `packages/cli/src/services/BuiltinCommandLoader.ts`

### Priority 10: Test Files
- [ ] All UI test files (`*.test.tsx`, `*.test.ts`)
- [ ] Snapshot tests in `__snapshots__/`

## Specific Audit Checklist

### React/Ink Architecture
- [ ] Understand component hierarchy
- [ ] Review prop drilling vs context usage
- [ ] Check for unnecessary re-renders
- [ ] Verify proper memo usage
- [ ] Look for performance bottlenecks
- [ ] Check for memory leaks
- [ ] Review key prop usage

### State Management
- [ ] Review state update patterns
- [ ] Check for race conditions
- [ ] Verify immutable updates
- [ ] Look for state synchronization issues
- [ ] Check for stale closures
- [ ] Review reducer logic
- [ ] Verify action creators

### Error Handling
- [ ] Review ErrorBoundary implementation
- [ ] Check error message display
- [ ] Verify error recovery
- [ ] Look for unhandled errors
- [ ] Check for proper error logging
- [ ] Review user-friendly error messages

### Input Handling
- [ ] Review keyboard shortcut implementation
- [ ] Check for input validation
- [ ] Verify proper event handling
- [ ] Look for race conditions in input
- [ ] Check for proper focus management
- [ ] Review input buffering

### Slash Commands
- [ ] Verify all commands are tested
- [ ] Check for command conflicts
- [ ] Review command argument parsing
- [ ] Look for proper error handling
- [ ] Check for command documentation
- [ ] Verify permission checks

### Message Rendering
- [ ] Review rendering performance
- [ ] Check for proper escaping
- [ ] Verify ANSI code handling
- [ ] Look for layout issues
- [ ] Check for long message handling
- [ ] Review streaming updates

### Thinking Mode Visualization
- [ ] Review thinking chunk display
- [ ] Check for proper streaming
- [ ] Verify collapse/expand logic
- [ ] Look for rendering issues
- [ ] Check for performance impact

## SRP Focus Areas

### Look for:
- Components doing too much (god components)
- Mixed concerns in hooks
- State management mixed with business logic
- Rendering logic mixed with data fetching
- Command handlers with complex business logic

### Expected Responsibilities:
- Components: Only rendering and local state
- Hooks: Only specific state/side effect
- Contexts: Only state provision
- Commands: Only command orchestration

## Bug Hunting Areas

### Critical Bugs to Find:
- **React Anti-patterns**: Direct state mutation, missing dependencies
- **Memory Leaks**: Unclosed subscriptions, growing state
- **Race Conditions**: Concurrent state updates
- **Rendering Issues**: Flicker, incorrect display
- **Input Bugs**: Lost keystrokes, wrong shortcuts
- **State Bugs**: Stale state, synchronization issues
- **Performance**: Slow rendering, lag

### Edge Cases:
- Very long messages
- Rapid user input
- Streaming interruption
- Command execution during streaming
- Theme switching during operation
- Window resize
- Terminal size changes
- Concurrent command execution

## Technical Debt Indicators

### Watch for:
- TODO comments about UI improvements
- Commented-out components
- Duplicate component logic
- Hard-coded styling
- Magic numbers for layout
- Prop drilling through many layers
- Large components (>200 lines)
- Complex state logic in components

## Testing Gaps

### Critical Tests Needed:
- [ ] Component rendering tests
- [ ] User interaction tests
- [ ] Keyboard shortcut tests
- [ ] Error boundary tests
- [ ] State management tests
- [ ] Hook tests
- [ ] Command execution tests
- [ ] Snapshot tests for UI

### Integration Tests:
- [ ] Full chat flow
- [ ] Command execution flow
- [ ] Error recovery flow
- [ ] Theme switching

## Code Quality Checks

### Component Quality:
- [ ] Component length (<200 lines ideally)
- [ ] Prop types clear
- [ ] Proper TypeScript types
- [ ] Clear component names
- [ ] Single responsibility
- [ ] Proper composition
- [ ] Reusable components

### Hook Quality:
- [ ] Clear purpose
- [ ] Proper dependencies
- [ ] No missing dependencies
- [ ] Proper cleanup
- [ ] Testable
- [ ] Well-named

## Performance Considerations

- [ ] Check for unnecessary renders
- [ ] Review memo/useMemo usage
- [ ] Look for expensive computations
- [ ] Check list rendering performance
- [ ] Review streaming update efficiency
- [ ] Look for layout thrashing

## Accessibility Considerations

- [ ] Keyboard navigation
- [ ] Screen reader compatibility
- [ ] Color contrast
- [ ] Clear error messages
- [ ] Focus indicators

## Integration Points

Document:
1. UI → Core (API calls)
2. UI → Services (command execution)
3. UI → Config (settings)
4. Commands → Tools (tool execution)
5. Streaming → UI Updates (real-time)

## Red Flags to Watch For

🚩 Direct state mutation
🚩 Missing useEffect dependencies
🚩 Memory leaks (subscriptions not cleaned up)
🚩 Components >300 lines
🚩 Prop drilling >3 levels
🚩 No error boundaries
🚩 Unhandled promise rejections in UI
🚩 Performance issues (lag, flicker)
🚩 Hard-coded strings (no i18n consideration)

## Success Criteria

✅ Complete understanding of UI architecture
✅ All UI bugs identified
✅ Performance issues documented
✅ State management patterns clear
✅ All findings documented
✅ User experience issues noted

## Notes Section

Document:
- UI/UX issues
- Performance observations
- Code patterns (good/bad)
- Refactoring opportunities

---

## Next Steps

After completing this chunk:
1. Review UI/UX findings
2. Test UI interactively
3. Proceed to Chunk 6: Non-Interactive & Output Modes
