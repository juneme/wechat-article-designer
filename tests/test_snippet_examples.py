from __future__ import annotations

import re
import unittest
from pathlib import Path

from scripts.audit_wechat_widths import audit_html

HTML_FENCE = re.compile(r"```html\s*(.*?)```", re.DOTALL)
PROHIBITED = (
    "<script",
    "<style",
    "<svg",
    "<table",
    "position:absolute",
    "position:relative",
    "display:grid",
    "display:flex",
)


class SnippetExamplesTests(unittest.TestCase):
    def test_documented_html_primitives_keep_baseline_structure(self) -> None:
        reference = (
            Path(__file__).resolve().parents[1] / "references" / "snippets.md"
        ).read_text(encoding="utf-8")
        examples = HTML_FENCE.findall(reference)
        self.assertGreaterEqual(len(examples), 10)
        for example in examples:
            normalized = example.lower().replace(" ", "")
            for token in PROHIBITED:
                self.assertNotIn(token, normalized, token)
            self.assertEqual(audit_html(example), [])


if __name__ == "__main__":
    unittest.main()
