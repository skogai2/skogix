---
type: Decision
title: Orchestration model — workorders dispatched to herdr agents in wt worktrees
description: The main session orchestrates; workers run in herdr tabs inside wt worktrees, driven by committed workorder files, and land via wt merge.
tags: [decision, orchestration, herdr, worktrunk, workorders]
status: stable
generated: { by: "human:skogix", at: "2026-10-09T00:00:00Z" }
---

# Context

skogai should be run as an orchestration setup. skogix and the main
Claude session discuss design and architecture. Implementation is handed
to worker agents as workorders. `TOOLS.md` left open whether `wt` or
`herdr worktree create` owns worktree creation, because both create
worktrees.

# Decision

- **Roles.** The main session is the orchestrator: it writes workorders,
  dispatches them, checks results and lands them. Workers implement exactly
  one workorder each.
- **wt owns the worktree lifecycle** (create, merge, remove). Branches are
  `wo/<NNNN-slug>`, and worktrees go in `.skogai/worktrees/` (user wt config).
  The merge pipeline is `wt merge`: squash, rebase, the `pre-merge` hooks in
  `.config/wt.toml`, then a fast-forward.
- **herdr owns panes and agents.** All workers run in a single herdr
  workspace labeled `workers`, with one tab per workorder. Agents are named
  `wo-<NNNN>`. Workspaces are not created per repo or per worktree.
  `herdr worktree create` is not used.
- **A workorder is a file.** `.skogai/workorders/NNNN-slug.md` has YAML
  frontmatter with `status: open|done|blocked`. It is committed to master
  before dispatch, so the worker's branch contains it. The worker appends a
  `## Report` section and sets the status. After the merge, the workorder
  and its report are in master's history.
- **Merging is automatic.** skogai is experimental, so a workorder that
  reaches `status: done` is landed without asking skogix first.
- **Default worker kind is `claude`.** Codex is the planned long-term kind
  (`WO_KIND=codex`). Claude workers run with `acceptEdits` and pre-allowed
  `git`/`openknowledge`. Any other command blocks, and the orchestrator
  sees the worker as `blocked`.

`bin/wo` implements this: `new`, `dispatch`, `status`, `land`.

# Consequences

- The open question in `TOOLS.md` is closed.
- Each workorder is reviewed only through its report and its diff before
  `wo land`. The `pre-merge` hook is the only automated gate.
- Worker permissions are passed as CLI flags in `bin/wo`, not set in
  `.claude/settings.json`. This keeps the orchestrator's own permissions
  unchanged.
