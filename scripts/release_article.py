#!/usr/bin/env python3
"""Run the mandatory WeChat article release gates through one command."""

from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import uuid
from argparse import Namespace
from pathlib import Path
from typing import Any

try:
    from . import article_workspace, wechat_console_api
    from .design_contract import (
        ContractError,
        fragment_sha256,
        load_contract,
        validate_contract,
    )
except ImportError:
    import article_workspace  # type: ignore[no-redef]
    import wechat_console_api  # type: ignore[no-redef]
    from design_contract import (  # type: ignore[no-redef]
        ContractError,
        fragment_sha256,
        load_contract,
        validate_contract,
    )

AUDITS = (
    "audit_wechat_markup.py",
    "audit_audience_boundary.py",
    "audit_wechat_widths.py",
    "audit_wechat_typography.py",
    "audit_wechat_contrast.py",
    "audit_design_contract.py",
)
REQUIRED_ENV = (
    "WECHAT_CONSOLE_URL",
    "WECHAT_IMAGE_API_KEY",
    "WECHAT_PUBLISH_API_KEY",
)
DEFINITE_DRAFT_FAILURES = {400, 401, 409, 422, 503}


class ReleaseError(RuntimeError):
    pass


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _save_json(path: Path, value: dict[str, Any]) -> None:
    article_workspace._atomic_write_bytes(path, _json_bytes(value))


def _backend_status() -> dict[str, Any]:
    missing = [name for name in REQUIRED_ENV if not os.environ.get(name, "").strip()]
    if missing:
        return {
            "ready": False,
            "reason": "missing console configuration",
            "missing": missing,
        }
    try:
        result, exit_code = wechat_console_api._run(Namespace(command="status"))
    except wechat_console_api.ConsoleApiError as exc:
        return {"ready": False, "reason": str(exc), "http_status": exc.http_status}
    ready = (
        exit_code == 0
        and result.get("console_configured") is True
        and result.get("image_api_key_configured") is True
        and result.get("publish_api_key_configured") is True
        and result.get("server_healthy") is True
    )
    return {"ready": ready, "reason": None if ready else "console health check failed", "status": result}


