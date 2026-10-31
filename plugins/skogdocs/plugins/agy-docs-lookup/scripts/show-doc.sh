#!/usr/bin/env bash
set -euo pipefail

# Usage: show-doc.sh [-c cache_dir] [-H] <slug>
# Output ends with a "source:" line holding the page's docs URL.
# Prints one cached Antigravity doc page, e.g. `show-doc.sh hooks`, or with
# -H only its headings, to pick the sections worth reading. Slugs come from
# search-docs.sh output or the first column of index.txt.

# Cache dir precedence: -c/--cache, then $AGY_DOCS_DIR, then the XDG cache.
CACHE="${AGY_DOCS_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/agy-docs}"

headings_only=0
while getopts ":c:H" opt; do
    case $opt in
        c) CACHE="$OPTARG" ;;
        H) headings_only=1 ;;
        *) echo "usage: show-doc.sh [-c cache_dir] [-H] <slug>" >&2; exit 2 ;;
    esac
done
shift $((OPTIND - 1))

if [[ $# -ne 1 ]]; then
    echo "usage: show-doc.sh [-c cache_dir] [-H] <slug>" >&2
    exit 2
fi

slug="$1"
slug="${slug%%#*}"
slug="${slug%%\?*}"
slug="${slug%/}"
slug="${slug%.md}"
slug="${slug#https://antigravity.google/docs/}"
slug="${slug#/docs/}"
file="$CACHE/$slug.md"

if [[ ! -f "$file" ]]; then
    echo "no cached page '$slug'. Known slugs close to it:" >&2
    if [[ -f "$CACHE/index.txt" ]]; then
        matches=$(cut -f1 "$CACHE/index.txt" | grep -i -- "${slug##*/}" || true)
        printf '%s\n' "$matches" | sed -n '1,10p' >&2
    fi
    exit 1
fi

if [[ $headings_only -eq 1 ]]; then
    grep -n '^#' "$file" || true
else
    cat "$file"
fi
# Footer so the source URL is in the output, for citing the page.
echo
echo "source: https://antigravity.google/docs/$slug"
