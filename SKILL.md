---
name: wechat-article-designer
description: Create, revise, troubleshoot, and deliver mobile-first WeChat Official Account (微信公众号) articles. Use for original article design, copy or layout revision, WeChat editor compatibility, image placeholders or uploaded assets, covers, audience-boundary and risk audits, console API image uploads, and validated delivery to the WeChat draft box.
---

# WeChat Article Designer

Produce audience-facing WeChat article fragments and, when explicitly requested, deliver validated drafts through the configured console API.

## Operating contract

1. Choose the delivery route before creating assets or calling an API.
2. Keep source instructions and workflow context outside publishable copy.
3. Produce a WeChat article fragment, not a web page. Keep all required styling inline.
4. Preserve supplied facts, brand rules, assets, and approved claims. Do not invent institutional evidence or business data.
5. Use the real WeChat editor and phone preview as the publishing source of truth; browser rendering is only a preflight.
6. Treat draft creation as staging without authorization for mass publication.

## Route the request

| Request | Route |
|---|---|
| New full article | Run original-style synthesis, then the article production workflow. |
| Revision or troubleshooting | Preserve the current visual register unless a redesign is requested; diagnose the specific failure before editing. |
| Explicit named template | Load only the named route and adapt the structure to the final copy, assets, and risk profile. |
| HTML, preview, or manual editor delivery | Use hosted images or manual placeholders. Do not call `create-draft`. |
| Draft-box delivery | Read `references/direct-publishing.md`, complete every validation gate, then create the draft without asking for a second confirmation. |

Do not show a template picker unless style browsing is requested.

## Produce the article

### 1. Establish the brief

Identify the target reader, narrator, desired action, information density, emotional register, image roles, factual evidence, brand names, palette source, and industry risk profile. Ask only for information that cannot be inferred safely.

### 2. Set the design direction

For a new article:

1. Read `references/original-style-synthesis.md` and `GALLERY.md`.
2. Define the visual thesis, palette behavior, opener, section rhythm, edge geometry, image behavior, content-native motif, closing device, and delivery mode.
3. Load two to four relevant DNA routes by dimension. Do not copy one route's full DOM or section order.
4. Name the synthesized style in one short line and proceed.

For a revision, compare the requested change with the existing design fingerprint. Keep unrelated structure and copy stable.

### 3. Write for the reader

- Make the article understandable as a standalone publication.
- Remove source-request echoes, workflow narration, validation status, local paths, and approval language.
- For AI or Codex tutorials, use generic reusable examples rather than task-specific wording.
- Run `scripts/audit_audience_boundary.py` on the final HTML or article JSON. Resolve every finding before delivery.

### 4. Build the fragment

- Wrap the final body with `<!-- 微信公众号复制开始 -->` and `<!-- 微信公众号复制结束 -->`.
- Prefer `section`, `p`, and `span` flow. Use `img` only for final hosted article images.
- Sample a supplied visual before choosing colors. Assign the sampled light field, readable dark, primary, and limited accents by role.
- Choose Steady or Creative mode from `references/creative-css-capabilities.md`; preserve supported expressive CSS.
- Use `references/snippets.md` for image slots, compact fact flows, captions, risk substitutions, troubleshooting, and the pre-publish checklist.

### 5. Route images correctly

For manual editor delivery:

- Inspect every source image and assign a narrative role.
- Use the editable-paragraph placeholder from `references/snippets.md`: the frame owns height and styling; one direct-child 1px `p` containing `&nbsp;` provides the caret.
- Keep filename maps and replacement instructions outside the editable image container.
- Prefer a single bitmap or single-column flow for dense repeated people or items. Use manual swipe only when the exact final block can be tested in WeChat.

For direct draft delivery:

- Finalize images before upload.
- Upload body images in `article` mode and insert the returned HTTPS `article_url` values.
- Upload the 2.35:1 cover separately and use the permanent `media_id` as `thumb_media_id`.
- Do not leave manual placeholder anchors or local paths in the final HTML.

Generated illustrations may support a story but may not serve as proof of a certification, designation, official document, seal, logo, or real-world event.

