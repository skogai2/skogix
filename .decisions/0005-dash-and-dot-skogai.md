---
type: Decision
title: dash- and dot-skogai — origin is the source of truth; both layers are kept
description: Remotes are the only source of truth and every local checkout (including /skogai and ~/.skogai) is disposable; /skogai plus skogcli replaced ~/.skogai as the shared layer, and dot-skogai stays and will be used once an installer exists.
tags: [decision, repos, dash-skogai, dot-skogai]
status: stable
generated: { by: "claude-code/claude-opus-5-5", at: "2026-10-09T23:33:53Z" }
verified: { by: "human:skogix", at: "2026-10-09T23:33:53Z" }
sources:
  - id: interview
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0019-interview-dash-and-dot-skogai.md
    title: Interview workorder 0019
---

# Context

The `dash-skogai` survey (workorder 0007) found two separate local
checkouts, `/skogai` and `~/.local/src/dash-skogai`, and asked which one is
the source of truth. `dot-skogai`
(`~/.skogai`) was untracked and empty, and its role was unclear.
skogix answered both in the workorder 0019 interview.[^interview]

[^interview]: Interview workorder 0019

# Decision

- **The remote is the only source of truth.** Work is pushed to the repo's
  origin and is pulled wherever it is used locally. Every local checkout,
  including `/skogai` and `~/.skogai`, is disposable. The goal is to
  rebuild the machine from the ground up (from `archinstall`) on each
  iteration.
- **Dispatch to whichever repo a change belongs in.** dash-skogai and
  dot-skogai are no exception. What counts is that the change reaches
  origin.
- **Layers.** `~/.skogai` (dot-skogai) was the original user-level layer,
  the skogai counterpart of `~/.claude/`. `/skogai` (dash-skogai) plus
  skogcli/skogai-cli replaced it as the shared layer, so that repos can be
  self-contained and are not bound to one machine.
- **dot-skogai is kept and will be used.** It is empty because no
  "dot-skogai installer" exists yet. How to implement that is undecided.
- **Vision before details.** For both repos, only the end goal and intent
  are fixed for now. That goal is full agent access to `/skogai` and
  agent-approved PRs with a skogix veto. The implementation details are not
  fixed.

# Consequences

- Knowledge pages for these repos keep current state and vision in
  separate sections. See [dash-skogai](../repos/dash-skogai.md) and
  [dot-skogai](../repos/dot-skogai.md).
- Changes that exist only in a local checkout are not durable. They
  have to reach origin.
