---
name: wechat-article-designer
description: Write, art-direct, compose, validate, version, and deliver original mobile-first WeChat Official Account (微信公众号) articles without template or design-contract gates, including expressive inline layouts, Chinese typography, images, SVG/SMIL scenes, editor compatibility, local preview, and configured draft-box delivery.
---

# WeChat Article Designer

Write and design one audience-facing WeChat article as an original composition. Let the subject, evidence, voice, images, and reading rhythm determine the visual language. Do not select a theme, reuse a fixed page template, or compose toward a machine design score.

## Operating boundary

1. Own both writing and design unless the user explicitly supplies locked copy.
2. Infer missing subjective choices and finish a coherent result before asking for preferences. Never invent names, dates, credentials, institutional claims, evidence, or other factual details.
3. Create or reuse one article workspace. Keep source instructions, local paths, design reasoning, audit output, experiments, and conversation text outside publishable copy.
4. Resolve delivery before production. When all three console variables exist and `status` confirms both keys plus a healthy server, prepare a direct draft route. Otherwise prepare local preview. A user request for preview-only, HTML-only, or stop-before-draft overrides the backend.
5. Produce an HTML fragment with inline styles. The real WeChat editor and phone preview remain the rendering authority.
6. Draft creation is authorized staging when the backend is healthy. It never authorizes publication or mass sending.
7. New articles and substantial redesigns use the complete creative workflow below. Minor corrections preserve the established editorial and visual system.

There is no Creative/Steady split and no mandatory design contract. `design-contract.json`, `data-type-role`, `data-module-id`, `data-density`, `data-spacing-role`, `data-geometry-role`, palette roles, effect quotas, fixed type roles, and a `PLANNED`/`READY` state are not release requirements. Legacy workspaces may retain those files as private history.

## Read only what the task needs

| Task | Reference |
|---|---|
| New article or substantial redesign | `references/editorial-writing-grammar.md`, `references/article-design-synthesis.md`, `references/modular-composition-system.md`, `references/typography-system.md`, `references/design-grammar.md` |
| Inline CSS choice or fallback | `references/css-capabilities.md` |
| Reusable primitive | `references/snippets.md` |
| Workspace, revision, or migration | `references/article-workspaces.md` |
| SVG scene or motion | `references/svg-design-genes.md` |
| Learn from a visual source | `references/design-learning-workflow.md` |
| Draft-box delivery | `references/direct-publishing.md` |

For an explicit visual reference, preserve its visual thesis, hierarchy, rhythm, spatial relationships, and signature moves as closely as the content and WeChat surface allow. Rebuild it for the final evidence and copy; do not flatten it into the house examples.

## Complete creative workflow

### 1. Resolve route and workspace

Check `WECHAT_CONSOLE_URL`, `WECHAT_IMAGE_API_KEY`, and `WECHAT_PUBLISH_API_KEY` without printing their values. If all exist, run:

```powershell
python scripts/wechat_console_api.py status
```

Use direct draft only when the command succeeds, both key flags are true, and `server_healthy` is true. Create the workspace with `--no-preview` for that route; otherwise create it with preview enabled. A failed or missing backend immediately selects local preview.

```powershell
python scripts/article_workspace.py create --title "Article title" --date YYYY-MM-DD
```

### 2. Establish the editorial core

Privately identify the reader situation, literal topic, narrator, central friction, defensible judgment, evidence boundary, reader gain, desired action, information density, emotional register, image roles, and brand constraints. Write the complete article before polishing visual fragments. Make it understandable without the request or conversation that produced it.

Use headings, lists, comparisons, quotations, data, and emphasis only when those relationships exist in the content. Remove agent offers, approval requests, validation narration, file instructions, source-request echoes, and other workflow language.

### 3. Discover the article's visual idea

Read the content for visual material: scale, tension, repetition, sequence, texture, season, place, movement, contrast, objects, evidence, and emotional turns. When comparison helps, sketch two or three lightweight directions privately and choose the strongest. Do not ask the user to approve intermediate directions.

Define a visual thesis and one or more content-native motifs, then compose. This is creative guidance, not a form to complete. A strong article may be quiet or exuberant; it may use open prose, editorial typography, posters, panels, borders, gradients, shadows, irregular rhythm, multiple SVG scenes, image-led pacing, or none of them. Use what the article needs. There is no component quota and no requirement to justify decorative decisions to a validator.

### 4. Build the publishable fragment

- Wrap the exact publishable markup with `<!-- 微信公众号复制开始 -->` and `<!-- 微信公众号复制结束 -->`.
- Use inline styles and mobile-first flow. Do not add a document wrapper, style block, script, web font, or external stylesheet.
- Treat the 320px content column as a hard rendered-width ceiling. SVG `viewBox` coordinates are not CSS pixels; responsive SVG may use `width:100%`.
- Make continuous prose comfortable to read. The default is `font-size:15-16px`, generous leading, and `text-indent:2em` on each ordinary body paragraph.
- Mark an indented prose paragraph as `p[data-indent-role="body-paragraph"]`. This marker exists only to keep indentation on body prose. Titles, leads, labels, lists, quotations, dialogue, captions, cards, actions, closings, and containers use no first-line indent.
- Never simulate indentation with full-width spaces or repeated non-breaking spaces.
- Keep major titles and section headings on one mobile line when the wording and visual voice permit it. Reduce display size or refine composition before wrapping. Do not replace distinctive language with generic copy, force `white-space:nowrap`, or create overflow. A deliberately balanced two-line heading remains valid.
- `data-media-id` is required only for a local body image that the release command must upload and replace. Other design markers are optional and have no release meaning.
- Use local primitives as raw material, not a checklist. Do not stack examples merely because they exist.

