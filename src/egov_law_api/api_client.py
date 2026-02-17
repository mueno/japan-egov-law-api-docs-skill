"""Shared client helpers for e-Gov Law API v2."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib import error, parse, request

DEFAULT_BASE_URL = os.environ.get("EGOV_LAW_API_BASE_URL", "https://laws.e-gov.go.jp/api/2")
DEFAULT_TIMEOUT = float(os.environ.get("EGOV_LAW_API_TIMEOUT_SECONDS", "30"))
E_GOV_TERMS_URL = "https://laws.e-gov.go.jp/terms/"
E_GOV_ATTRIBUTION_TEMPLATE = "出典: e-Gov法令検索 (https://laws.e-gov.go.jp/) （YYYY年MM月DD日利用）"
E_GOV_EDIT_NOTICE_TEMPLATE = "本資料は e-Gov法令検索の情報をもとに作成し、編集・加工しています。"
E_GOV_USAGE_NOTE = (
    "再配布時はe-Gov利用規約に従い、出典表示と必要な改変明示を行ってください。"
)


@dataclass(frozen=True)
class ApiResponse:
    """HTTP response details returned from e-Gov API."""

    url: str
    status: int
    headers: dict[str, str]
    body: bytes


def parse_query_items(items: Iterable[str]) -> dict[str, Any]:
    """Parse repeated KEY=VALUE pairs into a dictionary."""
    query: dict[str, Any] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid --query value: {item!r}. Use key=value.")
        key, value = item.split("=", 1)
        if not key:
            raise ValueError(f"Invalid --query key in value: {item!r}.")
        current = query.get(key)
        if current is None:
            query[key] = value
            continue
        if isinstance(current, list):
            current.append(value)
            continue
        query[key] = [current, value]
    return query


def build_url(base_url: str, path: str, query: dict[str, Any] | None = None) -> str:
    """Build a URL with optional query parameters."""
    normalized = base_url.rstrip("/")
    full_path = f"{normalized}/{path.lstrip('/')}"
    if not query:
        return full_path
    filtered = {k: v for k, v in query.items() if v is not None}
    if not filtered:
        return full_path
    return f"{full_path}?{parse.urlencode(filtered, doseq=True)}"


def fetch(url: str, timeout: float, accept: str) -> ApiResponse:
    """Fetch a URL and return status, headers, and body."""
    req = request.Request(url, headers={"Accept": accept})
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return ApiResponse(url=url, status=resp.status, headers=headers, body=resp.read())
    except error.HTTPError as exc:
        headers = {k.lower(): v for k, v in exc.headers.items()} if exc.headers else {}
        return ApiResponse(url=url, status=exc.code, headers=headers, body=exc.read())


def request_endpoint(
    path: str,
    query: dict[str, Any] | None = None,
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT,
    accept: str = "application/json, application/xml",
) -> ApiResponse:
    """Call e-Gov endpoint and return ApiResponse."""
    url = build_url(base_url=base_url, path=path, query=query)
    return fetch(url=url, timeout=timeout, accept=accept)


def decode_bytes(raw: bytes) -> str:
    """Decode bytes payload as UTF-8 with replacement fallback."""
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("utf-8", errors="replace")


def parse_json_text(text: str) -> Any:
    """Parse JSON text and return Python object."""
    return json.loads(text)


def format_payload(body: bytes, headers: dict[str, str], *, raw: bool = False) -> str:
    """Render payload as pretty JSON when possible."""
    text = decode_bytes(body)
    if raw:
        return text
    content_type = headers.get("content-type", "").lower()
    if "application/json" in content_type:
        try:
            return json.dumps(parse_json_text(text), ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            return text
    return text


def bool_query(enabled: bool) -> str | None:
    """Convert bool to e-Gov API query string form."""
    return "true" if enabled else None


def resolve_binary_output(path: str | None, fallback: str) -> Path:
    """Resolve output path for binary downloads."""
    if path:
        return Path(path).expanduser()
    return Path(fallback)


def write_binary_output(path: str | None, fallback: str, payload: bytes) -> Path:
    """Write binary payload to disk and return output path."""
    out_path = resolve_binary_output(path, fallback)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(payload)
    return out_path


def source_terms() -> dict[str, str]:
    """Return reusable source attribution metadata for e-Gov-derived outputs."""
    return {
        "terms_url": E_GOV_TERMS_URL,
        "attribution_template": E_GOV_ATTRIBUTION_TEMPLATE,
        "edited_content_template": E_GOV_EDIT_NOTICE_TEMPLATE,
        "usage_note": E_GOV_USAGE_NOTE,
    }
