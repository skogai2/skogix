---
type: Repository
title: open-knowledge-plugin
description: Claude Code-native OKF toolchain (skills, subagents, MCP server, GitHub Action) — a standalone fork, live-installed on this machine.
tags: [repo, okf, plugin, src, forks]
generated: { by: "claude-code/claude-sonnet-5", at: "2026-10-10T00:00:00Z" }
stale_after: 2026-11-10T00:00:00Z
sources:
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: survey
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0014-survey-open-knowledge-plugin.md
    title: Survey workorder 0014
---

# Role

The Claude Code-native toolchain for the Open Knowledge Format: agent
skills, two backfill subagents, a dormant Stop hook, an MCP server and a
GitHub Action.[^survey] It is a fork (`okf-skills`, upstream
`scaccogatto/okf-skills`), a **standalone repo**, not a path or
submodule inside the `skogai` monorepo. Its `SKOGAI.md` calls it
"vendored" into "the monorepo" — that wording is stale, from the earlier
submodule era, and is tracked by workorder 0017.

# Location

Local clone: `/home/skogix/.local/src/open-knowledge-plugin`. Remotes:
`origin` → `https://github.com/skogai2/open-knowledge-plugin.git`,
`upstream` → `https://github.com/scaccogatto/okf-skills.git`. gita
groups: `src`, `forks`. This exact path is also a live Claude Code
plugin-marketplace source (`known_marketplaces.json`), and this very
survey's OKF tools were loaded from it.

# State

Active, mature, documents itself in its own OKF bundle
(`.okf/index.md`).[^survey] The CI-is-broken finding from the survey
(the HEAD commit deleted `.claude-plugin/plugin.json` but
`ci.yml` still checked it) is resolved — the CI workflows folder has
since been renamed.

# Workorder notes

- This directory is a live plugin-marketplace source, not just a
  passive clone — a `wt` merge landing into this exact path changes the
  orchestrator's own live plugin tools underneath them; say explicitly
  whether that's expected, and consider a Claude Code restart after.
- Push/PR against `origin` only; `upstream` is read-only fork source.

# Open issues

- Two marketplace registrations (local directory + git source) resolve
  to the same plugin today — intentional dev/prod split, or prune to one?
- Should skogai's own decisions/workorders eventually route through this
  toolchain's `/okf:*` skills instead of hand-written markdown?

[^survey]: Survey workorder 0014
