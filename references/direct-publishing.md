# Direct Draft Delivery

Use this reference when a finished article should pass through the configured console server. The server owns WeChat credentials and API calls. The Skill sends prepared local images and final draft data; it never receives AppSecret and never publishes or mass sends.

## Route health

The direct route requires all three environment variables:

```text
WECHAT_CONSOLE_URL
WECHAT_IMAGE_API_KEY
WECHAT_PUBLISH_API_KEY
```

Do not print their values. Run:

```powershell
python scripts/wechat_console_api.py status
```

The route is healthy only when the command succeeds, both key flags are true, and `server_healthy` is true. Missing configuration or any failed health condition immediately selects local preview. A user preview-only request always selects local preview.

## Prepare media

Store local files under the workspace `assets/` directory. Record them in `release-manifest.json`; do not put visual design rules there.

```json
{
  "name": "lead-image",
  "placement": "body",
  "required": true,
  "state": "generated-local",
  "source_path": "lead.png",
  "remote_ref": ""
}
```

Allowed states are `placeholder`, `generated-local`, `supplied-local`, and `hosted`.

For a local body image, place exactly one matching marker in the fragment:

```html
<img data-media-id="lead-image" src="wechat-media://lead-image" alt="" style="display:block;width:100%;height:auto;" />
```

Release uploads body images in article mode, requires the returned HTTPS `article_url`, and replaces the temporary source. The final direct payload may contain only WeChat-hosted HTTPS body images.

The direct route also requires one PNG, JPEG, GIF, or WebP cover with an actual 2.35:1 ratio. Register it as `placement:"cover"`, keep its workspace-relative source after upload, and do not add a body marker. Release uploads it in material mode and stores the permanent `media_id` as `article.json.thumb_media_id`.

Generated imagery may illustrate or establish atmosphere, but cannot prove a certification, official document, seal, logo, real event, real person, product result, or institutional status.

## Missing images

When a required local source, body mapping, or direct cover is missing or invalid, release returns exit code `3` with:

- `status: image-generation-required`;
- a list of blockers;
- a unique `attempt_id` bound to the current blocker set.

Invoke the available image capability immediately, save the result under `assets/`, update the corresponding manifest item, and rerun release. Do not ask for a second confirmation.

Only after an actual image-generation failure may local preview be authorized with both flags:

```powershell
python scripts/release_article.py deliver WORKSPACE --image-generation-attempt-id ID --image-generation-failed "reason"
```

An invented, stale, or unrelated ID is rejected.

## Release entrypoint

The only mutating client entrypoint is:

```powershell
python scripts/release_article.py deliver WORKSPACE
```

The low-level client exposes health and local validation diagnostics but does not allow a caller to bypass workspace synchronization, postflight audits, route selection, or submission locking.

Release performs this sequence:

1. load the fragment, metadata, operational media, and submission state;
2. block an unresolved `submitting` or `ambiguous` request;
3. resolve backend health and user preview override;
4. audit local publishable content before external mutation;
5. upload prepared body and cover media on the direct route;
6. audit the exact hosted result;
7. synchronize body, route, preview state, request ID, assets, and revision snapshot transactionally;
8. validate the final draft payload;
9. store `submitting` before the request leaves the machine;
10. create one new draft or persist the exact failure state.

No design plan, type-role matrix, palette registration, module marker, or design-contract status participates in this sequence.

## Draft payload

`article.json` uses the server contract:

```json
{
  "request_id": "article-unique-revision-id",
  "title": "Article title",
  "author": "",
  "digest": "",
  "content": "<section>...</section>",
  "content_source_url": "",
  "thumb_media_id": "PERMANENT_COVER_MEDIA_ID",
  "need_open_comment": 0,
  "only_fans_can_comment": 0
}
```

Validation enforces title up to 32 characters, author up to 16, digest up to 120, content under 20,000 characters and 1 MB, allowed comment flags, no active HTML, a permanent cover ID, and WeChat-hosted HTTPS body images.

## Failure routing

Before draft submission begins, configuration failure, unhealthy status, image upload failure, hosted-result validation failure, local draft validation failure, `401`, `422`, or a confirmed `503` with `draft_created:false` switches to local preview. Old `preview.html` is physically removed on a successful direct route and regenerated on fallback. Partially uploaded WeChat materials remain under the user's control.

Local audit errors block both routes because preview is not a way to deliver unsafe or unreadable content.

After the draft request begins, a timeout, `502`, pending, unknown, malformed success response, process interruption, or any unconfirmed result is ambiguous. Never retry automatically and never switch to preview. The persisted lock protects against duplicate drafts.

The user checks the real draft box and then records the outcome:

```powershell
python scripts/article_workspace.py resolve-draft WORKSPACE --outcome created
python scripts/article_workspace.py resolve-draft WORKSPACE --outcome not-created
```

## Exit behavior

- `0` with `draft-created`: draft creation was confirmed or the same confirmed result was reused.
- `0` with `local-preview`: fallback or preview-only delivery succeeded.
- `2` with `ambiguous`: do not retry; user inspection is required.
- `2` with `blocked`: a local hard gate or invalid workspace stopped delivery.
- `3` with `image-generation-required`: generate the specified assets before continuing.
