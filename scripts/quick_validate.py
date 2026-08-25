#!/usr/bin/env python3
"""Run the portable structural checks required for this skill package."""

from __future__ import annotations

import re
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

import article_workspace
import audit_audience_boundary
import audit_wechat_contrast
import audit_wechat_markup
import audit_wechat_typography
import audit_wechat_widths
import release_article
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


def _regression_checks() -> list[str]:
    failures: list[str] = []
    valid = """<!-- 微信公众号复制开始 -->
<section style="margin:0;padding:0;background:#F8F4EA;color:#24211D;">
  <h1 style="margin:0;font-size:28px;line-height:1.2;text-indent:0;">风从纸上经过</h1>
  <svg viewBox="0 0 360 80" width="100%" height="auto" role="img"><title>风</title><desc>流动的线</desc><path d="M10 40 H350" stroke="#477A72"><animate attributeName="stroke-dashoffset" values="0;20" dur="4s" repeatCount="indefinite"/></path></svg>
  <p data-indent-role="body-paragraph" style="margin:0;color:#24211D;font-size:16px;line-height:1.9;text-indent:2em;">这是一段用于验证自由构图流程的连续正文，它没有文字角色、模块、密度、间距、几何或色板标记。</p>
</section>
<!-- 微信公众号复制结束 -->"""
    checks = {
        "marker-free markup": audit_wechat_markup.audit_html(valid),
        "marker-free width": audit_wechat_widths.audit_html(valid),
        "marker-free typography": audit_wechat_typography.audit_html(valid),
        "marker-free contrast": audit_wechat_contrast.audit_html(valid),
        "marker-free audience": audit_audience_boundary.audit_text(valid),
    }
    for label, findings in checks.items():
        if any(item.get("severity") == "error" for item in findings):
            failures.append(f"{label} unexpectedly failed: {findings}")

    negative_cases = {
        "script gate": any(
            item.get("severity") == "error"
            for item in audit_wechat_markup.audit_html(
                valid.replace("</section>", "<script>alert(1)</script></section>", 1)
            )
        ),
        "width gate": any(
            item.get("severity") == "error"
            for item in audit_wechat_widths.audit_html(
                '<section style="width:321px;">x</section>'
            )
        ),
        "indent gate": any(
            item.get("severity") == "error"
            for item in audit_wechat_typography.audit_html(
                '<p data-indent-role="body-paragraph" '
                'style="font-size:16px;line-height:1.9;text-indent:4em;">'
                "这是一段错误缩进的连续正文，需要被机器阻止交付。</p>"
            )
        ),
        "contrast gate": any(
            item.get("severity") == "error"
            for item in audit_wechat_contrast.audit_html(
                '<p style="color:#777777;background:#888888;font-size:16px;">'
                "不可读文字</p>"
            )
        ),
        "workflow-language gate": bool(
            audit_audience_boundary.audit_text("如果你希望，我可以继续为你调整排版。")
        ),
    }
    for label, passed in negative_cases.items():
        if not passed:
            failures.append(f"{label} did not block the regression fixture")
    if "audit_design_contract.py" in release_article.AUDITS:
        failures.append("legacy design-contract audit is active in the v4 release path")

    with tempfile.TemporaryDirectory(prefix="wechat-v4-regression-") as temporary:
        created = article_workspace.create_workspace(
            Path(temporary),
            "自由构图回归",
            date(2026, 8, 25),
            local_preview=False,
        )
        workspace = Path(created["article_dir"])
        (workspace / "fragment.html").write_text(valid, encoding="utf-8")
        first = article_workspace.sync_workspace(workspace)
        first_request = str(first["request_id"])
        second = article_workspace.sync_workspace(workspace)
        if second["changed"] or second["request_id"] != first_request:
            failures.append("idempotent sync changed state or request_id")
        manifest = article_workspace._read_json(workspace / "manifest.json")
        manifest["local_preview_enabled"] = True
        article_workspace._atomic_write_bytes(
            workspace / "manifest.json", article_workspace._json_bytes(manifest)
        )
        preview_sync = article_workspace.sync_workspace(workspace)
        if not (workspace / "preview.html").is_file() or (
            preview_sync["request_id"] != first_request
        ):
            failures.append("preview route did not create preview without rotating request_id")
        manifest = article_workspace._read_json(workspace / "manifest.json")
        manifest["local_preview_enabled"] = False
        article_workspace._atomic_write_bytes(
            workspace / "manifest.json", article_workspace._json_bytes(manifest)
        )
        article_workspace.sync_workspace(workspace)
        if (workspace / "preview.html").exists():
            failures.append("direct route left preview.html behind")
        article_workspace.update_runtime_manifest(
            workspace,
            draft_submission={
                "state": "ambiguous",
                "request_id": first_request,
                "reason": "regression fixture",
            },
        )
        try:
            article_workspace.sync_workspace(workspace)
        except article_workspace.WorkspaceError:
            pass
        else:
            failures.append("ambiguous draft state did not lock synchronization")
    return failures


def main(argv: list[str] | None = None) -> int:
    values = sys.argv[1:] if argv is None else argv
    if len(values) != 1:
        print("Usage: python scripts/quick_validate.py <skill-directory>", file=sys.stderr)
        return 1
    valid, message = validate_skill(Path(values[0]).expanduser().resolve())
    if valid:
        failures = _regression_checks()
        if failures:
            print("\n".join(failures), file=sys.stderr)
            return 1
    print(message)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
