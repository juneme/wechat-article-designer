#!/usr/bin/env python3
"""Create and maintain versioned workspaces for WeChat articles."""

from __future__ import annotations

import argparse
import hashlib
import html
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
TRACKED_FILES = (
    "article.json",
    "fragment.html",
    "preview.html",
    "release-manifest.json",
    "design-report.json",
    "design-report.md",
    "design-contract.json",
    "design-contract.md",
    "manifest.json",
)
WINDOWS_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}
MEDIA_STATES = {
    "placeholder",
    "generated-local",
    "supplied-local",
    "hosted",
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


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    ).encode("utf-8")


def _atomic_write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_bytes(value)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_write_text(path: Path, value: str) -> None:
    _atomic_write_bytes(path, value.replace("\r\n", "\n").encode("utf-8"))


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value: Any = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise WorkspaceError(f"cannot read JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WorkspaceError(f"JSON root must be an object: {path}")
    return value


def update_runtime_manifest(article_dir: Path, **values: Any) -> dict[str, Any]:
    article_dir = article_dir.expanduser().resolve()
    path = article_dir / "manifest.json"
    manifest = _read_json(path)
    if manifest.get("schema_version") != 4:
        raise WorkspaceError("runtime state requires a schema-4 workspace")
    manifest.update(values)
    manifest["updated_at"] = _now().isoformat()
    _atomic_write_bytes(path, _json_bytes(manifest))
    return manifest


def _extract_fragment(raw: str) -> str:
    if raw.count(START) != 1 or raw.count(END) != 1:
        raise WorkspaceError("fragment.html must contain exactly one WeChat boundary pair")
    if raw.index(START) > raw.index(END):
        raise WorkspaceError("fragment.html boundary comments are reversed")
    prefix, remainder = raw.split(START, 1)
    fragment, suffix = remainder.split(END, 1)
    if prefix.strip() or suffix.strip():
        raise WorkspaceError(
            "fragment.html may contain only boundary comments and publishable markup"
        )
    value = fragment.strip()
    if not value:
        raise WorkspaceError("fragment.html contains no publishable markup")
    return value


def _fragment_file(fragment: str) -> str:
    return f"{START}\n{fragment.strip()}\n{END}\n"


def _preview_sources(fragment: str, release: dict[str, Any]) -> str:
    result = fragment
    for item in release.get("media", []):
        if not isinstance(item, dict) or item.get("placement") != "body":
            continue
        name = item.get("name")
        source = item.get("source_path")
        if not isinstance(name, str) or not isinstance(source, str) or not source:
            continue
        escaped_name = re.escape(name)
        local_url = "assets/" + source.replace("\\", "/")
        result = re.sub(
            rf"(?P<quote>['\"])wechat-media://{escaped_name}(?P=quote)",
            lambda match: f'{match.group("quote")}{html.escape(local_url, quote=True)}'
            f'{match.group("quote")}',
            result,
            flags=re.IGNORECASE,
        )
    return result


def _preview_html(title: str, fragment: str, release: dict[str, Any]) -> str:
    escaped_title = html.escape(title, quote=True)
    preview_fragment = _preview_sources(fragment, release)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{escaped_title} - 微信预览</title>
  <style>
    html {{ background:#e9e9e7; }}
    body {{ box-sizing:border-box;width:320px;min-height:100vh;margin:0 auto;padding:0;background:#fff;color:#202020; }}
    img,svg {{ max-width:100%; }}
  </style>
</head>
<body>
{preview_fragment}
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


def empty_release_manifest(title: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "article_title": title,
        "media": [],
        "delivery": {
            "target": "auto",
            "backend_ready": False,
            "user_requested_preview_only": False,
            "fallback_reason": "",
            "image_generation_status": "not-required",
            "image_generation_reason": "",
        },
    }


def validate_release_manifest(value: dict[str, Any], title: str | None = None) -> None:
    if value.get("schema_version") != 1:
        raise WorkspaceError("release-manifest.json schema_version must be 1")
    article_title = value.get("article_title")
    if not isinstance(article_title, str) or not article_title.strip():
        raise WorkspaceError("release-manifest.json article_title must be non-empty")
    if title is not None and article_title != title:
        raise WorkspaceError(
            "release-manifest.json article_title must match article.json title"
        )
    media = value.get("media")
    if not isinstance(media, list):
        raise WorkspaceError("release-manifest.json media must be an array")
    names: set[str] = set()
    covers = 0
    for index, item in enumerate(media):
        if not isinstance(item, dict):
            raise WorkspaceError(f"release media item {index} must be an object")
        name = item.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{1,80}", name):
            raise WorkspaceError(
                f"release media item {index} has an invalid machine-readable name"
            )
        if name in names:
            raise WorkspaceError(f"release media name is duplicated: {name}")
        names.add(name)
        placement = item.get("placement")
        if placement not in {"body", "cover"}:
            raise WorkspaceError(f"release media {name!r} placement must be body or cover")
        covers += placement == "cover"
        if item.get("state") not in MEDIA_STATES:
            raise WorkspaceError(f"release media {name!r} has an invalid state")
        if type(item.get("required")) is not bool:
            raise WorkspaceError(f"release media {name!r} required must be boolean")
        for field in ("source_path", "remote_ref"):
            if not isinstance(item.get(field, ""), str):
                raise WorkspaceError(f"release media {name!r} {field} must be a string")
        source = item.get("source_path", "")
        if source:
            source_path = Path(source)
            if source_path.is_absolute() or source_path.drive or ".." in source_path.parts:
                raise WorkspaceError(
                    f"release media {name!r} source_path must stay under assets/"
                )
    if covers > 1:
        raise WorkspaceError("release-manifest.json may contain only one cover")
    delivery = value.get("delivery")
    if not isinstance(delivery, dict):
        raise WorkspaceError("release-manifest.json delivery must be an object")
    if delivery.get("target") not in {"auto", "direct-draft", "local-preview"}:
        raise WorkspaceError("release delivery target is invalid")
    for field in ("backend_ready", "user_requested_preview_only"):
        if type(delivery.get(field)) is not bool:
            raise WorkspaceError(f"release delivery {field} must be boolean")
    for field in ("fallback_reason", "image_generation_reason"):
        if not isinstance(delivery.get(field), str):
            raise WorkspaceError(f"release delivery {field} must be a string")
    if delivery.get("image_generation_status") not in {
        "not-required",
        "pending",
        "complete",
        "failed",
    }:
        raise WorkspaceError("release delivery image_generation_status is invalid")


def load_release_manifest(article_dir: Path, title: str | None = None) -> dict[str, Any]:
    path = article_dir / "release-manifest.json"
    if not path.is_file():
        raise WorkspaceError(
            "release-manifest.json is missing; run article_workspace.py migrate"
        )
    value = _read_json(path)
    validate_release_manifest(value, title)
    return value


def _asset_inventory(assets: Path) -> list[dict[str, Any]]:
    if not assets.is_dir():
        return []
    result: list[dict[str, Any]] = []
    for path in sorted(item for item in assets.rglob("*") if item.is_file()):
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        result.append(
            {
                "path": path.relative_to(assets).as_posix(),
                "sha256": digest.hexdigest(),
                "bytes": path.stat().st_size,
            }
        )
    return result


def _state_hash(
    article_dir: Path,
    article: dict[str, Any],
    release: dict[str, Any],
    fragment_file: str,
    preview: bytes | None,
) -> str:
    state: dict[str, Any] = {
        "article": article,
        "release": release,
        "fragment_sha256": hashlib.sha256(fragment_file.encode("utf-8")).hexdigest(),
        "preview_sha256": hashlib.sha256(preview).hexdigest() if preview else None,
        "assets": _asset_inventory(article_dir / "assets"),
    }
    for filename in (
        "design-report.json",
        "design-report.md",
        "design-contract.json",
        "design-contract.md",
    ):
        path = article_dir / filename
        if path.is_file():
            state[filename] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashlib.sha256(
        json.dumps(state, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _restore_files(article_dir: Path, backups: dict[str, bytes | None]) -> None:
    for name, value in backups.items():
        path = article_dir / name
        if value is None:
            path.unlink(missing_ok=True)
        else:
            _atomic_write_bytes(path, value)


def _snapshot(article_dir: Path, revision: int, timestamp: datetime) -> Path:
    root = article_dir / "revisions"
    root.mkdir(parents=True, exist_ok=True)
    revision_dir = root / (
        f"r{revision:03d}_{timestamp.strftime('%Y%m%d-%H%M%S-%f')}"
    )
    revision_dir.mkdir(parents=False, exist_ok=False)
    try:
        for filename in TRACKED_FILES:
            source = article_dir / filename
            if source.is_file():
                shutil.copy2(source, revision_dir / filename)
        assets = article_dir / "assets"
        if assets.is_dir():
            shutil.copytree(assets, revision_dir / "assets")
    except Exception:
        shutil.rmtree(revision_dir, ignore_errors=True)
        raise
    return revision_dir


def _workspace_files(article_dir: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    article_dir = article_dir.expanduser().resolve()
    if not article_dir.is_dir():
        raise WorkspaceError(f"article workspace does not exist: {article_dir}")
    manifest = _read_json(article_dir / "manifest.json")
    article = _read_json(article_dir / "article.json")
    try:
        fragment_file = (article_dir / "fragment.html").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise WorkspaceError(f"cannot read fragment.html: {exc}") from exc
    _extract_fragment(fragment_file)
    return manifest, article, fragment_file


def create_workspace(
    root: Path,
    title: str,
    article_date: date,
    *,
    local_preview: bool = True,
) -> dict[str, Any]:
    root = root.expanduser().resolve()
    article_dir = _next_available(root, f"{article_date.isoformat()}_{_slug(title)}")
    article_dir.mkdir(parents=True)
    (article_dir / "assets").mkdir()
    (article_dir / "revisions").mkdir()

    timestamp = _now()
    article_id = uuid.uuid4().hex
    fragment = (
        '<section style="margin:0;padding:0;background:#FFFFFF;color:#202020;'
        'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',\'Microsoft YaHei\','
        'sans-serif;"></section>'
    )
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
    release = empty_release_manifest(title)
    fragment_file = _fragment_file(fragment)
    preview = (
        _preview_html(title, fragment, release).encode("utf-8")
        if local_preview
        else None
    )
    manifest = {
        "schema_version": 4,
        "architecture": "free-composition-postflight",
        "article_id": article_id,
        "title": title,
        "slug": _slug(title),
        "article_date": article_date.isoformat(),
        "created_at": timestamp.isoformat(),
        "updated_at": timestamp.isoformat(),
        "revision": 1,
        "state_sha256": "",
        "draft_payload_sha256": _payload_hash(article),
        "local_preview_enabled": local_preview,
        "draft_submission": None,
        "image_generation_attempt": None,
    }
    manifest["state_sha256"] = _state_hash(
        article_dir, article, release, fragment_file, preview
    )
    try:
        _atomic_write_text(article_dir / "fragment.html", fragment_file)
        _atomic_write_bytes(article_dir / "article.json", _json_bytes(article))
        _atomic_write_bytes(
            article_dir / "release-manifest.json", _json_bytes(release)
        )
        if preview is not None:
            _atomic_write_bytes(article_dir / "preview.html", preview)
        _atomic_write_bytes(article_dir / "manifest.json", _json_bytes(manifest))
        revision_dir = _snapshot(article_dir, 1, timestamp)
    except Exception:
        shutil.rmtree(article_dir, ignore_errors=True)
        raise
    return {
        "ok": True,
        "operation": "create",
        "article_dir": str(article_dir),
        "article_id": article_id,
        "revision": 1,
        "revision_dir": str(revision_dir),
        "preview_file": str(article_dir / "preview.html") if local_preview else None,
    }


def sync_workspace(article_dir: Path) -> dict[str, Any]:
    article_dir = article_dir.expanduser().resolve()
    manifest, article, raw_fragment = _workspace_files(article_dir)
    submission = manifest.get("draft_submission")
    if isinstance(submission, dict) and submission.get("state") in {
        "submitting",
        "ambiguous",
    }:
        raise WorkspaceError(
            "workspace has an unresolved draft submission; run resolve-draft first"
        )
    title = article.get("title")
    if not isinstance(title, str) or not title.strip():
        raise WorkspaceError("article.json title must be a non-empty string")
    release = load_release_manifest(article_dir, title)
    fragment = _extract_fragment(raw_fragment)
    fragment_file = _fragment_file(fragment)
    article["content"] = fragment

    article_id = manifest.get("article_id")
    if not isinstance(article_id, str) or not article_id:
        raise WorkspaceError("manifest.json is missing article_id")
    old_payload_hash = manifest.get("draft_payload_sha256")
    new_payload_hash = _payload_hash(article)
    payload_changed = old_payload_hash != new_payload_hash
    timestamp = _now()
    current_revision = manifest.get("revision", 0)
    if type(current_revision) is not int or current_revision < 0:
        raise WorkspaceError("manifest revision must be a non-negative integer")
    if payload_changed:
        article["request_id"] = _request_id(
            article_id, current_revision + 1, timestamp
        )
        new_payload_hash = _payload_hash(article)
        manifest["draft_submission"] = None

    local_preview = manifest.get("local_preview_enabled") is True
    preview = (
        _preview_html(title, fragment, release).encode("utf-8")
        if local_preview
        else None
    )
    new_state_hash = _state_hash(
        article_dir, article, release, fragment_file, preview
    )
    changed = new_state_hash != manifest.get("state_sha256")
    revision = current_revision + 1 if changed else current_revision
    manifest.update(
        {
            "schema_version": 4,
            "architecture": "free-composition-postflight",
            "title": title,
            "slug": _slug(title),
            "revision": revision,
            "state_sha256": new_state_hash,
            "draft_payload_sha256": new_payload_hash,
        }
    )
    if changed:
        manifest["updated_at"] = timestamp.isoformat()

    backups = {
        name: (article_dir / name).read_bytes()
        if (article_dir / name).is_file()
        else None
        for name in TRACKED_FILES
    }
    revision_dir: Path | None = None
    try:
        _atomic_write_text(article_dir / "fragment.html", fragment_file)
        _atomic_write_bytes(article_dir / "article.json", _json_bytes(article))
        _atomic_write_bytes(
            article_dir / "release-manifest.json", _json_bytes(release)
        )
        if preview is None:
            (article_dir / "preview.html").unlink(missing_ok=True)
        else:
            _atomic_write_bytes(article_dir / "preview.html", preview)
        _atomic_write_bytes(article_dir / "manifest.json", _json_bytes(manifest))
        if changed:
            revision_dir = _snapshot(article_dir, revision, timestamp)
    except Exception:
        _restore_files(article_dir, backups)
        raise
    return {
        "ok": True,
        "operation": "sync",
        "article_dir": str(article_dir),
        "changed": changed,
        "payload_changed": payload_changed,
        "revision": revision,
        "request_id": article.get("request_id"),
        "revision_dir": str(revision_dir) if revision_dir else None,
        "preview_file": str(article_dir / "preview.html") if local_preview else None,
    }


def _legacy_release_manifest(article_dir: Path, title: str) -> dict[str, Any]:
    release = empty_release_manifest(title)
    contract_path = article_dir / "design-contract.json"
    if not contract_path.is_file():
        return release
    contract = _read_json(contract_path)
    media = contract.get("media", {})
    assets = media.get("assets", []) if isinstance(media, dict) else []
    if isinstance(assets, list):
        for index, item in enumerate(assets):
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            if not isinstance(name, str) or not re.fullmatch(
                r"[A-Za-z0-9._:-]{1,80}", name
            ):
                name = f"legacy-media-{index + 1}"
            release["media"].append(
                {
                    "name": name,
                    "placement": item.get("placement")
                    if item.get("placement") in {"body", "cover"}
                    else "body",
                    "required": item.get("required") is True,
                    "state": item.get("state")
                    if item.get("state") in MEDIA_STATES
                    else "placeholder",
                    "source_path": item.get("source_path")
                    if isinstance(item.get("source_path"), str)
                    else "",
                    "remote_ref": item.get("remote_ref")
                    if isinstance(item.get("remote_ref"), str)
                    else "",
                }
            )
    return release


def migrate_workspace(article_dir: Path) -> dict[str, Any]:
    article_dir = article_dir.expanduser().resolve()
    manifest, article, _ = _workspace_files(article_dir)
    title = article.get("title")
    if not isinstance(title, str) or not title.strip():
        raise WorkspaceError("article.json title must be a non-empty string")
    release_path = article_dir / "release-manifest.json"
    created_release_manifest = not release_path.is_file()
    backups = {
        name: (article_dir / name).read_bytes()
        if (article_dir / name).is_file()
        else None
        for name in TRACKED_FILES
    }
    try:
        if created_release_manifest:
            release = _legacy_release_manifest(article_dir, title)
            _atomic_write_bytes(release_path, _json_bytes(release))
        else:
            validate_release_manifest(_read_json(release_path), title)
        timestamp = _now()
        manifest.update(
            {
                "schema_version": 4,
                "architecture": "free-composition-postflight",
                "title": title,
                "slug": _slug(title),
                "local_preview_enabled": (article_dir / "preview.html").is_file(),
                "updated_at": timestamp.isoformat(),
            }
        )
        manifest.setdefault("revision", 0)
        manifest.setdefault("draft_submission", None)
        manifest.setdefault("image_generation_attempt", None)
        manifest["state_sha256"] = ""
        _atomic_write_bytes(article_dir / "manifest.json", _json_bytes(manifest))
        result = sync_workspace(article_dir)
    except Exception:
        _restore_files(article_dir, backups)
        raise
    result.update(
        {
            "operation": "migrate",
            "created_release_manifest": created_release_manifest,
            "legacy_design_contract_preserved": (
                article_dir / "design-contract.json"
            ).is_file(),
        }
    )
    return result


def inspect_workspace(article_dir: Path) -> dict[str, Any]:
    article_dir = article_dir.expanduser().resolve()
    _, article, raw_fragment = _workspace_files(article_dir)
    fragment = _extract_fragment(raw_fragment)
    report = {
        "schema_version": 1,
        "generated_at": _now().isoformat(),
        "advisory_only": True,
        "article_title": article.get("title", ""),
        "observations": {
            "svg_scenes": len(re.findall(r"<svg\b", fragment, re.IGNORECASE)),
            "motion_nodes": len(
                re.findall(r"<(?:animate|animateTransform|set)\b", fragment, re.IGNORECASE)
            ),
            "colors": sorted(set(re.findall(r"#[0-9A-Fa-f]{3,8}\b", fragment))),
            "font_sizes": sorted(
                set(
                    re.findall(
                        r"font-size\s*:\s*([^;\"']+)",
                        fragment,
                        re.IGNORECASE,
                    )
                )
            ),
            "legacy_design_markers": len(
                re.findall(
                    r"\bdata-(?:type-role|module-id|density|spacing-role|geometry-role)=",
                    fragment,
                    re.IGNORECASE,
                )
            ),
        },
    }
    observations = report["observations"]
    markdown = (
        "# Post-composition design report\n\n"
        "This report is advisory. It is never a release gate.\n\n"
        f"- SVG scenes: {observations['svg_scenes']}\n"
        f"- Motion nodes: {observations['motion_nodes']}\n"
        f"- Distinct color tokens: {len(observations['colors'])}\n"
        f"- Font-size values: {', '.join(observations['font_sizes']) or 'none'}\n"
        f"- Legacy design markers: {observations['legacy_design_markers']}\n"
    )
    backups = {
        name: (article_dir / name).read_bytes()
        if (article_dir / name).is_file()
        else None
        for name in TRACKED_FILES
    }
    try:
        _atomic_write_bytes(article_dir / "design-report.json", _json_bytes(report))
        _atomic_write_text(article_dir / "design-report.md", markdown)
        result = sync_workspace(article_dir)
    except Exception:
        _restore_files(article_dir, backups)
        raise
    return {
        "ok": True,
        "operation": "inspect",
        "advisory_only": True,
        "report": report,
        "sync": result,
    }


def resolve_draft_submission(article_dir: Path, outcome: str) -> dict[str, Any]:
    article_dir = article_dir.expanduser().resolve()
    manifest = _read_json(article_dir / "manifest.json")
    submission = manifest.get("draft_submission")
    if not isinstance(submission, dict) or submission.get("state") not in {
        "submitting",
        "ambiguous",
    }:
        raise WorkspaceError("workspace has no unresolved draft submission")
    resolved = dict(submission)
    resolved.update(
        {
            "state": outcome,
            "updated_at": _now().isoformat(),
            "reason": "Resolved by the user after inspecting the real draft box.",
        }
    )
    update_runtime_manifest(article_dir, draft_submission=resolved)
    return {
        "ok": True,
        "operation": "resolve-draft",
        "outcome": outcome,
        "request_id": resolved.get("request_id"),
    }


def _date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create and synchronize free-composition WeChat article workspaces"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create", help="create a new article workspace")
    create.add_argument("--title", required=True)
    create.add_argument("--date", type=_date, default=date.today())
    create.add_argument("--root", default="articles")
    create.add_argument(
        "--no-preview",
        action="store_true",
        help="omit preview.html for an expected direct-draft route",
    )
    sync = subparsers.add_parser(
        "sync", help="transactionally synchronize article state and revisions"
    )
    sync.add_argument("article_dir")
    inspect = subparsers.add_parser(
        "inspect", help="write an optional post-composition design report"
    )
    inspect.add_argument("article_dir")
    plan = subparsers.add_parser(
        "plan", help="legacy alias for the non-blocking inspect command"
    )
    plan.add_argument("article_dir")
    migrate = subparsers.add_parser(
        "migrate", help="migrate a legacy workspace to the v4 release manifest"
    )
    migrate.add_argument("article_dir")
    resolve = subparsers.add_parser(
        "resolve-draft", help="resolve an ambiguous draft after user inspection"
    )
    resolve.add_argument("article_dir")
    resolve.add_argument(
        "--outcome", choices=("created", "not-created"), required=True
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "create":
            result = create_workspace(
                Path(args.root),
                args.title,
                args.date,
                local_preview=not args.no_preview,
            )
        elif args.command == "sync":
            result = sync_workspace(Path(args.article_dir))
        elif args.command in {"inspect", "plan"}:
            result = inspect_workspace(Path(args.article_dir))
            if args.command == "plan":
                result["legacy_alias"] = "plan no longer freezes or gates design"
        elif args.command == "migrate":
            result = migrate_workspace(Path(args.article_dir))
        else:
            result = resolve_draft_submission(Path(args.article_dir), args.outcome)
    except (OSError, UnicodeError, json.JSONDecodeError, WorkspaceError, ValueError) as exc:
        print(
            json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