### 5. Use images and motion freely within the publishing boundary

When a required body image or cover is missing, use an available image-generation capability first without turning generated imagery into evidence. Save prepared files under `assets/` and register only operational media data in `release-manifest.json`.

Inline SVG and SMIL are available whenever they improve explanation, comparison, pacing, atmosphere, emotional transition, seasonal change, or narrative world-building. Multiple scenes are valid when each has a real compositional job. Gradients, masks, clipping, paths, filters, `textPath`, morphing, and ambient motion may be explored when the exact result has a meaningful initial state and survives editor testing. Essential facts and actions must remain available in initial state or adjacent HTML.

CSS keyframe animation is not publishable because a fragment cannot carry its required style block. Use inline SVG/SMIL for motion. Treat compatibility warnings as reasons to inspect the actual draft, not reasons to make every article visually conservative.

### 6. Run postflight release

Do not freeze a design plan before composing. The optional command below records observations after the design exists and never blocks release:

```powershell
python scripts/article_workspace.py inspect ".\articles\date_title"
```

Deliver only through:

```powershell
python scripts/release_article.py deliver ".\articles\date_title"
```

The release command audits the finished article, selects the resolved route, uploads prepared media, synchronizes revisions, and either creates one new draft or produces local preview. It does not compare the design with a contract.

## Operational media manifest

`release-manifest.json` contains delivery data only. It is not a visual brief:

```json
{
  "schema_version": 1,
  "article_title": "Article title",
  "media": [
    {
      "name": "cover",
      "placement": "cover",
      "required": true,
      "state": "generated-local",
      "source_path": "cover.jpg",
      "remote_ref": ""
    }
  ],
  "delivery": {
    "target": "auto",
    "backend_ready": false,
    "user_requested_preview_only": false,
    "fallback_reason": "",
    "image_generation_status": "complete",
    "image_generation_reason": ""
  }
}
```

States are `placeholder`, `generated-local`, `supplied-local`, or `hosted`. A body item uses a matching `<img data-media-id="name" src="wechat-media://name" ...>` until upload. A direct draft requires one prepared 2.35:1 cover. Keep the local cover source even after upload so dimensions remain verifiable.

## Hard release gates

Postflight validation blocks delivery only for defects that make the article unsafe, operationally ambiguous, or materially unreadable:

- unsupported factual invention or leakage of source instructions, workflow narration, private paths, conversation history, cache, experiments, or local test data;
- scripts, event handlers, external CSS/fonts, dangerous URLs, active embeds, CSS Grid, or positioned layouts that cannot survive WeChat;
- rendered fixed widths above 320px or percentages above 100%;
- body prose below 14px or below 1.5 leading when those values are explicitly set;
- non-body indentation, marked body indentation other than `2em`, or manual-space indentation;
- known text contrast below the hard 3:1 readability floor;
- unhosted images in a direct draft, missing operational media mappings, or an invalid cover;
- backend routing, draft validation, revision transaction, idempotence, or ambiguous-submission failures.

Unknown CSS, expressive effects, gradients, image-backed text, SVG motion, compact labels, unusual spacing, and other aesthetic decisions produce warnings or require human inspection. They do not fail merely for differing from recommendations.

## Delivery behavior

If required media is missing, release returns exit code `3`, `image-generation-required`, blockers, and an `attempt_id`. Immediately generate the media, update `release-manifest.json`, and rerun without asking for confirmation. Only after a real generation failure may the same attempt ID be submitted with `--image-generation-failed`; release then creates local preview.

If image upload, server validation, or a definite pre-draft request fails, switch immediately to local preview. Already uploaded WeChat materials remain under the user's control. When draft creation has started and returns timeout, `502`, pending, unknown, or any ambiguous result, do not retry and do not fall back. The workspace remains locked until the user checks the real draft box and runs:

```powershell
python scripts/article_workspace.py resolve-draft WORKSPACE --outcome created
python scripts/article_workspace.py resolve-draft WORKSPACE --outcome not-created
```

A healthy backend route must not leave `preview.html` behind. A local-preview route must generate it. Revisions increment when body, metadata, operational media, assets, preview state, optional design report, or preserved legacy design files change. `request_id` rotates only when the draft payload changes. Snapshot failure rolls the synchronization back.

For a v2/v3 workspace, run `python scripts/article_workspace.py migrate WORKSPACE`. Migration creates `release-manifest.json` from legacy media records and preserves the old design files without making them release gates. The legacy `plan` command is a non-blocking alias for `inspect`.

## Final review

Before handing off, review the actual reader-facing article and all draft metadata. Check facts, promises, brands, incentives, institutional language, evidence images, title, author, digest, opening, transitions, closing, and action. Inspect approximately 320px, 375px, and 390px viewports, then inspect the actual WeChat draft on a phone when available. The user decides whether the final draft should be published.
