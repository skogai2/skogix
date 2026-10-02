# SkogAI — The Broadest Description

## A north star to return to

SkogAI is an attempt to make a personal computer into a coherent, inspectable environment where a human and multiple AI agents can work together on real projects without surrendering ownership, context, or control.

It is not fundamentally a chatbot, a model wrapper, a web dashboard, a single CLI, a RAG database, an MCP server, or an orchestrator. Those have all been useful implementation surfaces. The enduring idea is the system around them:

> **A local-first, Git-centered, context-routed operating environment for human and agent work.**

The desired experience is simple: identify a piece of work, create a safe and intelligible place for it, give the right agent only the context and authority it needs, let it act, and receive a result that can be inspected, tested, accepted, rejected, or continued.

Everything else exists to make that loop trustworthy.

---

## 1. Why SkogAI exists

Ordinary AI tools tend to treat every interaction as an isolated conversation. They know too little about the real project, or they accumulate so much indiscriminate context that the useful signal disappears. Their actions often happen inside opaque sessions, under the human's identity, with unclear authority and weak continuity.

SkogAI tries to solve the larger workstation problem:

- How does an agent know what matters here?
- How is work isolated from unrelated work?
- How can several agents have distinct identities, skills, permissions, and responsibilities?
- How does useful experience survive a session without turning into an unbounded prompt?
- How can the human see what happened and remain the final authority?
- How can the system change tools and model providers without losing its own identity?

The answer is not “one smarter agent.” It is an environment with durable structure.

---

## 2. The central lifecycle

The clearest expression of SkogAI is this lifecycle:

```text
intent or task
  → repository selection
  → isolated worktree or workspace
  → routed, task-relevant context
  → explicit execution contract
  → provider or agent run
  → observable result
  → validation
  → Git diff / commit / issue / pull request
  → useful experience captured as memory, knowledge, or a lesson
```

The implementation may use a CLI, shell scripts, containers, UNIX users, tmux, MCP, GitHub, local models, cloud models, or an external orchestrator. None of those is the lifecycle itself.

The lifecycle is complete only when a result is reproducible and inspectable. A design document, running service, successful connection, or agent report is not enough on its own.

---

## 3. The durable principles

### Local first

The workstation is the center of gravity. Cloud services may extend it, but they do not own the project, the identity, the knowledge, or the workflow. The system should remain understandable and useful when individual providers disappear.

### Git is the shared language

Git provides identity, history, scope, comparison, recovery, and review. A diff is the preferred boundary between an agent's internal process and the rest of the system: event in, diff out.

Not every operation must literally be a Git diff, but durable project changes should converge on inspectable artifacts—commits, patches, issues, pull requests, decisions, or versioned documents.

### Context is constructed, not accumulated

More true information is not automatically better context. SkogAI follows a context-dilution principle: irrelevant but reasonable information can make an agent worse.

Context should therefore be selected progressively:

- the root router identifies where knowledge lives;
- routes reveal the relevant domain;
- workflows describe the current process;
- references explain facts and constraints;
- lessons add experience when their conditions match;
- tools and scripts act only when needed.

The goal is not maximum context. It is maximum useful signal per token and per decision.

### Structural security over promises

Agents should not merely be instructed to behave safely. Wherever practical, safety should come from operating-system and repository structure:

- distinct identities;
- proper UNIX users, homes, groups, and permissions;
- isolation by default;
- explicit shared spaces;
- scoped credentials;
- protected human keys and home state;
- observable processes and durable logs.

Agents are named participants in the system—not invisible root daemons and not arbitrary subprocesses wearing the human's identity.

### Provider neutrality

Claude, Codex, local models, GPTMe, Goose, and future providers are workers behind contracts. They may retain their own native loops, authentication, transcripts, and tool behavior, but SkogAI should own task identity, context construction, execution scope, results, and project history.

### Evidence outranks claims

Current code outranks prose. Tests outrank intended behavior. Reproducible execution outranks reports that something once worked.

Capabilities should be described precisely:

- proposed;
- experimental;
- implemented;
- tested;
- integrated;
- operational;
- removed;
- superseded;
- historical.

### The human remains sovereign

Agents may be proactive, opinionated, and capable of disagreement. They may plan, act, test, document, and improve the system. The human retains final authority over goals, trust, permissions, architecture, and acceptance.

---

