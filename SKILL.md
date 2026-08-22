---
name: wechat-article-designer
description: Create, revise, version, validate, and deliver mobile-first WeChat Official Account (微信公众号) articles, including content-specific visual synthesis, Chinese typography, image handling, SVG editorial components, editor compatibility, and authorized draft-box delivery.
---

# WeChat Article Designer

Create audience-facing WeChat article fragments from the article's content and the living design grammar. Do not choose or reuse a fixed page template.

## Operating contract

1. Create or reuse one article workspace before preparing images or draft data.
2. Use the console server for final draft delivery. Do not add clipboard-copy controls to previews.
3. Keep source instructions, design reasoning, validation notes, and local paths outside publishable copy.
4. Preserve supplied facts, names, assets, claims, and brand rules. Do not invent evidence.
5. Produce a fragment with inline styles, not a web page.
6. Treat the real WeChat editor and phone preview as the rendering authority.
7. Draft creation is staging; it does not authorize publication or mass sending.

## Route the request

| Request | Read |
|---|---|
| New article or substantial redesign | `references/editorial-writing-grammar.md`, `references/article-design-synthesis.md`, `references/modular-composition-system.md`, `references/typography-system.md`, and `references/design-grammar.md` |
| CSS capability or fallback decision | `references/creative-css-capabilities.md` |
| Reusable inline block | `references/snippets.md` |
| Article creation, synchronization, or version history | `references/article-workspaces.md` |
| SVG component or interactive editorial layout | `references/svg-design-genes.md` |
| Learn a design source | `references/design-learning-workflow.md` |
| Direct draft-box delivery | `references/direct-publishing.md` |

For an explicit visual reference, preserve its visual thesis or signature relationship, then rebuild structure, typography, evidence, images, and fallbacks around the final article.

## Design a new article

### 1. Establish the brief

Identify the reader, narrator, literal topic, desired action, information density, emotional register, image roles, evidence, brand constraints, and risk profile. Ask only for information that cannot be inferred safely.

### 2. Build structure before styling

Create a private:

- editorial promise for reader situation, central friction, defensible judgment, reader gain, and evidence boundary;
- content map for facts, argument, images, and reader action;
- module manifest for semantic roles, order, width, weight, and density;
- type plan for display, section, item, body, label, caption, and data roles.

Then evaluate the complete living grammar across palette, typography, composition, geometry, media behavior, pacing, evidence, and closing logic. Write one article-specific design contract with a visual thesis, content-native motif, must/avoid rules, and Steady fallback.

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
- Adapt only the needed blocks from `references/snippets.md`; do not stack every available component.

## Article workspace

Read `references/article-workspaces.md` and create one workspace per article with `scripts/article_workspace.py`. Keep `fragment.html` as the editable markup source, local images under `assets/`, and server draft data in `article.json`.

Run workspace sync after changing the fragment or draft metadata. Sync regenerates the script-free preview, rotates `request_id` only when the payload changed, and snapshots the prepared state under `revisions/`. Do not manually copy one article's root-level files over another article.

## Images

For preview-only preparation, use the editable image placeholder in `references/snippets.md`. Keep filenames and insertion instructions outside the publishable boundary, then remove placeholders before direct delivery.

For direct delivery:

1. Finalize body images and a 2.35:1 cover.
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

Use Steady mode by default. Use Creative mode only when expressive CSS materially supports the article and the exact final fragment can be previewed with its solid fallback.

SVG editorial components are an established Creative capability. When an SVG materially improves explanation, comparison, sequence, reveal, or emphasis, read `references/svg-design-genes.md` and compose it from the article's Visual DNA. Essential facts and actions must remain understandable from the initial state or surrounding prose, but a duplicate fallback block is not required. SVG uses the normal article checks and draft validation, not a separate validation workflow.

## Direct draft workflow

Read `references/direct-publishing.md` before using the console client.

1. Confirm `WECHAT_CONSOLE_URL`, `WECHAT_IMAGE_API_KEY`, and `WECHAT_PUBLISH_API_KEY` without printing values.
2. Run `python scripts/wechat_console_api.py status`.
3. Upload final images, build the mapped HTML, and upload the existing 2.35:1 cover format.
4. Synchronize the article workspace to update content, version history, and the idempotent `request_id`.
5. Run the standard local article checks and `validate-draft`; fix every error.
6. Run `create-draft` only when draft-box delivery was requested.

Never automatically retry `create-draft` after a timeout, `502`, pending, or unknown result. Inspect operation state and the real draft box first.

## Quality gates

Before delivery:

1. Run the audience, width, typography, and contrast audits.
2. Complete the checklist in `references/snippets.md`.
3. Review facts, promises, institutional terms, incentives, brands, and evidence images.
4. Check approximately 320px, 375px, and 390px widths for overflow, long text, image loading, and reading order.
5. Review the longest title, heading, label, URL, body size, leading, Chinese tracking, captions, and density changes.
6. Preview Creative mode, manual swipe, or any fragile pattern in the real editor when available.
7. For SVG, confirm the initial state and surrounding prose preserve essential meaning without requiring interaction.
8. For direct delivery, require hosted body images, a permanent cover `media_id`, and successful draft validation.

For preview-only work, report the article workspace and validation state. For direct delivery, report the confirmed API result. Keep design synthesis and validation history out of the published article.
