---
type: Index
title: studio — the gamemaker framework, translated to generic agent work
description: The reusable mechanics of gamemaker/ (Claude Code Game Studios) with the game domain removed, mapped onto skogai's vocabulary.
tags: [studio, gamemaker, patterns, orchestration]
status: draft
---

# studio

`gamemaker/` is a 49-agent, 74-skill framework for building games with
Claude Code. Most of its weight is game-specific: engine specialists, GDDs,
art bibles, playtests. Under that layer is a general model of how a human
and a team of agents turn an idea into a shipped, verified result. That
model is the same loop skogai runs:

```text
intent → workorder → isolated worktree → routed context → agent run
       → observable result → validation → land → memory / knowledge
```

This folder keeps the model and drops the domain. It contains no agents,
only the patterns that agents, skills and workorders are built from. Each
pattern is written so a domain (a game, a CLI, a knowledge bundle, an agent
home repo) can be plugged in.

## What was kept and what it became

| gamemaker | studio (generic) | skogai counterpart |
|---|---|---|
| Studio hierarchy: directors → leads → specialists | [Role archetypes](docs/roles.md): steward, lead, worker, reviewer | orchestrator session → workers (decision 0002) |
| Director gates (`CD-PILLARS`, `TD-ADR`, …) | [Gates](docs/gates.md): named review points with a fixed verdict vocabulary | `pre-merge` hook, `wo land` review of report + diff |
| Verdicts + `NOT ASSESSED` + escalation | Same, unchanged | — (new) |
| Concept → Systems → Technical Setup → Pre-Production → Production → Polish → Release | [Lifecycle](docs/lifecycle.md): Frame → Shape → Ground → Plan → Build → Verify → Land | the north-star lifecycle |
| `workflow-catalog.yaml` (phase steps + artifact globs) | Lifecycle steps detected by artifact on disk, never by memory | `status:` in workorder frontmatter |
| Epic / story / acceptance criteria / `/story-done` | [Work units](docs/work-units.md): goal → workorder → criteria → evidence | `.skogai/workorders/NNNN-slug.md` + `## Report` |
| `modes.rigor` fronting review, workflow, team size, docs, QA | [Modes](docs/modes.md): one rigor knob, three automation levels | "skogai is experimental, land automatically" |
| `production/session-state/active.md` checkpoint | [Context and memory](docs/context-and-memory.md): the file is the memory | decision 0007 (memory must be maintained) |
| `rules/agent-memory.md` | "Record a method, not a state" | decision 0007 best-before dates |
| `rules/skill-authoring.md` (five obligations) | [Checks and recovery](docs/checks-and-recovery.md) | — (new) |
| `error-recovery-protocol.md` (Trigger 0) | Observe the artifact, not the transcript | "a design document … or agent report is not enough on its own" |
| Collaboration protocol (Question → Options → Decision → Draft → Approval) | [CLAUDE.md](CLAUDE.md) operating contract | skogix veto |
| "Nothing goes upstream" | Push only to origins we own | decision 0006 |
| "Helpers emit observations, never verdicts" | Same, unchanged | — |
| Read design docs by section | Progressive disclosure: route → section → file | `wip/progressive-disclosure.md`, routing |

## What was dropped

- All 49 agent definitions and the 74 skills. They are game instances of
  the patterns; a domain writes its own from [templates/](templates/).
- Engine references, engine code roots, per-engine test runners.
- Game documents: GDD, art bible, pillars, playtest, economy, localisation.
- The YAML resolver (`yaml-helper.sh`, 2 000+ lines) and `effects-map.md`
  (2 500 lines). The *idea* of resolving config once at skill start is kept;
  the machinery was too heavy to carry over unread.
- Hooks. Their jobs are listed in [checks-and-recovery](docs/checks-and-recovery.md)
  as candidates, but per decision 0007 a fence is structural first and a
  hook second.

## Layout

```text
studio/
├── README.md                 # this file: the translation map
├── CLAUDE.md                 # the operating contract a project imports
├── docs/
│   ├── lifecycle.md          # phases, detected by artifact
│   ├── roles.md              # archetypes, authority, delegation
│   ├── gates.md              # review points and verdicts
│   ├── modes.md              # rigor and automation
│   ├── work-units.md         # goal → workorder → evidence
│   ├── context-and-memory.md # checkpoint, section reads, memory hygiene
│   └── checks-and-recovery.md# check-authoring obligations, error recovery
└── templates/
    ├── role.md               # an agent definition skeleton
    ├── gate.md               # a gate definition skeleton
    ├── workorder.md          # a unit of work with acceptance criteria
    ├── checkpoint.md         # the session checkpoint file
    └── project.yaml          # the minimal config surface
```

## Using it

1. Import `studio/CLAUDE.md` from the project's own `CLAUDE.md`.
2. Name the domain's roles from `templates/role.md`. Start with one
   worker and one reviewer; add roles only when two kinds of work keep
   colliding.
3. Define the gates the domain actually needs from `templates/gate.md`.
   A domain with no gates runs at `rigor: minimal` and that is fine.
4. Write work as workorders from `templates/workorder.md`.

## Open questions

- Where this lives long-term. It is a pattern library, so it fits
  `dash-skogai` (shared layer) or `marketplace` (as a plugin) better than
  this personal repo. It starts here because `gamemaker/` is here.
- Whether gates become workorder `status` transitions in `bin/wo`, or stay
  as prompts an orchestrator follows.
- OKF types: the docs here use `type: Pattern`. If they move into a bundle,
  they should be validated there.
