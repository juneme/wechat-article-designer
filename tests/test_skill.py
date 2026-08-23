from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from argparse import Namespace
from datetime import date
from pathlib import Path
from unittest import mock

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import article_workspace
import audit_audience_boundary
import audit_design_contract
import audit_release_hygiene
import audit_wechat_contrast
import audit_wechat_markup
import audit_wechat_typography
import audit_wechat_widths
import design_contract
import release_article
import wechat_console_api


def ready_contract(title: str, *, local_preview: bool = True) -> dict[str, object]:
    contract = design_contract.empty_contract(title, local_preview=local_preview)
    contract["status"] = "READY"
    editorial = contract["editorial"]
    for key in (
        "reader",
        "narrator",
        "desired_action",
        "reader_situation",
        "central_friction",
        "judgment",
        "reader_gain",
        "evidence_boundary",
        "dominant_module",
        "closing_job",
    ):
        editorial[key] = f"verified {key}"
    editorial["reasoning_path"] = ["claim", "evidence", "action"]
    editorial["module_sequence"] = ["opening", "body", "closing"]

    layout = contract["layout"]
    layout["density_curve"] = ["open", "dense", "open"]
    layout["alignment_behavior"] = "Left reading flow; short labels may center."

    typography = contract["typography"]
    typography["role_relationships"] = "Display leads body by size and weight."

    color = contract["color"]
    for key in ("primary_signal", "secondary_signal", "correction"):
        color[key]["reason"] = f"N/A: {key} is not needed."
    color["usage_ratio"] = "Field 85%, ink 15%; no decorative signals."
    color["contrast"]["rationale"] = "Thresholds fit the selected reading sizes."

    contract["media"]["no_media_reason"] = "N/A: the article is type-led."
    geometry = contract["geometry"]
    for key in (
        "edge_language",
        "divider_policy",
        "surface_policy",
        "radius_policy",
        "content_native_motif",
        "recurrence_limit",
    ):
        geometry[key] = f"N/A: {key} is not used in this type-led fixture."
    geometry["used_roles"] = []
    effects = contract["effects"]
    effects.update(
        {
            "semantic_job": "N/A: motion would add no meaning.",
            "static_state": "All information is visible in ordinary flow.",
            "fallback": "Keep the same static flow.",
            "compatibility_risk": "None beyond baseline inline CSS.",
            "test_obligation": "Inspect 320px, 375px, and 390px widths.",
        }
    )
    delivery = contract["delivery"]
    delivery["editor_fallback"] = "Use the generated local preview before draft start."
    delivery["stop_condition"] = "Stop after a confirmed draft or local preview."
    contract["must_keep"] = ["Verified claims and literal topic"]
    contract["avoid"] = ["Agent workflow language"]
    contract["checks"] = {
        "editorial_passed": True,
        "design_values_verified": True,
        "fragment_sha256": "0" * 64,
    }
    return contract


