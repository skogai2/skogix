---
type: Repository
title: config
description: Machine-configuration docs and runtime state for skogix's workstation, deployed directly at ~/.config/skogai.
tags: [repo, config, home]
generated: { by: "claude-code/claude-sonnet-5", at: "2026-10-10T00:00:00Z" }
stale_after: 2026-11-10T00:00:00Z
sources:
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: survey
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0003-survey-config.md
    title: Survey workorder 0003
---

# Role

Hand-maintained machine-configuration documentation (`atuin.md`,
`mappings.md`, `window-manager.md`, `containers.md`) plus a small
coordination/logging layer (`.skogai/state`, `plugins/hook-tap`). Tracked
by skogai per decision 0003.[^decision-0003]

# Location

Local: `/home/skogix/.config/skogai` — this *is* the live config
directory, not deployed via symlink from elsewhere. Remote:
`https://github.com/skogai2/config.git`. gita group: `home`.

# State

Active, work-in-progress; two `[@TODO:...]` placeholders remain in
`mappings.md`. Local `master` has diverged from `origin/master` by one
commit each way.[^survey] `.skogai/logs/`'s hook-tap noise is resolved —
it's now in the global gitignore per decision 0003.

# Workorder notes

- A `wt` worktree is a separate checkout elsewhere on disk; it is safe to
  edit and won't touch the live `~/.config/skogai` until merged.
- `.claude/`, `plugins/*/log.jsonl`, `.skogai/state/` are gitignored
  runtime state — not reproduced in a fresh worktree, not deliverables.
- No build/test/lint exists; don't invent one.

# Open issues

- `master`/`origin/master` divergence (1 commit each way) needs a
  merge/rebase decision before more work lands here.
- `SKOGAI.md` routes to `@SKOGIX.md`, which doesn't exist; workorder 0018
  (open) is dispatched to fix every dead router route.
- `state/`, `plugins/hook-tap/`, and the coordination DB are undocumented
  in `SKOGAI.md`/`AGENTS.md`.

[^decision-0003]: Decision 0003 — repo roles
[^survey]: Survey workorder 0003
