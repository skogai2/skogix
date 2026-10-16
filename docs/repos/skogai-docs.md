---
type: Repository
title: skogai-docs
status: deprecated
description: A Claude Code docs-lookup plugin repo; superseded by marketplace, which now vendors the docs copy instead.
tags: [repo, deprecated]
generated: { by: "claude-code/claude-sonnet-5", at: "2026-10-10T00:00:00Z" }
stale_after: 2026-11-10T00:00:00Z
sources:
  - id: decision-0003
    resource: /decisions/0003-repo-roles.md
    title: Decision 0003 — repo roles
  - id: survey
    resource: https://github.com/skogai2/skogai/blob/master/.skogai/workorders/0009-survey-skogai-docs.md
    title: Survey workorder 0009
---

# Role

Was a Claude Code plugin marketplace (`code-docs-tools`) with one plugin,
`code-docs-lookup`, letting Claude answer Claude Code questions from a
local, offline-searchable docs copy instead of from memory.[^survey]
**Superseded by [marketplace](marketplace.md)**, which now vendors its
own docs copy; `skogai-docs` is no longer tracked by gita.[^decision-0003]

# Location

Was tracked at `/home/skogix/.local/src/skogai-docs`, with a second,
actually-live clone at `/home/skogix/claude-docs`. Remote:
`https://github.com/skogai2/skogai-docs.git`. No longer in a gita group.

# State

Deprecated. At last survey it was active but mid-build, with a
known-broken plain-prompt invocation path (`HANDOVER.md`'s "Open
problems," cause not found).[^survey] That work is not being continued
here — `marketplace`'s `docs/` + `code-docs-lookup` plugin replace it.

# Workorder notes

- Not a workorder target. Any future docs-lookup work belongs in
  [marketplace](marketplace.md).

# Open issues

None — superseded, no further decision needed here.

[^decision-0003]: Decision 0003 — repo roles
[^survey]: Survey workorder 0009
