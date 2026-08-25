#!/usr/bin/env python3
"""Detect width structures that exceed the hard 320px article limit."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

PERCENTAGE = re.compile(r"^([0-9]+(?:\.[0-9]+)?)%$")
PIXELS = re.compile(r"^([0-9]+(?:\.[0-9]+)?)px$")
HARD_WIDTH_PX = 320.0
VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


def _style_map(value: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for declaration in value.split(";"):
        if ":" not in declaration:
            continue
        name, raw_value = declaration.split(":", 1)
        result[name.strip().lower()] = raw_value.strip().lower()
    return result


class _Node:
    def __init__(
        self,
        tag: str,
        style: dict[str, str],
        attributes: dict[str, str | None],
        line: int,
        parent: _Node | None,
    ) -> None:
        self.tag = tag
        self.style = style
        self.attributes = attributes
        self.line = line
        self.parent = parent
        self.children: list[_Node] = []


class _TreeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.nodes: list[_Node] = []
        self.stack: list[_Node] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        parent = self.stack[-1] if self.stack else None
        node = _Node(
            tag=tag,
            style=_style_map(attributes.get("style") or ""),
            attributes=attributes,
            line=self.getpos()[0],
            parent=parent,
        )
        if parent is not None:
            parent.children.append(node)
        self.nodes.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break


def _normalized(value: str | None) -> str | None:
    if value is None:
        return None
    return re.sub(r"\s*!important\s*$", "", value, flags=re.IGNORECASE).strip()


def _percentage(value: str | None) -> float | None:
    normalized = _normalized(value)
    match = PERCENTAGE.fullmatch(normalized or "")
    return float(match.group(1)) if match else None


def _pixels(value: str | None) -> float | None:
    normalized = _normalized(value)
    match = PIXELS.fullmatch(normalized or "")
    return float(match.group(1)) if match else None


def audit_html(value: str) -> list[dict[str, Any]]:
    parser = _TreeParser()
    parser.feed(value)
    parser.close()
    findings: list[dict[str, Any]] = []

    for node in parser.nodes:
        # A numeric width attribute on an outer rendered image or SVG viewport is
        # a CSS-pixel width. Inside SVG, width is normally a coordinate in the
        # viewBox and must not be compared with the article column.
        ancestor = node.parent
        has_svg_ancestor = False
        while ancestor is not None:
            if ancestor.tag == "svg":
                has_svg_ancestor = True
                break
            ancestor = ancestor.parent
        attribute_width = (
            node.attributes.get("width")
            if node.tag == "img" or (node.tag == "svg" and not has_svg_ancestor)
            else None
        )
        if (
            node.style.get("width") is None
            and isinstance(attribute_width, str)
            and re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", attribute_width.strip())
        ):
            attribute_width = f"{attribute_width.strip()}px"
        values: dict[str, str | None] = {
            "width": node.style.get("width") or attribute_width,
            "min-width": node.style.get("min-width"),
            "max-width": node.style.get("max-width"),
        }
        for property_name, raw in values.items():
            percent = _percentage(raw)
            pixels = _pixels(raw)
            if percent is not None and percent > 100:
                findings.append(
                    {
                        "code": "width-over-100-percent",
                        "severity": "error",
                        "line": node.line,
                        "property": property_name,
                        "value": raw,
                    }
                )
            if pixels is not None and pixels > HARD_WIDTH_PX:
                findings.append(
                    {
                        "code": "fixed-width-over-320px",
                        "severity": "error",
                        "line": node.line,
                        "property": property_name,
                        "value": raw,
                    }
                )
            normalized = _normalized(raw)
            if normalized and percent is None and pixels is None and normalized not in {
                "auto",
                "none",
            }:
                findings.append(
                    {
                        "code": "unverifiable-width-expression",
                        "severity": "warning",
                        "line": node.line,
                        "property": property_name,
                        "value": raw,
                    }
                )

        if node.style.get("overflow-x") not in {"auto", "scroll"}:
            continue

        non_card_children = [
            child
            for child in node.children
            if child.style.get("display") != "inline-block"
        ]
        if non_card_children:
            findings.append(
                {
                    "code": "swipe-items-not-direct-inline-blocks",
                    "severity": "error",
                    "line": node.line,
                    "child_lines": [child.line for child in non_card_children],
                }
            )

        for child in node.children:
            child_width = _pixels(child.style.get("width"))
            if child_width is not None and child_width > HARD_WIDTH_PX:
                findings.append(
                    {
                        "code": "swipe-item-over-320px",
                        "severity": "error",
                        "line": child.line,
                        "value": child.style.get("width"),
                    }
                )

        ancestor = node.parent
        while ancestor is not None:
            if ancestor.style.get("overflow") == "hidden" or ancestor.style.get(
                "overflow-x"
            ) == "hidden":
                findings.append(
                    {
                        "code": "swipe-inside-clipping-ancestor",
                        "severity": "error",
                        "line": node.line,
                        "ancestor_line": ancestor.line,
                    }
                )
                break
            ancestor = ancestor.parent

    return findings


def _article_html(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() != ".json":
        return raw
    payload: Any = json.loads(raw)
    if not isinstance(payload, dict) or not isinstance(payload.get("content"), str):
        raise ValueError("article JSON must contain a string content field")
    return payload["content"]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect widths that exceed the hard 320px WeChat limit"
    )
    parser.add_argument("article", help="HTML or article JSON path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    path = Path(args.article).expanduser()
    try:
        if not path.is_file():
            raise ValueError(f"article file does not exist: {args.article}")
        findings = audit_html(_article_html(path))
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ValueError,
    ) as exc:
        print(
            json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 1

    errors = [item for item in findings if item["severity"] == "error"]
    print(
        json.dumps(
            {
                "ok": not errors,
                "article": path.name,
                "error_count": len(errors),
                "warning_count": len(findings) - len(errors),
                "findings": findings,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
