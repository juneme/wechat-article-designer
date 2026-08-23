#!/usr/bin/env python3
"""Verify structural design-contract values against the final fragment."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

try:
    from .design_contract import (
        ContractError,
        exception_map,
        fragment_sha256,
        load_contract,
        validate_contract,
    )
except ImportError:
    from design_contract import (  # type: ignore[no-redef]
        ContractError,
        exception_map,
        fragment_sha256,
        load_contract,
        validate_contract,
    )

START = "<!-- 微信公众号复制开始 -->"
END = "<!-- 微信公众号复制结束 -->"
PX = re.compile(r"^(-?(?:\d+(?:\.\d+)?|\.\d+))px$", re.IGNORECASE)
SPACING_RULES = {
    "section-gap": ("margin", "top", "section_gap_px"),
    "paragraph-gap": ("margin", "bottom", "paragraph_gap_px"),
    "caption-gap": ("margin", "top", "caption_gap_px"),
    "dense-row-padding": ("padding", "vertical", "dense_row_padding_px"),
}


def _style(value: str | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for declaration in (value or "").split(";"):
        if ":" not in declaration:
            continue
        name, content = declaration.split(":", 1)
        result[name.strip().lower()] = content.strip().lower()
    return result


def _px(value: str) -> float | None:
    if value.strip() in {"0", "+0", "-0"}:
        return 0.0
    match = PX.fullmatch(value.strip())
    return float(match.group(1)) if match else None


def _box(style: dict[str, str], property_name: str) -> tuple[float, float, float, float] | None:
    values = style.get(property_name, "").split()
    if not values:
        return None
    parsed: list[float] = []
    for value in values:
        number = _px(value)
        if number is None:
            return None
        parsed.append(number)
    if len(parsed) == 1:
        return parsed[0], parsed[0], parsed[0], parsed[0]
    if len(parsed) == 2:
        return parsed[0], parsed[1], parsed[0], parsed[1]
    if len(parsed) == 3:
        return parsed[0], parsed[1], parsed[2], parsed[1]
    if len(parsed) == 4:
        return parsed[0], parsed[1], parsed[2], parsed[3]
    return None


def _side(style: dict[str, str], property_name: str, side: str) -> float | None:
    direct = style.get(f"{property_name}-{side}")
    if direct is not None:
        return _px(direct)
    box = _box(style, property_name)
    if box is None:
        return None
    return box[{"top": 0, "right": 1, "bottom": 2, "left": 3}[side]]


class ContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.modules: list[tuple[str, str, int]] = []
        self.media: list[tuple[str, int, str, str, int]] = []
        self.spacing: dict[str, list[tuple[dict[str, str], int]]] = {}
        self.geometry: dict[str, list[tuple[dict[str, str], int]]] = {}
        self.layout: dict[str, list[tuple[dict[str, str], int]]] = {}
        self.fixed_widths: set[float] = set()
        self.captions: list[dict[str, Any]] = []
        self._open_tags: list[str] = []
        self._active_captions: list[dict[str, Any]] = []
        self._event_index = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        line = self.getpos()[0]
        self._event_index += 1
        module = values.get("data-module-id")
        if module:
            self.modules.append((module, values.get("data-density") or "", line))
        media = values.get("data-media-id")
        if media:
            self.media.append(
                (
                    media,
                    line,
                    values.get("src") or "",
                    values.get("data-media-crop") or "",
                    self._event_index,
                )
            )
        caption = values.get("data-caption-for")
        if caption:
            record: dict[str, Any] = {
                "name": caption,
                "line": line,
                "tag": tag,
                "depth": len(self._open_tags),
                "parts": [],
                "event": self._event_index,
            }
            self._active_captions.append(record)
        spacing = values.get("data-spacing-role")
        if spacing:
            self.spacing.setdefault(spacing, []).append((_style(values.get("style")), line))
        style = _style(values.get("style"))
        geometry = values.get("data-geometry-role")
        if geometry:
            for role in geometry.split():
                self.geometry.setdefault(role, []).append((style, line))
        layout = values.get("data-layout-role")
        if layout:
            self.layout.setdefault(layout, []).append((style, line))
        for property_name in ("width", "min-width", "max-width"):
            width = _px(style.get(property_name, ""))
            if width is not None:
                self.fixed_widths.add(width)
        if tag not in {"svg", "rect", "image", "mask"}:
            attribute_width = values.get("width")
            if attribute_width and re.fullmatch(r"\d+(?:\.\d+)?", attribute_width):
                self.fixed_widths.add(float(attribute_width))
        if tag not in {"br", "img"}:
            self._open_tags.append(tag)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in {"br", "img"}:
            self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        for record in self._active_captions:
            record["parts"].append(data)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self._open_tags) - 1, -1, -1):
            if self._open_tags[index] != tag:
                continue
            closing = [
                record
                for record in self._active_captions
                if record["tag"] == tag and record["depth"] == index
            ]
            for record in closing:
                self.captions.append(record)
                self._active_captions.remove(record)
            del self._open_tags[index:]
            break


def _extract(raw: str) -> tuple[str, int]:
    if raw.count(START) != 1 or raw.count(END) != 1:
        raise ValueError("fragment must contain exactly one WeChat boundary pair")
    prefix, remainder = raw.split(START, 1)
    fragment, suffix = remainder.split(END, 1)
    if prefix.strip() or suffix.strip():
        raise ValueError("fragment may contain only the boundary pair and publishable HTML")
    return fragment.strip(), prefix.count("\n")


def audit_html(fragment: str, contract: dict[str, Any]) -> list[dict[str, object]]:
    parser = ContractParser()
    parser.feed(fragment)
    parser.close()
    findings: list[dict[str, object]] = []
    legacy_migration = "legacy-contract-migration" in exception_map(contract)

    def add(code: str, message: str, line: int = 1) -> None:
        findings.append({"code": code, "severity": "error", "line": line, "message": message})

    expected_digest = contract["checks"]["fragment_sha256"]
    actual_digest = fragment_sha256(fragment)
    if expected_digest != actual_digest:
        add("fragment-contract-digest", "The READY contract does not bind this exact fragment.")

    expected_modules = contract["editorial"]["module_sequence"]
    actual_modules = [name for name, _, _ in parser.modules]
    if actual_modules != expected_modules:
        add(
            "module-sequence-contract-mismatch",
            f"Expected data-module-id order {expected_modules!r}; found {actual_modules!r}.",
            parser.modules[0][2] if parser.modules else 1,
        )

    expected_density = contract["layout"]["density_curve"]
    actual_density = [density for _, density, _ in parser.modules]
    if not legacy_migration and actual_density != expected_density:
        add(
            "density-curve-contract-mismatch",
            f"Expected module density {expected_density!r}; found {actual_density!r}.",
            parser.modules[0][2] if parser.modules else 1,
        )

    layout = contract["layout"]
    expected_layout_roles = {"outer-baseline", "content-inset"}
    if not legacy_migration and set(parser.layout) != expected_layout_roles:
        add(
            "layout-role-contract-mismatch",
            f"Expected layout markers {sorted(expected_layout_roles)!r}; "
            f"found {sorted(parser.layout)!r}.",
        )
    for role, contract_name in (
        ("outer-baseline", "outer_baseline_px"),
        ("content-inset", "content_inset_px"),
    ):
        if legacy_migration:
            continue
        expected = float(layout[contract_name])
        for style, line in parser.layout.get(role, []):
            actual = (_side(style, "padding", "left"), _side(style, "padding", "right"))
            if not all(value is not None and abs(value - expected) <= 0.01 for value in actual):
                add(
                    "layout-value-contract-mismatch",
                    f"{role} requires horizontal padding {expected:g}px; found {actual!r}.",
                    line,
                )
    expected_widths = {float(value) for value in layout["fixed_widths_px"]}
    if not legacy_migration and parser.fixed_widths != expected_widths:
        add(
            "fixed-widths-contract-mismatch",
            f"Expected fixed widths {sorted(expected_widths)!r}; "
            f"found {sorted(parser.fixed_widths)!r}.",
        )
    expected_spacing = set(layout["used_spacing_roles"])
    if set(parser.spacing) != expected_spacing:
        add(
            "spacing-roles-contract-mismatch",
            f"Expected spacing roles {sorted(expected_spacing)!r}; "
            f"found {sorted(parser.spacing)!r}.",
        )
    for role in layout["used_spacing_roles"]:
        markers = parser.spacing.get(role, [])
        if not markers:
            add("missing-spacing-role", f"No element implements data-spacing-role={role!r}.")
            continue
        property_name, side, contract_name = SPACING_RULES[role]
        expected = float(layout[contract_name])
        for style, line in markers:
            if side == "vertical":
                actual = (_side(style, property_name, "top"), _side(style, property_name, "bottom"))
                matches = all(value is not None and abs(value - expected) <= 0.01 for value in actual)
            else:
                value = _side(style, property_name, side)
                actual = value
                matches = value is not None and abs(value - expected) <= 0.01
            if not matches:
                add(
                    "spacing-contract-mismatch",
                    f"{role} requires {expected:g}px; found {actual!r}.",
                    line,
                )

    expected_geometry = set(contract["geometry"]["used_roles"])
    if set(parser.geometry) != expected_geometry:
        add(
            "geometry-contract-mismatch",
            f"Expected geometry markers {sorted(expected_geometry)!r}; "
            f"found {sorted(parser.geometry)!r}.",
        )
    implementations = contract["geometry"]["implementations"]
    for role in expected_geometry:
        markers = parser.geometry.get(role, [])
        for declaration in implementations.get(role, []):
            property_name, expected_value = declaration.split(":", 1)
            if not any(
                style.get(property_name.strip().lower()) == expected_value.strip().lower()
                for style, _ in markers
            ):
                add(
                    "geometry-css-contract-mismatch",
                    f"Geometry role {role!r} does not implement {declaration!r}.",
                    markers[0][1] if markers else 1,
                )

    expected_media = [
        item["name"]
        for item in sorted(contract["media"]["assets"], key=lambda item: item["order"])
        if item["placement"] == "body"
    ]
    actual_media = [name for name, _, _, _, _ in parser.media]
    if actual_media != expected_media:
        add(
            "media-order-contract-mismatch",
            f"Expected body media order {expected_media!r}; found {actual_media!r}.",
            parser.media[0][1] if parser.media else 1,
        )
    expected_urls = {
        item["name"]: item.get("remote_ref")
        for item in contract["media"]["assets"]
        if item["placement"] == "body" and item["state"] == "hosted"
    }
    body_assets = {
        item["name"]: item
        for item in contract["media"]["assets"]
        if item["placement"] == "body"
    }
    for name, line, source, crop, _ in parser.media:
        expected = expected_urls.get(name)
        if expected is not None and source != expected:
            add(
                "media-source-contract-mismatch",
                f"Body media {name!r} does not use its recorded hosted URL.",
                line,
            )
        asset = body_assets.get(name)
        if not legacy_migration and asset is not None and crop != asset["crop"]:
            add(
                "media-crop-contract-mismatch",
                f"Body media {name!r} requires data-media-crop={asset['crop']!r}.",
                line,
            )
    captions_by_media: dict[str, list[dict[str, Any]]] = {}
    for record in parser.captions:
        captions_by_media.setdefault(str(record["name"]), []).append(record)
    for name, asset in body_assets.items():
        if legacy_migration:
            continue
        records = captions_by_media.get(name, [])
        caption = str(asset["caption"]).strip()
        omitted = bool(re.match(r"^(?:N/A|none)\s*:", caption, re.IGNORECASE))
        if omitted and records:
            add(
                "unexpected-media-caption",
                f"Body media {name!r} records no caption but the fragment contains one.",
                int(records[0]["line"]),
            )
        if not omitted:
            actual_text = [
                re.sub(r"\s+", " ", "".join(record["parts"])).strip()
                for record in records
            ]
            media_line, media_event = next(
                (
                    (line, event)
                    for media_name, line, _, _, event in parser.media
                    if media_name == name
                ),
                (1, -1),
            )
            valid_caption = (
                len(records) == 1
                and actual_text == [caption]
                and int(records[0]["event"]) > media_event
            )
            if not valid_caption:
                add(
                    "media-caption-contract-mismatch",
                    f"Body media {name!r} requires one following caption with exact contract text.",
                    int(records[0]["line"]) if records else media_line,
                )
    unexpected_captions = set(captions_by_media) - set(body_assets)
    for name in sorted(unexpected_captions):
        add(
            "unknown-media-caption",
            f"Caption references unknown body media {name!r}.",
            int(captions_by_media[name][0]["line"]),
        )
    return findings


def audit(path: Path, contract_path: Path) -> dict[str, object]:
    contract = load_contract(contract_path)
    validate_contract(contract, required_status="READY")
    fragment, line_offset = _extract(path.read_text(encoding="utf-8"))
    findings = audit_html(fragment, contract)
    for finding in findings:
        finding["line"] = int(finding["line"]) + line_offset
    return {
        "ok": not findings,
        "article": path.name,
        "contract": contract_path.name,
        "error_count": len(findings),
        "warning_count": 0,
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the final fragment against its design contract")
    parser.add_argument("article", type=Path)
    parser.add_argument("--contract", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = audit(args.article, args.contract)
    except (OSError, UnicodeError, json.JSONDecodeError, ContractError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
