# Contributing

Thanks for contributing.

## Branch Strategy (Best Practice)

Use short-lived topic branches and open Pull Requests to `main`.

Branch naming:

- `feature/<short-description>` for new features
- `fix/<short-description>` for bug fixes
- `docs/<short-description>` for documentation-only changes
- `chore/<short-description>` for maintenance work
- `release/<version>` for release preparation
- `hotfix/<short-description>` for urgent production fixes

Recommended flow:

1. Sync latest `main`
2. Create a topic branch
3. Commit only one logical change set per branch
4. Open a PR and wait for checks/review
5. Squash merge (recommended), then delete branch

`main` should be treated as protected and stable. Avoid direct pushes.

## Before Opening a Pull Request

1. Open an issue first for major changes and discuss scope.
2. Keep changes focused and minimal.
3. Update `.claude/commands/legal-jp-egov-api.md`, `SKILL.md`, and `references/` when behavior changes.
4. Keep `NOTICE.md` aligned when attribution/disclaimer behavior changes.

## Local Checks

Run the following checks before submitting:

```bash
python3 -m py_compile scripts/egov_law_api.py
python3 -m py_compile scripts/egov_law_mcp_server.py
python3 -m py_compile examples/ios_legal_draft_evidence.py
python3 scripts/egov_law_api.py --help
python3 -m py_compile src/egov_law_api/*.py
```

## Pull Request Expectations

- Describe what changed and why.
- Include sample command(s) and expected output shape.
- Avoid unrelated refactors in the same pull request.
- Keep PRs small enough to review quickly.
- Rebase or merge latest `main` before final review if needed.

## Commit Guidance

- Use clear commit messages.
- Prefer one logical change per commit.
