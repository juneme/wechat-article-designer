#!/usr/bin/env python3
"""Audit WeChat fragment markup, inline CSS, URLs, and editor compatibility."""

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
        load_contract,
        validate_contract,
    )
except ImportError:
    from design_contract import (  # type: ignore[no-redef]
        ContractError,
        exception_map,
        load_contract,
        validate_contract,
    )

START = "<!-- 微信公众号复制开始 -->"
END = "<!-- 微信公众号复制结束 -->"
HTML_TAGS = {
    "a",
    "blockquote",
    "br",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "img",
    "li",
    "ol",
    "p",
    "section",
    "span",
    "strong",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "ul",
}
SVG_TAGS = {
    "animate",
    "animatetransform",
    "circle",
    "clippath",
    "defs",
    "desc",
    "ellipse",
    "g",
    "image",
    "line",
    "mask",
    "path",
    "polygon",
    "polyline",
    "rect",
    "set",
    "svg",
    "text",
    "title",
    "tspan",
}
ALLOWED_TAGS = HTML_TAGS | SVG_TAGS
VOID_TAGS = {"br", "img"}
GLOBAL_ATTRIBUTES = {
    "aria-label",
    "aria-labelledby",
    "data-content-kind",
    "data-density",
    "data-caption-for",
    "data-geometry-role",
    "data-indent-role",
    "data-layout-role",
    "data-media-crop",
    "data-media-id",
    "data-module-id",
    "data-spacing-role",
    "data-type-role",
    "id",
    "role",
    "style",
    "title",
}
TAG_ATTRIBUTES = {
    "a": {"href", "rel", "target"},
    "img": {"alt", "height", "src", "width"},
    "ol": {"reversed", "start", "type"},
    "li": {"value"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan", "scope"},
    "svg": {"fill", "height", "preserveaspectratio", "stroke", "viewbox", "width", "xmlns", "xmlns:xlink"},
    "g": {"fill", "opacity", "stroke", "stroke-width", "transform"},
    "path": {"d", "fill", "fill-rule", "opacity", "pathlength", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-width", "transform"},
    "circle": {"cx", "cy", "fill", "opacity", "r", "stroke", "stroke-width", "transform"},
    "ellipse": {"cx", "cy", "fill", "opacity", "rx", "ry", "stroke", "stroke-width", "transform"},
    "rect": {"fill", "height", "opacity", "rx", "ry", "stroke", "stroke-width", "transform", "width", "x", "y"},
    "line": {"opacity", "stroke", "stroke-dasharray", "stroke-linecap", "stroke-width", "transform", "x1", "x2", "y1", "y2"},
    "polyline": {"fill", "opacity", "points", "stroke", "stroke-linecap", "stroke-linejoin", "stroke-width", "transform"},
    "polygon": {"fill", "opacity", "points", "stroke", "stroke-linejoin", "stroke-width", "transform"},
    "text": {"dominant-baseline", "fill", "font-family", "font-size", "font-weight", "text-anchor", "transform", "x", "y"},
    "tspan": {"dx", "dy", "fill", "font-family", "font-size", "font-weight", "text-anchor", "x", "y"},
    "image": {"height", "href", "preserveaspectratio", "width", "x", "xlink:href", "y"},
    "clippath": {"clippathunits", "transform"},
    "mask": {"height", "maskunits", "width", "x", "y"},
    "animate": {"accumulate", "additive", "attributename", "begin", "calcmode", "dur", "fill", "from", "href", "keytimes", "keysplines", "repeatcount", "restart", "to", "values", "xlink:href"},
    "animatetransform": {"accumulate", "additive", "attributename", "begin", "calcmode", "dur", "fill", "from", "href", "keytimes", "keysplines", "repeatcount", "restart", "to", "type", "values", "xlink:href"},
    "set": {"attributename", "begin", "dur", "fill", "href", "restart", "to", "xlink:href"},
}
ALLOWED_CSS = {
    "align-items",
    "aspect-ratio",
    "background",
    "background-color",
    "background-image",
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
    "display",
    "flex",
    "flex-basis",
    "flex-direction",
    "flex-grow",
    "flex-shrink",
    "flex-wrap",
    "font-family",
    "font-size",
    "font-style",
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
    "text-align",
    "text-decoration",
    "text-indent",
    "text-shadow",
    "text-transform",
    "transform",
    "transform-origin",
    "vertical-align",
    "white-space",
    "width",
    "word-break",
    "writing-mode",
}
DENIED_CSS_PREFIXES = ("animation", "grid", "position", "transition")
CONDITIONAL_CSS = {
    "aspect-ratio",
    "box-shadow",
    "opacity",
    "object-fit",
    "object-position",
    "text-shadow",
    "transform",
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
    def __init__(self, *, allow_media_placeholders: bool = False) -> None:
        super().__init__(convert_charrefs=True)
        self.allow_media_placeholders = allow_media_placeholders
        self.stack: list[tuple[str, int]] = []
        self.findings: list[dict[str, object]] = []
        self.tags: set[str] = set()
        self.expressive_css_used = False

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
        line = self.getpos()[0]
        self.tags.add(tag)
        if tag not in ALLOWED_TAGS:
            self.add("tag-not-allowed", line, f"Tag <{tag}> is not allowed.")
        if tag == "table":
            self.add(
                "real-table-editor-test",
                line,
                "A real data table requires exact editor and phone testing.",
                warning=True,
            )

        names = [name for name, _ in attrs]
        if len(names) != len(set(names)):
            self.add("duplicate-attribute", line, f"Tag <{tag}> has duplicate attributes.")
        allowed = GLOBAL_ATTRIBUTES | TAG_ATTRIBUTES.get(tag, set())
        for name, raw_value in attrs:
            value = raw_value or ""
            if name.startswith("on") or name in {"contenteditable", "srcdoc"}:
                self.add("unsafe-attribute", line, f"Attribute {name} is prohibited.")
                continue
            if name not in allowed:
                self.add(
                    "attribute-not-allowed",
                    line,
                    f"Attribute {name} is not allowlisted for <{tag}>.",
                )
            if name == "style":
                self._audit_style(value, line)
            if tag in {"img", "image"} and name in {"src", "href", "xlink:href"}:
                placeholder = value.lower().startswith("wechat-media://")
                if not value.lower().startswith("https://") and not (
                    self.allow_media_placeholders and placeholder
                ):
                    self.add(
                        "non-hosted-image",
                        line,
                        "Article images must use final HTTPS URLs.",
                    )
            if tag == "a" and name == "href" and not re.match(
                r"^(?:https://|mailto:|tel:|#)", value, re.IGNORECASE
            ):
                self.add("unsafe-link", line, "Links must use HTTPS, mailto, tel, or a fragment.")
            if tag in {"animate", "animatetransform", "set"} and name == "begin":
                if re.search(r"(?:click|mouse|focus|touch)", value, re.IGNORECASE):
                    self.add(
                        "interaction-dependent-motion",
                        line,
                        "Interaction-triggered SMIL requires an exact editor test and readable fallback.",
                        warning=True,
                    )

        if tag not in VOID_TAGS:
            self.stack.append((tag, line))

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
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
            self.add("comment-not-allowed", self.getpos()[0], "Only boundary comments are allowed.")

    def handle_data(self, data: str) -> None:
        if data.strip() and not self.stack:
            self.add(
                "text-outside-element",
                self.getpos()[0],
                "Visible fragment text must be inside an allowlisted element.",
            )

    def handle_decl(self, decl: str) -> None:
        self.add("document-wrapper", self.getpos()[0], "Fragments cannot contain a document declaration.")

    def unknown_decl(self, data: str) -> None:
        self.add("unknown-declaration", self.getpos()[0], "Unknown HTML declaration.")

    def close(self) -> None:
        super().close()
        for tag, line in self.stack:
            self.add("unclosed-tag", line, f"Tag <{tag}> is not closed.")
        self.stack.clear()

    def _audit_style(self, raw: str, line: int) -> None:
        if re.search(r"@(?:keyframes|import|font-face)", raw, re.IGNORECASE):
            self.add("css-rule-not-allowed", line, "CSS at-rules are prohibited.")
        if re.search(r"(?:expression|javascript:|url\s*\(|var\s*\()", raw, re.IGNORECASE):
            self.add("unsafe-css-value", line, "CSS URL, expression, or variable syntax is prohibited.")
        for name, value in _style_declarations(raw):
            if not name:
                self.add("invalid-css-declaration", line, f"Invalid CSS declaration {value!r}.")
                continue
            if name.startswith(DENIED_CSS_PREFIXES) or name in {
                "bottom",
                "inset",
                "left",
                "right",
                "top",
                "z-index",
            }:
                self.add("css-property-prohibited", line, f"CSS property {name} is prohibited.")
                continue
            if name not in ALLOWED_CSS:
                self.add(
                    "unknown-css-property",
                    line,
                    f"CSS property {name} is outside the compatibility allowlist.",
                    warning=True,
                )
            if name == "display" and value.strip().lower() == "grid":
                self.add("css-grid-prohibited", line, "CSS Grid is prohibited.")
            conditional = name in CONDITIONAL_CSS
            conditional = conditional or (
                name == "display" and value.strip().lower() in {"flex", "inline-flex"}
            )
            conditional = conditional or (
                name in {"background", "background-image"}
                and "gradient(" in value.lower()
            )
            conditional = conditional or (
                name == "overflow-x" and value.strip().lower() in {"auto", "scroll"}
            )
            expressive = name in {
                "box-shadow",
                "opacity",
                "text-shadow",
                "transform",
                "writing-mode",
            }
            expressive = expressive or (
                name in {"background", "background-image"}
                and "gradient(" in value.lower()
            )
            if expressive:
                self.expressive_css_used = True
            if conditional:
                self.add(
                    "conditional-css-editor-test",
                    line,
                    f"Conditional CSS {name} requires an exact editor test.",
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
    contract: dict[str, Any],
    *,
    require_boundary: bool = True,
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
                        "message": "fragment.html may contain only markers and publishable content.",
                        "warning_candidate": False,
                    }
                )

    parser = MarkupParser(
        allow_media_placeholders=contract["delivery"]["target"] == "local-preview"
    )
    parser.feed(value)
    parser.close()
    findings.extend(parser.findings)
    if parser.expressive_css_used and "svg" not in parser.tags:
        if contract["effects"]["kind"] != "static-css":
            findings.append(
                {
                    "code": "effect-contract-mismatch",
                    "line": 1,
                    "message": "Expressive CSS requires effects.kind=static-css.",
                    "warning_candidate": False,
                }
            )
    if "svg" in parser.tags:
        if contract["effects"]["kind"] != "svg-smil":
            findings.append(
                {
                    "code": "motion-contract-mismatch",
                    "line": 1,
                    "message": "SVG markup requires effects.kind=svg-smil.",
                    "warning_candidate": False,
                }
            )

    exceptions = exception_map(contract)
    resolved: list[dict[str, object]] = []
    for finding in findings:
        warning_candidate = bool(finding.pop("warning_candidate"))
        reason = exceptions.get(str(finding["code"])) if warning_candidate else None
        finding["severity"] = "warning" if warning_candidate else "error"
        finding["acknowledged"] = bool(reason)
        if reason:
            finding["exception_reason"] = reason
        resolved.append(finding)
    return resolved


def audit(path: Path, contract_path: Path) -> dict[str, object]:
    contract = load_contract(contract_path)
    validate_contract(contract, required_status="READY")
    value, require_boundary = _article_html(path)
    findings = audit_html(value, contract, require_boundary=require_boundary)
    errors = [item for item in findings if item["severity"] == "error"]
    return {
        "ok": not errors,
        "article": path.name,
        "contract": contract_path.name,
        "error_count": len(errors),
        "warning_count": len(findings) - len(errors),
        "findings": findings,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit WeChat markup and inline CSS")
    parser.add_argument("article", type=Path, help="fragment HTML or article JSON")
    parser.add_argument("--contract", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if not args.article.is_file():
            raise ValueError(f"article file does not exist: {args.article}")
        result = audit(args.article, args.contract)
    except (OSError, UnicodeError, json.JSONDecodeError, ContractError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
