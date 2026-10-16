---
type: Decision
title: Roles of the skogai2 repos and how skogai tracks them
description: skogai orchestrates; agent home repos become implementers later; gita in ~/.local/src replaces the old projects/ submodules; some repos are parked or superseded.
tags: [decision, repos, gita, orchestration]
status: stable
generated: { by: "human:skogix", at: "2026-10-10T00:00:00Z" }
sources:
  - id: surveys
    resource: https://github.com/skogai2/skogai/tree/master/.skogai/workorders
    title: Repo survey workorders 0002–0014
---

# Context

skogai used to hold the other repos as submodules under `projects/`. That
layout is gone. The 13 survey workorders (0002–0014) mapped the skogai2
org, and skogix answered the open questions they raised on 2026-10-10.[^surveys]

[^surveys]: Repo survey workorders 0002–0014

# Decision

- **Tracking.** gita tracks every repo skogai manages. New clones go in
  `~/.local/src/<repo>`. Repos that already live in a fixed home location
  stay there (`~/skogai`, `~/claude`, `~/.config/skogai`, `~/skogix`, `~/dot`).
  The gita groups are `home`, `src`, `forks` and `parked`.
- **skogai is the orchestrator.** It writes workorders and dispatches them
  to any gita-tracked repo with `repo: <gita name>`
  (see [0002](0002-orchestration-model.md)).
- **Agent home repos are future implementers.** `claude`, `dot` and the
  other agent homes will each take an implementation role that skogai
  orchestrates to. That integration waits until skogai is closer to its
  original design. Until then, do not send workorders into those repos.
- **Parked:** `skogai-fleet` (the nelson rework) may be reworked later, but
  not now.
- **Superseded:** `skogai-docs` / `~/claude-docs` was "clone the Claude Code
  docs to disk". `marketplace` replaces it, and it is no longer tracked.
- **Personal:** `skogix` is skogix's own dump repo. Its `old-skills/`
  directory is a large old test repo of skills, rules and scripts. It is not
  a workorder target.
- **Untracked for skogix to sort out:** `dot-skogai`, `open-knowledge-format`,
  `knowledge-catalog`, `forge` and `gptme-contrib`.
- **Dormant:** the global git hooks and dotfiles installers in `claude` and
  `dot` stay unused. Workers must not run them.
- **Global ignores:** `**/.skogai/logs/` (hook-tap output) and
  `**/.skogai/worktrees/` (wt worktree location) are in `~/.config/git/ignore`.

# Consequences

- Each repo's role and state are recorded in [repos](../repos/index.md).
- Cross-repo workorders need a `.config/wt.toml` in the target repo if they
  should be gated by a `pre-merge` check.
