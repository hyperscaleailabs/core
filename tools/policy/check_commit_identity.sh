#!/usr/bin/env bash
# Commit metadata guards: no co-author trailers with a real identity, no email
# addresses in commit messages, and author identities confined to noreply forms.
#
# This lived inline in .github/workflows/policy.yml, which meant it was first
# exercised on a hosted runner, after the push. PR #28 hit that: its first push
# failed on "author identity must use a noreply email", a rule nothing runnable
# locally covered - check_pii.sh scans the working tree, not commit metadata.
# See sdlc/docs/lessons/2026-08-12-retire-em-dash-guard.md, L1, and the same
# reasoning behind infra/scripts/check-hsai.sh.
#
# Usage:
#   check_commit_identity.sh                  # commits this branch adds to origin/main
#   check_commit_identity.sh <rev-list args>  # explicit selection, as CI passes
#
# Exit 1 on any violation.
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" || exit 1

# Allowed identity forms. GitHub injects noreply co-author trailers on squash
# merges when the branch author differs from the merging account, so only
# trailers carrying a non-noreply identity are violations.
NOREPLY='@users\.noreply\.github\.com|<noreply@github\.com>'
NOREPLY_OR_EXAMPLE="${NOREPLY}|@example\.(com|org|net)"
MESSAGE_EMAIL_ALLOWED='example\.(com|org|net)|users\.noreply\.github\.com'
EMAIL='[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Held as an array so the recent-slice fallback ("HEAD -n 20") stays two
# arguments without relying on word splitting.
if [ "$#" -gt 0 ]; then
    selection=("$@")
elif git rev-parse --verify --quiet origin/main >/dev/null &&
     [ -n "$(git rev-list --no-merges origin/main..HEAD 2>/dev/null)" ]; then
    selection=("origin/main..HEAD")
else
    # On origin/main itself the range above is empty. Fall back to a recent
    # slice so the guard degrades to "scan something", never to "scan nothing".
    selection=(HEAD -n 20)
fi

if ! git rev-list "${selection[@]}" >/dev/null 2>&1; then
    echo "::error::not a valid commit selection: ${selection[*]}"
    exit 1
fi

echo "== commit messages and author identities (${selection[*]}) =="

bad=0
count=0
while IFS= read -r commit; do
    count=$((count + 1))
    message=$(git log -1 --format='%B' "$commit")
    identity=$(git log -1 --format='%an <%ae>' "$commit")

    if printf '%s\n' "$message" | grep -iE 'co-authored-by:' | grep -vqiE "$NOREPLY"; then
        echo "Commit $commit: co-author trailer with non-noreply identity"
        bad=1
    fi
    if printf '%s\n' "$message" | grep -E "$EMAIL" | grep -vqE "$MESSAGE_EMAIL_ALLOWED"; then
        echo "Commit $commit: email address in commit message"
        bad=1
    fi
    if printf '%s\n' "$identity" | grep -vqE "$NOREPLY_OR_EXAMPLE"; then
        echo "Commit $commit: author identity must use a noreply email"
        bad=1
    fi
done < <(git rev-list --no-merges "${selection[@]}")

# A selection that matches nothing is a guard reporting ok without looking.
if [ "$count" -eq 0 ]; then
    echo "::error::commit selection matched no commits: ${selection[*]}"
    exit 1
fi

if [ "$bad" -eq 0 ]; then
    echo "ok ($count commit(s) scanned)"
fi
exit $bad
