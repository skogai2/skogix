---
type: Repository
title: skogai-routing
description: Defines the "routing file" convention (SKOGAI.md/CLAUDE.md/AGENTS.md as choice-portals) plus a skill teaching the skogfences layout; a seed, not yet wired in.
tags: [repo, design-doc, src]
generated: { by: "claude-code/claude-opus-5-5", at: "2026-10-17T00:00:00Z" }
stale_after: 2026-11-17T00:00:00Z
sources:
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: survey
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0012-survey-skogai-routing.md
    title: Survey workorder 0012
---

# Role

Defines the "routing file" convention — all-caps `.md` files
(`SKOGAI.md`/`CLAUDE.md`/`AGENTS.md`) that own other files and act as
choice-portals — plus a Claude Code skill
(`skills/skogai-routing/SKILL.md`) teaching the `/skogai`/`.skogai`
("skogfences") vocabulary.[^survey] Not covered in decision 0003 —
untracked/not yet assigned a firm role.

# Location

Local clone: `/home/skogix/.local/src/skogai-routing`. Remote:
`https://github.com/skogai2/skogai-routing.git`. gita group: `src`.
Older copies of the same skill content exist elsewhere on this machine
(e.g. under `old-dot-skogai/`), outside this repo.

# State

Seed/skeleton, not yet active tooling: a single `init` commit; the
glossary points to `docs/concepts/definitions.md`, which doesn't
exist.[^survey] It defines the theory of routing files but has no
root-level routing file of its own, and isn't yet referenced from the
real repos (e.g. this one) that use the `@`-include convention it
documents.

# v1 router work

A later, more developed version of the skill (the `type: router` +
`<routes>` convention, `CLAUDE.md` routing rules, JSON schemas,
validators) lived only in `~/skogix/.projects/routing`. On 2026-10-17
it moved to `~/skogai/dash-skogai`: the convention is the draft type
`type/router.md`, the rest is kept as-is under `tmp/routing/`, and the
open questions are `router` items in `dash-skogai/TODO.md`. Its
validator is broken (unresolvable schema `$ref`). skogai decision 0006
keeps routing out of dash until the type layer works.

# Workorder notes

- If asked to add a root routing file, decide whether it supersedes
  `skills/skogai-routing/AGENTS.md` as the entry point.
- The three reference docs' `dot-skogai/...` permalinks look like
  copy-paste leftovers from a `dot-skogai` source tree.

# Open issues

- Is wiring this convention into skogai's own routing files an intended
  next step, or does skogai-routing stay a separate, unreferenced spec?
- Should `docs/concepts/definitions.md` be created, or was the glossary
  reference written for a different repo?

[^survey]: Survey workorder 0012
