---
type: Repository
title: okn
description: The Open Knowledge CLI (openknowledge/okn), a mature fork vendored for skogai2; validates and serves this very knowledge bundle.
tags: [repo, okf, cli, src, forks]
generated: { by: "claude-code/claude-sonnet-5", at: "2026-10-10T00:00:00Z" }
stale_after: 2026-11-10T00:00:00Z
sources:
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: survey
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0013-survey-okn.md
    title: Survey workorder 0013
---

# Role

The Open Knowledge CLI: turns repository markdown into a managed,
searchable OKF knowledge base, with validation, search, review,
publishing and Knowledge CI.[^survey] It is the tool that validates
skogai's own `.skogai/knowledge` bundle. The repo is `skogai2/okn`, a
fork of `openknowledge-sh/openknowledge`; its `SKOGAI.md` calling it
`okf2` is stale wording, tracked by workorder 0016.

# Location

Local clone: `/home/skogix/.local/src/okn`. Remotes: `origin` →
`https://github.com/skogai2/okn.git`, `upstream` →
`https://github.com/openknowledge-sh/openknowledge.git`. gita groups:
`src`, `forks`.

# State

Active, mature — dense recent commit history, release tagging
(`v0.13.0`), a Go CLI, a web viewer, full CI.[^survey] It carries its own
colocated OKF `Wiki/` documenting the product itself. No `.config/wt.toml`
exists yet, so there's no `pre-merge` safety net for a `wt` worktree
here.

# Workorder notes

- The full `pnpm test` is heavy (Playwright, full Go suite); tell the
  worker which narrower script to run (e.g. `test:cli`, `check:format`)
  unless a full run is actually wanted.
- Any `Wiki/`-touching change must follow `Wiki/AGENTS.md`'s ASD-STE100
  writing rules and run `okn validate "Wiki"`.
- The repo already carries an existing uncommitted staged `.gitignore`
  change predating any worker — say whether to carry it forward or drop
  it.

# Open issues

- No skogai-side decision or routing entry yet documents this repo's
  role from the orchestration side, distinct from its own product
  `Wiki/`.

[^survey]: Survey workorder 0013
