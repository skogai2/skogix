---
type: Repository
title: skogai-git-workflow
description: A design doc proposing a git-diff-staging-based "turn-based editing protocol"; not yet implemented.
tags: [repo, design-doc, src]
generated: { by: "claude-code/claude-sonnet-5", at: "2026-10-10T00:00:00Z" }
stale_after: 2026-11-10T00:00:00Z
sources:
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: survey
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0011-survey-skogai-git-workflow.md
    title: Survey workorder 0011
---

# Role

Proposes a "turn-based editing protocol" where `git diff`/`git add -p`
staging stand in for an agent conversation's proposal/consensus state,
and sketches a `skogai-turn` CLI (`status`, `pass`, `commit`, `reset`) as
an MVP.[^survey] Not covered in decision 0003 — untracked/not yet
assigned a firm role.

# Location

Local clone: `/home/skogix/.local/src/skogai-git-workflow`. Remote:
`https://github.com/skogai2/skogai-git-workflow.git`. gita group: `src`.

# State

Seed, not yet implemented. A single `init` commit added `README.md` and
an unrelated 3-line script, `bin/claude-simple-prompt`; no `skogai-turn`
CLI exists anywhere in the repo.[^survey]

# Workorder notes

- Any workorder to "implement the turn protocol" is greenfield work, not
  a fix — point it at the MVP section of `README.md`.
- No build/test/lint exists; verification is by inspection.

# Open issues

- Is `bin/claude-simple-prompt` meant to become part of the eventual
  implementation, or is it unrelated and parked here incidentally?
- Is this repo meant to build the `skogai-turn` CLI, or stay a design
  doc for now?

[^survey]: Survey workorder 0011
