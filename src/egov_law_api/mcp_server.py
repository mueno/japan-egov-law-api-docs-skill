"""MCP server exposing e-Gov Law API v2 tools."""

from __future__ import annotations

import asyncio
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional
from urllib import error, parse

from mcp.server.fastmcp import FastMCP

from .api_client import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    bool_query,
    decode_bytes,
    parse_json_text,
    request_endpoint,
    write_binary_output,
)

mcp = FastMCP("japan-egov-law-api")

MAX_TEXT_CHARS = int(os.environ.get("EGOV_LAW_MCP_MAX_TEXT_CHARS", "4000"))
MAX_ID_CHARS = int(os.environ.get("EGOV_LAW_MCP_MAX_ID_CHARS", "256"))
MAX_FILE_TYPE_CHARS = int(os.environ.get("EGOV_LAW_MCP_MAX_FILE_TYPE_CHARS", "16"))
MAX_LIMIT = int(os.environ.get("EGOV_LAW_MCP_MAX_LIMIT", "100"))
RATE_LIMIT_PER_MINUTE = int(os.environ.get("EGOV_LAW_MCP_RATE_LIMIT_PER_MINUTE", "60"))
RATE_LIMIT_WINDOW_SECONDS = 60.0

if MAX_TEXT_CHARS < 256:
    MAX_TEXT_CHARS = 4000
if MAX_ID_CHARS < 32:
    MAX_ID_CHARS = 256
if MAX_FILE_TYPE_CHARS < 3:
    MAX_FILE_TYPE_CHARS = 16
if MAX_LIMIT < 1:
    MAX_LIMIT = 100
if RATE_LIMIT_PER_MINUTE < 1:
    RATE_LIMIT_PER_MINUTE = 60

_FILE_TYPE_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,16}$")
_rate_window: list[float] = []
_rate_lock = asyncio.Lock()


def _to_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def _sanitize_text(value: str, max_len: int = 400) -> str:
    compact = " ".join(value.split())
    if len(compact) <= max_len:
        return compact
    return f"{compact[:max_len]}..."


def _error_json(
    message: str,
    *,
    error_type: str = "ValidationError",
    http_status: int | None = None,
    url: str | None = None,
) -> str:
    payload: dict[str, Any] = {
        "success": False,
        "error_type": error_type,
        "error": _sanitize_text(message),
    }
    if http_status is not None:
        payload["http_status"] = http_status
    if url is not None:
        payload["url"] = url
    return _to_json(payload)


def _validate_optional_text(name: str, value: str, max_len: int = MAX_TEXT_CHARS) -> Optional[str]:
    normalized = value.strip()
    if not normalized:
        return None
    if len(normalized) > max_len:
        raise ValueError(f"{name} is too long (max {max_len} chars).")
    return normalized


def _validate_required_text(name: str, value: str, max_len: int = MAX_TEXT_CHARS) -> str:
    normalized = _validate_optional_text(name, value, max_len=max_len)
    if normalized is None:
        raise ValueError(f"{name} must not be empty.")
    return normalized


def _validate_limit(value: int) -> int:
    if value < 1 or value > MAX_LIMIT:
        raise ValueError(f"limit must be between 1 and {MAX_LIMIT}.")
    return value


def _validate_offset(value: int) -> int:
    if value < 0:
        raise ValueError("offset must be >= 0.")
    return value


def _validate_response_format(value: str) -> str:
    if value not in {"json", "xml"}:
        raise ValueError("response_format must be json or xml.")
    return value


def _validate_law_ref(name: str, value: str) -> str:
    normalized = _validate_required_text(name, value, max_len=MAX_ID_CHARS)
    return normalized


def _validate_file_type(value: str) -> str:
    normalized = _validate_required_text("file_type", value, max_len=MAX_FILE_TYPE_CHARS)
    if not _FILE_TYPE_PATTERN.fullmatch(normalized):
        raise ValueError("file_type contains invalid characters.")
    return normalized


def _decode_response_payload(headers: dict[str, str], body: bytes) -> Any:
    text = decode_bytes(body)
    content_type = headers.get("content-type", "").lower()
    if "application/json" in content_type:
        try:
            return parse_json_text(text)
        except json.JSONDecodeError:
            return text
    return text


def _success_json(
    *,
    endpoint: str,
    status: int,
    url: str,
    headers: dict[str, str],
    body: bytes,
) -> str:
    return _to_json(
        {
            "success": True,
            "endpoint": endpoint,
            "status": status,
            "url": url,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "data": _decode_response_payload(headers, body),
        }
    )


def _http_error_json(
    *,
    endpoint: str,
    status: int,
    url: str,
    body: bytes,
) -> str:
    body_text = decode_bytes(body)
    return _to_json(
        {
            "success": False,
            "error_type": "HTTPError",
            "endpoint": endpoint,
            "http_status": status,
            "url": url,
            "error_body": _sanitize_text(body_text, max_len=1200),
        }
    )


