#!/usr/bin/env bash
# Verify relative markdown links across the tree: linked files must exist and
# heading anchors must resolve (GitHub slug rules: lowercase; drop characters
# other than alphanumerics, spaces, hyphens, underscores; spaces to hyphens).
# External (http/https/mailto) and root-relative site links are out of scope.
# Exit 1 on any breakage.
#
# Scope is what git tracks. It used to be every *.md under the tree, which was
# equivalent only while no module had dependencies: the first module with a
# node_modules/ directory produced hundreds of failures from third-party
# READMEs, none of them ours and none of them fixable here.
set -euo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

status=0

slug() {
  printf '%s\n' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9 _-]//g; s/ /-/g'
}

check_anchor() {
  local file=$1 anchor=$2 src=$3 base heading
  # tolerate GitHub's -N suffix for duplicate headings
  base=$(printf '%s\n' "$anchor" | sed -E 's/-[0-9]+$//')
  while IFS= read -r heading; do
    s=$(slug "$heading")
    if [ "$s" = "$anchor" ] || [ "$s" = "$base" ]; then
      return 0
    fi
  done < <(sed -nE 's/^#{1,6} +//p' "$file")
  echo "BROKEN ANCHOR: $src -> $file#$anchor"
  return 1
}

while IFS= read -r -d '' src; do
  dir=$(dirname "$src")
  while IFS= read -r target; do
    case "$target" in
      http://*|https://*|mailto:*|'') continue ;;
      # Root-relative targets are site URLs (atlas renders `/patterns/tool-use`),
      # never repository paths - resolving them against the file's directory
      # reports every one of them as broken.
      /*) continue ;;
    esac
    path=${target%%#*}
    # Percent-escapes are how a markdown link carries a path containing
    # brackets (`src/pages/[section]/index.astro` -> `%5Bsection%5D`); decode
    # before testing the filesystem or every such link reads as broken.
    case "$path" in
      *%*) path=$(printf '%b' "${path//%/\\x}") ;;
    esac
    anchor=""
    case "$target" in
      *'#'*) anchor=${target#*#} ;;
    esac
    if [ -n "$path" ] && [ ! -e "$dir/$path" ]; then
      echo "BROKEN LINK: $src -> $target"
      status=1
      continue
    fi
    if [ -n "$anchor" ]; then
      dest=${path:+$dir/$path}
      dest=${dest:-$src}
      case "$dest" in
        *.md) check_anchor "$dest" "$anchor" "$src" || status=1 ;;
      esac
    fi
  done < <(grep -oE '\]\([^)]+\)' "$src" | sed -E 's/^\]\(//; s/\)$//; s/ "[^"]*"$//')
done < <(git ls-files -z '*.md' '*.markdown')

if [ "$status" -eq 0 ]; then
  echo "markdown links OK"
fi
exit "$status"
