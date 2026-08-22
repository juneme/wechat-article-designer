from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from scripts.article_workspace import END, START, create_workspace, sync_workspace


class ArticleWorkspaceTests(unittest.TestCase):
    def test_create_uses_safe_unique_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = create_workspace(root, "Sample: Draft / One?", date(2030, 1, 2))
            second = create_workspace(root, "Sample: Draft / One?", date(2030, 1, 2))

            first_path = Path(first["article_dir"])
            second_path = Path(second["article_dir"])
            self.assertEqual(first_path.name, "2030-01-02_Sample_Draft_One")
            self.assertEqual(second_path.name, "2030-01-02_Sample_Draft_One_2")
            self.assertTrue((first_path / "assets").is_dir())
            self.assertTrue((first_path / "revisions").is_dir())

    def test_sync_rotates_request_id_only_when_payload_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            created = create_workspace(Path(temporary), "Sample", date(2030, 1, 2))
            article_dir = Path(created["article_dir"])
            first = sync_workspace(article_dir)
            first_article = json.loads(
                (article_dir / "article.json").read_text(encoding="utf-8")
            )
            second = sync_workspace(article_dir)

            self.assertTrue(first["changed"])
            self.assertFalse(second["changed"])
            self.assertEqual(first["request_id"], second["request_id"])
            self.assertEqual(len(list((article_dir / "revisions").iterdir())), 1)

            changed_fragment = (
                f"{START}\n"
                '<section style="margin:0;padding:0;"><p>Updated body</p></section>\n'
                f"{END}\n"
            )
            (article_dir / "fragment.html").write_text(
                changed_fragment, encoding="utf-8"
            )
            third = sync_workspace(article_dir)
            third_article = json.loads(
                (article_dir / "article.json").read_text(encoding="utf-8")
            )

            self.assertTrue(third["changed"])
            self.assertNotEqual(first_article["request_id"], third_article["request_id"])
            self.assertEqual(third_article["content"].count("Updated body"), 1)
            self.assertEqual(len(list((article_dir / "revisions").iterdir())), 2)
            preview = (article_dir / "preview.html").read_text(encoding="utf-8")
            self.assertIn("Updated body", preview)
            self.assertNotIn("clipboard", preview.lower())
            self.assertNotIn("<script", preview.lower())


if __name__ == "__main__":
    unittest.main()
