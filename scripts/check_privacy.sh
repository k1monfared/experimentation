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

# Also scan the most recent commit message and its body for AI attribution.
last_msg=$(git log -1 --format='%B' 2>/dev/null || true)
if echo "$last_msg" | grep -iE 'claude|anthropic|co-authored-by' >/dev/null; then
    echo "check_privacy.sh: latest commit message contains AI attribution" >&2
    exit 1
fi

echo "check_privacy.sh: clean"
exit 0
