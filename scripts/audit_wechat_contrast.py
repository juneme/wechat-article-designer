#!/usr/bin/env python3
"""Detect objectively unreadable text contrast without policing the palette."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

START = "<!-- 微信公众号复制开始 -->"
END = "<!-- 微信公众号复制结束 -->"
COLOR = re.compile(
    r"^(?:#(?P<hex>[0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})|"
    r"rgba?\((?P<rgb>[^)]+)\))$",
    re.IGNORECASE,
)
COLOR_TOKEN = re.compile(
    r"#[0-9a-f]{8}|#[0-9a-f]{6}|#[0-9a-f]{3}|rgba?\([^)]+\)",
    re.IGNORECASE,
)
TRANSPARENT = (0.0, 0.0, 0.0, 0.0)
BLACK = (0.0, 0.0, 0.0, 1.0)
WHITE = (255.0, 255.0, 255.0, 1.0)
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


def declarations(raw: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for declaration in raw.split(";"):
        if ":" not in declaration:
            continue
        key, value = declaration.split(":", 1)
        result[key.strip().lower()] = re.sub(
            r"\s*!important\s*$", "", value, flags=re.IGNORECASE
        ).strip()
    return result


def parse_color(value: str | None) -> tuple[float, float, float, float] | None:
    if not value:
        return None
    value = value.strip()
    if value.lower() == "transparent":
        return TRANSPARENT
    match = COLOR.fullmatch(value)
    if not match:
        return None
    if match.group("hex"):
        raw = match.group("hex")
        if len(raw) == 3:
            return tuple(float(int(char * 2, 16)) for char in raw) + (1.0,)
        if len(raw) == 6:
            return tuple(float(int(raw[index : index + 2], 16)) for index in (0, 2, 4)) + (1.0,)
        return tuple(float(int(raw[index : index + 2], 16)) for index in (0, 2, 4)) + (
            int(raw[6:8], 16) / 255.0,
        )
    parts = [part.strip() for part in match.group("rgb").split(",")]
    if len(parts) not in {3, 4}:
        return None
    try:
        channels = [
            float(part.rstrip("%")) * 2.55 if part.endswith("%") else float(part)
            for part in parts[:3]
        ]
        alpha = float(parts[3]) if len(parts) == 4 else 1.0
    except ValueError:
        return None
    return tuple(max(0.0, min(255.0, channel)) for channel in channels) + (
        max(0.0, min(1.0, alpha)),
    )


def composite(
    foreground: tuple[float, float, float, float],
    background: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    alpha = foreground[3] + background[3] * (1.0 - foreground[3])
    if alpha == 0:
        return TRANSPARENT
    channels = tuple(
        (
            foreground[index] * foreground[3]
            + background[index] * background[3] * (1.0 - foreground[3])
        )
        / alpha
        for index in range(3)
    )
    return channels + (alpha,)


def luminance(color: tuple[float, float, float, float]) -> float:
    def channel(value: float) -> float:
        value /= 255.0
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(color[0]) + 0.7152 * channel(color[1]) + 0.0722 * channel(color[2])


def contrast(
    foreground: tuple[float, float, float, float],
    background: tuple[float, float, float, float],
) -> float:
    front = composite(foreground, background) if foreground[3] < 1 else foreground
    lighter, darker = sorted(
        (luminance(front), luminance(background)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


def color_label(color: tuple[float, float, float, float]) -> str:
    return "#" + "".join(f"{round(channel):02X}" for channel in color[:3])


def _px(value: str | None) -> float | None:
    if not value:
        return None
    match = re.fullmatch(r"(\d+(?:\.\d+)?)px", value.strip())
    return float(match.group(1)) if match else None


def _weight(value: str | None) -> int:
    if not value or value.lower() == "normal":
        return 400
    if value.lower() in {"bold", "bolder"}:
        return 700
    return int(value) if re.fullmatch(r"[1-9]00", value) else 400


class _Node:
    def __init__(
        self,
        *,
        tag: str,
        line: int,
        color: tuple[float, float, float, float] | None,
        background: tuple[float, float, float, float],
        background_declared: bool,
        uncertain_background: bool,
        font_size: str | None,
        font_weight: str | None,
    ) -> None:
        self.tag = tag
        self.line = line
        self.color = color
        self.background = background
        self.background_declared = background_declared
        self.uncertain_background = uncertain_background
        self.font_size = font_size
        self.font_weight = font_weight


class ContrastParser(HTMLParser):
    def __init__(self, line_offset: int = 0) -> None:
        super().__init__(convert_charrefs=True)
        self.line_offset = line_offset
        self.stack: list[_Node] = []
        self.segments: list[dict[str, object]] = []
        self.declared_colors: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        style = declarations(attributes.get("style") or "")
        line = self.getpos()[0] + self.line_offset
        for property_name, raw_value in style.items():
            if property_name in {
                "background",
                "background-color",
                "box-shadow",
                "color",
                "text-shadow",
            } or property_name.startswith("border"):
                for token in COLOR_TOKEN.findall(raw_value):
                    self.declared_colors.append(
                        {
                            "line": line,
                            "property": property_name,
                            "value": token,
                        }
                    )
        for property_name in ("fill", "stroke"):
            raw_value = attributes.get(property_name)
            if raw_value and COLOR_TOKEN.fullmatch(raw_value.strip()):
                self.declared_colors.append(
                    {
                        "line": line,
                        "property": property_name,
                        "value": raw_value.strip(),
                    }
                )
        parent = self.stack[-1] if self.stack else None
        color = parent.color if parent else BLACK
        background = parent.background if parent else WHITE
        background_declared = parent.background_declared if parent else False
        uncertain = parent.uncertain_background if parent else False
        font_size = parent.font_size if parent else None
        font_weight = parent.font_weight if parent else None
        background_effect = False

        if "color" in style:
            color = parse_color(style["color"])
        if tag in {"g", "text", "tspan"} and "fill" in attributes:
            color = parse_color(attributes["fill"])
        if "font-size" in style:
            font_size = style["font-size"]
        if "font-weight" in style:
            font_weight = style["font-weight"]
        elif tag in {"b", "strong"}:
            font_weight = "700"

        if "background" in style:
            parsed = parse_color(style["background"])
            if parsed is None:
                if style["background"].lower() not in {"none", "initial"}:
                    uncertain = True
                    background_effect = True
            elif parsed[3] > 0:
                background = composite(parsed, background) if parsed[3] < 1 else parsed
                background_declared = True
                if parsed[3] == 1:
                    uncertain = False
        if "background-color" in style:
            parsed = parse_color(style["background-color"])
            if parsed is None:
                uncertain = True
            elif parsed[3] > 0:
                background = composite(parsed, background) if parsed[3] < 1 else parsed
                background_declared = True
                if parsed[3] == 1:
                    uncertain = False
        if style.get("background-image", "none").lower() != "none":
            background_effect = True
        if background_effect:
            uncertain = True
        if tag in {"text", "tspan"}:
            uncertain = True

        node = _Node(
            tag=tag,
            line=line,
            color=color,
            background=background,
            background_declared=background_declared,
            uncertain_background=uncertain,
            font_size=font_size,
            font_weight=font_weight,
        )
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

    def handle_data(self, data: str) -> None:
        if not data.strip() or not self.stack:
            return
        anchor = next(
            (
                node
                for node in reversed(self.stack)
                if node.tag
                in {
                    "blockquote",
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                    "li",
                    "p",
                    "span",
                    "td",
                    "text",
                    "th",
                    "tspan",
                }
            ),
            None,
        )
        if anchor is None:
            return
        current = self.stack[-1]
        self.segments.append(
            {
                "line": anchor.line,
                "text": re.sub(r"\s+", " ", data).strip(),
                "color": current.color,
                "background": current.background,
                "background_declared": current.background_declared,
                "uncertain_background": current.uncertain_background,
                "font_size": current.font_size,
                "font_weight": current.font_weight,
            }
        )


def _article_html(path: Path) -> tuple[str, int]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        payload: Any = json.loads(raw)
        if not isinstance(payload, dict) or not isinstance(payload.get("content"), str):
            raise ValueError("article JSON must contain a string content field")
        return payload["content"], 0
    if raw.count(START) != 1 or raw.count(END) != 1 or raw.index(START) > raw.index(END):
        raise ValueError("HTML must contain exactly one ordered WeChat boundary pair")
    prefix, remainder = raw.split(START, 1)
    return remainder.split(END, 1)[0], prefix.count("\n")


def audit_html(
    value: str,
    *,
    line_offset: int = 0,
) -> list[dict[str, object]]:
    parser = ContrastParser(line_offset=line_offset)
    parser.feed(value)
    parser.close()
    findings: list[dict[str, object]] = []
    seen_manual: set[int] = set()

    for segment in parser.segments:
        line = int(segment["line"])
        if segment["uncertain_background"] or segment["color"] is None:
            if line in seen_manual:
                continue
            seen_manual.add(line)
            findings.append(
                {
                "code": "contrast-manual-review",
                "severity": "warning",
                "line": line,
                "message": "Text on an image, gradient, or unparseable color requires manual contrast confirmation.",
                }
            )
            continue

        foreground = segment["color"]
        background = segment["background"]
        ratio = contrast(foreground, background)
        minimum = 3.0
        if ratio + 1e-6 < minimum:
            findings.append(
                {
                    "code": "text-contrast",
                    "severity": "error",
                    "line": line,
                    "message": (
                        f"{color_label(foreground)} on {color_label(background)} is "
                        f"{ratio:.2f}:1; the hard readability floor is {minimum:g}:1."
                    ),
                }
            )
    return findings


def audit(path: Path) -> dict[str, object]:
    value, line_offset = _article_html(path)
    findings = audit_html(value, line_offset=line_offset)
    errors = [item for item in findings if item["severity"] == "error"]
    return {
        "ok": not errors,
        "article": path.name,
        "error_count": len(errors),
        "warning_count": len(findings) - len(errors),
        "findings": findings,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect objectively unreadable WeChat text contrast"
    )
    parser.add_argument("article", type=Path, help="HTML fragment or article JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if not args.article.is_file():
            raise ValueError(f"article file does not exist: {args.article}")
        result = audit(args.article)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
