#!/usr/bin/env python3
"""Detect likely chat or work-process residue in publishable article copy."""

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
        "request_echo_zh",
        re.compile(r"(?:按|按照|根据)(?:你|用户)(?:的)?(?:要求|反馈|意见)"),
    ),
    (
        "chat_history_zh",
        re.compile(
            r"(?:这|本|上|上一|刚才)(?:一)?(?:轮|次)?(?:对话|聊天)"
            r"|(?:你|我们)刚才(?:说|提到|讨论)"
        ),
    ),
    (
        "assistant_process_zh",
        re.compile(
            r"(?:我|我们)(?:已经|已|会|将|正在)(?:为你|替你)?"
            r"(?:修改|生成|创建|上传|检查|处理|继续|完成)"
        ),
    ),
    (
        "handoff_prompt_zh",
        re.compile(r"(?:请|可以)?回复[：:]|你(?:回复|确认)后|等待你(?:回复|确认)"),
    ),
    (
        "private_context_zh",
        re.compile(
            r"(?:当前|本次)(?:任务|工作区|会话|运行)"
            r"|(?:本地|工作区)(?:文件|路径)"
            r"|[A-Za-z]:\\"
        ),
    ),
    (
        "request_echo_en",
        re.compile(r"\b(?:as|per) you requested\b", re.IGNORECASE),
    ),
    (
        "chat_history_en",
        re.compile(r"\b(?:in this chat|earlier in our conversation)\b", re.IGNORECASE),
    ),
    (
        "assistant_process_en",
        re.compile(
            r"\bI (?:have|will|am going to) (?:generated|created|uploaded|updated|checked)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "handoff_prompt_en",
        re.compile(r"\b(?:reply with|once you confirm)\b", re.IGNORECASE),
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
        description="Detect chat residue in audience-facing article copy"
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
                "article": str(path.resolve()),
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
