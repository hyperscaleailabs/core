#!/usr/bin/env bash
# PII policy check for hsailabs core (public repo).
# Modes:
#   check_pii.sh staged            scan staged file content
#   check_pii.sh commit-msg FILE   scan a commit message file
#   check_pii.sh tree              scan the whole working tree (CI)
# Exits non-zero on any violation. Patterns are intentionally strict; extend the
# allowlist below (and .gitleaks.toml) in the same PR when a false positive appears.

set -euo pipefail

# In-cluster Kubernetes service DNS (<svc>.<ns>.svc.cluster.local) appears inside
# connection URIs of the form scheme://user:password@host, which the email pattern
# cannot distinguish from an address. The suffix is reserved by Kubernetes and can
# never be a real mail domain, so allowing it costs no coverage. Credentials in such
# URIs are caught by gitleaks, not by the email rule.
ALLOW_RE='example\.(com|org|net)|users\.noreply\.github\.com|\.svc\.cluster\.local|/(Users|home)/(runner|worker|app|service|node|ci|ubuntu|user|example)\b|/(Users|home)/\.\.\.|[Cc]:\\+Users\\+\.\.\.'

# pattern id : regex
PATTERNS=(
  'email-address|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
  'email-address-urlencoded|[a-zA-Z0-9._+-]+(%40|%2[fF]40)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
  'home-path-unix|/(Users|home)/[A-Za-z0-9._-]+'
  'home-path-windows|[Cc]:\\+Users\\+[A-Za-z0-9._-]+'
  'coauthor-trailer|[Cc]o-[Aa]uthored-[Bb]y:'
  'private-key-block|-----BEGIN [A-Z ]*PRIVATE KEY-----'
)

# Files that must contain the patterns this script hunts for, because detecting
# a pattern means naming it. The exemption is per path, so extracting a guard
# out of an exempted file into a new one drops the exemption with it: that is
# how check_commit_identity.sh arrived here, having carried the co-author
# pattern out of policy.yml.
SELF_PATHS='^(tools/policy/check_pii\.sh|tools/policy/check_commit_identity\.sh|\.gitleaks\.toml|\.github/workflows/policy\.yml)$'

fail=0

scan_text() {
  local label="$1" text="$2"
  local id re hits
  for entry in "${PATTERNS[@]}"; do
    id="${entry%%|*}"
    re="${entry#*|}"
    hits=$(printf '%s\n' "$text" | grep -nE -e "$re" | grep -vE -e "$ALLOW_RE" || true)
    if [ -n "$hits" ]; then
      echo "POLICY VIOLATION [$id] in $label:"
      printf '%s\n' "$hits" | head -5
      fail=1
    fi
  done
}

is_binary() {
  local source="$1" f="$2" enc
  if [ "$source" = "staged" ]; then
    enc=$(git show ":$f" 2>/dev/null | file -b --mime-encoding -)
  else
    enc=$(file -b --mime-encoding "$f")
  fi
  [ "$enc" = "binary" ]
}

scan_file_list() {
  local source="$1"
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    if printf '%s' "$f" | grep -qE "$SELF_PATHS"; then continue; fi
    [ "$source" = "staged" ] || [ -f "$f" ] || continue
    # Test for binary before reading: slurping a binary into a shell variable emits
    # "ignored null byte" warnings that bury real violations in the output.
    if is_binary "$source" "$f"; then continue; fi
    if [ "$source" = "staged" ]; then
      content=$(git show ":$f" 2>/dev/null || true)
    else
      content=$(cat "$f")
    fi
    scan_text "$f" "$content"
  done
}

case "${1:-}" in
  staged)
    scan_file_list staged < <(git diff --cached --name-only --diff-filter=ACMR)
    ;;
  commit-msg)
    msg=$(grep -v '^#' "${2:?commit message file required}" || true)
    scan_text "commit message" "$msg"
    ;;
  tree)
    scan_file_list tree < <(git ls-files)
    ;;
  *)
    echo "usage: $0 {staged|commit-msg FILE|tree}" >&2
    exit 2
    ;;
esac

if [ "$fail" -ne 0 ]; then
  echo ""
  echo "This is a public repository: no personal names, emails, home paths,"
  echo "credentials, or co-author trailers may be committed. See CONTRIBUTING.md."
  exit 1
fi
