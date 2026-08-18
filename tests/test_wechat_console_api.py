from __future__ import annotations

import importlib.util
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import ModuleType
from typing import Iterator

import pytest

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "wechat_console_api.py"
IMAGE_KEY = "image-key-for-local-mock"
PUBLISH_KEY = "publish-key-for-local-mock"


def _load_client() -> ModuleType:
    spec = importlib.util.spec_from_file_location("wechat_console_api", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mock_console() -> Iterator[tuple[str, ThreadingHTTPServer]]:
    class Handler(BaseHTTPRequestHandler):
        def _json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            self.server.records.append(("GET", self.path, self.headers, b""))
            if self.path == "/healthz":
                self._json(200, {"status": "ok"})
            else:
                self._json(404, {"detail": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            self.server.records.append(("POST", self.path, self.headers, body))
            authorization = self.headers.get("Authorization")
            if self.path == "/api/v1/wechat-images":
                if authorization != f"Bearer {IMAGE_KEY}":
                    self._json(401, {"detail": "bad image key"})
                    return
                filenames = []
                marker = b'name="images"; filename="'
                for part in body.split(marker)[1:]:
                    filenames.append(part.split(b'"', 1)[0].decode("utf-8"))
                mode = "article" if b"\r\narticle\r\n" in body else "material"
                items = []
                for index, filename in enumerate(filenames, start=1):
                    item = {
                        "filename": filename,
                        "url": f"http://mmbiz.qpic.cn/mock/{index}",
                        "status": "complete",
                        "errors": [],
                        "media_id": None,
                        "material_url": None,
                        "article_url": None,
                    }
                    if mode == "article":
                        item["article_url"] = item["url"]
                    else:
                        item["media_id"] = f"cover-media-{index}"
                        item["material_url"] = item["url"]
                    items.append(item)
                self._json(
                    201,
                    {
                        "items": items,
                        "count": len(items),
                        "success_count": len(items),
                        "error_count": 0,
                        "mode": mode,
                    },
                )
                return
            if self.path == "/api/v1/wechat-drafts":
                if authorization != f"Bearer {PUBLISH_KEY}":
                    self._json(401, {"detail": "bad publish key"})
                    return
                payload = json.loads(body.decode("utf-8"))
                self.server.draft_payloads.append(payload)
                if payload["title"] == "Pending":
                    self._json(
                        202,
                        {
                            "status": "pending",
                            "media_id": None,
                            "request_id": payload["request_id"],
                            "cached": True,
                            "validation": {
                                "characters": 70,
                                "bytes": 70,
                                "images": 1,
                            },
                        },
                    )
                    return
                self._json(
                    201,
                    {
                        "status": "created",
                        "media_id": "draft-media-1",
                        "request_id": payload["request_id"],
                        "cached": False,
                        "validation": {"characters": 70, "bytes": 70, "images": 1},
                    },
                )
                return
            self._json(404, {"detail": "not found"})

        def log_message(self, _format: str, *_args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.records = []
    server.draft_payloads = []
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}", server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_status_and_multipart_image_upload(
    tmp_path: Path, monkeypatch, capsys, mock_console
) -> None:
    base_url, server = mock_console
    monkeypatch.setenv("WECHAT_CONSOLE_URL", base_url)
    monkeypatch.setenv("WECHAT_IMAGE_API_KEY", IMAGE_KEY)
    monkeypatch.setenv("WECHAT_PUBLISH_API_KEY", PUBLISH_KEY)
    client = _load_client()

    assert client.main(["status"]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["console_configured"] is True
    assert status["transport_scheme"] == "http"
    assert status["transport_encrypted"] is False
    assert status["server_healthy"] is True
    assert "console_url" not in status
    assert status["image_api_key_configured"] is True
    assert status["publish_api_key_configured"] is True
    assert status["warnings"] == []

    first = tmp_path / "lead.jpg"
    second = tmp_path / "detail.png"
    first.write_bytes(b"jpeg-body")
    second.write_bytes(b"png-body")
    assert (
        client.main(["upload-images", "--mode", "article", str(first), str(second)])
        == 0
    )
    uploaded = json.loads(capsys.readouterr().out)
    assert [item["source_path"] for item in uploaded["items"]] == [
        str(first.resolve()),
        str(second.resolve()),
    ]
    assert uploaded["items"][0]["article_url"].startswith("https://mmbiz.qpic.cn/")
    assert uploaded["warnings"] == []

    uploads = [
        record for record in server.records if record[1] == "/api/v1/wechat-images"
    ]
    assert len(uploads) == 2
    for _, _, headers, body in uploads:
        assert headers["Authorization"] == f"Bearer {IMAGE_KEY}"
        assert headers["Content-Type"].startswith("multipart/form-data; boundary=")
        assert body.count(b'name="images"') == 1
        assert b'name="mode"' in body and b"\r\narticle\r\n" in body
    assert b"jpeg-body" in uploads[0][3]
    assert b"png-body" in uploads[1][3]


def test_remote_http_is_allowed_with_a_security_warning(monkeypatch) -> None:
    monkeypatch.setenv("WECHAT_CONSOLE_URL", "http://console.example.test:8791")
    client = _load_client()

    assert client._base_url() == "http://console.example.test:8791"
    assert client._transport_warnings() == [
        "Remote HTTP is not encrypted; API keys and article data may be "
        "intercepted. Enable HTTPS when possible."
    ]


def test_partial_upload_is_counted_as_an_error(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("WECHAT_IMAGE_API_KEY", IMAGE_KEY)
    client = _load_client()
    image = tmp_path / "partial.png"
    image.write_bytes(b"partial-image")

    monkeypatch.setattr(
        client,
        "_request_json",
        lambda *_args, **_kwargs: (
            200,
            {
                "items": [
                    {
                        "filename": image.name,
                        "status": "partial",
                        "errors": [],
                        "article_url": "http://mmbiz.qpic.cn/mock/partial",
                    }
                ]
            },
        ),
    )

    result = client._upload_images([image], "article")

    assert result["success_count"] == 0
    assert result["error_count"] == 1
    assert result["items"][0]["article_url"].startswith("https://mmbiz.qpic.cn/")


def test_article_url_upgrade_is_limited_to_wechat_hosts() -> None:
    client = _load_client()

    assert (
        client._normalize_article_url("http://mmbiz.qpic.cn/mock/1")
        == "https://mmbiz.qpic.cn/mock/1"
    )
    suspicious = "http://mmbiz.qpic.cn.example.com/mock/1"
    assert client._normalize_article_url(suspicious) == suspicious


def test_cover_upload_validation_and_draft_payload(
    tmp_path: Path, monkeypatch, capsys, mock_console
) -> None:
    base_url, server = mock_console
    monkeypatch.setenv("WECHAT_CONSOLE_URL", base_url)
    monkeypatch.setenv("WECHAT_IMAGE_API_KEY", IMAGE_KEY)
    monkeypatch.setenv("WECHAT_PUBLISH_API_KEY", PUBLISH_KEY)
    client = _load_client()

    cover = tmp_path / "cover.png"
    cover.write_bytes(b"cover-body")
    assert client.main(["upload-cover", str(cover)]) == 0
    cover_result = json.loads(capsys.readouterr().out)
    assert cover_result["media_id"] == "cover-media-1"

    article_path = tmp_path / "article.json"
    article = {
        "request_id": "article-example-001",
        "title": "测试文章",
        "author": "作者",
        "digest": "摘要",
        "content": ('<section><img src="https://mmbiz.qpic.cn/mock/1"></section>'),
        "thumb_media_id": cover_result["media_id"],
    }
    article_path.write_text(json.dumps(article, ensure_ascii=False), encoding="utf-8")
    request_count = len(server.records)
    assert client.main(["validate-draft", "--article", str(article_path)]) == 0
    validated = json.loads(capsys.readouterr().out)
    assert validated["valid"] is True
    assert validated["validation"]["images"] == 1
    assert len(server.records) == request_count

    assert client.main(["create-draft", "--article", str(article_path)]) == 0
    created = json.loads(capsys.readouterr().out)
    assert created["media_id"] == "draft-media-1"
    assert created["local_validation"]["images"] == 1
    assert server.records[-1][2]["Authorization"] == f"Bearer {PUBLISH_KEY}"
    assert server.records[-1][2]["Content-Type"] == "application/json; charset=utf-8"
    assert server.draft_payloads == [
        {
            **article,
            "content_source_url": "",
            "need_open_comment": 0,
            "only_fans_can_comment": 0,
        }
    ]


def test_http_errors_are_structured_and_do_not_expose_keys(
    tmp_path: Path, monkeypatch, capsys, mock_console
) -> None:
    base_url, _server = mock_console
    monkeypatch.setenv("WECHAT_CONSOLE_URL", base_url)
    monkeypatch.setenv("WECHAT_IMAGE_API_KEY", "wrong-secret-key")
    client = _load_client()
    image = tmp_path / "photo.png"
    image.write_bytes(b"image")

    assert client.main(["upload-images", str(image)]) == 1
    captured = capsys.readouterr()
    error = json.loads(captured.err)
    assert error == {"ok": False, "error": "bad image key", "http_status": 401}
    assert "wrong-secret-key" not in captured.err
    assert captured.out == ""


def test_invalid_draft_is_rejected_before_network(
    tmp_path: Path, monkeypatch, capsys, mock_console
) -> None:
    base_url, server = mock_console
    monkeypatch.setenv("WECHAT_CONSOLE_URL", base_url)
    monkeypatch.setenv("WECHAT_PUBLISH_API_KEY", PUBLISH_KEY)
    client = _load_client()
    article_path = tmp_path / "invalid.json"
    article_path.write_text(
        json.dumps(
            {
                "request_id": "article-invalid-001",
                "title": "Invalid",
                "content": '<img src="https://example.com/not-wechat.png">',
                "thumb_media_id": "cover-id",
            }
        ),
        encoding="utf-8",
    )

    assert client.main(["create-draft", "--article", str(article_path)]) == 1
    error = json.loads(capsys.readouterr().err)
    assert "article_url" in error["error"]
    assert server.records == []


def test_pending_draft_returns_incomplete_exit_code(
    tmp_path: Path, monkeypatch, capsys, mock_console
) -> None:
    base_url, _server = mock_console
    monkeypatch.setenv("WECHAT_CONSOLE_URL", base_url)
    monkeypatch.setenv("WECHAT_PUBLISH_API_KEY", PUBLISH_KEY)
    client = _load_client()
    article_path = tmp_path / "pending.json"
    article_path.write_text(
        json.dumps(
            {
                "request_id": "article-pending-001",
                "title": "Pending",
                "content": '<img src="https://mmbiz.qpic.cn/mock/1">',
                "thumb_media_id": "cover-id",
            }
        ),
        encoding="utf-8",
    )

    assert client.main(["create-draft", "--article", str(article_path)]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "pending"
    assert result["media_id"] is None
