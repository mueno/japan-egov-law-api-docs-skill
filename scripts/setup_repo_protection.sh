#!/usr/bin/env bash
set -euo pipefail

# Apply GitHub repository hardening for public repositories.
# Usage:
#   scripts/setup_repo_protection.sh --apply [owner/repo] [branch]
#
# Example:
#   scripts/setup_repo_protection.sh --apply mueno/japan-egov-law-api-docs-skill main

if [[ "${1:-}" != "--apply" ]]; then
  cat <<'EOF'
Dry-run mode.
This script modifies GitHub repository settings.
Run with --apply to execute:

  scripts/setup_repo_protection.sh --apply [owner/repo] [branch]
EOF
  exit 0
fi

REPO="${2:-mueno/japan-egov-law-api-docs-skill}"
BRANCH="${3:-main}"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required." >&2
  exit 1
fi

VISIBILITY="$(gh api "repos/${REPO}" --jq '.visibility')"
if [[ "${VISIBILITY}" != "public" ]]; then
  echo "Repository ${REPO} is '${VISIBILITY}'. Branch protection requires public repo or GitHub Pro." >&2
  echo "Make the repository public first, then rerun this script." >&2
  exit 2
fi

echo "Enabling vulnerability alerts..."
gh api -X PUT "repos/${REPO}/vulnerability-alerts" \
  -H 'Accept: application/vnd.github+json' >/dev/null

echo "Enabling automated security fixes..."
gh api -X PUT "repos/${REPO}/automated-security-fixes" \
  -H 'Accept: application/vnd.github+json' >/dev/null

echo "Applying branch protection to ${BRANCH}..."
TMP_JSON="$(mktemp)"
cat >"${TMP_JSON}" <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["validate"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": false
}
JSON

gh api -X PUT "repos/${REPO}/branches/${BRANCH}/protection" \
  -H 'Accept: application/vnd.github+json' \
  --input "${TMP_JSON}" >/dev/null

rm -f "${TMP_JSON}"

echo "Done. Current branch protection status:"
gh api "repos/${REPO}/branches/${BRANCH}" \
  --jq '{name,protected,protection:{required_pull_request_reviews:.protection.required_pull_request_reviews.enabled,required_status_checks:.protection.required_status_checks.enabled,enforce_admins:.protection.enforce_admins.enabled}}'
