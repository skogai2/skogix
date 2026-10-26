---
type: Pattern
title: Modes — one rigor knob, three automation levels
description: How gamemaker scales ceremony to project size with a single modes.rigor value that fronts review, workflow, team size, docs and QA, plus a separate automation knob for how often the human is asked.
tags: [studio, modes, config, rigor, automation]
status: draft
---

# Modes

gamemaker's best measured result is that ceremony must be adjustable. The
same brief built at `rigor: minimal` wrote 1 document before the first line
of code; at `standard` it wrote 30 and took 58 minutes longer. Both
produced a working, tested game, and reviewers ranked the `standard` build
last: the extra documents bought traceability, not a better result. Two
knobs carry that lesson.

## `modes.rigor` — how much structure

One value, `minimal | standard | full`, that **fronts** several others:

| Fronted knob | minimal | standard | full |
|---|---|---|---|
| `review_mode` (gates) | solo | lean | full |
| `workflow` (required artifacts) | brief only | key design notes, critical decisions | every design note and decision |
| `team.size` (roles spawned) | individual | small | full roster + adversarial review |
| `qa.level` (evidence) | criteria checked | tests for logic | tests + observed runs everywhere |

Rules gamemaker learned the hard way:

- **Never seed a fronted knob in the shared config.** Writing
  `review_mode: lean` into `project.yaml` pins it and silently breaks the
  rigor expansion. Set a fronted knob only as a deliberate override.
- **No hardcoded fallback.** A skill that falls back to `standard` when a
  knob is unset ignores `minimal` and `full` entirely. The fallback is the
  rigor expansion.
- **Resolve once, at skill start**, and use the resolved value. Do not
  re-derive it at each step.
- **Per-part overrides must match a real part.** An override key that
  matches nothing is an error to report, not a no-op.

## `modes.automation` — how often to ask

| Mode | Asks | Writes |
|---|---|---|
| `collaborative` | Every multi-option decision, with options. | After an explicit yes per file. |
| `guided` | Major decisions only, two options with a recommendation. Minor ones: state the choice and continue. | New files wait for a yes; updates proceed after a summary. |
| `autonomous` | Only `always_ask` categories. | Directly. Every decision is logged. |

**Major vs minor** is decided by the skill author per decision, not by the
agent at run time. A short `always_ask` list (destructive operations,
pushing, spending money, anything outside the repo) prompts in every mode.

skogai today is `rigor: minimal`, `automation: autonomous` with landing as
the logged decision, and skogix's veto as the `always_ask` override.

## Precedence

```text
--flag on the run  >  project.local.yaml (per person, gitignored)
  >  project.yaml (shared)  >  rigor expansion
```
