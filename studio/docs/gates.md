---
type: Pattern
title: Gates — named review points with honest verdicts
description: gamemaker's director-gate pattern without the directors — gate definitions, the verdict vocabulary including NOT ASSESSED, escalation, review modes and recording outcomes.
tags: [studio, gates, review, verdicts]
status: draft
---

# Gates

A gate is a named point where a reviewer judges an artifact before work
moves on. gamemaker has 28 of them (`CD-PILLARS`, `TD-ADR`,
`QL-STORY-READY`, …). The pattern underneath is what transfers.

## A gate is a file

Each gate is defined once, in its own file (`templates/gate.md`), with:

- **ID** — `<ROLE>-<WHAT>`, e.g. `TECH-DECISION`, `QA-READY`, `SCOPE-PLAN`.
- **Trigger** — which step runs it.
- **Context to pass** — the exact inputs, by path and section.
- **Prompt** — the question the reviewer answers.
- **Verdicts** — the gate's own three words.

The orchestrator **passes the gate file's path** to the reviewer and does
not read it itself. The gate is read in the reviewer's context window, so
the orchestrator stays small and the prompt cannot drift between callers.

## The verdict vocabulary

Every gate returns one of four:

| Verdict | Meaning | Action |
|---|---|---|
| **APPROVE** | No issues. | Continue. |
| **CONCERNS [list]** | Issues, not blocking. | Show the human: revise / accept / discuss. |
| **REJECT [blockers]** | Blocking issues. | Do not write or advance until resolved. |
| **NOT ASSESSED [what was missing]** | An input was missing or unreadable; no judgement was made. | Supply it and re-run, or record it. Never treat it as APPROVE. |

A gate may rename the first three (`ADEQUATE / GAPS / INADEQUATE`,
`ON TRACK / AT RISK / OFF TRACK`); `NOT ASSESSED` is the same word
everywhere.

**Rank:** REJECT > CONCERNS > NOT ASSESSED > APPROVE. A known problem is
more actionable than an unknown, and a gate that could not look has
approved nothing.

**Escalation:** when several reviewers run at one gate, the strictest
verdict wins. One REJECT overrides every APPROVE; one NOT ASSESSED keeps
the result from being APPROVE.

## Review modes

| `review_mode` | What runs |
|---|---|
| `full` | Every gate. |
| `lean` | Phase gates only. |
| `solo` | No gates. Each skipped gate still prints `[GATE-ID] skipped — solo`. |

It follows `modes.rigor` unless set (see `modes.md`). A skill may accept
`--review <mode>` for one run.

A gate that is the *only* check of its kind in a pipeline runs in every
mode. gamemaker does this for narrative consistency; the generic rule is
that a mode may remove redundant review, never the last one.

## Recording the outcome

Write the verdict into the reviewed artifact's header, so the record lives
with the thing it judged:

```markdown
> **Review (TECH-DECISION)**: APPROVED 2026-10-25
> **Review (QA-READY)**: NOT ASSESSED 2026-10-25 — no acceptance criteria
```

In skogai the natural home is the workorder's `## Report`, and the `wo
land` step is a gate whose reviewer is the orchestrator.

## Phase gates

A phase gate is a panel: one reviewer per steward concern, spawned in
parallel, verdicts escalated as above. The panel's width scales with
`workflow` (scope steward alone at minimal, technical + scope at standard,
all at full). Width never softens a verdict.