def _asset_path(article_dir: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ReleaseError("local media is missing source_path")
    assets = (article_dir / "assets").resolve()
    candidate = (assets / value).resolve()
    try:
        candidate.relative_to(assets)
    except ValueError as exc:
        raise ReleaseError("media source_path must stay inside the workspace assets directory") from exc
    if not candidate.is_file():
        raise ReleaseError(f"media source file does not exist: {value}")
    return candidate


def _image_dimensions(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()
    if raw.startswith(b"\x89PNG\r\n\x1a\n") and len(raw) >= 24:
        return struct.unpack(">II", raw[16:24])
    if raw[:6] in {b"GIF87a", b"GIF89a"} and len(raw) >= 10:
        return struct.unpack("<HH", raw[6:10])
    if raw.startswith(b"RIFF") and raw[8:12] == b"WEBP" and len(raw) >= 30:
        kind = raw[12:16]
        if kind == b"VP8X":
            width = 1 + int.from_bytes(raw[24:27], "little")
            height = 1 + int.from_bytes(raw[27:30], "little")
            return width, height
        if kind == b"VP8 " and raw[23:26] == b"\x9d\x01\x2a":
            width, height = struct.unpack("<HH", raw[26:30])
            return width & 0x3FFF, height & 0x3FFF
        if kind == b"VP8L" and len(raw) >= 25 and raw[20] == 0x2F:
            bits = int.from_bytes(raw[21:25], "little")
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if raw.startswith(b"\xff\xd8"):
        index = 2
        while index + 9 <= len(raw):
            if raw[index] != 0xFF:
                index += 1
                continue
            marker = raw[index + 1]
            index += 2
            if marker in {0xD8, 0xD9}:
                continue
            if index + 2 > len(raw):
                break
            length = int.from_bytes(raw[index : index + 2], "big")
            if length < 2 or index + length > len(raw):
                break
            if marker in {
                0xC0,
                0xC1,
                0xC2,
                0xC3,
                0xC5,
                0xC6,
                0xC7,
                0xC9,
                0xCA,
                0xCB,
                0xCD,
                0xCE,
                0xCF,
            }:
                height = int.from_bytes(raw[index + 3 : index + 5], "big")
                width = int.from_bytes(raw[index + 5 : index + 7], "big")
                return width, height
            index += length
    raise ReleaseError(
        f"cannot read image dimensions for {path.name}; use PNG, JPEG, GIF, or WebP"
    )


def _cover_is_235_by_100(path: Path) -> tuple[bool, tuple[int, int]]:
    width, height = _image_dimensions(path)
    if width <= 0 or height <= 0:
        raise ReleaseError(f"cover has invalid dimensions: {width}x{height}")
    return abs((width / height) - 2.35) <= 0.01, (width, height)


def _blocker_fingerprint(blockers: list[str]) -> str:
    return hashlib.sha256(
        json.dumps(blockers, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _replace_body_media(fragment_file: str, media_id: str, source: str) -> str:
    pattern = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
    matched = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal matched
        tag = match.group(0)
        marker = re.search(
            r"\bdata-media-id\s*=\s*(['\"])(.*?)\1",
            tag,
            re.IGNORECASE | re.DOTALL,
        )
        if marker is None or html.unescape(marker.group(2)) != media_id:
            return tag
        matched += 1
        escaped = html.escape(source, quote=True)
        if re.search(r"\bsrc\s*=", tag, re.IGNORECASE):
            return re.sub(
                r"\bsrc\s*=\s*(['\"])(.*?)\1",
                f'src="{escaped}"',
                tag,
                count=1,
                flags=re.IGNORECASE | re.DOTALL,
            )
        return tag[:-1] + f' src="{escaped}">'

    result = pattern.sub(replace, fragment_file)
    if matched != 1:
        raise ReleaseError(
            f"body media {media_id!r} must map to exactly one <img data-media-id>"
        )
    return result


def _upload_local_media(
    article_dir: Path,
    contract: dict[str, Any],
    article: dict[str, Any],
    fragment_file: str,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    candidate_contract = copy.deepcopy(contract)
    candidate_article = dict(article)
    candidate_fragment = fragment_file
    local_assets = [
        item
        for item in sorted(candidate_contract["media"]["assets"], key=lambda item: item["order"])
        if item["state"] in {"generated-local", "supplied-local"}
    ]
    if any(item["state"] == "generated-local" for item in local_assets):
        candidate_contract["delivery"]["image_generation_status"] = "complete"
        candidate_contract["delivery"]["image_generation_reason"] = (
            "Required generated assets exist in the workspace."
        )
    for item in local_assets:
        path = _asset_path(article_dir, item.get("source_path"))
        if item["placement"] == "cover":
            result = wechat_console_api._upload_images([path], "material")
            uploaded = result["items"][0]
            if (
                result.get("error_count")
                or uploaded.get("status") != "complete"
                or not uploaded.get("media_id")
            ):
                raise ReleaseError(f"cover upload failed for {item['name']!r}")
            candidate_article["thumb_media_id"] = uploaded["media_id"]
            item["remote_ref"] = uploaded["media_id"]
        else:
            result = wechat_console_api._upload_images([path], "article")
            uploaded = result["items"][0]
            article_url = uploaded.get("article_url")
            if (
                result.get("error_count")
                or uploaded.get("status") != "complete"
                or not isinstance(article_url, str)
                or not article_url.startswith("https://")
            ):
                raise ReleaseError(f"body image upload failed for {item['name']!r}")
            candidate_fragment = _replace_body_media(
                candidate_fragment, item["name"], article_url
            )
            item["remote_ref"] = article_url
        item["state"] = "hosted"
    return candidate_contract, candidate_article, candidate_fragment


def _use_local_media_placeholders(
    contract: dict[str, Any], fragment_file: str
) -> str:
    result = fragment_file
    for item in contract["media"]["assets"]:
        if item["placement"] == "body" and item["state"] != "hosted":
            marker = re.compile(
                r"<([a-z][a-z0-9]*)\b[^>]*\bdata-media-id\s*=\s*(['\"])"
                + re.escape(item["name"])
                + r"\2[^>]*>",
                re.IGNORECASE,
            )
            match = marker.search(result)
            if match is None:
                raise ReleaseError(
                    f"body media {item['name']!r} has no data-media-id marker"
                )
            if match.group(1).lower() == "img":
                result = _replace_body_media(
                    result, item["name"], f"wechat-media://{item['name']}"
                )
    return result


def _image_blockers(
    article_dir: Path,
    contract: dict[str, Any],
    article: dict[str, Any],
    direct: bool,
) -> list[str]:
    blockers = [
        f"required media {item['name']!r} is still a placeholder"
        for item in contract["media"]["assets"]
        if item.get("required") is True and item.get("state") == "placeholder"
    ]
    for item in contract["media"]["assets"]:
        is_direct_cover = direct and item.get("placement") == "cover"
        state = item.get("state")
        requires_local_source = (
            item.get("required") is True
            and state in {"generated-local", "supplied-local"}
        ) or (is_direct_cover and state in {"generated-local", "supplied-local", "hosted"})
        if not requires_local_source:
            continue
        try:
            path = _asset_path(article_dir, item.get("source_path"))
        except ReleaseError as exc:
            blockers.append(f"required media {item['name']!r} has no valid local source: {exc}")
            continue
        if is_direct_cover:
            try:
                valid_ratio, dimensions = _cover_is_235_by_100(path)
            except (OSError, ReleaseError) as exc:
                blockers.append(f"cover {item['name']!r} cannot be validated: {exc}")
            else:
                if not valid_ratio:
                    blockers.append(
                        f"cover {item['name']!r} is {dimensions[0]}x{dimensions[1]}; "
                        "direct draft requires a 2.35:1 cover"
                    )
    if direct:
        covers = [item for item in contract["media"]["assets"] if item["placement"] == "cover"]
        if not covers:
            blockers.append("direct draft requires a generated or supplied 2.35:1 cover")
        for item in covers:
            if item.get("state") == "placeholder":
                blockers.append(f"cover {item['name']!r} is still a placeholder")
            if item.get("state") == "hosted" and not str(
                article.get("thumb_media_id", "")
            ).strip():
                blockers.append(
                    f"hosted cover {item['name']!r} has no article.json thumb_media_id"
                )
    return blockers


def _finalize_contract(
    contract: dict[str, Any],
    fragment_file: str,
    *,
    backend_ready: bool,
    target: str,
    preview_only: bool,
    generation_failure: str | None,
    fallback_reason: str | None,
) -> dict[str, Any]:
    candidate = copy.deepcopy(contract)
    if candidate.get("status") not in {"PLANNED", "READY"}:
        raise ReleaseError("design contract must pass the PLANNED gate before release")
    fragment = article_workspace._extract_fragment(fragment_file)
    delivery = candidate["delivery"]
    delivery["backend_ready"] = backend_ready
    delivery["target"] = target
    delivery["user_requested_preview_only"] = preview_only
    delivery["fallback_reason"] = fallback_reason or ""
    if generation_failure:
        delivery["image_generation_status"] = "failed"
        delivery["image_generation_reason"] = generation_failure
    elif any(item["state"] == "generated-local" for item in candidate["media"]["assets"]):
        delivery["image_generation_status"] = "complete"
        delivery["image_generation_reason"] = "Required generated assets exist in the workspace."
    elif delivery.get("image_generation_status") in {"pending", "failed"}:
        delivery["image_generation_status"] = "not-required"
        delivery["image_generation_reason"] = "N/A: no required placeholder remains."
    candidate["status"] = "READY"
    candidate["checks"]["fragment_sha256"] = fragment_sha256(fragment)
    validate_contract(candidate, required_status="READY")
    return candidate


def _run_audits(
    fragment_file: str,
    contract: dict[str, Any],
    article: dict[str, Any],
) -> list[dict[str, Any]]:
    scripts = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix="wechat-release-audit-") as temporary:
        root = Path(temporary)
        article_path = root / "fragment.html"
        metadata_path = root / "article.json"
        contract_path = root / "design-contract.json"
        article_path.write_text(fragment_file, encoding="utf-8")
        audit_article = dict(article)
        audit_article["content"] = article_workspace._extract_fragment(fragment_file)
        metadata_path.write_bytes(_json_bytes(audit_article))
        contract_path.write_bytes(_json_bytes(contract))
        results: list[dict[str, Any]] = []
        audit_environment = os.environ.copy()
        audit_environment["PYTHONUTF8"] = "1"
        audit_environment["PYTHONIOENCODING"] = "utf-8"
        for script in AUDITS:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(scripts / script),
                    str(
                        metadata_path
                        if script == "audit_audience_boundary.py"
                        else article_path
                    ),
                    "--contract",
                    str(contract_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=audit_environment,
            )
            raw = completed.stdout.strip() or completed.stderr.strip()
            try:
                result = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ReleaseError(f"{script} returned invalid audit output") from exc
            result["audit"] = script
            results.append(result)
            if completed.returncode != 0 or result.get("ok") is not True:
                raise ReleaseError(
                    f"release audit failed: {script}: {result.get('error') or result.get('findings')}"
                )
        return results


def _persist_and_sync(
    article_dir: Path,
    contract: dict[str, Any],
    article: dict[str, Any],
    fragment_file: str,
    *,
    local_preview: bool,
) -> dict[str, Any]:
    manifest = article_workspace._read_json(article_dir / "manifest.json")
    manifest["local_preview_enabled"] = local_preview
    backups = {
        name: (article_dir / name).read_bytes() if (article_dir / name).is_file() else None
        for name in article_workspace.TRACKED_FILES
    }
    try:
        _save_json(article_dir / "design-contract.json", contract)
        _save_json(article_dir / "article.json", article)
        article_workspace._atomic_write_text(article_dir / "fragment.html", fragment_file)
        _save_json(article_dir / "manifest.json", manifest)
        return article_workspace.sync_workspace(article_dir)
    except Exception:
        article_workspace._restore_files(article_dir, backups)
        raise


def release_workspace(
    article_dir: Path,
    *,
    preview_only: bool = False,
    generation_failure: str | None = None,
    generation_attempt_id: str | None = None,
) -> tuple[dict[str, Any], int]:
    article_dir = article_dir.expanduser().resolve()
    manifest, article, fragment_file = article_workspace._workspace_files(article_dir)
    contract = load_contract(article_dir / "design-contract.json")
    validate_contract(contract)
    if manifest.get("planned_contract_sha256") != article_workspace.planning_hash(contract):
        raise ReleaseError(
            "design decisions are not the recorded PLANNED contract; run the plan gate again"
        )
    submission = manifest.get("draft_submission")
    if isinstance(submission, dict) and submission.get("state") in {
        "submitting",
        "ambiguous",
    }:
        return {
            "ok": False,
            "operation": "release",
            "status": "ambiguous",
            "do_not_retry": True,
            "article_dir": str(article_dir),
            "request_id": submission.get("request_id"),
            "error": (
                "workspace has an unresolved draft submission; inspect the real draft box, "
                "then run article_workspace.py resolve-draft"
            ),
        }, 2
    status = _backend_status()
    direct = bool(status["ready"]) and not preview_only

    blockers = _image_blockers(article_dir, contract, article, direct)
    attempt = manifest.get("image_generation_attempt")
    blocker_sha256 = _blocker_fingerprint(blockers) if blockers else ""
    if generation_failure:
        if not blockers:
            raise ReleaseError(
                "--image-generation-failed is invalid because no current image blocker exists"
            )
        if (
            not generation_attempt_id
            or not isinstance(attempt, dict)
            or attempt.get("state") != "required"
            or attempt.get("attempt_id") != generation_attempt_id
            or attempt.get("blocker_sha256") != blocker_sha256
        ):
            raise ReleaseError(
                "image-generation failure must reference the current attempt_id returned by "
                "an earlier image-generation-required result"
            )
        failed_attempt = dict(attempt)
        failed_attempt.update(
            {
                "state": "failed",
                "reason": generation_failure,
                "updated_at": article_workspace._now().isoformat(),
            }
        )
        article_workspace.update_runtime_manifest(
            article_dir, image_generation_attempt=failed_attempt
        )
    elif generation_attempt_id:
        raise ReleaseError(
            "--image-generation-attempt-id requires --image-generation-failed"
        )
    elif blockers:
        if not (
            isinstance(attempt, dict)
            and attempt.get("state") == "required"
            and attempt.get("blocker_sha256") == blocker_sha256
        ):
            attempt = {
                "state": "required",
                "attempt_id": uuid.uuid4().hex,
                "blocker_sha256": blocker_sha256,
                "blockers": blockers,
                "created_at": article_workspace._now().isoformat(),
                "updated_at": article_workspace._now().isoformat(),
                "reason": "",
            }
            article_workspace.update_runtime_manifest(
                article_dir, image_generation_attempt=attempt
            )
        return {
            "ok": False,
            "operation": "release",
            "status": "image-generation-required",
            "article_dir": str(article_dir),
            "blockers": blockers,
            "attempt_id": attempt["attempt_id"],
            "next_action": (
                "Generate the required assets, set their contract state and source_path, "
                "then rerun. After a real generation failure, rerun with both the returned "
                "--image-generation-attempt-id and --image-generation-failed."
            ),
        }, 3
    elif attempt is not None:
        article_workspace.update_runtime_manifest(
            article_dir, image_generation_attempt=None
        )
    if blockers:
        direct = False

    candidate_contract = copy.deepcopy(contract)
    candidate_article = dict(article)
    candidate_fragment = fragment_file
    fallback_reason = status.get("reason") if not direct and not preview_only else None
    if generation_failure:
        fallback_reason = f"image generation failed: {generation_failure}"

    preflight_audits: list[dict[str, Any]] = []
    if direct:
        preflight_fragment = _use_local_media_placeholders(
            candidate_contract, candidate_fragment
        )
        preflight_contract = _finalize_contract(
            candidate_contract,
            preflight_fragment,
            backend_ready=True,
            target="local-preview",
            preview_only=True,
            generation_failure=None,
            fallback_reason="pre-upload local audit only",
        )
        preflight_audits = _run_audits(
            preflight_fragment, preflight_contract, candidate_article
        )
        try:
            candidate_contract, candidate_article, candidate_fragment = _upload_local_media(
                article_dir, candidate_contract, candidate_article, candidate_fragment
            )
        except (ReleaseError, wechat_console_api.ConsoleApiError) as exc:
            direct = False
            fallback_reason = f"media delivery failed before draft creation: {exc}"

    if not direct:
        candidate_fragment = _use_local_media_placeholders(
            candidate_contract, candidate_fragment
        )

    target = "direct-draft" if direct else "local-preview"
    candidate_contract = _finalize_contract(
        candidate_contract,
        candidate_fragment,
        backend_ready=bool(status["ready"]),
        target=target,
        preview_only=preview_only,
        generation_failure=generation_failure,
        fallback_reason=fallback_reason,
    )
    audits = _run_audits(candidate_fragment, candidate_contract, candidate_article)
    sync = _persist_and_sync(
        article_dir,
        candidate_contract,
        candidate_article,
        candidate_fragment,
        local_preview=not direct,
    )
    if not direct:
        return {
            "ok": True,
            "operation": "release",
            "status": "local-preview",
            "article_dir": str(article_dir),
            "preview_file": sync["preview_file"],
            "fallback_reason": fallback_reason or generation_failure or "preview requested",
            "backend": status,
            "audits": audits,
            "preflight_audits": preflight_audits,
            "sync": sync,
        }, 0

    article_path = article_dir / "article.json"
    def fallback_after_failure(
        reason: str, http_status: int | None
    ) -> tuple[dict[str, Any], int]:
        fallback_contract = _finalize_contract(
            candidate_contract,
            candidate_fragment,
            backend_ready=False,
            target="local-preview",
            preview_only=False,
            generation_failure=None,
            fallback_reason=reason,
        )
        fallback_audits = _run_audits(
            candidate_fragment, fallback_contract, candidate_article
        )
        fallback_sync = _persist_and_sync(
            article_dir,
            fallback_contract,
            candidate_article,
            candidate_fragment,
            local_preview=True,
        )
        return {
            "ok": True,
            "operation": "release",
            "status": "local-preview",
            "preview_file": fallback_sync["preview_file"],
            "fallback_reason": reason,
            "http_status": http_status,
            "audits": fallback_audits,
            "sync": fallback_sync,
        }, 0

    try:
        wechat_console_api._load_draft(str(article_path))
    except wechat_console_api.ConsoleApiError as exc:
        return fallback_after_failure(f"local draft validation failed: {exc}", exc.http_status)
    persisted_manifest = article_workspace._read_json(article_dir / "manifest.json")
    persisted_article = article_workspace._read_json(article_path)
    current_request_id = str(persisted_article.get("request_id") or "")
    prior_submission = persisted_manifest.get("draft_submission")
    if (
        isinstance(prior_submission, dict)
        and prior_submission.get("state") == "created"
        and prior_submission.get("request_id") == current_request_id
    ):
        return {
            "ok": True,
            "operation": "release",
            "status": "draft-created",
            "article_dir": str(article_dir),
            "draft": prior_submission.get("result")
            or {"request_id": current_request_id, "cached": True},
            "audits": audits,
            "preflight_audits": preflight_audits,
            "sync": sync,
        }, 0
    submitting = {
        "state": "submitting",
        "request_id": current_request_id,
        "payload_sha256": persisted_manifest.get("draft_payload_sha256") or "",
        "updated_at": article_workspace._now().isoformat(),
        "reason": "Draft request is in flight.",
        "result": None,
    }
    article_workspace.update_runtime_manifest(
        article_dir, draft_submission=submitting
    )
    try:
        draft, exit_code = wechat_console_api._create_draft_article(str(article_path))
    except wechat_console_api.ConsoleApiError as exc:
        if exc.ambiguous or exc.http_status not in DEFINITE_DRAFT_FAILURES:
            ambiguous_submission = dict(submitting)
            ambiguous_submission.update(
                {
                    "state": "ambiguous",
                    "updated_at": article_workspace._now().isoformat(),
                    "reason": str(exc),
                }
            )
            article_workspace.update_runtime_manifest(
                article_dir, draft_submission=ambiguous_submission
            )
            return {
                "ok": False,
                "operation": "release",
                "status": "ambiguous",
                "do_not_retry": True,
                "error": str(exc),
                "http_status": exc.http_status,
                "article_dir": str(article_dir),
            }, 2
        definite_submission = dict(submitting)
        definite_submission.update(
            {
                "state": "not-created",
                "updated_at": article_workspace._now().isoformat(),
                "reason": str(exc),
            }
        )
        article_workspace.update_runtime_manifest(
            article_dir, draft_submission=definite_submission
        )
        return fallback_after_failure(
            f"definite pre-draft failure: {exc}", exc.http_status
        )
    if exit_code != 0 or draft.get("ambiguous"):
        ambiguous_submission = dict(submitting)
        ambiguous_submission.update(
            {
                "state": "ambiguous",
                "updated_at": article_workspace._now().isoformat(),
                "reason": "Draft API returned an ambiguous operation state.",
                "result": draft,
            }
        )
        article_workspace.update_runtime_manifest(
            article_dir, draft_submission=ambiguous_submission
        )
        draft.update(
            {
                "ok": False,
                "status": "ambiguous",
                "do_not_retry": True,
                "article_dir": str(article_dir),
            }
        )
        return draft, 2
    created_submission = dict(submitting)
    created_submission.update(
        {
            "state": "created",
            "updated_at": article_workspace._now().isoformat(),
            "reason": "Draft creation was confirmed.",
            "result": draft,
        }
    )
    article_workspace.update_runtime_manifest(
        article_dir, draft_submission=created_submission
    )
    return {
        "ok": True,
        "operation": "release",
        "status": "draft-created",
        "article_dir": str(article_dir),
        "draft": draft,
        "audits": audits,
        "preflight_audits": preflight_audits,
        "sync": sync,
    }, 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Enforce every design, validation, routing, and draft-delivery gate"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    deliver = subparsers.add_parser("deliver")
    deliver.add_argument("article_dir", type=Path)
    deliver.add_argument("--preview-only", action="store_true")
    deliver.add_argument(
        "--image-generation-failed",
        metavar="REASON",
        help="record a real image-generation failure and permit local-preview fallback",
    )
    deliver.add_argument(
        "--image-generation-attempt-id",
        help="bind a real generation failure to the current workspace blocker set",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        result, exit_code = release_workspace(
            args.article_dir,
            preview_only=args.preview_only,
            generation_failure=args.image_generation_failed,
            generation_attempt_id=args.image_generation_attempt_id,
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ContractError,
        ReleaseError,
        article_workspace.WorkspaceError,
    ) as exc:
        result = {"ok": False, "operation": "release", "status": "blocked", "error": str(exc)}
        exit_code = 2
    stream = sys.stdout if result.get("ok") else sys.stderr
    print(json.dumps(result, ensure_ascii=False, indent=2), file=stream)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
