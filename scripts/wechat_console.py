from __future__ import annotations

import argparse
import getpass
import json
import mimetypes
import os
import re
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse, urlsplit, urlunsplit
from urllib.request import Request, urlopen


CONFIG_PATH = Path.home() / ".codex" / "yunoe" / "client.json"
WRITE_METHODS = {"POST", "PUT", "DELETE"}
WECHAT_IMAGE_HOST_ALIASES = {"mmbiz.qpic.cn", "mmecoa.qpic.cn"}
_IMAGE_TAG_PATTERN = re.compile(
    r"<img\b(?:[^>'\"]|'[^']*'|\"[^\"]*\")*>", re.IGNORECASE
)
_SOURCE_ATTRIBUTE_PATTERN = re.compile(
    r"(?P<prefix>\bsrc\s*=\s*)"
    r"(?:(?P<quote>['\"])(?P<quoted>.*?)(?P=quote)|(?P<bare>[^\s>]+))",
    re.IGNORECASE,
)


class ClientError(RuntimeError):
    pass


def _json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _print_json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def _server_url(value: str) -> str:
    result = value.strip().rstrip("/")
    parsed = urlparse(result)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ClientError("服务器地址必须以 http:// 或 https:// 开头")
    return result


def _normalize_article_image_url(source: str) -> str:
    parsed = urlsplit(source.strip())
    if (parsed.hostname or "").lower() not in WECHAT_IMAGE_HOST_ALIASES:
        return source.strip()
    return urlunsplit(
        ("https", "mmbiz.qpic.cn", parsed.path, parsed.query, parsed.fragment)
    )


def _normalize_article_content(content: str) -> str:
    def normalize_tag(tag_match: re.Match[str]) -> str:
        def normalize_source(source_match: re.Match[str]) -> str:
            quote = source_match.group("quote") or ""
            source = source_match.group("quoted") or source_match.group("bare") or ""
            normalized = _normalize_article_image_url(source)
            return f"{source_match.group('prefix')}{quote}{normalized}{quote}"

        return _SOURCE_ATTRIBUTE_PATTERN.sub(
            normalize_source, tag_match.group(0), count=1
        )

    return _IMAGE_TAG_PATTERN.sub(normalize_tag, content)


def _save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = CONFIG_PATH.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    try:
        os.chmod(temporary, 0o600)
    except OSError:
        pass
    temporary.replace(CONFIG_PATH)


def _load_config() -> dict:
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ClientError("尚未配对，请先运行 pair") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ClientError(f"本地配对配置不可读：{exc}") from exc
    if not config.get("console_url") or not config.get("client_token"):
        raise ClientError("本地配对配置不完整，请重新运行 pair")
    return config


def _decode_response(response) -> object:
    raw = response.read()
    if not raw:
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClientError("服务器返回了无法解析的响应") from exc


