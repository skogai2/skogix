---
type: Pattern
title: Checks and recovery — honest coverage, observed artifacts
description: The five check-authoring obligations from gamemaker's skill-authoring rule and its error-recovery protocol, which are domain-free already.
tags: [studio, checks, gates, error-recovery, hooks]
status: draft
---

# Checks and recovery

These two parts of gamemaker needed almost no translation. They are the
most transferable thing in it.

## Writing a check

**A check that cannot report that it did not run is not a check.** The
recurring failure: a step that could not run produces the same output as a
step that ran and found nothing, and the permissive reading wins because it
lets work proceed.

1. **Every gating verdict has a "could not assess" value**, ranked above
   pass and below fail, and the report says which reason applied.
2. **An absent value never defaults to the permissive one.** Before
   defaulting, check who writes the key. A key with a reader and no writer
   takes its default on every run, so the default *is* the behaviour.
3. **A skipped step announces itself** in the output, by name.
4. **Never assert what you cannot source**, and wire the gap into the
   verdict: `NOT SOURCEABLE — <what> is not covered by <path>` forces
   `NOT ASSESSED`, it does not sit beside a pass.
5. **Derive the covered set; do not enumerate it.** An allowlist is silent
   about everything added after it. If the set cannot be derived, keep the
   list and write down why.

Two more:

- **Assert something that cannot be true by accident.** A check for
  "unity" passes on "community".
- **A gate you have not watched fail is not a gate.** Break what it guards,
  see it fail, restore.

The test: *if this step silently did not run, what would the output look
like?* If the answer is "the same", it is not finished.

## Recovering from a failed agent

**Trigger 0: observe the artifact, not the transcript.** Before reading an
agent's answer, check that the path its brief named exists. A missing
artifact is a failed step however fluent the reply is. Recovery is cheap:
resume the agent (do not respawn), name the unmet contract, and say that
"I could not write it" is an acceptable answer and silence is not.

Then, for BLOCKED or errors:

1. Surface it at once: `<role>: BLOCKED — <what is missing, where expected>`.
2. Decide whether later steps depend on it. If so, stop there.
3. Offer: skip and note the gap / retry narrower / stop and fix.
4. Always produce a partial report. Never fill a skipped role's part with
   your own content.
5. **A skip does not clear the block.** The run's final verdict names the
   gap; it is not COMPLETE.

In skogai this is how the orchestrator reads a worker: the workorder's
`status`, its `## Report` and its diff, never the worker's last message.

## Hooks gamemaker used, as candidates

| Hook | Job | Generic form |
|---|---|---|
| `session-start.sh` | print the checkpoint, detect gaps | print the checkpoint region |
| `pre-compact.sh` | remind to write state | same |
| `validate-commit.sh` / `validate-push.sh` | message format, tests, protected paths | `pre-merge` hook in `wt` |
| `validate-read.sh` | refuse whole reads of large docs | read-by-section fence |
| `validate-write.sh` | refuse writes outside a role's paths | role path fence |
| `log-agent.sh` / `log-agent-stop.sh` | audit trail of subagents | hook-tap (`.skogai/logs/`) |

Per decision 0007, prefer a structural fence (permissions, separate
worktree, separate user) over a hook, and a hook over a written rule.