async def _enforce_rate_limit(tool_name: str) -> None:
    now = time.monotonic()
    async with _rate_lock:
        while _rate_window and (now - _rate_window[0]) > RATE_LIMIT_WINDOW_SECONDS:
            _rate_window.pop(0)
        if len(_rate_window) >= RATE_LIMIT_PER_MINUTE:
            raise ValueError(
                f"Rate limit exceeded: max {RATE_LIMIT_PER_MINUTE} requests/minute. Tool={tool_name}"
            )
        _rate_window.append(now)


async def _request_json_endpoint(endpoint: str, query: dict[str, Any]) -> str:
    response = await asyncio.to_thread(
        request_endpoint,
        endpoint,
        query,
        base_url=DEFAULT_BASE_URL,
        timeout=DEFAULT_TIMEOUT,
        accept="application/json, application/xml",
    )
    if response.status >= 400:
        return _http_error_json(
            endpoint=endpoint,
            status=response.status,
            url=response.url,
            body=response.body,
        )
    return _success_json(
        endpoint=endpoint,
        status=response.status,
        url=response.url,
        headers=response.headers,
        body=response.body,
    )


@mcp.tool()
async def egov_search_law(
    law_title: str = "",
    law_num: str = "",
    law_id: str = "",
    asof: str = "",
    limit: int = 5,
    offset: int = 0,
    order: str = "",
    response_format: Literal["json", "xml"] = "json",
) -> str:
    """Search laws by title/number/id using e-Gov GET /laws."""
    try:
        await _enforce_rate_limit("egov_search_law")
        law_title_n = _validate_optional_text("law_title", law_title)
        law_num_n = _validate_optional_text("law_num", law_num)
        law_id_n = _validate_optional_text("law_id", law_id)
        asof_n = _validate_optional_text("asof", asof)
        order_n = _validate_optional_text("order", order, max_len=64)
        if not any([law_title_n, law_num_n, law_id_n]):
            raise ValueError("Specify at least one of law_title, law_num, or law_id.")

        query = {
            "law_title": law_title_n,
            "law_num": law_num_n,
            "law_id": law_id_n,
            "asof": asof_n,
            "limit": _validate_limit(limit),
            "offset": _validate_offset(offset),
            "order": order_n,
            "response_format": _validate_response_format(response_format),
        }
        return await _request_json_endpoint("/laws", query)
    except ValueError as exc:
        return _error_json(str(exc))
    except error.URLError as exc:
        return _error_json(str(exc), error_type="NetworkError")
    except Exception as exc:  # pragma: no cover
        return _error_json(str(exc), error_type=type(exc).__name__)


@mcp.tool()
async def egov_keyword_search(
    keyword: str,
    asof: str = "",
    law_num: str = "",
    law_title: str = "",
    limit: int = 5,
    offset: int = 0,
    order: str = "",
    response_format: Literal["json", "xml"] = "json",
) -> str:
    """Search law text by keyword using e-Gov GET /keyword."""
    try:
        await _enforce_rate_limit("egov_keyword_search")
        query = {
            "keyword": _validate_required_text("keyword", keyword),
            "asof": _validate_optional_text("asof", asof),
            "law_num": _validate_optional_text("law_num", law_num),
            "law_title": _validate_optional_text("law_title", law_title),
            "limit": _validate_limit(limit),
            "offset": _validate_offset(offset),
            "order": _validate_optional_text("order", order, max_len=64),
            "response_format": _validate_response_format(response_format),
        }
        return await _request_json_endpoint("/keyword", query)
    except ValueError as exc:
        return _error_json(str(exc))
    except error.URLError as exc:
        return _error_json(str(exc), error_type="NetworkError")
    except Exception as exc:  # pragma: no cover
        return _error_json(str(exc), error_type=type(exc).__name__)


@mcp.tool()
async def egov_get_law_data(
    law_id_or_num_or_revision_id: str,
    law_full_text_format: Literal["json", "xml"] = "json",
    asof: str = "",
    elm: str = "",
    omit_amendment_suppl_provision: bool = False,
    include_attached_file_content: bool = False,
    response_format: Literal["json", "xml"] = "json",
) -> str:
    """Get law full text (or filtered element) using e-Gov GET /law_data/{id}."""
    try:
        await _enforce_rate_limit("egov_get_law_data")
        law_ref = _validate_law_ref(
            "law_id_or_num_or_revision_id",
            law_id_or_num_or_revision_id,
        )
        path = f"/law_data/{parse.quote(law_ref, safe='')}"
        query = {
            "law_full_text_format": _validate_response_format(law_full_text_format),
            "asof": _validate_optional_text("asof", asof),
            "elm": _validate_optional_text("elm", elm),
            "omit_amendment_suppl_provision": bool_query(omit_amendment_suppl_provision),
            "include_attached_file_content": bool_query(include_attached_file_content),
            "response_format": _validate_response_format(response_format),
        }
        return await _request_json_endpoint(path, query)
    except ValueError as exc:
        return _error_json(str(exc))
    except error.URLError as exc:
        return _error_json(str(exc), error_type="NetworkError")
    except Exception as exc:  # pragma: no cover
        return _error_json(str(exc), error_type=type(exc).__name__)


