# japan-egov-law-api-docs

言語: [English](README.md) | [日本語](README.ja.md)

e-Gov法令API v2（公式）を使って、日本法令の探索・確認を行うための Codex skill と、すぐ使える CLI / MCP サーバーです。

## このskillでできること

- `law_title` / `law_num` / `law_id` / キーワードで法令を特定
- 法令本文（条文単位含む）の取得
- 改正履歴と施行時期の確認
- 法令ファイル・添付ファイルの取得
- `law_id` / `law_revision_id` / 取得時刻を含む証跡出力

## リポジトリ構成

```text
.
├── README.md
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

## Skillとして使う

1. このリポジトリを clone
2. Codex skills ディレクトリ配下に配置  
   例: `~/.codex/skills/japan-egov-law-api-docs`
3. `SKILL.md` と `agents/openai.yaml` が存在することを確認

## クイックセットアップ（CLI + MCP）

```bash
cd /ABSOLUTE/PATH/TO/japan-egov-law-api-docs-skill
uv sync
uv run python scripts/egov_law_api.py --help
```

MCPサーバー起動:

```bash
uv run python scripts/egov_law_mcp_server.py
```

`python3 scripts/egov_law_mcp_server.py` で `Missing dependency: mcp` が出る場合は `uv sync` を先に実行してください。

## Codexでの呼び出し例

```text
Use $japan-egov-law-api-docs to identify relevant Japanese laws from e-Gov API v2 and return citation-ready evidence with law IDs and timestamps.
```

## CLI（インストール不要）

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

成功時、CLIは `stderr` に出典・利用条件の案内を表示します。

## インストール可能コマンド

```bash
uv tool install --editable .
egov-law --help
egov-law-mcp
```

## MCPツール

- `egov_search_law`
- `egov_keyword_search`
- `egov_get_law_data`
- `egov_get_law_revisions`
- `egov_download_law_file`
- `egov_download_attachment`

MCPレスポンスには `source_terms`（利用規約URL・出典テンプレ等）が同梱されます。

## MCPクライアント設定例

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

## iOS法務草稿サンプル

```bash
python3 examples/ios_legal_draft_evidence.py --output-dir examples/output
```

生成物:

- `examples/output/ios_legal_evidence_pack.json`
- `examples/output/ios_legal_draft_checklist.md`
- `examples/ios_legal_draft_workflow.md`

直近改正影響の大きいテーマ（例: `消費税法`, `特定受託事業者に係る取引の適正化等に関する法律`）も含みます。

## 検証

```bash
python3 -m py_compile scripts/egov_law_api.py
uv run python scripts/egov_law_api.py --help
uv run python scripts/egov_law_mcp_server.py
```

## バージョニング

- セマンティックバージョニング推奨（`v0.1.0` など）
- タグごとに GitHub Releases を作成し、変更点を明記

## ブランチ運用とPR

- 短命ブランチ（`feature/*`, `fix/*`, `docs/*`, `chore/*`）を使用
- `main` へは直接pushせず、PR経由で反映
- PRは小さく保ち、レビュー/チェック後に squash merge 推奨
- 詳細は `CONTRIBUTING.md` を参照

## 公開後のリポジトリ保護設定

private かつプラン制約で branch protection API が使えない場合は、
公開（public）に切り替えた直後に次を実行してください。

```bash
scripts/setup_repo_protection.sh --apply mueno/japan-egov-law-api-docs-skill main
```

このスクリプトで以下を一括設定します。

- Vulnerability Alerts
- Automated Security Fixes
- `main` の branch protection（PRレビュー必須 + `validate` チェック必須）

## ライセンスと利用条件

- リポジトリのコード/ドキュメント: MIT（`LICENSE`）
- e-Gov法令データ利用: e-Gov利用規約に従う（<https://laws.e-gov.go.jp/terms/>）
- 実務上の出典・改変明示ルール: `NOTICE.md`
- 依存関係・ツールの権利整理: `THIRD_PARTY_NOTICES.md`

重要: このリポジトリのMITライセンスは、e-Gov由来コンテンツの利用条件を置き換えるものではありません。再配布時は `NOTICE.md` を必ず確認してください。

## 謝辞

公式法令情報を e-Gov法令API v2 として公開いただいている e-Gov法令検索チームおよび関係者の皆さまに感謝します。

本リポジトリは独立したコミュニティプロジェクトであり、日本国政府またはデジタル庁による承認・提携・保証を受けたものではありません。

## 安全上の注意（非弁行為回避）

このskillは、法令一次情報の取得と草稿支援のためのものです。法的助言、適法性の最終判断、紛争戦略の助言は提供しません。

次の用途には使わないでください。

- 弁護士相談の代替
- 違法/適法の最終確定
- 訴訟・紛争戦略の助言
- 専門家レビューなしの最終規約/ポリシー確定

最終判断は有資格の専門家レビューを前提にしてください。

## 無保証・責任制限

法令で許容される最大限の範囲で、本リポジトリおよび出力は現状有姿（AS IS）で提供され、明示黙示を問わず保証はありません。  
合同会社AllNewを含む提供者・作成者・貢献者は、本リポジトリまたは出力の利用に起因する損害について責任を負いません。
