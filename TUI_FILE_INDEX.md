# TUI Implementation - Key Files Index

## Entry Points & Main Components

### Application Entry
- **Main Entry**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/gemini.tsx`
- **App Component**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/App.tsx`
- **Container/State Hub**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/AppContainer.tsx` (1,489 lines)

### Layouts
- **Default Layout**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/layouts/DefaultAppLayout.tsx`
- **Screen Reader Layout**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/layouts/ScreenReaderAppLayout.tsx`
- **Main Content**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/components/MainContent.tsx`

## Core Hooks (80+ Total)

### Most Important Hooks
- **Streaming/API**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/hooks/useCodinGLMStream.ts` (1000+ lines)
  - Manages CodinGLM API streaming
  - Tool scheduling and execution
  - Approval modes
  - Error handling

- **Keyboard Input**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/hooks/useKeypress.ts`
  - Subscribes to keyboard events
  - Provides active/inactive control

- **History Management**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/hooks/useHistoryManager.ts`
  - Chat history persistence
  - Message logging
  - History clearing

- **Input Buffer**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/components/shared/text-buffer.ts`
  - Multi-line text editing
  - Cursor positioning
  - Selection management

- **Tool Scheduling**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/hooks/useReactToolScheduler.ts`
  - Tool execution orchestration
  - Tool state tracking

- **Message Queue**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/hooks/useMessageQueue.ts`
  - Message buffering during streaming
  - Queue management

- **Shell Commands**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/hooks/shellCommandProcessor.ts`
  - Shell command execution
  - Output capture

### Supporting Hooks
- Loading Indicator: `useLoadingIndicator.ts`
- Terminal Size: `useTerminalSize.ts`
- Settings: `useSettingsCommand.ts`
- Theme: `useThemeCommand.ts`
- Input History: `useInputHistory.ts`
- Shell History: `useShellHistory.ts`
- Reverse Search: `useReverseSearchCompletion.ts`
- Command Completion: `useCommandCompletion.ts`
- Memory Monitor: `useMemoryMonitor.ts`
- Vim Mode: `vim.ts`
- Mouse Events: `useMouse.ts`
- Focus Detection: `useFocus.ts`
- Flicker Detection: `useFlickerDetector.ts`

## Input Components

### Main Input Components
- **Composer**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/components/Composer.tsx`
  - Input area wrapper
  - Shows context, loading, indicators
  - Handles dialogs

- **InputPrompt**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/components/InputPrompt.tsx`
  - Text input field
  - Command suggestions
  - Completion handling

- **Suggestions Display**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/components/SuggestionsDisplay.tsx`
  - Slash command suggestions
  - File path completions
  - @ mention handling

### Other Input Components
- **Shell Input**: `ShellInputPrompt.tsx`
- **Confirmation Dialog**: `ShellConfirmationDialog.tsx`
- **Loop Detection**: `LoopDetectionConfirmation.tsx`

## Message Display Components

### Message Type Components (in `/components/messages/`)
- **User Message**: `UserMessage.tsx`
- **CodinGLM Message**: `CodinGLMMessage.tsx`
- **CodinGLM Content**: `CodinGLMMessageContent.tsx`
- **Tool Message**: `ToolMessage.tsx`
- **Tool Group**: `ToolGroupMessage.tsx`
- **Tool Confirmation**: `ToolConfirmationMessage.tsx`
- **Compression**: `CompressionMessage.tsx`
- **Error Message**: `ErrorMessage.tsx`
- **Info/Warning**: `InfoMessage.tsx`, `WarningMessage.tsx`
- **Todos**: `Todo.tsx`
- **Diff Renderer**: `DiffRenderer.tsx`

### Display Components
- **History Item Display**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/components/HistoryItemDisplay.tsx`
  - Routes messages to correct component
  - Handles all message types

- **Markdown Display**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/MarkdownDisplay.tsx`
  - Renders markdown as terminal UI
  - Code highlighting
  - Tables/lists

## Context API Providers