def _request(
    method: str,
    url: str,
    *,
    token: str | None = None,
    account_id: int | None = None,
    body: bytes | None = None,
    content_type: str | None = None,
) -> object:
    headers = {"Accept": "application/json", "User-Agent": "yunoe/1"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if account_id is not None:
        headers["X-Wechat-Account-ID"] = str(account_id)
    if content_type:
        headers["Content-Type"] = content_type
    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=90) as response:
            return _decode_response(response)
    except HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode("utf-8"))
            detail = payload.get("detail") or payload
        except Exception:
            detail = exc.reason
        suffix = "；写操作未自动重试，请先核对远端状态" if method in WRITE_METHODS and exc.code >= 500 else ""
        raise ClientError(f"HTTP {exc.code}: {detail}{suffix}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        suffix = "；写操作结果可能不确定，请勿自动重试" if method in WRITE_METHODS else ""
        raise ClientError(f"无法连接服务器：{exc}{suffix}") from exc


def _authorized_request(
    args: argparse.Namespace,
    method: str,
    path: str,
    *,
    payload: object | None = None,
    body: bytes | None = None,
    content_type: str | None = None,
) -> object:
    config = _load_config()
    if payload is not None:
        body = _json_bytes(payload)
        content_type = "application/json"
    return _request(
        method,
        f"{config['console_url']}{path}",
        token=config["client_token"],
        account_id=args.account_id,
        body=body,
        content_type=content_type,
    )


def _multipart(files: list[Path], *, mode: str | None = None) -> tuple[bytes, str]:
    boundary = f"wechat-{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    if mode is not None:
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                b'Content-Disposition: form-data; name="mode"\r\n\r\n',
                mode.encode(),
                b"\r\n",
            ]
        )
    for path in files:
        if not path.is_file():
            raise ClientError(f"文件不存在：{path}")
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        safe_name = path.name.replace('"', "")
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                (
                    f'Content-Disposition: form-data; name="images"; '
                    f'filename="{safe_name}"\r\n'
                ).encode("utf-8"),
                f"Content-Type: {content_type}\r\n\r\n".encode(),
                path.read_bytes(),
                b"\r\n",
            ]
        )
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def _load_payload(path_value: str, *, allow_content_file: bool = False) -> dict:
    path = Path(path_value).expanduser().resolve()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ClientError(f"JSON 文件不存在：{path}") from exc
    except json.JSONDecodeError as exc:
        raise ClientError(f"JSON 格式错误：{exc}") from exc
    if not isinstance(payload, dict):
        raise ClientError("JSON 顶层必须是对象")
    if allow_content_file and "content_file" in payload:
        content_path = (path.parent / str(payload.pop("content_file"))).resolve()
        try:
            payload["content"] = content_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise ClientError(f"正文文件不存在：{content_path}") from exc
    if allow_content_file and isinstance(payload.get("content"), str):
        payload["content"] = _normalize_article_content(payload["content"])
    return payload


def _exchange_pairing(console_url: str, code: str) -> tuple[str, str | None]:
    console_url = _server_url(console_url)
    code = code.strip()
    if not code:
        raise ClientError("验证码不能为空")
    result = _request(
        "POST",
        f"{console_url}/api/v1/pairing/exchange",
        body=_json_bytes({"code": code}),
        content_type="application/json",
    )
    if not isinstance(result, dict) or not result.get("client_token"):
        raise ClientError("服务器未返回客户端令牌")
    saved_url = _server_url(str(result.get("console_url") or console_url))
    _save_config(
        {
            "console_url": saved_url,
            "client_token": result["client_token"],
            "paired_at": datetime.now(UTC).isoformat(timespec="seconds"),
        }
    )
    return saved_url, result.get("warning")


def command_pair(args: argparse.Namespace) -> None:
    code = getpass.getpass("请输入云浪控制台 1 分钟验证码：").strip()
    saved_url, warning = _exchange_pairing(args.server, code)
    print(f"配对成功：{saved_url}")
    if warning:
        print(f"提醒：{warning}")