def write_contract(workspace: Path, contract: dict[str, object]) -> None:
    (workspace / "design-contract.json").write_text(
        json.dumps(contract, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def bind_workspace_fragment(workspace: Path, contract: dict[str, object]) -> None:
    raw = (workspace / "fragment.html").read_text(encoding="utf-8")
    fragment = article_workspace._extract_fragment(raw)
    contract["status"] = "READY"
    contract["checks"]["fragment_sha256"] = design_contract.fragment_sha256(fragment)
    write_contract(workspace, contract)


class ContractTests(unittest.TestCase):
    def test_empty_contract_is_rejected_and_completed_contract_is_valid(self) -> None:
        empty = design_contract.empty_contract("Test")
        with self.assertRaises(design_contract.ContractError):
            design_contract.validate_contract(empty)

        valid = ready_contract("Test")
        design_contract.validate_contract(valid, required_status="READY")
        markdown = design_contract.render_contract_markdown(valid)
        self.assertIn("Test", markdown)
        self.assertIn('"body_first_line_indent_em": 2.0', markdown)

    def test_type_range_violation_blocks_contract(self) -> None:
        contract = ready_contract("Test")
        contract["typography"]["roles"]["body"]["font_size_px"] = 14
        with self.assertRaises(design_contract.ContractError):
            design_contract.validate_contract(contract, required_status="READY")

    def test_na_without_reason_is_rejected(self) -> None:
        contract = ready_contract("Test")
        contract["media"]["no_media_reason"] = "N/A"
        with self.assertRaises(design_contract.ContractError):
            design_contract.validate_contract(contract, required_status="READY")


class ArticleAuditTests(unittest.TestCase):
    def test_width_audit_rejects_600px(self) -> None:
        findings = audit_wechat_widths.audit_html(
            '<section style="width:600px;"></section><img width="600" />'
        )
        self.assertEqual(
            sum(item["code"] == "fixed-width-over-320px" for item in findings), 2
        )

    def test_nested_strong_text_is_checked_for_contrast(self) -> None:
        contract = ready_contract("Test")
        findings = audit_wechat_contrast.audit_html(
            '<p style="color:#777777;background:#777777;font-size:16px;">'
            "before <strong>nested text</strong></p>",
            contract,
        )
        self.assertIn("text-contrast", {item["code"] for item in findings})

    def test_gradient_contrast_requires_recorded_manual_review(self) -> None:
        contract = ready_contract("Test")
        html = (
            '<p style="color:#FFFFFF;background:linear-gradient(#202020,#FFFFFF);">text</p>'
        )
        findings = audit_wechat_contrast.audit_html(html, contract)
        self.assertEqual(findings[0]["severity"], "error")
        contract["exceptions"] = [
            {"code": "contrast-manual-review", "reason": "Confirmed in phone preview."}
        ]
        findings = audit_wechat_contrast.audit_html(html, contract)
        self.assertEqual(findings[0]["severity"], "warning")
        self.assertTrue(findings[0]["acknowledged"])

    def test_unrecorded_color_is_rejected(self) -> None:
        contract = ready_contract("Test")
        findings = audit_wechat_contrast.audit_html(
            '<p style="color:#123456;background:#FFFFFF;">text</p>', contract
        )
        self.assertIn("unrecorded-color", {item["code"] for item in findings})

    def test_agent_workflow_language_is_caught_but_dialogue_is_exempt(self) -> None:
        phrase = "如果你希望，我可以继续为你修改。请告诉我你的选择。"
        findings = audit_audience_boundary.audit_text(phrase)
        self.assertTrue(findings)
        dialogue = (
            '<section data-content-kind="dialogue"><p><strong>'
            + phrase
            + "</strong><span>仍属于引语。</span></p></section><p>正常正文。</p>"
        )
        extracted = audit_audience_boundary._html_text(dialogue)
        self.assertEqual(audit_audience_boundary.audit_text(extracted), [])

    def test_typography_matches_contract_and_rejects_manual_indent(self) -> None:
        contract = ready_contract("Test")
        family = "-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif"
        good = (
            f'<section style="font-family:{family};font-weight:400;text-align:left;'
            'letter-spacing:0;overflow-wrap:anywhere;text-indent:0;">'
            '<p data-type-role="body" style="font-size:16px;line-height:1.9;'
            'text-indent:2em;">正文内容。</p></section>'
        )
        self.assertEqual(audit_wechat_typography.audit_html(good, contract), [])

        bad = good.replace("text-indent:2em;\">正文", "text-indent:0;\">\u3000正文")
        codes = {
            item["code"]
            for item in audit_wechat_typography.audit_html(bad, contract)
        }
        self.assertIn("first-line-indent-contract-mismatch", codes)
        self.assertIn("manual-space-indentation", codes)

        double_indent = good.replace(">正文内容。", ">&emsp;&emsp;正文内容。")
        double_codes = {
            item["code"]
            for item in audit_wechat_typography.audit_html(double_indent, contract)
        }
        self.assertIn("manual-space-indentation", double_codes)
        self.assertNotIn("first-line-indent-contract-mismatch", double_codes)

    def test_markup_rejects_active_html_keyframes_and_local_images(self) -> None:
        contract = ready_contract("Test")
        value = (
            f"{audit_wechat_markup.START}\n"
            '<section style="animation:x 1s;@keyframes x{};'
            'background:linear-gradient(#202020,#FFFFFF);">'
            '<script>alert(1)</script><img src="local.png" alt="x" />'
            f"</section>plain root text\n{audit_wechat_markup.END}\n"
        )
        codes = {
            item["code"]
            for item in audit_wechat_markup.audit_html(value, contract)
        }
        self.assertTrue(
            {
                "tag-not-allowed",
                "css-rule-not-allowed",
                "effect-contract-mismatch",
                "non-hosted-image",
                "text-outside-element",
            }
            <= codes
        )

    def test_draft_validator_uses_markup_hard_rules(self) -> None:
        with self.assertRaises(wechat_console_api.ConsoleApiError):
            wechat_console_api._validate_content("<script>alert(1)</script>")

    def test_unconfirmed_draft_response_is_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            article = Path(temp) / "article.json"
            article.write_text(
                json.dumps(
                    {
                        "request_id": "request-001",
                        "title": "Test",
                        "author": "",
                        "digest": "",
                        "content": "<section></section>",
                        "content_source_url": "",
                        "thumb_media_id": "cover-id",
                        "need_open_comment": 0,
                        "only_fans_can_comment": 0,
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.object(
                wechat_console_api,
                "_request_json",
                return_value=(200, {"status": "unexpected"}),
            ), mock.patch.dict(
                "os.environ",
                {
                    "WECHAT_CONSOLE_URL": "https://console.example.test",
                    "WECHAT_PUBLISH_API_KEY": "synthetic-key",
                },
            ):
                with self.assertRaises(wechat_console_api.ConsoleApiError) as caught:
                    wechat_console_api._create_draft_article(str(article))
            self.assertTrue(caught.exception.ambiguous)

    def test_503_requires_explicit_no_draft_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            article = Path(temp) / "article.json"
            article.write_text(
                json.dumps(
                    {
                        "request_id": "request-503",
                        "title": "Test",
                        "author": "",
                        "digest": "",
                        "content": "<section></section>",
                        "content_source_url": "",
                        "thumb_media_id": "cover-id",
                        "need_open_comment": 0,
                        "only_fans_can_comment": 0,
                    }
                ),
                encoding="utf-8",
            )
            environment = {
                "WECHAT_CONSOLE_URL": "https://console.example.test",
                "WECHAT_PUBLISH_API_KEY": "synthetic-key",
            }
            ambiguous = wechat_console_api.ConsoleApiError(
                "unavailable", http_status=503, response_payload={"status": "unknown"}
            )
            with mock.patch.object(
                wechat_console_api, "_request_json", side_effect=ambiguous
            ), mock.patch.dict("os.environ", environment):
                with self.assertRaises(wechat_console_api.ConsoleApiError) as caught:
                    wechat_console_api._create_draft_article(str(article))
            self.assertTrue(caught.exception.ambiguous)

            confirmed = wechat_console_api.ConsoleApiError(
                "unavailable",
                http_status=503,
                response_payload={"draft_created": False},
            )
            with mock.patch.object(
                wechat_console_api, "_request_json", side_effect=confirmed
            ), mock.patch.dict("os.environ", environment):
                with self.assertRaises(wechat_console_api.ConsoleApiError) as caught:
                    wechat_console_api._create_draft_article(str(article))
            self.assertFalse(caught.exception.ambiguous)

    def test_structural_contract_checks_modules_spacing_media_and_digest(self) -> None:
        contract = ready_contract("Test")
        contract["editorial"]["module_sequence"] = ["opening", "body", "closing"]
        contract["layout"]["used_spacing_roles"] = ["section-gap", "paragraph-gap"]
        contract["layout"]["fixed_widths_px"] = [120]
        contract["geometry"]["edge_language"] = "Use square editorial edges."
        contract["geometry"]["used_roles"] = ["edge-language"]
        contract["geometry"]["implementations"] = {
            "edge-language": ["border-radius:0"]
        }
        contract["media"] = {
            "assets": [
                {
                    "name": "lead",
                    "reader_job": "Opening illustration.",
                    "authority": "Illustrative only.",
                    "order": 1,
                    "crop": "natural",
                    "caption": "Lead caption.",
                    "state": "placeholder",
                    "placement": "body",
                    "required": False,
                    "source_path": "",
                }
            ],
            "no_media_reason": "",
        }
        html = (
            '<section data-module-id="opening" data-density="open" '
            'data-layout-role="outer-baseline" data-geometry-role="edge-language" '
            'style="width:120px;margin:0;padding:0 8px;border-radius:0;"></section>'
            '<section data-module-id="body" data-density="dense" '
            'data-layout-role="content-inset" data-spacing-role="section-gap" '
            'style="margin:42px 0 0;padding:0 18px;">'
            '<p data-spacing-role="paragraph-gap" style="margin:0 0 10px;">Body</p>'
            '<img data-media-id="lead" data-media-crop="natural" '
            'src="wechat-media://lead" alt="" />'
            '<p data-caption-for="lead">Lead caption.</p>'
            "</section>"
            '<section data-module-id="closing" data-density="open" '
            'data-spacing-role="section-gap" '
            'style="margin:42px 0 0;"></section>'
        )
        contract["checks"]["fragment_sha256"] = design_contract.fragment_sha256(html)
        self.assertEqual(audit_design_contract.audit_html(html, contract), [])
        changed = html.replace('data-module-id="body"', 'data-module-id="proof"')
        codes = {item["code"] for item in audit_design_contract.audit_html(changed, contract)}
        self.assertIn("fragment-contract-digest", codes)
        self.assertIn("module-sequence-contract-mismatch", codes)
        no_geometry = html.replace(' data-geometry-role="edge-language"', "")
        codes = {
            item["code"] for item in audit_design_contract.audit_html(no_geometry, contract)
        }
        self.assertIn("geometry-contract-mismatch", codes)
        wrong_layout = html.replace("padding:0 18px", "padding:0 17px")
        codes = {
            item["code"]
            for item in audit_design_contract.audit_html(wrong_layout, contract)
        }
        self.assertIn("layout-value-contract-mismatch", codes)
        wrong_density = html.replace('data-density="dense"', 'data-density="open"')
        codes = {
            item["code"]
            for item in audit_design_contract.audit_html(wrong_density, contract)
        }
        self.assertIn("density-curve-contract-mismatch", codes)
        wrong_geometry = html.replace("border-radius:0", "border-radius:8px")
        codes = {
            item["code"]
            for item in audit_design_contract.audit_html(wrong_geometry, contract)
        }
        self.assertIn("geometry-css-contract-mismatch", codes)
        wrong_crop = html.replace('data-media-crop="natural"', 'data-media-crop="prepared"')
        codes = {
            item["code"]
            for item in audit_design_contract.audit_html(wrong_crop, contract)
        }
        self.assertIn("media-crop-contract-mismatch", codes)
        wrong_caption = html.replace("Lead caption.</p>", "Wrong caption.</p>")
        codes = {
            item["code"]
            for item in audit_design_contract.audit_html(wrong_caption, contract)
        }
        self.assertIn("media-caption-contract-mismatch", codes)


class WorkspaceTests(unittest.TestCase):
    def create_ready_workspace(self, root: Path) -> Path:
        result = article_workspace.create_workspace(
            root, "Test Article", date(2026, 8, 22), local_preview=True
        )
        workspace = Path(result["article_dir"])
        contract = ready_contract("Test Article")
        contract["status"] = "PLANNED"
        contract["checks"]["fragment_sha256"] = ""
        write_contract(workspace, contract)
        article_workspace.record_plan(workspace)
        bind_workspace_fragment(workspace, contract)
        return workspace

    def test_direct_route_physically_removes_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.create_ready_workspace(Path(temp))
            self.assertTrue((workspace / "preview.html").is_file())
            result = article_workspace.sync_workspace(workspace, local_preview=False)
            self.assertTrue(result["changed"])
            self.assertFalse((workspace / "preview.html").exists())

    def test_planned_and_ready_stage_gates_cannot_be_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = article_workspace.create_workspace(
                Path(temp), "Stage Gates", date(2026, 8, 22), local_preview=True
            )
            workspace = Path(result["article_dir"])
            with self.assertRaises(design_contract.ContractError):
                article_workspace.record_plan(workspace)

            contract = ready_contract("Stage Gates")
            contract["status"] = "PLANNED"
            contract["checks"]["fragment_sha256"] = ""
            write_contract(workspace, contract)
            planned = article_workspace.record_plan(workspace)
            self.assertTrue(planned["changed"])
            with self.assertRaises(design_contract.ContractError):
                article_workspace.sync_workspace(workspace)

            bind_workspace_fragment(workspace, contract)
            synced = article_workspace.sync_workspace(workspace)
            self.assertTrue(synced["changed"])

    def test_first_plan_rejects_html_written_before_design_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = article_workspace.create_workspace(
                Path(temp), "Plan Order", date(2026, 8, 23), local_preview=True
            )
            workspace = Path(result["article_dir"])
            contract = ready_contract("Plan Order")
            contract["status"] = "PLANNED"
            contract["checks"]["fragment_sha256"] = ""
            write_contract(workspace, contract)
            (workspace / "fragment.html").write_text(
                f"{article_workspace.START}\n<section>implemented early</section>\n"
                f"{article_workspace.END}\n",
                encoding="utf-8",
            )
            with self.assertRaises(article_workspace.WorkspaceError):
                article_workspace.record_plan(workspace)

    def test_schema_three_workspace_and_contract_two_can_migrate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = article_workspace.create_workspace(
                Path(temp), "Migration", date(2026, 8, 23), local_preview=True
            )
            workspace = Path(result["article_dir"])
            manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
            manifest["schema_version"] = 3
            for key in (
                "implementation_base_sha256",
                "active_plan_iterations",
                "draft_submission",
                "image_generation_attempt",
            ):
                manifest.pop(key, None)
            (workspace / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            contract = ready_contract("Migration")
            contract["schema_version"] = 2
            contract["geometry"].pop("implementations", None)
            write_contract(workspace, contract)
            migrated = article_workspace.migrate_workspace(workspace)
            self.assertTrue(migrated["changed"])
            self.assertEqual(migrated["schema_version"], 4)
            migrated_contract = design_contract.load_contract(
                workspace / "design-contract.json"
            )
            self.assertEqual(migrated_contract["schema_version"], 3)
            design_contract.validate_contract(
                migrated_contract, required_status="READY"
            )
            self.assertIn(
                "legacy-contract-migration",
                design_contract.exception_map(migrated_contract),
            )

    def test_schema_two_workspace_without_contract_can_migrate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = article_workspace.create_workspace(
                Path(temp), "Legacy Workspace", date(2026, 8, 23), local_preview=True
            )
            workspace = Path(result["article_dir"])
            manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
            manifest["schema_version"] = 2
            for key in (
                "workspace_state_sha256",
                "planned_contract_sha256",
                "implementation_base_sha256",
                "active_plan_iterations",
                "draft_submission",
                "image_generation_attempt",
            ):
                manifest.pop(key, None)
            (workspace / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (workspace / "design-contract.json").unlink()
            (workspace / "design-contract.md").unlink()
            migrated = article_workspace.migrate_workspace(workspace)
            self.assertTrue(migrated["changed"])
            migrated_contract = design_contract.load_contract(
                workspace / "design-contract.json"
            )
            self.assertEqual(migrated_contract["status"], "INCOMPLETE")
            self.assertEqual(migrated_contract["scope"], "substantial-redesign")

    def test_revision_tracks_all_state_but_request_id_tracks_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.create_ready_workspace(Path(temp))
            first = article_workspace.sync_workspace(workspace)
            first_id = first["request_id"]
            revision = first["revision"]

            contract = design_contract.load_contract(workspace / "design-contract.json")
            contract["geometry"]["edge_language"] = "Changed edge decision."
            contract["geometry"]["used_roles"] = ["edge-language"]
            contract["geometry"]["implementations"] = {
                "edge-language": ["border-radius:0"]
            }
            contract["status"] = "PLANNED"
            contract["checks"]["fragment_sha256"] = ""
            write_contract(workspace, contract)
            article_workspace.record_plan(workspace)
            bind_workspace_fragment(workspace, contract)
            changed_contract = article_workspace.sync_workspace(workspace)
            self.assertEqual(changed_contract["revision"], revision + 2)
            self.assertEqual(changed_contract["request_id"], first_id)

            (workspace / "assets" / "synthetic.txt").write_text(
                "synthetic fixture", encoding="utf-8"
            )
            changed_asset = article_workspace.sync_workspace(workspace)
            self.assertEqual(
                changed_asset["revision"], changed_contract["revision"] + 1
            )
            self.assertEqual(changed_asset["request_id"], first_id)

            (workspace / "preview.html").write_text("stale preview", encoding="utf-8")
            changed_preview = article_workspace.sync_workspace(workspace)
            self.assertEqual(
                changed_preview["revision"], changed_asset["revision"] + 1
            )
            self.assertEqual(changed_preview["request_id"], first_id)

            fragment = workspace / "fragment.html"
            fragment.write_text(
                f"{article_workspace.START}\n"
                '<section style="margin:0;">changed body</section>\n'
                f"{article_workspace.END}\n",
                encoding="utf-8",
            )
            contract = design_contract.load_contract(workspace / "design-contract.json")
            bind_workspace_fragment(workspace, contract)
            changed_body = article_workspace.sync_workspace(workspace)
            self.assertNotEqual(changed_body["request_id"], first_id)

    def test_transaction_rolls_back_root_files_after_write_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.create_ready_workspace(Path(temp))
            article_workspace.sync_workspace(workspace)
            contract = design_contract.load_contract(workspace / "design-contract.json")
            contract["geometry"]["divider_policy"] = "Changed divider decision."
            contract["geometry"]["used_roles"] = ["divider-policy"]
            contract["geometry"]["implementations"] = {
                "divider-policy": ["border-top-style:solid"]
            }
            contract["status"] = "PLANNED"
            contract["checks"]["fragment_sha256"] = ""
            write_contract(workspace, contract)
            article_workspace.record_plan(workspace)
            bind_workspace_fragment(workspace, contract)
            snapshot = {
                name: (workspace / name).read_bytes()
                for name in article_workspace.TRACKED_FILES
                if (workspace / name).is_file()
            }
            original = article_workspace._atomic_write_bytes
            failed = False

            def fail_once(path: Path, value: bytes) -> None:
                nonlocal failed
                if path.parent == workspace and path.name == "fragment.html" and not failed:
                    failed = True
                    raise OSError("synthetic write failure")
                original(path, value)

            with mock.patch.object(
                article_workspace, "_atomic_write_bytes", side_effect=fail_once
            ):
                with self.assertRaises(article_workspace.WorkspaceError):
                    article_workspace.sync_workspace(workspace)

            restored = {
                name: (workspace / name).read_bytes()
                for name in article_workspace.TRACKED_FILES
                if (workspace / name).is_file()
            }
            self.assertEqual(restored, snapshot)


class ReleaseWorkflowTests(unittest.TestCase):
    def create_planned_workspace(self, root: Path, *, placeholder: bool = False) -> Path:
        result = article_workspace.create_workspace(
            root, "Release Article", date(2026, 8, 23), local_preview=True
        )
        workspace = Path(result["article_dir"])
        contract = ready_contract("Release Article")
        contract["status"] = "PLANNED"
        contract["checks"]["fragment_sha256"] = ""
        contract["editorial"]["module_sequence"] = ["body"]
        contract["layout"]["density_curve"] = ["open"]
        contract["layout"]["used_spacing_roles"] = ["paragraph-gap"]
        contract["geometry"]["used_roles"] = []
        (workspace / "assets" / "cover.png").write_bytes(
            b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + struct.pack(">II", 2350, 1000)
        )
        cover = {
            "name": "cover",
            "reader_job": "Represent the article in the draft list.",
            "authority": "Illustrative only.",
            "order": 2,
            "crop": "aspect-ratio:2.35",
            "caption": "N/A: cover does not appear in the body.",
            "state": "hosted",
            "placement": "cover",
            "required": True,
            "source_path": "cover.png",
            "remote_ref": "cover-id",
        }
        contract["media"] = {"assets": [cover], "no_media_reason": ""}
        media = ""
        if placeholder:
            contract["media"] = {
                "assets": [
                    {
                        "name": "hero",
                        "reader_job": "Establish the article subject.",
                        "authority": "Illustrative only.",
                        "order": 1,
                        "crop": "prepared",
                        "caption": "N/A: purely illustrative.",
                        "state": "placeholder",
                        "placement": "body",
                        "required": True,
                        "source_path": "",
                    },
                    cover,
                ],
                "no_media_reason": "",
            }
            contract["delivery"]["image_generation_status"] = "pending"
            contract["delivery"]["image_generation_reason"] = (
                "Required hero image still needs generation."
            )
            media = (
                '<img data-media-id="hero" data-media-crop="prepared" '
                'src="wechat-media://hero" alt="" '
                'style="display:block;width:100%;height:auto;margin:0;border:0;" />'
            )
        write_contract(workspace, contract)
        article_workspace.record_plan(workspace)
        family = "-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif"
        fragment = (
            f"{article_workspace.START}\n"
            '<section data-module-id="body" data-density="open" '
            'data-layout-role="outer-baseline" '
            'style="margin:0;padding:0 8px;background:#FFFFFF;color:#202020;">'
            '<section data-layout-role="content-inset" '
            'style="margin:0;padding:0 18px;background:#FFFFFF;color:#202020;">'
            f'<p data-type-role="body" data-spacing-role="paragraph-gap" '
            f'style="margin:0 0 10px;padding:0;color:#202020;background:#FFFFFF;'
            f"font-family:{family};font-size:16px;line-height:1.9;font-weight:400;"
            'letter-spacing:0;text-align:left;text-indent:2em;overflow-wrap:anywhere;">'
            "Verified article copy.</p>"
            f"{media}</section></section>\n"
            f"{article_workspace.END}\n"
        )
        (workspace / "fragment.html").write_text(fragment, encoding="utf-8")
        return workspace

    def test_backend_status_requires_all_variables_and_healthy_response(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertFalse(release_article._backend_status()["ready"])
        configured = {
            "WECHAT_CONSOLE_URL": "https://console.example.test",
            "WECHAT_IMAGE_API_KEY": "image-key",
            "WECHAT_PUBLISH_API_KEY": "publish-key",
        }
        unhealthy = {
            "console_configured": True,
            "image_api_key_configured": True,
            "publish_api_key_configured": True,
            "server_healthy": False,
        }
        healthy = dict(unhealthy, server_healthy=True)
        with mock.patch.dict("os.environ", configured, clear=True), mock.patch.object(
            wechat_console_api, "_run", return_value=(unhealthy, 0)
        ):
            self.assertFalse(release_article._backend_status()["ready"])
        with mock.patch.dict("os.environ", configured, clear=True), mock.patch.object(
            wechat_console_api, "_run", return_value=(healthy, 0)
        ):
            self.assertTrue(release_article._backend_status()["ready"])

    def test_prepared_generated_media_is_uploaded_and_bound_to_fragment(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            (workspace / "assets").mkdir()
            (workspace / "assets" / "hero.png").write_bytes(b"synthetic-image")
            contract = ready_contract("Test")
            contract["media"] = {
                "assets": [
                    {
                        "name": "hero",
                        "reader_job": "Opening illustration.",
                        "authority": "Illustrative only.",
                        "order": 1,
                        "crop": "natural",
                        "caption": "N/A: no caption needed.",
                        "state": "generated-local",
                        "placement": "body",
                        "required": True,
                        "source_path": "hero.png",
                    }
                ],
                "no_media_reason": "",
            }
            fragment = (
                '<img data-media-id="hero" src="wechat-media://hero" alt="" '
                'style="display:block;width:100%;height:auto;" />'
            )
            upload = {
                "items": [
                    {
                        "status": "complete",
                        "article_url": "https://mmbiz.qpic.cn/hero.png",
                    }
                ],
                "error_count": 0,
            }
            with mock.patch.object(
                wechat_console_api, "_upload_images", return_value=upload
            ):
                updated, _, updated_fragment = release_article._upload_local_media(
                    workspace, contract, {"thumb_media_id": ""}, fragment
                )
            asset = updated["media"]["assets"][0]
            self.assertEqual(asset["state"], "hosted")
            self.assertEqual(asset["remote_ref"], "https://mmbiz.qpic.cn/hero.png")
            self.assertIn('src="https://mmbiz.qpic.cn/hero.png"', updated_fragment)

    def test_missing_image_blocks_until_generation_failure_is_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.create_planned_workspace(Path(temp), placeholder=True)
            with mock.patch.dict("os.environ", {}, clear=True):
                blocked, blocked_code = release_article.release_workspace(workspace)
                self.assertEqual(blocked_code, 3)
                self.assertEqual(blocked["status"], "image-generation-required")
                delivered, delivered_code = release_article.release_workspace(
                    workspace,
                    generation_failure="image service unavailable",
                    generation_attempt_id=blocked["attempt_id"],
                )
            self.assertEqual(delivered_code, 0)
            self.assertEqual(delivered["status"], "local-preview")
            self.assertTrue((workspace / "preview.html").is_file())

    def test_generation_failure_cannot_skip_the_required_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.create_planned_workspace(Path(temp), placeholder=True)
            with mock.patch.dict("os.environ", {}, clear=True):
                with self.assertRaises(release_article.ReleaseError):
                    release_article.release_workspace(
                        workspace,
                        generation_failure="not actually attempted",
                        generation_attempt_id="invented",
                    )

    def test_cover_dimensions_are_machine_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            square = Path(temp) / "square.png"
            square.write_bytes(
                b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + struct.pack(">II", 1000, 1000)
            )
            valid = Path(temp) / "cover.png"
            valid.write_bytes(
                b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + struct.pack(">II", 2350, 1000)
            )
            self.assertFalse(release_article._cover_is_235_by_100(square)[0])
            self.assertTrue(release_article._cover_is_235_by_100(valid)[0])

    def test_definite_401_switches_to_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.create_planned_workspace(Path(temp))
            article = json.loads((workspace / "article.json").read_text(encoding="utf-8"))
            article["thumb_media_id"] = "cover-id"
            (workspace / "article.json").write_text(json.dumps(article), encoding="utf-8")
            error = wechat_console_api.ConsoleApiError("unauthorized", http_status=401)
            with mock.patch.object(
                release_article,
                "_backend_status",
                return_value={"ready": True, "reason": None},
            ), mock.patch.object(
                wechat_console_api, "_create_draft_article", side_effect=error
            ):
                result, exit_code = release_article.release_workspace(workspace)
            self.assertEqual(exit_code, 0)
            self.assertEqual(result["status"], "local-preview")
            self.assertTrue((workspace / "preview.html").is_file())

    def test_ambiguous_draft_result_does_not_create_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.create_planned_workspace(Path(temp))
            article = json.loads((workspace / "article.json").read_text(encoding="utf-8"))
            article["thumb_media_id"] = "cover-id"
            (workspace / "article.json").write_text(json.dumps(article), encoding="utf-8")
            error = wechat_console_api.ConsoleApiError("timeout", ambiguous=True)
            with mock.patch.object(
                release_article,
                "_backend_status",
                return_value={"ready": True, "reason": None},
            ), mock.patch.object(
                wechat_console_api, "_create_draft_article", side_effect=error
            ) as create_draft:
                result, exit_code = release_article.release_workspace(workspace)
                repeated, repeated_code = release_article.release_workspace(workspace)
            self.assertEqual(exit_code, 2)
            self.assertEqual(result["status"], "ambiguous")
            self.assertTrue(result["do_not_retry"])
            self.assertFalse((workspace / "preview.html").exists())
            self.assertEqual(repeated_code, 2)
            self.assertEqual(repeated["status"], "ambiguous")
            self.assertEqual(create_draft.call_count, 1)
            manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["draft_submission"]["state"], "ambiguous")

    def test_confirmed_draft_is_persisted_and_not_resubmitted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.create_planned_workspace(Path(temp))
            article = json.loads((workspace / "article.json").read_text(encoding="utf-8"))
            article["thumb_media_id"] = "cover-id"
            (workspace / "article.json").write_text(json.dumps(article), encoding="utf-8")

            def created(path_value: str) -> tuple[dict[str, object], int]:
                payload = json.loads(Path(path_value).read_text(encoding="utf-8"))
                return {
                    "status": "created",
                    "media_id": "draft-media-id",
                    "request_id": payload["request_id"],
                }, 0

            with mock.patch.object(
                release_article,
                "_backend_status",
                return_value={"ready": True, "reason": None},
            ), mock.patch.object(
                wechat_console_api, "_create_draft_article", side_effect=created
            ) as create_draft:
                first, first_code = release_article.release_workspace(workspace)
                second, second_code = release_article.release_workspace(workspace)
            self.assertEqual(first_code, 0)
            self.assertEqual(second_code, 0)
            self.assertEqual(first["status"], "draft-created")
            self.assertEqual(second["status"], "draft-created")
            self.assertEqual(create_draft.call_count, 1)
            manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["draft_submission"]["state"], "created")

    def test_low_level_create_draft_is_disabled(self) -> None:
        with self.assertRaises(wechat_console_api.ConsoleApiError):
            wechat_console_api._run(Namespace(command="create-draft"))
        with self.assertRaises(SystemExit), mock.patch("sys.stderr"):
            wechat_console_api._build_parser().parse_args(
                ["upload-images", "synthetic.png"]
            )

    def test_publishable_metadata_is_audited_before_media_upload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.create_planned_workspace(Path(temp))
            article = json.loads((workspace / "article.json").read_text(encoding="utf-8"))
            article["thumb_media_id"] = "cover-id"
            article["digest"] = "如果你希望，我可以继续为你修改。"
            (workspace / "article.json").write_text(json.dumps(article), encoding="utf-8")
            with mock.patch.object(
                release_article,
                "_backend_status",
                return_value={"ready": True, "reason": None},
            ), mock.patch.object(release_article, "_upload_local_media") as upload:
                with self.assertRaises(release_article.ReleaseError):
                    release_article.release_workspace(workspace)
            upload.assert_not_called()

    def test_release_persistence_rolls_back_before_sync_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = self.create_planned_workspace(Path(temp))
            contract = design_contract.load_contract(workspace / "design-contract.json")
            article = json.loads((workspace / "article.json").read_text(encoding="utf-8"))
            fragment = (workspace / "fragment.html").read_text(encoding="utf-8")
            backups = {
                name: (workspace / name).read_bytes() if (workspace / name).is_file() else None
                for name in article_workspace.TRACKED_FILES
            }
            article["digest"] = "candidate change"
            with mock.patch.object(
                article_workspace,
                "sync_workspace",
                side_effect=article_workspace.WorkspaceError("synthetic sync failure"),
            ):
                with self.assertRaises(article_workspace.WorkspaceError):
                    release_article._persist_and_sync(
                        workspace,
                        contract,
                        article,
                        fragment,
                        local_preview=True,
                    )
            restored = {
                name: (workspace / name).read_bytes() if (workspace / name).is_file() else None
                for name in article_workspace.TRACKED_FILES
            }
            self.assertEqual(restored, backups)


class ReleaseHygieneTests(unittest.TestCase):
    def test_cache_cleanup_is_scoped_and_auditable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "agents").mkdir()
            (root / "agents" / "openai.yaml").write_text(
                "Use $wechat-article-designer with the three console variables; "
                "when healthy create a new draft, otherwise deliver a local preview.",
                encoding="utf-8",
            )
            cache = root / "scripts" / "__pycache__"
            cache.mkdir(parents=True)
            (cache / "synthetic.pyc").write_bytes(b"test")
            removed = audit_release_hygiene.clean_caches(root)
            self.assertIn("scripts/__pycache__", removed)
            self.assertFalse(cache.exists())
            self.assertEqual(audit_release_hygiene.audit_root(root), [])

    def test_conversation_content_is_detected_but_readme_examples_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "agents").mkdir()
            (root / "agents" / "openai.yaml").write_text(
                "Use $wechat-article-designer with the three console variables; "
                "when healthy create a new draft, otherwise deliver a local preview. "
                "如果你希望，我可以继续。",
                encoding="utf-8",
            )
            (root / "notes.md").write_text("User: leaked request", encoding="utf-8")
            (root / "README.md").write_text("User: allowed usage example", encoding="utf-8")
            findings = audit_release_hygiene.audit_root(root)
            self.assertEqual(
                [item["path"] for item in findings if item["code"] == "conversation-content"],
                ["notes.md"],
            )
            self.assertIn(
                "conversational-default-prompt", {item["code"] for item in findings}
            )


if __name__ == "__main__":
    unittest.main()
