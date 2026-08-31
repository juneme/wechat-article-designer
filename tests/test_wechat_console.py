from __future__ import annotations

import argparse
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "wechat_console.py"
SPEC = importlib.util.spec_from_file_location("wechat_console", SCRIPT_PATH)
assert SPEC and SPEC.loader
wechat_console = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wechat_console)


class AuthorizedRequestTests(unittest.TestCase):
    def request_account_id(self, explicit_account_id: int | None) -> int | None:
        args = argparse.Namespace(account_id=explicit_account_id)
        config = {
            "console_url": "https://console.example",
            "client_token": "test-token",
            "active_account_id": 2,
        }
        with (
            patch.object(wechat_console, "_load_config", return_value=config),
            patch.object(wechat_console, "_request", return_value={}) as request,
        ):
            wechat_console._authorized_request(args, "GET", "/test")
        return request.call_args.kwargs["account_id"]

    def test_uses_paired_account_by_default(self) -> None:
        self.assertEqual(self.request_account_id(None), 2)

    def test_explicit_account_overrides_paired_account(self) -> None:
        self.assertEqual(self.request_account_id(7), 7)


if __name__ == "__main__":
    unittest.main()
