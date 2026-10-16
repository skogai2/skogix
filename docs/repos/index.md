# Repos

Per-repo pages so an orchestrator can learn a repo's role, state and
workorder caveats without reading a full survey report. Each page cites
its survey workorder and [decision 0003](/decisions/0003-repo-roles.md)
in `sources`, and goes stale 30 days after it was written (see
[decision 0004](/decisions/0004-knowledge-lifecycle.md)).

## Orchestrator and home repos

* [skogai](skogai.md) — the orchestrator itself.
* [claude](claude.md) — agent home, future implementer, not yet a dispatch target.
* [dot](dot.md) — agent home, future implementer, not yet a dispatch target.
* [config](config.md) — machine-configuration docs, live at `~/.config/skogai`.
* [skogix](skogix.md) — skogix's personal repo, not a workorder target.

## Active orchestration-adjacent repos

* [dash-skogai](dash-skogai.md) — source for the shared `/skogai` workspace.
* [dot-skogai](dot-skogai.md) — source for the user-level `~/.skogai`, empty until an installer exists.
* [marketplace](marketplace.md) — Claude Code plugin marketplace, supersedes skogai-docs.
* [skogai-cli](skogai-cli.md) — the skogai CLI, mid-rework.
* [okn](okn.md) — the Open Knowledge CLI, validates this bundle.
* [open-knowledge-plugin](open-knowledge-plugin.md) — OKF toolchain, live-installed plugin source.

## Design docs / seeds

* [skogai-git-workflow](skogai-git-workflow.md) — turn-based editing protocol proposal.
* [skogai-routing](skogai-routing.md) — routing-file convention and skill.

## Parked or superseded

* [skogai-fleet](skogai-fleet.md) — parked "nelson" orchestration skill rewrite.
* [skogai-docs](skogai-docs.md) — deprecated, superseded by marketplace.
