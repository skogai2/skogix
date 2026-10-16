---
type: Decision
title: Knowledge and memory — two axes, maintained memory, and where each lives
description: Knowledge vs memory and global vs local form a 2×2; writing memory is always allowed but it must be maintained; global state lives in /skogai, and dot-skogai holds the tools that implement it per project.
tags: [decision, knowledge, memory, skogfences, dash-skogai, dot-skogai]
status: stable
generated: { by: "human:skogix", at: "2026-10-10T00:00:00Z" }
verified: { by: "human:skogix", at: "2026-10-10T00:00:00Z" }
sources:
  - id: skogfences
    resource: https://github.com/skogai2/skogai-routing/blob/master/skills/skogai-routing/references/skogfences.md
    title: skogfences — "welcome away from home"
---

# Context

Decision 0004 covered the lifecycle of knowledge pages, but not memory.
skogix restated the older skogai definitions, and the orchestrator
sanity-checked them against OKF on 2026-10-10.

# Decision

**Two axes.** Scope is global or local. Lifespan is knowledge (lasts) or
memory (expires).

| | Knowledge | Memory |
|---|---|---|
| **Global** | True-ish whatever the environment, reader or time. Examples: principles and patterns. No `stale_after`. | Shared once, to be acted on. Examples: events such as "the org was renamed". An append-only list. |
| **Local** | Like global knowledge, but context matters: the project, its owner, its state. Examples: decisions and repo pages. May carry `stale_after`. | Has a best-before date. On expiry it becomes knowledge, state, action (a workorder), or it is forgotten. |

- **Writing memory is always okay.** Anything may be written down, in any
  form. Claude Code's memory style is fine. The one requirement is that
  memory is **maintained**. Each local memory has a best-before date
  (`stale_after`). When it expires, someone triages it into one of the four
  outcomes. Forgotten memories stay only in git history and logs, not in
  active recall.
- **Global memory is read with a per-reader marker.** Each local repo keeps
  at least the id or timestamp of the last `/skogai/memory/` entry it read,
  or mirrors the folder and marks it as managed. Events are never edited.
  Only each reader's marker moves.
- **Promotion goes upward through repetition.** A local memory that keeps
  recurring becomes a pattern. A pattern that holds everywhere can become a
  principle. A principle stands until someone argues it out of place.
- **There are more types than these.** Principle, pattern, decision and
  list are examples, not a closed set. OKF `type` is free-form, so new
  types need no format change.
- **Rules are skogfences, not knowledge.** "The best way to enforce a rule
  is for it not to be an option to begin with."[^skogfences] Enforcement is
  structural: users, groups, permissions, separate homes and accounts.
  Knowledge pages may describe a fence. They never stand in for one. Checks
  in code such as `PUSH_OWNERS` in `bin/wo` are interim, until each agent's
  own account makes the forbidden action impossible.
- **Where things live.** `/skogai` (dash-skogai) holds the **global
  state**: `/skogai/knowledge/` and `/skogai/memory/`, as markdown in a
  shared format. dot-skogai holds the **implementation**, meaning the tools
  that apply that format inside a project's `.skogai/`.
- **One shared vocabulary.** The `.skogai/` file structure and a glossary
  of these concepts get defined once in `/skogai`. Every repo and agent then
  uses the same terms, whatever the implementation. `.skogai/ROUTES.md` in
  this repo is the temporary start of that structure.

[^skogfences]: skogfences — "welcome away from home"

# Consequences

- Until `/skogai/knowledge/` exists, global knowledge is staged in this
  bundle under `principles/` and moves to `/skogai` later.
- The memories in `skogai/tmp/` are triaged under this model.
  `write-and-commit-immediately` became the principle
  [write, commit, push](../principles/write-commit-push.md).
  `cc-memory-hooks-wired` expired and was forgotten.
  `gptme-util-memory-link` became state (the symlink), so the memory was
  forgotten. `okf-adoption-proposal` was already promoted to decision 0001.
- Memory maintenance needs a routine, such as a periodic triage workorder.
  The routine is not designed yet.
