---
type: Repository
title: dot
description: Agent-home repo for base-environment/dotfiles work, a future implementer skogai will orchestrate to — not a dispatch target yet.
tags: [repo, agent-home, home]
generated: { by: "claude-code/claude-sonnet-5", at: "2026-10-10T00:00:00Z" }
stale_after: 2026-11-10T00:00:00Z
sources:
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: survey
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0004-survey-dot.md
    title: Survey workorder 0004
---

# Role

Skogix's agent for the base environment: dotfiles, shared dev tooling,
shell ergonomics, agent infrastructure — explicitly not individual
project implementation.[^survey] Per decision 0003 it is a **future
implementer** skogai will orchestrate to, once skogai is closer to its
original design; no workorders go here yet.[^decision-0003]

# Location

Local: `/home/skogix/dot`. Remote: `https://github.com/skogai2/dot.git`.
gita group: `home`.

# State

Young, early work-in-progress: 7 commits, all 2026-09-30 to 2026-10-02,
none since.[^survey] Scaffolding (`gptme-agent-template`) is finished;
nine `review-gptme-*` tasks are still backlog. The disabled systemd unit
`gptme-agent-dot.service` means it isn't running autonomously.

# Workorder notes

- Not a dispatch target yet — decision 0003 holds off until skogai's
  orchestration integration with agent-home repos is further along.
- If that changes: run `git submodule update --init --recursive`
  (`gptme-contrib`); never run `dotfiles/install.sh` /
  `make install-dotfiles` (it rewrites global git config and
  `~/.config/git/hooks`, which currently points at the `claude` repo's
  copy instead).
- This repo's own `AGENTS.md` mandates "commit directly to master" and
  "no AI attribution," which conflicts with skogai's own workorder/attribution
  conventions — unresolved, moot while no workorders land here.

# Open issues

- `dot`'s global git-hooks install currently points at `claude`'s
  dotfiles, not its own — intentional, or should `dot` take over that
  symlink eventually?
- `gptme-contrib` submodule is pinned to a feature branch, not `master`.

[^decision-0003]: Decision 0003 — repo roles
[^survey]: Survey workorder 0004
