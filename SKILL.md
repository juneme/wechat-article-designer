---
name: wechat-article-designer
description: Create, revise, validate, and deliver mobile-first WeChat Official Account (微信公众号) articles through a stage-gated design contract covering editorial structure, explicit Chinese typography, palette, media, effects and fallbacks, editor compatibility, versioning, and configured draft-box delivery.
---

# WeChat Article Designer

Create audience-facing WeChat article fragments from the article's content and the living design grammar. Do not choose or reuse a fixed page template.

## Operating contract

1. Create or reuse one article workspace before preparing images or draft data.
2. Resolve the delivery route before production: use the console server when its full configuration is present and healthy; otherwise use a local preview. Do not add clipboard-copy controls to previews.
3. Keep source instructions, design reasoning, validation notes, and local paths outside publishable copy.
4. Preserve supplied facts, names, assets, claims, and brand rules. Do not invent evidence.
5. Produce a fragment with inline styles, not a web page.
6. Treat the real WeChat editor and phone preview as the rendering authority.
7. Draft creation is staging; it does not authorize publication or mass sending.
8. For a new article or substantial redesign, complete every stage gate and every design-contract dimension below. A conditional feature may be recorded as `none` or `N/A` with a content-based reason; it may not be silently omitted.
9. Keep the private design contract synchronized with the implementation. Do not introduce an unrecorded layout, type, color, media, geometry, or effect decision while composing HTML.
10. For a correction or minor revision, preserve the existing contract and rerun the gates affected by changed body, metadata, contract, assets, or preview state. Do not force a full redesign workflow unless the visual or editorial system changes materially.

## Route the request

| Request | Read |
|---|---|
| New article or substantial redesign | `references/editorial-writing-grammar.md`, `references/article-design-synthesis.md`, `references/modular-composition-system.md`, `references/typography-system.md`, `references/design-grammar.md`, and `references/creative-css-capabilities.md` |
| CSS capability or fallback decision | `references/creative-css-capabilities.md` |
| Reusable inline block | `references/snippets.md` |
| Article creation, synchronization, or version history | `references/article-workspaces.md` |
| SVG component or interactive editorial layout | `references/svg-design-genes.md` |
| Learn a design source | `references/design-learning-workflow.md` |
| Direct draft-box delivery | `references/direct-publishing.md` |

For an explicit visual reference, reproduce it as closely as the article content and WeChat boundaries allow while preserving its visual thesis and signature relationships. Adapt only what the final evidence, copy, mobile width, or editor compatibility requires.

## Non-negotiable production boundary

Apply this boundary to every new full article and substantial redesign. It is a staged workflow, not a menu of optional skill features.

1. **Route and workspace gate**: check the three console variables without printing their values, run `status` when all are present, choose direct draft or local preview, then create one article workspace. A user request for preview-only, HTML-only, or stop-before-draft overrides an available backend.
2. **Editorial gate**: complete the content map and editorial promise, then make the unstyled article pass `references/editorial-writing-grammar.md`. Do not style unresolved copy.
3. **Design gate**: edit the machine-readable `design-contract.json`. Every required dimension must contain a concrete decision or a reasoned `N/A`; no placeholder may remain. Set `status` to `PLANNED` after the planning checks pass, run the workspace `plan` command, and do not write publishable HTML before this state. `design-contract.md` is a generated private reading view and must not be edited.
4. **Implementation gate**: build only from the approved copy, module manifest, type plan, and planned design contract. If a better visual decision emerges, return the contract to `PLANNED` and rerun `plan` before using it. Keep the contract `PLANNED`; only the release command may bind the exact fragment and promote it to `READY`.
5. **Release gate**: use only `python scripts/release_article.py deliver <workspace>`. It binds the exact fragment to the contract, audits the local fragment and all publishable metadata before any upload, resolves the backend route, uploads prepared local media, re-audits the hosted result, creates one new draft when healthy, and otherwise produces the permitted local preview. Creative behavior requires a readable static state; the user may inspect the created Creative draft before deciding whether to retain or simplify it.

The design contract must answer all of these dimensions:

| Dimension | Required decision |
|---|---|
| Editorial and structure | Reader, purpose, evidence boundary, reasoning path, module sequence, dominant module, and closing job |
| Layout and rhythm | Reading order, outer baseline, content inset, widths, section spacing, paragraph spacing, density curve, and alignment behavior |
| Typography | Actual font stack, size, line height, weight, alignment, first-line indent, letter spacing, wrapping, and role relationships for every used text role |
| Color | Exact field, ink, primary signal, secondary signal, correction, and image-derived colors; usage ratio and contrast strategy |
| Media | The job, authority, order, crop, caption, and final/placeholder state of each image or illustration |
| Geometry and motif | Edge language, rules, surfaces, radius policy, content-native motif, and where each may recur |
| Effects and motion | Choose `none`, static expressive CSS, or SVG/SMIL; record its semantic job, compatibility risk, static state, fallback, and test obligation |
| Delivery | Steady or Creative mode, must-keep and avoid rules, editor fallback, target route, and stop condition |

