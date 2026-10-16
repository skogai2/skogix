---
type: Repository
title: skogai-cli
description: The skogai CLI (stdlib-only Python) for skogai conventions — mid-rework, currently not runnable.
tags: [repo, cli, src]
generated: { by: "claude-code/claude-sonnet-5", at: "2026-10-10T00:00:00Z" }
stale_after: 2026-11-10T00:00:00Z
sources:
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: survey
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0008-survey-skogai-cli.md
    title: Survey workorder 0008
---

# Role

The `skogai` CLI: "one place for skogai conventions" — stdlib-only
Python, starting with an `env` module and growing `config`/`links`/a
`.skogai` store synced from [dash-skogai](dash-skogai.md).[^survey]

# Location

Local clone: `/home/skogix/.local/src/skogai-cli`. Remote:
`https://github.com/skogai2/skogai-cli.git`. gita group: `src`.

# State

Mid-rework, currently not runnable. On 2026-10-08 the entire Python
implementation was wiped in one commit (preserved on the
`python-implementation` branch); since then only two research-notes
commits have landed, no code.[^survey] `SKOGAI.md` still links to seven
files that no longer exist on `master`.

# Workorder notes

- Say explicitly whether a workorder should resurrect code from
  `origin/python-implementation` or build the rework from scratch — the
  wipe commit is ambiguous on this.
- Don't assume `SKOGAI.md`'s doc links are real; several are dead until
  the rework recreates them.
- The only live install (`~/.local/bin/skogai`, a `uv` editable install)
  is already broken, pointing at a path from before the repo moved — not
  something a worktree worker needs to fix unless asked.

# Open issues

- Is `origin/python-implementation` meant to be cherry-picked from, or
  purely historical?
- Should `SKOGAI.md` be trimmed to match current (near-empty) reality,
  or kept as the target spec?

[^survey]: Survey workorder 0008
