---
type: Repository
title: skogai-fleet
description: A parked rewrite of the "nelson" multi-agent orchestration skill; may be reworked later but is not an active design to act on now.
tags: [repo, parked, skill]
generated: { by: "claude-code/claude-sonnet-5", at: "2026-10-10T00:00:00Z" }
stale_after: 2026-11-10T00:00:00Z
sources:
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: survey
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0010-survey-skogai-fleet.md
    title: Survey workorder 0010
---

# Role

A rewrite of an older "nelson" Claude Code skill: multi-agent
orchestration dressed in a Royal Navy squadron metaphor
(`SKILL.md`, `PERSONAS.md`, `references/`).[^survey] Per decision 0003
this is a **parked** old project that may be reworked later — it is not
a competing orchestration design to act on now, alongside
`bin/wo`/wt/herdr.[^decision-0003]

# Location

Local clone: `/home/skogix/.local/src/skogai-fleet`. Remote:
`https://github.com/skogai2/skogai-fleet.git`. gita groups: `src`,
`parked`.

# State

Parked. The orchestration skill itself is a skeleton: `SKILL.md` has 26
`TODO(script:...)` placeholders for helper scripts not yet built, and no
`.state/` directory exists anywhere — the workflow has never run to
completion.[^survey] A separate `hook-tap` side-plugin was added,
versioned, then deleted from the working tree without a commit.

# Workorder notes

- Not a dispatch target while parked.
- If reworked later: the uncommitted `plugins/hook-tap/` deletion (files
  gone on disk, still in `HEAD`) needs a decision first — commit the
  deletion or restore the files — before other work lands here.

# Open issues

- Is the `hook-tap` deletion intentional (retiring it) or accidental?
  Nothing in the repo says.

[^decision-0003]: Decision 0003 — repo roles
[^survey]: Survey workorder 0010
