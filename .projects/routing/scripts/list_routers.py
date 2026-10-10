#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6.0",
# ]
# ///
"""Scan a directory tree for router files (markdown with frontmatter type: router).

Usage: list_routers.py [root_dir] [-o output_file]

Prints one path per line (relative to root_dir) for every .md file whose
frontmatter has `type: router`. Directories named .git or node_modules are
skipped. With -o, also writes the same list (newline-separated) to a file.
"""

import sys
from collections.abc import Iterator
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts._lib import (
    FrontmatterParseError,
    parse_frontmatter,
)
from scripts._lib import is_router as _is_router_fm

SKIP_DIRS = {".git", "node_modules"}


def is_router(path: Path) -> bool:
    try:
        raw = path.read_text()
        frontmatter = parse_frontmatter(raw)
    except (FrontmatterParseError, UnicodeDecodeError, OSError):
        return False
    return _is_router_fm(frontmatter)


def find_routers(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if is_router(path):
            yield path.relative_to(root)


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

    routers = list(find_routers(root))
    lines = [str(p) for p in routers]

    for line in lines:
        print(line)

    if output_file:
        _ = Path(output_file).write_text("\n".join(lines) + ("\n" if lines else ""))
        print(f"\n({len(lines)} router file(s) written to {output_file})", file=sys.stderr)


if __name__ == "__main__":
    main()
