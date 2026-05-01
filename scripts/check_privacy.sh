#!/usr/bin/env bash
# Fail if any tracked file contains the strings claude / anthropic / co-authored-by
# (case-insensitive). Run from the repo root.
#
# Exit codes:
#   0 -- clean
#   1 -- found one or more matches (printed to stderr)
#   2 -- not in a git repo
set -u

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "check_privacy.sh: not in a git repository" >&2
    exit 2
fi

# Tracked files only. Skip binary files; grep -I handles that.
matches=$(git ls-files -z | xargs -0 grep -lIiE 'claude|anthropic|co-authored-by' 2>/dev/null || true)

# Allowlist of files where the policy strings legitimately appear:
#   - .gitignore must literally name the paths it ignores
#   - this script itself contains the regex it greps for
allowlist='^(\.gitignore|scripts/check_privacy\.sh)$'
filtered=$(printf '%s\n' "$matches" | grep -v '^$' | grep -vE "$allowlist" || true)

if [ -n "$filtered" ]; then
    echo "check_privacy.sh: privacy violations found in:" >&2
    printf '  %s\n' "$filtered" >&2
    exit 1
fi

# Scan the most recent commit message for AI attribution trailers/footers.
# We match specific trailer/footer patterns rather than bare mentions, so a
# commit whose message describes the policy itself does not trigger.
last_msg=$(git log -1 --format='%B' 2>/dev/null || true)
trailer_re='(^|\n)\s*(Co-Authored-By|Co-authored-by|Generated[ -]with|Authored[ -]by[ -]+(Claude|Anthropic))[: ]'
if printf '%s\n' "$last_msg" | grep -iE "$trailer_re" >/dev/null; then
    echo "check_privacy.sh: latest commit message contains an AI attribution trailer" >&2
    exit 1
fi

echo "check_privacy.sh: clean"
exit 0
