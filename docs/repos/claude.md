---
type: Repository
title: claude
description: Agent-home repo for the "claude" persona, a future implementer skogai will orchestrate to — not a dispatch target yet.
tags: [repo, agent-home, home]
generated: { by: "claude-code/claude-sonnet-5", at: "2026-10-10T00:00:00Z" }
stale_after: 2026-11-10T00:00:00Z
sources:
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: survey
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0002-survey-claude.md
    title: Survey workorder 0002
---

# Role

Claude Code's own "home" repo in skogix's per-agent-home setup — a full
gptme-agent-template instance giving the persona "claude" a workspace
(journal, tasks, knowledge, memory). Its job is orchestration-flavored
integration work, but per decision 0003 it is a **future implementer**
skogai will orchestrate to, once skogai is closer to its original design.
Until then, no workorders go here.[^decision-0003]

# Location

Local: `/home/skogix/claude`. Remote: `https://github.com/skogai2/claude.git`.
gita group: `home`.

# State

Active but with unfinished identity setup: `tasks/initial-agent-setup.md`
is still `state: active`, 13 of 15 tasks are `backlog`, and `.skogai/memory/`
has uncommitted edits.[^survey] A global git-hooks installer
(`dotfiles/install.sh`) is staged here but dormant.

# Workorder notes

- Not a dispatch target yet — decision 0003 holds off until skogai's
  orchestration integration with agent-home repos is further along.
- If that changes: don't run `dotfiles/install.sh` (it rewrites global
  git hooks machine-wide); run `git submodule update --init --recursive`
  first (`gptme-contrib`, `projects/gptme`); use `git rev-parse
  --show-toplevel` rather than hardcoded paths.
- This repo's own `AGENTS.md` forbids AI attribution on commits, which
  conflicts with this orchestrator's attribution convention — unresolved,
  moot while no workorders land here.

# Open issues

- Attribution-convention conflict between this repo's `AGENTS.md` and
  skogai's own commit/PR attribution requirement, unresolved.
- Identity-setup (`tasks/initial-agent-setup.md`) left mid-review.

[^decision-0003]: Decision 0003 — repo roles
[^survey]: Survey workorder 0002
