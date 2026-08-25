#!/usr/bin/env python3
"""Audit publishable WeChat markup without judging its visual style."""

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
HTML_TAGS = {
    "a",
    "b",
    "blockquote",
    "br",
    "div",
    "em",
    "figcaption",
    "figure",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "img",
    "li",
    "ol",
    "p",
    "section",
    "small",
    "span",
    "strong",
    "sub",
    "sup",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "u",
    "ul",
}
SVG_TAGS = {
    "animate",
    "animatemotion",
    "animatetransform",
    "circle",
    "clippath",
    "defs",
    "desc",
    "ellipse",
    "feblend",
    "fecolormatrix",
    "fecomponenttransfer",
    "fecomposite",
    "fedisplacementmap",
    "fedropshadow",
    "feflood",
    "fefunca",
    "fefuncb",
    "fefuncg",
    "fefuncr",
    "fegaussianblur",
    "feimage",
    "femerge",
    "femergenode",
    "feoffset",
    "filter",
    "g",
    "image",
    "line",
    "lineargradient",
    "marker",
    "mask",
    "mpath",
    "path",
    "pattern",
    "polygon",
    "polyline",
    "radialgradient",
    "rect",
    "set",
    "stop",
    "svg",
    "symbol",
    "text",
    "textpath",
    "title",
    "tspan",
    "use",
}
ALLOWED_TAGS = HTML_TAGS | SVG_TAGS
VOID_TAGS = {"br", "hr", "img"}
PROHIBITED_TAGS = {
    "audio",
    "base",
    "body",
    "button",
    "embed",
    "foreignobject",
    "form",
    "head",
    "html",
    "iframe",
    "input",
    "link",
    "meta",
    "object",
    "option",
    "script",
    "select",
    "source",
    "style",
    "textarea",
    "video",
}
KNOWN_CSS = {
    "align-content",
    "align-items",
    "align-self",
    "aspect-ratio",
    "background",
    "background-color",
    "background-image",
    "background-position",
    "background-repeat",
    "background-size",
    "border",
    "border-bottom",
    "border-color",
    "border-left",
    "border-radius",
    "border-right",
    "border-style",
    "border-top",
    "border-width",
    "box-shadow",
    "box-sizing",
    "color",
    "column-gap",
    "display",
    "filter",
    "flex",
    "flex-basis",
    "flex-direction",
    "flex-flow",
    "flex-grow",
    "flex-shrink",
    "flex-wrap",
    "font-family",
    "font-size",
    "font-style",
    "font-variant",
    "font-weight",
    "gap",
    "height",
    "justify-content",
    "letter-spacing",
    "line-height",
    "margin",
    "margin-bottom",
    "margin-left",
    "margin-right",
    "margin-top",
    "max-height",
    "max-width",
    "min-height",
    "min-width",
    "object-fit",
    "object-position",
    "opacity",
    "overflow",
    "overflow-wrap",
    "overflow-x",
    "overflow-y",
    "padding",
    "padding-bottom",
    "padding-left",
    "padding-right",
    "padding-top",
    "row-gap",
    "text-align",
    "text-decoration",
    "text-indent",
    "text-overflow",
    "text-shadow",
    "text-transform",
    "transform",
    "transform-origin",
    "vertical-align",
    "white-space",
    "width",
    "word-break",
    "word-spacing",
    "writing-mode",
}


def _style_declarations(raw: str) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for item in raw.split(";"):
        if not item.strip():
            continue
        if ":" not in item:
            result.append(("", item.strip()))
            continue
        name, value = item.split(":", 1)
        result.append((name.strip().lower(), value.strip()))
    return result


