---
name: agy-docs
description: >-
  Answer questions about Google Antigravity (the agy CLI, Antigravity App / 2.0,
  Antigravity IDE, IDE extensions, the Python SDK, settings.json, flags, slash
  commands, keybindings, skills, rules, plugins, MCP servers, hooks, sidecars,
  subagents, permissions, and terminal sandbox) by searching the official
  Antigravity documentation, not from memory. Use when the user asks how an
  Antigravity feature works, what a setting, flag, or slash command does, asks
  to look something up in the docs, or wants research across the docs.
---

# Antigravity docs (`agy-docs`)

Answer from the official Google Antigravity documentation. The docs change faster
than memory, so search them before answering questions about Antigravity behaviour,
CLI flags, `settings.json` keys, slash commands, hooks, plugins, or syntax.

The docs are cached locally as one Markdown file per page under
`${AGY_DOCS_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/agy-docs}`, with an `index.txt`.
Resolve paths below relative to this `SKILL.md` file's parent plugin root
(`<plugin-root>` is two levels above this file, e.g.
`/home/skogix/.gemini/config/plugins/agy-docs-lookup` when installed globally or
`/skogai/plugins/skogdocs/plugins/agy-docs-lookup` in the workspace):

- `[sync-docs.sh](../../scripts/sync-docs.sh)` (`<plugin-root>/scripts/sync-docs.sh`)
- `[search-docs.sh](../../scripts/search-docs.sh)` (`<plugin-root>/scripts/search-docs.sh`)
- `[show-doc.sh](../../scripts/show-doc.sh)` (`<plugin-root>/scripts/show-doc.sh`)

Run one script per command call with its full path written out (no command
substitutions, `&&`, `;`, or pipes) so it stays prefix-matchable and runs cleanly
inside the terminal sandbox. All three scripts default to `~/.cache/agy-docs`
automatically; pass `-c <cache_dir>` only if a custom cache path is needed.

## References

- [cli-reference.md](references/cli-reference.md) (`<plugin-root>/skills/agy-docs/references/cli-reference.md`):
  every `~/.gemini/antigravity-cli/settings.json` configuration key, every `agy`
  command-line startup flag, and every core TUI slash command from `cli/reference`.
  For questions about a `settings.json` key, CLI flag, or slash command, read this
  file first with `read_file` (or `show-doc.sh cli/reference`). Check the rest of
  the docs with the scripts below if you need more detail or the table links to a
  dedicated page.

## Workflow

1. **Make sure the cache exists.** Run `<plugin-root>/scripts/sync-docs.sh`. It is
   a fast offline no-op when `~/.cache/agy-docs/index.txt` is already present. Use
   `--force` to refresh from `https://antigravity.google/sitemap.xml` (requires
   network access outside the sandbox).
2. **Search.** Run `<plugin-root>/scripts/search-docs.sh <term> [more terms]`.
   - Several terms must all appear in a page (AND). Use one or two specific terms,
     e.g. `"hooks" "PreToolUse"`, rather than a whole sentence.
   - Use `-r` for regex, e.g. `-r "agentMode|toolPermission"`.
   - Use `-n <count>` to change how many pages are listed.
   - Try synonyms when nothing matches: `"skill"` / `"SKILL.md"`,
     `"subagent"` / `"agent"`, `"MCP"` / `"mcp_config.json"`,
     `"sandbox"` / `"enableTerminalSandbox"`, `"automation"` / `"sidecar"`.
3. **Read the pages that matter.** The search output gives a `slug:` for each page
   (e.g. `cli/reference`, `build-plugins`, `hooks`, `settings`, `sdk/overview`).
   For long pages, run `<plugin-root>/scripts/show-doc.sh -H <slug>` to see the
   headings, then `<plugin-root>/scripts/show-doc.sh <slug>` for the whole page.
   Read whole sections, not just the matched line, so you don't miss a caveat.
4. **Answer.** Give the answer directly, then cite the source URL(s) from the
   `source:` lines (`https://antigravity.google/docs/<slug>`). Cite only pages
   whose `source:` line a script printed for that page (a search hit, `show-doc.sh`,
   or `cli-reference.md`). A link inside a page's text is not a page you read:
   open it with `show-doc.sh` first, or leave it out. Quote exact setting names,
   flags, JSON keys, or commands from the docs. If the docs say something different
   from what you remember, say so and go with the docs.
5. **Say what the docs don't cover.** If the search finds nothing relevant, say so.
   Only then fall back to general knowledge, and label it as not from the docs.

## Research questions

For "compare X and Y", "what are all the ways to…" or "how do these pieces fit
together": search each concept separately, read the main page for each, and
synthesise across them. List the pages you used.

## Notes

- Don't paste whole pages into the answer. Summarise and link.
- Code examples in the docs are the authoritative syntax. Copy them rather than
  rewriting from memory.
- Official docs live under `https://antigravity.google/docs/`.
