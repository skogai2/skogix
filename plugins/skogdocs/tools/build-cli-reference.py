#!/usr/bin/env python3
"""Build the Antigravity CLI reference from the cached cli/reference.md docs page.

Usage: build-cli-reference.py <cli/reference.md> > references/cli-reference.md

Reads the "## Configuration keys (`settings.json`)", "## Command-line flags",
and "## Core slash commands" tables from cli/reference.md, converts relative
docs links to absolute https://antigravity.google/docs/ URLs, and writes a
consolidated offline reference.
"""
import collections
import re
import sys

DOCS = "https://antigravity.google/docs/"
PAGE_URL = DOCS + "cli/reference"

SETTINGS_ROW = re.compile(r"^\| \*\*`([A-Za-z0-9_]+)`\*\* \| ([^|]+) \| ([^|]+) \| (.*) \|$")
FLAG_ROW = re.compile(r"^\| (\*\*`--[^|]+) \| ([^|]+) \| (.*) \|$")
SLASH_ROW = re.compile(r"^\| ([^|]+) \| ([^|]+) \| ([^|]+) \| (.*) \|$")


def section_lines(lines, start_heading, end_heading):
    start = lines.index(start_heading)
    end = lines.index(end_heading) if end_heading else len(lines)
    return lines[start:end]


def absolute(text):
    return (
        text.replace("](/docs/", "](" + DOCS)
        .replace("](/schemas/", "](https://antigravity.google/schemas/")
        .replace("](#", "](" + PAGE_URL + "#")
    )


def extract_settings(lines):
    rows = []
    for line in section_lines(lines, "## Configuration keys (`settings.json`)", "## Next steps"):
        m = SETTINGS_ROW.match(line.strip())
        if m:
            key, val_type, default, desc = (s.strip() for s in m.groups())
            rows.append((key, val_type, default, absolute(desc)))
    return rows


def extract_flags(lines):
    rows = []
    for line in section_lines(lines, "## Command-line flags", "## Configuration keys (`settings.json`)"):
        m = FLAG_ROW.match(line.strip())
        if m:
            flag, default, desc = (s.strip() for s in m.groups())
            rows.append((flag, default, absolute(desc)))
    return rows


def extract_slash_commands(lines):
    rows = []
    for line in section_lines(lines, "## Core slash commands", "## Default keybindings"):
        s = line.strip()
        if s.startswith("| Command |") or s.startswith("| :--"):
            continue
        m = SLASH_ROW.match(s)
        if m:
            cmd, category, alias, purpose = (part.strip() for part in m.groups())
            rows.append(( absolute(cmd), category, alias, absolute(purpose)))
    return rows


def build(lines):
    settings = extract_settings(lines)
    flags = extract_flags(lines)
    slash_cmds = extract_slash_commands(lines)

    settings_by_type = collections.OrderedDict()
    for key, val_type, default, desc in settings:
        settings_by_type.setdefault(val_type, []).append((key, default, desc))

    slash_by_cat = collections.OrderedDict()
    for cmd, category, alias, purpose in slash_cmds:
        slash_by_cat.setdefault(category, []).append((cmd, alias, purpose))

    out = [
        "# Antigravity CLI reference (settings.json, flags, and slash commands)",
        "",
        "Reference for every `settings.json` configuration key, CLI startup flag, and TUI slash command in the Antigravity CLI (`agy`) docs.",
        "",
        f"Source: {PAGE_URL} (Core slash commands, Command-line flags, and Configuration keys tables). Re-check the source page if a setting, flag, or command is missing or behaves differently.",
        "",
        "## Index",
        "",
        f"- **settings.json keys** ({len(settings)}): " + ", ".join(f"`{t}` ({len(items)})" for t, items in settings_by_type.items()),
        f"- **Command-line flags** ({len(flags)})",
        f"- **Core slash commands** ({len(slash_cmds)}): " + ", ".join(f"{cat} ({len(items)})" for cat, items in slash_by_cat.items()),
        "",
        "## Configuration keys (`~/.gemini/antigravity-cli/settings.json`)",
        "",
        "| Key | Type | Default | Description |",
        "| :- | :- | :- | :- |",
    ]
    for key, val_type, default, desc in settings:
        out.append(f"| `{key}` | {val_type} | {default} | {desc} |")
    out.append("")

    out += [
        "## Command-line flags (`agy`)",
        "",
        "| Flag | Default | Description |",
        "| :- | :- | :- |",
    ]
    for flag, default, desc in flags:
        out.append(f"| {flag} | {default} | {desc} |")
    out.append("")

    out += [
        "## Core slash commands",
        "",
        "| Command | Category | Alias | Purpose |",
        "| :- | :- | :- | :- |",
    ]
    for cmd, category, alias, purpose in slash_cmds:
        out.append(f"| {cmd} | {category} | {alias} | {purpose} |")
    out.append("")

    out += [
        "## See also",
        "",
        f"- CLI settings and `/config` behavior: {DOCS}settings",
        f"- Terminal sandbox and permission rules: {DOCS}sandbox",
        f"- Plugins and `agy plugin` subcommands: {DOCS}plugins",
        f"- Headless mode (`-p` / `--print`): {DOCS}cli/headless",
    ]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        sys.stdout.write(build(f.read().split("\n")))
