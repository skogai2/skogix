> Gate definition. The orchestrator passes this file's path to the reviewer;
> the reviewer reads it. The orchestrator does not.

# <ROLE>-<WHAT> — <short name>

Reviewer: `<role>` | Model: session (inherit)

**Trigger**: <which step runs this gate, and when>

**Context to pass**:
- <artifact path, and the sections by heading>
- <any other input, verbatim>

**Prompt**:
> "<The question the reviewer answers. Say what passes, what is a concern,
> and what blocks. Say what to mark DEFERRED instead of blocking.>"

**Verdicts**: <APPROVE> / <CONCERNS> / <REJECT>
*(plus NOT ASSESSED, naming the missing input — see `studio/docs/gates.md`)*
