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

## 2026-10-17 09:08 · turn 9d217961

**User**

> go ahead with first and the second should probably merge as best it  can with types etc in ~/skogai/dash-skogai with the type-setup etc.

**Assistant**

Both merges are written, but neither `.projects` folder is deleted: the auto-mode classifier blocked `rm`. Nothing is committed.

**1. claude-docs → `skogix/docs/repos/`**
- **`skogai-docs.md`**:
  - Has a new **Gotchas** section from `HANDOVER.md`, including the unsolved plain-prompt Skill error.
  - The location now says `~/.local/src/skogai-docs` is the only clone.
  - Its source list now includes `HANDOVER.md`.
- **`marketplace.md`**: corrected. `plugins/` only has `skogai-core` now, so docs lookup isn't live in any plugin. That's now listed there as an open issue.

**2. routing → `~/skogai/dash-skogai`**
- **`type/router.md`** (new, `status: draft`) brings the convention into the type layer:
  - it says the frontmatter `type` names the root block (`router` names `<routes>`);
  - it gives the entry format, when to use `@` versus a plain path, and the "no transitive bloat" rule;
  - it sets `owns: [<name>/SKOGAI.md]`. It's also listed in `type/index.md`.
- **`tmp/routing/`** holds the full skill copied as-is, plus a `README.md` saying what went where and noting the broken validator.
- **`TODO.md`** has 7 new `router` items for things I couldn't settle myself:
  - Decision 0006 says routing stays out of dash until the type layer works. Should `router` stay a draft or go back to `tmp/`?
  - Who owns `CLAUDE.md`?
  - Should "the frontmatter type names the root block" apply to every type?
  - Permalinks versus refs.
  - How to map the `lesson`/`workflow` schemas onto types.
  - The validators versus "don't rebuild okn".
  - Where the Claude Code references should live.
- **`skogix/docs/repos/skogai-routing.md`** now has a note pointing to the new location.

`mise run dash:check` reports the same 2 errors as before, both for `src/index.md`. I added nothing new there.

**For you to run** (the routing folder is tracked in the `skogix` repo):
```
! rm -rf ~/skogix/.projects/claude-docs
! git -C ~/skogix rm -r -q .projects/routing
```

Should I commit in both repos after that?

**Actions**

- Bash: `python3 - <<'EOF'`
- Bash: `rtk git -C /home/skogix/skogai/dash-skogai log --oneline -10; rtk git -C /home/skogix/skogai/dash-skogai status --short`
- Bash: `rtk find /home/skogix/skogai/dash-skogai -path '*/.git' -prune -o -path '*/node_modules' -prune -o -type f -print | head…`
- Read `/home/skogix/skogai/dash-skogai/TODO.md`
- Read `/home/skogix/skogai/dash-skogai/type/type.md`
- Read `/home/skogix/skogai/dash-skogai/type/type.schema.json`
- Read `/home/skogix/skogai/dash-skogai/type/index.md`
- Read `/home/skogix/skogai/dash-skogai/SKOGAI.md`
- Read `/home/skogix/skogai/dash-skogai/CLAUDE.md`
- Read `/home/skogix/skogai/dash-skogai/type/rule.md`
- Read `/home/skogix/skogai/dash-skogai/type/tool.md`
- Read `/home/skogix/skogai/dash-skogai/type/spec.md`
- Read `/home/skogix/skogai/dash-skogai/type/tool/okn.md`
- Read `/home/skogix/skogai/dash-skogai/src/index.md`
- Bash: `rtk ls -la /home/skogix/skogai/dash-skogai /home/skogix/skogai/dash-skogai/src; rtk grep -rn -i 'rout' /home/skogix/skog…`
- Read `.projects/routing/schemas/document.schema.json`
- Read `.projects/routing/schemas/frontmatter.schema.json`
- Read `.projects/routing/schemas/lesson.schema.json`
- Read `.projects/routing/schemas/workflow.schema.json`
- Read `.projects/routing/references/dynamic-output-blocks.md`
- Bash: `mkdir -p /home/skogix/skogai/dash-skogai/tmp/routing && cp -r /home/skogix/skogix/.projects/routing/SKILL.md /home/skogi…`
- Write `/home/skogix/skogai/dash-skogai/type/router.md`
- Write `/home/skogix/skogai/dash-skogai/tmp/routing/README.md`
- Edit `/home/skogix/skogai/dash-skogai/type/index.md`
- Edit `/home/skogix/skogai/dash-skogai/TODO.md`
- Bash: `mise -C /home/skogix/skogai run dash:check 2>&1 | tail -20; git -C /home/skogix/skogai check-ignore -v dash-skogai/tmp/r…`
- Bash: `rm -r /home/skogix/skogai/dash-skogai/tmp/routing/scripts/__pycache__ && rtk ls /home/skogix/skogai/dash-skogai/tmp/rout…`
- Bash: `python3 - <<'EOF'`

