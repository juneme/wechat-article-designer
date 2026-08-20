---
name: wechat-article-designer
description: Create, revise, validate, and deliver mobile-first WeChat Official Account (微信公众号) articles, including content-specific visual synthesis, Chinese typography, image handling, editor compatibility, and authorized draft-box delivery.
---

# WeChat Article Designer

Create audience-facing WeChat article fragments from the article's content and the living design grammar. Do not choose or reuse a fixed page template.

## Operating contract

1. Choose manual HTML delivery or direct draft delivery before preparing images.
2. Keep source instructions, design reasoning, validation notes, and local paths outside publishable copy.
3. Preserve supplied facts, names, assets, claims, and brand rules. Do not invent evidence.
4. Produce a fragment with inline styles, not a web page.
5. Treat the real WeChat editor and phone preview as the rendering authority.
6. Draft creation is staging; it does not authorize publication or mass sending.

## Route the request

| Request | Read |
|---|---|
| New article or substantial redesign | `references/original-style-synthesis.md`, `references/modular-composition-system.md`, `references/typography-system.md`, and `GALLERY.md` |
| CSS capability or fallback decision | `references/creative-css-capabilities.md` |
| Reusable inline block | `references/snippets.md` |
| Learn a design source | `references/design-learning-workflow.md` and `references/design-knowledge-schema.md` |
| Direct draft-box delivery | `references/direct-publishing.md` |

For an explicit visual reference, preserve its visual thesis or signature relationship, then rebuild structure, typography, evidence, images, and fallbacks around the final article.

## Design a new article

### 1. Establish the brief

Identify the reader, narrator, literal topic, desired action, information density, emotional register, image roles, evidence, brand constraints, and risk profile. Ask only for information that cannot be inferred safely.

### 2. Build structure before styling

Create a private:

- content map for facts, argument, images, and reader action;
- module manifest for semantic roles, order, width, weight, and density;
- type plan for display, section, item, body, label, caption, and data roles.

Then evaluate the complete living grammar across palette, typography, composition, geometry, media behavior, pacing, evidence, and closing logic. Write one article-specific design contract with a visual thesis, content-native motif, must/avoid rules, and Steady fallback.

Do not show a template picker or start from a previous article. When exploration is requested, propose a small set of directions derived from the current content.

### 3. Write for the reader

- Make the article understandable without the source request.
- Remove workflow narration, approval language, validation status, and source-request echoes.
- Keep claims within supplied evidence and audience boundaries.
- Run `scripts/audit_audience_boundary.py` before delivery.

### 4. Build the fragment

- Wrap publishable markup with `<!-- 微信公众号复制开始 -->` and `<!-- 微信公众号复制结束 -->`.
- Prefer single-column `section`, `p`, and `span` flow.
- Keep all required styles inline.
- Use the article's images and subject to determine palette, motif, media rhythm, and transitions.
- Set Chinese letter spacing to `0`; make hierarchy readable without color, cards, gradients, or shadows.
- Adapt only the needed blocks from `references/snippets.md`; do not stack every available component.

## Images

For manual editor delivery, use the editable image placeholder in `references/snippets.md`. Keep filenames and insertion instructions outside the copy boundary.

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

## Direct draft workflow

Read `references/direct-publishing.md` before using the console client.

1. Confirm `WECHAT_CONSOLE_URL`, `WECHAT_IMAGE_API_KEY`, and `WECHAT_PUBLISH_API_KEY` without printing values.
2. Run `python scripts/wechat_console_api.py status`.
3. Upload final images, build the mapped HTML, and upload the cover.
4. Create a UTF-8 article payload with a new idempotent `request_id`.
5. Run local audits and `validate-draft`; fix every error.
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
7. For direct delivery, require hosted body images, a permanent cover `media_id`, and successful draft validation.

For HTML delivery, provide the final fragment, asset map, and minimal insertion instructions. For direct delivery, report the confirmed API result. Keep design synthesis and validation history out of the published article.
