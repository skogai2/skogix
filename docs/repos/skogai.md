---
type: Repository
title: skogai
description: The orchestrator repo — writes workorders, dispatches them via wt/herdr, lands them; this knowledge bundle lives here.
tags: [repo, orchestration, home]
generated: { by: "claude-code/claude-sonnet-5", at: "2026-10-10T00:00:00Z" }
stale_after: 2026-11-10T00:00:00Z
sources:
  - id: decision-0002
    resource: /decisions/0002-orchestration-model.md
    title: Decision 0002 — orchestration model
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: decision-0004
    resource: /decisions/0004-knowledge-lifecycle.md
    title: Decision 0004 — knowledge lifecycle
---

# Role

The main session orchestrates from here: it discusses design with skogix,
writes `.skogai/workorders/NNNN-slug.md`, dispatches them to herdr-hosted
worker agents in `wt` worktrees, and lands finished work.[^decision-0002]
It also tracks every other skogai2 repo's role and state via
`gita`.[^decision-0003] This bundle (`.skogai/knowledge/`) is itself part
of skogai's role: the synthesized layer over the raw workorder
archive.[^decision-0004]

# Location

Local: `/home/skogix/skogai`. Remote: `https://github.com/skogai2/skogai.git`.
gita group: `home`.

# State

Active, the most-maintained repo in the fleet. `bin/wo` implements
`new`/`dispatch`/`status`/`land`; `TOOLS.md` documents the tool stack
(herdr, wt, gita). Workers run with `--permission-mode auto`; anything they
try outside allowed commands shows as `blocked`.

# Workorder notes

- A workorder here is committed to master before dispatch, so the worker's
  `wo/<slug>` branch contains it.
- `wt merge` runs the `pre-merge` hook in `.config/wt.toml`
  (`openknowledge validate`) before fast-forwarding.
- `repo: <gita name>` in a workorder's frontmatter targets another repo
  instead; see [decision 0002](/decisions/0002-orchestration-model.md).

# Open issues

- Cross-repo workorders need their own `.config/wt.toml` in the target
  repo if they should be gated by a `pre-merge` hook — most target repos
  don't have one yet (see e.g. [okn](okn.md)).

[^decision-0002]: Decision 0002 — orchestration model
[^decision-0003]: Decision 0003 — repo roles
[^decision-0004]: Decision 0004 — knowledge lifecycle
