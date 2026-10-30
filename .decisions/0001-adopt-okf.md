---
type: Decision
title: Adopt Open Knowledge Format for skogai's structured knowledge
description: Replace the ad-hoc .skogai/proposals and knowledge/decisions draft files with a real OKF bundle at .skogai/knowledge.
tags: [decision, okf, knowledge]
status: stable
generated: { by: "human:skogix", at: "2026-10-09T00:00:00Z" }
---

# Context

skogai had been drafting an ad-hoc decision/proposal format by hand:
`.skogai/knowledge/DECISIONS.md` (a router stub pointing at an empty
`decisions/` folder) and `.skogai/proposals/` (`proposal-okf-adoption.md`,
`types-and-decisions.md`). The latter was itself an unfinished attempt to
reinvent decision-file conventions — frontmatter fields, numbering,
`index.md` vs. a hand-maintained index — that the Open Knowledge Format
(OKF) spec already defines.

# Decision

Replace the hand-rolled drafts with a real OKF v0.2 bundle at
`.skogai/knowledge`, scaffolded with `openknowledge scaffold`, with
maintenance rules `project`, `writing`, `decisions`, `agents`, and
`changelog` enabled (see `.openknowledge.toml` and `AGENTS.md`). The old
draft files (`knowledge/DECISIONS.md`, `proposals/proposal-okf-adoption.md`,
`proposals/types-and-decisions.md`) were deleted rather than migrated
verbatim — OKF's own `index.md` and `type`/`status` conventions supersede
the questions they were trying to answer from scratch.

# Consequences

- `.skogai/ROUTES.md` now points at `knowledge/index.md` instead of the
  removed `knowledge/DECISIONS.md`.
- Future decisions in this repo go in `.skogai/knowledge/decisions/` as
  OKF concept files (`type: Decision`), not as unnumbered proposal drafts.
- The `decisions` maintenance rule in `AGENTS.md` governs how these get
  written going forward.
