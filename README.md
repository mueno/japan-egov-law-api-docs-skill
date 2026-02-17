# japan-egov-law-api-docs

Codex skill plus ready-to-run CLI and MCP server for Japanese law discovery and
verification using the official e-Gov Law API v2.

## What This Skill Does

- Resolve law identity by `law_title`, `law_num`, `law_id`, or keyword.
- Retrieve authoritative law text and article-level fragments.
- Check revision history and enforcement timing.
- Download official law files and attachments.
- Return citation-ready evidence with law IDs and retrieval timestamps.

## Repository Structure

```text
.
├── SKILL.md
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

## Install Skill

1. Clone this repository.
2. Place this folder under your Codex skills directory:
   - Typical path: `~/.codex/skills/japan-egov-law-api-docs`
3. Confirm `SKILL.md` and `agents/openai.yaml` are present.

## Use In Codex (Skill)

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

## Validation

```bash
python3 -m py_compile scripts/egov_law_api.py
python3 scripts/egov_law_api.py --help
python3 scripts/egov_law_mcp_server.py  # start MCP server
```

## Versioning and Releases

- Semantic versioning is recommended (`v0.1.0`, `v0.1.1`, ...).
- Use GitHub Releases for each tagged version with a short changelog.

## Suggested GitHub Topics

- `codex-skill`
- `japanese-law`
- `egov`
- `legal-tech`

## Safety Note

This skill retrieves primary-source legal text. It does not provide legal advice.
Final legal decisions should be reviewed by qualified professionals.
