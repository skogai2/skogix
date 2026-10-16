---
type: Repository
title: skogix
description: Skogix's personal narrative/scratch repo, plus a nested old-skills test repo of skills, rules and scripts.
tags: [repo, personal, home]
generated: { by: "claude-code/claude-sonnet-5", at: "2026-10-10T00:00:00Z" }
stale_after: 2026-11-10T00:00:00Z
sources:
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: survey
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0005-survey-skogix.md
    title: Survey workorder 0005
---

# Role

Skogix's (the human's) own personal/narrative scratch repo: notes on his
workflow and communication style, plus `old-skills/`, a large old test
repo of skills, rules and scripts.[^decision-0003] Per decision 0003 this
is personal content, **not a workorder target**.

# Location

Local: `/home/skogix/skogix`. Remote: `https://github.com/skogai2/skogix.git`.
gita group: `skogix`.

# State

Seed/early-stage, actively being reorganized: 3 commits, most recent
today.[^survey] `old-skills/` is checked in as a submodule-mode gitlink
with no `.gitmodules` entry, so a fresh clone or `wt` worktree would see
it empty.

# Workorder notes

- Not a workorder target per decision 0003 — this is skogix's personal
  dump, not orchestrated content.
- If ever touched: `old-skills/` won't populate from a plain checkout
  (dangling gitlink); `docs/` and `story/` are near-duplicates, unclear
  which is canonical.

# Open issues

- `old-skills` gitlink has no `.gitmodules` entry — intentional or an
  unfinished `git submodule add`?
- `docs/SKOGIX.md:11`'s route target `@~/skogai/¡` looks corrupted.
- Commit `f17777a`'s message describes adding `.skogai/knowledge/decisions/`
  content that doesn't actually exist in the diff.

[^decision-0003]: Decision 0003 — repo roles
[^survey]: Survey workorder 0005
