---
type: Pattern
title: Roles — archetypes, not a roster
description: gamemaker's 49-agent studio hierarchy reduced to four archetypes and the rules for instantiating them for a domain.
tags: [studio, roles, agents, delegation]
status: draft
---

# Roles

gamemaker ships 49 named agents in three tiers. The tiers are the part
worth keeping; the names are a game's instance of them.

## Four archetypes

| Archetype | Owns | Decides | gamemaker examples |
|---|---|---|---|
| **Steward** | One concern across the whole project: *vision*, *technical soundness*, or *scope and schedule*. | Conflicts in its concern; phase-gate verdicts. | creative-director, technical-director, producer |
| **Lead** | One domain (a directory, a subsystem, a kind of artifact). | How work in the domain is split; review of domain work. | lead-programmer, narrative-director, qa-lead |
| **Worker** | One unit of work at a time. | Nothing binding outside its unit. | gameplay-programmer, writer, sound-designer |
| **Reviewer** | Nothing; it reads. | A verdict at a gate. | the director *at* a gate, qa-tester in adversarial mode |

A reviewer is a role played at a gate, not necessarily a separate agent:
gamemaker's directors spend most of their time as reviewers.

The three steward concerns map to skogai like this: **vision** is skogix
(the veto), **technical** is the orchestrator session's review of report and
diff, **scope** is whoever writes and orders the workorders.

## Tier is authority, not model

gamemaker's README says it plainly: tiers are seniority of role, not a
billing plan. Most of its agents inherit the session's model. Pin a bigger
model only where a role's judgement is the product (stewards at gates), and
never present a small-model pin as a saving without checking how the role is
started.

## Instantiating roles for a domain

1. Start with **one worker and one reviewer**. gamemaker's own default
   (`team.size: individual`) runs most pipelines with one or two agents.
2. Add a lead only when workers in one domain keep needing the same
   context or keep colliding.
3. Add a steward only when a concern needs a standing owner across
   domains. Most projects need the human as all three.
4. Each role gets a definition from `templates/role.md`: what it owns,
   the paths it may write, who it escalates to, and the skills it may use.

## Delegation rules

- Down: steward → lead → worker. Do not skip a tier for a complex decision.
- Across: consult, never decide in another's domain.
- Up: a disagreement goes to the shared parent; with none, to the steward of
  the concern; the human overrules anyone.
- Out: a role writes only inside its paths. Wider writes need delegation for
  that task, and the delegation is stated in the brief.

## Teams

gamemaker's `team-*` skills run a fixed pipeline of roles for one feature
(design → implement → review → test). The generic form:

```text
lead frames the unit → workers in parallel where independent
  → reviewer at the gate → lead closes or returns it
```

Before spawning, **announce the active set**: which roles this run will
spawn and which the pipeline names but will not, at the current team size.
A correctly collapsed run and a broken pipeline look the same otherwise.

In skogai, a team is a set of workorders dispatched together; a pipeline
step that waits for another is a workorder that names its dependency.