@mcp.tool()
async def egov_get_law_revisions(
    law_id_or_num: str,
    law_title: str = "",
    amendment_law_title: str = "",
    response_format: Literal["json", "xml"] = "json",
) -> str:
    """Get revision history using e-Gov GET /law_revisions/{law_id_or_num}."""
    try:
        await _enforce_rate_limit("egov_get_law_revisions")
        law_ref = _validate_law_ref("law_id_or_num", law_id_or_num)
        path = f"/law_revisions/{parse.quote(law_ref, safe='')}"
        query = {
            "law_title": _validate_optional_text("law_title", law_title),
            "amendment_law_title": _validate_optional_text("amendment_law_title", amendment_law_title),
            "response_format": _validate_response_format(response_format),
        }
        return await _request_json_endpoint(path, query)
    except ValueError as exc:
        return _error_json(str(exc))
    except error.URLError as exc:
        return _error_json(str(exc), error_type="NetworkError")
    except Exception as exc:  # pragma: no cover
        return _error_json(str(exc), error_type=type(exc).__name__)


@mcp.tool()
async def egov_download_law_file(
    file_type: str,
    law_id_or_num_or_revision_id: str,
    asof: str = "",
    output_path: str = "",
) -> str:
    """Download law file using e-Gov GET /law_file/{file_type}/{id}."""
    try:
        await _enforce_rate_limit("egov_download_law_file")
        file_type_n = _validate_file_type(file_type)
        law_ref = _validate_law_ref("law_id_or_num_or_revision_id", law_id_or_num_or_revision_id)
        path = f"/law_file/{parse.quote(file_type_n, safe='')}/{parse.quote(law_ref, safe='')}"
        query = {"asof": _validate_optional_text("asof", asof)}

        response = await asyncio.to_thread(
            request_endpoint,
            path,
            query,
            base_url=DEFAULT_BASE_URL,
            timeout=DEFAULT_TIMEOUT,
            accept="*/*",
        )
        if response.status >= 400:
            return _http_error_json(
                endpoint="/law_file/{file_type}/{law_id_or_num_or_revision_id}",
                status=response.status,
                url=response.url,
                body=response.body,
            )

        fallback = f"law_file_{law_ref}.{file_type_n}"
        saved_to = await asyncio.to_thread(write_binary_output, output_path or None, fallback, response.body)
        return _to_json(
            {
                "success": True,
                "endpoint": "/law_file/{file_type}/{law_id_or_num_or_revision_id}",
                "status": response.status,
                "url": response.url,
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                "saved_to": str(saved_to.resolve()),
                "bytes": len(response.body),
            }
        )
    except ValueError as exc:
        return _error_json(str(exc))
    except error.URLError as exc:
        return _error_json(str(exc), error_type="NetworkError")
    except Exception as exc:  # pragma: no cover
        return _error_json(str(exc), error_type=type(exc).__name__)


@mcp.tool()
async def egov_download_attachment(
    law_revision_id: str,
    src: str = "",
    output_path: str = "",
) -> str:
    """Download law attachment using e-Gov GET /attachment/{law_revision_id}."""
    try:
        await _enforce_rate_limit("egov_download_attachment")
        law_revision_id_n = _validate_law_ref("law_revision_id", law_revision_id)
        path = f"/attachment/{parse.quote(law_revision_id_n, safe='')}"
        src_n = _validate_optional_text("src", src)
        query = {"src": src_n}

        response = await asyncio.to_thread(
            request_endpoint,
            path,
            query,
            base_url=DEFAULT_BASE_URL,
            timeout=DEFAULT_TIMEOUT,
            accept="*/*",
        )
        if response.status >= 400:
            return _http_error_json(
                endpoint="/attachment/{law_revision_id}",
                status=response.status,
                url=response.url,
                body=response.body,
            )

        fallback = Path(src_n).name if src_n else f"attachment_{law_revision_id_n}.zip"
        saved_to = await asyncio.to_thread(write_binary_output, output_path or None, fallback, response.body)
        return _to_json(
            {
                "success": True,
                "endpoint": "/attachment/{law_revision_id}",
                "status": response.status,
                "url": response.url,
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                "saved_to": str(saved_to.resolve()),
                "bytes": len(response.body),
            }
        )
    except ValueError as exc:
        return _error_json(str(exc))
    except error.URLError as exc:
        return _error_json(str(exc), error_type="NetworkError")
    except Exception as exc:  # pragma: no cover
        return _error_json(str(exc), error_type=type(exc).__name__)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
