---
name: router-file-convention
type: reference
permalink: skogai-routing/router-file-convention
---

<overview>
The v1 SkogAI routing document contract: YAML frontmatter plus one `<routes>`
XML block. This is the source of truth for document shape; `SKILL.md` keeps the
operating steps.
</overview>

<loading_model>
SKOGAI.md is not natively loaded by Claude Code. It is pulled into context the
same way any other file is: via a native `@`-link written inside a file Claude
Code does auto-load. In practice, a repo's `CLAUDE.md` is itself a router
document:

```markdown
---
permalink: skogai-routing/claude
type: router
---

<routes>

- @SKOGAI.md

</routes>
```

That `<routes>` block is the loading surface. This skill does not implement
loading; it defines what a router document looks like and how to
scaffold/validate one.
</loading_model>

<v1_shape>
A routing file has two parts: YAML frontmatter, then one XML block.

```markdown
---
permalink: skogai-routing/skogai
type: router
---

<routes>

- @MY/PATH/TO/DIR/ - list a directory and allow reading from the files within
- @SUBFOLDER/SKOGAI.md - link to another subfolder's router

</routes>
```

Frontmatter fields:

- `type` (required): always `router` for a routing file. The validator uses it
  to choose the schema/rules for the document body.
- `permalink` (recommended): a stable slug identifying this document,
  independent of its current file path.

<permalink_resolution>
A permalink is `reponame/filename` — a logical identifier, not a filesystem
path. `reponame` names a logical repo, project, or concept, not necessarily
the repo you're currently sitting in. The same `reponame/filename` value
resolves to whichever of these actually exists on the machine:

- `$HOME/reponame/filename.md` (repo checked out directly)
- `$HOME/.local/src/reponame/filename.md` (repo checked out under the shared
  src root)
- `./projects/reponame/filename.md` inside a monorepo (the `projects/<name>/`
  directory is treated as if it were its own future repo)

Example: this repo's own `SKOGAI.md` has permalink `skogai-routing/skogai`. If
`skogai-routing` is vendored as `./projects/skogai-routing/` inside another
repo, the file lives at `./projects/skogai-routing/SKOGAI.md` but the
permalink stays `skogai-routing/skogai` — not `parent-repo/projects/...`. The
permalink must stay stable across all three locations, including if the repo
is later moved between them (e.g. extracted from a monorepo into its own
`$HOME/skogai-routing` checkout).
</permalink_resolution>

`<routes>` body:

- A flat list, one entry per line: `- <path-or-@link> [- <description>]`.
- Blank lines are allowed, but every nonblank line must be a nonempty list
  entry.
- The opening and closing tags each occupy their own line.
- The opening tag has no attributes.
- No second XML block is allowed.
- Markdown prose and fenced examples may appear before or after the routes
  block.
- Entries may be `@`-links or plain paths; both are valid. `@`-links also
  trigger Claude Code auto-inclusion.
- Nothing in `<routes>` is auto-resolved beyond native `@`-linking. A plain
  path is a hint for Claude to read that file when relevant, not an automatic
  injection.

See `../examples/SKOGAI.md.example` for a router with directory/subfolder
routes and `../examples/CLAUDE.md.example` for a minimal router that points at
`@SKOGAI.md`.
</v1_shape>

<future_types>
`<routes>` is the only implemented type in v1. The intended family is typed
documents where a frontmatter `type` matches an XML root tag, such as `router`
with `<routes>`.

Do not invent additional types speculatively. `schemas/router.schema.json` is
deliberately scoped to `router`; extend it, or add sibling schemas, only when a
concrete second type is requested.
</future_types>
