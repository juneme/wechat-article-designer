# 云浪控制台客户端

## Pairing and startup check

Run `status` at the start of every article task while writing begins. If the client is not paired, open the local pairing window:

```powershell
pythonw scripts/wechat_console.py pair-ui --server http://SERVER:8791
```

The user enters the one-minute verification code only in this local window. The code is masked, never sent through chat or placed on the command line, and is discarded after the exchange. The issued client token is saved without being displayed.

The terminal command remains available for environments without a desktop UI:

The server URL is supplied once. Run:

```powershell
python scripts/wechat_console.py pair --server http://SERVER:8791
```

Enter the one-minute verification code at the hidden prompt. The code is single-use. The response's unified client token is saved under `%USERPROFILE%\.codex\yunoe\client.json`; it is never printed.

Each successful pairing creates a separate client token bound to the console user, not to one official account. Pairing in Codex, Trae, or another client does not revoke tokens already issued to the same user; the 16 most recently used tokens remain valid. Switching the active official account does not require pairing again: commands without `--account-id` follow the server's current account, and `status` reads that account live from the server. A password change revokes all browser sessions and client tokens for that user. Run `status` after a password change and pair each required client again.

HTTP is supported for a trusted personal deployment, but both verification code and token travel in plaintext. Prefer HTTPS on untrusted networks.

## Commands

```text
status
pair-ui --server URL
image-upload --mode article|material|both FILE [FILE ...]
temp-upload FILE [FILE ...]
temp-list [--limit 500]
draft-create --json FILE
draft-list [--limit 100] [--offset 0]
draft-get ID
draft-update ID --json FILE
draft-delete ID --confirm
wechat-list [--offset 0] [--count 20] [--no-content]
wechat-get MEDIA_ID
wechat-update MEDIA_ID --json FILE
wechat-delete MEDIA_ID --confirm
```

Pass `--account-id ID` before the command only for a one-command override to another official account owned by the paired user. Never infer this flag from locally saved pairing data.

Draft create JSON accepts `content_file`; paths are resolved relative to the JSON file. Update JSON contains only changed article fields.

## Safety

- Never print, log, paste, or commit the saved client token.
- Never place a verification code on the command line.
- Do not automatically retry writes after a timeout or 5xx.
- Keep the same generated `request_id` when checking an uncertain create. Do not create a new one until the real draft box has been inspected.
- Deletion requires `--confirm`. Local-task deletion removes both the WeChat draft and local record. Direct WeChat deletion uses `media_id` and also removes a matching local record.
- WeChat has no deletion API for article-image URLs. Deleting a local history item cannot invalidate such a URL.
