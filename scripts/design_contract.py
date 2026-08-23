#!/usr/bin/env python3
"""Create, validate, and render machine-readable article design contracts."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
CROP_VALUE = re.compile(
    r"^(?:natural|prepared|aspect-ratio:(?:\d+(?:\.\d+)?|\.\d+)"
    r"|object-fit:(?:cover|contain):(?:\d+(?:\.\d+)?|\.\d+))$",
    re.IGNORECASE,
)
CSS_DECLARATION = re.compile(r"^[a-z-]+:[^:;]+$", re.IGNORECASE)
UNRESOLVED_TEXT = re.compile(
    r"^(?:todo|tbd|placeholder|fill[ -]?me|待补充|待定|占位)(?:\b|\s|[:：])",
    re.IGNORECASE,
)
STATUS_VALUES = {"INCOMPLETE", "PLANNED", "READY"}
SCOPE_VALUES = {"new-article", "substantial-redesign"}
TYPE_RANGES = {
    "display": ((28.0, 38.0), (1.20, 1.35)),
    "section": ((22.0, 27.0), (1.35, 1.55)),
    "item": ((17.0, 20.0), (1.45, 1.65)),
    "deck": ((15.0, 17.0), (1.75, 1.95)),
    "body": ((15.0, 16.0), (1.85, 2.00)),
    "caption": ((12.0, 13.0), (1.60, 1.80)),
    "label": ((10.0, 12.0), (1.40, 1.60)),
    "code": ((12.0, 14.0), (1.60, 1.80)),
    "data": ((28.0, 52.0), (1.00, 1.20)),
}
ALIGNMENTS = {"left", "center", "right"}
EFFECT_KINDS = {"none", "static-css", "svg-smil"}
MEDIA_STATES = {"generated-local", "hosted", "placeholder", "supplied-local"}
MEDIA_PLACEMENTS = {"body", "cover"}
IMAGE_GENERATION_STATUSES = {"not-required", "pending", "complete", "failed"}
SPACING_ROLES = {"section-gap", "paragraph-gap", "caption-gap", "dense-row-padding"}
GEOMETRY_ROLES = {
    "edge-language",
    "divider-policy",
    "surface-policy",
    "radius-policy",
    "content-native-motif",
}
DENSITY_VALUES = {"open", "moderate", "dense", "pause", "dominant"}
READING_ORDERS = {"single-column", "single-column-with-manual-swipe"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
EXCEPTION_CODES = {
    "agent-offer",
    "body-first-line-indent",
    "conditional-css-editor-test",
    "contrast-manual-review",
    "conversation-history",
    "instruction-echo",
    "interaction-dependent-motion",
    "private-context",
    "real-table-editor-test",
    "reply-request",
    "unknown-css-property",
    "unverifiable-width-expression",
    "workflow-narration",
    "legacy-contract-migration",
}


class ContractError(ValueError):
    pass


def empty_contract(
    title: str,
    *,
    scope: str = "new-article",
    local_preview: bool = True,
) -> dict[str, Any]:
    target = "local-preview" if local_preview else "direct-draft"
    return {
        "schema_version": 3,
        "status": "INCOMPLETE",
        "scope": scope,
        "article_title": title,
        "editorial": {
            "reader": "",
            "narrator": "",
            "topic": title,
            "desired_action": "",
            "reader_situation": "",
            "central_friction": "",
            "judgment": "",
            "reader_gain": "",
            "evidence_boundary": "",
            "reasoning_path": [],
            "module_sequence": [],
            "dominant_module": "",
            "closing_job": "",
        },
        "layout": {
            "reading_order": "single-column",
            "outer_baseline_px": 8,
            "content_inset_px": 18,
            "fixed_width_limit_px": 320,
            "fixed_widths_px": [],
            "section_gap_px": 42,
            "paragraph_gap_px": 10,
            "caption_gap_px": 8,
            "dense_row_padding_px": 16,
            "used_spacing_roles": ["section-gap", "paragraph-gap"],
            "density_curve": [],
            "alignment_behavior": "",
        },
        "typography": {
            "body_first_line_indent_em": 2.0,
            "role_relationships": "",
            "roles": {
                "display": {
                    "font_stack": [
                        "-apple-system",
                        "BlinkMacSystemFont",
                        "Segoe UI",
                        "Microsoft YaHei",
                        "sans-serif",
                    ],
                    "font_size_px": 32,
                    "line_height": 1.30,
                    "font_weight": 700,
                    "alignment": "left",
                    "letter_spacing_px": 0,
                    "wrap": "overflow-wrap:anywhere",
                },
                "body": {
                    "font_stack": [
                        "-apple-system",
                        "BlinkMacSystemFont",
                        "Segoe UI",
                        "Microsoft YaHei",
                        "sans-serif",
                    ],
                    "font_size_px": 16,
                    "line_height": 1.90,
                    "font_weight": 400,
                    "alignment": "left",
                    "letter_spacing_px": 0,
                    "wrap": "overflow-wrap:anywhere",
                },
            },
        },
        "color": {
            "field": {"value": "#FFFFFF", "reason": "Primary reading field"},
            "ink": {"value": "#202020", "reason": "Primary reading ink"},
            "primary_signal": {"value": None, "reason": ""},
            "secondary_signal": {"value": None, "reason": ""},
            "correction": {"value": None, "reason": ""},
            "image_support": [],
            "usage_ratio": "",
            "contrast": {
                "body_min_ratio": 4.0,
                "large_min_ratio": 3.0,
                "rationale": "",
            },
        },
        "media": {"assets": [], "no_media_reason": ""},
        "geometry": {
            "edge_language": "",
            "divider_policy": "",
            "surface_policy": "",
            "radius_policy": "",
            "content_native_motif": "",
            "recurrence_limit": "",
            "used_roles": [],
            "implementations": {},
        },
        "effects": {
            "kind": "none",
            "semantic_job": "",
            "static_state": "",
            "fallback": "",
            "compatibility_risk": "",
            "test_obligation": "",
            "user_review_after_draft": False,
        },
        "delivery": {
            "mode": "steady",
            "backend_ready": not local_preview,
            "target": target,
            "user_requested_preview_only": False,
            "image_policy": "auto-generate-then-preview",
            "image_generation_status": "not-required",
            "image_generation_reason": "N/A: no required image has been declared.",
            "draft_behavior": "create-new-draft",
            "fallback_reason": "",
            "editor_fallback": "",
            "stop_condition": "",
        },
        "must_keep": [],
        "avoid": [],
        "exceptions": [],
        "checks": {
            "editorial_passed": False,
            "design_values_verified": False,
            "fragment_sha256": "",
        },
    }


def load_contract(path: Path) -> dict[str, Any]:
    try:
        value: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read design contract {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("design-contract.json root must be an object")
    return value


def fragment_sha256(fragment: str) -> str:
    """Bind a READY contract to the exact publishable fragment."""
    return hashlib.sha256(fragment.strip().encode("utf-8")).hexdigest()


def _mapping(value: Any, path: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return {}
    return value


def _list(value: Any, path: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{path} must be an array")
        return []
    return value


def _text(
    value: Any,
    path: str,
    errors: list[str],
    *,
    allow_empty: bool = False,
) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        errors.append(f"{path} must be a non-empty string")
        return ""
    normalized = value.strip()
    if re.fullmatch(r"(?:N/A|none)", normalized, re.IGNORECASE):
        errors.append(f"{path} uses {normalized!r} without a reason")
    if UNRESOLVED_TEXT.match(normalized):
        errors.append(f"{path} contains an unresolved placeholder")
    return normalized


def _number(value: Any, path: str, errors: list[str]) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{path} must be a number")
        return None
    return float(value)


def _number_range(
    value: Any,
    path: str,
    low: float,
    high: float,
    errors: list[str],
) -> float | None:
    number = _number(value, path, errors)
    if number is not None and not low <= number <= high:
        errors.append(f"{path} must be between {low:g} and {high:g}")
    return number


def _string_list(value: Any, path: str, errors: list[str]) -> list[str]:
    items = _list(value, path, errors)
    result: list[str] = []
    for index, item in enumerate(items):
        result.append(_text(item, f"{path}[{index}]", errors))
    if not result:
        errors.append(f"{path} must contain at least one item")
    return result


def _reasoned_color(
    value: Any,
    path: str,
    errors: list[str],
    *,
    required: bool = False,
) -> None:
    item = _mapping(value, path, errors)
    color = item.get("value")
    reason = item.get("reason")
    if color is None:
        if required:
            errors.append(f"{path}.value must be a #RRGGBB color")
        _text(reason, f"{path}.reason", errors)
        return
    if not isinstance(color, str) or not HEX_COLOR.fullmatch(color):
        errors.append(f"{path}.value must be a #RRGGBB color or null")
    _text(reason, f"{path}.reason", errors)


def exception_map(contract: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    values = contract.get("exceptions")
    if not isinstance(values, list):
        return result
    for item in values:
        if not isinstance(item, dict):
            continue
        code = item.get("code")
        reason = item.get("reason")
        if isinstance(code, str) and code.strip() and isinstance(reason, str) and reason.strip():
            result[code.strip()] = reason.strip()
    return result


def migrate_contract(contract: dict[str, Any]) -> dict[str, Any]:
    """Upgrade a schema-2 contract without inventing article-specific design facts."""
    version = contract.get("schema_version")
    if version == 3:
        return copy.deepcopy(contract)
    if version != 2:
        raise ContractError(f"cannot migrate design-contract schema {version!r}")

    migrated = copy.deepcopy(contract)
    migrated["schema_version"] = 3
    geometry = migrated.setdefault("geometry", {})
    implementations = geometry.setdefault("implementations", {})
    for role in geometry.get("used_roles", []):
        implementations.setdefault(role, [])
    layout = migrated.setdefault("layout", {})
    reading_order = str(layout.get("reading_order", "")).casefold()
    layout["reading_order"] = (
        "single-column-with-manual-swipe"
        if "swipe" in reading_order or "horizontal" in reading_order
        else "single-column"
    )
    modules = migrated.get("editorial", {}).get("module_sequence", [])
    old_density = layout.get("density_curve", [])
    density: list[str] = []
    for index in range(len(modules)):
        value = str(old_density[index] if index < len(old_density) else "moderate").casefold()
        density.append(
            next(
                (
                    candidate
                    for candidate in ("dominant", "dense", "open", "pause", "moderate")
                    if candidate in value
                ),
                "moderate",
            )
        )
    layout["density_curve"] = density
    for item in migrated.get("media", {}).get("assets", []):
        crop = str(item.get("crop", "")).strip()
        lowered = crop.casefold()
        if item.get("placement") == "cover" or "2.35" in lowered:
            item["crop"] = "aspect-ratio:2.35"
            if item.get("placement") == "cover":
                item["required"] = True
        elif "natural" in lowered:
            item["crop"] = "natural"
        else:
            item["crop"] = "prepared"
    exceptions = migrated.setdefault("exceptions", [])
    if not any(
        isinstance(item, dict) and item.get("code") == "legacy-contract-migration"
        for item in exceptions
    ):
        exceptions.append(
            {
                "code": "legacy-contract-migration",
                "reason": (
                    "Migrated from schema 2; preserve the existing design for minor revisions "
                    "and remove this exception on the next substantial redesign."
                ),
            }
        )
    return migrated


def validate_contract(
    contract: dict[str, Any],
    *,
    required_status: str | None = None,
) -> None:
    errors: list[str] = []
    if contract.get("schema_version") != 3:
        errors.append("schema_version must be 3")

    status = contract.get("status")
    if status not in STATUS_VALUES:
        errors.append("status must be INCOMPLETE, PLANNED, or READY")
    if required_status is not None and status != required_status:
        errors.append(f"status must be {required_status}")
    if contract.get("scope") not in SCOPE_VALUES:
        errors.append("scope must be new-article or substantial-redesign")
    _text(contract.get("article_title"), "article_title", errors)

    editorial = _mapping(contract.get("editorial"), "editorial", errors)
    for key in (
        "reader",
        "narrator",
        "topic",
        "desired_action",
        "reader_situation",
        "central_friction",
        "judgment",
        "reader_gain",
        "evidence_boundary",
        "dominant_module",
        "closing_job",
    ):
        _text(editorial.get(key), f"editorial.{key}", errors)
    _string_list(editorial.get("reasoning_path"), "editorial.reasoning_path", errors)
    module_sequence = _string_list(
        editorial.get("module_sequence"), "editorial.module_sequence", errors
    )

    layout = _mapping(contract.get("layout"), "layout", errors)
    if layout.get("reading_order") not in READING_ORDERS:
        errors.append(
            "layout.reading_order must be single-column or single-column-with-manual-swipe"
        )
    _number_range(layout.get("outer_baseline_px"), "layout.outer_baseline_px", 0, 64, errors)
    _number_range(layout.get("content_inset_px"), "layout.content_inset_px", 0, 80, errors)
    if layout.get("fixed_width_limit_px") != 320:
        errors.append("layout.fixed_width_limit_px must be the hard 320px limit")
    widths = _list(layout.get("fixed_widths_px"), "layout.fixed_widths_px", errors)
    for index, width in enumerate(widths):
        _number_range(width, f"layout.fixed_widths_px[{index}]", 0, 320, errors)
    for key in (
        "section_gap_px",
        "paragraph_gap_px",
        "caption_gap_px",
        "dense_row_padding_px",
    ):
        _number_range(layout.get(key), f"layout.{key}", 0, 80, errors)
    spacing_roles = _string_list(
        layout.get("used_spacing_roles"), "layout.used_spacing_roles", errors
    )
    for role in spacing_roles:
        if role not in SPACING_ROLES:
            errors.append(f"layout.used_spacing_roles contains unsupported role {role!r}")
    density_curve = _string_list(
        layout.get("density_curve"), "layout.density_curve", errors
    )
    if len(density_curve) != len(module_sequence):
        errors.append("layout.density_curve must contain one value per editorial module")
    for index, value in enumerate(density_curve):
        if value not in DENSITY_VALUES:
            errors.append(
                f"layout.density_curve[{index}] must be open, moderate, dense, pause, or dominant"
            )
    _text(layout.get("alignment_behavior"), "layout.alignment_behavior", errors)

    typography = _mapping(contract.get("typography"), "typography", errors)
    indent = _number_range(
        typography.get("body_first_line_indent_em"),
        "typography.body_first_line_indent_em",
        0,
        2,
        errors,
    )
    exceptions = exception_map(contract)
    if indent is not None and indent != 2.0 and "body-first-line-indent" not in exceptions:
        errors.append(
            "typography.body_first_line_indent_em defaults to 2; deviations require "
            "a body-first-line-indent exception"
        )
    _text(
        typography.get("role_relationships"),
        "typography.role_relationships",
        errors,
    )
    roles = _mapping(typography.get("roles"), "typography.roles", errors)
    if not roles:
        errors.append("typography.roles must contain at least one used text role")
    for role, values in roles.items():
        if role not in TYPE_RANGES:
            errors.append(f"typography.roles.{role} is not a supported role")
            continue
        item = _mapping(values, f"typography.roles.{role}", errors)
        size_range, leading_range = TYPE_RANGES[role]
        _string_list(
            item.get("font_stack"),
            f"typography.roles.{role}.font_stack",
            errors,
        )
        _number_range(
            item.get("font_size_px"),
            f"typography.roles.{role}.font_size_px",
            *size_range,
            errors,
        )
        _number_range(
            item.get("line_height"),
            f"typography.roles.{role}.line_height",
            *leading_range,
            errors,
        )
        weight = item.get("font_weight")
        if type(weight) is not int or not 100 <= weight <= 900:
            errors.append(f"typography.roles.{role}.font_weight must be 100-900")
        if item.get("alignment") not in ALIGNMENTS:
            errors.append(
                f"typography.roles.{role}.alignment must be left, center, or right"
            )
        if item.get("letter_spacing_px") != 0:
            errors.append(f"typography.roles.{role}.letter_spacing_px must be 0")
        wrap = _text(item.get("wrap"), f"typography.roles.{role}.wrap", errors)
        if wrap and not re.fullmatch(
            r"(?:overflow-wrap|word-break|white-space):[^:;]+", wrap
        ):
            errors.append(
                f"typography.roles.{role}.wrap must be one inline property:value pair"
            )

    color = _mapping(contract.get("color"), "color", errors)
    _reasoned_color(color.get("field"), "color.field", errors, required=True)
    _reasoned_color(color.get("ink"), "color.ink", errors, required=True)
    for key in ("primary_signal", "secondary_signal", "correction"):
        _reasoned_color(color.get(key), f"color.{key}", errors)
    image_support = _list(color.get("image_support"), "color.image_support", errors)
    for index, value in enumerate(image_support):
        _reasoned_color(value, f"color.image_support[{index}]", errors)
    _text(color.get("usage_ratio"), "color.usage_ratio", errors)
    contrast = _mapping(color.get("contrast"), "color.contrast", errors)
    body_ratio = _number_range(
        contrast.get("body_min_ratio"), "color.contrast.body_min_ratio", 1, 21, errors
    )
    large_ratio = _number_range(
        contrast.get("large_min_ratio"), "color.contrast.large_min_ratio", 1, 21, errors
    )
    if body_ratio is not None and large_ratio is not None and large_ratio > body_ratio:
        errors.append(
            "color.contrast.large_min_ratio cannot exceed body_min_ratio"
        )
    _text(contrast.get("rationale"), "color.contrast.rationale", errors)

    media = _mapping(contract.get("media"), "media", errors)
    assets = _list(media.get("assets"), "media.assets", errors)
    if not assets:
        _text(media.get("no_media_reason"), "media.no_media_reason", errors)
    media_orders: set[float] = set()
    media_names: set[str] = set()
    cover_count = 0
    for index, value in enumerate(assets):
        item = _mapping(value, f"media.assets[{index}]", errors)
        for key in ("name", "reader_job", "authority", "crop", "caption"):
            _text(item.get(key), f"media.assets[{index}].{key}", errors)
        crop = item.get("crop")
        if isinstance(crop, str) and not CROP_VALUE.fullmatch(crop.strip()):
            errors.append(
                f"media.assets[{index}].crop must be natural, prepared, "
                "aspect-ratio:<ratio>, or object-fit:<cover|contain>:<ratio>"
            )
        if item.get("placement") not in MEDIA_PLACEMENTS:
            errors.append(f"media.assets[{index}].placement must be body or cover")
        if item.get("placement") == "cover":
            cover_count += 1
            if item.get("required") is not True:
                errors.append(f"media.assets[{index}].required must be true for a cover")
            if item.get("crop") != "aspect-ratio:2.35":
                errors.append(
                    f"media.assets[{index}].crop must be aspect-ratio:2.35 for a cover"
                )
        name = item.get("name")
        if isinstance(name, str) and name.strip():
            if name in media_names:
                errors.append(f"media.assets[{index}].name duplicates {name!r}")
            media_names.add(name)
        if type(item.get("required")) is not bool:
            errors.append(f"media.assets[{index}].required must be a boolean")
        source_path = item.get("source_path")
        if item.get("state") in {"generated-local", "supplied-local"}:
            _text(source_path, f"media.assets[{index}].source_path", errors)
        elif source_path not in {None, ""}:
            _text(source_path, f"media.assets[{index}].source_path", errors)
        remote_ref = item.get("remote_ref")
        if item.get("state") == "hosted":
            remote = _text(remote_ref, f"media.assets[{index}].remote_ref", errors)
            if item.get("placement") == "body" and remote:
                parsed = urlsplit(remote)
                hostname = (parsed.hostname or "").lower()
                if parsed.scheme != "https" or not (
                    hostname == "mmbiz.qpic.cn" or hostname.endswith(".mmbiz.qpic.cn")
                ):
                    errors.append(
                        f"media.assets[{index}].remote_ref must be a WeChat HTTPS article URL"
                    )
        elif remote_ref not in {None, ""}:
            errors.append(f"media.assets[{index}].remote_ref is only valid for hosted media")
        order = _number_range(
            item.get("order"), f"media.assets[{index}].order", 1, 999, errors
        )
        if order in media_orders:
            errors.append(f"media.assets[{index}].order duplicates {order:g}")
        if order is not None:
            media_orders.add(order)
        if item.get("state") not in MEDIA_STATES:
            errors.append(
                f"media.assets[{index}].state must be generated-local, supplied-local, "
                "placeholder, or hosted"
            )
    if cover_count > 1:
        errors.append("media.assets supports at most one cover")

    geometry = _mapping(contract.get("geometry"), "geometry", errors)
    for key in (
        "edge_language",
        "divider_policy",
        "surface_policy",
        "radius_policy",
        "content_native_motif",
        "recurrence_limit",
    ):
        _text(geometry.get(key), f"geometry.{key}", errors)
    geometry_roles = _list(geometry.get("used_roles"), "geometry.used_roles", errors)
    seen_geometry_roles: set[str] = set()
    for index, role in enumerate(geometry_roles):
        value = _text(role, f"geometry.used_roles[{index}]", errors)
        if value not in GEOMETRY_ROLES:
            errors.append(f"geometry.used_roles[{index}] is not supported")
        if value in seen_geometry_roles:
            errors.append(f"geometry.used_roles[{index}] duplicates {value}")
        seen_geometry_roles.add(value)
    geometry_fields = {
        "edge-language": "edge_language",
        "divider-policy": "divider_policy",
        "surface-policy": "surface_policy",
        "radius-policy": "radius_policy",
        "content-native-motif": "content_native_motif",
    }
    for role, field in geometry_fields.items():
        decision = geometry.get(field)
        active = isinstance(decision, str) and not re.match(
            r"^\s*(?:N/A|none)\s*:", decision, re.IGNORECASE
        )
        if active and role not in seen_geometry_roles:
            errors.append(f"geometry.used_roles must include {role!r} for geometry.{field}")
        if not active and role in seen_geometry_roles:
            errors.append(f"geometry.used_roles cannot include inactive role {role!r}")
    implementations = _mapping(
        geometry.get("implementations"), "geometry.implementations", errors
    )
    legacy_migration = "legacy-contract-migration" in exceptions
    if set(implementations) != seen_geometry_roles:
        errors.append(
            "geometry.implementations keys must exactly match geometry.used_roles"
        )
    for role, declarations_value in implementations.items():
        declarations = _list(
            declarations_value, f"geometry.implementations.{role}", errors
        )
        if not declarations and not legacy_migration:
            errors.append(
                f"geometry.implementations.{role} must contain an inline CSS declaration"
            )
        for index, declaration in enumerate(declarations):
            value = _text(
                declaration,
                f"geometry.implementations.{role}[{index}]",
                errors,
            )
            if value and not CSS_DECLARATION.fullmatch(value):
                errors.append(
                    f"geometry.implementations.{role}[{index}] must be one property:value pair"
                )

    effects = _mapping(contract.get("effects"), "effects", errors)
    if effects.get("kind") not in EFFECT_KINDS:
        errors.append("effects.kind must be none, static-css, or svg-smil")
    for key in (
        "semantic_job",
        "static_state",
        "fallback",
        "compatibility_risk",
        "test_obligation",
    ):
        _text(effects.get(key), f"effects.{key}", errors)
    if type(effects.get("user_review_after_draft")) is not bool:
        errors.append("effects.user_review_after_draft must be a boolean")
    if effects.get("kind") != "none" and effects.get("user_review_after_draft") is not True:
        errors.append("expressive effects require user_review_after_draft=true")

    delivery = _mapping(contract.get("delivery"), "delivery", errors)
    if delivery.get("mode") not in {"steady", "creative"}:
        errors.append("delivery.mode must be steady or creative")
    if effects.get("kind") != "none" and delivery.get("mode") != "creative":
        errors.append("static-css and svg-smil effects require delivery.mode=creative")
    if (
        delivery.get("mode") == "creative"
        and effects.get("user_review_after_draft") is not True
    ):
        errors.append("creative delivery requires effects.user_review_after_draft=true")
    if type(delivery.get("backend_ready")) is not bool:
        errors.append("delivery.backend_ready must be a boolean")
    if delivery.get("target") not in {"direct-draft", "local-preview"}:
        errors.append("delivery.target must be direct-draft or local-preview")
    if type(delivery.get("user_requested_preview_only")) is not bool:
        errors.append("delivery.user_requested_preview_only must be a boolean")
    fallback_reason = delivery.get("fallback_reason")
    if not isinstance(fallback_reason, str):
        errors.append("delivery.fallback_reason must be a string")
        fallback_reason = ""
    if (
        delivery.get("backend_ready") is True
        and delivery.get("user_requested_preview_only") is not True
        and not fallback_reason.strip()
        and delivery.get("target") != "direct-draft"
    ):
        errors.append("a ready backend defaults to delivery.target=direct-draft")
    if delivery.get("backend_ready") is False and delivery.get("target") != "local-preview":
        errors.append("an unavailable backend requires delivery.target=local-preview")
    if delivery.get("target") == "direct-draft" and fallback_reason.strip():
        errors.append("direct-draft delivery cannot retain a fallback_reason")
    if delivery.get("image_policy") != "auto-generate-then-preview":
        errors.append("delivery.image_policy must be auto-generate-then-preview")
    image_generation_status = delivery.get("image_generation_status")
    if image_generation_status not in IMAGE_GENERATION_STATUSES:
        errors.append(
            "delivery.image_generation_status must be not-required, pending, complete, or failed"
        )
    _text(
        delivery.get("image_generation_reason"),
        "delivery.image_generation_reason",
        errors,
    )
    required_placeholders = [
        item
        for item in assets
        if isinstance(item, dict)
        and item.get("required") is True
        and item.get("state") == "placeholder"
    ]
    if required_placeholders and image_generation_status not in {"pending", "failed"}:
        errors.append(
            "required placeholder media requires image_generation_status=pending or failed"
        )
    if status == "READY" and image_generation_status == "pending":
        errors.append("READY delivery cannot retain a pending image-generation attempt")
    if delivery.get("target") == "direct-draft" and image_generation_status == "failed":
        errors.append("failed image generation requires local-preview delivery")
    if delivery.get("draft_behavior") != "create-new-draft":
        errors.append("delivery.draft_behavior must be create-new-draft")
    _text(delivery.get("editor_fallback"), "delivery.editor_fallback", errors)
    _text(delivery.get("stop_condition"), "delivery.stop_condition", errors)
    if status == "READY" and delivery.get("target") == "direct-draft":
        for index, value in enumerate(assets):
            if isinstance(value, dict) and value.get("state") != "hosted":
                errors.append(
                    f"media.assets[{index}].state must be hosted for READY direct draft"
                )

    _string_list(contract.get("must_keep"), "must_keep", errors)
    _string_list(contract.get("avoid"), "avoid", errors)
    exception_values = _list(contract.get("exceptions"), "exceptions", errors)
    seen_codes: set[str] = set()
    for index, value in enumerate(exception_values):
        item = _mapping(value, f"exceptions[{index}]", errors)
        code = _text(item.get("code"), f"exceptions[{index}].code", errors)
        _text(item.get("reason"), f"exceptions[{index}].reason", errors)
        if code and code not in EXCEPTION_CODES:
            errors.append(f"exceptions[{index}].code is not a recognized audit code")
        if code in seen_codes:
            errors.append(f"exceptions[{index}].code duplicates {code}")
        seen_codes.add(code)

    checks = _mapping(contract.get("checks"), "checks", errors)
    for key in ("editorial_passed", "design_values_verified"):
        if type(checks.get(key)) is not bool:
            errors.append(f"checks.{key} must be a boolean")
    if status in {"PLANNED", "READY"}:
        for key in ("editorial_passed", "design_values_verified"):
            if checks.get(key) is not True:
                errors.append(f"checks.{key} must be true for {status}")
    digest = checks.get("fragment_sha256")
    if not isinstance(digest, str):
        errors.append("checks.fragment_sha256 must be a string")
    elif status == "READY" and not SHA256.fullmatch(digest):
        errors.append("checks.fragment_sha256 must bind READY to the final fragment")
    elif status != "READY" and digest:
        errors.append("checks.fragment_sha256 must be empty before READY")

    if errors:
        raise ContractError("design contract is invalid:\n- " + "\n- ".join(errors))


def render_contract_markdown(contract: dict[str, Any]) -> str:
    def block(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False)

    return f"""# Article Design Contract

This file is generated from `design-contract.json`. Do not edit it directly.

- Article: {contract.get('article_title', '')}
- Scope: {contract.get('scope', '')}
- Status: {contract.get('status', '')}

## Editorial and structure

```json
{block(contract.get('editorial', {}))}
```

## Layout and rhythm

```json
{block(contract.get('layout', {}))}
```

## Typography

```json
{block(contract.get('typography', {}))}
```

## Color

```json
{block(contract.get('color', {}))}
```

## Media

```json
{block(contract.get('media', {}))}
```

## Geometry and motif

```json
{block(contract.get('geometry', {}))}
```

## Effects and motion

```json
{block(contract.get('effects', {}))}
```

## Delivery

```json
{block(contract.get('delivery', {}))}
```

## Locked decisions and exceptions

```json
{block({'must_keep': contract.get('must_keep', []), 'avoid': contract.get('avoid', []), 'exceptions': contract.get('exceptions', [])})}
```

## Gate checks

```json
{block(contract.get('checks', {}))}
```
"""
