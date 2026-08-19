#!/usr/bin/env python3
"""Detect width structures that can collapse after WeChat editor rewrites."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

PERCENTAGE = re.compile(r"^([0-9]+(?:\.[0-9]+)?)%$")


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
        line: int,
        parent: _Node | None,
    ) -> None:
        self.tag = tag
        self.style = style
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
            line=self.getpos()[0],
            parent=parent,
        )
        if parent is not None:
            parent.children.append(node)
        self.nodes.append(node)
        if tag not in {"area", "base", "br", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}:
            self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break


def _percentage(value: str | None) -> float | None:
    if value is None:
        return None
    normalized = re.sub(r"\s*!important\s*$", "", value, flags=re.IGNORECASE)
    match = PERCENTAGE.fullmatch(normalized.strip())
    return float(match.group(1)) if match else None


def audit_html(value: str) -> list[dict[str, Any]]:
    parser = _TreeParser()
    parser.feed(value)
    parser.close()
    findings: list[dict[str, Any]] = []

    for node in parser.nodes:
        width = _percentage(node.style.get("width"))
        if width is not None and width > 100:
            findings.append(
                {
                    "rule": "oversized_percentage_width",
                    "line": node.line,
                    "value": node.style["width"],
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
                    "rule": "swipe_items_not_direct_inline_blocks",
                    "line": node.line,
                    "child_lines": [child.line for child in non_card_children],
                }
            )

        ancestor = node.parent
        while ancestor is not None:
            if ancestor.style.get("overflow") == "hidden" or ancestor.style.get(
                "overflow-x"
            ) == "hidden":
                findings.append(
                    {
                        "rule": "swipe_inside_clipping_ancestor",
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
        description="Detect WeChat width and swipe structures that can collapse"
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
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(
            json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 1

    print(
        json.dumps(
            {
                "ok": not findings,
                "article": path.name,
                "finding_count": len(findings),
                "findings": findings,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not findings else 2


if __name__ == "__main__":
    raise SystemExit(main())
