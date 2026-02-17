#!/usr/bin/env python3
"""Generate e-Gov evidence pack for iOS Terms/Privacy drafting."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import parse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from egov_law_api.api_client import (  # noqa: E402
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    decode_bytes,
    parse_json_text,
    request_endpoint,
)


LAW_SCOPES = [
    {
        "topic": "Privacy policy core",
        "law_title": "個人情報の保護に関する法律",
        "why_to_check": "個人情報の取得・利用目的・第三者提供・開示請求対応の基礎要件を確認する。",
    },
    {
        "topic": "External transmission / tracker disclosure",
        "law_title": "電気通信事業法",
        "why_to_check": "外部送信規律（情報送信指令通信）の説明事項を整理する。",
    },
    {
        "topic": "Consumer-facing terms risk",
        "law_title": "消費者契約法",
        "why_to_check": "利用規約の無効条項リスク（免責・解除・損害賠償制限）を点検する。",
    },
    {
        "topic": "Paid plans / subscription disclosure",
        "law_title": "特定商取引に関する法律",
        "why_to_check": "有料プラン・継続課金の表示義務や通信販売表示の必要性を確認する。",
    },
]

E_GOV_TERMS_URL = "https://laws.e-gov.go.jp/terms/"
ATTRIBUTION_TEMPLATE = "出典: e-Gov法令検索 (https://laws.e-gov.go.jp/) （YYYY年MM月DD日利用）"
EDIT_NOTICE_TEMPLATE = "本資料は e-Gov法令検索の情報をもとに作成し、当社で編集・加工しています。"
DISCLAIMER_TEXT = (
    "This material is for legal-source retrieval and draft support only. "
    "It is not legal advice or legality judgment."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an e-Gov evidence pack for iOS legal drafting.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "examples" / "output"),
        help="Directory to write evidence artifacts.",
    )
    parser.add_argument(
        "--asof",
        default="",
        help="Optional date (YYYY-MM-DD) for historical lookup.",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"e-Gov API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"HTTP timeout seconds (default: {DEFAULT_TIMEOUT})",
    )
    return parser.parse_args()


def call_json(path: str, query: dict[str, Any], *, base_url: str, timeout: float) -> dict[str, Any]:
    response = request_endpoint(
        path=path,
        query=query,
        base_url=base_url,
        timeout=timeout,
        accept="application/json",
    )
    if response.status >= 400:
        body_text = decode_bytes(response.body)
        raise RuntimeError(f"HTTP {response.status} for {response.url}: {body_text[:300]}")
    text = decode_bytes(response.body)
    payload = parse_json_text(text)
    if not isinstance(payload, dict):
        raise RuntimeError(f"Unexpected payload type for {response.url}: {type(payload)}")
    return payload


def extract_law_title(item: dict[str, Any]) -> str:
    """Extract best-effort law title from one /laws item."""
    revision_info = item.get("current_revision_info") or item.get("revision_info") or {}
    title = revision_info.get("law_title")
    if isinstance(title, str):
        return title
    return ""


def select_best_match(laws: list[dict[str, Any]], query_title: str) -> dict[str, Any]:
    """Select best law match by exact-title preference."""
    if not laws:
        return {}
    exact = [law for law in laws if extract_law_title(law) == query_title]
    if exact:
        return exact[0]
    prefixed = [law for law in laws if extract_law_title(law).startswith(query_title)]
    if prefixed:
        return prefixed[0]
    contains = [law for law in laws if query_title in extract_law_title(law)]
    if contains:
        return contains[0]
    return laws[0]


def fetch_scope_evidence(scope: dict[str, str], *, asof: str, base_url: str, timeout: float) -> dict[str, Any]:
    query = {
        "law_title": scope["law_title"],
        "limit": 20,
        "response_format": "json",
        "asof": asof or None,
    }
    search_result = call_json("/laws", query, base_url=base_url, timeout=timeout)
    laws = search_result.get("laws") or []
    if not laws:
        return {
            "topic": scope["topic"],
            "law_title_query": scope["law_title"],
            "why_to_check": scope["why_to_check"],
            "found": False,
            "message": "No law matched the provided title query.",
        }

    first = select_best_match(laws, scope["law_title"])
    law_info = first.get("law_info") or {}
    current_revision = first.get("current_revision_info") or first.get("revision_info") or {}
    law_id = law_info.get("law_id")
    law_num = law_info.get("law_num")
    law_title = current_revision.get("law_title") or scope["law_title"]
    law_revision_id = current_revision.get("law_revision_id")
    updated = current_revision.get("updated")
    amendment_enforcement_date = current_revision.get("amendment_enforcement_date")
    amendment_law_title = current_revision.get("amendment_law_title")
    amendment_law_num = current_revision.get("amendment_law_num")

    revisions: dict[str, Any] = {}
    article1: dict[str, Any] = {}
    if isinstance(law_id, str) and law_id:
        revisions = call_json(
            f"/law_revisions/{parse.quote(law_id, safe='')}",
            {"response_format": "json"},
            base_url=base_url,
            timeout=timeout,
        )
    if isinstance(law_revision_id, str) and law_revision_id:
        article1 = call_json(
            f"/law_data/{parse.quote(law_revision_id, safe='')}",
            {
                "response_format": "json",
                "law_full_text_format": "json",
                "elm": "MainProvision-Article[1]",
                "asof": asof or None,
            },
            base_url=base_url,
            timeout=timeout,
        )

    return {
        "topic": scope["topic"],
        "law_title_query": scope["law_title"],
        "why_to_check": scope["why_to_check"],
        "found": True,
        "law_title": law_title,
        "law_id": law_id,
        "law_num": law_num,
        "law_revision_id": law_revision_id,
        "updated": updated,
        "amendment_enforcement_date": amendment_enforcement_date,
        "amendment_law_title": amendment_law_title,
        "amendment_law_num": amendment_law_num,
        "laws_search_result": search_result,
        "law_revisions_result": revisions,
        "article1_result": article1,
    }


def build_markdown(pack: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# iOS Legal Draft Evidence Pack")
    lines.append("")
    lines.append(f"- Generated at (UTC): `{pack['generated_at_utc']}`")
    lines.append(f"- e-Gov API base URL: `{pack['base_url']}`")
    lines.append(f"- asof: `{pack['asof'] or 'latest'}`")
    lines.append("")
    lines.append("> This material supports drafting only.")
    lines.append("> It is not legal advice, legality judgment, or dispute strategy guidance.")
    lines.append("> Final legal review must be done by qualified professionals.")
    lines.append("")
    lines.append("## Source Attribution and Terms")
    lines.append(f"- Terms URL: `{pack['source_terms']['terms_url']}`")
    lines.append("- Attribution template:")
    lines.append("```text")
    lines.append(pack["source_terms"]["attribution_template"])
    lines.append("```")
    lines.append("- Edited-content template:")
    lines.append("```text")
    lines.append(pack["source_terms"]["edited_content_template"])
    lines.append("```")
    lines.append(
        "- Do not present edited/processed output as if it was authored by the Japanese government."
    )
    lines.append("")
    lines.append("## Drafting Flow")
    lines.append("1. Use this evidence pack to decide which clauses need legal text support.")
    lines.append("2. Draft policy clauses in plain language aligned to app behavior.")
    lines.append("3. Keep `law_id` and `law_revision_id` in your internal review notes.")
    lines.append("4. Request licensed legal review before publication.")
    lines.append("")
    lines.append("## Coverage Summary")
    lines.append("| Topic | Law title | law_id | law_revision_id | Updated | Amendment enforcement date |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for item in pack["items"]:
        if not item.get("found"):
            lines.append(f"| {item['topic']} | (not found) | - | - | - | - |")
            continue
        lines.append(
            f"| {item['topic']} | {item.get('law_title','')} | {item.get('law_id','')} | "
            f"{item.get('law_revision_id','')} | {item.get('updated','')} | "
            f"{item.get('amendment_enforcement_date','')} |"
        )
    lines.append("")
    lines.append("## Per-Law Notes")
    for item in pack["items"]:
        lines.append(f"### {item['topic']}")
        lines.append(f"- Why to check: {item['why_to_check']}")
        if not item.get("found"):
            lines.append(f"- Result: {item.get('message', 'not found')}")
            lines.append("")
            continue
        lines.append(f"- Law title: `{item.get('law_title', '')}`")
        lines.append(f"- Law num: `{item.get('law_num', '')}`")
        lines.append(f"- law_id: `{item.get('law_id', '')}`")
        lines.append(f"- law_revision_id: `{item.get('law_revision_id', '')}`")
        lines.append(f"- updated: `{item.get('updated', '')}`")
        lines.append(f"- amendment_enforcement_date: `{item.get('amendment_enforcement_date', '')}`")
        lines.append(f"- amendment_law_title: `{item.get('amendment_law_title', '')}`")
        lines.append(f"- amendment_law_num: `{item.get('amendment_law_num', '')}`")
        lines.append("- Suggested next command:")
        lines.append("```bash")
        lines.append(
            "egov-law law-data "
            f"--law-id-or-num-or-revision-id {item.get('law_revision_id','')} "
            "--elm 'MainProvision-Article[1]'"
        )
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    items: list[dict[str, Any]] = []
    for scope in LAW_SCOPES:
        evidence = fetch_scope_evidence(
            scope,
            asof=args.asof,
            base_url=args.base_url,
            timeout=args.timeout,
        )
        items.append(evidence)

    pack = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_url": args.base_url,
        "asof": args.asof,
        "source_terms": {
            "terms_url": E_GOV_TERMS_URL,
            "attribution_template": ATTRIBUTION_TEMPLATE,
            "edited_content_template": EDIT_NOTICE_TEMPLATE,
            "disclaimer": DISCLAIMER_TEXT,
        },
        "items": items,
    }

    json_path = output_dir / "ios_legal_evidence_pack.json"
    md_path = output_dir / "ios_legal_draft_checklist.md"
    json_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(pack), encoding="utf-8")

    print(str(json_path))
    print(str(md_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
