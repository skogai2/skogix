---
type: Repository
title: dot-skogai
description: Source repo for ~/.skogai, the user-level skogai folder (the skogai counterpart of ~/.claude) — currently empty, waiting for a dot-skogai installer.
tags: [repo, infrastructure, untracked]
generated: { by: "claude-code/claude-opus-5-5", at: "2026-10-09T23:33:53Z" }
verified: { by: "human:skogix", at: "2026-10-09T23:33:53Z" }
stale_after: 2026-11-08T23:33:53Z
sources:
  - id: interview
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0019-interview-dash-and-dot-skogai.md
    title: Interview workorder 0019
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: decision-0005
    resource: /decisions/0005-dash-and-dot-skogai.md
    title: Decision 0005 — dash- and dot-skogai
  - id: init-commit
    resource: https://github.com/skogai2/dot-skogai/commit/3a436d7774874662bde92157373bd62fe96b5225
    title: dot-skogai init commit (skogai-routing references)
---

# Role

`~/.skogai` ("dot" is the file-safe name for the leading period) is the
user-level skogai folder. It plays the same role for skogai projects that
`~/.claude/` plays for Claude Code.[^init-commit] It was the original, and
for a while the only, SkogAI folder. It held journal, memory, knowledge,
inbox, plans, projects, scripts, skills and docs. Each repo had a
`config.json` that told skogcli which modules and files to use from it.[^interview]
Since then [dash-skogai](dash-skogai.md) (`/skogai`) plus
skogcli/skogai-cli has taken over the shared, machine-independent role
(see [decision 0005](/decisions/0005-dash-and-dot-skogai.md)).

# Current state

- `~/.skogai` is a checkout of `https://github.com/skogai2/dot-skogai.git`,
  and it is **empty**.
- It is untracked in gita ([decision 0003](/decisions/0003-repo-roles.md)).

# Vision (not built yet)

dot-skogai **will be used**. It is empty only because no "dot-skogai
installer" exists yet, and how that installer will work has not been
decided. Until there is enough in place to start adding to dot- and
dash-skogai, only the end goal and intent matter.[^interview]

# Workorder notes

- Dispatch to dot-skogai whenever a change belongs there, as with any
  repo. Note that it is untracked in gita, so `repo:` cannot name it yet.
- As with dash-skogai, the remote is the source of truth, and `~/.skogai`
  is a disposable checkout.

[^interview]: Interview workorder 0019
[^init-commit]: dot-skogai init commit (skogai-routing references)