Mandatory decision does not mean mandatory decoration. In particular, never add animation, SVG, cards, gradients, shadows, or images merely to satisfy the matrix. Body paragraphs default to `text-indent:2em`; non-body roles use `0`, and a different body convention requires a recorded `body-first-line-indent` exception.

## Design a new article

### 1. Establish the brief

Identify the reader, narrator, literal topic, desired action, information density, emotional register, image roles, evidence, brand constraints, and risk profile. The Skill owns both writing and design. Infer subjective and non-factual decisions, finish a coherent result, and let the user judge the output; never invent names, dates, evidence, claims, credentials, or institutional facts.

### 2. Write and structure before styling

Create a private:

- editorial promise for reader situation, central friction, defensible judgment, reader gain, and evidence boundary;
- content map for facts, argument, images, and reader action;
- module manifest for semantic roles, order, width, weight, and density;
- type plan for display, section, item, body, label, caption, and data roles.

Make the complete unstyled article pass the editorial review. Then evaluate the complete living grammar and fill every section of `design-contract.json` with article-specific values. Generate `design-contract.md` through the workspace command. The JSON contract, not an improvised HTML treatment, controls layout, typography, color, media, geometry, effects, fallback, and delivery.

Do not show a template picker or start from a previous article. When exploration is requested, propose a small set of directions derived from the current content.

### 3. Write for the reader

- Read `references/editorial-writing-grammar.md` and make the unstyled draft pass its review before composing HTML.
- Make the article understandable without the source request.
- Remove workflow narration, approval language, validation status, and source-request echoes.
- Keep claims within supplied evidence and audience boundaries.
- Use headings, lists, numbers, comparisons, and emphasis only for relationships that exist in the source content.
- Run `scripts/audit_audience_boundary.py` before delivery.

### 4. Build the fragment

- Wrap publishable markup with `<!-- 微信公众号复制开始 -->` and `<!-- 微信公众号复制结束 -->`; these legacy-named comments are extraction markers, not a clipboard feature.
- Prefer single-column `section`, `p`, and `span` flow.
- Keep all required styles inline.
- Use the article's images and subject to determine palette, motif, media rhythm, and transitions.
- Set Chinese letter spacing to `0`; make hierarchy readable without color, cards, gradients, or shadows.
- Put a supported `data-type-role` on each text-role root and `data-content-kind="dialogue"` or `"quotation"` on genuine quoted speech. Every module uses `data-module-id` and its matching `data-density`. Mark exactly one horizontal-padding implementation for `data-layout-role="outer-baseline"` and one for `data-layout-role="content-inset"`; list every pixel width in `layout.fixed_widths_px`. Mark used spacing and geometry with `data-spacing-role` and `data-geometry-role`, and make each geometry marker implement the exact declarations in `geometry.implementations`. Body media uses the recorded `data-media-id` and `data-media-crop`; a non-`N/A` caption follows it with `data-caption-for` and exact caption text. Implement the recorded font stack, sizes, line heights, weights, alignment, paragraph gaps, wrapping, and first-line indent exactly. Do not insert manual spaces to simulate indentation.
- Adapt only the needed blocks from `references/snippets.md`; do not stack every available component.
- Do not add a visual treatment that is absent from the design contract. Update and recheck the contract first when implementation changes a design decision.

## Article workspace

Read `references/article-workspaces.md` and create one workspace per article with `scripts/article_workspace.py`. Use `create --no-preview` for a ready direct-draft route and the default create command for the local-preview route. Keep `fragment.html` as the editable markup source, local images under `assets/`, and server draft data in `article.json`.

Complete `design-contract.json`, set it to `PLANNED`, and run `plan` before HTML implementation. Do not set `READY` or `checks.fragment_sha256` manually: the enforced release command binds and promotes the exact audited fragment. Sync rejects a changed design plan or stale fragment binding, regenerates the private Markdown view, creates the script-free preview only for the local-preview route, physically removes an obsolete preview on the direct route, rotates `request_id` only when draft payload changed, and snapshots every body, metadata, contract, asset, or preview change under `revisions/`. Do not edit generated contract Markdown or copy one article's root-level files over another article.

## Images

When a required image is missing, generate it first with an available image capability while respecting the evidence boundary. If generation or final hosting cannot be completed, switch the article to local preview and use the editable image placeholder in `references/snippets.md`. Keep filenames and insertion instructions outside the publishable boundary, then remove placeholders before direct delivery.

If the release command returns exit code `3` with `image-generation-required`, retain its `attempt_id`, immediately invoke the available image capability without asking the user, store the result under workspace `assets/`, update its contract media state and `source_path`, rerun `plan` only if a design decision changed, and run release again. Do not hand off at exit code `3`. Only after the image capability actually fails may release be rerun with both `--image-generation-attempt-id <id>` and `--image-generation-failed "reason"`; an invented or stale ID is rejected.

