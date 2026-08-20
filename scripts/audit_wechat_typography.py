#!/usr/bin/env python3
"""Audit inline typography in the WeChat copy boundary."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path

START = "<!-- 微信公众号复制开始 -->"
END = "<!-- 微信公众号复制结束 -->"
TITLE_HINTS = re.compile(r"(?:TITLE|HEADING|MASTHEAD|HERO_ACTION)")
DATA_HINTS = re.compile(r"(?:NUMBER|COUNT|SALARY|ORDER)")
CJK = re.compile(r"[\u3400-\u9fff]")
PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def is_body_token(token: str) -> bool:
    return (
        token in {"BODY", "INTRO", "DECK", "PARAGRAPH", "ACTION_METHOD"}
        or token.startswith("BODY_")
        or token.endswith("_BODY")
        or "COPY_LINE" in token
        or bool(re.fullmatch(r"REQUIREMENT(?:_\d+)?", token))
        or bool(re.fullmatch(r"BENEFIT_\d+_DESC", token))
    )


def parse_style(raw: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for declaration in raw.split(";"):
        if ":" not in declaration:
            continue
        key, value = declaration.split(":", 1)
        result[key.strip().lower()] = value.strip()
    return result


def px(value: str | None) -> float | None:
    if not value:
        return None
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)px", value.strip())
    return float(match.group(1)) if match else None


def leading(value: str | None, font_size: float | None) -> float | None:
    if not value:
        return None
    value = value.strip()
    if re.fullmatch(r"\d+(?:\.\d+)?", value):
        return float(value)
    line_px = px(value)
    if line_px is not None and font_size:
        return line_px / font_size
    return None


class TypographyParser(HTMLParser):
    def __init__(self, line_offset: int = 0) -> None:
        super().__init__(convert_charrefs=True)
        self.line_offset = line_offset
        self.stack: list[dict[str, object]] = []
        self.nodes: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "br":
            for node in self.stack:
                node["br"] = int(node["br"]) + 1
            return
        if tag in VOID_TAGS:
            return
        attr_map = dict(attrs)
        node = {
            "tag": tag,
            "style": parse_style(attr_map.get("style") or ""),
            "text": [],
            "line": self.getpos()[0] + self.line_offset,
            "br": 0,
        }
        self.stack.append(node)
        if tag in {"p", "span"}:
            self.nodes.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "br":
            for node in self.stack:
                node["br"] = int(node["br"]) + 1

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        for node in self.stack:
            node["text"].append(data)


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
    parser = TypographyParser(line_offset=prefix.count("\n"))
    parser.feed(fragment)
    findings: list[dict[str, object]] = []

    def add(code: str, node: dict[str, object], message: str) -> None:
        findings.append({"code": code, "line": node["line"], "message": message})

    for node in parser.nodes:
        style = node["style"]
        text = re.sub(r"\s+", " ", "".join(node["text"])).strip()
        if not text or text == "&nbsp;":
            continue
        size = px(style.get("font-size"))
        line_height = leading(style.get("line-height"), size)
        spacing = px(style.get("letter-spacing"))
        tokens = PLACEHOLDER.findall(text)
        literal_text = PLACEHOLDER.sub("", text).strip()
        is_body = any(is_body_token(token) for token in tokens) or (
            len(literal_text) >= 42 and (size or 15) <= 18
        )
        is_title = bool(TITLE_HINTS.search(text)) and not DATA_HINTS.search(text)
        is_data = bool(DATA_HINTS.search(text))

        if is_body and size is not None and size < 14:
            add("body-font-size", node, f"Body-like text is {size:g}px; use 14px only for compact facts and normally 15-16px.")
        if is_body and line_height is not None and line_height < 1.75:
            add("body-line-height", node, f"Body-like leading is {line_height:.2f}; use at least 1.75 and normally 1.85-2.0.")
        if size is not None and size >= 28 and not is_data and line_height is not None and line_height < 1.15:
            add("display-line-height", node, f"Display leading is {line_height:.2f}; multi-line mobile titles need at least 1.15.")
        if is_title and size is not None and size >= 30:
            if "word-break" not in style and "overflow-wrap" not in style:
                add("title-wrap", node, "Large title lacks word-break or overflow-wrap protection for long Latin text.")
        if spacing is not None and spacing != 0 and CJK.search(text):
            add("cjk-letter-spacing", node, "Chinese text must use zero letter spacing.")
        if spacing is not None and spacing > 1 and "{{" in text and not re.search(r"(?:_EN|LABEL|EYEBROW|PUBLICATION_LINE)", text):
            add("placeholder-letter-spacing", node, "Content placeholder may become Chinese text but uses letter spacing above 1px.")
        if style.get("text-align") == "center" and (is_body or len(text) > 48):
            add("centered-prose", node, "Long prose is centered; mobile reading copy should normally align left.")

    return {
        "ok": not findings,
        "article": path.name,
        "finding_count": len(findings),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit mobile WeChat typography")
    parser.add_argument("article", type=Path, help="WeChat HTML article fragment")
    args = parser.parse_args()
    result = audit(args.article)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