class MarkupParser(HTMLParser):
    """Collect hard safety failures and advisory editor-compatibility warnings."""

    def __init__(self, *, allow_media_placeholders: bool = False) -> None:
        super().__init__(convert_charrefs=True)
        self.allow_media_placeholders = allow_media_placeholders
        self.stack: list[tuple[str, int]] = []
        self.findings: list[dict[str, object]] = []

    def add(
        self,
        code: str,
        line: int,
        message: str,
        *,
        warning: bool = False,
    ) -> None:
        self.findings.append(
            {
                "code": code,
                "line": line,
                "message": message,
                "warning_candidate": warning,
            }
        )

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        line = self.getpos()[0]
        if tag in PROHIBITED_TAGS:
            self.add("active-or-external-content", line, f"Tag <{tag}> is prohibited.")
        elif tag not in ALLOWED_TAGS:
            self.add(
                "unknown-element",
                line,
                f"Tag <{tag}> is not in the tested WeChat vocabulary.",
                warning=True,
            )
        if tag == "table":
            self.add(
                "real-table-editor-test",
                line,
                "A real table needs exact editor and phone testing.",
                warning=True,
            )

        names = [name.lower() for name, _ in attrs]
        if len(names) != len(set(names)):
            self.add("duplicate-attribute", line, f"Tag <{tag}> has duplicate attributes.")
        for raw_name, raw_value in attrs:
            name = raw_name.lower()
            value = raw_value or ""
            if name.startswith("on") or name in {"contenteditable", "srcdoc"}:
                self.add("unsafe-attribute", line, f"Attribute {name} is prohibited.")
            if name in {"href", "src", "xlink:href"} and re.match(
                r"^(?:data|file|javascript|vbscript):", value, re.IGNORECASE
            ):
                self.add("unsafe-url", line, f"Attribute {name} uses an unsafe URL.")
            if name == "style":
                self._audit_style(value, line)
            if tag in {"img", "image", "feimage"} and name in {
                "src",
                "href",
                "xlink:href",
            }:
                placeholder = value.lower().startswith("wechat-media://")
                internal_svg = value.startswith("#")
                if not value.lower().startswith("https://") and not internal_svg and not (
                    self.allow_media_placeholders and placeholder
                ):
                    self.add(
                        "non-hosted-image",
                        line,
                        "Publishable images must use final HTTPS URLs.",
                    )
            if tag == "a" and name == "href" and not re.match(
                r"^(?:https://|mailto:|tel:|#)", value, re.IGNORECASE
            ):
                self.add(
                    "unsafe-link",
                    line,
                    "Links must use HTTPS, mailto, tel, or a fragment.",
                )
            if tag in {"mpath", "textpath", "use"} and name in {
                "href",
                "xlink:href",
            } and not value.startswith("#"):
                self.add(
                    "external-svg-reference",
                    line,
                    "SVG references must target an element in the same fragment.",
                )
            if tag in {"animate", "animatemotion", "animatetransform", "set"}:
                if name == "begin" and re.search(
                    r"(?:click|mouse|focus|touch)", value, re.IGNORECASE
                ):
                    self.add(
                        "interaction-dependent-motion",
                        line,
                        "Interaction-triggered SVG motion needs a readable initial state.",
                        warning=True,
                    )
        if tag not in VOID_TAGS:
            self.stack.append((tag, line))

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        line = self.getpos()[0]
        if not self.stack:
            self.add("unexpected-closing-tag", line, f"Unexpected closing tag </{tag}>.")
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
            return
        expected = self.stack[-1][0]
        self.add(
            "mismatched-closing-tag",
            line,
            f"Expected </{expected}> before </{tag}>.",
        )
        matches = [index for index, item in enumerate(self.stack) if item[0] == tag]
        if matches:
            del self.stack[matches[-1] :]

    def handle_comment(self, data: str) -> None:
        if data.strip() not in {"微信公众号复制开始", "微信公众号复制结束"}:
            self.add(
                "comment-not-allowed",
                self.getpos()[0],
                "Private comments must not enter publishable copy.",
            )

    def handle_data(self, data: str) -> None:
        if data.strip() and not self.stack:
            self.add(
                "text-outside-element",
                self.getpos()[0],
                "Visible fragment text must be inside an element.",
            )

    def handle_decl(self, decl: str) -> None:
        self.add(
            "document-wrapper",
            self.getpos()[0],
            "Publishable content must be an HTML fragment, not a document.",
        )

    def close(self) -> None:
        super().close()
        for tag, line in self.stack:
            self.add("unclosed-tag", line, f"Tag <{tag}> is not closed.")
        self.stack.clear()

    def _audit_style(self, raw: str, line: int) -> None:
        if re.search(r"@(?:keyframes|import|font-face)", raw, re.IGNORECASE):
            self.add("css-rule-not-allowed", line, "CSS at-rules are prohibited.")
        if re.search(
            r"(?:expression\s*\(|javascript:|url\s*\(|var\s*\()",
            raw,
            re.IGNORECASE,
        ):
            self.add(
                "unsafe-css-value",
                line,
                "CSS URLs, expressions, and variables are prohibited.",
            )
        for name, value in _style_declarations(raw):
            if not name:
                self.add(
                    "invalid-css-declaration",
                    line,
                    f"Invalid CSS declaration {value!r}.",
                )
                continue
            lowered = value.lower()
            if name == "display" and lowered == "grid":
                self.add("css-grid-prohibited", line, "CSS Grid is not reliable in WeChat.")
            if name == "position" and lowered in {"absolute", "fixed", "sticky"}:
                self.add(
                    "positioned-layout-prohibited",
                    line,
                    f"Position {lowered} is not reliable in WeChat.",
                )
            if name.startswith("animation") or name.startswith("transition"):
                self.add(
                    "css-motion-not-publishable",
                    line,
                    f"CSS property {name} requires a style block and is not publishable.",
                )
            if name not in KNOWN_CSS and name not in {
                "bottom",
                "inset",
                "left",
                "position",
                "right",
                "top",
                "z-index",
            }:
                self.add(
                    "untested-css-property",
                    line,
                    f"CSS property {name} needs exact editor testing.",
                    warning=True,
                )
            if name in {
                "filter",
                "transform",
                "writing-mode",
            } or "gradient(" in lowered:
                self.add(
                    "expressive-css-editor-test",
                    line,
                    f"Expressive CSS {name} needs exact editor testing.",
                    warning=True,
                )


