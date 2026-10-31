# Codex baseline

A local configuration playground for `/skogai`. Run from any directory:

```sh
/skogai/codex/run login
/skogai/codex/run
```

The launcher starts in `codex/workspace/`, uses `codex/` as `CODEX_HOME`,
stores SQLite state in `codex/state/`, and uses `codex/tmp/` for temporary files.
It avoids the shared Codex daemon. Your normal `~/.codex` configuration,
sessions and file-based login are separate; sign in once for this environment.
No credentials or plugins are copied into it.

## What to edit

- `config.toml`: the baseline Codex settings. No model or provider is pinned yet.
- `AGENTS.md`: instructions for work in this directory and its playground.
- `workspace/`: disposable experiments, ignored by Git.
- `run`: environment setup and CLI launcher; all arguments pass through.

For example, work on the main repository using this configuration:

```sh
/skogai/codex/run -C /skogai
```

Or check configuration without starting an agent:

```sh
/skogai/codex/run features list
```

## Scope

This is configuration separation, not an OS sandbox. The baseline enables full
filesystem/network access and disables approval prompts. The launcher inherits
your environment (including API keys, proxies and PATH) and keeps your real HOME.
Tools can still use their ordinary user configuration. Codex may also load
applicable repository instructions, trusted project configuration, system policy
and automatically discovered integrations outside this folder. For tighter
experiments, control those inputs explicitly.

Generated Codex files are ignored by default; only the baseline files are allowed
into Git. To start a fresh experiment without removing this one, copy the tracked
baseline files to another directory and launch its `run`. To reset settings only,
restore `config.toml` from Git; this preserves login and session history.

Validated with Codex CLI 0.165.0. The executable/toolchain is shared, so this does
not pin the CLI version or installed build dependencies.

References: [environment variables](https://learn.chatgpt.com/docs/config-file/environment-variables)
and [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).
