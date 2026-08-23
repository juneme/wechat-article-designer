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


class _Node:
    def __init__(
        self,
        *,
        tag: str,
        line: int,
        style: dict[str, str],
        role: str | None,
        explicit_role: str | None,
    ) -> None:
        self.tag = tag
        self.line = line
        self.style = style
        self.role = role
        self.explicit_role = explicit_role
        self.text: list[str] = []


class TypographyParser(HTMLParser):
    def __init__(self, line_offset: int = 0) -> None:
        super().__init__(convert_charrefs=True)
        self.line_offset = line_offset
        self.stack: list[_Node] = []
        self.nodes: list[_Node] = []
        self.missing_role_lines: set[int] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        inherited_style = (
            {
                name: value
                for name, value in self.stack[-1].style.items()
                if name in INHERITED_PROPERTIES
            }
            if self.stack
            else {}
        )
        inherited_style.update(parse_style(attributes.get("style") or ""))
        explicit_role = attributes.get("data-type-role")
        role = explicit_role or (self.stack[-1].role if self.stack else None)
        node = _Node(
            tag=tag,
            line=self.getpos()[0] + self.line_offset,
            style=inherited_style,
            role=role,
            explicit_role=explicit_role,
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
        if data.strip() and (not self.stack or self.stack[-1].role is None):
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
) -> None:
    findings.append(
        {"code": code, "severity": "error", "line": line, "message": message}
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

    for line in sorted(parser.missing_role_lines):
        _add(
            findings,
            "missing-type-role",
            line,
            "Visible text must inherit a supported data-type-role.",
        )

    for node in parser.nodes:
        if node.explicit_role is None:
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
        planned_size = float(planned["font_size_px"])
        if actual_size is None or abs(actual_size - planned_size) > 0.01:
            _add(
                findings,
                "font-size-contract-mismatch",
                node.line,
                f"Role {role} requires {planned_size:g}px; found {style.get('font-size')!r}.",
            )

        actual_leading = _line_height(style.get("line-height"), actual_size)
        planned_leading = float(planned["line_height"])
        if actual_leading is None or abs(actual_leading - planned_leading) > 0.01:
            _add(
                findings,
                "line-height-contract-mismatch",
                node.line,
                f"Role {role} requires {planned_leading:g}; found {style.get('line-height')!r}.",
            )

        actual_weight = _font_weight(style.get("font-weight"))
        if actual_weight != planned["font_weight"]:
            _add(
                findings,
                "font-weight-contract-mismatch",
                node.line,
                f"Role {role} requires weight {planned['font_weight']}; found {style.get('font-weight')!r}.",
            )

        if (style.get("text-align") or "").lower() != planned["alignment"]:
            _add(
                findings,
                "alignment-contract-mismatch",
                node.line,
                f"Role {role} requires {planned['alignment']} alignment; found {style.get('text-align')!r}.",
            )

        if not _zero_px(style.get("letter-spacing")):
            _add(
                findings,
                "letter-spacing-contract-mismatch",
                node.line,
                f"Role {role} requires zero letter spacing; found {style.get('letter-spacing')!r}.",
            )

        planned_stack = [str(item).casefold() for item in planned["font_stack"]]
        if _font_stack(style.get("font-family")) != planned_stack:
            _add(
                findings,
                "font-stack-contract-mismatch",
                node.line,
                f"Role {role} font-family does not match its contract font_stack.",
            )

        wrap = str(planned["wrap"])
        property_name, expected = wrap.split(":", 1)
        if style.get(property_name.strip().lower(), "").lower() != expected.strip().lower():
            _add(
                findings,
                "wrap-contract-mismatch",
                node.line,
                f"Role {role} requires {wrap}; implementation differs.",
            )

        expected_indent = (
            float(typography["body_first_line_indent_em"]) if role == "body" else 0.0
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
        if leading_ascii or leading_content.startswith(("\u3000", "\u00a0")):
            _add(
                findings,
                "manual-space-indentation",
                node.line,
                "Use CSS text-indent; do not simulate indentation with spaces or NBSP.",
            )

    return findings


def audit(path: Path, contract_path: Path) -> dict[str, object]:
    contract = load_contract(contract_path)
    validate_contract(contract, required_status="READY")
    value, line_offset = _article_html(path)
    findings = audit_html(value, contract, line_offset=line_offset)
    return {
        "ok": not findings,
        "article": path.name,
        "contract": contract_path.name,
        "error_count": len(findings),
        "warning_count": 0,
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
