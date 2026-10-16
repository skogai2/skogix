---
type: Decision
title: A change counts once it reaches origin — wo land pushes, but only to origins we own
description: Unpushed local work is treated as not having happened; wo land pushes the merged default branch to origin when origin is a skogai2 or Skogix repo, and never to fork upstreams.
tags: [decision, git, orchestration, push]
status: stable
generated: { by: "human:skogix", at: "2026-10-10T00:00:00Z" }
verified: { by: "human:skogix", at: "2026-10-10T00:00:00Z" }
---

# Context

[Decision 0005](0005-dash-and-dot-skogai.md) made each repo's remote origin
the only source of truth. Until then, `wo land` merged locally and skogix
pushed by hand. skogix's rule is that "we push whenever a
concept/idea/module/change is made", and that a change made locally but
not pushed is disposable and is treated as not having happened.

# Decision

- **`wo land` pushes.** After both merges succeed, it pushes the target
  repo's default branch and skogai's `master` to `origin`.
- **Only to origins we own.** A push is allowed only when the origin push
  URL belongs to the `skogai2` org or to the `Skogix` user. Fork upstreams
  (for example `openknowledge-sh/openknowledge` or `scaccogatto/okf-skills`)
  are never pushed to. `wo land` refuses to land a workorder whose repo has
  any other origin.
- **No silent reconciling.** Before it merges, `wo land` fetches and
  refuses to continue if the local default branch is behind origin or has
  diverged from it. Reconciling is a separate, explicit step.
- **Interim, by design.** This is the setup until agents have their own
  GitHub users, SSH keys and scoped privileges. At that point the system
  itself enforces what each agent may do, and PRs approved by agents
  replace direct pushes (see decision 0005's vision).

# Consequences

- Anything still unmerged when a session ends is disposable by definition.
- The owner allowlist is `PUSH_OWNERS` in `bin/wo`.
