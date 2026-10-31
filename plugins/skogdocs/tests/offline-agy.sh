#!/usr/bin/env bash
# Offline checks for agy-docs-lookup: no model calls. Covers the docs cache,
# lookup scripts, the CLI reference, plugin validation, and a fresh-config install.
# Run from anywhere: tests/offline-agy.sh
source "$(dirname "$0")/lib.sh"
AGY_PLUGIN="$REPO/plugins/agy-docs-lookup"

# ---- 01-sync.sh
# Stage 01: sync-docs.sh builds a complete, well-formed docs cache.
echo "stage 01: sync (agy)"

cache="$TEST_TMP/agy-docs"
check "sync exits 0" "$AGY_PLUGIN/scripts/sync-docs.sh" -c "$cache"
check "index.txt exists" test -s "$cache/index.txt"

pages=$(find "$cache" -name '*.md' | wc -l)
entries=$(wc -l < "$cache/index.txt")
[[ "$pages" -ge 90 ]] || fail "only $pages pages; expected the full Antigravity docs set"
pass "page count is $pages"
[[ "$pages" -eq "$entries" ]] || fail "index has $entries entries but $pages pages exist"
pass "index entries match pages"

bad=0
while IFS=$'\t' read -r slug title; do
    page="$cache/$slug.md"
    [[ -s "$page" ]] || { echo "    empty or missing: $slug"; bad=$((bad + 1)); continue; }
    [[ "$(sed -n 2p "$page")" == "Source: https://antigravity.google/docs/$slug" ]] \
        || { echo "    bad Source line: $slug"; bad=$((bad + 1)); }
done < "$cache/index.txt"
[[ $bad -eq 0 ]] || fail "$bad page(s) failed the per-page checks"
pass "every page has a Source line that matches its slug"

check "second sync without --force is a no-op" \
    bash -c "'$AGY_PLUGIN/scripts/sync-docs.sh' -c '$cache' | grep -q 'already cached'"

# ---- 02-lookup.sh
# Stage 02: search-docs.sh and show-doc.sh find and print real pages.
echo "stage 02: search and show (agy)"

[[ -s "$cache/index.txt" ]] || fail "stage 01 cache missing; run stage 01 first"

hits=$("$AGY_PLUGIN/scripts/search-docs.sh" -c "$cache" "enableTerminalSandbox")
grep -q "slug:   cli/reference" <<< "$hits" || fail "search does not find cli/reference for enableTerminalSandbox"
pass "search finds cli/reference for a known setting"

miss=$("$AGY_PLUGIN/scripts/search-docs.sh" -c "$cache" "zzqqnonexistentzzqq")
grep -q "no matches" <<< "$miss" || fail "search should report no matches"
pass "search reports no matches for nonsense"

heads=$("$AGY_PLUGIN/scripts/show-doc.sh" -c "$cache" -H cli/reference)
grep -q "^1:# CLI commands" <<< "$heads" || fail "show-doc -H does not start with the page title"
pass "show-doc -H lists the page headings"

full=$("$AGY_PLUGIN/scripts/show-doc.sh" -c "$cache" cli/reference)
grep -q "enableTerminalSandbox" <<< "$full" || fail "show-doc does not print the settings table"
pass "show-doc prints the whole page"

by_url=$("$AGY_PLUGIN/scripts/show-doc.sh" -c "$cache" "https://antigravity.google/docs/cli/reference?tab=cli#configuration-keys-settingsjson")
[[ "$(sed -n 1p <<< "$by_url")" == "# CLI commands" ]] || fail "show-doc does not accept a docs URL with query/fragment"
pass "show-doc accepts a docs URL"

if "$AGY_PLUGIN/scripts/show-doc.sh" -c "$cache" no-such-page-zzqq >/dev/null 2>&1; then
    fail "show-doc should exit non-zero for an unknown page"
fi
pass "show-doc exits non-zero for an unknown page"

grep -q "^source: https://antigravity.google/docs/cli/reference$" <<< "$full" || fail "show-doc output has no source line"
pass "show-doc ends with the source URL"

# ---- 03-reference.sh
# Stage 03: the CLI reference is exactly what the generator builds from the docs.
echo "stage 03: cli reference (agy)"

[[ -s "$cache/cli/reference.md" ]] || fail "stage 01 cache missing; run stage 01 first"

generated="$TEST_TMP/cli-reference.md"
check "generator runs" bash -c "'$REPO/tools/build-cli-reference.py' '$cache/cli/reference.md' > '$generated'"

committed="$AGY_PLUGIN/skills/agy-docs/references/cli-reference.md"
check "committed reference matches generator output" diff -q "$generated" "$committed"

source_settings=$(awk '/^## Configuration keys/{f=1} /^## Next steps/{f=0} f && /^\| \*\*`[A-Za-z0-9_]+`\*\* \|/' "$cache/cli/reference.md" | wc -l)
ref_settings=$(awk '/^## Configuration keys/{f=1} /^## Command-line flags/{f=0} f && /^\| `[A-Za-z0-9_]+` \|/' "$committed" | wc -l)
[[ "$source_settings" -eq "$ref_settings" ]] || fail "reference has $ref_settings settings, docs table has $source_settings"
pass "reference has all $ref_settings settings.json keys from the docs table"

grep -qE '\]\((/docs/|#)' "$committed" && fail "reference has relative links"
pass "reference has no relative links"

# ---- 04-plugin.sh
# Stage 04: the plugin is valid under strict validation and every file it points at exists.
echo "stage 04: plugin files and strict validation (agy)"

check "plugin validates (--strict)" agy plugin validate --strict "$AGY_PLUGIN"

skill="$AGY_PLUGIN/skills/agy-docs/SKILL.md"
check "skill has name" grep -q '^name: agy-docs$' "$skill"
check "skill has description" grep -q '^description:' "$skill"
check "logo file exists" test -s "$AGY_PLUGIN/assets/logo.svg"

for script in sync-docs.sh search-docs.sh show-doc.sh; do
    check "$script exists and is executable" test -x "$AGY_PLUGIN/scripts/$script"
done

ref="$AGY_PLUGIN/skills/agy-docs/references/cli-reference.md"
check "skill links the cli reference" grep -q 'references/cli-reference.md' "$skill"
check "cli reference file exists" test -s "$ref"

while read -r script; do
    check "SKILL.md names $script" test -x "$AGY_PLUGIN/scripts/$script"
done < <(grep -o 'scripts/[a-z-]*\.sh' "$skill" | sed 's#scripts/##' | sort -u)

# ---- 05-install.sh
# Stage 05: agy plugin install installs the plugin into a fresh HOME config dir and enables it.
echo "stage 05: install into a fresh config dir (agy)"

fresh_home="$TEST_TMP/home"
mkdir -p "$fresh_home"
check "plugin install" env HOME="$fresh_home" agy plugin install "$AGY_PLUGIN"
list_json=$(HOME="$fresh_home" agy plugin list --json)
python3 - "$list_json" <<'PY' || fail "plugin not listed or not enabled in agy plugin list --json"
import json, sys
plugins = json.loads(sys.argv[1])
match = [p for p in plugins if p.get("name") == "agy-docs-lookup"]
assert len(match) == 1, plugins
p = match[0]
assert p.get("enabled") is True, p
assert p.get("skills") == ["agy-docs"], p
PY
pass "plugin is listed, enabled, and exposes skill agy-docs"
