# Codex configuration playground

This directory is a baseline for experimenting with Codex configuration.

- Keep reusable configuration, instructions and documentation in version control.
- Put disposable experiments and generated artifacts in `workspace/`.
- Keep credentials, session history, databases and logs untracked.
- Prefer changes inside this directory unless the task calls for repository changes.
- Do not import the user's normal Codex configuration, credentials or plugins
  automatically. Add integrations deliberately so the baseline stays understandable.
- This is configuration isolation, not filesystem or network isolation.
