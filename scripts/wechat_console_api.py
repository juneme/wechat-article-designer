#!/usr/bin/env python3
"""Upload WeChat article assets and create drafts through the console API."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import uuid
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

MAX_IMAGES = 20
MAX_CONTENT_CHARACTERS = 20_000
MAX_CONTENT_BYTES = 1_000_000
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")
IMAGE_HOST = "mmbiz.qpic.cn"
ALLOWED_DRAFT_FIELDS = {
    "request_id",
    "title",
    "author",
    "digest",
    "content",
    "content_source_url",
    "thumb_media_id",
    "need_open_comment",
    "only_fans_can_comment",
}


class ConsoleApiError(RuntimeError):
    def __init__(self, message: str, *, http_status: int | None = None) -> None:
        super().__init__(message)
        self.http_status = http_status


class _ArticleInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.errors: list[str] = []
        self.image_urls: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        lowered = tag.lower()
        if lowered in {"script", "style", "iframe", "object", "embed"}:
            self.errors.append(f"content must not contain <{lowered}>")
        for name, value in attrs:
            if name.lower().startswith("on"):
                self.errors.append(f"content must not contain event attribute {name}")
            if lowered == "img" and name.lower() == "src" and value:
                self.image_urls.append(value.strip())


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConsoleApiError(f"environment variable {name} is required")
    return value


def _base_url() -> str:
    value = _required_env("WECHAT_CONSOLE_URL").rstrip("/")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ConsoleApiError("WECHAT_CONSOLE_URL must be an absolute HTTP(S) URL")
    return value


def _transport_warnings() -> list[str]:
    parsed = urlsplit(_base_url())
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme == "http" and hostname not in {"localhost", "127.0.0.1", "::1"}:
        return [
            "Remote HTTP is not encrypted; API keys and article data may be "
            "intercepted. Enable HTTPS when possible."
        ]
    return []


def _decode_json(raw: bytes, context: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConsoleApiError(f"{context} returned invalid JSON") from exc


def _error_message(exc: HTTPError) -> str:
    try:
        payload = _decode_json(exc.read(), "console API error")
    except ConsoleApiError:
        return f"console API returned HTTP {exc.code}"
    if isinstance(payload, dict):
        detail = payload.get("detail") or payload.get("error") or payload.get("message")
        if isinstance(detail, str) and detail.strip():
            return detail.strip()
        if detail is not None:
            return json.dumps(detail, ensure_ascii=False, separators=(",", ":"))
    return f"console API returned HTTP {exc.code}"


def _request_json(
    method: str,
    path: str,
    *,
    api_key: str | None = None,
    body: bytes | None = None,
    content_type: str | None = None,
    timeout: int = 120,
) -> tuple[int, Any]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "wechat-article-designer/1.0",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if content_type:
        headers["Content-Type"] = content_type
    request = Request(
        f"{_base_url()}{path}", data=body, headers=headers, method=method
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, _decode_json(response.read(), "console API")
    except HTTPError as exc:
        raise ConsoleApiError(
            _error_message(exc), http_status=exc.code
        ) from exc
    except URLError as exc:
        reason = getattr(exc, "reason", exc)
        raise ConsoleApiError(f"cannot reach console API: {reason}") from exc
    except TimeoutError as exc:
        raise ConsoleApiError("console API request timed out") from exc


def _resolve_images(values: list[str]) -> list[Path]:
    if not values:
        raise ConsoleApiError("at least one image path is required")
    if len(values) > MAX_IMAGES:
        raise ConsoleApiError(f"a single upload supports at most {MAX_IMAGES} images")
    paths: list[Path] = []
    for value in values:
        path = Path(value).expanduser()
        if not path.is_file():
            raise ConsoleApiError(f"image file does not exist: {value}")
        paths.append(path.resolve())
    return paths


def _multipart_body(paths: list[Path], mode: str) -> tuple[bytes, str]:
    boundary = f"----WechatArticleDesigner{uuid.uuid4().hex}"
    chunks: list[bytes] = []

    def add(value: str) -> None:
        chunks.append(value.encode("utf-8"))

    add(f"--{boundary}\r\n")
    add('Content-Disposition: form-data; name="mode"\r\n\r\n')
    add(f"{mode}\r\n")
    for path in paths:
        filename = path.name.replace('"', "_").replace("\r", "_").replace("\n", "_")
        media_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        add(f"--{boundary}\r\n")
        add(
            'Content-Disposition: form-data; name="images"; '
            f'filename="{filename}"\r\n'
        )
        add(f"Content-Type: {media_type}\r\n\r\n")
        chunks.append(path.read_bytes())
        add("\r\n")
    add(f"--{boundary}--\r\n")
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def _upload_images(paths: list[Path], mode: str) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    image_key = _required_env("WECHAT_IMAGE_API_KEY")
    for index, path in enumerate(paths):
        body, content_type = _multipart_body([path], mode)
        try:
            _, response = _request_json(
                "POST",
                "/api/v1/wechat-images",
                api_key=image_key,
                body=body,
                content_type=content_type,
            )
            if not isinstance(response, dict) or not isinstance(
                response.get("items"), list
            ):
                raise ConsoleApiError("image API response is missing items")
            if len(response["items"]) != 1 or not isinstance(
                response["items"][0], dict
            ):
                raise ConsoleApiError("image API returned an invalid item")
            normalized = dict(response["items"][0])
            normalized["source_path"] = str(path)
            items.append(normalized)
        except ConsoleApiError as exc:
            if not items:
                raise
            items.append(
                {
                    "source_path": str(path),
                    "filename": path.name,
                    "status": "failed",
                    "errors": [str(exc)],
                    "http_status": exc.http_status,
                }
            )
            for remaining in paths[index + 1 :]:
                items.append(
                    {
                        "source_path": str(remaining),
                        "filename": remaining.name,
                        "status": "failed",
                        "errors": ["not attempted after the previous upload error"],
                    }
                )
            break
    return {
        "operation": "upload_images",
        "mode": mode,
        "items": items,
        "count": len(items),
        "success_count": sum(item.get("status") != "failed" for item in items),
        "error_count": sum(item.get("status") == "failed" for item in items),
    }


def _string_field(
    payload: dict[str, Any],
    name: str,
    *,
    required: bool = False,
    max_length: int | None = None,
) -> str:
    value = payload.get(name, "")
    if not isinstance(value, str):
        raise ConsoleApiError(f"draft field {name} must be a string")
    if required and not value:
        raise ConsoleApiError(f"draft field {name} is required")
    if max_length is not None and len(value) > max_length:
        raise ConsoleApiError(
            f"draft field {name} exceeds {max_length} characters"
        )
    return value


def _flag_field(payload: dict[str, Any], name: str) -> int:
    value = payload.get(name, 0)
    if type(value) is not int or value not in {0, 1}:
        raise ConsoleApiError(f"draft field {name} must be 0 or 1")
    return value


def _validate_content(content: str) -> dict[str, int]:
    characters = len(content)
    byte_count = len(content.encode("utf-8"))
    if characters >= MAX_CONTENT_CHARACTERS:
        raise ConsoleApiError(
            f"draft content must be under {MAX_CONTENT_CHARACTERS} characters; got {characters}"
        )
    if byte_count >= MAX_CONTENT_BYTES:
        raise ConsoleApiError(
            f"draft content must be under {MAX_CONTENT_BYTES} bytes; got {byte_count}"
        )
    inspector = _ArticleInspector()
    try:
        inspector.feed(content)
        inspector.close()
    except Exception as exc:
        raise ConsoleApiError("draft content is not parseable HTML") from exc
    if inspector.errors:
        raise ConsoleApiError("; ".join(dict.fromkeys(inspector.errors)))
    for source in inspector.image_urls:
        parsed = urlsplit(source)
        hostname = (parsed.hostname or "").lower()
        if parsed.scheme != "https" or not parsed.netloc:
            raise ConsoleApiError(f"draft contains a non-HTTPS image URL: {source[:120]}")
        if not (hostname == IMAGE_HOST or hostname.endswith(f".{IMAGE_HOST}")):
            raise ConsoleApiError(
                "draft images must use article_url values returned by the image API: "
                f"{source[:120]}"
            )
    return {
        "characters": characters,
        "bytes": byte_count,
        "images": len(inspector.image_urls),
    }


def _load_draft(path_value: str) -> tuple[dict[str, Any], dict[str, int]]:
    path = Path(path_value).expanduser()
    if not path.is_file():
        raise ConsoleApiError(f"article JSON file does not exist: {path_value}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConsoleApiError(f"cannot read article JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ConsoleApiError("article JSON must contain one object")
    unknown = sorted(set(payload) - ALLOWED_DRAFT_FIELDS)
    if unknown:
        raise ConsoleApiError(f"article JSON contains unknown fields: {', '.join(unknown)}")

    request_id = _string_field(payload, "request_id", required=True)
    if not REQUEST_ID_PATTERN.fullmatch(request_id):
        raise ConsoleApiError(
            "draft field request_id must be 8-128 characters using letters, digits, . _ : or -"
        )
    title = _string_field(payload, "title", required=True, max_length=32)
    author = _string_field(payload, "author", max_length=16)
    digest = _string_field(payload, "digest", max_length=120)
    content = _string_field(payload, "content", required=True)
    content_source_url = _string_field(
        payload, "content_source_url", max_length=1024
    )
    thumb_media_id = _string_field(
        payload, "thumb_media_id", required=True, max_length=256
    )
    normalized = {
        "request_id": request_id,
        "title": title,
        "author": author,
        "digest": digest,
        "content": content,
        "content_source_url": content_source_url,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": _flag_field(payload, "need_open_comment"),
        "only_fans_can_comment": _flag_field(payload, "only_fans_can_comment"),
    }
    return normalized, _validate_content(content)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Use the WeChat console API from the article designer skill."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="check console health and local configuration")

    upload = subparsers.add_parser(
        "upload-images", help="upload one or more article or material images"
    )
    upload.add_argument("images", nargs="+")
    upload.add_argument(
        "--mode", choices=("article", "material", "both"), default="article"
    )

    cover = subparsers.add_parser(
        "upload-cover", help="upload one cover as permanent WeChat material"
    )
    cover.add_argument("image")

    validate = subparsers.add_parser(
        "validate-draft", help="validate article JSON without creating a draft"
    )
    validate.add_argument("--article", required=True)

    create = subparsers.add_parser(
        "create-draft", help="create an idempotent WeChat draft"
    )
    create.add_argument("--article", required=True)
    return parser


def _run(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    if args.command == "status":
        _, server = _request_json("GET", "/healthz", timeout=15)
        return {
            "operation": "status",
            "console_url": _base_url(),
            "image_api_key_configured": bool(
                os.environ.get("WECHAT_IMAGE_API_KEY", "").strip()
            ),
            "publish_api_key_configured": bool(
                os.environ.get("WECHAT_PUBLISH_API_KEY", "").strip()
            ),
            "server": server,
            "warnings": _transport_warnings(),
        }, 0
    if args.command == "upload-images":
        result = _upload_images(_resolve_images(args.images), args.mode)
        result["warnings"] = _transport_warnings()
        has_errors = bool(result.get("error_count")) or any(
            item.get("status") != "complete"
            or bool(item.get("errors"))
            or (args.mode in {"article", "both"} and not item.get("article_url"))
            or (args.mode in {"material", "both"} and not item.get("media_id"))
            for item in result["items"]
        )
        return result, 2 if has_errors else 0
    if args.command == "upload-cover":
        result = _upload_images(_resolve_images([args.image]), "material")
        item = result["items"][0]
        if (
            item.get("status") != "complete"
            or item.get("errors")
            or not item.get("media_id")
        ):
            raise ConsoleApiError("cover upload did not return a permanent media_id")
        return {
            "operation": "upload_cover",
            "source_path": item["source_path"],
            "filename": item.get("filename"),
            "media_id": item["media_id"],
            "material_url": item.get("material_url") or item.get("url"),
            "item": item,
            "warnings": _transport_warnings(),
        }, 0
    if args.command == "validate-draft":
        draft, validation = _load_draft(args.article)
        return {
            "operation": "validate_draft",
            "valid": True,
            "request_id": draft["request_id"],
            "title": draft["title"],
            "thumb_media_id": draft["thumb_media_id"],
            "validation": validation,
        }, 0
    if args.command == "create-draft":
        draft, validation = _load_draft(args.article)
        body = json.dumps(draft, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
        http_status, response = _request_json(
            "POST",
            "/api/v1/wechat-drafts",
            api_key=_required_env("WECHAT_PUBLISH_API_KEY"),
            body=body,
            content_type="application/json; charset=utf-8",
        )
        if not isinstance(response, dict):
            raise ConsoleApiError("draft API returned an invalid response")
        result = dict(response)
        result.update(
            {
                "operation": "create_draft",
                "local_validation": validation,
                "warnings": _transport_warnings(),
            }
        )
        if http_status == 202 or response.get("status") == "pending":
            return result, 2
        if (
            response.get("status") != "created"
            or not response.get("media_id")
            or response.get("request_id") != draft["request_id"]
        ):
            raise ConsoleApiError("draft API did not confirm draft creation")
        return result, 0
    raise ConsoleApiError(f"unsupported command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        result, exit_code = _run(args)
    except ConsoleApiError as exc:
        error: dict[str, Any] = {"ok": False, "error": str(exc)}
        if exc.http_status is not None:
            error["http_status"] = exc.http_status
        print(json.dumps(error, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
