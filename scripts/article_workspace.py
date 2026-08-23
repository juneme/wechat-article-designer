#!/usr/bin/env python3
"""Create and transactionally version WeChat article workspaces."""

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

try:
    from .design_contract import (
        ContractError,
        empty_contract,
        fragment_sha256,
        load_contract,
        migrate_contract,
        render_contract_markdown,
        validate_contract,
    )
except ImportError:
    from design_contract import (  # type: ignore[no-redef]
        ContractError,
        empty_contract,
        fragment_sha256,
        load_contract,
        migrate_contract,
        render_contract_markdown,
        validate_contract,
    )

START = "<!-- 微信公众号复制开始 -->"
END = "<!-- 微信公众号复制结束 -->"
TRACKED_FILES = (
    "article.json",
    "design-contract.json",
    "design-contract.md",
    "fragment.html",
    "preview.html",
    "manifest.json",
)
STATE_FILES = TRACKED_FILES[:-1]
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
        if temporary.exists():
            temporary.unlink()


def _atomic_write_text(path: Path, value: str) -> None:
    _atomic_write_bytes(path, value.encode("utf-8"))


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise WorkspaceError(f"cannot read JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WorkspaceError(f"JSON root must be an object: {path}")
    return value


def update_runtime_manifest(article_dir: Path, **values: Any) -> dict[str, Any]:
    """Atomically persist release runtime state that does not create a revision."""
    article_dir = article_dir.expanduser().resolve()
    manifest_path = article_dir / "manifest.json"
    manifest = _read_json(manifest_path)
    if manifest.get("schema_version") != 4:
        raise WorkspaceError("runtime state requires a schema-4 workspace")
    manifest.update(values)
    manifest["updated_at"] = _now().isoformat()
    _atomic_write_bytes(manifest_path, _json_bytes(manifest))
    return manifest


def _extract_fragment(raw: str) -> str:
    if raw.count(START) != 1 or raw.count(END) != 1:
        raise WorkspaceError("fragment.html must contain exactly one WeChat boundary pair")
    prefix, remainder = raw.split(START, 1)
    fragment, suffix = remainder.split(END, 1)
    if prefix.strip() or suffix.strip():
        raise WorkspaceError(
            "fragment.html may contain only the boundary pair and publishable fragment"
        )
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
    body {{ box-sizing:border-box;width:320px;min-height:100vh;margin:0 auto;padding:0;background:#fff;color:#202020; }}
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


def planning_hash(contract: dict[str, Any]) -> str:
    """Hash design decisions while excluding implementation and route runtime state."""
    normalized = json.loads(json.dumps(contract, ensure_ascii=False))
    normalized["status"] = "PLANNED"
    normalized["checks"]["fragment_sha256"] = ""
    delivery = normalized["delivery"]
    for key in (
        "backend_ready",
        "target",
        "user_requested_preview_only",
        "image_generation_status",
        "image_generation_reason",
        "fallback_reason",
    ):
        delivery.pop(key, None)
    for item in normalized["media"]["assets"]:
        for key in ("state", "source_path", "remote_ref"):
            item.pop(key, None)
    encoded = json.dumps(
        normalized,
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


def _asset_inventory(assets: Path) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    if not assets.is_dir():
        return inventory
    for path in sorted(item for item in assets.rglob("*") if item.is_file()):
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        inventory.append(
            {
                "path": path.relative_to(assets).as_posix(),
                "size": path.stat().st_size,
                "sha256": digest.hexdigest(),
            }
        )
    return inventory


def _state_hash(outputs: dict[str, bytes | None], assets: Path) -> str:
    digest = hashlib.sha256()
    for name in STATE_FILES:
        digest.update(name.encode("utf-8"))
        value = outputs.get(name)
        if value is None:
            digest.update(b"\0ABSENT")
        else:
            digest.update(b"\0PRESENT\0")
            digest.update(value)
    digest.update(
        json.dumps(
            _asset_inventory(assets),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    return digest.hexdigest()


def _physical_mismatch(article_dir: Path, outputs: dict[str, bytes | None]) -> bool:
    for name in STATE_FILES:
        path = article_dir / name
        expected = outputs.get(name)
        if expected is None:
            if path.exists():
                return True
        elif not path.is_file() or path.read_bytes() != expected:
            return True
    return False


def _build_outputs(
    *,
    article: dict[str, Any],
    contract: dict[str, Any],
    fragment_file: str,
    preview_enabled: bool,
    manifest: dict[str, Any],
) -> dict[str, bytes | None]:
    fragment = _extract_fragment(fragment_file)
    preview = _preview_html(str(article["title"]), fragment) if preview_enabled else None
    return {
        "article.json": _json_bytes(article),
        "design-contract.json": _json_bytes(contract),
        "design-contract.md": render_contract_markdown(contract).encode("utf-8"),
        "fragment.html": fragment_file.encode("utf-8"),
        "preview.html": preview.encode("utf-8") if preview is not None else None,
        "manifest.json": _json_bytes(manifest),
    }


def _restore_files(article_dir: Path, backups: dict[str, bytes | None]) -> None:
    for name, value in backups.items():
        path = article_dir / name
        if value is None:
            if path.exists():
                path.unlink()
        else:
            _atomic_write_bytes(path, value)


def _commit_revision(
    article_dir: Path,
    outputs: dict[str, bytes | None],
    revision: int,
    timestamp: datetime,
) -> Path:
    revisions = article_dir / "revisions"
    final = revisions / f"r{revision:03d}_{timestamp.strftime('%Y%m%d-%H%M%S')}"
    stage = revisions / f".{final.name}.{uuid.uuid4().hex}.tmp"
    if final.exists():
        raise WorkspaceError(f"revision directory already exists: {final}")

    backups = {
        name: (article_dir / name).read_bytes() if (article_dir / name).is_file() else None
        for name in TRACKED_FILES
    }
    try:
        stage.mkdir(parents=True)
        for name, value in outputs.items():
            if value is not None:
                destination = stage / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(value)
        assets = article_dir / "assets"
        if assets.is_dir():
            shutil.copytree(assets, stage / "assets")

        for name, value in outputs.items():
            path = article_dir / name
            if value is None:
                if path.exists():
                    path.unlink()
            else:
                _atomic_write_bytes(path, value)
        stage.replace(final)
    except Exception as exc:
        try:
            _restore_files(article_dir, backups)
        finally:
            if stage.exists():
                shutil.rmtree(stage)
        raise WorkspaceError(f"workspace transaction failed and was rolled back: {exc}") from exc
    return final


def _workspace_files(article_dir: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    if not article_dir.is_dir():
        raise WorkspaceError(f"article workspace does not exist: {article_dir}")
    manifest = _read_json(article_dir / "manifest.json")
    if manifest.get("schema_version") != 4:
        raise WorkspaceError(
            "workspace schema is not supported; run "
            "python scripts/article_workspace.py migrate <article-workspace>"
        )
    article = _read_json(article_dir / "article.json")
    try:
        fragment_file = (article_dir / "fragment.html").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise WorkspaceError(f"cannot read fragment.html: {exc}") from exc
    return manifest, article, fragment_file


def _check_title(article: dict[str, Any], contract: dict[str, Any]) -> str:
    title = article.get("title")
    if not isinstance(title, str) or not title.strip():
        raise WorkspaceError("article.json title must be a non-empty string")
    if contract.get("article_title") != title:
        raise WorkspaceError("design-contract.json article_title must match article.json title")
    return title


def create_workspace(
    root: Path,
    title: str,
    article_date: date,
    *,
    scope: str = "new-article",
    local_preview: bool = True,
) -> dict[str, Any]:
    root = root.expanduser().resolve()
    article_dir = _next_available(root, f"{article_date.isoformat()}_{_slug(title)}")
    article_dir.mkdir(parents=True)
    (article_dir / "assets").mkdir()
    (article_dir / "revisions").mkdir()

    article_id = uuid.uuid4().hex
    timestamp = _now()
    fragment = '<section style="margin:0;padding:0;background:#FFFFFF;color:#202020;"></section>'
    fragment_file = f"{START}\n{fragment}\n{END}\n"
    initial_fragment_sha256 = fragment_sha256(fragment)
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
    contract = empty_contract(title, scope=scope, local_preview=local_preview)
    manifest = {
        "schema_version": 4,
        "article_id": article_id,
        "title": title,
        "slug": _slug(title),
        "article_date": article_date.isoformat(),
        "created_at": timestamp.isoformat(),
        "updated_at": timestamp.isoformat(),
        "revision": 0,
        "draft_payload_sha256": None,
        "workspace_state_sha256": None,
        "planned_contract_sha256": None,
        "implementation_base_sha256": initial_fragment_sha256,
        "active_plan_iterations": 0,
        "draft_submission": {
            "state": "idle",
            "request_id": "",
            "payload_sha256": "",
            "updated_at": "",
            "reason": "",
            "result": None,
        },
        "image_generation_attempt": None,
        "local_preview_enabled": local_preview,
    }
    outputs = _build_outputs(
        article=article,
        contract=contract,
        fragment_file=fragment_file,
        preview_enabled=local_preview,
        manifest=manifest,
    )
    manifest["workspace_state_sha256"] = _state_hash(
        outputs, article_dir / "assets"
    )
    outputs["manifest.json"] = _json_bytes(manifest)
    for name, value in outputs.items():
        if value is not None:
            _atomic_write_bytes(article_dir / name, value)

    return {
        "ok": True,
        "operation": "create",
        "article_dir": str(article_dir),
        "article_id": article_id,
        "design_contract_json": str(article_dir / "design-contract.json"),
        "design_contract_markdown": str(article_dir / "design-contract.md"),
        "preview_file": str(article_dir / "preview.html") if local_preview else None,
    }


def record_plan(article_dir: Path) -> dict[str, Any]:
    article_dir = article_dir.expanduser().resolve()
    manifest, article, fragment_file = _workspace_files(article_dir)
    contract = load_contract(article_dir / "design-contract.json")
    validate_contract(contract, required_status="PLANNED")
    _check_title(article, contract)

    implementation_digest = fragment_sha256(_extract_fragment(fragment_file))
    plan_iterations = manifest.get("active_plan_iterations")
    if type(plan_iterations) is not int or plan_iterations < 0:
        raise WorkspaceError("manifest active_plan_iterations must be a non-negative integer")
    if (
        plan_iterations == 0
        and manifest.get("implementation_base_sha256") != implementation_digest
    ):
        raise WorkspaceError(
            "fragment.html changed before the PLANNED gate; restore the last READY fragment, "
            "run plan, and only then implement the redesign"
        )

    preview_enabled = bool(manifest.get("local_preview_enabled", True))
    expected_target = "local-preview" if preview_enabled else "direct-draft"
    if contract["delivery"]["target"] != expected_target:
        raise WorkspaceError(
            "design contract delivery target does not match workspace preview route"
        )

    timestamp = _now()
    revision = int(manifest.get("revision", 0)) + 1
    candidate_manifest = dict(manifest)
    candidate_manifest.update(
        {
            "title": article["title"],
            "slug": _slug(str(article["title"])),
            "updated_at": timestamp.isoformat(),
            "revision": revision,
            "planned_contract_sha256": planning_hash(contract),
            "active_plan_iterations": plan_iterations + 1,
        }
    )
    outputs = _build_outputs(
        article=article,
        contract=contract,
        fragment_file=fragment_file,
        preview_enabled=preview_enabled,
        manifest=candidate_manifest,
    )
    state_hash = _state_hash(outputs, article_dir / "assets")
    changed = state_hash != manifest.get("workspace_state_sha256") or _physical_mismatch(
        article_dir, outputs
    )
    if not changed:
        return {
            "ok": True,
            "operation": "plan",
            "article_dir": str(article_dir),
            "changed": False,
            "revision": manifest.get("revision", 0),
            "revision_dir": None,
        }

    candidate_manifest["workspace_state_sha256"] = state_hash
    outputs["manifest.json"] = _json_bytes(candidate_manifest)
    revision_dir = _commit_revision(article_dir, outputs, revision, timestamp)
    return {
        "ok": True,
        "operation": "plan",
        "article_dir": str(article_dir),
        "changed": True,
        "revision": revision,
        "revision_dir": str(revision_dir),
    }


def sync_workspace(
    article_dir: Path,
    *,
    local_preview: bool | None = None,
) -> dict[str, Any]:
    article_dir = article_dir.expanduser().resolve()
    manifest, article, fragment_file = _workspace_files(article_dir)
    contract = load_contract(article_dir / "design-contract.json")

    if local_preview is not None:
        contract["delivery"]["target"] = (
            "local-preview" if local_preview else "direct-draft"
        )
        contract["delivery"]["backend_ready"] = not local_preview
        manifest["local_preview_enabled"] = local_preview
    preview_enabled = bool(manifest.get("local_preview_enabled", True))
    validate_contract(contract, required_status="READY")
    if manifest.get("planned_contract_sha256") != planning_hash(contract):
        raise WorkspaceError(
            "design decisions changed after the PLANNED gate; set PLANNED and run plan again"
        )
    title = _check_title(article, contract)
    expected_target = "local-preview" if preview_enabled else "direct-draft"
    if contract["delivery"]["target"] != expected_target:
        raise WorkspaceError(
            "design contract delivery target does not match workspace preview route"
        )

    fragment = _extract_fragment(fragment_file)
    if contract["checks"]["fragment_sha256"] != fragment_sha256(fragment):
        raise WorkspaceError(
            "READY design contract is stale; finalize the exact fragment before synchronization"
        )
    candidate_article = dict(article)
    candidate_article["content"] = fragment
    draft_hash = _payload_hash(candidate_article)
    draft_changed = draft_hash != manifest.get("draft_payload_sha256")
    timestamp = _now()
    revision = int(manifest.get("revision", 0)) + 1
    if draft_changed:
        article_id = manifest.get("article_id")
        if not isinstance(article_id, str) or not article_id:
            raise WorkspaceError("manifest.json is missing article_id")
        candidate_article["request_id"] = _request_id(article_id, revision, timestamp)

    candidate_manifest = dict(manifest)
    candidate_manifest.update(
        {
            "title": title,
            "slug": _slug(title),
            "updated_at": timestamp.isoformat(),
            "revision": revision,
            "draft_payload_sha256": draft_hash,
            "local_preview_enabled": preview_enabled,
            "implementation_base_sha256": fragment_sha256(fragment),
            "active_plan_iterations": 0,
        }
    )
    outputs = _build_outputs(
        article=candidate_article,
        contract=contract,
        fragment_file=fragment_file,
        preview_enabled=preview_enabled,
        manifest=candidate_manifest,
    )
    state_hash = _state_hash(outputs, article_dir / "assets")
    changed = state_hash != manifest.get("workspace_state_sha256") or _physical_mismatch(
        article_dir, outputs
    )
    if not changed:
        return {
            "ok": True,
            "operation": "sync",
            "article_dir": str(article_dir),
            "changed": False,
            "revision": manifest.get("revision", 0),
            "request_id": article.get("request_id"),
            "revision_dir": None,
            "preview_file": (
                str(article_dir / "preview.html") if preview_enabled else None
            ),
        }

    candidate_manifest["workspace_state_sha256"] = state_hash
    outputs["manifest.json"] = _json_bytes(candidate_manifest)
    revision_dir = _commit_revision(article_dir, outputs, revision, timestamp)
    return {
        "ok": True,
        "operation": "sync",
        "article_dir": str(article_dir),
        "changed": True,
        "draft_changed": draft_changed,
        "revision": revision,
        "request_id": candidate_article.get("request_id"),
        "revision_dir": str(revision_dir),
        "preview_file": str(article_dir / "preview.html") if preview_enabled else None,
    }


def migrate_workspace(article_dir: Path) -> dict[str, Any]:
    article_dir = article_dir.expanduser().resolve()
    if not article_dir.is_dir():
        raise WorkspaceError(f"article workspace does not exist: {article_dir}")
    manifest = _read_json(article_dir / "manifest.json")
    source_schema = manifest.get("schema_version")
    if source_schema == 4:
        return {
            "ok": True,
            "operation": "migrate",
            "article_dir": str(article_dir),
            "changed": False,
            "schema_version": 4,
        }
    if source_schema not in {2, 3}:
        raise WorkspaceError(f"cannot migrate workspace schema {source_schema!r}")

    article = _read_json(article_dir / "article.json")
    fragment_file = (article_dir / "fragment.html").read_text(encoding="utf-8")
    fragment = _extract_fragment(fragment_file)
    preview_enabled = bool(manifest.get("local_preview_enabled", True))
    contract_path = article_dir / "design-contract.json"
    if contract_path.is_file():
        contract = migrate_contract(load_contract(contract_path))
    else:
        title = str(article.get("title") or manifest.get("title") or "未命名文章")
        contract = empty_contract(
            title,
            scope="substantial-redesign",
            local_preview=preview_enabled,
        )

    timestamp = _now()
    revision = int(manifest.get("revision", 0)) + 1
    status = contract.get("status")
    planned_hash = (
        planning_hash(contract) if status in {"PLANNED", "READY"} else None
    )
    migrated_manifest = dict(manifest)
    migrated_manifest.update(
        {
            "schema_version": 4,
            "updated_at": timestamp.isoformat(),
            "revision": revision,
            "planned_contract_sha256": planned_hash,
            "implementation_base_sha256": fragment_sha256(fragment),
            "active_plan_iterations": 1 if status == "PLANNED" else 0,
            "draft_submission": {
                "state": "idle",
                "request_id": "",
                "payload_sha256": "",
                "updated_at": "",
                "reason": "",
                "result": None,
            },
            "image_generation_attempt": None,
            "local_preview_enabled": preview_enabled,
        }
    )
    (article_dir / "assets").mkdir(exist_ok=True)
    (article_dir / "revisions").mkdir(exist_ok=True)
    outputs = _build_outputs(
        article=article,
        contract=contract,
        fragment_file=fragment_file,
        preview_enabled=preview_enabled,
        manifest=migrated_manifest,
    )
    migrated_manifest["workspace_state_sha256"] = _state_hash(
        outputs, article_dir / "assets"
    )
    outputs["manifest.json"] = _json_bytes(migrated_manifest)
    revision_dir = _commit_revision(article_dir, outputs, revision, timestamp)
    return {
        "ok": True,
        "operation": "migrate",
        "article_dir": str(article_dir),
        "changed": True,
        "from_schema": source_schema,
        "schema_version": 4,
        "contract_schema_version": contract["schema_version"],
        "revision": revision,
        "revision_dir": str(revision_dir),
    }


def resolve_draft_submission(article_dir: Path, outcome: str) -> dict[str, Any]:
    article_dir = article_dir.expanduser().resolve()
    manifest, _, _ = _workspace_files(article_dir)
    submission = manifest.get("draft_submission")
    if not isinstance(submission, dict) or submission.get("state") not in {
        "submitting",
        "ambiguous",
    }:
        raise WorkspaceError("workspace has no unresolved draft submission")
    if outcome not in {"created", "not-created"}:
        raise WorkspaceError("draft outcome must be created or not-created")
    resolved = dict(submission)
    resolved.update(
        {
            "state": outcome,
            "updated_at": _now().isoformat(),
            "reason": "Resolved after the user inspected the real draft box.",
            "result": (
                {
                    "status": "created",
                    "request_id": submission.get("request_id"),
                    "manual_confirmation": True,
                }
                if outcome == "created"
                else None
            ),
        }
    )
    update_runtime_manifest(article_dir, draft_submission=resolved)
    return {
        "ok": True,
        "operation": "resolve-draft",
        "article_dir": str(article_dir),
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
        description="Create and transactionally version WeChat article workspaces"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create", help="create a new article workspace")
    create.add_argument("--title", required=True)
    create.add_argument("--date", type=_date, default=date.today())
    create.add_argument("--root", default="articles")
    create.add_argument(
        "--scope",
        choices=("new-article", "substantial-redesign"),
        default="new-article",
    )
    create.add_argument(
        "--no-preview",
        action="store_true",
        help="do not create a local preview for a direct-draft workspace",
    )
    plan = subparsers.add_parser(
        "plan", help="validate and version a PLANNED design contract"
    )
    plan.add_argument("article_dir")
    sync = subparsers.add_parser(
        "sync", help="validate READY state and transactionally synchronize it"
    )
    sync.add_argument("article_dir")
    preview_group = sync.add_mutually_exclusive_group()
    preview_group.add_argument(
        "--preview",
        action="store_true",
        help="switch to the local-preview fallback",
    )
    preview_group.add_argument(
        "--no-preview",
        action="store_true",
        help="switch to direct draft and physically remove any local preview",
    )
    migrate = subparsers.add_parser(
        "migrate", help="transactionally upgrade a schema-2 or schema-3 workspace"
    )
    migrate.add_argument("article_dir")
    resolve = subparsers.add_parser(
        "resolve-draft", help="record the user's inspection of an ambiguous draft"
    )
    resolve.add_argument("article_dir")
    resolve.add_argument("--outcome", choices=("created", "not-created"), required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "create":
            result = create_workspace(
                Path(args.root),
                args.title,
                args.date,
                scope=args.scope,
                local_preview=not args.no_preview,
            )
        elif args.command == "plan":
            result = record_plan(Path(args.article_dir))
        elif args.command == "sync":
            preview_override = True if args.preview else False if args.no_preview else None
            result = sync_workspace(
                Path(args.article_dir),
                local_preview=preview_override,
            )
        elif args.command == "migrate":
            result = migrate_workspace(Path(args.article_dir))
        else:
            result = resolve_draft_submission(Path(args.article_dir), args.outcome)
    except (OSError, ContractError, WorkspaceError, ValueError) as exc:
        print(
            json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
