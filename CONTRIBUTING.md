# Contributing

Thanks for contributing.

## Before Opening a Pull Request

1. Open an issue first for major changes and discuss scope.
2. Keep changes focused and minimal.
3. Update `SKILL.md` and `references/` when behavior changes.
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

## Commit Guidance

- Use clear commit messages.
- Prefer one logical change per commit.
