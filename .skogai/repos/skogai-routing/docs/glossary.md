---
title: glossary
permalink: skogai-routing/glossary
type: reference
---

<quick_start>

routing focuses a lot on the concept of ownership and choices. with such short time to express important information - the words we use is even more important than usual

this repo defines a convention for how files declare responsibility over other files, and how an agent walks that structure to find context.

</quick_start>

<definitions>

```ownership
the file, concept, or tag a given file belongs to or is the responsibility of. a file may have more than one owner.

_avoid_: parent, manages, responsible for
```

```routing-file
a file named in all-caps (e.g. `SKOGAI.md`, `CLAUDE.md`, `MEMORY.md`, `HISTORY.md`, `SPECS.md`) that owns other files or concepts and acts as a choice portal — it links, references, or injects the context it owns. all-caps naming is the formal marker of this type, not just a convention: a lowercase file performing the same function is not a routing file.
_avoid_: caps file, router
```

```leaf
a file with an owner that itself owns nothing — it ends the ownership chain.
_avoid_: child, managed file
```

```root
when talking paths, projects and relative positions of files - the "root" is always defined from the closest `.git` folder, walking up the file tree towards `/`. it is also the one routing file at a repo's git root (`SKOGAI.md`, `CLAUDE.md`, or `AGENTS.md`). it is the only file with no in-graph file-owner. its `permalink` frontmatter records the repository's own external identity — the name youd use to find or reference this repo in the first place (e.g. `myproject/skogai`) — not a parent file.
_avoid_: intro agent file (fine as description, not as the canonical name)
```

```ownership-(relationship)
non-transitive. if a owns b and b owns c, a does not thereby own c. every file's chain is exactly one hop to its direct owner(s); walking further up or down the graph is a separate lookup, never implied.
_avoid_: inheritance, cascading ownership
```

</definitions>
