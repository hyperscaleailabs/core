#!/usr/bin/env bash
# Atlas module policy guards. Runs from anywhere; resolves the repository root.
#
# These live in a script rather than inline in .github/workflows/atlas.yml so
# they can be run before pushing (`make policy`). A guard that exists only as
# workflow YAML is first exercised in CI, which is exactly how the first version
# of this file shipped: its own grep pattern matched its own source line, and
# nothing local could have caught that.
#
# Exit 1 on any violation.
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

SELF="atlas/scripts/check-policy.sh"
status=0

fail() {
  echo "::error::$1"
  status=1
}

# 1. The standalone repository this module came from still exists but no longer
#    moves. atlas/NOTICE.md is the single exception: it is the provenance and
#    licensing record, and a license audit has to be able to find the origin.
echo "== no references to the pre-integration repository =="
hits=$(grep -rn 'hyperscaleailabs/agentic-atlas' \
         --include='*.astro' --include='*.ts' --include='*.mjs' \
         --include='*.md' --include='*.json' --include='*.yaml' \
         --include='*.yml' --exclude=package-lock.json \
         --exclude-dir=.git --exclude-dir=node_modules . 2>/dev/null \
       | grep -v '^\./atlas/NOTICE\.md:' \
       | grep -v "^\./$SELF:" || true)
if [ -n "$hits" ]; then
  printf '%s\n' "$hits"
  fail "reference to the pre-integration standalone repository; use atlas/src/lib/repo.ts"
else
  echo "ok"
fi

# 2. One home for repository URLs in the *site code*, so the next move is one
#    edit. Content is excluded on purpose: an article's `sources` entries are
#    absolute URLs by definition - that is what attribution is - and a lab note
#    links back to the module article it publishes.
echo "== repository URLs come from src/lib/repo.ts only (site code) =="
hits=$(grep -rn 'github\.com/hyperscaleailabs/core' atlas/src \
         --exclude=repo.ts --exclude-dir=content || true)
if [ -n "$hits" ]; then
  printf '%s\n' "$hits"
  fail "hardcoded repository URL in atlas/src/; import from src/lib/repo.ts"
else
  echo "ok"
fi

# 3. Build output and dependencies are regenerated; the ingestion cache is a
#    snapshot of somebody else's pages. None of it belongs in a public tree.
echo "== no committed build output, dependencies, or ingestion cache =="
hits=$(git ls-files atlas | grep -E '^atlas/(dist|node_modules|\.astro|\.vercel)/|^atlas/pipeline/cache/[^.]' || true)
if [ -n "$hits" ]; then
  printf '%s\n' "$hits"
  fail "build output, dependencies, or pipeline cache committed"
else
  echo "ok"
fi

# 4. Repo-wide coverage exists in the policy workflow; kept here so the atlas
#    tree carries its own guard when path filters skip the others.
echo "== no absolute home-directory paths =="
hits=$(grep -rnE '/(Users|home)/[a-z0-9_-]+/' \
         --include='*.md' --include='*.astro' --include='*.ts' --include='*.mjs' \
         --include='*.yaml' --include='*.json' --include='*.sh' \
         --exclude=package-lock.json --exclude-dir=node_modules \
         --exclude-dir=dist --exclude-dir=.astro atlas 2>/dev/null || true)
if [ -n "$hits" ]; then
  printf '%s\n' "$hits"
  fail "absolute home-directory path committed; use module-relative paths"
else
  echo "ok"
fi

# 5. Atlas summarizes and links; it never republishes. An article with no
#    recorded source cannot be checked against the thing it describes.
echo "== every article records at least one source =="
missing=0
while IFS= read -r f; do
  [ -e "$f" ] || continue
  n=$(awk '/^sources:/{flag=1;next}/^[a-zA-Z]/{flag=0}flag&&/^  - /{c++}END{print c+0}' "$f")
  if [ "$n" -eq 0 ]; then
    echo "$f: no sources recorded"
    missing=1
  fi
done < <(git ls-files 'atlas/src/content/*/*.md' 'atlas/src/content/*/*.mdx')
if [ "$missing" -ne 0 ]; then
  fail "attribution is required on every article"
else
  echo "ok"
fi

if [ "$status" -eq 0 ]; then
  echo ""
  echo "atlas policy guards OK"
fi
exit "$status"