def _article_html(path: Path) -> tuple[str, bool]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() != ".json":
        return raw, True
    payload: Any = json.loads(raw)
    if not isinstance(payload, dict) or not isinstance(payload.get("content"), str):
        raise ValueError("article JSON must contain a string content field")
    return payload["content"], False


def audit_html(
    value: str,
    *,
    require_boundary: bool = True,
    allow_media_placeholders: bool = False,
) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    if require_boundary:
        if value.count(START) != 1 or value.count(END) != 1:
            findings.append(
                {
                    "code": "copy-boundary",
                    "line": 1,
                    "message": "HTML must contain exactly one WeChat boundary pair.",
                    "warning_candidate": False,
                }
            )
        elif value.index(START) > value.index(END):
            findings.append(
                {
                    "code": "copy-boundary-order",
                    "line": 1,
                    "message": "The WeChat boundary markers are reversed.",
                    "warning_candidate": False,
                }
            )
        else:
            prefix, remainder = value.split(START, 1)
            _, suffix = remainder.split(END, 1)
            if prefix.strip() or suffix.strip():
                findings.append(
                    {
                        "code": "content-outside-boundary",
                        "line": 1,
                        "message": "fragment.html may contain only publishable content.",
                        "warning_candidate": False,
                    }
                )
    parser = MarkupParser(allow_media_placeholders=allow_media_placeholders)
    parser.feed(value)
    parser.close()
    findings.extend(parser.findings)
    resolved: list[dict[str, object]] = []
    for finding in findings:
        warning = bool(finding.pop("warning_candidate"))
        finding["severity"] = "warning" if warning else "error"
        resolved.append(finding)
    return resolved


def audit(path: Path, *, allow_media_placeholders: bool = False) -> dict[str, object]:
    value, require_boundary = _article_html(path)
    findings = audit_html(
        value,
        require_boundary=require_boundary,
        allow_media_placeholders=allow_media_placeholders,
    )
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
        description="Audit WeChat safety and editor compatibility"
    )
    parser.add_argument("article", type=Path, help="fragment HTML or article JSON")
    parser.add_argument("--allow-media-placeholders", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if not args.article.is_file():
            raise ValueError(f"article file does not exist: {args.article}")
        result = audit(
            args.article,
            allow_media_placeholders=args.allow_media_placeholders,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
