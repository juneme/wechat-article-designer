from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "audit_audience_boundary.py"


def _load_auditor() -> ModuleType:
    spec = importlib.util.spec_from_file_location("audit_audience_boundary", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_audience_facing_copy_passes() -> None:
    auditor = _load_auditor()

    assert auditor.audit_text("完成配置后，系统会自动校验文章并写入草稿箱。") == []


def test_conversation_residue_is_reported() -> None:
    auditor = _load_auditor()
    findings = auditor.audit_text(
        "根据你的要求，我已经为你生成文章。请回复：确认后继续。"
    )

    assert {finding["rule"] for finding in findings} == {
        "request_echo_zh",
        "assistant_process_zh",
        "handoff_prompt_zh",
    }


def test_live_prompt_example_does_not_trigger_without_chat_narration() -> None:
    auditor = _load_auditor()

    assert auditor.audit_text("示例指令：围绕低碳出行设计一篇公众号文章。") == []
