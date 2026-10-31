#!/usr/bin/env bash
set -euo pipefail

# Usage: sync-docs.sh [-c cache_dir] [--force]
# Downloads the official Google Antigravity docs discovered via sitemap.xml
# (each page fetched as <url>.md) and writes one Markdown file per page under
# the cache dir with a "Source: <url>" header line, plus an index.txt listing
# "<slug><TAB><title>" for every page. Re-running is a no-op unless --force.

# Cache dir precedence: -c/--cache, then $AGY_DOCS_DIR, then the XDG cache.
DEFAULT_CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/agy-docs"
CACHE="${AGY_DOCS_DIR:-$DEFAULT_CACHE}"
SEED_CACHE="${AGY_DOCS_SEED_DIR:-$DEFAULT_CACHE}"
BASE="https://antigravity.google/docs/"
SITEMAP_URL="https://antigravity.google/sitemap.xml"

force=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --force) force=1 ;;
        -c|--cache) CACHE="${2:?--cache needs a directory}"; shift ;;
        *) echo "usage: sync-docs.sh [-c cache_dir] [--force]" >&2; exit 2 ;;
    esac
    shift
done

if [[ $force -eq 0 && -f "$CACHE/index.txt" ]]; then
    echo "docs already cached at $CACHE (use --force to refresh)"
    exit 0
fi

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

# Format a directory of raw .md pages (without Source: lines) into $tmp/pages + $tmp/index.txt.
format_raw_pages() {
    local raw_dir="$1"
    mkdir -p "$tmp/pages"
    : > "$tmp/index.txt"
    while IFS= read -r raw_file; do
        local slug="${raw_file#"$raw_dir"/}"
        slug="${slug%.md}"
        local out="$tmp/pages/$slug.md"
        mkdir -p "$(dirname "$out")"
        local first_line
        first_line=$(sed -n 1p "$raw_file")
        local title="$first_line"
        title="${title#\# }"
        if [[ -z "$title" || "$title" == "$first_line" ]]; then
            title="$slug"
        fi
        printf '%s\t%s\n' "$slug" "$title" >> "$tmp/index.txt"
        {
            printf '# %s\n' "$title"
            printf 'Source: %s%s\n' "$BASE" "$slug"
            sed '1d' "$raw_file"
        } > "$out"
    done < <(find "$raw_dir" -type f -name '*.md' | sort)
}

if [[ -n "${AGY_DOCS_RAW_DIR:-}" && -d "${AGY_DOCS_RAW_DIR}" ]]; then
    echo "building docs cache from raw pages in $AGY_DOCS_RAW_DIR"
    format_raw_pages "$AGY_DOCS_RAW_DIR"
elif curl -sfL "$SITEMAP_URL" -o "$tmp/sitemap.xml" 2>/dev/null; then
    echo "fetching docs listed in $SITEMAP_URL"
    mkdir -p "$tmp/raw"
    grep -oE 'https://antigravity\.google/docs/[^<]+' "$tmp/sitemap.xml" \
        | sed 's#/$##' \
        | sort -u \
        | while IFS= read -r url; do
            slug="${url#"$BASE"}"
            mkdir -p "$(dirname "$tmp/raw/$slug.md")"
            printf 'url = "%s.md"\noutput = "%s/raw/%s.md"\n' "$url" "$tmp" "$slug"
        done > "$tmp/curl.cfg"

    if [[ ! -s "$tmp/curl.cfg" ]]; then
        echo "error: no /docs/ URLs found in $SITEMAP_URL" >&2
        exit 1
    fi

    curl -sfL --parallel --parallel-max 16 -K "$tmp/curl.cfg"
    format_raw_pages "$tmp/raw"
elif [[ $force -eq 0 && "$CACHE" != "$SEED_CACHE" && -s "$SEED_CACHE/index.txt" ]]; then
    echo "network unavailable; seeding $CACHE from local cache $SEED_CACHE"
    mkdir -p "$(dirname "$CACHE")"
    rm -rf "$CACHE"
    mkdir -p "$CACHE"
    cp -r "$SEED_CACHE/." "$CACHE/"
    pages=$(find "$CACHE" -name '*.md' | wc -l)
    echo "synced $pages pages to $CACHE"
    exit 0
else
    echo "error: could not reach $SITEMAP_URL (if running in a sandbox without network, run sync-docs.sh outside the sandbox first)" >&2
    exit 1
fi

pages=$(find "$tmp/pages" -name '*.md' | wc -l)
if [[ "$pages" -eq 0 ]]; then
    echo "error: no pages found in bundle" >&2
    exit 1
fi

# Swap in the new copy in one step so a failed run never leaves a half cache.
mkdir -p "$(dirname "$CACHE")"
rm -rf "$CACHE"
mkdir -p "$CACHE"
cp -r "$tmp/pages/." "$CACHE/"
mv "$tmp/index.txt" "$CACHE/index.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$CACHE/synced-at.txt"

echo "synced $pages pages to $CACHE"
