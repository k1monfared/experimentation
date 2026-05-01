#!/usr/bin/env bash
# Install scripts/check_privacy.sh as a git pre-commit hook in this clone.
# Idempotent. Run from any directory inside the repo.
set -euo pipefail

repo_root=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [ -z "$repo_root" ]; then
    echo "install_pre_commit: not inside a git repository" >&2
    exit 1
fi

hook_path="$repo_root/.git/hooks/pre-commit"
guard="$repo_root/scripts/check_privacy.sh"
if [ ! -x "$guard" ]; then
    echo "install_pre_commit: scripts/check_privacy.sh not found or not executable" >&2
    exit 1
fi

cat > "$hook_path" <<'HOOK'
#!/usr/bin/env bash
# Auto-installed pre-commit hook. Runs the project's privacy guard so commits
# that introduce policy-string violations are blocked locally before they
# reach CI.
set -e
repo=$(git rev-parse --show-toplevel)
exec "$repo/scripts/check_privacy.sh"
HOOK

chmod +x "$hook_path"
echo "install_pre_commit: installed pre-commit hook -> $hook_path"
