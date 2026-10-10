#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6.0",
# ]
# ///
"""Find router files under a directory and print the XML tags each one contains.

Usage: list_xml_tags.py [root_dir] [-o output_file]

For every *.md file under root_dir with frontmatter `type: router` (same
discovery as list_routers.py — .git/node_modules skipped), prints:

    <relative-path>: <tag1> <tag2> ...

one line per file, tags in first-appearance order. Files with no XML tags
print "(no xml tags)". With -o, also writes the same lines to a file.
"""

import sys
from collections.abc import Iterator
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts._lib import (
    FrontmatterParseError,
    extract_xml_tags,
    is_router,
    parse_frontmatter,
)

SKIP_DIRS = {".git", "node_modules"}


def find_router_files(root: Path) -> Iterator[tuple[Path, str]]:
    for path in sorted(root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        try:
            raw = path.read_text()
            frontmatter = parse_frontmatter(raw)
        except (FrontmatterParseError, UnicodeDecodeError, OSError):
            continue
        if is_router(frontmatter):
            yield path, raw


def main() -> None:
    args = sys.argv[1:]
    output_file: str | None = None
    if "-o" in args:
        i = args.index("-o")
        output_file = args[i + 1]
        del args[i : i + 2]

    root = Path(args[0]).resolve() if args else Path.cwd()
    if not root.is_dir():
        print(f"Error: not a directory: {root}", file=sys.stderr)
        sys.exit(1)

    lines: list[str] = []
    for path, raw in find_router_files(root):
        tags = extract_xml_tags(raw)
        rel = path.relative_to(root)
        lines.append(f"{rel}: {' '.join(tags) if tags else '(no xml tags)'}")

    for line in lines:
        print(line)

    if output_file:
        _ = Path(output_file).write_text("\n".join(lines) + ("\n" if lines else ""))
        print(f"\n({len(lines)} router file(s) written to {output_file})", file=sys.stderr)


if __name__ == "__main__":
    main()