### All Contexts (in `/contexts/`)
1. **AppContext.tsx** - Version, startup warnings
2. **UIStateContext.tsx** - Main UI state (1300+ lines)
3. **UIActionsContext.tsx** - UI action callbacks
4. **ConfigContext.tsx** - Configuration object
5. **SettingsContext.tsx** - User settings
6. **KeypressContext.tsx** - Keyboard event distribution (1000+ lines)
7. **MouseContext.tsx** - Mouse event handling
8. **StreamingContext.tsx** - Streaming state
9. **VimModeContext.tsx** - Vim mode toggle
10. **SessionContext.tsx** - Session statistics
11. **ShellFocusContext.tsx** - Shell input focus
12. **OverflowContext.tsx** - Text overflow state

## Dialog Components (in `/components/`)
- **Auth Dialog**: `auth/AuthDialog.tsx`, `auth/ApiAuthDialog.tsx`
- **Theme Dialog**: `ThemeDialog.tsx`
- **Settings Dialog**: `SettingsDialog.tsx`
- **Model Dialog**: `ModelDialog.tsx`
- **Editor Dialog**: `EditorSettingsDialog.tsx`
- **Folder Trust**: `FolderTrustDialog.tsx`
- **IDE Trust**: `IdeTrustChangeDialog.tsx`
- **Permissions**: `PermissionsModifyTrustDialog.tsx`
- **Pro Quota**: `ProQuotaDialog.tsx`
- **Dialog Manager**: `DialogManager.tsx`

## Commands (in `/commands/`)
All slash command implementations:
- `/about`, `/auth`, `/bug`, `/chat`, `/clear`
- `/compress`, `/copy`, `/corgi`, `/directory`, `/docs`
- `/editor`, `/extensions`, `/help`, `/ide`, `/init`
- `/memory`, `/model`, `/mcp`, `/permissions`, `/policies`
- `/privacy`, `/profile`, `/quit`, `/restore`, `/settings`
- `/stats`, `/terminal-setup`, `/theme`, `/tools`, `/vim`

Each command file exports a command handler and configuration.

## Keyboard Architecture

### Keyboard Input Processing
- **KeypressContext**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/contexts/KeypressContext.tsx`
  - Raw input handling
  - Sequence parsing (Kitty, legacy, mouse)
  - Event distribution

- **useKeypress Hook**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/hooks/useKeypress.ts`
  - Subscribe/unsubscribe interface
  - Active/inactive control

- **Key Matchers**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/keyMatchers.ts`
  - Keyboard shortcut definitions
  - Command mapping

### Input Parsing
- **Vim Buffer**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/components/shared/vim-buffer-actions.ts`
- **Text Utilities**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/textUtils.ts`
- **Input Utils**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/input.ts`

## Theme System (in `/themes/`)
- **Theme Type**: `theme.ts`
- **Theme Manager**: `theme-manager.ts`
- **Semantic Colors**: `semantic-colors.ts`
- **Color Utilities**: `color-utils.ts`

### Theme Files
- `ansi.ts`, `ansi-light.ts`
- `atom-one-dark.ts`
- `ayu.ts`, `ayu-light.ts`
- `default.ts`, `default-light.ts`
- `dracula.ts`
- `github-dark.ts`, `github-light.ts`
- `googlecode.ts`
- `no-color.ts`
- `shades-of-purple.ts`
- `xcode.ts`

## Type Definitions

### Main Types
- **UI Types**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/types.ts`
  - Message types
  - Streaming states
  - Tool call types
  - History item types

- **Command Types**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/commands/types.ts`

## Rendering & Display Utils

### Markdown & Code Display
- **MarkdownDisplay**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/MarkdownDisplay.tsx`
- **CodeColorizer**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/CodeColorizer.tsx`
- **InlineMarkdownRenderer**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/InlineMarkdownRenderer.tsx`
- **TableRenderer**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/TableRenderer.tsx`

### Text & Formatting
- **Text Output**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/textOutput.ts`
- **Text Utilities**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/textUtils.ts`
- **Display Utils**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/displayUtils.ts`
- **Highlight**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/highlight.ts`

