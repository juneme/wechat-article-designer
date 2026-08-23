#!/usr/bin/env python3
"""Validate implemented article typography against design-contract.json."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

try:
    from .design_contract import ContractError, load_contract, validate_contract
except ImportError:
    from design_contract import (  # type: ignore[no-redef]
        ContractError,
        load_contract,
        validate_contract,
    )

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
INHERITED_PROPERTIES = {
    "font-family",
    "font-size",
    "font-style",
    "font-weight",
    "letter-spacing",
    "line-height",
    "overflow-wrap",
    "text-align",
    "text-indent",
    "text-transform",
    "white-space",
    "word-break",
}
MANUAL_INDENT_SPACE = re.compile(
    r"^[\u00a0\u1680\u2000-\u200a\u202f\u205f\u3000\ufeff]"
)
CONTAINER_TAGS = {
    "blockquote",
    "li",
    "ol",
    "section",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "ul",
}
SINGLE_LINE_HEADING_ROLES = {"display", "section"}
SINGLE_LINE_HEADING_BUDGET_PX = 288.0


def parse_style(raw: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for declaration in raw.split(";"):
        if ":" not in declaration:
            continue
        name, value = declaration.split(":", 1)
        result[name.strip().lower()] = re.sub(
            r"\s*!important\s*$", "", value, flags=re.IGNORECASE
        ).strip()
    return result


def _number_unit(value: str | None, unit: str) -> float | None:
    if not value:
        return None
    match = re.fullmatch(rf"(-?\d+(?:\.\d+)?){re.escape(unit)}", value.strip())
    return float(match.group(1)) if match else None


def _line_height(value: str | None, font_size: float | None) -> float | None:
    if not value:
        return None
    normalized = value.strip()
    if re.fullmatch(r"\d+(?:\.\d+)?", normalized):
        return float(normalized)
    pixels = _number_unit(normalized, "px")
    return pixels / font_size if pixels is not None and font_size else None


def _font_weight(value: str | None) -> int | None:
    if not value:
        return None
    normalized = value.strip().lower()
    if normalized == "normal":
        return 400
    if normalized in {"bold", "bolder"}:
        return 700
    if re.fullmatch(r"[1-9]00", normalized):
        return int(normalized)
    return None


def _font_stack(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [
        part.strip().strip("\"'").casefold()
        for part in value.split(",")
        if part.strip()
    ]


def _zero_px(value: str | None) -> bool:
    if value is None:
        return False
    return bool(re.fullmatch(r"(?:0+(?:\.0+)?|0+(?:\.0+)?px)", value.strip()))


def _indent_em(value: str | None, font_size: float | None) -> float | None:
    if value is None:
        return None
    normalized = value.strip()
    if re.fullmatch(r"0+(?:\.0+)?(?:em|px)?", normalized):
        return 0.0
    ems = _number_unit(normalized, "em")
    if ems is not None:
        return ems
    pixels = _number_unit(normalized, "px")
    return pixels / font_size if pixels is not None and font_size else None


def _normalized_contract_variant(value: dict[str, Any]) -> dict[str, Any]:
    stack = value.get("font_stack")
    return {
        "font_stack": (
            [str(item).casefold() for item in stack]
            if isinstance(stack, list)
            else stack
        ),
        "font_size_px": value.get("font_size_px"),
        "line_height": value.get("line_height"),
        "font_weight": value.get("font_weight"),
        "alignment": str(value.get("alignment", "")).casefold(),
        "letter_spacing_px": value.get("letter_spacing_px"),
        "wrap": str(value.get("wrap", "")).casefold(),
    }


def _estimated_text_width(
    value: str, font_size: float, letter_spacing: float
) -> float:
    width = 0.0
    visible_characters = 0
    for character in re.sub(r"\s+", " ", value).strip():
        visible_characters += 1
        codepoint = ord(character)
        if character.isspace():
            factor = 0.33
        elif codepoint >= 0x2E80:
            factor = 1.0
        elif character in "ilI1|!.,:;'`":
            factor = 0.35
        elif character in "mwMW@#%&":
            factor = 0.9
        else:
            factor = 0.58
        width += font_size * factor
    width += max(0, visible_characters - 1) * letter_spacing
    return width


class _Node:
    def __init__(
        self,
        *,
        tag: str,
        line: int,
        style: dict[str, str],
        declared_style: dict[str, str],
        role: str | None,
        explicit_role: str | None,
        indent_role: str | None,
        inside_svg: bool,
    ) -> None:
        self.tag = tag
        self.line = line
        self.style = style
        self.declared_style = declared_style
        self.role = role
        self.explicit_role = explicit_role
        self.indent_role = indent_role
        self.inside_svg = inside_svg
        self.text: list[str] = []
        self.has_break = False


class TypographyParser(HTMLParser):
    def __init__(self, line_offset: int = 0) -> None:
        super().__init__(convert_charrefs=True)
        self.line_offset = line_offset
        self.stack: list[_Node] = []
        self.nodes: list[_Node] = []
        self.missing_role_lines: set[int] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "br":
            for open_node in self.stack:
                open_node.has_break = True
        attributes = dict(attrs)
        declared_style = parse_style(attributes.get("style") or "")
        inherited_style = (
            {
                name: value
                for name, value in self.stack[-1].style.items()
                if name in INHERITED_PROPERTIES
            }
            if self.stack
            else {}
        )
        inherited_style.update(declared_style)
        explicit_role = attributes.get("data-type-role")
        role = explicit_role or (self.stack[-1].role if self.stack else None)
        inside_svg = tag == "svg" or any(node.inside_svg for node in self.stack)
        node = _Node(
            tag=tag,
            line=self.getpos()[0] + self.line_offset,
            style=inherited_style,
            declared_style=declared_style,
            role=role,
            explicit_role=explicit_role,
            indent_role=attributes.get("data-indent-role"),
            inside_svg=inside_svg,
        )
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

    def handle_data(self, data: str) -> None:
        if any(node.tag in {"defs", "desc", "title"} for node in self.stack):
            return
        for node in self.stack:
            node.text.append(data)
        if data.strip() and (
            not self.stack
            or (self.stack[-1].role is None and not self.stack[-1].inside_svg)
        ):
            self.missing_role_lines.add(self.getpos()[0] + self.line_offset)


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
    fragment = remainder.split(END, 1)[0]
    return fragment, prefix.count("\n")


def _add(
    findings: list[dict[str, object]],
    code: str,
    line: int,
    message: str,
    *,
    severity: str = "error",
) -> None:
    findings.append(
        {"code": code, "severity": severity, "line": line, "message": message}
    )


def audit_html(
    value: str,
    contract: dict[str, Any],
    *,
    line_offset: int = 0,
) -> list[dict[str, object]]:
    parser = TypographyParser(line_offset=line_offset)
    parser.feed(value)
    parser.close()
    findings: list[dict[str, object]] = []
    typography = contract["typography"]
    roles: dict[str, Any] = typography["roles"]

    for node in parser.nodes:
        if node.tag not in CONTAINER_TAGS or "text-indent" not in node.declared_style:
            continue
        size = _number_unit(node.style.get("font-size"), "px")
        indent = _indent_em(node.declared_style.get("text-indent"), size)
        if indent is None or abs(indent) > 0.01:
            _add(
                findings,
                "container-indent-not-allowed",
                node.line,
                "Layout containers must declare text-indent:0 or omit the declaration.",
            )

    for line in sorted(parser.missing_role_lines):
        _add(
            findings,
            "missing-type-role",
            line,
            "Visible text must inherit a supported data-type-role.",
        )

    for node in parser.nodes:
        if node.explicit_role is None or node.inside_svg:
            continue
        visible = "".join(node.text)
        if not visible.strip():
            continue
        role = node.explicit_role
        if role not in roles:
            _add(
                findings,
                "unknown-type-role",
                node.line,
                f"data-type-role={role!r} is absent from the design contract.",
            )
            continue
        planned = roles[role]
        style = node.style
        actual_size = _number_unit(style.get("font-size"), "px")
        actual_leading = _line_height(style.get("line-height"), actual_size)
        actual_weight = _font_weight(style.get("font-weight"))
        actual_tracking = (
            0.0
            if _zero_px(style.get("letter-spacing"))
            else _number_unit(style.get("letter-spacing"), "px")
        )

        actual_variant = {
            "font_stack": _font_stack(style.get("font-family")),
            "font_size_px": actual_size,
            "line_height": actual_leading,
            "font_weight": actual_weight,
            "alignment": (style.get("text-align") or "").lower(),
            "letter_spacing_px": actual_tracking,
            "wrap": next(
                (
                    f"{name}:{style[name]}".casefold()
                    for name in ("overflow-wrap", "word-break", "white-space")
                    if style.get(name)
                ),
                None,
            ),
        }
        planned_variants = planned.get("variants")
        if not isinstance(planned_variants, list) or not planned_variants:
            planned_variants = [
                {key: value for key, value in planned.items() if key != "variants"}
            ]
        normalized_variants = [
            _normalized_contract_variant(item)
            for item in planned_variants
            if isinstance(item, dict)
        ]
        if actual_variant not in normalized_variants:
            _add(
                findings,
                "typography-variant-contract-mismatch",
                node.line,
                f"Role {role} does not match any machine-recorded typography variant.",
            )

        if role in SINGLE_LINE_HEADING_ROLES and actual_size is not None:
            estimated_width = _estimated_text_width(
                visible,
                actual_size,
                actual_tracking if actual_tracking is not None else 0.0,
            )
            if node.has_break:
                _add(
                    findings,
                    "heading-forced-line-break",
                    node.line,
                    f"Role {role} contains an explicit line break. Review the final "
                    "composition at 320px; a balanced two-line heading is valid when it "
                    "preserves voice, meaning, and visual rhythm.",
                    severity="warning",
                )
            elif estimated_width > SINGLE_LINE_HEADING_BUDGET_PX:
                _add(
                    findings,
                    "heading-wrap-risk",
                    node.line,
                    f"Role {role} is estimated at {estimated_width:.0f}px against a "
                    f"{SINGLE_LINE_HEADING_BUDGET_PX:.0f}px mobile heading budget. "
                    "Review its wording, type, usable width, and line balance in the final "
                    "composition; avoid nowrap overflow.",
                    severity="warning",
                )

        is_body_paragraph = node.indent_role == "body-paragraph"
        if node.indent_role is not None and not is_body_paragraph:
            _add(
                findings,
                "unknown-indent-role",
                node.line,
                "data-indent-role supports only 'body-paragraph'.",
            )
        if is_body_paragraph and (node.tag != "p" or role != "body"):
            _add(
                findings,
                "invalid-body-paragraph-indent",
                node.line,
                "data-indent-role='body-paragraph' requires a p with data-type-role='body'.",
            )
        expected_indent = (
            float(typography["body_first_line_indent_em"])
            if is_body_paragraph and node.tag == "p" and role == "body"
            else 0.0
        )
        actual_indent = _indent_em(style.get("text-indent"), actual_size)
        if actual_indent is None or abs(actual_indent - expected_indent) > 0.01:
            _add(
                findings,
                "first-line-indent-contract-mismatch",
                node.line,
                f"Role {role} requires text-indent:{expected_indent:g}em; found {style.get('text-indent')!r}.",
            )

        leading_ascii = bool(re.match(r" {2,}", visible)) and not visible.startswith(
            ("\r", "\n", "\t")
        )
        leading_content = visible.lstrip(" \t\r\n")
        if leading_ascii or MANUAL_INDENT_SPACE.match(leading_content):
            _add(
                findings,
                "manual-space-indentation",
                node.line,
                "Use CSS text-indent; do not simulate indentation with ASCII, Unicode, or nonbreaking spaces.",
            )

    return findings


def audit(path: Path, contract_path: Path) -> dict[str, object]:
    contract = load_contract(contract_path)
    validate_contract(contract, required_status="READY")
    value, line_offset = _article_html(path)
    findings = audit_html(value, contract, line_offset=line_offset)
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
    parser = argparse.ArgumentParser(
        description="Validate WeChat typography against design-contract.json"
    )
    parser.add_argument("article", type=Path, help="HTML fragment or article JSON")
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
