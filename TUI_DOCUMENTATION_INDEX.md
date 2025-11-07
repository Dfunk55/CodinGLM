# CodinGLM TUI Documentation Index

This directory contains comprehensive documentation of the CodinGLM Text User Interface (TUI) implementation. All documents have been created to help understand the architecture, components, and file organization.

## Documentation Files

### 1. TUI_IMPLEMENTATION_ANALYSIS.md (17 KB, 488 lines)
**The most comprehensive guide to understanding the TUI.**

Contents:
- Overview and entry point information
- Technology stack details
- Core directory structure breakdown
- Detailed component descriptions (AppContainer, layouts, MainContent, input system, streaming)
- Advanced keyboard input handling explanation
- Message type system
- UI state management architecture
- Rendering pipeline and component flow
- User input handling (text, commands, special modes)
- Keyboard event processing architecture
- Theme system (12+ themes)
- Performance optimizations
- Known limitations and improvement suggestions
- Integration points and external dependencies
- Testing infrastructure
- Accessibility features

**Best for**: Understanding the complete TUI architecture, how components interact, streaming logic, and state management.

**Start here if**: You want a comprehensive overview of how the TUI works.

---

### 2. TUI_FILE_INDEX.md (13 KB, 332 lines)
**A detailed map of every important file in the TUI codebase.**

Contents:
- Entry point files (gemini.tsx, AppContainer.tsx)
- Layout component locations
- All 80+ hook files listed with descriptions
- 100+ component files organized by type
- 12 context provider files
- Dialog components
- Slash command definitions (30+)
- Keyboard handling files
- Theme system files (12 themes)
- Type definitions
- Utility and helper files
- Configuration and settings files
- Auth handling files
- Test file locations
- Statistics (364 files, 63,000+ lines)
- File organization patterns
- Dependency map
- Entry point flow diagram

**Best for**: Quickly finding specific files, understanding the file structure, locating components you need to modify.

**Use this when**: You need to find where a specific feature is implemented.

---

### 3. TUI_ARCHITECTURE_QUICK_REFERENCE.md (13 KB, 468 lines)
**Visual diagrams and quick reference for the TUI architecture.**

Contents:
- Data flow architecture (input to output)
- State management architecture
- Rendering pipeline with component hierarchy
- Component hierarchy diagram (nested structure)
- Message type routing logic
- Input handling pipeline (keyboard to commands)
- Streaming state machine (Idle -> Responding -> WaitingForConfirmation)
- Hook integration points in AppContainer
- Terminal dimension calculations
- Complete context tree
- Command processing flow
- Keyboard shortcut resolution
- Theme system architecture
- Performance optimization points
- Testing strategy
- Key statistics (scale, performance numbers)
- Quick navigation guide

**Best for**: Visual learners, quickly understanding data flow, reference for architecture patterns.

**Use this when**: You need to understand how components communicate or data flows through the system.

---

## Quick Start Guide

### I want to understand...

**How the TUI renders content**
→ TUI_IMPLEMENTATION_ANALYSIS.md → "Rendering Pipeline" section

**How user input is processed**
→ TUI_ARCHITECTURE_QUICK_REFERENCE.md → "Input Handling Pipeline" section

**How streaming works**
→ TUI_IMPLEMENTATION_ANALYSIS.md → "Streaming & API Integration" section

**Where a specific component is located**
→ TUI_FILE_INDEX.md → Search for component name

**The state management approach**
→ TUI_ARCHITECTURE_QUICK_REFERENCE.md → "State Management Architecture"

**How keyboard shortcuts work**
→ TUI_ARCHITECTURE_QUICK_REFERENCE.md → "Keyboard Shortcut Resolution"

**The complete message display system**
→ TUI_IMPLEMENTATION_ANALYSIS.md → "Message Display Components" section

**How to add a new feature**
→ TUI_IMPLEMENTATION_ANALYSIS.md → "Integration Points" section

---

## Key Numbers & Scale

| Metric | Count |
|--------|-------|
| Total UI Files | 364 |
| Total Lines of UI Code | 63,000+ |
| React Components | 100+ |
| Custom Hooks | 80+ |
| Context Providers | 12 |
| Dialog Components | 10+ |
| Message Types | 15+ |
| Theme Files | 12 |
| Slash Commands | 30+ |
| Test Files | 50+ |

---

## Architecture at a Glance

```
User Input (Keyboard/Mouse)
    ↓
KeypressContext (sequence parsing)
    ↓
AppContainer (state management hub)
    ├─→ useGeminiStream (API communication)
    ├─→ useHistory (message persistence)
    ├─→ useTextBuffer (text editing)
    └─→ 20+ other hooks
    ↓
UIStateContext (read-only state)
    ↓
DefaultAppLayout
    ├─→ MainContent (message display)
    └─→ Composer (input area)
        ├─→ LoadingIndicator
        ├─→ InputPrompt
        └─→ Footer
```

---

## Main Components at a Glance

| Component | Purpose | File |
|-----------|---------|------|
| **AppContainer** | Central state hub | AppContainer.tsx (1,489 lines) |
| **MainContent** | Renders chat history | components/MainContent.tsx |
| **Composer** | Input area wrapper | components/Composer.tsx |
| **InputPrompt** | Text input field | components/InputPrompt.tsx |
| **useGeminiStream** | API streaming | hooks/useGeminiStream.ts (1000+ lines) |
| **KeypressContext** | Keyboard input | contexts/KeypressContext.tsx (1000+ lines) |
| **HistoryItemDisplay** | Message router | components/HistoryItemDisplay.tsx |
| **DefaultAppLayout** | Main layout | layouts/DefaultAppLayout.tsx |

---

## Core Hooks at a Glance