## 4. The system SkogAI tried to become

### A workstation control plane

The `skogai` interface was intended as the stable entrypoint into a larger collection of tools: projects, repositories, worktrees, configuration, agents, tasks, memory, services, and diagnostics.

The interface should organize choices rather than duplicate every underlying tool. Git, Worktrunk, tmux, systemd, Podman, Ansible, GitHub, and model CLIs may continue doing what they already do well.

### An agent ecosystem

SkogAI has repeatedly imagined specialized agents rather than one universal personality:

- project and Git agents;
- dotfile and workstation agents;
- documentation and librarian agents;
- task and planning agents;
- infrastructure and service agents;
- local, strict, small-context agents;
- large-context agents for exploration;
- personal or relational agents with persistent identity.

Each agent may have an identity, purpose, values, relationships, skills, tools, goals, preferences, workspace, journal, and knowledge. The orchestrator's job is to assemble the right participants and boundaries for the work—not to impersonate all of them.

### A knowledge operating system

SkogAI treats documentation as part of execution, not an afterthought. Documentation can tell both humans and agents what exists, what is true, what is decided, and how work should proceed.

Its durable knowledge surfaces have included:

- decisions and ADRs;
- principles and conventions;
- lessons learned from work;
- workflows;
- patterns and references;
- templates;
- skills as executable knowledge;
- tools and scripts;
- project maps and histories;
- people and agent identities;
- experiments and incubators.

Knowledge and memory are related but distinct:

- **Knowledge** is durable, reviewed, reusable, and meant to remain true.
- **Memory** is evolving experience: observations, session history, relationships, and potentially useful context.

Knowledge is the lighthouse; memory is the weather report.

### A routing system

Routers such as `SKOGAI.md` exist to keep the active context small while making the larger knowledge space discoverable. Routing should reveal ownership as well as location: which file, repository, or component is authoritative for a concept.

This is progressive disclosure applied to an entire workstation and repository fleet.

### A task and orchestration layer

Tasks should be durable objects with identity, state, dependencies, ownership, evidence, and completion criteria. They may originate locally or in GitHub, and they may be handled by a person, one agent, or a coordinated group.

The orchestration layer should answer:

- what is being attempted;
- why it matters;
- where it may act;
- which context applies;
- which provider or agent should run;
- what success looks like;
- what happened;
- and what remains unresolved.

### A memory and retrieval layer

RAG, knowledge graphs, Markdown search, embeddings, MCP memory tools, and databases have all been explored as ways to retrieve useful prior context.

The durable requirement is smaller than any of those implementations: remember selectively, retrieve intentionally, distinguish observation from fact, preserve provenance, and never let opaque memory silently override current project truth.

### A service and integration fabric

MCP, APIs, tunnels, DNS, containers, systemd services, and remote access extend the local environment. Their role is to make capabilities reachable and composable while preserving ownership, authentication, monitoring, and recovery.

They support SkogAI; they are not SkogAI's center.

### A project-intelligence layer

Because the project spans many repositories and experiments, SkogAI also needs a bird's-eye model of itself:

- what is current;
- what changed;
- which repository owns what;
- what is proven versus merely claimed;
- where implementations overlap or contradict one another;
- what was removed or became historical;
- which next action creates the most global progress.

Without this layer, local activity can look like progress while the overall system becomes less coherent.

---

## 5. SkogAI notation

The notation is one attempt to give the system a compact language for references, intent, identity, composition, choice, relation, and transformation.

Its symbols have included:

- `$` — reference or useful reality;
- `@` — intent or action;
- `_` — existence;
- `=` — identity;
- `|` — choice;
- `[]` — similarity or contextual grouping;
- `{}` — difference;
- `.` — belonging;
- `:` — following or relation;
- `->` — becoming;
- `*` — composition.

The deeper intention matters more than the exact parser: configuration, prompts, memory, context, and actions should be addressable as composable data rather than buried in application-specific interfaces.

“Everything is a JSON object” expressed the same instinct from another direction: make state explicit, inspectable, transformable, and portable.

---

## 6. What SkogAI is not

SkogAI is not identical to any of these:

