---
name: legal-jp-egov-api
description: Use e-Gov Law API v2 for Japanese legal-source retrieval, revision checks, and citation-ready evidence generation.
---

# Japan e-Gov Law API Docs (Claude Standard)

## Overview

Use this command to fetch Japanese law data from e-Gov Law API v2 and produce
citation-ready outputs for drafting/review workflows.

## Workflow

1. Freeze scope
- Clarify whether the task is `law discovery`, `text retrieval`, `revision checks`, or `file download`.
- Keep factual retrieval separate from legal interpretation.

2. Resolve law identity
- Use `/laws` with `law_title` when law name is known.
- Use `/keyword` when only themes/phrases are known.
- Capture `law_id`, `law_num`, and `law_revision_id`.

3. Retrieve text and revisions
- Use `/law_data/{law_id_or_num_or_revision_id}` for full text or `elm` filtering.
- Use `/law_revisions/{law_id_or_num}` for amendment timing.

4. Produce evidence output
- Include `law_title`, `law_num`, `law_id`, `law_revision_id`, endpoint, and retrieval timestamp.
- Include e-Gov source terms metadata and attribution template.

## Quick Start

```bash
python3 scripts/egov_law_api.py search-law \
  --law-title '個人情報の保護に関する法律' \
  --limit 3

python3 scripts/egov_law_api.py law-data \
  --law-id-or-num-or-revision-id 415AC0000000057 \
  --elm 'MainProvision-Article[1]'

python3 scripts/egov_law_api.py keyword \
  --keyword '業務委託' \
  --limit 5
```

## Guardrails

- Primary-source retrieval and drafting support only.
- Do not provide legal advice, legality determinations, or dispute strategy.
- Include attribution/edit notices when redistributing e-Gov-derived outputs.
- Escalate final legal judgments to qualified legal professionals.

## Resources

- `scripts/egov_law_api.py`
- `scripts/egov_law_mcp_server.py`
- `references/egov-law-api-v2-quick-reference.md`
- `NOTICE.md`
