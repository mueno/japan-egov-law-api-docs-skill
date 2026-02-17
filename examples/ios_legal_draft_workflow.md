# iOS利用規約・プライバシーポリシー草稿向けサンプル

このドキュメントは、e-Gov法令検索skillを使って草稿の根拠確認を行うための実践テンプレートです。

デフォルトで以下の「iOS利用規約/プライバシーポリシーで基本となる法令」を証跡化します。
- 個人情報の保護に関する法律
- 電気通信事業法（外部送信規律）
- 消費者契約法
- 特定商取引に関する法律

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
Do not provide legal advice or legality conclusions; provide draft-support notes only.
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

特定商取引法（有料プラン表示の確認）:

```bash
egov-law search-law --law-title '特定商取引に関する法律' --limit 1
egov-law revisions --law-id-or-num 351AC0000000057
```

個人情報保護法（最新版確認）:

```bash
egov-law search-law --law-title '個人情報の保護に関する法律' --limit 1
egov-law revisions --law-id-or-num 415AC0000000057
```

## 5. 草稿運用のコツ

1. 先にアプリ実装実態（収集データ・SDK・課金）を整理してから法令照合する。
2. 法令本文は原文ベースで確認し、草稿では平易化しすぎない。
3. 根拠ID（`law_id`, `law_revision_id`）はレビューコメントに残す。
4. 公開前に必ず弁護士レビューを実施する。

## 6. e-Gov利用条件に沿った出典表記

対外資料や社内配布物にe-Gov由来情報を載せる場合は、最低限以下を記載:

```text
出典: e-Gov法令検索 (https://laws.e-gov.go.jp/) （YYYY年MM月DD日利用）
本資料は e-Gov法令検索の情報をもとに作成し、当社で編集・加工しています。
```

※編集・加工していない場合は、2行目は不要です。  
※編集版を「国が作成した資料」のように見せる表現は避けてください。

## 7. 非弁行為回避の運用ルール

本ツールは法令テキストの検索・取得・証跡化を行うものであり、弁護士法第72条に定める法律事務（鑑定・代理・仲裁・和解等）を提供するものではありません。以下の運用ルールを遵守してください。

1. 出力の用途を「法令情報整理」「草稿支援」に限定する。
2. 個別案件の適法性判断、紛争対応方針、交渉方針は出力させない。
3. 対外説明（ユーザー向け最終文言・契約条項確定）は弁護士レビュー後に確定する。

> この資料は法的助言ではありません。最終判断は有資格者のレビューを前提にしてください。
