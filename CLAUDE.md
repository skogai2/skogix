# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`skogix` is a personal configuration repo (owner: skogix). On the owner's machine it is checked out at **`/skogai`**, and almost every absolute path in it assumes that location (`/skogai/claude`, `/skogai/bin/claude`, `/skogai/plugins/skogdocs`, ...). In a cloud checkout (e.g. `/home/user/skogix`) those paths don't exist, so the launchers and settings won't work as-is. There is no app to build; the code is shell launchers, agent configs, and one plugin marketplace with tests.

## Layout and how the pieces connect

- **`mise.toml`** is the entry point. It sets `CLAUDE_CONFIG_DIR=/skogai/claude` and `SKOGAI_CONFIG_DIR`, and defines mise *wrappers* so that `claude` and `agy` resolve to `/skogai/bin/claude` and `/skogai/bin/agy`.
- **`bin/claude`, `bin/agy`** are clean-environment launchers: they `exec env -i` with a minimal allowlisted environment (`PATH=/usr/local/bin:/usr/bin`, zsh, a per-agent `ZDOTDIR`) so the agent doesn't inherit the user's shell state. If you add an env var an agent needs, it must be passed explicitly here.
- **Per-agent config dirs**, each isolated from the user's normal home config:
  - `claude/`: the project-scoped `CLAUDE_CONFIG_DIR`. Only `settings.json` and `shell/.zshrc` are tracked; everything else (credentials, sessions, caches) is gitignored by a deny-all `.gitignore`. `shell/.zshrc` is the zsh used by the Bash tool (activates mise shims).
  - `agy/`: the same pattern for Google Antigravity (`settings.json`, `shell/.bashrc`, `shell/.zshrc`).
  - `codex/`: a Codex CLI baseline. `codex/run` sets `CODEX_HOME` to that directory and launches from `codex/workspace/`. See `codex/README.md`.
  When you add a file that should be tracked in one of these dirs, also add a `!` exception to that dir's `.gitignore`.
- **`plugins/skogdocs/`** is a plugin marketplace (`code-docs-tools`) with two plugins that answer questions from a local copy of the official docs, not from memory: `code-docs-lookup` (Claude Code) and `agy-docs-lookup` (Antigravity). `claude/settings.json` registers it as a directory marketplace, and `.agents/plugins.json` registers the agy plugin for Antigravity. **Read `plugins/skogdocs/HANDOVER.md` before changing it**: it lists the architecture, open problems, and many hard-won gotchas (for example, `${CLAUDE_PLUGIN_ROOT}` is not exported to Bash, `--bare` skips plugins, and SIGPIPE under `pipefail`).
- **`scripts/claude/hooks/`** holds herdr-managed hook scripts. Don't edit them; herdr overwrites them on update. Note that `claude/settings.json` references the hook as `/skogai/claude/hooks/herdr-agent-state.sh`, not at this path.
- **`.skogai/`** is the knowledge and notes area:
  - `decisions/`: numbered decision records in OKF format (YAML frontmatter with `type: Decision`, `status`, `generated`, `sources`). Several of them describe tooling that lives in the separate `skogai2/skogai` repo (`bin/wo`, `.skogai/workorders/`, wt/herdr orchestration), not in this repo.
  - `personal/`: skogix's own docs and stories. `personal/docs/definitions.md` and `user.md` explain skogix's vocabulary.
  - `repos/`: git submodules (aube, demand, usage, hk, pitchfork). They aren't initialised by default (`git submodule update --init`). `.gitmodules` lists `hk` twice.
- **`mise.md`** contains reference notes on `mise bootstrap` and dotfiles, not configuration.

## Commands

Lint shell scripts with hk (shellcheck, shellharden, shfmt), configured in `hk.pkl`:

```bash
hk check --all
```

```bash
hk fix --all
```

skogdocs plugin tests (run from `plugins/skogdocs/`). The tests call `claude` by name, and under the `/skogai` Bash tool `PATH` is only `/usr/bin:/usr/local/bin`, so prepend `~/.local/bin` first:

```bash
tests/offline.sh        # Claude Code plugin: docs sync, lookup scripts, env reference, manifest, install (needs network)
```

```bash
tests/offline-agy.sh    # Antigravity plugin offline checks
```

```bash
tests/environment.sh    # one isolated Claude run, judged from its events
```

```bash
tests/run-all.sh        # offline.sh + environment.sh
```

```bash
tests/agent.sh          # real `claude -p` run; calls the API and costs money (~$0.10). PROMPT=... to change the prompt
```

The test stages are sequential sections inside each script (stage 01 builds the docs cache that later stages use), so there is no single-test runner; set `TEST_TMP` to reuse a cache between runs. When stage 03 fails because upstream changed the env-var table, regenerate the reference and commit it, because the committed file must match the generator's output:

```bash
python3 tools/build-env-reference.py
```

Run outputs go to `/tmp/code-docs-lookup-runs/`. Each one contains a copy of the login, so delete old runs.

## Conventions

- In decision 0005, skogix decided that origin is the only source of truth: local checkouts are disposable, and work counts once it is pushed.
- Commit messages in history are short, prefixed by area (`claude: ...`, `skogdocs: ...`, `repos: ...`).
