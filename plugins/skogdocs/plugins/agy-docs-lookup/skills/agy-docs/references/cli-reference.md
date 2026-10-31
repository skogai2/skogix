# Antigravity CLI reference (settings.json, flags, and slash commands)

Reference for every `settings.json` configuration key, CLI startup flag, and TUI slash command in the Antigravity CLI (`agy`) docs.

Source: https://antigravity.google/docs/cli/reference (Core slash commands, Command-line flags, and Configuration keys tables). Re-check the source page if a setting, flag, or command is missing or behaves differently.

## Index

- **settings.json keys** (33): `string` (13), `boolean` (12), `integer` (1), `string\[\]` (1), `object` (6)
- **Command-line flags** (17)
- **Core slash commands** (42): Utilities (13), Tools & Tasks (10), Reasoning (3), Configurations (7), Account (2), Core (1), Conversations (4), Planning (2)

## Configuration keys (`~/.gemini/antigravity-cli/settings.json`)

| Key | Type | Default | Description |
| :- | :- | :- | :- |
| `agentMode` | string | `""` (default mode) | Default startup [execution mode](https://antigravity.google/docs/cli/modes): `""` (standard `default` mode), `"accept-edits"` (auto-approve workspace file edits), `"auto"` (Preview; `v1.3.5+` on macOS and Linux, `v1.4.4+` on Windows; requires the terminal sandbox; auto-approves edits, runs commands in the terminal sandbox by default, and automatically checks any command that needs to run outside the sandbox so safe, reversible commands run without prompting while irreversible actions still prompt; not available for business or enterprise accounts), or `"plan"` (research and outline steps before writing code). Can be overridden per session with `--mode`. |
| `colorScheme` | string | `"terminal"` | Color theme: `"light"`, `"solarized light"`, `"colorblind-friendly light"`, `"dark"`, `"solarized dark"`, `"colorblind-friendly dark"`, `"tokyo night"`, or `"terminal"` (inherits native shell colors). |
| `altScreenMode` | string | `"default"` | Screen buffer usage: `"default"` (renders the conversation inline and opens full-screen views in the alternate screen), `"always"` (runs the whole TUI in the alternate screen), or `"never"` (never uses the alternate screen; available only in `settings.json`). |
| `toolPermission` | string | `"request-review"` | Global safety presets: `"request-review"` (prompts for write, bash, web, and MCP tools unless an allow rule covers them), `"proceed-in-sandbox"` (runs terminal commands without prompting when the sandbox is on and the command runs inside it; in `v1.4.4+`, behaves like `"request-review"` if the sandbox isn’t available), `"always-proceed"` (runs commands, web requests, and MCP tools without prompting unless an ask or deny rule matches), or `"strict"` (prompts before every tool action, including file reads, even if an allow rule matches). Deny rules apply in every mode. |
| `artifactReviewPolicy` | string | `"asks-for-review"` | Whether the agent waits for your review when it asks for feedback on an artifact, such as an implementation plan: `"asks-for-review"` (always waits), `"agent-decides"` (currently the same as `"asks-for-review"`), or `"always-proceed"` (never waits). Doesn’t affect file edits. |
| `notifications` | boolean | `false` | Rings the terminal bell and shows a desktop notification when the agent needs your approval or an answer, or finishes its turn. |
| `showTips` | boolean | `true` | Displays helpful usage tips while the agent is generating responses. |
| `showFeedbackSurvey` | boolean | `true` | Displays periodic quality feedback surveys upon active task completions. |
| `editor` | string | `"auto"` | External editor for opening artifacts and files and for composing prompts (`Ctrl+G`): `"auto"` (uses `$EDITOR`, then falls back to `vim`, or to `edit` and `notepad` on Windows), `"vim"`, `"emacs"`, or any other editor command. |
| `editorMode` | string | `"default"` | Prompt editing model: `"default"` (flat text editing) or `"vim"` (modal editing). Distinct from `editor`, which selects an external program. Refer to [Vim editor mode](https://antigravity.google/docs/cli/vim-editor-mode). |
| `vimInsertFirst` | boolean | `false` | Starts Vim editing in Insert mode and makes a bare `Enter` submit. Requires `editorMode` set to `"vim"`. |
| `allowNonWorkspaceAccess` | boolean | `false` | Lets the agent read and edit files outside your workspace folders, subject to `toolPermission`, `agentMode`, and your permission rules. |
| `enableTerminalSandbox` | boolean | `false` | Restricts all local execution commands launched by agents to OS containment rings (in `v1.4.4+`, no effect if the sandbox isn’t available on your machine). |
| `useG1Credits` | boolean | `false` | Uses your AI credits for model requests after your plan’s quota runs out. Not available for business accounts. |
| `verbosity` | string | `"medium"` | Visual verbosity level: `"high"` (renders every tool call, command, and thought in full), `"medium"` (groups related tool calls and thoughts into summaries while keeping commands and responses visible), or `"low"` (renders only responses and collapses tool activity into a token usage summary). |
| `runningLightSpeed` | string | `"medium"` | Visual running light progress animation speed: `"fast"`, `"medium"`, `"slow"`, or `"off"`. |
| `copyOnSelect` | boolean | `true` | In alt-screen mode, copies text to the clipboard when you release a mouse selection. When `false`, the artifact viewer uses your terminal’s own text selection. |
| `hideActiveItems` | boolean | `false` | Hides the list of active subagents and background tasks below the prompt box (**Show Active Tasks** in `/config`). |
| `pickerGrouping` | string | `"none"` | How the [`/resume`](https://antigravity.google/docs/cli/commands/resume) picker lists conversations: `"none"` (one list, most recent first) or `"grouped"` (grouped by workspace). |
| `queuedMessages` | string | `"queue"` | What happens to a message you send while the agent is working: `"queue"` (held until the current turn ends) or `"send-immediately"` (interrupts the agent and sends it right away). |
| `clearScrollbackOnResize` | boolean | `true` | In inline rendering, clears your terminal’s scrollback when the CLI redraws the conversation, such as after you resize the window. |
| `disableSlashCommands` | boolean | `false` | In [headless mode](https://antigravity.google/docs/cli/headless) (`-p`), sends prompts that start with `/` as typed instead of running slash commands or skills. Same as `--disable-slash-commands`. |
| `historySize` | integer | `2000` | Prompt history entries kept on disk, trimmed when the CLI exits: `-1` keeps every entry, and `0` clears the history. |
| `model` | string | `""` | The model you chose with `/model`, saved by its label. |
| `modelProvider` | string | `""` | `"gemini"` sends model requests directly to the Gemini API with the key in `GEMINI_API_KEY` ([Using a Gemini API key](https://antigravity.google/docs/install#using-a-gemini-api-key)). |
| `trustedWorkspaces` | string\[\] | `[]` | Folders you chose to trust when the CLI asked. The CLI adds entries for you. |
| `useTerminalCursor` | boolean | `false` | Uses your terminal’s own cursor shape instead of a block cursor. |
| `permissions` | object | — | Allow, ask, and deny rules for the agent’s tools. Refer to [`permissions`](https://antigravity.google/docs/settings?tab=cli#permissions). |
| `statusLine` | object | — | Custom status line script. Refer to [`statusLine` and `title`](https://antigravity.google/docs/settings?tab=cli#statusline-and-title). |
| `title` | object | — | Custom terminal title script. Refer to [`statusLine` and `title`](https://antigravity.google/docs/settings?tab=cli#statusline-and-title). |
| `sandboxProxy` | object | — | HTTP proxy for sandboxed terminal commands. Refer to [`sandboxProxy`](https://antigravity.google/docs/settings?tab=cli#sandboxproxy). |
| `customModelsConfig` | object | — | Extra models for the Gemini API key setup. Refer to [`customModelsConfig` and `gcp`](https://antigravity.google/docs/settings?tab=cli#custommodelsconfig-and-gcp). |
| `gcp` | object | — | Saved by the **Use a Google Cloud project** sign-in. Refer to [`customModelsConfig` and `gcp`](https://antigravity.google/docs/settings?tab=cli#custommodelsconfig-and-gcp). |

## Command-line flags (`agy`)

| Flag | Default | Description |
| :- | :- | :- |
| **`--mode`** | `""` | Set the agent [execution mode](https://antigravity.google/docs/cli/modes) for this session: `accept-edits`, `auto` (Preview; `v1.3.5+` on macOS and Linux, `v1.4.4+` on Windows; requires the terminal sandbox; not available for business or enterprise accounts), or `plan`. |
| **`--model`** | — | Select the model for the current CLI session (refer to `agy models`). |
| **`--effort`** | — | Set the [reasoning effort](https://antigravity.google/docs/cli/commands/effort) for the current CLI session (`low` through `max`, depending on the model). |
| **`--agent`** | — | Select the agent for the current CLI session (refer to `agy agents`). |
| **`--add-dir`** | `[]` | Add a directory to the workspace (repeatable). |
| **`--conversation`** | — | Resume a previous conversation by ID. |
| **`--output-format`** | `text` | Output format for print mode (`text`, `json`, `stream-json`). |
| **`--input-format`** | `text` | Input format for print mode (`text`, `stream-json`). |
| **`--json-schema`** | — | JSON schema string or path to a schema file to enforce structured output in print mode. |
| **`--print-timeout`** | `0s` | Optional time limit for print mode (`0` waits until the turn completes). |
| **`--disable-slash-commands`** | `false` | Disable slash command and skill expansion in print mode. |
| **`--sandbox`** | `false` | Run in a terminal sandbox with OS containment restrictions enabled (in `v1.4.4+`, no effect if the sandbox isn’t available on your machine). |
| **`--dangerously-skip-permissions`** | `false` | Auto-approve all tool permission requests without prompting. |
| **`--remote-control`** | `false` | Create a [Remote Control](https://antigravity.google/docs/remote-control?tab=cli) connection for the CLI session on startup. |
| **`--project`** | — | Project ID or project name for the current CLI session. |
| **`--new-project`** | `false` | Create a new project for this session. |
| **`--log-file`** | — | Override the CLI log file path. |

## Core slash commands

| Command | Category | Alias | Purpose |
| :- | :- | :- | :- |
| **`/add-dir <path>`** | Utilities | — | Add a directory path to the active workspace. |
| **[`/agents`](https://antigravity.google/docs/cli/commands/agents)** | Tools & Tasks | — | Open the [Agent Manager panel](https://antigravity.google/docs/cli/commands/agents) to switch custom agents and monitor background subagents. |
| **`/artifact`** | Tools & Tasks | — | Open the Artifact Review panel. |
| **[`/boost`](https://antigravity.google/docs/boost)** `<task>` | Reasoning | — | Run on-demand multi-agent deep reasoning loops. |
| **[`/browser`](https://antigravity.google/docs/commands/browser)** `<task>` | Tools & Tasks | — | Delegate web browsing, UI verification, and in-browser debugging to the [browser subagent](https://antigravity.google/docs/commands/browser). |
| **[`/btw`](https://antigravity.google/docs/cli/commands/btw) `<query>`** | Utilities | — | Ask a [side question in the background](https://antigravity.google/docs/cli/commands/btw) without interrupting the main conversation. |
| **[`/changelog`](https://antigravity.google/docs/cli/commands/changelog)** | Utilities | — | Open the [interactive release notes viewer](https://antigravity.google/docs/cli/commands/changelog) or print CLI changes in headless mode. |
| **`/clear`** | Utilities | `/new` | Clear the terminal and reset active conversation contexts. |
| **[`/codesearch`](https://antigravity.google/docs/cli/commands/codesearch) `<query>`** | Utilities | `/cs`, `/search` | Open the [interactive Code Search panel](https://antigravity.google/docs/cli/commands/codesearch) to search code across the workspace. |
| **`/config`** | Configurations | `/settings` | Open the interactive Settings Editor overlay. |
| **[`/context`](https://antigravity.google/docs/cli/commands/context)** | Utilities | — | Open the [context usage visualization panel](https://antigravity.google/docs/cli/commands/context). |
| **[`/credits`](https://antigravity.google/docs/cli/commands/credits)** | Account | — | View remaining G1 credits and purchase links. |
| **[`/diff`](https://antigravity.google/docs/cli/commands/diff)** | Utilities | — | Open the [interactive diff viewer](https://antigravity.google/docs/cli/commands/diff) to view changes, turns, and commits. |
| **[`/effort`](https://antigravity.google/docs/cli/commands/effort) `[level]`** | Configurations | — | Set or inspect the active model’s [reasoning effort level](https://antigravity.google/docs/cli/commands/effort) (`low` through `max`, depending on the model). |
| **`/exit`** | Core | `/quit` | Close the TUI session and restore your host shell. |
| **`/feedback`** | Utilities | — | Open the feedback submission panel. |
| **`/fork`** | Conversations | `/branch` | Clone the current conversation thread into a new parallel session. |
| **[`/goal`](https://antigravity.google/docs/commands/goal)** `<objective>` | Reasoning | — | Run autonomously until the [goal is verified complete](https://antigravity.google/docs/commands/goal), without intermediate pauses. |
| **[`/grill-me`](https://antigravity.google/docs/commands/grill-me)** `[task]` | Planning | — | Have the agent [interview you](https://antigravity.google/docs/commands/grill-me) one question at a time, with a recommended answer for each, before it starts work. |
| **`/help`** | Utilities | — | Open the help panel showing commands and shortcuts. |
| **`/hooks`** | Tools & Tasks | — | Browse active pre-flight/post-format script hooks. |
| **`/keybindings`** | Configurations | — | Open the interactive Keyboard Shortcut Editor. |
| **[`/learn`](https://antigravity.google/docs/commands/learn)** `[instruction]` | Tools & Tasks | — | Capture session corrections as persistent [rules or skills](https://antigravity.google/docs/commands/learn) through a reviewable proposal. |
| **`/logout`** | Account | — | Disconnect your profile and purge authentication tokens from the secure keyring. |
| **`/mcp`** | Tools & Tasks | — | Open the Model Context Protocol (MCP) server manager. |
| **`/model`** | Configurations | — | Choose your preferred reasoning model (persists across sessions). To run a single prompt on another model without changing your default, use `/model <model> <prompt>`. |
| **`/open <path>`** | Utilities | — | Force the path to open inside your default system editor. |
| **[`/permissions`](https://antigravity.google/docs/cli/commands/permissions)** | Configurations | — | Open the interactive tool permissions manager panel. |
| **[`/plan`](https://antigravity.google/docs/plan)** `[task]` | Planning | — | Explore the codebase, clarify requirements, and draft a reviewable [Implementation Plan](https://antigravity.google/docs/implementation-plan). |
| **[`/plugin`](https://antigravity.google/docs/plugins?tab=cli)** | Tools & Tasks | `/plugins` | Open the interactive [Plugins Manager](https://antigravity.google/docs/marketplace?tab=cli) or run inline `install`, `uninstall`, `enable`, `disable`, and `list` commands. |
| **`/rename <name>`** | Conversations | — | Rename the current session thread. |
| **[`/remote-control`](https://antigravity.google/docs/remote-control?tab=cli#interactive-mode) \[on/off\]** | Utilities | — | Toggle Remote Control for the active terminal session. |
| **[`/resume`](https://antigravity.google/docs/cli/commands/resume)** | Conversations | `/switch`, `/conversation` | Open the [conversation picker overlay](https://antigravity.google/docs/cli/commands/resume) to select and load previous threads. |
| **`/rewind`** | Conversations | `/undo` | Roll back your conversation history to a previous message. |
| **[`/schedule`](https://antigravity.google/docs/commands/schedule)** `<when> <task>` | Tools & Tasks | — | Set a [one-shot timer or recurring cron schedule](https://antigravity.google/docs/commands/schedule) that wakes the agent with an instruction. |
| **`/skills`** | Tools & Tasks | — | Browse loaded local and global Agent Skills. Run `/skills reload` to reload skills from disk. |
| **[`/statusline`](https://antigravity.google/docs/cli/commands/statusline)** | Configurations | — | Open the Status Bar customization overlay. |
| **`/tasks`** | Tools & Tasks | — | Open the Task Manager panel to monitor background shell execution logs. |
| **[`/teamwork`](https://antigravity.google/docs/teamwork)** `<task>` | Reasoning | — | Launch [collaborative multi-agent teams](https://antigravity.google/docs/teamwork) for long-horizon projects (paid plans). |
| **[`/title`](https://antigravity.google/docs/cli/commands/title) \[on/off\]** | Configurations | — | Toggle or set terminal window title updates. |
| **[`/usage`](https://antigravity.google/docs/cli/commands/usage)** | Utilities | `/quota` | Display model quota usage. |
| **[`/voice`](https://antigravity.google/docs/cli/commands/voice)** | Utilities | `/record` | Dictate a prompt using your microphone. |

## See also

- CLI settings and `/config` behavior: https://antigravity.google/docs/settings
- Terminal sandbox and permission rules: https://antigravity.google/docs/sandbox
- Plugins and `agy plugin` subcommands: https://antigravity.google/docs/plugins
- Headless mode (`-p` / `--print`): https://antigravity.google/docs/cli/headless
