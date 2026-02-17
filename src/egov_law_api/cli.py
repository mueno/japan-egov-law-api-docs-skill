"""CLI for e-Gov Law API v2."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence
from urllib import error, parse

from .api_client import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    bool_query,
    E_GOV_ATTRIBUTION_TEMPLATE,
    E_GOV_EDIT_NOTICE_TEMPLATE,
    E_GOV_TERMS_URL,
    E_GOV_USAGE_NOTE,
    format_payload,
    parse_query_items,
    request_endpoint,
    write_binary_output,
)


def _run_json_like(args: argparse.Namespace, path: str, query: dict[str, object]) -> int:
    response = request_endpoint(
        path=path,
        query=query,
        base_url=args.base_url,
        timeout=args.timeout,
        accept="application/json, application/xml",
    )
    if response.status >= 400:
        print(f"HTTP {response.status}: {response.url}", file=sys.stderr)
        print(format_payload(response.body, response.headers, raw=True))
        return 1
    print(format_payload(response.body, response.headers, raw=args.raw))
    _print_source_notice()
    return 0


def _print_source_notice() -> None:
    print(
        (
            f"[Source Terms] {E_GOV_USAGE_NOTE}\n"
            f"[Source Terms] terms: {E_GOV_TERMS_URL}\n"
            f"[Source Terms] attribution: {E_GOV_ATTRIBUTION_TEMPLATE}\n"
            f"[Source Terms] edited-content: {E_GOV_EDIT_NOTICE_TEMPLATE}"
        ),
        file=sys.stderr,
    )


def command_search_law(args: argparse.Namespace) -> int:
    query = parse_query_items(args.query)
    query.update(
        {
            "law_title": args.law_title,
            "law_num": args.law_num,
            "law_id": args.law_id,
            "asof": args.asof,
            "limit": args.limit,
            "offset": args.offset,
            "order": args.order,
            "response_format": args.response_format,
        }
    )
    return _run_json_like(args, "/laws", query)


def command_keyword(args: argparse.Namespace) -> int:
    query = parse_query_items(args.query)
    query.update(
        {
            "keyword": args.keyword,
            "asof": args.asof,
            "law_num": args.law_num,
            "law_title": args.law_title,
            "limit": args.limit,
            "offset": args.offset,
            "order": args.order,
            "response_format": args.response_format,
        }
    )
    return _run_json_like(args, "/keyword", query)


def command_revisions(args: argparse.Namespace) -> int:
    query = parse_query_items(args.query)
    query.update(
        {
            "law_title": args.law_title,
            "amendment_law_title": args.amendment_law_title,
            "response_format": args.response_format,
        }
    )
    path = f"/law_revisions/{parse.quote(args.law_id_or_num, safe='')}"
    return _run_json_like(args, path, query)


def command_law_data(args: argparse.Namespace) -> int:
    query = parse_query_items(args.query)
    query.update(
        {
            "law_full_text_format": args.law_full_text_format,
            "asof": args.asof,
            "elm": args.elm,
            "omit_amendment_suppl_provision": bool_query(args.omit_amendment_suppl_provision),
            "include_attached_file_content": bool_query(args.include_attached_file_content),
            "response_format": args.response_format,
        }
    )
    path = f"/law_data/{parse.quote(args.law_id_or_num_or_revision_id, safe='')}"
    return _run_json_like(args, path, query)


def command_law_file(args: argparse.Namespace) -> int:
    query = parse_query_items(args.query)
    query.update({"asof": args.asof})
    law_ref = parse.quote(args.law_id_or_num_or_revision_id, safe="")
    file_type = parse.quote(args.file_type, safe="")
    path = f"/law_file/{file_type}/{law_ref}"
    response = request_endpoint(
        path=path,
        query=query,
        base_url=args.base_url,
        timeout=args.timeout,
        accept="*/*",
    )
    if response.status >= 400:
        print(f"HTTP {response.status}: {response.url}", file=sys.stderr)
        print(format_payload(response.body, response.headers, raw=True))
        return 1
    fallback_name = f"law_file_{args.law_id_or_num_or_revision_id}.{args.file_type}"
    output = write_binary_output(args.output, fallback_name, response.body)
    print(str(output))
    _print_source_notice()
    return 0


def command_attachment(args: argparse.Namespace) -> int:
    query = parse_query_items(args.query)
    query.update({"src": args.src})
    revision_id = parse.quote(args.law_revision_id, safe="")
    path = f"/attachment/{revision_id}"
    response = request_endpoint(
        path=path,
        query=query,
        base_url=args.base_url,
        timeout=args.timeout,
        accept="*/*",
    )
    if response.status >= 400:
        print(f"HTTP {response.status}: {response.url}", file=sys.stderr)
        print(format_payload(response.body, response.headers, raw=True))
        return 1
    fallback_name = Path(args.src).name if args.src else f"attachment_{args.law_revision_id}.zip"
    output = write_binary_output(args.output, fallback_name, response.body)
    print(str(output))
    _print_source_notice()
    return 0


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--query",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Extra query parameter. Repeat for multiple values.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI for e-Gov Law API v2")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_law = subparsers.add_parser("search-law", help="Call /laws")
    add_common_options(search_law)
    search_law.add_argument("--law-title")
    search_law.add_argument("--law-num")
    search_law.add_argument("--law-id")
    search_law.add_argument("--asof")
    search_law.add_argument("--limit", type=int)
    search_law.add_argument("--offset", type=int)
    search_law.add_argument("--order")
    search_law.add_argument("--response-format", choices=("json", "xml"), default="json")
    search_law.add_argument("--raw", action="store_true", help="Print without JSON pretty-format.")
    search_law.set_defaults(func=command_search_law)

    keyword = subparsers.add_parser("keyword", help="Call /keyword")
    add_common_options(keyword)
    keyword.add_argument("--keyword", required=True)
    keyword.add_argument("--law-num")
    keyword.add_argument("--law-title")
    keyword.add_argument("--asof")
    keyword.add_argument("--limit", type=int)
    keyword.add_argument("--offset", type=int)
    keyword.add_argument("--order")
    keyword.add_argument("--response-format", choices=("json", "xml"), default="json")
    keyword.add_argument("--raw", action="store_true", help="Print without JSON pretty-format.")
    keyword.set_defaults(func=command_keyword)

    revisions = subparsers.add_parser("revisions", help="Call /law_revisions/{law_id_or_num}")
    add_common_options(revisions)
    revisions.add_argument("--law-id-or-num", required=True)
    revisions.add_argument("--law-title")
    revisions.add_argument("--amendment-law-title")
    revisions.add_argument("--response-format", choices=("json", "xml"), default="json")
    revisions.add_argument("--raw", action="store_true", help="Print without JSON pretty-format.")
    revisions.set_defaults(func=command_revisions)

    law_data = subparsers.add_parser("law-data", help="Call /law_data/{id_or_num_or_revision_id}")
    add_common_options(law_data)
    law_data.add_argument("--law-id-or-num-or-revision-id", required=True)
    law_data.add_argument("--law-full-text-format", choices=("json", "xml"))
    law_data.add_argument("--asof")
    law_data.add_argument("--elm")
    law_data.add_argument("--omit-amendment-suppl-provision", action="store_true")
    law_data.add_argument("--include-attached-file-content", action="store_true")
    law_data.add_argument("--response-format", choices=("json", "xml"), default="json")
    law_data.add_argument("--raw", action="store_true", help="Print without JSON pretty-format.")
    law_data.set_defaults(func=command_law_data)

    law_file = subparsers.add_parser("law-file", help="Call /law_file/{file_type}/{id_or_num_or_revision_id}")
    add_common_options(law_file)
    law_file.add_argument("--file-type", required=True, help="Examples: xml, html, pdf")
    law_file.add_argument("--law-id-or-num-or-revision-id", required=True)
    law_file.add_argument("--asof")
    law_file.add_argument("--output", help="Output file path. Defaults to ./law_file_<id>.<file_type>")
    law_file.set_defaults(func=command_law_file)

    attachment = subparsers.add_parser("attachment", help="Call /attachment/{law_revision_id}")
    add_common_options(attachment)
    attachment.add_argument("--law-revision-id", required=True)
    attachment.add_argument("--src", help="Optional src from attached_files_info.")
    attachment.add_argument("--output", help="Output file path.")
    attachment.set_defaults(func=command_attachment)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except error.URLError as exc:
        print(f"Network error: {exc}", file=sys.stderr)
        return 1


def run() -> None:
    """Console-script entrypoint."""
    raise SystemExit(main())


if __name__ == "__main__":
    run()
