---
type: Repository
title: marketplace
description: Claude Code plugin marketplace repo (hook-tap, open-knowledge-plugin submodule) plus a vendored copy of the Claude Code docs.
tags: [repo, plugins, src]
generated: { by: "claude-code/claude-sonnet-5", at: "2026-10-10T00:00:00Z" }
stale_after: 2026-11-10T00:00:00Z
sources:
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: survey
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0006-survey-marketplace.md
    title: Survey workorder 0006
---

# Role

A Claude Code plugin marketplace: `.claude-plugin/marketplace.json` plus
the plugin sources it catalogs (`hook-tap`, `open-knowledge-plugin` as a
submodule), and a vendored, offline copy of the official Claude Code
docs.[^survey] Per decision 0003 it replaces/supersedes
`skogai-docs`.[^decision-0003]

# Location

Local clone: `/home/skogix/.local/src/marketplace`. Remote:
`https://github.com/skogai2/marketplace.git`. gita group: `src`. Also
live-installed as `skogai-marketplace` in `~/.claude/plugins/` — a
separate, auto-updating clone, not this one.

# State

Active, in-progress; the plugin set has already been reworked at least
once (`open-knowledge-plugin` was removed, then re-added as a
submodule).[^survey] As of 2026-10-17 `plugins/` holds only
`skogai-core`; `code-docs-lookup` and `openknowledge/` are gone.

# Workorder notes

- Editing this clone (or a worktree of it) does not change what the live
  `skogai-marketplace` install loads — that resyncs from `origin/master`
  on GitHub, independently.
- Any plugin add/rename must also update `.claude-plugin/marketplace.json`
  or it won't be installable.
- A workorder touching `plugins/open-knowledge-plugin/` is really
  targeting [open-knowledge-plugin](open-knowledge-plugin.md); bump the
  submodule pointer rather than editing in place.

# Open issues

- Docs lookup (`code-docs-lookup`) is no longer in any plugin; the
  vendored `docs/` has no consumer. Bring it back or drop the docs?
- Two independent `open-knowledge-plugin` marketplace registrations exist
  on this machine; standardize on one?

[^decision-0003]: Decision 0003 — repo roles
[^survey]: Survey workorder 0006
