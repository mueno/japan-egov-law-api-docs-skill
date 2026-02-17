# japan-egov-law-api-docs

Language: [English](README.md) | [日本語](README.ja.md)

Claude command/skill-first package plus ready-to-run CLI and MCP server for
Japanese law discovery and verification using the official e-Gov Law API v2.

## What This Skill Does

- Resolve law identity by `law_title`, `law_num`, `law_id`, or keyword.
- Retrieve authoritative law text and article-level fragments.
- Check revision history and enforcement timing.
- Download official law files and attachments.
- Return citation-ready evidence with law IDs and retrieval timestamps.

## Repository Structure

```text
.
├── .claude/commands/legal-jp-egov-api.md
├── README.ja.md
├── SKILL.md
├── NOTICE.md
├── THIRD_PARTY_NOTICES.md
├── agents/openai.yaml
├── pyproject.toml
├── examples/
│   ├── ios_legal_draft_evidence.py
│   └── ios_legal_draft_workflow.md
├── references/egov-law-api-v2-quick-reference.md
├── scripts/egov_law_api.py
├── scripts/egov_law_mcp_server.py
└── src/egov_law_api/
    ├── api_client.py
    ├── cli.py
    └── mcp_server.py
```

## Use In Claude (Standard)

1. Clone this repository.
2. Open this folder as your Claude Code workspace.
3. Use the local command: `/legal-jp-egov-api`

If you want to reuse the command in another workspace, copy:

- `.claude/commands/legal-jp-egov-api.md`

## Quick Setup (CLI + MCP)

```bash
cd /ABSOLUTE/PATH/TO/japan-egov-law-api-docs-skill
uv sync
uv run python scripts/egov_law_api.py --help
```

Start MCP server:

```bash
uv run python scripts/egov_law_mcp_server.py
```

If you run `python3 scripts/egov_law_mcp_server.py` directly and see
`Missing dependency: mcp`, run `uv sync` first.

## Use In Codex (Optional)

Codex compatibility is provided as an optional interface.
Optional Codex files are `SKILL.md` and `agents/openai.yaml`.

Use trigger prompt:

```text
Use $japan-egov-law-api-docs to identify relevant Japanese laws from e-Gov API v2 and return citation-ready evidence with law IDs and timestamps.
```

## Quick CLI (No Install)

```bash
python3 scripts/egov_law_api.py search-law \
  --law-title '個人情報の保護に関する法律' \
  --limit 3

python3 scripts/egov_law_api.py keyword \
  --keyword '業務委託' \
  --limit 5

python3 scripts/egov_law_api.py law-data \
  --law-id-or-num-or-revision-id 415AC0000000057 \
  --elm 'MainProvision-Article[1]'
```

Note: CLI prints source-attribution guidance to `stderr` on successful runs.

## Installable CLI Commands

```bash
uv tool install --editable .
egov-law --help
egov-law search-law --law-title '個人情報の保護に関する法律' --limit 3
```

## Quick MCP Server (No Install)

```bash
python3 scripts/egov_law_mcp_server.py
```

## Installable MCP Command

```bash
uv tool install --editable .
egov-law-mcp
```

## MCP Tools

- `egov_search_law`
- `egov_keyword_search`
- `egov_get_law_data`
- `egov_get_law_revisions`
- `egov_download_law_file`
- `egov_download_attachment`

All MCP responses include a `source_terms` object with terms URL and attribution templates.

## MCP Client Config Example

```json
{
  "mcpServers": {
    "japan-egov-law-api": {
      "command": "python3",
      "args": [
        "/ABSOLUTE/PATH/TO/japan-egov-law-api-docs-skill/scripts/egov_law_mcp_server.py"
      ]
    }
  }
}
```

## iOS Legal Draft Examples

Run sample evidence generation for iOS Terms/Privacy drafting:

```bash
python3 examples/ios_legal_draft_evidence.py --output-dir examples/output
```

Then use:

- `examples/output/ios_legal_evidence_pack.json`
- `examples/output/ios_legal_draft_checklist.md`
- `examples/ios_legal_draft_workflow.md`

The sample includes recent-change-sensitive themes such as:

- `消費税法`
- `特定受託事業者に係る取引の適正化等に関する法律` (freelancer protection)

## Validation

```bash
python3 -m py_compile scripts/egov_law_api.py
uv run python scripts/egov_law_api.py --help
uv run python scripts/egov_law_mcp_server.py  # start MCP server
```

## Versioning and Releases

- Semantic versioning is recommended (`v0.1.0`, `v0.1.1`, ...).
- Use GitHub Releases for each tagged version with a short changelog.

## Branching and PR Workflow

- Use short-lived topic branches (`feature/*`, `fix/*`, `docs/*`, `chore/*`).
- Open PRs to `main` and avoid direct pushes to `main`.
- Keep PRs small and squash-merge after review/checks.
- See `CONTRIBUTING.md` for details.

## Repository Hardening (After Public Visibility)

If the repository is private under a plan that blocks branch protection APIs,
make it public first and then run:

```bash
scripts/setup_repo_protection.sh --apply mueno/japan-egov-law-api-docs-skill main
```

This script enables:

- vulnerability alerts
- automated security fixes
- branch protection for `main` (PR review + required check `validate`)

## Suggested GitHub Topics

- `claude-code`
- `codex-skill`
- `japanese-law`
- `egov`
- `legal-tech`

## License and Terms Alignment

- Repository code/documentation: MIT (`LICENSE`)
- e-Gov law content usage: follows e-Gov terms (`https://laws.e-gov.go.jp/terms/`)
- Practical usage rules and templates: `NOTICE.md`
- Third-party dependency/tool rights summary: `THIRD_PARTY_NOTICES.md`

Important: This repository license does not replace e-Gov content terms. If you
redistribute outputs containing e-Gov law content, follow `NOTICE.md` for source
attribution and edited-content labeling.

## Acknowledgements

We sincerely thank the e-Gov Law Search team and related contributors for making
official legal information publicly accessible via e-Gov Law API v2.

This repository is an independent community project and is not endorsed by, or
affiliated with, the Japanese government or the Digital Agency.

## Safety Note

This skill is for primary-source retrieval and drafting support only.
It does not provide legal advice, legal opinion, or case-specific legality judgment.

Do not use this skill output as:

- a substitute for attorney consultation,
- a final determination of legality/illegality,
- litigation/dispute strategy advice,
- final contract/policy text without qualified legal review.

Final legal decisions must be reviewed by qualified professionals.

## No Warranty and Liability

To the maximum extent permitted by law, this repository and its outputs are
provided "AS IS" without warranties, and the providers/authors (including
AllNew LLC / 合同会社AllNew and contributors) are not liable for any damages
arising from use of this repository or its outputs.
