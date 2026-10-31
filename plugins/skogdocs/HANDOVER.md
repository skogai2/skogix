# Handover: code-docs-lookup

## Goal
Claude answers Claude Code questions from the official docs, not from memory, and cites only pages it read.

## Steps that matter

1. **Docs cache.** `plugins/code-docs-lookup/scripts/sync-docs.sh` downloads the docs bundle and splits it into one file per page plus `index.txt`. The plugin passes `-c ${CLAUDE_PLUGIN_DATA}/docs`. *Verified:* `tests/offline.sh`.
2. **Lookup.** `search-docs.sh` finds pages with all the given terms. `show-doc.sh` prints a page, or its headings with `-H`, and ends with a `source:` URL. *Verified:* `tests/offline.sh`.
3. **Env reference.** `tools/build-env-reference.py` builds `references/env-vars.md` from the docs table. Upstream edits the table often, so regenerate when stage 03 fails. The committed file must match the generator's output. *Verified:* `tests/offline.sh`.
4. **Plugin and marketplace.** `.claude-plugin/marketplace.json` lists `plugins/code-docs-lookup`. The manifest validates, and the plugin installs and shows as enabled in a fresh config dir. *Verified:* `tests/offline.sh`.
5. **Isolated runs.** `tests/run-case.sh` gives each run its own `CLAUDE_CONFIG_DIR` (also set in the run's `settings.json` `env`), an empty working dir under `/tmp`, only `Bash` and `Skill` as built-in tools, no MCP, bundled skills hidden with `skillOverrides`, and the plugin scripts and both skills (`Skill(code-docs-lookup:… *)`) pre-approved. *Verified:* `tests/environment.sh`, which reads the init event and the transcript.
6. **Judge a run from events, not prose.** `tests/check-run.py` checks the tool calls: docs scripts were called, no web tools, every cited page was printed by a script, and nothing from the real `~/.claude` appears. *Verified:* the plain prompt and `/code-docs-lookup:ask` both pass `tests/agent.sh` (2026-10-29, about $0.07 and $0.15).

## Open problems

- **The env reference can't be reached in `-p` runs.** `cat` (and `grep`) on `references/env-vars.md` is blocked: Claude Code only allows reads inside the session's working dirs, whatever the allow rule says. Every run has one denial for it, then falls back to the scripts. Possible fix: serve references through a script, like `show-doc.sh` does for pages.
- **`--system-prompt` is not verified.** The run passes it, but no event records the system prompt.

## Gotchas found while building this

- `CLAUDE.md` and other `.claude` folders above the working dir load even with `CLAUDE_CONFIG_DIR` set. Keep runs out of `$HOME`.
- `--bare` skips installed plugins, so it cannot be used here.
- `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` are substituted in skill and command text and in Bash rules in `allowed-tools`. They are not exported to the Bash tool, and a `Read(...)` rule with them is not substituted.
- A pipe into `head` can make a script exit 141 (SIGPIPE) under `pipefail`. Capture output before taking the first line.
- Plugin install in a directory marketplace loads the plugin in place from the repo.
- In `-p`, anything that would prompt is auto-denied, including the model's own `Skill` call. The error text is just the prompt (`Execute skill: …`); look in the result event's `permission_denials`. Users running the skill headless need `--allowedTools "Skill(code-docs-lookup:claude-code-docs *)"`.
- The docs bundle lists some pages twice (`plugins/create`, `plugins/install`, `plugins/mods/overview`). `sync-docs.sh` keeps the first copy.
- A login also brings the account's claude.ai connectors. `--disallowedTools "mcp__*"` hides their tools but the servers still connect; the run's settings turn them off with `ENABLE_CLAUDEAI_MCP_SERVERS=false` and `disableClaudeAiConnectors`.
- New Claude Code releases add bundled skills and `cc-plugin-*` built-ins. `tests/environment.sh` catches new skills; add them to `BUNDLED_SKILLS` in `run-case.sh`.
- The tests call `claude` by name. In the `/skogai` Bash tool `PATH` is only `/usr/bin:/usr/local/bin`, so prepend `~/.local/bin` first.
- The model will cite a link it saw inside a page's text. The skill says to cite only pages a script printed.

## Run it

```sh
tests/offline.sh && tests/environment.sh     # cheap; should pass
tests/agent.sh                               # costs money (~$0.10); PROMPT=… to try another prompt
```

Run outputs go to `/tmp/code-docs-lookup-runs/`. Each one holds a copy of the login in its config dir, so delete old runs.
