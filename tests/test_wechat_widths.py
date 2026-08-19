from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "audit_wechat_widths.py"
SAFE_FIXTURE = Path(__file__).parent / "fixtures" / "safe_swipe.html"


def _load_auditor() -> ModuleType:
    spec = importlib.util.spec_from_file_location("audit_wechat_widths", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_oversized_clipped_swipe_is_rejected() -> None:
    auditor = _load_auditor()
    html = """
    <section style="overflow:hidden">
      <section style="overflow-x:auto;white-space:nowrap">
        <section style="width:900%">
          <section style="display:inline-block;width:10%">item</section>
        </section>
      </section>
    </section>
    """

    assert {finding["rule"] for finding in auditor.audit_html(html)} == {
        "oversized_percentage_width",
        "swipe_items_not_direct_inline_blocks",
        "swipe_inside_clipping_ancestor",
    }


def test_direct_child_swipe_passes() -> None:
    auditor = _load_auditor()
    html = """
    <section style="overflow-x:auto;overflow-y:hidden;white-space:nowrap;font-size:0">
      <section style="display:inline-block;width:88%;white-space:normal">one</section>
      <section style="display:inline-block;width:88%;white-space:normal">two</section>
    </section>
    """

    assert auditor.audit_html(html) == []


def test_responsive_safe_swipe_fixture_passes() -> None:
    auditor = _load_auditor()

    assert auditor.audit_html(SAFE_FIXTURE.read_text(encoding="utf-8")) == []


def test_cli_reports_article_name(tmp_path: Path, capsys) -> None:
    auditor = _load_auditor()
    article = tmp_path / "article.html"
    article.write_text('<section style="width:360%"></section>', encoding="utf-8")

    assert auditor.main([str(article)]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["article"] == "article.html"
    assert result["findings"][0]["rule"] == "oversized_percentage_width"


def test_important_oversized_width_is_rejected() -> None:
    auditor = _load_auditor()
    html = '<section style="width:360% !important"></section>'

    assert auditor.audit_html(html)[0]["rule"] == "oversized_percentage_width"
