#!/usr/bin/env python3
"""Detect source-instruction and work-process residue in publishable copy."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

PATTERNS = (
    (
        "instruction_echo_zh",
        re.compile(
            r"(?:\u6309|\u6309\u7167|\u6839\u636e)"
            r"(?:\u4f60|\u7528\u6237)(?:\u7684)?"
            r"(?:\u8981\u6c42|\u53cd\u9988|\u610f\u89c1)"
        ),
    ),
    (
        "source_history_zh",
        re.compile(
            r"(?:\u8fd9|\u672c|\u4e0a|\u4e0a\u4e00|\u521a\u624d)"
            r"(?:\u4e00)?(?:\u8f6e|\u6b21)?"
            r"(?:\u5bf9\u8bdd|\u804a\u5929)"
            r"|(?:\u4f60|\u6211\u4eec)\u521a\u624d"
            r"(?:\u8bf4|\u63d0\u5230|\u8ba8\u8bba)"
        ),
    ),
    (
        "workflow_narration_zh",
        re.compile(
            r"(?:\u6211|\u6211\u4eec)"
            r"(?:\u5df2\u7ecf|\u5df2|\u4f1a|\u5c06|\u6b63\u5728)"
            r"(?:\u4e3a\u4f60|\u66ff\u4f60)?"
            r"(?:\u4fee\u6539|\u751f\u6210|\u521b\u5efa|\u4e0a\u4f20|"
            r"\u68c0\u67e5|\u5904\u7406|\u7ee7\u7eed|\u5b8c\u6210)"
        ),
    ),
    (
        "action_request_zh",
        re.compile(
            r"(?:\u8bf7|\u53ef\u4ee5)?\u56de\u590d[\uff1a:]"
            r"|\u4f60(?:\u56de\u590d|\u786e\u8ba4)\u540e"
            r"|\u7b49\u5f85\u4f60(?:\u56de\u590d|\u786e\u8ba4)"
        ),
    ),
    (
        "private_context_zh",
        re.compile(
            r"(?:\u5f53\u524d|\u672c\u6b21)"
            r"(?:\u4efb\u52a1|\u5de5\u4f5c\u533a|\u4f1a\u8bdd|\u8fd0\u884c)"
            r"|(?:\u672c\u5730|\u5de5\u4f5c\u533a)"
            r"(?:\u6587\u4ef6|\u8def\u5f84)"
            r"|[A-Za-z]:\\"
        ),
    ),
    (
        "instruction_echo_en",
        re.compile(r"\b(?:as|per) \x79\x6f\x75 requested\b", re.IGNORECASE),
    ),
    (
        "source_history_en",
        re.compile(
            r"\b(?:in this \x63\x68\x61\x74|"
            r"earlier in \x6f\x75\x72 "
            r"\x63\x6f\x6e\x76\x65\x72\x73\x61\x74\x69\x6f\x6e)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "workflow_narration_en",
        re.compile(
            r"\b\x49 (?:have|will|am going to) "
            r"(?:generated|created|uploaded|updated|checked)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "action_request_en",
        re.compile(r"\b(?:reply with|once \x79\x6f\x75 confirm)\b", re.IGNORECASE),
    ),
)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _html_text(value: str) -> str:
    parser = _TextExtractor()
    parser.feed(value)
    parser.close()
    return " ".join(parser.parts)


def _article_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() != ".json":
        return _html_text(raw) if "<" in raw and ">" in raw else raw

    payload: Any = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("article JSON must contain an object")
    fields = []
    for name in ("title", "author", "digest"):
        value = payload.get(name)
        if isinstance(value, str):
            fields.append(value)
    content = payload.get("content")
    if isinstance(content, str):
        fields.append(_html_text(content))
    return " ".join(fields)


def audit_text(value: str) -> list[dict[str, str]]:
    normalized = re.sub(r"\s+", " ", value).strip()
    findings: list[dict[str, str]] = []
    for rule, pattern in PATTERNS:
        for match in pattern.finditer(normalized):
            start = max(0, match.start() - 28)
            end = min(len(normalized), match.end() + 28)
            findings.append(
                {
                    "rule": rule,
                    "match": match.group(0),
                    "context": normalized[start:end],
                }
            )
    return findings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect source-instruction residue in audience-facing article copy"
    )
    parser.add_argument("article", help="HTML, text, or article JSON path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    path = Path(args.article).expanduser()
    try:
        if not path.is_file():
            raise ValueError(f"article file does not exist: {args.article}")
        findings = audit_text(_article_text(path))
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
