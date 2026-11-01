---
title: changelog
type: reference
permalink: skogai-routing/changelog
---

# changelog

## 0.1.0

first release. the scope is the routing step only.

- `SKOGAI.md` at the repo root is the single entry point (the root routing file).
- intentions and glossary moved from root-level all-caps files to lowercase leaves under `docs/`. under the glossary's own rule only routing files are all-caps.
- removed `skills/skogai-routing/AGENTS.md`. it only redirected to `SKILL.md`, so it was a second entry point to the same place.
- removed a stray hook-tap log from the skill folder and ignored hook logs going forward.
- reference permalinks now use `skogai-routing/…` instead of the old `dot-skogai/…` prefix.
- fixed a garbled `root` definition, a dangling pointer to a non-existent `docs/concepts/definitions.md`, and escaped closing tags in `dash-skogai.md`.
