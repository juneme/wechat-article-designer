# Direct Publishing Through the WeChat Console API

Use this reference only when article assets or a finished article must pass through the configured console server. The server owns WeChat credentials and WeChat API interaction; this Skill only sends local files and final article data to the server.

Use `references/article-workspaces.md` for the local directory and revision contract. Clipboard delivery is not part of this workflow.

## Route selection

For an ordinary request to create or substantially redesign an article, resolve delivery before production:

1. Check whether `WECHAT_CONSOLE_URL`, `WECHAT_IMAGE_API_KEY`, and `WECHAT_PUBLISH_API_KEY` are all non-empty without printing their values.
2. When all three are present, run `python scripts/wechat_console_api.py status`.
3. Treat direct draft as ready only when the command succeeds, `console_configured`, both key flags, and `server_healthy` are all true.
4. Use direct draft by default when ready. A user request for preview-only, HTML-only, preparation-only, or stop-before-draft overrides this default.
5. When configuration is incomplete or status is unhealthy or unreachable, use the local-preview route; do not attempt partial direct delivery.

This route selection is the user's delivery default for this Skill. It authorizes one staged draft after all design and validation gates pass; it never authorizes publication or mass sending.

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

## 1. Prepare Body Images

Inspect and finalize images before release. If a required image does not exist, generate it first with an available image capability without fabricating evidence. Store each generated or supplied file under the workspace `assets/` directory and register it in `design-contract.json` with a unique `name`, `placement`, `required`, `source_path`, and state of `generated-local` or `supplied-local`.

```json
{
  "name": "lead-image",
  "reader_job": "Establish the literal subject before the first section.",
  "authority": "Illustrative only; not evidence of a real event.",
  "order": 1,
  "crop": "natural",
  "caption": "N/A: the surrounding body supplies the context.",
  "placement": "body",
  "required": true,
  "source_path": "lead.jpg",
  "state": "generated-local"
}
```

Bind the body position with the same identifier. Before upload, use the controlled placeholder scheme rather than a local filesystem path:

```html
<img data-media-id="lead-image" data-media-crop="natural" src="wechat-media://lead-image" alt="" style="display:block;width:100%;height:auto;" />
```

The release command uploads local media, normalizes the returned WeChat article URL to HTTPS, replaces exactly one matching `<img data-media-id>`, and marks the contract asset hosted. It stops the direct route on a missing or duplicate marker. Do not use a local path, temporary URL, or non-WeChat host in the fragment.

## 2. Prepare the Cover

Generate or finalize the 2.35:1 cover, record `crop: "aspect-ratio:2.35"` and `required: true`, and register it as `placement: "cover"` with its workspace-relative `source_path`. Keep that local source even after upload or when reusing a permanent `thumb_media_id`; direct delivery requires the asset record and reads PNG, JPEG, GIF, or WebP dimensions before any submission. A missing source or ratio mismatch returns the image-generation gate. The cover does not appear in the fragment and therefore has no `data-media-id` marker there.

The release command uploads it as permanent material and writes the returned `media_id` to `article.json.thumb_media_id`. A cover URL is not a valid replacement.

## 3. Build the Article Workspace

Keep the final fragment, metadata, media map, and `PLANNED` contract in one workspace. Do not manually promote the contract to `READY`; the release command generates the exact fragment binding after every audit passes.

```powershell
python scripts/release_article.py deliver '.\articles\日期_标题'
```

This resolves backend health, validates the design contract, audits the local fragment plus title, author, and digest before any upload, uploads prepared local media, audits the exact hosted fragment, updates `article.json.content`, keeps the direct-draft route from generating a local preview, rotates `request_id` only for changed payload data, stores a revision snapshot, and creates one new draft automatically.

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

The following read-only diagnostic remains available, but it is not a release substitute:

```powershell
python scripts/wechat_console_api.py validate-draft --article '.\article.json'
```

Validation enforces the server contract: title up to 32 characters, author up to 16, digest up to 120, content under 20,000 characters and 1 MB, prohibited active HTML, comment flags of `0` or `1`, and HTTPS body images hosted on `mmbiz.qpic.cn`.

SVG components use the same article validation and draft path. Do not create an SVG evidence file or run a separate SVG production audit.

## 4. Create the Draft

`release_article.py deliver` is the only mutating entrypoint. It creates a new draft automatically after all gates succeed without a second confirmation. Revisions also create a new draft until the client implements draft updates:

```powershell
python scripts/release_article.py deliver '.\articles\日期_标题'
```

Success returns a draft `media_id`, the `request_id`, a `cached` flag, and server validation counts. A cached response is a successful idempotent replay, not a second draft. Creating a draft does not publish or mass-send the article; the user reviews the final draft and decides any later publication action in the WeChat backend.

Use `--preview-only` for preview-only requests. Low-level draft creation and image-upload CLI commands are unavailable so contract, audit, synchronization, route, and idempotency gates cannot be bypassed.

## Failure Handling

- Exit code `0`: a draft or permitted local preview was delivered.
- Exit code `2`: delivery is blocked or a draft result is ambiguous; inspect the structured result and never retry an ambiguous request.
- Exit code `3`: required image generation must be attempted before delivery may continue.

Check the HTTP status and error message. `401` normally means the corresponding bearer key is missing or wrong, `409` means a request ID was reused for different article data, `422` means the submitted contract is invalid, and `502` or `503` means the server cannot currently complete the WeChat operation.

Never automatically retry `create-draft` after a timeout, `502`, `pending`, `unknown`, or any response marked `ambiguous`. Do not generate a fallback preview in this state. The user inspects the real draft box because creation may have completed before the response was lost. A confirmed `created` response is idempotently cached; an `unknown` result deliberately blocks reuse of the same `request_id`.

The release command switches once to local preview when configuration, health, upload, cover preparation, or route-specific draft validation fails before draft creation. A required missing image first returns `image-generation-required` plus an `attempt_id`; after the available image capability actually fails, rerun with both `--image-generation-attempt-id <id>` and `--image-generation-failed "reason"` to permit preview fallback. A definite `401` or `422`, or a `503` carrying `draft_created:false`, creates the preview automatically. Local article audit failures block before material upload. Partially uploaded WeChat materials from upload-specific or hosted-result failures are left for the user to manage. After a draft request becomes ambiguous, the persisted workspace lock reports `do_not_retry` and never switches routes. Resolve it only after inspecting the draft box:

```powershell
python scripts/article_workspace.py resolve-draft '.\articles\日期_标题' --outcome created
# or, only after confirming absence:
python scripts/article_workspace.py resolve-draft '.\articles\日期_标题' --outcome not-created
```