## Advanced Components

### Layout & Sizing
- **MaxSizedBox**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/components/shared/MaxSizedBox.tsx`
- **OverflowProvider**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/contexts/OverflowContext.tsx`
- **UI Sizing**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/ui-sizing.ts`

### Indicators & Displays
- **Loading Indicator**: `components/LoadingIndicator.tsx`
- **Auto Accept Indicator**: `components/AutoAcceptIndicator.tsx`
- **Shell Mode Indicator**: `components/ShellModeIndicator.tsx`
- **Raw Markdown Indicator**: `components/RawMarkdownIndicator.tsx`
- **Notifications**: `components/Notifications.tsx`

### Views (in `/components/views/`)
- **ChatList**: `ChatList.tsx`
- **ToolsList**: `ToolsList.tsx`
- **ExtensionsList**: `ExtensionsList.tsx`
- **McpStatus**: `McpStatus.tsx`

## Utilities & Helpers

### Core Utilities
- **Clipboard Utils**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/clipboardUtils.ts`
- **Command Utils**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/commandUtils.ts`
- **Console Patcher**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/ConsolePatcher.ts`
- **Markdown Utilities**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/markdownUtilities.ts`
- **Mouse Utilities**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/mouse.ts`
- **Terminal Setup**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/terminalSetup.ts`
- **Kitty Protocol Detector**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/kittyProtocolDetector.ts`

### Formatters
- **Formatters**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/formatters.ts`
- **Stats Computation**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/utils/computeStats.ts`

## Configuration & Settings

### Auth Handling
- **useAuth Hook**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/auth/useAuth.ts`
- **Auth Dialog**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/auth/AuthDialog.tsx`
- **API Auth Dialog**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/auth/ApiAuthDialog.tsx`
- **Auth In Progress**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/auth/AuthInProgress.tsx`

### Editor Settings
- **Editor Settings Manager**: `/home/user/CodinGLM/gemini-cli/packages/cli/src/ui/editors/editorSettingsManager.ts`

## Test Files
Test files mirror component/hook structure with `.test.ts` or `.test.tsx` suffix.

Key test files:
- `AppContainer.test.tsx` (51,194 bytes - comprehensive)
- `useCodinGLMStream.test.tsx`
- `useKeypress.test.tsx`
- `InputPrompt.test.tsx`
- Component-specific tests throughout

## Statistics

- **Total UI Files**: 364
- **Total UI Code Lines**: 63,000+
- **Main Components**: 100+
- **Custom Hooks**: 80+
- **Context Providers**: 12
- **Dialog Components**: 10+
- **Message Type Components**: 15+
- **Theme Files**: 12
- **Slash Commands**: 30+
- **Test Files**: 50+

## File Organization Pattern

The TUI follows a consistent organizational pattern:
```
/src/ui/
├── [Component].tsx          # Component file
├── [Component].test.tsx     # Component tests
├── subdirectory/
│   ├── [Component].tsx
│   └── [Component].test.tsx
└── index.ts (when needed)  # Barrel export
```

## Dependency Map

Core dependencies for TUI:
- `react` (19.2.0) - Component framework
- `ink` (@jrichman/ink@6.4.0) - Terminal renderer
- `chalk` - Terminal colors
- `string-width` - Width calculations
- `highlight.js`, `lowlight` - Code highlighting
- `readline` (Node.js) - Raw keyboard input
- `@google/gemini-cli-core` - API and config

## Entry Point Flow

```
gemini.tsx (startInteractiveUI)
  ↓
render(AppWrapper, { exitOnCtrlC: false, ... })
  ↓
KeypressProvider
  ↓
SettingsContext.Provider
  ↓
MouseProvider
  ↓
SessionStatsProvider
  ↓
VimModeProvider
  ↓
AppContainer (state mgmt)
  ↓
App (layout selection)
  ↓
DefaultAppLayout/ScreenReaderAppLayout
```

