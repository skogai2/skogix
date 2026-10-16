---
type: Decision
title: Knowledge lifecycle — raw workorders, synthesized pages, deprecation instead of deletion
description: Landed workorders are the immutable raw record; knowledge pages summarize them with OKF sources and stale_after, and outdated pages are deprecated rather than deleted.
tags: [decision, knowledge, okf, workorders]
status: stable
generated: { by: "human:skogix", at: "2026-10-10T00:00:00Z" }
---

# Context

Surveys and other workorders produce long reports that go stale. skogix
asked how to handle "old sources and archived reports". The OKF spec
provides `sources` (§5.1) for provenance, `status: draft|stable|deprecated`
(§5.4), and `stale_after` (§5.5). The bundle's agent rules say to keep raw
material separate from synthesized content.

# Decision

- **Raw layer: `.skogai/workorders/`.** A landed workorder, including its
  `## Report`, is the archive. It is never edited after landing. A newer
  workorder replaces it, and the old one stays in place. Git history covers
  everything else.
- **Synthesized layer: `.skogai/knowledge/`.** Concept pages summarize what
  is currently true. They cite the workorders they derive from in `sources`,
  using absolute GitHub URLs, because workorders live outside the bundle.
- **Staleness.** Pages derived from a point-in-time survey carry a
  `stale_after` date, 30 days by default. A stale page is a signal to
  dispatch a fresh survey workorder. It is not a signal to delete the page.
- **Deprecation, not deletion.** When a page no longer describes anything
  current, set `status: deprecated` and say in one line what replaced it.
  Delete a page only if it never should have existed.
- **No separate archive folder.** OKF `status` and git already cover what
  an `archive/` folder would do.

# Consequences

- Before trusting a knowledge page, an agent checks `status` and
  `stale_after`.
- Re-surveying is cheap. Copy the survey workorder brief with a new number,
  dispatch it, then update the page and its `sources`.
