# TUI Architecture - Quick Reference Guide

## Data Flow Architecture

```
User Input (Keyboard/Mouse)
    ↓
KeypressContext (raw mode stdin)
    ↓ (sequence parsing & buffering)
    ↓
Key Handler Broadcast
    ↓
[Subscribed useKeypress handlers]
    ├─→ InputPrompt (text editing)
    ├─→ useGeminiStream (streaming control)
    └─→ AppContainer (global shortcuts)
```

## State Management Architecture

```
AppContainer (Central Hub)
    ↓
    ├─→ useHistory() 
    │   └─→ history[], addItem(), clearItems()
    │
    ├─→ useGeminiStream()
    │   ├─→ streamingState
    │   ├─→ pendingHistoryItems
    │   ├─→ thought (LLM reasoning)
    │   └─→ tool calls
    │
    ├─→ useTextBuffer()
    │   └─→ input text state
    │
    └─→ Dialog Hooks
        ├─→ useThemeCommand()
        ├─→ useAuthCommand()
        ├─→ useSettingsCommand()
        └─→ [10+ more dialog hooks]
    ↓
UIState Context (Read-only)
    ↓
Child Components
    └─→ Access state via useUIState()

UIActions Context (Write)
    ↓
Child Components
    └─→ Trigger actions via useUIActions()
```

## Rendering Pipeline

```
Ink.render() entry
    ↓
KeypressProvider (input distribution)
    ↓
SettingsContext (user preferences)
    ↓
MouseProvider (click/drag events)
    ↓
SessionStatsProvider (metrics)
    ↓
VimModeProvider (vim toggle)
    ↓
AppContainer (state management)
    │
    ├─→ useGeminiStream (API streaming)
    ├─→ useHistory (chat history)
    ├─→ useMemoryMonitor (memory tracking)
    ├─→ [10+ more custom hooks]
    │
    └─→ UIStateContext.Provider
        └─→ UIActionsContext.Provider
            ↓
            App (layout selection)
                ↓
                DefaultAppLayout
                    ├─→ MainContent
                    │   ├─→ Static (history)
                    │   └─→ OverflowProvider (pending)
                    │
                    └─→ Composer
                        ├─→ LoadingIndicator
                        ├─→ InputPrompt
                        └─→ Footer

    Render Time: measured for perf tracking
```

## Component Hierarchy

```
DefaultAppLayout
├── MainContent (horizontal scrollable area)
│   ├── Static { HistoryItemDisplay[] }
│   │   ├── AppHeader
│   │   └── [Rendered messages]
│   │       ├── UserMessage
│   │       ├── GeminiMessage
│   │       ├── ToolGroupMessage
│   │       ├── ErrorMessage
│   │       └── [15+ message types]
│   │
│   └── OverflowProvider { PendingItems }
│       └── [Live updating items]
│
└── (mainControlsRef) measurement container
    ├── Notifications
    ├── DialogManager
    │   ├── AuthDialog
    │   ├── ThemeDialog
    │   ├── SettingsDialog
    │   └── [8+ more dialogs]
    │
    └── Composer
        ├── LoadingIndicator
        ├── ContextSummaryDisplay
        ├── InputPrompt
        │   ├── TextInput (multiline)
        │   └── SuggestionsDisplay
        │       ├── Slash command suggestions
        │       ├── File path completions
        │       └── Previous message history
        │
        └── Footer
            └── Keyboard help
```

## Message Type Routing

```
HistoryItemDisplay (router component)
    ↓
MessageType check
    ├─→ 'user' → UserMessage
    ├─→ 'gemini' → GeminiMessage
    ├─→ 'gemini_content' → GeminiMessageContent
    ├─→ 'tool_group' → ToolGroupMessage
    ├─→ 'error' → ErrorMessage
    ├─→ 'warning' → WarningMessage
    ├─→ 'info' → InfoMessage
    ├─→ 'tool_group' → ToolGroupMessage
    ├─→ 'compression' → CompressionMessage
    ├─→ 'about' → AboutBox
    ├─→ 'help' → Help
    ├─→ 'stats' → StatsDisplay
    ├─→ 'quit' → SessionSummaryDisplay
    ├─→ 'extensions_list' → ExtensionsList
    ├─→ 'tools_list' → ToolsList
    ├─→ 'mcp_status' → McpStatus
    └─→ 'chat_list' → ChatList
```

