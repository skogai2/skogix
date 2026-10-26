---
type: Pattern
title: Lifecycle — phases detected by artifact
description: gamemaker's seven production stages generalised to seven phases of any agent-built project, each entered when its required artifacts exist on disk.
tags: [studio, lifecycle, phases]
status: draft
---

# Lifecycle

gamemaker moves a game through Concept → Systems Design → Technical Setup →
Pre-Production → Production → Polish → Release. With the game removed,
each stage answers a question that any project answers:

| Phase | Question | gamemaker stage | Typical artifacts |
|---|---|---|---|
| **Frame** | What is this and why does it matter? | Concept | brief (one page), principles / non-goals |
| **Shape** | What are its parts and how do they depend on each other? | Systems Design | parts map, one design note per part |
| **Ground** | What is it built on, and what is fixed? | Technical Setup | decisions (ADRs), stack pin, control rules |
| **Plan** | What is the order of work? | Pre-Production | goals, workorders with acceptance criteria |
| **Build** | Do the work, one unit at a time. | Production | diffs, workorder reports |
| **Verify** | Does it hold up as a whole? | Polish | evidence, review notes, fixed findings |
| **Land** | Is it in origin and recorded? | Release | merged branch, changelog, knowledge pages |

This is the north-star lifecycle seen from the project's side: Frame and
Shape are "intent", Plan produces workorders, Build is the agent run, Verify
is validation, Land is "Git diff / commit / PR" plus captured knowledge.

## Phases are read from disk

gamemaker's `workflow-catalog.yaml` lists each phase's steps with the
artifact that proves the step happened (a glob, plus a pattern to match
inside the file). `/help` reads the catalog and the disk, and tells the
user where they are. Nothing is remembered; everything is observed.

Keep this:

```yaml
phases:
  frame:
    next: shape
    steps:
      - id: brief
        required: true
        artifact: { glob: "docs/brief.md" }
      - id: principles
        required: false
        artifact: { glob: "docs/brief.md", pattern: "^## Principles" }
```

- `required: true` blocks moving to the next phase; `false` is a suggestion.
- `repeatable: true` marks a step that runs once per part or per workorder.
- A step whose completion cannot be detected says so in a `note:`; it is
  never assumed complete.

## Phase transitions are advisory

A phase gate (see `gates.md`) gives a verdict, and the human decides
whether to move on. The current phase is written to `project.yaml`
(`project.phase`) only when the human accepts the move.

## Minimal path

At `rigor: minimal` the ladder is replaced by a short path, because a
small project that never runs a phase gate would otherwise sit in Frame
forever with every later artifact flagged as missing:

```text
brief → workorders (in build order) → build next → close it → repeat
```

The brief's build order is the plan. This is what skogai runs today.
