#!/usr/bin/env python3
"""Audit the skill release root for caches, local residue, and unsafe metadata."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

CACHE_DIRS = {".mypy_cache", ".pytest_cache", ".ruff_cache", "__pycache__"}
CACHE_FILES = {".coverage"}
CACHE_SUFFIXES = {".pyc", ".pyo"}
WORK_DIRS = {
    "articles",
    "experiments",
    "outputs",
    "scratch",
    "temp",
    "tests",
    "tmp",
    "work",
}
ARTICLE_ARTIFACTS = {
    "article.json",
    "design-contract.json",
    "design-contract.md",
    "design-report.json",
    "design-report.md",
    "fragment.html",
    "manifest.json",
    "preview.html",
    "release-manifest.json",
}
TRANSCRIPT_NAMES = re.compile(
    r"(?:^|[-_])(?:chat|conversation|transcript|对话|聊天)(?:[-_]|$)",
    re.IGNORECASE,
)
TRANSCRIPT_CONTENT = re.compile(
    r"^\s*(?:user|assistant|system|developer|用户|助手|系统|开发者)\s*[:：]",
    re.IGNORECASE,
)
TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".json",
    ".md",
    ".py",
    ".svg",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
LOCAL_PATH = re.compile(
    r"(?:[A-Za-z]:[\\/](?:Users|Documents)[\\/]|/(?:Users|home)/[A-Za-z0-9._-]+/)",
    re.IGNORECASE,
)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~-]{24,}\b", re.IGNORECASE),
)
PROMPT_PHRASES = re.compile(
    r"\b(?:if you want|if you would like|let me know|I can continue)\b"
    r"|如果你(?:希望|需要|愿意)|请告诉我|我可以(?:继续|再|为你)|等待你(?:回复|确认)",
    re.IGNORECASE,
)


def _inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root)
    except ValueError:
        return False
    return path.resolve() != root


def clean_caches(root: Path) -> list[str]:
    root = root.resolve()
    removed: list[str] = []
    candidates = sorted(
        (
            path
            for path in root.rglob("*")
            if path.name in CACHE_DIRS
            or path.name in CACHE_FILES
            or path.suffix.lower() in CACHE_SUFFIXES
        ),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for path in candidates:
        if not path.exists() or not _inside(root, path):
            continue
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        removed.append(relative)
    return sorted(set(removed))


def audit_root(root: Path) -> list[dict[str, object]]:
    root = root.resolve()
    findings: list[dict[str, object]] = []

    def add(code: str, path: Path, message: str, line: int | None = None) -> None:
        finding: dict[str, object] = {
            "code": code,
            "path": path.relative_to(root).as_posix(),
            "message": message,
        }
        if line is not None:
            finding["line"] = line
        findings.append(finding)

    for path in sorted(root.rglob("*")):
        if path.name in CACHE_DIRS or path.name in CACHE_FILES or path.suffix.lower() in CACHE_SUFFIXES:
            add("release-cache", path, "Cache or compiled output is present in the release root.")
            continue
        if path.is_dir():
            if path.name.lower() in WORK_DIRS:
                add(
                    "work-data",
                    path,
                    "Development-test, working, experimental, or generated-output directory is not releasable.",
                )
            continue
        if path.name in ARTICLE_ARTIFACTS:
            add("article-artifact", path, "Generated article workspace data is not releasable.")
        if TRANSCRIPT_NAMES.search(path.stem):
            add("conversation-artifact", path, "Conversation or transcript artifacts are not releasable.")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            value = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            add("text-read-error", path, f"Cannot read text release file: {exc}")
            continue
        inspect_transcript_content = path.name != "README.md"
        for line_number, line in enumerate(value.splitlines(), start=1):
            if LOCAL_PATH.search(line):
                add("local-absolute-path", path, "Local absolute path is embedded in a release file.", line_number)
            if any(pattern.search(line) for pattern in SECRET_PATTERNS):
                add("possible-secret", path, "Possible credential or private key material is embedded.", line_number)
            if inspect_transcript_content and TRANSCRIPT_CONTENT.search(line):
                add(
                    "conversation-content",
                    path,
                    "Conversation-role content is embedded in a release file.",
                    line_number,
                )

    metadata = root / "agents" / "openai.yaml"
    if not metadata.is_file():
        add("missing-agent-metadata", root / "agents", "agents/openai.yaml is required.")
    else:
        value = metadata.read_text(encoding="utf-8")
        required = (
            "$wechat-article-designer",
            "three console variables",
            "healthy",
            "create a new draft",
            "local preview",
        )
        if any(item not in value for item in required):
            add(
                "nondeterministic-default-prompt",
                metadata,
                "Default prompt must encode the configured draft-or-preview route.",
            )
        if PROMPT_PHRASES.search(value):
            add(
                "conversational-default-prompt",
                metadata,
                "Default prompt contains conversational agent-offer language.",
            )
    return findings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit skill release hygiene")
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="remove only recognized cache directories and compiled cache files",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(json.dumps({"ok": False, "error": f"root does not exist: {root}"}), file=sys.stderr)
        return 1
    removed = clean_caches(root) if args.clean else []
    findings = audit_root(root)
    result = {
        "ok": not findings,
        "root": str(root),
        "removed_caches": removed,
        "finding_count": len(findings),
        "findings": findings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
