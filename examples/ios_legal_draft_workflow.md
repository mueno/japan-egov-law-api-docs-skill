# iOS利用規約・プライバシーポリシー草稿向けサンプル

このドキュメントは、e-Gov法令検索skillを使って草稿の根拠確認を行うための実践テンプレートです。

デフォルトで以下の「直近改正が実務影響しやすいテーマ」も含めて証跡化します。
- 消費税法
- フリーランス保護法（特定受託事業者に係る取引の適正化等に関する法律）

## 1. 証跡パックを作る

```bash
cd /ABSOLUTE/PATH/TO/japan-egov-law-api-docs-skill
python3 examples/ios_legal_draft_evidence.py --output-dir examples/output
```

出力:
- `examples/output/ios_legal_evidence_pack.json`
- `examples/output/ios_legal_draft_checklist.md`

チェックリストには `updated` / `amendment_enforcement_date` も出るため、
「最新改正ベースで草稿確認したか」をレビュー時に明示できます。

## 2. 条文をピンポイント確認する

```bash
egov-law search-law --law-title '個人情報の保護に関する法律' --limit 1
egov-law revisions --law-id-or-num 415AC0000000057
egov-law law-data --law-id-or-num-or-revision-id 415AC0000000057 --elm 'MainProvision-Article[1]'
```

## 3. 草稿プロンプト例（Skill向け）

```text
Use $japan-egov-law-api-docs to verify Japanese legal sources for my iOS privacy policy draft.
Focus on APPI and telecom external-transmission requirements.
Return law_title, law_num, law_id, law_revision_id, endpoint, and retrieval timestamp for each claim.
Separate factual quotes from interpretation.
```

## 4. MCPツール呼び出し例

`egov_keyword_search`:

```json
{
  "keyword": "外部送信",
  "limit": 5,
  "response_format": "json"
}
```

`egov_get_law_data`:

```json
{
  "law_id_or_num_or_revision_id": "415AC0000000057",
  "elm": "MainProvision-Article[1]",
  "response_format": "json",
  "law_full_text_format": "json"
}
```

消費税法（現行改正の確認）:

```bash
egov-law search-law --law-title '消費税法' --limit 1
egov-law revisions --law-id-or-num 363AC0000000108
```

フリーランス保護法（正式法名で確認）:

```bash
egov-law search-law --law-title '特定受託事業者に係る取引の適正化等に関する法律' --limit 1
egov-law revisions --law-id-or-num 505AC0000000025
```

## 5. 草稿運用のコツ

1. 先にアプリ実装実態（収集データ・SDK・課金）を整理してから法令照合する。
2. 法令本文は原文ベースで確認し、草稿では平易化しすぎない。
3. 根拠ID（`law_id`, `law_revision_id`）はレビューコメントに残す。
4. 公開前に必ず弁護士レビューを実施する。

> この資料は法的助言ではありません。最終判断は有資格者のレビューを前提にしてください。
