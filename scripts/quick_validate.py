#!/usr/bin/env python3
"""Run the portable structural checks required for this skill package."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ALLOWED_FRONTMATTER = {"allowed-tools", "description", "license", "metadata", "name"}
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_skill(root: Path) -> tuple[bool, str]:
    skill_file = root / "SKILL.md"
    if not skill_file.is_file():
        return False, "SKILL.md not found"
    value = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---", value, re.DOTALL)
    if not match:
        return False, "Invalid or missing YAML frontmatter"
    try:
        frontmatter: Any = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return False, f"Invalid YAML frontmatter: {exc}"
    if not isinstance(frontmatter, dict):
        return False, "Frontmatter must be a mapping"
    unknown = set(frontmatter) - ALLOWED_FRONTMATTER
    if unknown:
        return False, f"Unexpected frontmatter keys: {', '.join(sorted(unknown))}"
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not isinstance(name, str) or not NAME.fullmatch(name) or len(name) > 64:
        return False, "Skill name must be lowercase hyphen-case and at most 64 characters"
    if not isinstance(description, str) or not description.strip():
        return False, "Skill description must be a non-empty string"
    if len(description) > 1024 or "<" in description or ">" in description:
        return False, "Skill description contains an invalid length or angle bracket"
    body = value[match.end() :]
    if re.search(r"(?m)^[ ]{0,3}\[TODO:[^\n]*\][ \t]*$", body):
        return False, "Skill instructions contain an unfinished TODO placeholder"
    metadata = root / "agents" / "openai.yaml"
    if not metadata.is_file():
        return False, "agents/openai.yaml not found"
    try:
        agent: Any = yaml.safe_load(metadata.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return False, f"Invalid agents/openai.yaml: {exc}"
    prompt = agent.get("interface", {}).get("default_prompt") if isinstance(agent, dict) else None
    if not isinstance(prompt, str) or "$wechat-article-designer" not in prompt:
        return False, "default_prompt must mention $wechat-article-designer"
    return True, "Skill is valid"


def main(argv: list[str] | None = None) -> int:
    values = sys.argv[1:] if argv is None else argv
    if len(values) != 1:
        print("Usage: python scripts/quick_validate.py <skill-directory>", file=sys.stderr)
        return 1
    valid, message = validate_skill(Path(values[0]).expanduser().resolve())
    print(message)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
