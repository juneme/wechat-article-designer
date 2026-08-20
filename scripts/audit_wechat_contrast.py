#!/usr/bin/env python3
"""Audit text contrast against effective solid backgrounds in a WeChat fragment."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path

START = "<!-- 微信公众号复制开始 -->"
END = "<!-- 微信公众号复制结束 -->"
COLOR = re.compile(
    r"^(?:#(?P<hex>[0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})|"
    r"rgba?\((?P<rgb>[^)]+)\))$",
    re.IGNORECASE,
)
TRANSPARENT = (0.0, 0.0, 0.0, 0.0)
WHITE = (255.0, 255.0, 255.0, 1.0)
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def declarations(raw: str) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for declaration in raw.split(";"):
        if ":" not in declaration:
            continue
        key, value = declaration.split(":", 1)
        result.append((key.strip().lower(), value.strip()))
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
        return tuple(float(int(raw[index : index + 2], 16)) for index in (0, 2, 4)) + (int(raw[6:8], 16) / 255.0,)
    parts = [part.strip() for part in match.group("rgb").split(",")]
    if len(parts) not in {3, 4}:
        return None
    try:
        channels = [float(part.rstrip("%")) * 2.55 if part.endswith("%") else float(part) for part in parts[:3]]
        alpha = float(parts[3]) if len(parts) == 4 else 1.0
    except ValueError:
        return None
    return tuple(max(0.0, min(255.0, channel)) for channel in channels) + (max(0.0, min(1.0, alpha)),)


def composite(
    foreground: tuple[float, float, float, float],
    background: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    alpha = foreground[3] + background[3] * (1.0 - foreground[3])
    if alpha == 0:
        return TRANSPARENT
    channels = tuple(
        (foreground[index] * foreground[3] + background[index] * background[3] * (1.0 - foreground[3])) / alpha
        for index in range(3)
    )
    return channels + (alpha,)


def luminance(color: tuple[float, float, float, float]) -> float:
    def channel(value: float) -> float:
        value /= 255.0
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(color[0]) + 0.7152 * channel(color[1]) + 0.0722 * channel(color[2])


def contrast(foreground: tuple[float, float, float, float], background: tuple[float, float, float, float]) -> float:
    front = composite(foreground, background) if foreground[3] < 1 else foreground
    lighter, darker = sorted((luminance(front), luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def color_label(color: tuple[float, float, float, float]) -> str:
    return "#" + "".join(f"{round(channel):02X}" for channel in color[:3])


def px(value: str | None) -> float | None:
    if not value:
        return None
    match = re.fullmatch(r"(\d+(?:\.\d+)?)px", value.strip())
    return float(match.group(1)) if match else None


def weight(value: str | None) -> int:
    if not value:
        return 400
    if value == "bold":
        return 700
    try:
        return int(value)
    except ValueError:
        return 400


class ContrastParser(HTMLParser):
    def __init__(self, line_offset: int = 0) -> None:
        super().__init__(convert_charrefs=True)
        self.line_offset = line_offset
        self.stack: list[dict[str, object]] = []
        self.nodes: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in VOID_TAGS:
            return
        attr_map = dict(attrs)
        rules = declarations(attr_map.get("style") or "")
        inherited_color = self.stack[-1]["color"] if self.stack else (0.0, 0.0, 0.0, 1.0)
        canvas = self.stack[-1]["background"] if self.stack else WHITE
        node_color = inherited_color
        node_background = canvas
        style: dict[str, str] = {}
        for key, value in rules:
            style[key] = value
            if key == "color":
                parsed = parse_color(value)
                if parsed is not None:
                    node_color = parsed
            if key in {"background", "background-color"}:
                parsed = parse_color(value)
                if parsed is not None:
                    node_background = composite(parsed, canvas) if parsed[3] < 1 else parsed
        node = {
            "tag": tag,
            "style": style,
            "color": node_color,
            "background": node_background,
            "text": [],
            "line": self.getpos()[0] + self.line_offset,
        }
        self.stack.append(node)
        if tag in {"p", "span"}:
            self.nodes.append(node)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if self.stack and self.stack[-1]["tag"] in {"p", "span"}:
            self.stack[-1]["text"].append(data)


def audit(path: Path) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8")
    if START not in raw or END not in raw:
        return {
            "ok": False,
            "article": path.name,
            "finding_count": 1,
            "findings": [{"code": "copy-boundary", "line": 1, "message": "Missing WeChat copy boundary."}],
        }
    prefix, fragment_and_end = raw.split(START, 1)
    fragment = fragment_and_end.split(END, 1)[0]
    parser = ContrastParser(line_offset=prefix.count("\n"))
    parser.feed(fragment)
    findings: list[dict[str, object]] = []
    for node in parser.nodes:
        text = re.sub(r"\s+", " ", "".join(node["text"])).strip()
        style = node["style"]
        size = px(style.get("font-size"))
        if not text or text == "&nbsp;" or (size is not None and size <= 1):
            continue
        foreground = node["color"]
        background = node["background"]
        if foreground[3] == 0 or background[3] < 1:
            continue
        ratio = contrast(foreground, background)
        is_large = size is not None and (size >= 24 or (size >= 18.66 and weight(style.get("font-weight")) >= 700))
        minimum = 3.0 if is_large else 4.5
        if ratio + 1e-6 < minimum:
            findings.append(
                {
                    "code": "text-contrast",
                    "line": node["line"],
                    "message": (
                        f"{color_label(foreground)} on {color_label(background)} is {ratio:.2f}:1; "
                        f"this text role needs at least {minimum:.1f}:1."
                    ),
                }
            )
    return {"ok": not findings, "article": path.name, "finding_count": len(findings), "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit text contrast in a mobile WeChat fragment")
    parser.add_argument("article", type=Path, help="WeChat HTML article fragment")
    args = parser.parse_args()
    result = audit(args.article)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
