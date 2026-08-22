#!/usr/bin/env python3
"""Create and maintain versioned workspaces for WeChat articles."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import unicodedata
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any

START = "<!-- 微信公众号复制开始 -->"
END = "<!-- 微信公众号复制结束 -->"
WINDOWS_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


class WorkspaceError(RuntimeError):
    pass


def _now() -> datetime:
    return datetime.now().astimezone()


def _slug(value: str, *, limit: int = 64) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip()
    normalized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", normalized)
    normalized = re.sub(r"\s+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip(" ._")
    normalized = normalized[:limit].rstrip(" ._") or "未命名文章"
    if normalized.upper() in WINDOWS_RESERVED:
        normalized = f"文章_{normalized}"
    return normalized


def _atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(value, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _write_json(path: Path, value: dict[str, Any]) -> None:
    _atomic_write_text(
        path,
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
    )


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise WorkspaceError(f"cannot read JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WorkspaceError(f"JSON root must be an object: {path}")
    return value


def _extract_fragment(raw: str) -> str:
    if START not in raw or END not in raw:
        raise WorkspaceError("fragment.html must contain both WeChat boundary comments")
    prefix, remainder = raw.split(START, 1)
    fragment, suffix = remainder.split(END, 1)
    if START in prefix or END in suffix or START in fragment or END in fragment:
        raise WorkspaceError("fragment.html must contain exactly one boundary pair")
    value = fragment.strip()
    if not value:
        raise WorkspaceError("fragment.html contains no publishable markup")
    return value


def _preview_html(title: str, fragment: str) -> str:
    escaped_title = (
        title.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{escaped_title} - 微信预览</title>
  <style>
    html {{ background:#e9e9e7; }}
    body {{ box-sizing:border-box;width:min(100%,390px);min-height:100vh;margin:0 auto;padding:0;background:#fff;color:#202020; }}
    img,svg {{ max-width:100%; }}
  </style>
</head>
<body>
{fragment}
</body>
</html>
"""


def _payload_hash(payload: dict[str, Any]) -> str:
    comparable = {key: value for key, value in payload.items() if key != "request_id"}
    encoded = json.dumps(
        comparable,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _request_id(article_id: str, revision: int, timestamp: datetime) -> str:
    stamp = timestamp.strftime("%Y%m%d%H%M%S%f")
    return f"article-{article_id[:12]}-r{revision:03d}-{stamp}"


def _next_available(root: Path, stem: str) -> Path:
    candidate = root / stem
    counter = 2
    while candidate.exists():
        candidate = root / f"{stem}_{counter}"
        counter += 1
    return candidate


def create_workspace(root: Path, title: str, article_date: date) -> dict[str, Any]:
    root = root.expanduser().resolve()
    article_dir = _next_available(root, f"{article_date.isoformat()}_{_slug(title)}")
    article_dir.mkdir(parents=True)
    (article_dir / "assets").mkdir()
    (article_dir / "revisions").mkdir()

    article_id = uuid.uuid4().hex
    timestamp = _now()
    fragment = '<section style="margin:0;padding:0;background:#FFFFFF;color:#202020;"></section>'
    fragment_file = f"{START}\n{fragment}\n{END}\n"
    article = {
        "request_id": _request_id(article_id, 1, timestamp),
        "title": title,
        "author": "",
        "digest": "",
        "content": fragment,
        "content_source_url": "",
        "thumb_media_id": "",
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }
    manifest = {
        "schema_version": 1,
        "article_id": article_id,
        "title": title,
        "slug": _slug(title),
        "article_date": article_date.isoformat(),
        "created_at": timestamp.isoformat(),
        "updated_at": timestamp.isoformat(),
        "revision": 0,
        "draft_payload_sha256": None,
    }
    _atomic_write_text(article_dir / "fragment.html", fragment_file)
    _atomic_write_text(article_dir / "preview.html", _preview_html(title, fragment))
    _write_json(article_dir / "article.json", article)
    _write_json(article_dir / "manifest.json", manifest)
    return {
        "ok": True,
        "operation": "create",
        "article_dir": str(article_dir),
        "article_id": article_id,
    }


def _snapshot(article_dir: Path, revision: int, timestamp: datetime) -> Path:
    revision_dir = article_dir / "revisions" / (
        f"r{revision:03d}_{timestamp.strftime('%Y%m%d-%H%M%S')}"
    )
    revision_dir.mkdir(parents=True, exist_ok=False)
    for filename in ("article.json", "fragment.html", "preview.html", "manifest.json"):
        source = article_dir / filename
        if source.is_file():
            shutil.copy2(source, revision_dir / filename)
    assets = article_dir / "assets"
    if assets.is_dir():
        shutil.copytree(assets, revision_dir / "assets")
    return revision_dir


def sync_workspace(article_dir: Path) -> dict[str, Any]:
    article_dir = article_dir.expanduser().resolve()
    manifest_path = article_dir / "manifest.json"
    article_path = article_dir / "article.json"
    fragment_path = article_dir / "fragment.html"
    if not article_dir.is_dir():
        raise WorkspaceError(f"article workspace does not exist: {article_dir}")
    manifest = _read_json(manifest_path)
    article = _read_json(article_path)
    try:
        raw_fragment = fragment_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise WorkspaceError(f"cannot read {fragment_path}: {exc}") from exc
    fragment = _extract_fragment(raw_fragment)
    title = article.get("title")
    if not isinstance(title, str) or not title.strip():
        raise WorkspaceError("article.json title must be a non-empty string")
    article["content"] = fragment
    new_hash = _payload_hash(article)
    changed = new_hash != manifest.get("draft_payload_sha256")
    timestamp = _now()
    revision_dir: Path | None = None
    if changed:
        revision = int(manifest.get("revision", 0)) + 1
        article_id = manifest.get("article_id")
        if not isinstance(article_id, str) or not article_id:
            raise WorkspaceError("manifest.json is missing article_id")
        article["request_id"] = _request_id(article_id, revision, timestamp)
        manifest["revision"] = revision
        manifest["draft_payload_sha256"] = _payload_hash(article)
    manifest["title"] = title
    manifest["slug"] = _slug(title)
    manifest["updated_at"] = timestamp.isoformat()
    _write_json(article_path, article)
    _atomic_write_text(article_dir / "preview.html", _preview_html(title, fragment))
    _write_json(manifest_path, manifest)
    if changed:
        revision_dir = _snapshot(article_dir, int(manifest["revision"]), timestamp)
    return {
        "ok": True,
        "operation": "sync",
        "article_dir": str(article_dir),
        "changed": changed,
        "revision": manifest.get("revision", 0),
        "request_id": article.get("request_id"),
        "revision_dir": str(revision_dir) if revision_dir else None,
    }


def _date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create and synchronize versioned WeChat article workspaces"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create", help="create a new article workspace")
    create.add_argument("--title", required=True)
    create.add_argument("--date", type=_date, default=date.today())
    create.add_argument("--root", default="articles")
    sync = subparsers.add_parser(
        "sync", help="sync fragment, preview, draft payload, and revision snapshot"
    )
    sync.add_argument("article_dir")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "create":
            result = create_workspace(Path(args.root), args.title, args.date)
        else:
            result = sync_workspace(Path(args.article_dir))
    except (OSError, WorkspaceError, ValueError) as exc:
        print(
            json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
