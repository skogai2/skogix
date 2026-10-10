---
name: dynamic-output-blocks
type: reference
permalink: skogai-routing/dynamic-output-blocks
---

<overview>
how `!`command`` dynamic-injection blocks actually work in a SKILL.md, why they silently fail, and how to tell real subagent tool output from fabricated output. learned the hard way debugging this skill's own `<output>` block.
</overview>

<what_it_does>
`!`<command>`` is harness-level preprocessing. it runs the shell command *before* Claude ever sees the skill content, and the command's output replaces the placeholder as plain text. this is not something Claude executes — Claude only ever sees the final, already-rendered result.

substitution runs once over the original file. output is inserted as plain text and is not re-scanned for further `!`command`` placeholders — a command cannot emit a placeholder for a later pass to expand.
</what_it_does>

<allowed_tools_gate>
every `!`command`` in a skill body is gated by the frontmatter `allowed-tools` field. if no pattern in `allowed-tools` matches the resolved command, the invocation requires interactive approval — every single time, regardless of which exact form the command takes (absolute path, relative path, wrapped in `sh`, wrapped in `uv run`, etc).

this was the actual root cause of this skill's `<output>` block permanently failing with "Shell command permission check failed" — the frontmatter had no `allowed-tools` line at all. the varying command forms seen across attempts were a red herring (see [[plugin_cache_gotcha]] below); the real bug was the missing gate.

fix: declare a `Bash(...)` pattern per script actually invoked in the body, e.g.:
```yaml
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/list_routers.py*), Bash(${CLAUDE_SKILL_DIR}/scripts/list_xml_tags.py*)
```
</allowed_tools_gate>

<verified_fix>
confirmed working live in a later session, not just in source: invoking the skill
directly resolved both `<output>` lines and the self-check with real data (`list_routers.py`
→ `CLAUDE.md`/`SKOGAI.md`, `list_xml_tags.py` → both tagged `routes`, self-check → `PASS
SKOGAI.md.example`) and no permission prompt fired. the "Base directory for this skill"
line reported the installed cache path with hash `ada85c76ed62`, which matches the repo's
HEAD merge commit (`ada85c7`) at the time — proof the deployed plugin, not just the dev
checkout, carries the fix.
</verified_fix>

<use_claude_skill_dir>
always reference bundled scripts with `${CLAUDE_SKILL_DIR}`, never a relative path (`./scripts/...`) and never a hardcoded absolute path. `${CLAUDE_SKILL_DIR}` is documented specifically to resolve correctly "regardless of the current working directory" — a relative path only works if cwd happens to equal the skill's own directory, which is not guaranteed and was directly disproven in this session (cwd was the repo root, not the skill dir, when the bug was hit).

use it in both the skill body and the matching `allowed-tools` pattern, so the two stay in sync.
</use_claude_skill_dir>

<plugin_cache_gotcha>
plugins install into per-marketplace hashed cache directories under `~/.claude/plugins/cache/<marketplace>/<plugin>/<hash>/...`. multiple copies of the same skill — stale marketplace cache, freshly reinstalled cache, local dev-repo checkout — can all exist on disk simultaneously, and which one actually runs for a given invocation depends on install/reload state, not which file you last edited.

editing the dev-repo source does **not** change runtime behavior until the plugin is reinstalled and reloaded (`/plugin` + `/reload-plugins`). the fastest way to tell which copy actually ran is the "Base directory for this skill: ..." line every skill invocation reports — check it before assuming a fix took effect or diagnosing a "bug" that's actually just a stale cache.

the cache *root* prefix itself can differ across harness deployments (e.g. plain
`~/.claude/plugins/cache/...` vs a profile-scoped path like
`~/.local/share/cps/profiles/<profile>/claude/plugins/cache/...`) even for the same
machine and the same plugin. don't assume a fixed root — the reliable identity check
is the trailing `<plugin-name>/<hash>/...` segment, and matching that hash against
`git log --oneline` (or `git rev-parse --short HEAD`) tells you whether the running
copy is current, regardless of which root it's mounted under.
</plugin_cache_gotcha>

<subagent_skill_preload>
a subagent whose frontmatter lists a skill under `skills:` auto-loads that skill on every invocation — including running its `<output>` block — before the agent does anything else. this means a subsequent ask like "run script X" can come back with `tool_uses: 0` and still be completely truthful: the agent already had real, freshly-executed output sitting in its loaded context from skill-preload, and needed zero additional tool calls to answer.

`tool_uses: 0` is **not** by itself evidence of fabrication. it was misdiagnosed as hallucination once in this session's debugging before being corrected. the actual test for fabrication is whether the returned data matches the real target (e.g. does the file list match the path/cwd actually in scope) — not the raw tool-call count.

follow-up test in a later session: dispatching `route-guide` (which lists `skogai-routing`
under its `skills:` frontmatter) with a question about where a specific rule lives did
**not** come back with `tool_uses: 0` — it used 3 tool calls and answered with exact file
paths, line numbers, and quoted JSON/Python that were verified afterward to match the
real files exactly. this doesn't contradict the preload claim (a bare `tool_uses: 0`
answer is still possible and not automatically fabricated), but it's a reminder that the
mechanism doesn't stop an agent from also doing its own direct verification when the
question calls for specifics the preloaded `<output>` block doesn't cover — the preload
is a floor, not a ceiling, on what a subagent will check.
</subagent_skill_preload>

<at_link_not_always_needed>
`@`-linking a path vs. passing it as a plain string made no observed difference when the ask was "run this script against this path" — both produced identical, correctly-scoped output, with a real Bash call either way. a script invocation takes the path as an argument; it doesn't need the target's contents pre-loaded into context the way a Read or Grep call would.

the `@` vs. plain-path rules in [[at-linking]] govern content auto-inclusion and are most load-bearing for Read/Grep-style access — they aren't a precondition for handing a path string to a Bash-executed script.
</at_link_not_always_needed>

<companion_reference>
for `@`-link mechanics (how `@` works, permissions, subagent rules, caching behavior), see [at-linking.md](./at-linking.md). for the philosophy of when to `@`-link vs. use a plain path in a router file, see [claude-md-routing-rules.md](./claude-md-routing-rules.md).
</companion_reference>