- the Python, F#, Bash, or argc CLI implementation;
- `core`, `skogcli`, `skogcli2`, `skogharness`, or `skogwork`;
- Paperclip, GPTMe, Goose, Claude Code, Codex, or any provider;
- Basic Memory, Hindsight, FAISS, a knowledge graph, or one database;
- MCPHub, one MCP server, or the MCP protocol;
- Podman, Docker, Ansible, systemd, Cloudflare, Tailscale, or one deployment topology;
- tmux, i3, Kitty, Neovim, or a particular interface;
- one schema, one router version, one plugin format, or one repository layout.

Those are implementations, dependencies, experiments, or habitats. They may be kept, replaced, split, merged, or abandoned without invalidating the project.

SkogAI fails only if it loses the coherent human-agent work environment it was trying to create.

---

## 7. Recurring experiments and what they were seeking

Across its different eras, SkogAI has repeatedly tried to solve the same problems through different forms:

| Experiment | Underlying need |
|---|---|
| Central CLI and argc command trees | One understandable control surface |
| Specialized agents and personas | Division of cognitive labor and persistent identity |
| Worktrees, containers, UNIX users | Safe and comprehensible execution scope |
| Routers and progressive disclosure | High-signal context without prompt bloat |
| RAG, graphs, Basic Memory, lessons | Useful continuity beyond a single session |
| MCP and service gateways | Provider-independent capability access |
| tmux rooms, channels, chat, Delta Chat | Persistent human-agent presence and communication |
| GitHub issues, local tasks, gptodo | Durable work identity and lifecycle |
| Ansible, bootstrap, Podman quadlets | Reproducible workstation and services |
| Project-intelligence reports | Global coherence across many repositories |
| SkogAI notation and JSON configuration | A compact, composable language for the environment |

The implementations sometimes collided because several experiments attempted to own the same need. The recovery task is not to preserve every experiment. It is to assign each enduring need one clear authority and contract.

---

## 8. The minimum viable SkogAI

If everything had to be rebuilt from a small, honest base, SkogAI would need only:

1. **One entrypoint** that can identify a project and a task.
2. **One isolation mechanism** that creates a safe worktree or workspace.
3. **One routing convention** that supplies only authoritative, relevant context.
4. **One provider-neutral execution record** containing the request, scope, provider, events, outcome, and errors.
5. **One validation path** that tests the result and exposes the resulting diff.
6. **One durable task record** linking intent, execution, evidence, and completion.
7. **One selective continuity mechanism** that can capture and retrieve a lesson without becoming project truth by accident.
8. **One status view** that says what is current, broken, experimental, and historical.

Everything else can grow from that without pretending to be foundational.

---

## 9. The first proof to recover

The immediate north-star proof is deliberately narrow:

```text
select repository and task
  → create isolated worktree
  → resolve SKOGAI.md and task-specific routes
  → run one agent under an explicit identity and permission boundary
  → produce one controlled change
  → run deterministic validation
  → inspect and record the Git diff
  → capture one useful lesson with provenance
  → retrieve that lesson in a later relevant task
```

This should work from a clean checkout and fail visibly when any boundary is missing.

Until that proof exists, adding another orchestrator, memory system, transport, dashboard, or agent framework is exploration—not completion.

---

## 10. A recovery rule

When SkogAI becomes confusing, ask these questions in order:

1. What human intention are we serving?
2. What durable task represents it?
3. Which repository and worktree own the change?
4. Which source owns the required context?
5. Which agent identity and permissions are appropriate?
6. What explicit execution contract is being invoked?
7. What observable artifact will prove the result?
8. What should become durable knowledge, and what should remain temporary memory?
9. Which current component is authoritative for each step?
10. Can the whole path be reproduced without relying on hidden workstation state?

If a component cannot answer one of those questions, it is probably supporting infrastructure or an experiment—not the center of SkogAI.

---

## 11. Broadest short description

> **SkogAI is a local-first, Git-centered operating environment for collaborative human and AI work. It turns intent into isolated project work, constructs only the context required for that work, assigns it to agents with explicit identities and permissions, and returns observable, testable, versioned results. Around that core it develops durable knowledge, selective memory, routing, skills, tasks, services, and project intelligence so that useful experience compounds without sacrificing clarity or human control. Its tools and providers are replaceable; its enduring purpose is to make agent work coherent, inspectable, secure, and genuinely part of the workstation.**

---

## 12. The line to return to

When everything else explodes:

> **Intent in. Right context. Safe place. Named agent. Observable work. Diff out. Knowledge retained. Human in control.**
