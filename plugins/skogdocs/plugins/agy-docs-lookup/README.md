# agy-docs-lookup

An Antigravity plugin that answers Google Antigravity questions (CLI, App, IDE, extensions, Python SDK, settings, flags, slash commands, skills, rules, plugins, hooks, MCP, sidecars, sandbox, and permissions) from a local, offline-searchable copy of the official docs at `https://antigravity.google/docs`.

## Install

```sh
agy plugin validate --strict /skogai/plugins/skogdocs/plugins/agy-docs-lookup
agy plugin install /skogai/plugins/skogdocs/plugins/agy-docs-lookup
```

Or register for a workspace via `.agents/plugins.json`:

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

## Usage

Invoke `/agy-docs <question>` in chat, or ask any question about Antigravity features, configuration, or CLI usage to trigger the `agy-docs` skill automatically.

## Scripts

- `scripts/sync-docs.sh [-c cache_dir] [--force]`: Syncs all official Antigravity doc pages (`.md`) from `https://antigravity.google/sitemap.xml` into `${AGY_DOCS_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/agy-docs}`.
- `scripts/search-docs.sh [-c cache_dir] [-n max_pages] [-r] <term> [more terms...]`: Searches cached pages for all given terms.
- `scripts/show-doc.sh [-c cache_dir] [-H] <slug>`: Prints a cached page (or its headings with `-H`) and its canonical `source:` URL.
