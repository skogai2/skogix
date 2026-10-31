# code-docs-tools

Official documentation lookup plugins for **Claude Code** (`code-docs-lookup`) and **Google Antigravity** (`agy-docs-lookup`). Each plugin answers questions from a local copy of its official documentation rather than from memory.

## Install (Claude Code)

```sh
claude plugin marketplace add /skogai/plugins/skogdocs
claude plugin install code-docs-lookup@code-docs-tools
```

Use it with `/code-docs-lookup:ask <question>` or `/code-docs-lookup:claude-code-docs <question>`.

## Install (Google Antigravity / `agy`)

```sh
agy plugin install /skogai/plugins/skogdocs/plugins/agy-docs-lookup
```

Or register it in a workspace `.agents/plugins.json`:

```json
{
  "entries": [
    {
      "path": "plugins/skogdocs/plugins",
      "include_only": ["agy-docs-lookup"]
    }
  ]
}
```

Use it with `/agy-docs <question>` (or ask any Antigravity question naturally).

Status and architecture notes are in [HANDOVER.md](HANDOVER.md).

## Tests

```sh
tests/offline.sh        # Claude Code offline checks: docs cache, scripts, reference, plugin, install
tests/offline-agy.sh    # Antigravity offline checks: docs cache, scripts, reference, strict validate, install
tests/environment.sh    # one Claude run in a fresh config dir; checks the run's own events
tests/agent.sh          # one real `claude -p` run; calls the API (costs money)
```
