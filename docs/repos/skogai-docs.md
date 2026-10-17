---
type: Repository
title: skogai-docs
status: deprecated
description: A Claude Code docs-lookup plugin repo; superseded by marketplace, which now vendors the docs copy instead.
tags: [repo, deprecated]
generated: { by: "claude-code/claude-opus-5-5", at: "2026-10-17T00:00:00Z" }
stale_after: 2026-11-17T00:00:00Z
sources:
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: survey
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0009-survey-skogai-docs.md
    title: Survey workorder 0009
  - id: handover
    resource: https://github.com/skogai2/skogai-docs/blob/master/HANDOVER.md
    title: skogai-docs HANDOVER.md
---

# Role

Was a Claude Code plugin marketplace (`code-docs-tools`) with one plugin,
`code-docs-lookup`, letting Claude answer Claude Code questions from a
local, offline-searchable docs copy instead of from memory.[^survey]
**Superseded by [marketplace](marketplace.md)**, which now vendors its
own docs copy; `skogai-docs` is no longer tracked by gita.[^decision-0003]

# Location

Local clone: `/home/skogix/.local/src/skogai-docs`, at `8836fc0`, in
sync with origin. The second clone (`~/claude-docs`, later
`~/skogix/.projects/claude-docs`) was identical and has been removed.
Remote: `https://github.com/skogai2/skogai-docs.git`. No longer in a
gita group.

# State

Deprecated. At last survey it was active but mid-build, with a
known-broken plain-prompt invocation path (`HANDOVER.md`'s "Open
problems," cause not found).[^survey] That work is not being continued
here. `marketplace` vendors the docs under `docs/`, but no longer has a
`code-docs-lookup` plugin, so docs lookup is not live anywhere.

# Gotchas

Found while building the plugin; they hold for any Claude Code plugin
work.[^handover]

- `CLAUDE.md` and `.claude/` folders above the working dir load even
  with `CLAUDE_CONFIG_DIR` set. Isolated test runs must stay out of
  `$HOME`.
- `--bare` skips installed plugins.
- `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` are substituted
  in skill and command text and in `allowed-tools` Bash rules. They are
  not exported to the Bash tool, and `Read(...)` rules are not
  substituted.
- A pipe into `head` under `pipefail` can exit 141 (SIGPIPE).
- A directory marketplace loads the plugin in place from the repo.
- Unsolved: with a plain prompt the model's own Skill call returned
  `is_error: true` and the skill body never arrived; the named
  `/code-docs-lookup:claude-code-docs` form worked.

# Workorder notes

- Not a workorder target. Any future docs-lookup work belongs in
  [marketplace](marketplace.md).

# Open issues

None — superseded, no further decision needed here.

[^decision-0003]: Decision 0003 — repo roles
[^handover]: skogai-docs HANDOVER.md
[^survey]: Survey workorder 0009
