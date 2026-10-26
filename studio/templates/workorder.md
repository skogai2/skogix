---
status: open            # open | done | blocked
type: logic             # logic | integration | observable | config | docs
repo: <gita name>       # omit for this repo
goal: <goal slug>
depends_on: []          # workorder numbers that must land first
---

# NNNN — <title>

## Context

- **Design**: `<path>` § <heading> — <one-line summary>
- **Decision**: `<path>` — <one-line summary of what it decided>

## Acceptance criteria

- [ ] <specific enough that the worker knows, without asking, when it is met>
- [ ] <…>

## Evidence

<what proves each criterion, per docs/work-units.md "Evidence by type", and
where it will be kept>

## Out of scope

- <NNNN+1>: <what that workorder handles instead>

## Files

- `<path>` — <create | change>

## Report

<!-- The worker appends here and sets `status`. Per criterion: met / not met,
     with the evidence path. Deviations from the design or the decisions, as
     facts. Anything not run, by name. -->
