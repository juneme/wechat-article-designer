#!/usr/bin/env python3
"""Detect agent-workflow language and private residue in article workspaces."""

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
        "instruction-echo",
        re.compile(
            r"(?:按|按照|根据)(?:你|用户)(?:的)?(?:要求|反馈|意见)"
            r"|(?:as|per) you requested",
            re.IGNORECASE,
        ),
    ),
    (
        "conversation-history",
        re.compile(
            r"(?:这|本|上|上一|刚才)(?:一)?(?:轮|次)?(?:对话|聊天)"
            r"|(?:你|我们)刚才(?:说|提到|讨论)"
            r"|\b(?:in this chat|earlier in our conversation)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "workflow-narration",
        re.compile(
            r"(?:我|我们)(?:已经|已|会|将|正在|可以)(?:为你|替你)?"
            r"(?:修改|生成|创建|上传|检查|处理|继续|完成|优化|排版)"
            r"|(?:已|已经)(?:为你)?(?:生成|创建|上传|修改|完成|优化)"
            r"|\bI (?:have|will|can|am going to) "
            r"(?:generate|create|upload|update|check|continue|revise)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "agent-offer",
        re.compile(
            r"如果你(?:希望|需要|愿意)"
            r"|如需我(?:继续|修改|调整)"
            r"|我可以(?:继续|再|为你)"
            r"|\bif you(?: would like| want| need),? I can\b",
            re.IGNORECASE,
        ),
    ),
    (
        "reply-request",
        re.compile(
            r"请(?:告诉我|回复|确认|选择)"
            r"|你(?:回复|确认)后"
            r"|等待你(?:回复|确认)"
            r"|\b(?:reply with|tell me|once you confirm)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "private-context",
        re.compile(
            r"(?:当前|本次)(?:任务|工作区|会话|运行)"
            r"|(?:本地|工作区)(?:文件|路径)"
            r"|[A-Za-z]:\\(?:Users|Documents)\\"
            r"|/Users/[^/]+/",
            re.IGNORECASE,
        ),
    ),
)

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


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.context: list[tuple[str, bool]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        inherited = self.context[-1][1] if self.context else False
        suppressed = inherited or attributes.get("data-content-kind") in {
            "dialogue",
            "quotation",
        }
        if tag not in VOID_TAGS:
            self.context.append((tag, suppressed))

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.context) - 1, -1, -1):
            if self.context[index][0] == tag:
                del self.context[index:]
                break

    def handle_data(self, data: str) -> None:
        if not self.context or not self.context[-1][1]:
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


def audit_text(
    value: str,
) -> list[dict[str, str | bool]]:
    normalized = re.sub(r"\s+", " ", value).strip()
    findings: list[dict[str, str | bool]] = []
    for code, pattern in PATTERNS:
        for match in pattern.finditer(normalized):
            start = max(0, match.start() - 28)
            end = min(len(normalized), match.end() + 28)
            finding: dict[str, str | bool] = {
                "code": code,
                "severity": "error",
                "match": match.group(0),
                "context": normalized[start:end],
            }
            findings.append(finding)
    return findings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect agent-workflow residue in article copy and workspace HTML"
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
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ValueError,
    ) as exc:
        print(
            json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 1

    errors = [item for item in findings if item["severity"] == "error"]
    print(
        json.dumps(
            {
                "ok": not errors,
                "article": path.name,
                "error_count": len(errors),
                "warning_count": len(findings) - len(errors),
                "findings": findings,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