## Direct draft workflow

Read `references/direct-publishing.md` before any console command.

1. Confirm configuration of `WECHAT_CONSOLE_URL`, `WECHAT_IMAGE_API_KEY`, and `WECHAT_PUBLISH_API_KEY` without printing secret values.
2. Run `python scripts/wechat_console_api.py status`.
3. Upload final body images with `upload-images --mode article`; stop on a nonzero exit code, an incomplete item, or a missing `article_url`.
4. Build the final HTML from the returned image mapping.
5. Upload the cover with `upload-cover` and store the returned `media_id`.
6. Build UTF-8 article JSON with a new idempotent `request_id` for the exact payload.
7. Run the audience audit and `validate-draft`; fix every error.
8. For draft-box delivery, run `create-draft` immediately after validation.
9. Report the draft `media_id`, `request_id`, `cached` flag, validation counts, and any transport warning.

Never automatically retry `create-draft` after a timeout, `502`, `pending`, or `unknown` result. Inspect the console operation state and the real draft box first because WeChat may have created the draft before the response was lost.

## Compatibility contract

These rules apply to every final fragment:

- No scripts, event handlers, external CSS, `<style>`, web fonts, iframes, objects, or embeds.
- No local or relative image paths.
- No `position:absolute`, `position:relative`, or CSS Grid without exact-path real-editor evidence.
- No table layout by default. Replace unstable tables with flow content.
- Keep fixed widths within the mobile column and maintain deliberate horizontal baselines.
- Keep the first-screen spacing intentional; do not compensate for editor spacing with stacked empty wrappers.
- Balance opening and closing counts for `section`, `p`, and `span`.

Steady mode uses inline flow, solid fills, borders, alpha colors, radii, `inline-block`, compact flex, and verified manual overflow strips. Creative mode may add controlled gradients and shadows only with solid fallbacks and nonessential effects. The article must remain readable if those effects are removed.

## Quality gates

Before delivery:

1. Run the audience-boundary audit.
2. Run the checklist in `references/snippets.md` and the mode rules in `references/creative-css-capabilities.md`.
3. Check for active HTML, local paths, unverified positioning, Grid, fragile tables, unmatched tags, and unintended horizontal overflow.
4. Review every promise, outcome claim, institutional term, incentive, brand name, and generated evidence image.
5. Verify approximately 320px, 375px, and 390px widths. Check image loading, long-word wrapping, content order, and outer overflow.
6. For Creative mode or fragile editor patterns, test the exact final fragment in the real WeChat phone preview when available.
7. For direct delivery, require HTTPS `mmbiz.qpic.cn` body images, a permanent cover `media_id`, and a successful `validate-draft` result.

## Resource router

Load only what the current route needs:

- Original full article: `references/original-style-synthesis.md` and `GALLERY.md`.
- CSS support, Steady/Creative modes, and originality comparisons: `references/creative-css-capabilities.md`.
- Reusable HTML, image slots, risk substitutions, troubleshooting, and final checklist: `references/snippets.md`.
- Console upload and draft creation: `references/direct-publishing.md`.
- Public-interest or institutional work: `references/modern-institutional-public-interest.md`.
- Recruitment routes: `references/soft-app-recruitment.md` or `references/dopamine-editorial-recruitment.md`.
- Artbook routes: `references/paper-cut-artbook.md`, `references/contour-index.md`, `references/chromatic-folio.md`, or `references/paper-cut-original-series.md`.
- Cinematic composition: `references/still-frame-cinema.md`.
- Browser-only capability research: `references/progressive-enhancement-lab.md`; keep experiments outside the publishable fragment.
- Baked image frame: run `scripts/bake_image_frame.py --help`.
- Deterministic cover generation: run `scripts/generate_wechat_cover.py --help`.

## Handoff

For HTML or manual delivery, provide the final fragment, asset map, and minimal insertion instructions. For draft delivery, report the confirmed API result and state that final publication remains in the WeChat backend.

Exclude design synthesis, internal reasoning, source cleanup, local validation, and workflow history from the published article.
