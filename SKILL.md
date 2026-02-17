---
name: japan-egov-law-api-docs
description: Use this skill when identifying, verifying, and quoting Japanese laws from primary sources via e-Gov Law API Version 2. Trigger for tasks such as keyword-based law discovery, metadata lookup, revision-history checks, article-level text retrieval, and official law-file downloads.
---

# Japan e-Gov Law API Docs

Note: This `SKILL.md` is kept for Codex compatibility.  
Claude standard command interface is `.claude/commands/legal-jp-egov-api.md`.

## Overview

Use this skill to fetch law data from e-Gov Law API v2 and produce
citation-ready legal research outputs with explicit identifiers and timestamps.

## Workflow

1. Freeze scope
- Clarify whether the user needs `law discovery`, `full text`, `revision checks`,
  or `downloadable files`.
- Separate factual retrieval from legal interpretation.

2. Resolve law identity
- Start from `/laws` with `law_title` if law names are known.
- Start from `/keyword` if only themes or phrases are known.
- Capture `law_id`, `law_num`, and `law_revision_id` for downstream calls.

3. Retrieve authoritative text
- Call `/law_data/{law_id_or_num_or_revision_id}`.
- Use `elm` when only selected parts are needed (for example, an article).
- Prefer `response_format=json&law_full_text_format=json` for machine processing.

4. Verify revision timing
- Call `/law_revisions/{law_id_or_num}` when temporal accuracy matters.
- Record `amendment_enforcement_date`, `repeal_status`, and revision IDs.

5. Produce answer with evidence
- For every substantive statement, provide:
  `law_title`, `law_num`, `law_id`, `law_revision_id`, API endpoint, and
  retrieval timestamp.
- Include e-Gov source terms metadata (terms URL + attribution template).
- Mark any interpretation as inference, not as raw statutory fact.

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

# If installed as a command:
egov-law search-law --law-title '個人情報の保護に関する法律' --limit 3
egov-law keyword --keyword '業務委託' --limit 5
```

## Guardrails

- Treat e-Gov API responses as primary-source snapshots.
- Always keep law identifiers and retrieval timestamp in outputs.
- Distinguish legal text (fact) from interpretation (opinion).
- Add source attribution when publishing outputs based on e-Gov content.
- If content is edited/processed, state that edits were made.
- Do not present edited material as if government-authored.
- Do not provide legal advice, case-specific legal conclusions, or dispute strategy.
- Do not present output as a substitute for attorney consultation.
- Escalate final legal judgment to licensed professionals.

## Resources

- `scripts/egov_law_api.py`
- `scripts/egov_law_mcp_server.py`
- `src/egov_law_api/`
- `examples/ios_legal_draft_evidence.py`
- `examples/ios_legal_draft_workflow.md`
- `references/egov-law-api-v2-quick-reference.md`
- `NOTICE.md`

## iOS Drafting Notes

- For iOS Terms/Privacy drafting, run `examples/ios_legal_draft_evidence.py` first.
- The sample output includes recent-change checkpoints (for example tax and freelancer-protection law topics) with `updated` and `amendment_enforcement_date`.
- Keep all generated text as draft/reference material and require attorney review before publication.