## Input Handling Pipeline

```
Raw stdin (non-canonical mode)
    ↓
readline.emitKeypressEvents()
    ↓
KeypressProvider.handleKeypress()
    │
    ├─→ Sequence Detection
    │   ├─→ couldBeKittySequence()?
    │   ├─→ couldBeMouseSequence()?
    │   └─→ couldBePasteMarker()?
    │
    ├─→ Buffering (50ms timeout)
    │   └─→ Handles incomplete sequences
    │
    ├─→ Parsing
    │   ├─→ parseKittyPrefix() - Kitty protocol
    │   ├─→ parseMouseEvent() - Mouse events
    │   └─→ Legacy sequence parsing
    │
    └─→ Broadcast
        ↓
        Subscribers:
        ├─→ InputPrompt (text + navigation)
        ├─→ useGeminiStream (Escape cancel)
        ├─→ AppContainer (global shortcuts)
        └─→ [Custom handlers]
```

## Streaming State Machine

```
Idle
├─→ User submits message
│   └─→ Responding
│       ├─→ API streaming content
│       │   └─→ Still Responding
│       │
│       └─→ Tool request
│           ├─→ WaitingForConfirmation
│           │   ├─→ User approves
│           │   │   └─→ Responding (tool executes)
│           │   │
│           │   └─→ User denies
│           │       └─→ Idle
│           │
│           └─→ Auto-approve mode
│               └─→ Responding (executes immediately)
│
└─→ Escape pressed
    └─→ Cancellation (if Responding/Waiting)
        └─→ Idle
```

## Hook Integration Points

```
AppContainer
├─→ useHistory()
│   └─→ historyManager: {
│       addItem(), clearItems(), loadHistory()
│   }
│
├─→ useGeminiStream()
│   ├─→ streamingState
│   ├─→ submitQuery(partListUnion)
│   ├─→ cancelOngoingRequest()
│   ├─→ thought
│   └─→ pendingHistoryItems
│
├─→ useTerminalSize()
│   └─→ { columns, rows }
│
├─→ useTextBuffer()
│   └─→ buffer: { text, setText(), ... }
│
├─→ useMemoryMonitor()
│   └─→ Tracks memory during session
│
├─→ useKeypress()
│   └─→ Registers global key handlers
│
├─→ useThemeCommand()
│   └─→ Theme dialog management
│
├─→ useAuthCommand()
│   └─→ Auth state & dialogs
│
├─→ useSettingsCommand()
│   └─→ Settings management
│
└─→ [15+ more hooks]
    ├─→ useSlashCommandProcessor()
    ├─→ useMessageQueue()
    ├─→ useAutoAcceptIndicator()
    └─→ ...
```

## Terminal Dimensions Calculation

```
Terminal Size (from useTerminalSize)
    ↓ (columns, rows)
    ↓
calculateMainAreaWidth()
    ├─→ SHELL_WIDTH_FRACTION = 0.89
    └─→ terminalWidth * 0.89
    ↓
calculatePromptWidths(mainAreaWidth)
    ├─→ FRAME_PADDING_AND_BORDER = 4
    ├─→ PROMPT_PREFIX_WIDTH = 2
    ├─→ frameOverhead = 6
    └─→ inputWidth = mainAreaWidth - 6
    ↓
availableTerminalHeight calculation
    ├─→ controlsHeight (measured via measureElement)
    ├─→ staticExtraHeight = 3
    └─→ availableTerminalHeight = 
        terminalHeight - controlsHeight - 5
    ↓
constrainHeight flag (user toggle)
    └─→ Limits pending items visible height
```

## Context Tree

```
App (Root)
├─→ KeypressContext
│   └─→ { subscribe(), unsubscribe() }
│
├─→ SettingsContext
│   └─→ LoadedSettings
│
├─→ MouseContext
│   └─→ Mouse event handling
│
├─→ SessionStatsProvider
│   └─→ Session metrics
│
├─→ VimModeProvider
│   └─→ { vimEnabled, toggleVimEnabled() }
│
├─→ AppContext
│   └─→ { version, startupWarnings }
│
├─→ UIStateContext
│   └─→ UIState (1300+ line object)
│
├─→ UIActionsContext
│   └─→ Action callbacks
│
├─→ ConfigContext
│   └─→ Config object
│
├─→ StreamingContext
│   └─→ Current StreamingState
│
├─→ ShellFocusContext
│   └─→ Shell input focus state
│
└─→ OverflowContext (per section)
    └─→ Text overflow state
```

