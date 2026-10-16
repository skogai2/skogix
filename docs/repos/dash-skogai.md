---
type: Repository
title: dash-skogai
description: Source repo for /skogai, the shared machine-wide skogai layer for the skogai group's human and agent users — today a skogix-owned bootstrap of admin scripts, launchers and a coordination DB.
tags: [repo, infrastructure, src]
generated: { by: "claude-code/claude-opus-5-5", at: "2026-10-09T23:33:53Z" }
verified: { by: "human:skogix", at: "2026-10-09T23:33:53Z" }
stale_after: 2026-11-08T23:33:53Z
sources:
  - id: interview
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0019-interview-dash-and-dot-skogai.md
    title: Interview workorder 0019
  - id: interview-0020
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0020-interview-skogai-glossary-and-layout.md
    title: Interview workorder 0020
  - id: survey
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0007-survey-dash-skogai.md
    title: Survey workorder 0007
  - id: decision-0005
    resource: /decisions/0005-dash-and-dot-skogai.md
    title: Decision 0005 — dash- and dot-skogai
  - id: readme
    resource: /home/skogix/.local/src/dash-skogai/README.md
    title: dash-skogai README
---

# Role

`/skogai` ("dash" because it hangs directly off `/`) is the shared,
machine-wide skogai layer. It is owned by `skogix` and the `skogai` group,
and it is setgid. The `skogai` group holds the human users and the agent
Unix users `amy`, `claude`, `dot` and `goose`, whose homes are under
`/home`.[^interview] With skogcli/skogai-cli, it replaced `~/.skogai`
([dot-skogai](dot-skogai.md)) as the global layer, so that skogai repos can
be self-contained and are not tied to one machine's home directory
(see [decision 0005](/decisions/0005-dash-and-dot-skogai.md)).

# Current state

- Today it holds `admin/` bootstrap scripts that create the group and agent
  users and set up coordination, a generator for `uv` launchers for gptme
  and gptme-contrib (`bin/`, `tools/`), and a live `gptme-coordination` DB in
  `coordination/`.[^survey] It is not yet usable for direct agent work.
- The permissions are as the README states: `admin/`, `bin/` and `tools/`
  are `755`, so only the owner writes them, and only `coordination/` is
  group-writable.[^readme]
- Changes do not go through an agent approval process yet.
- `knowledge/` is the global knowledge bundle (`/skogai/knowledge/` once
  pulled): the shared glossary, the `.skogai/` layout and the named types,
  from interview workorder 0020. dash-skogai is the definition; every
  `.skogai` (dot-skogai) is an instance of it.[^interview-0020]

# Vision (not built yet)

- The agent Unix users have **full access** to `/skogai`.
- Changes reach `master` through PRs that **every agent approves**, and
  skogix has a veto. The earlier `skogai/dash-skogai` worked this way,
  and it serves as an example.
- `/skogai` holds everything shared between agents and skogai projects,
  for example the ansible playbooks (earlier versions are in the old
  `skogai` GitHub org, such as `skogansible-migration`) and the source of
  shared projects.
- Each repo selects or syncs what it needs from `/skogai` through
  skogcli/skogai-cli. Previously a per-repo `config.json` chose which
  modules to pull in.

# Location

- Source of truth: the remote `https://github.com/skogai2/dash-skogai.git`
  ([decision 0005](/decisions/0005-dash-and-dot-skogai.md)).
- `/skogai`: the live checkout. `~/dash-skogai` is a symlink to it.
- `/home/skogix/.local/src/dash-skogai`: the gita clone, in group `src`.

# Workorder notes

- Dispatch to dash-skogai whenever a change belongs there, as with any
  repo. What counts is that the change reaches origin. Local checkouts,
  `/skogai` included, pull from origin when they are used.
- Never run `admin/create-agents.sh`, `admin/setup-coordination.sh` or
  `admin/test-coordination.sh` on this machine. They use `sudo` and touch
  real system users.

[^interview]: Interview workorder 0019
[^survey]: Survey workorder 0007
[^interview-0020]: Interview workorder 0020
[^readme]: dash-skogai README