For direct delivery:

1. Finalize body images and a required 2.35:1 PNG, JPEG, GIF, or WebP cover whose local source remains under `assets/` so pixel dimensions can be machine checked, including after upload or `thumb_media_id` reuse.
2. Upload body images in article mode and insert returned HTTPS article URLs.
3. Upload the cover separately and use its permanent `media_id`.
4. Remove placeholders and local paths before draft validation.

Generated images may illustrate a story but may not prove certifications, official documents, seals, logos, real events, or institutional status.

Prefer vertical media flow for repeated images. Use manual horizontal swipe only when the exact final block can be tested in WeChat and a single-column fallback is available.

## Compatibility

Every final fragment must satisfy these invariants:

- no scripts, event handlers, external CSS, `style` blocks, web fonts, iframes, objects, or embeds;
- no local or relative image paths;
- no CSS Grid, positioned layout, fragile tables, or interaction-dependent information;
- no percentage width above `100%`;
- fixed widths stay inside the mobile column;
- opening and closing `section`, `p`, and `span` counts balance;
- all information remains readable after optional visual effects are removed.

Use Steady mode by default. Use Creative mode when expressive CSS materially supports the article and the exact final fragment has a readable solid fallback. A configured backend may create that Creative draft for the user's real-editor review; lack of a prior editor test does not force Steady.

Every new design must make an effects decision. `none` is the normal result when motion or expressive CSS adds no semantic value. CSS keyframe animation is not publishable because the fragment cannot contain a `style` block; use the established SVG/SMIL vocabulary when motion materially clarifies sequence or state.

SVG editorial components are an established Creative capability. When an SVG materially improves explanation, comparison, sequence, reveal, or emphasis, read `references/svg-design-genes.md` and compose it from the article's Visual DNA. Essential facts and actions must remain understandable from the initial state or surrounding prose, but a duplicate fallback block is not required. SVG uses the normal article checks and draft validation, not a separate validation workflow.

## Direct draft workflow

Read `references/direct-publishing.md` before using the console client.

1. Confirm `WECHAT_CONSOLE_URL`, `WECHAT_IMAGE_API_KEY`, and `WECHAT_PUBLISH_API_KEY` without printing values.
2. When all three are present, run `python scripts/wechat_console_api.py status`. Treat the backend as ready only when the command succeeds, both key flags are true, and `server_healthy` is true.
3. Generate required missing images through an available image capability. Record generated or supplied local assets in the contract; record a real failure before permitting placeholder fallback.
4. Run `python scripts/release_article.py deliver <workspace>`. This is the only authorized mutating entrypoint; the low-level client exposes only status and validation diagnostics. The release command audits local markup and metadata before uploading, synchronizes the selected route, validates the hosted payload, and creates one new draft automatically when ready.
5. Use `--preview-only` only when the user requested it. Use image-failure flags only with the current `attempt_id` after an actual generation attempt failed.

If any variable is missing, status is unhealthy, image generation or upload fails, route-specific server validation fails, or the backend returns a definite pre-draft error, do not attempt partial direct delivery; let the release command synchronize the local-preview route and report it. Local article-audit errors block both routes. Already uploaded WeChat material remains under the user's control. If draft creation has started and returns a timeout, `502`, `pending`, `unknown`, or another ambiguous result, do not retry and do not switch routes; report the ambiguity so the user can inspect the real draft box.

Never automatically retry `create-draft` after a timeout, `502`, pending, or unknown result. Inspect operation state and the real draft box first.

The release command records `submitting` before the request leaves the machine. A process interruption or ambiguous response locks the whole workspace against retry and preview fallback. After the user inspects the real draft box, run `python scripts/article_workspace.py resolve-draft <workspace> --outcome created` or `--outcome not-created`; do not edit the lock in `manifest.json`.

## Quality gates

Before delivery:

1. Let `release_article.py` run the markup, audience, width, typography, contrast, and structural contract audits. Do not call the mutating API client directly.
2. Confirm the release command produced a `READY`, machine-valid contract whose generated fragment digest, module order, spacing roles, geometry markers, and media order match the final fragment; inspect the regenerated private Markdown view.
3. Review facts, promises, institutional terms, incentives, brands, and evidence images.
4. Check approximately 320px, 375px, and 390px widths for overflow, long text, image loading, and reading order.
5. Review the longest title, heading, label, URL, body size, leading, Chinese tracking, captions, and density changes.
6. Preview Creative mode, manual swipe, or any fragile pattern in the real editor when available.
7. For SVG, confirm the initial state and surrounding prose preserve essential meaning without requiring interaction.
8. For direct delivery, require hosted body images, a permanent cover `media_id`, and successful draft validation.

For a backend-unavailable, failed pre-draft, or explicitly preview-only route, report the article workspace, local preview, and validation state. For direct delivery, report the confirmed new-draft API result, leave final review to the user, and do not create or present a local preview as the delivery artifact. Keep design synthesis and validation history out of the published article.
