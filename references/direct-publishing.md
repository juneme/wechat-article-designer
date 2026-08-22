# Direct Publishing Through the WeChat Console API

Use this reference only when article assets or a finished article must pass through the configured console server. The server owns WeChat credentials and WeChat API interaction; this Skill only sends local files and final article data to the server.

Use `references/article-workspaces.md` for the local directory and revision contract. Clipboard delivery is not part of this workflow.

## Configuration

Read configuration from the process environment:

```text
WECHAT_CONSOLE_URL=https://console.example.test:8791
WECHAT_IMAGE_API_KEY=image-api-bearer-key
WECHAT_PUBLISH_API_KEY=draft-api-bearer-key
```

`WECHAT_IMAGE_API_KEY` must contain the same secret as the console server's `AI_API_KEY`. `WECHAT_PUBLISH_API_KEY` must contain the same secret as the server's `PUBLISH_API_KEY`. Distinct client-side names clarify key purpose without creating new server credentials.

Never store these values in the Skill, article JSON, generated HTML, shell history examples, screenshots, or published output. The client accepts both HTTP and HTTPS remote console URLs. HTTP supports deployments without a domain or SSH tunnel but sends bearer keys and article data without transport encryption. Keep the structured warning in command output and enable HTTPS whenever available.

Check connectivity without exposing key values:

```powershell
python scripts/wechat_console_api.py status
```

The command reports whether each local key is configured, but never prints the keys. For a remote HTTP URL, a successful result includes a `warnings` entry instead of blocking the request.

## 1. Upload Body Images

Inspect and finalize images before upload. One command accepts at most 20 files and sends each file separately to keep memory use bounded.

```powershell
python scripts/wechat_console_api.py upload-images --mode article '.\images\lead.jpg' '.\images\detail.png'
```

Read each result by `source_path`, not by guessing from upload order. A successful item has `status: "complete"` and an `article_url`. Stop if the command returns a nonzero exit code, `error_count` is nonzero, or an intended item lacks `article_url`.

The client upgrades an `http://mmbiz.qpic.cn/...` article URL returned by WeChat to the same HTTPS host, path, and query before reporting success. Insert the normalized `article_url` into the final article:

```html
<img src="https://mmbiz.qpic.cn/..." alt="" style="display:block;width:100%;height:auto;" />
```

Do not use `material_url`, a local path, a temporary URL, or a non-WeChat host for body images. Do not retain a manual 1px image anchor inside a direct-publishing image frame.

## 2. Upload the Cover

Generate or finalize the 2.35:1 cover first, then upload the cover as permanent material:

```powershell
python scripts/wechat_console_api.py upload-cover '.\cover.png'
```

The command returns `media_id`. Use the returned value as `thumb_media_id`; a cover URL is not a valid replacement.

## 3. Build and Validate Article JSON

Synchronize the workspace after the final fragment and metadata changes:

```powershell
python scripts/article_workspace.py sync '.\articles\日期_标题'
```

This updates `article.json.content`, regenerates the script-free preview, rotates `request_id` only for changed payload data, and stores a revision snapshot.

Write UTF-8 JSON using this exact contract:

```json
{
  "request_id": "article-example-001",
  "title": "文章标题",
  "author": "作者",
  "digest": "文章摘要",
  "content": "<section>最终 HTML</section>",
  "content_source_url": "",
  "thumb_media_id": "COVER_MEDIA_ID",
  "need_open_comment": 0,
  "only_fans_can_comment": 0
}
```

`request_id` is the idempotency key. Reuse the key only for byte-equivalent article data. Generate a new request ID after any article-data change following an earlier submission.

Validate locally without contacting the draft endpoint:

```powershell
python scripts/wechat_console_api.py validate-draft --article '.\article.json'
```

Validation enforces the server contract: title up to 32 characters, author up to 16, digest up to 120, content under 20,000 characters and 1 MB, prohibited active HTML, comment flags of `0` or `1`, and HTTPS body images hosted on `mmbiz.qpic.cn`.

SVG components use the same article validation and draft path. Do not create an SVG evidence file or run a separate SVG production audit.

## 4. Create the Draft

`create-draft` is the only mutating command in the direct-publishing workflow. For full direct publishing or delivery to the WeChat draft box, run the command automatically after `validate-draft` succeeds without a second confirmation:

```powershell
python scripts/wechat_console_api.py create-draft --article '.\article.json'
```

Success returns a draft `media_id`, the `request_id`, a `cached` flag, and server validation counts. A cached response is a successful idempotent replay, not a second draft. Creating a draft does not publish or mass-send the article; final publication remains a separate manual or scan-confirmed action in the WeChat backend.

Do not run `create-draft` for preview-only, HTML-only, image-upload-only, or preparation-only requests. For the full direct-publishing workflow, proceed automatically unless a stop before draft creation is explicitly requested.

## Failure Handling

- Exit code `0`: operation completed successfully.
- Exit code `1`: configuration, local validation, transport, HTTP, or response-contract error. A structured error is written to stderr.
- Exit code `2`: one or more image items failed, or draft creation is still `pending`. The full structured response remains on stdout.

Check the HTTP status and error message. `401` normally means the corresponding bearer key is missing or wrong, `409` means a request ID was reused for different article data, `422` means the submitted contract is invalid, and `502` or `503` means the server cannot currently complete the WeChat operation.

Never automatically retry `create-draft` after a timeout, `502`, `pending`, or `unknown` result. First inspect the console operation state and the real WeChat draft box because draft creation may have completed before the response was lost. A confirmed `created` response is idempotently cached; an `unknown` result deliberately blocks reuse of the same `request_id`.
