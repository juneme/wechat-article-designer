from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "audit_audience_boundary.py"


def _load_auditor() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "audit_audience_boundary", SCRIPT_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_audience_facing_copy_passes() -> None:
    auditor = _load_auditor()

    assert auditor.audit_text("完成配置后，系统会自动校验文章并写入草稿箱。") == []


def test_source_residue_is_reported() -> None:
    auditor = _load_auditor()
    findings = auditor.audit_text(
        "\u6839\u636e\u4f60\u7684\u8981\u6c42\uff0c"
        "\u6211\u5df2\u7ecf\u4e3a\u4f60\u751f\u6210\u6587\u7ae0\u3002"
        "\u8bf7\u56de\u590d\uff1a\u786e\u8ba4\u540e\u7ee7\u7eed\u3002"
    )

    assert {finding["rule"] for finding in findings} == {
        "instruction_echo_zh",
        "workflow_narration_zh",
        "action_request_zh",
    }


def test_generic_instruction_example_passes() -> None:
    auditor = _load_auditor()

    assert auditor.audit_text("示例指令：围绕低碳出行设计一篇公众号文章。") == []


def test_cli_result_omits_local_path(tmp_path: Path, capsys) -> None:
    auditor = _load_auditor()
    article = tmp_path / "article.html"
    article.write_text("<section>公开内容</section>", encoding="utf-8")

    assert auditor.main([str(article)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["article"] == "article.html"
