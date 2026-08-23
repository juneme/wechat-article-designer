#!/usr/bin/env python3
"""Create and transactionally version WeChat article workspaces."""

from __future__ import annotations

import argparse
import copy
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
    from .audit_design_contract import (
        SPACING_RULES,
        ContractParser,
        _side,
    )
    from .audit_wechat_contrast import ContrastParser, color_label, parse_color
    from .audit_wechat_markup import MarkupParser
    from .audit_wechat_typography import (
        CONTAINER_TAGS,
        TypographyParser,
        _font_stack,
        _font_weight,
        _indent_em,
        _line_height,
        _number_unit,
        _zero_px,
    )
    from .audit_wechat_typography import (
        audit_html as audit_typography_html,
    )
    from .design_contract import (
        ContractError,
        contract_warnings,
        empty_contract,
        fragment_sha256,
        load_contract,
        migrate_contract,
        render_contract_markdown,
        validate_contract,
    )
except ImportError:
    from audit_design_contract import (  # type: ignore[no-redef]
        SPACING_RULES,
        ContractParser,
        _side,
    )
    from audit_wechat_contrast import (  # type: ignore[no-redef]
        ContrastParser,
        color_label,
        parse_color,
    )
    from audit_wechat_markup import MarkupParser  # type: ignore[no-redef]
    from audit_wechat_typography import (  # type: ignore[no-redef]
        CONTAINER_TAGS,
        TypographyParser,
        _font_stack,
        _font_weight,
        _indent_em,
        _line_height,
        _number_unit,
        _zero_px,
    )
    from audit_wechat_typography import (
        audit_html as audit_typography_html,
    )
    from design_contract import (  # type: ignore[no-redef]
        ContractError,
        contract_warnings,
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


def _uniform_number(values: list[float | None], label: str) -> float:
    if not values or any(value is None for value in values):
        raise WorkspaceError(f"cannot extract {label} from the selected fragment")
    concrete = [float(value) for value in values if value is not None]
    if any(abs(value - concrete[0]) > 0.01 for value in concrete[1:]):
        raise WorkspaceError(f"selected fragment uses conflicting values for {label}")
    return concrete[0]


def _extract_typography(
    fragment: str,
) -> tuple[dict[str, dict[str, Any]], float | None]:
    parser = TypographyParser()
    parser.feed(fragment)
    parser.close()
    observed: dict[str, list[tuple[dict[str, Any], float, bool]]] = {}

    for node in parser.nodes:
        if (
            node.tag in CONTAINER_TAGS
            and "text-indent" in node.declared_style
        ):
            size = _number_unit(node.style.get("font-size"), "px")
            indent = _indent_em(node.declared_style.get("text-indent"), size)
            if indent is None or abs(indent) > 0.01:
                raise WorkspaceError(
                    f"layout container at line {node.line} must not carry first-line indentation"
                )

    for node in parser.nodes:
        if node.explicit_role is None or not "".join(node.text).strip():
            continue
        style = node.style
        size = _number_unit(style.get("font-size"), "px")
        leading = _line_height(style.get("line-height"), size)
        weight = _font_weight(style.get("font-weight"))
        stack = _font_stack(style.get("font-family"))
        alignment = (style.get("text-align") or "").lower()
        if _zero_px(style.get("letter-spacing")):
            tracking = 0.0
        else:
            tracking = _number_unit(style.get("letter-spacing"), "px")
        wrap = next(
            (
                f"{name}:{style[name]}"
                for name in ("overflow-wrap", "word-break", "white-space")
                if style.get(name)
            ),
            None,
        )
        indent = _indent_em(style.get("text-indent"), size)
        missing = [
            name
            for name, value in (
                ("font-family", stack),
                ("font-size", size),
                ("line-height", leading),
                ("font-weight", weight),
                ("text-align", alignment),
                ("letter-spacing", tracking),
                ("text-indent", indent),
                ("wrapping", wrap),
            )
            if value is None or value == ""
        ]
        if missing:
            raise WorkspaceError(
                f"cannot extract typography role {node.explicit_role!r} at line "
                f"{node.line}; missing explicit or inherited {', '.join(missing)}"
            )
        is_body_paragraph = node.indent_role == "body-paragraph"
        if node.indent_role is not None and not is_body_paragraph:
            raise WorkspaceError(
                "data-indent-role supports only 'body-paragraph'"
            )
        if is_body_paragraph and (
            node.tag != "p" or node.explicit_role != "body"
        ):
            raise WorkspaceError(
                "data-indent-role='body-paragraph' requires a p with "
                "data-type-role='body'"
            )
        if not is_body_paragraph and abs(float(indent)) > 0.01:
            raise WorkspaceError(
                f"only marked body paragraphs may use text-indent; "
                f"role {node.explicit_role!r} at line {node.line} must use text-indent:0"
            )
        values = {
            "font_stack": stack,
            "font_size_px": float(size),
            "line_height": float(leading),
            "font_weight": int(weight),
            "alignment": alignment,
            "letter_spacing_px": float(tracking),
            "wrap": wrap,
        }
        observed.setdefault(node.explicit_role, []).append(
            (values, float(indent), is_body_paragraph)
        )

    if not observed:
        raise WorkspaceError(
            "selected fragment must contain visible text with data-type-role markers"
        )

    roles: dict[str, dict[str, Any]] = {}
    body_indents: list[float] = []
    for role, records in observed.items():
        first_values = records[0][0]
        if any(values != first_values for values, _, _ in records[1:]):
            raise WorkspaceError(
                f"typography role {role!r} uses conflicting implementation values"
            )
        roles[role] = first_values
        if role == "body":
            body_indents.extend(
                indent for _, indent, is_body_paragraph in records if is_body_paragraph
            )
    body_indent = (
        _uniform_number(body_indents, "body paragraph first-line indentation")
        if body_indents
        else None
    )
    return roles, body_indent


def _extract_palette(fragment: str, contract: dict[str, Any]) -> None:
    parser = ContrastParser()
    parser.feed(fragment)
    parser.close()
    colors: list[tuple[str, str]] = []
    for declared in parser.declared_colors:
        parsed = parse_color(str(declared["value"]))
        if parsed is None or parsed[3] == 0:
            continue
        label = color_label(parsed)
        property_name = str(declared["property"])
        if label not in {value for value, _ in colors}:
            colors.append((label, property_name))
    if not colors:
        return

    palette = contract["color"]
    backgrounds = [
        value
        for value, property_name in colors
        if property_name in {"background", "background-color"}
    ]
    foregrounds = [
        value
        for value, property_name in colors
        if property_name in {"color", "fill"}
    ]
    field = backgrounds[0] if backgrounds else str(palette["field"]["value"])
    ink = foregrounds[0] if foregrounds else str(palette["ink"]["value"])
    palette["field"] = {
        "value": field,
        "reason": "Machine-extracted reading field from the selected HTML.",
    }
    palette["ink"] = {
        "value": ink,
        "reason": "Machine-extracted primary text color from the selected HTML.",
    }

    remaining = [value for value, _ in colors if value not in {field, ink}]
    for key in ("primary_signal", "secondary_signal", "correction"):
        previous = palette.get(key, {})
        previous_value = previous.get("value") if isinstance(previous, dict) else None
        if previous_value in remaining:
            value = previous_value
            remaining.remove(value)
            reason = previous.get("reason") or "Retained semantic role from the selected design."
        elif remaining:
            value = remaining.pop(0)
            reason = "Machine-extracted supporting color from the selected HTML."
        else:
            value = None
            reason = ""
        palette[key] = {"value": value, "reason": reason}
    palette["image_support"] = [
        {
            "value": value,
            "reason": "Machine-extracted additional color from the selected HTML.",
        }
        for value in remaining
    ]
    palette["usage_ratio"] = (
        "Palette membership is machine-extracted; visual proportions follow the selected HTML."
    )
    if not str(palette["contrast"].get("rationale", "")).strip():
        palette["contrast"]["rationale"] = (
            "Readability thresholds are checked against the selected HTML."
        )


def _extract_media(fragment_parser: ContractParser, contract: dict[str, Any]) -> None:
    assets = contract["media"]["assets"]
    body_assets = {
        item["name"]: item for item in assets if item.get("placement") == "body"
    }
    implemented_names = [name for name, _, _, _, _ in fragment_parser.media]
    unknown = [name for name in implemented_names if name not in body_assets]
    missing = [name for name in body_assets if name not in implemented_names]
    if unknown:
        raise WorkspaceError(
            "selected fragment contains body media without contract authority metadata: "
            + ", ".join(repr(name) for name in unknown)
        )
    if missing:
        raise WorkspaceError(
            "contract body media is absent from the selected fragment: "
            + ", ".join(repr(name) for name in missing)
        )

    captions: dict[str, list[str]] = {}
    for record in fragment_parser.captions:
        captions.setdefault(str(record["name"]), []).append(
            re.sub(r"\s+", " ", "".join(record["parts"])).strip()
        )
    if any(len(values) > 1 for values in captions.values()):
        raise WorkspaceError("each body media item may have at most one selected caption")

    for order, (name, _, _, crop, _) in enumerate(fragment_parser.media, start=1):
        asset = body_assets[name]
        asset["order"] = order
        if crop:
            asset["crop"] = crop
        values = captions.get(name, [])
        asset["caption"] = (
            values[0]
            if values
            else "N/A: the selected HTML contains no caption for this body asset."
        )
    next_order = len(implemented_names) + 1
    for asset in sorted(
        (item for item in assets if item.get("placement") == "cover"),
        key=lambda item: item.get("order", 999),
    ):
        asset["order"] = next_order
        next_order += 1


def _extract_selected_implementation(
    contract: dict[str, Any], fragment_file: str
) -> dict[str, Any]:
    candidate = copy.deepcopy(contract)
    fragment = _extract_fragment(fragment_file)
    parser = ContractParser()
    parser.feed(fragment)
    parser.close()
    if not parser.modules:
        raise WorkspaceError(
            "selected fragment must mark each article module with data-module-id and data-density"
        )

    candidate["editorial"]["module_sequence"] = [
        name for name, _, _ in parser.modules
    ]
    candidate["layout"]["density_curve"] = [
        density for _, density, _ in parser.modules
    ]
    dominant = [name for name, density, _ in parser.modules if density == "dominant"]
    if dominant:
        candidate["editorial"]["dominant_module"] = dominant[0]

    layout = candidate["layout"]
    for role, key in (
        ("outer-baseline", "outer_baseline_px"),
        ("content-inset", "content_inset_px"),
    ):
        markers = parser.layout.get(role, [])
        if len(markers) != 1:
            raise WorkspaceError(
                f"selected fragment must contain exactly one data-layout-role={role!r}"
            )
        style, _ = markers[0]
        layout[key] = _uniform_number(
            [_side(style, "padding", "left"), _side(style, "padding", "right")],
            role,
        )
    layout["fixed_widths_px"] = sorted(parser.fixed_widths)
    layout["used_spacing_roles"] = list(parser.spacing)
    for role, markers in parser.spacing.items():
        if role not in SPACING_RULES:
            continue
        property_name, side, key = SPACING_RULES[role]
        values: list[float | None] = []
        for style, _ in markers:
            if side == "vertical":
                values.extend(
                    (
                        _side(style, property_name, "top"),
                        _side(style, property_name, "bottom"),
                    )
                )
            else:
                values.append(_side(style, property_name, side))
        layout[key] = _uniform_number(values, role)
    if not str(layout.get("alignment_behavior", "")).strip():
        layout["alignment_behavior"] = (
            "Alignment behavior is machine-extracted from the selected typography roles."
        )

    roles, body_indent = _extract_typography(fragment)
    candidate["typography"]["roles"] = roles
    if body_indent is not None:
        candidate["typography"]["body_first_line_indent_em"] = body_indent
    candidate["typography"]["role_relationships"] = "; ".join(
        f"{role} {values['font_size_px']:g}px/{values['line_height']:g}"
        for role, values in roles.items()
    )

    geometry = candidate["geometry"]
    geometry["used_roles"] = list(parser.geometry)
    geometry["implementations"] = {
        role: sorted(
            {
                f"{property_name}:{value}"
                for style, _ in markers
                for property_name, value in style.items()
            }
        )
        for role, markers in parser.geometry.items()
    }
    geometry_fields = {
        "edge-language": "edge_language",
        "divider-policy": "divider_policy",
        "surface-policy": "surface_policy",
        "radius-policy": "radius_policy",
        "content-native-motif": "content_native_motif",
    }
    for role, key in geometry_fields.items():
        geometry[key] = (
            f"Machine-extracted from data-geometry-role={role}."
            if role in parser.geometry
            else f"N/A: the selected HTML does not use {role}."
        )
    geometry["recurrence_limit"] = (
        f"The selected HTML contains {sum(len(items) for items in parser.geometry.values())} "
        "geometry-role marker(s)."
    )

    _extract_media(parser, candidate)
    _extract_palette(fragment, candidate)

    markup = MarkupParser(
        allow_media_placeholders=candidate["delivery"]["target"] == "local-preview"
    )
    markup.feed(fragment)
    markup.close()
    effect_kind = (
        "svg-smil"
        if "svg" in markup.tags
        else "static-css"
        if markup.expressive_css_used
        else "none"
    )
    effects = candidate["effects"]
    effects["kind"] = effect_kind
    if effect_kind != "none":
        defaults = {
            "semantic_job": "Support the selected article hierarchy.",
            "static_state": "Essential content is visible in the initial rendered state.",
            "fallback": "Retain readable single-column content when the effect is stripped.",
            "compatibility_risk": "The WeChat editor may simplify conditional presentation.",
            "test_obligation": "Inspect the final draft in the WeChat editor and on a phone.",
        }
        for key, value in defaults.items():
            if not str(effects.get(key, "")).strip():
                effects[key] = value

    candidate["status"] = "PLANNED"
    candidate["checks"]["design_values_verified"] = True
    candidate["checks"]["implementation_extracted"] = True
    candidate["checks"]["fragment_sha256"] = ""
    return candidate


def record_plan(article_dir: Path) -> dict[str, Any]:
    article_dir = article_dir.expanduser().resolve()
    manifest, article, fragment_file = _workspace_files(article_dir)
    contract = load_contract(article_dir / "design-contract.json")
    if contract.get("schema_version") != 4:
        raise WorkspaceError("plan requires a schema-4 design contract")
    if contract.get("status") not in {"EXPLORING", "PLANNED"}:
        raise WorkspaceError("plan accepts only an EXPLORING or PLANNED design contract")
    _check_title(article, contract)
    contract = _extract_selected_implementation(contract, fragment_file)
    validate_contract(contract, required_status="PLANNED")
    warnings = contract_warnings(contract)
    warnings.extend(
        finding
        for finding in audit_typography_html(_extract_fragment(fragment_file), contract)
        if finding.get("severity") == "warning"
    )

    plan_iterations = manifest.get("active_plan_iterations")
    if type(plan_iterations) is not int or plan_iterations < 0:
        raise WorkspaceError("manifest active_plan_iterations must be a non-negative integer")

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
            "warnings": warnings,
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
        "warnings": warnings,
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
