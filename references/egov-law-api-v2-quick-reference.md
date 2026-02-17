# e-Gov Law API v2 Quick Reference

Last verified: 2026-02-16 (JST)  
Primary spec source: `https://laws.e-gov.go.jp/api/2/swagger-ui/lawapi-v2.yaml`

## Base URLs

- Swagger UI: `https://laws.e-gov.go.jp/api/2/swagger-ui/`
- Redoc: `https://laws.e-gov.go.jp/api/2/redoc/`
- API base: `https://laws.e-gov.go.jp/api/2`

## Core Endpoints

1. `GET /laws`
- Purpose: List/search laws by metadata (`law_title`, `law_num`, etc.).
- Typical use: Resolve `law_id`/`law_revision_id` before full-text retrieval.

2. `GET /law_revisions/{law_id_or_num}`
- Purpose: Retrieve revision history for one law.
- Typical use: Confirm effective timing and revision transitions.

3. `GET /law_data/{law_id_or_num_or_revision_id}`
- Purpose: Retrieve law body (full text or filtered element with `elm`).
- Typical use: Quote specific statutory text with revision evidence.

4. `GET /keyword`
- Purpose: Full-text search inside law body content.
- Typical use: Discover applicable laws when only a concept/phrase is known.

5. `GET /law_file/{file_type}/{law_id_or_num_or_revision_id}`
- Purpose: Download official law files (`xml`, etc.).
- Typical use: Archive or downstream processing with original files.

6. `GET /attachment/{law_revision_id}`
- Purpose: Download attached files referenced by law body.
- Typical use: Retrieve figures or attachment PDFs linked from law XML.

## Practical Retrieval Flow

1. Discover law IDs
- Call `/laws?law_title=...` or `/keyword?keyword=...`.
- Capture `law_id`, `law_num`, `law_revision_id`, `law_title`.

2. Retrieve legal text
- Call `/law_data/{law_id_or_num_or_revision_id}`.
- Use `elm` when article-level extraction is enough.

3. Verify temporal applicability
- Call `/law_revisions/{law_id_or_num}`.
- Record the relevant `law_revision_id` and enforcement status/date.

4. Build citation-ready output
- Include endpoint used, exact identifiers, and retrieval timestamp.

## Important Notes from Official Spec

- Some JSON response behavior is marked as trial and may change.
- For large law text, direct URL access can be more stable than interactive Swagger execution.
- When `response_format` and `law_full_text_format` differ, returned `law_full_text` may be Base64-encoded.

## CLI Examples

No-install wrapper:

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

Installed command:

```bash
egov-law search-law --law-title '個人情報の保護に関する法律' --limit 3
egov-law keyword --keyword '業務委託' --limit 5
egov-law law-data --law-id-or-num-or-revision-id 415AC0000000057 --elm 'MainProvision-Article[1]'
```
