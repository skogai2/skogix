## 2026-10-17 08:21 · turn a89718ae

**User**

> hello claude!

**Assistant**

Hi! What are we working on?

## 2026-10-17 08:26 · turn c03ea134

**User**

> well id like your help to "summarize and merge back in" some smaller projects which only got a short starting setup and moved. @.projects/claude-docs/ @.projects/routing/ to begin with i belivee

**Assistant**

The two projects need different handling.

**`claude-docs`: an exact duplicate, safe to fold in and delete.**
- It's a clone of `~/.local/src/skogai-docs` at the same commit (8836fc0), matches origin, and the files are identical. The only extra is a `.skogai/logs/` folder.
- The one thing worth keeping is `HANDOVER.md`'s "Gotchas" list. For example: `CLAUDE.md` files above the working dir still load when `CLAUDE_CONFIG_DIR` is set; `--bare` skips installed plugins; `${CLAUDE_PLUGIN_ROOT}` isn't exported to the Bash tool; piping into `head` under `pipefail` exits 141. None of this is recorded in `docs/` yet.
- `docs/repos/skogai-docs.md` and `marketplace.md` are out of date:
  - They say the clone lives at `~/claude-docs`, but it's in `.projects/` now.
  - They say marketplace has a `code-docs-lookup` plugin. It doesn't anymore: `marketplace/plugins/` only holds `skogai-core`, so the docs-lookup feature currently exists nowhere live.

**`routing`: the only copy of its work, so it can't just be deleted.**
- It's a newer skill than the one in `~/.local/src/skogai-routing`, which is still the older skogfences seed. This one has the `type: router` + `<routes>` v1 convention, the `CLAUDE.md` routing rules, the schemas and the validators. It doesn't exist anywhere else on disk; it was only ever committed here (31050be).
- The validator is broken: its self-check fails with `Unresolvable: document.schema.json`. Separately, `router.schema.json` expects `objective`/`routing` sections, which contradicts the `<routes>` shape the docs describe.
- A skogai decision (0006, "start without routing or repos") keeps routing parked for now.

**What I suggest:**
1. **claude-docs:** add the gotchas, the plain-prompt open problem and the corrected location to `docs/repos/skogai-docs.md`, and fix the `code-docs-lookup` line in `marketplace.md`. Then `rm -rf .projects/claude-docs`, which loses nothing.
2. **routing:** commit it into `~/.local/src/skogai-routing` on a branch (`v1-router`), replacing `skills/skogai-routing/`. That repo is where it would naturally have moved. Then update `docs/repos/skogai-routing.md` with a summary that notes the broken validator and decision 0006, and remove `.projects/routing`.

Should I go ahead with both? Or for routing, would you rather keep it in `skogix` and only write the summary?

**Actions**

- Bash: `cd /home/skogix/skogix/.projects/routing; rtk git log --oneline 2>/dev/null | head; rtk find . -type f | head -100; rtk …`
- Bash: `cd /home/skogix; rtk ls -a skogai skogai/.skogai .local/src/marketplace 2>&1 | head -60; rtk find skogai .local/src/mark…`
- Bash: `cd /home/skogix; rtk ls .local/src/marketplace/plugins skogai/plugins skogix/docs skogix/wip skogix/.skogai 2>&1; rtk re…`
- Bash: `cd /home/skogix; find .local/src/marketplace -path '*/.git' -prune -o -type f -print | grep -v node_modules | head -60; …`
- Bash: `cd /home/skogix/skogix/docs; rtk read repos/skogai-routing.md repos/skogai-docs.md repos/marketplace.md repos/index.md d…`
- Bash: `cd /home/skogix; rtk ls -d .local/src/skogai-routing claude-docs .local/src/skogai-docs 2>&1; rtk ls .local/src/marketpl…`
- Bash: `cd /home/skogix; P=skogix/.projects; echo "== claude-docs vs skogai-docs"; rtk git -C .local/src/skogai-docs log --oneli…`
- Bash: `cd /home/skogix; find / -xdev -name validate_router.py -not -path '*/proc/*' 2>/dev/null | rtk grep -v '/skogix/.project…`
- Bash: `cd /home/skogix/skogix/.projects/routing; cat references/router-file-convention.md references/claude-md-routing-rules.md…`
- Bash: `cd /home/skogix; f=$(find skogai/.skogai skogai/docs -name '0006-start-without-routing*' 2>/dev/null | head -1); echo $f…`
- Bash: `cd /home/skogix; cat skogai/tmp/okn-survey/sandbox-core/bundle/decisions/0006-start-without-routing-or-repos.md | head -…`