| Hook | Purpose |
|------|---------|
| **useGeminiStream** | API streaming, tool execution, approval modes |
| **useHistory** | Chat history management |
| **useTextBuffer** | Multi-line text editing |
| **useKeypress** | Subscribe to keyboard events |
| **useReactToolScheduler** | Tool execution orchestration |
| **useMessageQueue** | Message buffering during streaming |
| **useTerminalSize** | Terminal dimension tracking |
| **useThemeCommand** | Theme dialog management |
| **useAuthCommand** | Authentication handling |

---

## Important Files to Know

**Essential Core Files**:
- `/src/gemini.tsx` - Entry point
- `/src/ui/AppContainer.tsx` - State management hub
- `/src/ui/contexts/KeypressContext.tsx` - Input handling
- `/src/ui/hooks/useGeminiStream.ts` - API streaming

**Layout Files**:
- `/src/ui/layouts/DefaultAppLayout.tsx` - Main layout
- `/src/ui/components/MainContent.tsx` - Content display area
- `/src/ui/components/Composer.tsx` - Input area

**Input Components**:
- `/src/ui/components/InputPrompt.tsx` - Text input
- `/src/ui/components/SuggestionsDisplay.tsx` - Suggestions

**Message Display**:
- `/src/ui/components/HistoryItemDisplay.tsx` - Message router
- `/src/ui/components/messages/GeminiMessage.tsx` - API response display
- `/src/ui/utils/MarkdownDisplay.tsx` - Markdown rendering

---

## State Management Quick Reference

**State is stored in**:
1. AppContainer.tsx (40+ state variables)
2. UIStateContext (1300+ line object)
3. Custom hooks (history, buffer, streaming, etc.)

**State is accessed via**:
1. useUIState() hook (for read-only access)
2. useUIActions() hook (for write access)
3. useXxxCommand() hooks (for feature-specific state)

**Context providers** (12 total):
1. AppContext - Version info
2. UIStateContext - Main UI state
3. UIActionsContext - Action callbacks
4. ConfigContext - Configuration
5. SettingsContext - User settings
6. KeypressContext - Keyboard events
7. MouseContext - Mouse events
8. StreamingContext - Streaming state
9. VimModeContext - Vim mode
10. SessionContext - Session stats
11. ShellFocusContext - Shell focus
12. OverflowContext - Text overflow

---

## Common Tasks

### To add a new dialog:
1. Create component in `/src/ui/components/`
2. Add state management in AppContainer.tsx
3. Wire into DialogManager.tsx
4. Reference TUI_FILE_INDEX.md for dialog examples

### To add a new slash command:
1. Create file in `/src/ui/commands/`
2. Export command handler
3. Register in command processor
4. Reference TUI_IMPLEMENTATION_ANALYSIS.md → "Command Processing" section

### To add a new keyboard shortcut:
1. Define in `/src/ui/keyMatchers.ts`
2. Add handler in AppContainer.tsx keyboard handler
3. Reference TUI_ARCHITECTURE_QUICK_REFERENCE.md → "Keyboard Shortcut Resolution"

### To understand a message type:
1. Check `/src/ui/types.ts` for definition
2. Find component in `/src/ui/components/messages/`
3. Look at HistoryItemDisplay.tsx for routing logic
4. Reference TUI_IMPLEMENTATION_ANALYSIS.md → "Message Display"

---

## Performance Considerations

**Key Performance Numbers**:
- Slow render threshold: 200ms
- Sequence parse timeout: 50ms
- Max message lines: 65,536
- Max sequence length: 256 chars

**Optimization techniques used**:
- Static component for history (no re-renders)
- useMemo throughout for expensive computations
- Flicker detection (warns of excessive re-renders)
- Memory monitoring during session
- Constraint mode for limiting visible content

See TUI_IMPLEMENTATION_ANALYSIS.md → "Performance Optimizations" for details.

---

## Accessibility

**Features**:
- Screen reader support (separate layout)
- Full keyboard navigation
- ARIA labels for context
- Multiple high-contrast themes
- Optional animation disabling

Reference: TUI_IMPLEMENTATION_ANALYSIS.md → "Accessibility Features"

---

## Related Files in Project

If you also need to understand:
- **Core API**: `/packages/core/` (referenced by TUI)
- **Configuration**: `/src/config/` (settings loading)
- **Commands**: `/src/ui/commands/` (slash command definitions)
- **Tests**: Any `*.test.ts` or `*.test.tsx` file (testing patterns)

---

## How to Use These Documents

### First time exploring:
1. Start with TUI_ARCHITECTURE_QUICK_REFERENCE.md for visual overview
2. Read TUI_IMPLEMENTATION_ANALYSIS.md for detailed understanding
3. Use TUI_FILE_INDEX.md to find specific files

### Need quick reference:
1. TUI_ARCHITECTURE_QUICK_REFERENCE.md for diagrams
2. TUI_FILE_INDEX.md for file locations
3. TUI_IMPLEMENTATION_ANALYSIS.md for detailed info

### Making changes:
1. Use TUI_FILE_INDEX.md to find files to modify
2. Reference TUI_ARCHITECTURE_QUICK_REFERENCE.md for component relationships
3. Check TUI_IMPLEMENTATION_ANALYSIS.md for context/impact

---

## Document Version Info

- Created: November 7, 2025
- Codebase Version: CodinGLM with gemini-cli fork (0.13.0-nightly)
- UI Framework: React 19.2.0 + Ink terminal renderer
- Language: TypeScript 5.3.3
- Coverage: 364 UI files, 63,000+ lines

---

## Additional Resources

Within the codebase:
- Each component file has JSDoc comments
- Test files show usage examples
- Theme files demonstrate color system
- Hook files show state patterns

External:
- Ink documentation: React rendering for terminals
- React Context API: State management pattern
- Node.js readline: Keyboard input handling

