#!/usr/bin/env python3
"""Audit only mobile readability and body-paragraph indentation boundaries."""

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
CJK = re.compile(r"[\u3400-\u9fff]")


def parse_style(raw: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for declaration in raw.split(";"):
        if ":" not in declaration:
            continue
        key, value = declaration.split(":", 1)
        result[key.strip().lower()] = re.sub(
            r"\s*!important\s*$", "", value, flags=re.IGNORECASE
        ).strip()
    return result


def px(value: str | None) -> float | None:
    if not value:
        return None
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)px", value.strip())
    return float(match.group(1)) if match else None


def leading(value: str | None, font_size: float | None) -> float | None:
    if not value:
        return None
    normalized = value.strip()
    if re.fullmatch(r"\d+(?:\.\d+)?", normalized):
        return float(normalized)
    line_px = px(normalized)
    if line_px is not None and font_size:
        return line_px / font_size
    return None


def _indent(value: str | None) -> tuple[bool, bool]:
    """Return (is_zero, is_two_em) for a machine-readable indent."""
    if value is None:
        return True, False
    normalized = value.strip().lower()
    if normalized in {"0", "0px", "0em", "0rem"}:
        return True, False
    match = re.fullmatch(r"(\d+(?:\.\d+)?)em", normalized)
    return False, bool(match and abs(float(match.group(1)) - 2.0) < 0.001)


class TypographyParser(HTMLParser):
    def __init__(self, line_offset: int = 0) -> None:
        super().__init__(convert_charrefs=True)
        self.line_offset = line_offset
        self.stack: list[dict[str, Any]] = []
        self.nodes: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in VOID_TAGS:
            return
        attributes = {name.lower(): value for name, value in attrs}
        own_style = parse_style(attributes.get("style") or "")
        inherited = dict(self.stack[-1]["effective_style"]) if self.stack else {}
        effective = dict(inherited)
        for name in (
            "font-size",
            "line-height",
            "letter-spacing",
            "text-align",
            "text-indent",
        ):
            if name in own_style:
                effective[name] = own_style[name]
        contexts = set(self.stack[-1]["contexts"]) if self.stack else set()
        if tag in {"blockquote", "figcaption", "li", "ol", "table", "ul"}:
            contexts.add(tag)
        if attributes.get("data-content-kind") in {"dialogue", "quotation"}:
            contexts.add(str(attributes["data-content-kind"]))
        node: dict[str, Any] = {
            "tag": tag,
            "attributes": attributes,
            "own_style": own_style,
            "effective_style": effective,
            "contexts": contexts,
            "line": self.getpos()[0] + self.line_offset,
            "text": [],
        }
        self.stack.append(node)
        self.nodes.append(node)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        for node in self.stack:
            node["text"].append(data)


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


def audit_html(value: str, *, line_offset: int = 0) -> list[dict[str, object]]:
    parser = TypographyParser(line_offset=line_offset)
    parser.feed(value)
    parser.close()
    findings: list[dict[str, object]] = []

    def add(
        code: str,
        node: dict[str, Any],
        message: str,
        *,
        severity: str = "error",
    ) -> None:
        findings.append(
            {
                "code": code,
                "severity": severity,
                "line": node["line"],
                "message": message,
            }
        )

    for node in parser.nodes:
        text = "".join(node["text"])
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            continue
        attributes = node["attributes"]
        own_style = node["own_style"]
        effective = node["effective_style"]
        marker = attributes.get("data-indent-role")
        indent_value = effective.get("text-indent")
        indent_zero, indent_two_em = _indent(indent_value)

        if not indent_zero and not (
            node["tag"] == "p" and marker == "body-paragraph"
        ):
            add(
                "indent-outside-body-paragraph",
                node,
                "Only p[data-indent-role='body-paragraph'] may use first-line indentation.",
            )
        if marker == "body-paragraph":
            if node["tag"] != "p":
                add(
                    "body-indent-marker-on-non-paragraph",
                    node,
                    "The body-paragraph indent marker is valid only on <p>.",
                )
            if not indent_two_em:
                add(
                    "body-indent-not-two-em",
                    node,
                    "A marked body paragraph must declare text-indent:2em.",
                )
        elif marker is not None:
            add(
                "unknown-indent-role",
                node,
                "Unknown data-indent-role value.",
            )

        contexts = node["contexts"]
        cjk_count = len(CJK.findall(normalized))
        body_like = (
            node["tag"] == "p"
            and not contexts.intersection(
                {"blockquote", "dialogue", "figcaption", "li", "quotation", "table"}
            )
            and (marker == "body-paragraph" or cjk_count >= 42)
        )
        if body_like:
            size = px(effective.get("font-size"))
            if size is not None and size < 14:
                add(
                    "body-font-size",
                    node,
                    f"Body prose is {size:g}px; the hard mobile minimum is 14px.",
                )
            line_height = leading(effective.get("line-height"), size)
            if line_height is not None and line_height < 1.5:
                add(
                    "body-line-height",
                    node,
                    f"Body prose leading is {line_height:.2f}; the hard minimum is 1.5.",
                )
            if marker is None and indent_zero:
                add(
                    "body-indent-advisory",
                    node,
                    "Continuous body prose normally uses a two-character first-line indent.",
                    severity="warning",
                )
            if re.match(r"^[\u3000\xa0 ]{2,}", text):
                add(
                    "manual-space-indent",
                    node,
                    "Use text-indent:2em instead of manual leading spaces.",
                )

        if "text-indent" in own_style and node["tag"] not in {"p"} and not indent_zero:
            add(
                "container-indent",
                node,
                "Containers, titles, labels, lists, quotes, captions, and closings use no indent.",
            )
    unique: list[dict[str, object]] = []
    seen: set[tuple[object, object, object]] = set()
    for finding in findings:
        key = (finding["code"], finding["line"], finding["message"])
        if key not in seen:
            seen.add(key)
            unique.append(finding)
    return unique


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
        description="Audit mobile readability and body-only indentation"
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
