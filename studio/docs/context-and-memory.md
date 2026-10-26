---
type: Pattern
title: Context and memory — the file is the memory
description: gamemaker's session checkpoint, section-level reads and agent-memory rules, generalised and lined up with skogai decision 0007.
tags: [studio, context, memory, checkpoint]
status: draft
---

# Context and memory

## The checkpoint

gamemaker keeps one file, `production/session-state/active.md`, as the
session's memory. A hook prints its checkpoint region at every session
start, including after a compaction. The design is worth copying exactly
(`templates/checkpoint.md`):

| Region | Read by | Rule |
|---|---|---|
| `<!-- CHECKPOINT -->` … `<!-- /CHECKPOINT -->` | session start, every time | **Overwrite, never append.** Under ~25 lines. Current task, next step, blocker, files in progress, open questions. |
| Everything after | humans, an agent that wants detail | Free-form narrative. Rotated into a dated log at ~200 lines; nothing is deleted. |

Why two regions: one append-only file doing both jobs grows forever, and
every reader ends up reading a different slice of it. A named region costs
the same no matter how long the narrative gets.

Write the checkpoint so a cold reader can resume without opening anything
else.

## Write incrementally

For a multi-section artifact: create the file with every heading and empty
bodies, discuss one section, write it as soon as it is approved, update the
checkpoint. The decisions are then in the file, and the conversation about
that section can be compacted. The context holds one section, not the
whole document's history.

## Read by section

A brief names the sections an agent needs by heading. The agent finds the
heading (grep `^#`) and reads that range. A whole-file read of a large
document needs a reason. This is progressive disclosure
(`wip/progressive-disclosure.md`) applied inside one file: route → file →
section.

## Agent memory

gamemaker's `rules/agent-memory.md` lines up with decision 0007 almost
point for point:

- **Writing memory is allowed, and must be disclosed.** Say that a memory
  was written and where. An unmentioned write cannot be corrected.
- **Record a method, not a state.** "Check that a build exists before
  profiling; return BLOCKED naming what is missing" lasts. "There is no
  build here" is a timestamp that will become false.
- **If you must record a state, state what invalidates it**, on the same
  line: `INVALIDATED WHEN: …`. This is decision 0007's best-before date in
  sentence form; `stale_after` is the same thing in frontmatter.
- **Never record a temporary absence as a fact.** No code, no config, no
  tests yet: those are the states the project exists to leave.
- **Verify before you trust.** A recalled path, setting or count is checked
  before it is acted on. Memory is a starting point, never evidence.
- **Memory never records something the human declined to have written.**
