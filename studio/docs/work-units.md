---
type: Pattern
title: Work units — goal, workorder, criteria, evidence
description: gamemaker's epic/story/acceptance-criteria/story-done loop mapped onto skogai workorders, with readiness and closing as gates.
tags: [studio, workorders, stories, acceptance-criteria]
status: draft
---

# Work units

gamemaker plans in epics and stories. A story is the unit an agent builds
in one go; it carries its own context so the builder does not read the
whole design. In skogai that unit already exists: the workorder.

| gamemaker | studio | skogai |
|---|---|---|
| epic | goal | a group of workorders (or a todo, per skogix's definitions) |
| story | workorder | `.skogai/workorders/NNNN-slug.md` |
| `Status: Ready / In Progress / Complete` | `status` | `open / done / blocked` |
| `/story-readiness` + `QL-STORY-READY` | readiness gate | — (new) |
| `/dev-story` | build | `wo dispatch` |
| `/story-done` + evidence | closing gate | `## Report` + `wo land` |

## What a workorder carries

`templates/workorder.md`. The parts that matter, from gamemaker's story
template:

- **Context, by reference.** The design note and decision it implements,
  by path and section, plus a one-line summary of each. The worker reads the
  summary and opens the source only when it needs to.
- **Acceptance criteria.** Each one specific enough that the worker knows,
  without asking, when it is met.
- **Type**, which decides the evidence (below).
- **Out of scope.** What neighbouring workorders handle. Builders drift
  into neighbouring work when nobody says where the border is.
- **Files.** What it is expected to create or change.

## Readiness

Before dispatch, a reviewer checks that every criterion is testable as
written: `READY / GAPS [criteria] / NOT READY`. A criterion that can only
be checked in a full integration run is marked DEFERRED, not blocked.

## Evidence by type

| Type | Evidence | Default |
|---|---|---|
| Logic | automated test, passing | blocking |
| Integration | integration test or a recorded run | blocking |
| Observable (UI, output, behaviour) | retained capture of it running | blocking |
| Config / data | smoke check | advisory |
| Docs / knowledge | validator pass (e.g. `openknowledge validate`) | blocking |

"Retained" is load-bearing: the evidence is still on disk when the unit
closes. Evidence that was captured and thrown away is an assertion.

**A parse check is not a run.** If the unit changes something observable,
someone launches it and looks.

## Closing

Closing checks each criterion against evidence and reports deviations
from the design, the decisions and the unit's own scope **as facts**. The
unit is marked done only on approval (or, in autonomous mode, with the
decision logged). The worker then names the next unit and writes the
checkpoint.