## Command Processing Flow

```
User Input
    ↓
isSlashCommand(text) check
    ├─→ YES: useSlashCommandProcessor
    │   ├─→ Command parsing
    │   ├─→ Validation
    │   └─→ Handler execution
    │       ├─→ openThemeDialog()
    │       ├─→ openSettingsDialog()
    │       ├─→ handleSlashCommand('/quit')
    │       └─→ [30+ commands]
    │
    └─→ NO: Submit to Gemini
        ├─→ useGeminiStream
        ├─→ Streaming response
        └─→ Tool handling
```

## Keyboard Shortcut Resolution

```
Key received
    ↓
keyMatchers[Command](key) check
    ├─→ QUIT (Ctrl+C)
    │   └─→ Increment ctrl+C counter
    │
    ├─→ EXIT (Ctrl+D)
    │   └─→ Increment ctrl+D counter
    │
    ├─→ SHOW_ERROR_DETAILS (Ctrl+Shift+E)
    │   └─→ Toggle error console
    │
    ├─→ CLEAR_SCREEN (Ctrl+L)
    │   └─→ Clear history and screen
    │
    ├─→ TOGGLE_MARKDOWN (Ctrl+Shift+M)
    │   └─→ Toggle markdown rendering
    │
    ├─→ TOGGLE_COPY_MODE (Ctrl+M)
    │   └─→ Enable terminal copy mode
    │
    └─→ [20+ more mappings]
        └─→ Various navigation & toggles
```

## Theme System Architecture

```
Theme Selection (settings)
    ↓
themeManager.getTheme(name)
    ├─→ theme.ts (theme type definition)
    ├─→ Load specific theme file
    │   ├─→ ansi.ts, dracula.ts, github-dark.ts, etc.
    │   └─→ export Theme object
    │
    └─→ Apply colors throughout
        ├─→ semantic-colors.ts (provides theme object)
        ├─→ All components: theme.text.primary, theme.status.error
        └─→ Dynamic theme switching via /theme command
```

## Performance Optimization Points

```
Rendering
├─→ Static component (history doesn't re-render)
├─→ useMemo (prevent recalculations)
├─→ Flicker detection (warn on >1 re-render per 16ms)
└─→ Slow render tracking (log renders >200ms)

Memory
├─→ useMemoryMonitor (watch heap growth)
├─→ Constraint mode (limit visible messages)
├─→ Message line limits (max 65,536 per message)
└─→ Cleanup on unmount

Terminal
├─→ Line wrapping disabled (Ink handles it)
├─→ Height measurement cached (update on resize)
├─→ PTY sizing synchronized
└─→ Alternate buffer optional
```

## Testing Strategy

```
Test Coverage
├─→ Unit Tests
│   ├─→ Hook tests (useGeminiStream, useKeypress, etc.)
│   ├─→ Utility tests (text handling, formatting)
│   └─→ Component tests (complex components)
│
├─→ Integration Tests
│   ├─→ AppContainer integration
│   ├─→ Command processing
│   └─→ Message flow
│
└─→ UI Testing
    └─→ ink-testing-library (snapshot + behavior tests)
```

## Key Statistics

```
Codebase Scale:
  - 364 UI files
  - 63,000+ lines of UI code
  - 100+ React components
  - 80+ custom hooks
  - 12 context providers
  - 30+ slash commands
  - 12 color themes
  - 50+ test files

State Management:
  - 40+ state variables in AppContainer
  - 1300+ line UIState object
  - 12 context providers
  - 80+ custom hooks

Performance:
  - Slow render threshold: 200ms
  - Sequence parse timeout: 50ms
  - Max message lines: 65,536
  - Max sequence length: 256 chars
```

## Quick Navigation Guide

Start here for:
- **Overall flow**: This file
- **File locations**: TUI_FILE_INDEX.md
- **Detailed analysis**: TUI_IMPLEMENTATION_ANALYSIS.md
- **Component code**: /src/ui/components/
- **Hooks**: /src/ui/hooks/
- **State management**: /src/ui/contexts/
- **Input handling**: KeypressContext.tsx
- **API streaming**: useGeminiStream.ts
- **Main state hub**: AppContainer.tsx