def command_pair_ui(args: argparse.Namespace) -> None:
    try:
        import ctypes
        import queue
        import threading
        import tkinter as tk
    except ImportError as exc:
        raise ClientError("当前 Python 缺少 Tk 图形界面支持，请使用终端 pair 命令") from exc

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass

    root = tk.Tk()
    root.withdraw()
    root.title("云浪公众号排版 · 本地安全配对")
    root.resizable(False, False)
    root.configure(bg="#f4f4f5")

    server_value = tk.StringVar(value=args.server or "")
    code_value = tk.StringVar()
    show_code_value = tk.BooleanVar(value=False)
    status_title_value = tk.StringVar(value="本地安全输入")
    status_detail_value = tk.StringVar(value="验证码不会显示在对话或命令行中。")
    events: queue.Queue[tuple[str, object, object | None]] = queue.Queue()

    shell = tk.Frame(root, bg="#f4f4f5")
    shell.pack(fill="both", expand=True)

    brand = tk.Canvas(
        shell,
        width=238,
        height=454,
        bg="#26282d",
        highlightthickness=0,
    )
    brand.pack(side="left", fill="y")
    brand.create_oval(146, -48, 306, 112, outline="#d8b36c", width=1)
    brand.create_oval(183, -11, 269, 75, fill="#d8b36c", outline="")
    brand.create_oval(201, 7, 269, 75, fill="#26282d", outline="")
    brand.create_line(0, 365, 80, 343, 162, 358, 238, 337, smooth=True, fill="#8a93a3")
    brand.create_line(0, 390, 86, 365, 164, 382, 238, 361, smooth=True, fill="#d8b36c")
    brand.create_text(
        28,
        34,
        text="YUNOE / CONNECT",
        fill="#d8b36c",
        font=("Segoe UI", 9, "bold"),
        anchor="nw",
    )
    brand.create_text(
        28,
        144,
        text="云浪\n公众号排版",
        fill="#f7f7f8",
        font=("Microsoft YaHei UI", 23, "bold"),
        anchor="nw",
    )
    brand.create_rectangle(28, 245, 68, 248, fill="#cc735e", outline="")
    brand.create_text(
        28,
        272,
        text="一次验证，本地保存\n之后可直接管理微信草稿",
        fill="#d2d4d9",
        font=("Microsoft YaHei UI", 10),
        anchor="nw",
    )
    brand.create_text(
        28,
        414,
        text="60 秒动态验证码",
        fill="#aeb2bb",
        font=("Microsoft YaHei UI", 9),
        anchor="nw",
    )

    panel = tk.Frame(shell, bg="#f4f4f5", padx=38, pady=30)
    panel.pack(side="left", fill="both", expand=True)

    tk.Label(
        panel,
        text="连接云浪控制台",
        bg="#f4f4f5",
        fg="#25272c",
        font=("Microsoft YaHei UI", 18, "bold"),
        anchor="w",
    ).pack(fill="x")
    tk.Label(
        panel,
        text="在这里输入服务地址与当前验证码",
        bg="#f4f4f5",
        fg="#6e727a",
        font=("Microsoft YaHei UI", 9),
        anchor="w",
        pady=4,
    ).pack(fill="x")

    tk.Label(
        panel,
        text="服务端地址",
        bg="#f4f4f5",
        fg="#2f3238",
        font=("Microsoft YaHei UI", 9, "bold"),
        anchor="w",
        pady=7,
    ).pack(fill="x")
    server_entry = tk.Entry(
        panel,
        textvariable=server_value,
        font=("Segoe UI", 11),
        relief="flat",
        bd=0,
        bg="#ffffff",
        fg="#23252a",
        insertbackground="#4c638c",
        highlightthickness=1,
        highlightbackground="#d8d9de",
        highlightcolor="#64789e",
    )
    server_entry.pack(fill="x", ipady=9)

    code_heading = tk.Frame(panel, bg="#f4f4f5")
    code_heading.pack(fill="x", pady=(7, 0))
    tk.Label(
        code_heading,
        text="1 分钟验证码",
        bg="#f4f4f5",
        fg="#2f3238",
        font=("Microsoft YaHei UI", 9, "bold"),
        anchor="w",
    ).pack(side="left")
    show_code = tk.Checkbutton(
        code_heading,
        text="显示",
        variable=show_code_value,
        command=lambda: code_entry.configure(show="" if show_code_value.get() else "●"),
        bg="#f4f4f5",
        fg="#696d75",
        activebackground="#f4f4f5",
        activeforeground="#2f3238",
        selectcolor="#f4f4f5",
        font=("Microsoft YaHei UI", 9),
        relief="flat",
        bd=0,
        highlightthickness=0,
        cursor="hand2",
    )
    show_code.pack(side="right")
    code_entry = tk.Entry(
        panel,
        textvariable=code_value,
        show="●",
        font=("Segoe UI", 15),
        relief="flat",
        bd=0,
        bg="#ffffff",
        fg="#23252a",
        insertbackground="#4c638c",
        highlightthickness=1,
        highlightbackground="#d8d9de",
        highlightcolor="#64789e",
    )
    code_entry.pack(fill="x", ipady=8)

    status_panel = tk.Frame(
        panel,
        bg="#eef0f4",
        highlightthickness=1,
        highlightbackground="#d9dde5",
        padx=13,
        pady=9,
    )
    status_panel.pack(fill="x", pady=(14, 13))
    status_label = tk.Label(
        status_panel,
        textvariable=status_title_value,
        bg="#eef0f4",
        fg="#465a78",
        font=("Microsoft YaHei UI", 9, "bold"),
        anchor="w",
        justify="left",
    )
    status_label.pack(fill="x")
    status_detail_label = tk.Label(
        status_panel,
        textvariable=status_detail_value,
        bg="#eef0f4",
        fg="#687282",
        font=("Microsoft YaHei UI", 8),
        anchor="w",
        justify="left",
        wraplength=340,
    )
    status_detail_label.pack(fill="x", pady=(2, 0))

    def set_status(title: str, detail: str, tone: str) -> None:
        colors = {
            "safe": ("#eef0f4", "#d9dde5", "#465a78", "#687282"),
            "warning": ("#f8f0e2", "#ead7b3", "#85552f", "#795f49"),
            "error": ("#f9ebe8", "#edcbc4", "#a13e35", "#7b554f"),
            "success": ("#e9eef6", "#cbd6e8", "#3f5f8a", "#64748a"),
        }
        background, border, title_color, detail_color = colors[tone]
        status_title_value.set(title)
        status_detail_value.set(detail)
        status_panel.configure(bg=background, highlightbackground=border)
        status_label.configure(bg=background, fg=title_color)
        status_detail_label.configure(bg=background, fg=detail_color)

    def update_transport_notice(*_ignored: object) -> None:
        if server_value.get().strip().lower().startswith("http://"):
            set_status(
                "HTTP 连接提醒",
                "验证码和令牌将明文传输，仅限可信个人网络；建议配置 HTTPS。",
                "warning",
            )
        else:
            set_status("本地安全输入", "验证码不会显示在对话或命令行中。", "safe")

    def finish_error(message: str) -> None:
        code_value.set("")
        set_status("验证失败", message, "error")
        pair_button.configure(state="normal", text="验证并保存")
        code_entry.focus_set()

    def finish_success(saved_url: str, warning: str | None) -> None:
        code_value.set("")
        message = f"已连接 {saved_url}"
        if warning:
            message += f"\n提醒：{warning}"
        set_status("配对成功", message, "success")
        pair_button.configure(state="disabled", text="配对成功")
        root.after(1400, root.destroy)

    def submit(*_ignored: object) -> None:
        server = server_value.get().strip()
        code = code_value.get().strip()
        if not server or not code:
            finish_error("请填写服务端地址和验证码。")
            return
        pair_button.configure(state="disabled", text="正在验证...")
        set_status("正在验证", "正在与云浪控制台建立连接，请稍候。", "safe")

        def worker() -> None:
            try:
                saved_url, warning = _exchange_pairing(server, code)
            except Exception as exc:
                events.put(("error", str(exc), None))
            else:
                events.put(("success", saved_url, warning))

        threading.Thread(target=worker, daemon=True).start()

    def poll_events() -> None:
        try:
            kind, value, detail = events.get_nowait()
        except queue.Empty:
            root.after(100, poll_events)
            return
        if kind == "success":
            finish_success(str(value), str(detail) if detail else None)
        else:
            finish_error(str(value))
        root.after(100, poll_events)

    pair_button = tk.Button(
        panel,
        text="验证并保存",
        command=submit,
        bg="#34373d",
        fg="#ffffff",
        activebackground="#4b5059",
        activeforeground="#ffffff",
        disabledforeground="#c5c8ce",
        font=("Microsoft YaHei UI", 11, "bold"),
        relief="flat",
        cursor="hand2",
        pady=9,
        bd=0,
        highlightthickness=0,
    )
    pair_button.pack(fill="x")

    server_value.trace_add("write", update_transport_notice)
    code_entry.bind("<Return>", submit)
    update_transport_notice()
    if server_value.get():
        code_entry.focus_set()
    else:
        server_entry.focus_set()
    root.after(100, poll_events)

    root.update_idletasks()
    window_width = max(680, root.winfo_reqwidth())
    window_height = max(454, root.winfo_reqheight())
    brand.configure(height=window_height)
    x = max(0, (root.winfo_screenwidth() - window_width) // 2)
    y = max(0, (root.winfo_screenheight() - window_height) // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.deiconify()
    root.lift()
    root.attributes("-topmost", True)
    root.after(800, lambda: root.attributes("-topmost", False))
    root.mainloop()


def command_status(args: argparse.Namespace) -> None:
    config = _load_config()
    context = _authorized_request(args, "GET", "/api/v1/account")
    if not isinstance(context, dict) or not isinstance(context.get("account"), dict):
        raise ClientError("服务器未返回当前公众号上下文")
    _print_json(
        {
            "paired": True,
            "server_healthy": True,
            "console_url": config["console_url"],
            "active_account_id": context.get("active_account_id"),
            "account": context["account"],
        }
    )


def command_upload(args: argparse.Namespace, *, temporary: bool = False) -> None:
    files = [Path(value).expanduser().resolve() for value in args.files]
    body, content_type = _multipart(files, mode=None if temporary else args.mode)
    path = "/api/v1/temp-images" if temporary else "/api/v1/wechat-images"
    _print_json(
        _authorized_request(
            args, "POST", path, body=body, content_type=content_type
        )
    )


def command_draft_create(args: argparse.Namespace) -> None:
    payload = _load_payload(args.json, allow_content_file=True)
    payload.setdefault(
        "request_id",
        f"article-{datetime.now(UTC):%Y%m%d%H%M%S}-{uuid.uuid4().hex[:8]}",
    )
    _print_json(_authorized_request(args, "POST", "/api/v1/wechat-drafts", payload=payload))


def command_draft_list(args: argparse.Namespace) -> None:
    query = urlencode({"limit": args.limit, "offset": args.offset})
    _print_json(_authorized_request(args, "GET", f"/api/v1/wechat-drafts?{query}"))


def command_draft_get(args: argparse.Namespace) -> None:
    _print_json(_authorized_request(args, "GET", f"/api/v1/wechat-drafts/{args.id}"))


def command_draft_update(args: argparse.Namespace) -> None:
    payload = _load_payload(args.json, allow_content_file=True)
    _print_json(
        _authorized_request(
            args, "PUT", f"/api/v1/wechat-drafts/{args.id}", payload=payload
        )
    )


def command_draft_delete(args: argparse.Namespace) -> None:
    if not args.confirm:
        raise ClientError("删除草稿必须显式提供 --confirm")
    _print_json(_authorized_request(args, "DELETE", f"/api/v1/wechat-drafts/{args.id}"))


def command_wechat_list(args: argparse.Namespace) -> None:
    query = urlencode(
        {"offset": args.offset, "count": args.count, "no_content": str(args.no_content).lower()}
    )
    _print_json(
        _authorized_request(args, "GET", f"/api/v1/wechat-drafts/wechat-box?{query}")
    )


def command_wechat_get(args: argparse.Namespace) -> None:
    _print_json(
        _authorized_request(args, "GET", f"/api/v1/wechat-drafts/wechat-box/{args.media_id}")
    )


def command_wechat_update(args: argparse.Namespace) -> None:
    payload = _load_payload(args.json, allow_content_file=True)
    _print_json(
        _authorized_request(
            args,
            "PUT",
            f"/api/v1/wechat-drafts/wechat-box/{args.media_id}",
            payload=payload,
        )
    )


def command_wechat_delete(args: argparse.Namespace) -> None:
    if not args.confirm:
        raise ClientError("删除微信草稿必须显式提供 --confirm")
    _print_json(
        _authorized_request(
            args, "DELETE", f"/api/v1/wechat-drafts/wechat-box/{args.media_id}"
        )
    )


def command_temp_list(args: argparse.Namespace) -> None:
    query = urlencode({"limit": args.limit})
    _print_json(_authorized_request(args, "GET", f"/api/v1/temp-images?{query}"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="云浪控制台轻量客户端")
    parser.add_argument("--account-id", type=int, help="指定配对用户名下的公众号 ID")
    commands = parser.add_subparsers(dest="command", required=True)

    pair = commands.add_parser("pair", help="使用一次性验证码配对")
    pair.add_argument("--server", required=True, help="云浪控制台根地址")
    pair.set_defaults(handler=command_pair)

    pair_ui = commands.add_parser("pair-ui", help="打开本地安全配对窗口")
    pair_ui.add_argument("--server", help="预填云浪控制台根地址")
    pair_ui.set_defaults(handler=command_pair_ui)

    status = commands.add_parser("status", help="验证本地配对")
    status.set_defaults(handler=command_status)

    image_upload = commands.add_parser("image-upload", help="上传微信公众号图片")
    image_upload.add_argument("--mode", choices=("article", "material", "both"), required=True)
    image_upload.add_argument("files", nargs="+")
    image_upload.set_defaults(handler=lambda args: command_upload(args, temporary=False))

    temp_upload = commands.add_parser("temp-upload", help="上传服务器临时图片")
    temp_upload.add_argument("files", nargs="+")
    temp_upload.set_defaults(handler=lambda args: command_upload(args, temporary=True))

    temp_list = commands.add_parser("temp-list", help="列出服务器临时图片")
    temp_list.add_argument("--limit", type=int, default=500)
    temp_list.set_defaults(handler=command_temp_list)

    draft_create = commands.add_parser("draft-create", help="创建微信草稿")
    draft_create.add_argument("--json", required=True)
    draft_create.set_defaults(handler=command_draft_create)

    draft_list = commands.add_parser("draft-list", help="列出本地草稿任务")
    draft_list.add_argument("--limit", type=int, default=100)
    draft_list.add_argument("--offset", type=int, default=0)
    draft_list.set_defaults(handler=command_draft_list)

    draft_get = commands.add_parser("draft-get", help="读取并核对本地草稿任务")
    draft_get.add_argument("id", type=int)
    draft_get.set_defaults(handler=command_draft_get)

    draft_update = commands.add_parser("draft-update", help="修改本地草稿任务")
    draft_update.add_argument("id", type=int)
    draft_update.add_argument("--json", required=True)
    draft_update.set_defaults(handler=command_draft_update)

    draft_delete = commands.add_parser("draft-delete", help="删除本地草稿任务")
    draft_delete.add_argument("id", type=int)
    draft_delete.add_argument("--confirm", action="store_true")
    draft_delete.set_defaults(handler=command_draft_delete)

    wechat_list = commands.add_parser("wechat-list", help="列出真实微信草稿箱")
    wechat_list.add_argument("--offset", type=int, default=0)
    wechat_list.add_argument("--count", type=int, default=20)
    wechat_list.add_argument("--no-content", action="store_true")
    wechat_list.set_defaults(handler=command_wechat_list)

    wechat_get = commands.add_parser("wechat-get", help="按 media_id 读取微信草稿")
    wechat_get.add_argument("media_id")
    wechat_get.set_defaults(handler=command_wechat_get)

    wechat_update = commands.add_parser("wechat-update", help="按 media_id 修改微信草稿")
    wechat_update.add_argument("media_id")
    wechat_update.add_argument("--json", required=True)
    wechat_update.set_defaults(handler=command_wechat_update)

    wechat_delete = commands.add_parser("wechat-delete", help="按 media_id 删除微信草稿")
    wechat_delete.add_argument("media_id")
    wechat_delete.add_argument("--confirm", action="store_true")
    wechat_delete.set_defaults(handler=command_wechat_delete)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        args.handler(args)
        return 0
    except ClientError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
