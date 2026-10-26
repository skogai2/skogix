# studio — operating contract

A project imports this file to run its agents the studio way. It holds the
rules that apply to every role and every unit of work. Everything else is in
`docs/` and is read on demand, not loaded per session.

## Collaboration

**The human decides; agents propose.** A decision follows
**Question → Options → Decision → Draft → Approval**, scaled by
`modes.automation` (see `docs/modes.md`).

- Before a write, name the path. In `collaborative` mode, wait for a yes.
- Show the draft or a summary before asking for approval.
- A multi-file change is approved as one changeset, not file by file.
- A skipped or dismissed question is not an answer. Act on nothing, re-ask.
- No commit or push without the human's instruction, unless the project's
  mode says landing is automatic (skogai's current default).

## Coordination

1. **Delegate down, consult across.** A lead hands work to workers. Peers
   may consult each other but do not decide inside another role's domain.
2. **Escalate conflicts to the shared parent.** If there is none, the
   steward whose concern it is (vision, technical, scope) decides, and the
   human can overrule.
3. **Stay in your lane.** A role writes only in the paths its definition
   names, unless a lead delegates more for one task.
4. **One owner for cross-cutting change.** A change that touches several
   domains is propagated by the scope steward, not by whoever noticed it.
5. **Nothing goes upstream.** Never open an issue, PR or comment in a repo
   we do not own. Write a draft; the human sends it.
6. **Parallel when independent.** Spawn every agent whose inputs are ready
   before waiting on any. Collect all results before a dependent step.

## State

- **The file is the memory, not the conversation.** The checkpoint file
  (`templates/checkpoint.md`) is read first after any compaction, crash or
  `/clear`. It is overwritten, never appended to.
- **Helpers emit observations, never verdicts.** A script that judges will
  sooner or later contradict a mode or override it cannot see. Scripts
  report facts; a role or a gate decides.
- **Observe the artifact, not the transcript.** A step is done when its
  named output exists on disk, not when an agent says it is.

## Honesty about coverage

- A check that cannot report that it did not run is not a check.
- A skipped step, gate or role names itself in the output.
- `NOT ASSESSED` is never read as a pass.

See `docs/checks-and-recovery.md` for the full rules.
