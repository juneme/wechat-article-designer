---
name: wechat-article-designer
description: "Design, revise, and troubleshoot WeChat Official Account (微信公众号) articles with content-driven original style synthesis from a 24-style internal DNA library, Steady and Creative delivery modes, evidence-backed inline CSS including flex, inline-block, manual swipe overflow, gradients, shadows, and large radii, mobile-first layouts, photo placeholders, covers, and publishing QA. Use for 微信公众号 / WeChat article HTML, new article creation, unique or bold original design, artbook and editorial collage directions, recruitment and public-interest posts, image slots, editor compatibility, cover generation, or direct-publishing preparation. Brand-agnostic across topics, audiences, and color palettes."
---

# WeChat Article Designer

> A brand-agnostic, industry-agnostic skill for producing WeChat 公众号 article HTML that renders correctly inside the WeChat editor and on mobile. This skill does not assume any specific brand, audience, industry, or topic — it works for any WeChat publisher.

## New-Creation Originality Gate

Classify the request before doing article design work.

Treat the request as a **new article creation** when the user wants a new full WeChat article designed from a topic, brief, draft copy, poster, reference image, or source material and is not asking to preserve an existing article layout.

For every new article creation:

1. Read `references/original-style-synthesis.md` and `GALLERY.md` internally. Do not show a template picker by default.
2. Extract the article's audience, emotional register, information density, image role, desired action, subject-native metaphors, and any authoritative visual system.
3. Build a new design fingerprint across palette behavior, opener, section rhythm, edge geometry, image treatment, recurring motif, closing device, and delivery mode.
4. Load two to four relevant source routes from the DNA catalog across different dimensions. Do not copy one asset as the complete DOM skeleton.
5. Name the new style in one short line, then proceed. Do not burden the user with another design decision when the supplied material is sufficient.
6. If the user explicitly names a template or asks for faithful reproduction, use that route as an exception. If the user explicitly asks to browse templates, show the 24-style gallery and wait for a choice.
7. Preserve all supplied topic, copy, audience, assets, and constraints. Ask only for information that is still required to produce the article.

Do **not** run original-style synthesis for:

- revisions, restyling, or troubleshooting of an existing article or HTML fragment;
- continuation of an article whose design fingerprint was already established;
- a standalone cover, image frame, or photo-processing request;
- compatibility audits, publishing checks, or risk-word reviews.

## Quick start workflow

After the new-creation originality gate, use this path to produce a publishable WeChat article fragment:

1. **Gather inputs**: article topic, target audience, key copy points, and any supplied main visual, poster, cover, logo, or brand palette.
2. **Synthesize the design fingerprint**: use `references/original-style-synthesis.md` and the DNA catalog in `GALLERY.md`; derive the recurring motif from the article itself.
3. **Resolve the delivery mode**: infer Creative for bold, original, experimental, strong-impact, gradient, or shadow requests; otherwise use Steady unless publishing constraints dictate one mode.
4. **Load source DNA**: inspect only the two to four routes needed for the chosen dimensions. Use them as vocabulary, not as a full-page starter.
5. **Pick the color tokens**: when a main visual is supplied, sample it first and map its real colors to `{{BRAND_*}}`; use fallback colors only when no authoritative visual exists.
6. **Compose for the story**: create an opener, section progression, image rhythm, and closing that differ structurally from the nearest library example.
7. **Customize copy**: keep mobile headings and content blocks readable rather than enforcing one fixed character count.
8. **Add photos**: use placeholders that match the new design fingerprint; let the user upload photos in the WeChat editor. Do not embed local paths.
9. **Run the mode-aware and originality self-audits** below. Fix any failure before delivery.
10. **Wrap with copy boundaries**: add `<!-- 微信公众号复制开始 -->` / `<!-- 微信公众号复制结束 -->` markers.

If the user only has draft text and no design direction, infer the visual register from the text, audience, and desired action. Ask only when a non-inferable brand or publishing choice materially changes the result.

## Core Workflow

Create a WeChat-ready article fragment, not an app or ordinary web page.

1. Preserve the user's copy and brand claims unless asked to rewrite.
2. Diagnose the problem type before styling: clutter, excessive copy, weak hierarchy, excessive decoration, and accidental nostalgia require different fixes.
3. For a new article, synthesize a design fingerprint before choosing snippets. For a revision, preserve the existing visual register unless the user requests a redesign.
4. Build mobile-first layouts with inline styles on each element.
5. Use simple flow tags: `section`, `p`, and `span`. Treat `table`, `tbody`, `tr`, and `td` as prohibited by default; use `img` only for an already-hosted image when the publishing workflow requires it.
6. Avoid external CSS, `<style>`, scripts, web fonts, complex selectors, and layout that depends on JavaScript.
7. Add copy boundaries:
   - `<!-- 微信公众号复制开始 -->`
   - `<!-- 微信公众号复制结束 -->`
8. Keep visual rhythm intentional. A selected style may be quiet, high-contrast, dark, colorful, editorial, or spacious; do not normalize every article to pale rounded cards. Avoid crowded multi-column mobile blocks unless the content is truly compact.
9. **Self-audit before delivery** (see "Self-Audit Before Delivery" section below).
10. Validate before finishing: no scripts, no style blocks, matched open/close tags, expected image count, brand-name consistency, and image-role accuracy.

## Resource routes

- **New full article**: read [`references/original-style-synthesis.md`](references/original-style-synthesis.md) and [`GALLERY.md`](GALLERY.md), build a unique design fingerprint, and load two to four source routes across different dimensions.
- **Creative CSS**: read [`references/creative-css-capabilities.md`](references/creative-css-capabilities.md). Keep effects mode-aware and degradable; never copy example claims or names.
- **Paper-cut artbook composition**: read [`references/paper-cut-artbook.md`](references/paper-cut-artbook.md) when the brief benefits from cool-white space, editorial collage, nonuniform image silhouettes, or a quiet art-book rhythm. Borrow its composition grammar by dimension; do not reproduce its complete sequence.
- **Contour field-note composition**: read [`references/contour-index.md`](references/contour-index.md) for topographic rings, stepped reading levels, organic specimen windows, and a sample-drawer swipe strip. Treat it as an artbook-family branch, not automatic proof of a separate gestalt.
- **Still-frame cinema composition**: read [`references/still-frame-cinema.md`](references/still-frame-cinema.md) for full-width color bands, centered title cards, hard widescreen frames, subtitle sequences, split screens, and a closed credits ending.
- **Chromatic folio composition**: read [`references/chromatic-folio.md`](references/chromatic-folio.md) for a validated color-bound cover, fold-tab index, circular lead plate, four-edge mount, gatefold, bookmark detail, and archive-sleeve ending. Treat it as a usable secondary artbook branch, not the quality bar for artbook-led exploration.
- **Paper-cut original series**: read [`references/paper-cut-original-series.md`](references/paper-cut-original-series.md) for the independently approved Botanical Press, Cut-Paper Atlas, Conservation Folio, Poetic Zine, and Material Board branches. Select one semantic route or borrow dimensions across them; never reuse one branch's full sequence as the generic Paper Cut skeleton.
- **Web capability R&D / progressive enhancement**: read [`references/progressive-enhancement-lab.md`](references/progressive-enhancement-lab.md). Separate the publishable fragment from the browser experiment host, define a single-column degradation contract, and label browser-only evidence as real-editor pending.
- **Explicit template request**: load only the named route from `GALLERY.md` and treat it as a structural starter. Show `assets/previews/template-gallery.png` only when the user explicitly asks to browse styles.
- **Soft App recruitment article**: read [`references/soft-app-recruitment.md`](references/soft-app-recruitment.md), then start from [`assets/soft-app-recruitment-article.html`](assets/soft-app-recruitment-article.html) as a candidate layout. Re-test the final copy in the real WeChat editor; if its compact flex rows are rewritten, use the documented single-column fallback.
- **Hard-edge dopamine recruitment article**: read [`references/dopamine-editorial-recruitment.md`](references/dopamine-editorial-recruitment.md), then start from [`assets/dopamine-editorial-recruitment-article.html`](assets/dopamine-editorial-recruitment-article.html). Keep the final WeChat fragment single-column and use editable-paragraph anchors inside image placeholders so inserted images stay inside the frame without deleting its wrapper.
- **2.35:1 recruitment cover**: run `scripts/generate_wechat_cover.py`; pass final Chinese copy explicitly so the bitmap contains exact approved text.
- **General sections and troubleshooting**: use `references/snippets.md`. For government-guided or public-interest work, use `references/modern-institutional-public-interest.md` instead of the recruitment pattern.
- **Clean poster-derived card systems**: use the "White-Interior Accent-Edge Grouped Card" in `references/snippets.md` when the authoritative visual has two or three bright accent colors but the article needs a light, reliable reading surface.

## Customizing for Your Brand

This skill is brand-agnostic. To apply it to your brand, replace these placeholders in the snippets:

| Placeholder | Replace with |
|---|---|
| `{{BRAND_PRIMARY}}` | Your brand's primary color (e.g. `#1f7b5d`) |
| `{{BRAND_ACCENT}}` | Your brand's accent color (e.g. `#ee7d2a`) |
| `{{BRAND_TERTIARY}}` | An optional third sampled accent; use only when the authoritative visual clearly supports it |
| `{{BRAND_BG}}` | Page background color (often `#ffffff`) |
| `{{BRAND_TEXT}}` | Body text color (often `#16221c` or near-black) |
| `{{BRAND_BORDER}}` | Card border color (lighter than primary) |
| `{{BRAND_DARK}}` | Darker companion to the primary, used for institutional bookends |
| `{{BRAND_DIVIDER}}` | Neutral divider color |
| `{{BRAND_SECONDARY_TEXT}}` | Cool neutral for labels and supporting text |
| `{{BRAND_GRID_BORDER}}` | Light border for compact fact grids |
| `{{READER_AGE}}` | Target reader age band (e.g. "young adults", "中老年") — affects font size and color contrast |
| `{{RISK_KEYWORDS}}` | Risk words specific to your industry (e.g. "医院/医生" for medical, "保证收益" for finance) |

Default fallbacks (used when no brand color is provided):

| Token | Default value | Purpose |
|---|---|---|
| Primary | `#1f7b5d` | Brand color, dark green, used for headlines, borders, anchors |
| Accent | `#ee7d2a` | Warm contrast, used for emphasis chips, the heart, CTA |
| Tertiary | `#5a9fb8` | Optional third sampled accent for a narrow edge or small marker only |
| Page background | `#ffffff` | Pure white — WeChat editor does not honor body background |
| Body text | `#16221c` | Near-black with slight green tint for warmth |
| Border | `#1f7b5d` | Solid primary, 2px, for photo frames |
| Caption gray | `rgba(22,34,28,0.58)` | Semi-transparent, for photo captions |
| Institutional dark | `#092f27` | Dark bookend / top rule for modern institutional work |
| Divider | `#9eada6` | Neutral rules and number separators |
| Secondary text | `#5b6f79` | Cool label and policy-note text |
| Grid border | `#d3ddd8` | Compact fact-grid borders |

## Main-Visual Color Extraction

When the user supplies a main visual, it outranks the fallback palette. Do not impose the skill's example green, a fashionable dark tone, or a generic complementary color on top of an existing visual system.

1. Inspect the visual itself, not only the logo. Sample 4-6 representative colors from large fields, type, rules, and small accents.
2. Assign roles instead of copying every sampled color: `{{BRAND_BG}}` for the light base, `{{BRAND_TEXT}}` for readable body text, `{{BRAND_PRIMARY}}` for headings/rules, `{{BRAND_ACCENT}}` for small emphasis, and `{{BRAND_DARK}}` only for limited bookends when the visual truly uses it.
3. Preserve temperature and material cues. If the visual is built from warm red, muted bronze, paper white, and ink brown, do not replace that relationship with an unrelated cool palette.
4. Control visual weight. A practical mobile starting ratio is 60-75% light background, 15-25% primary or accent surfaces, and no more than 5-10% very dark color.
5. If a deep tone feels heavy, keep it for short rules, labels, or the closing line; move large surfaces to a lighter sampled tint rather than inventing a new hue.
6. Verify text contrast separately from palette fidelity. Body text should remain near-black or another high-contrast sampled neutral even when the main visual uses pale decorative colors.

Only when no visual or brand palette is available should you start from the default fallbacks and derive an accent.

## WeChat Editor Compatibility Levels

**The WeChat editor phone preview is the source of truth, not the browser.** Apply evidence-based compatibility levels instead of treating every advanced declaration as a failure. Read `references/creative-css-capabilities.md` for the full matrix.

### Hard bans in final article fragments

- No `<script>`, event handlers, external CSS, `<style>`, or web-font dependencies.
- No browser-only or stateful payloads.
- No local image paths. Use placeholders or hosted assets required by the publishing workflow.
- No `position:absolute`, `position:relative`, or CSS Grid until the exact publishing path has real-editor evidence.
- No table layout by default. Keep only a documented exact-block exception after real-editor mobile verification.

### Proven CSS allowed in both modes

Allow solid fills, borders, alpha colors, `overflow:hidden`, large and pill radii, `display:inline-block`, compact `display:flex`, and the documented `overflow-x:auto` manual swipe pattern. These capabilities occur inside tested copy-boundary fragments; do not delete them merely because an old rule called them unsafe.

### Creative-mode CSS

Allow controlled gradients and shadows. Put a solid `background` immediately before each gradient fallback, keep shadows nonessential to hierarchy, and verify the exact fragment in phone preview. If either effect is stripped, the article must remain readable and visually organized.

### Table exception and deformation diagnosis

The default delivery contract is **zero table markup**. A browser preview is not evidence that a table is safe.

- The WeChat editor can inject a horizontally scrollable wrapper around a pasted table and normalize or rewrite `td` widths. This is especially destructive for asymmetric layouts such as `35% / 65%`, mixed label/title rows, or cells that depend on `colspan`.
- Symptoms include a new horizontal scroll area, columns becoming equal, a narrow label becoming too wide, headings wrapping unexpectedly, or the right edge being clipped.
- Do not try to repair this with more `width`, `min-width`, `table-layout`, or nested tables. Replace the entire block with a vertical or inline flow made from `section`, `p`, and `span`.
- A table is an exception only when the exact final block, with final copy and real images, has been pasted into the real WeChat editor and checked in its mobile preview at approximately 375px and 390px. Record that exception in the handoff; otherwise remove it.

## WeChat Constraints

WeChat may preserve inline styles but can strip or alter wrapper behavior when users copy only an image. The visual frame around an image is not part of the image unless it is baked into the bitmap.

Use these rules:

- If the user will manually paste photos into the editor, create an HTML photo frame with a placeholder, not a prefilled image.
- If the user needs to copy the image alone and retain the frame, bake the frame into the image with `scripts/bake_image_frame.py`.
- If a pasted photo appears with huge empty margins, a legacy padded text placeholder survived beside it. Replace that placeholder with the editable-paragraph-anchor pattern below and paste directly without deleting anything first.
- If a pasted photo carries an unwanted background color, the frame/background was baked into the image; switch back to an HTML frame placeholder.
- If the frame disappears during replacement, the editable placeholder node was selected and deleted together with its wrapper. Restore the editable-paragraph frame and paste into its blank area without selecting or deleting the anchor. If the user copied only an image and needs the frame to travel with it, use a baked frame instead.
- If the photo lands after the blank frame, the slot has no real caret target. A nested `section` plus `span` is not sufficient; make a 1px `<p>` the direct child of the visual frame.
- If the photo is surrounded by full-height blank frames above and below, WeChat split a styled paragraph around the inserted image. Keep `min-height`, padding, border, and background on the containing `section`, never on the anchor `<p>`.

## Photo Frame Pattern (Verified Editable-Paragraph Anchor)

The editable-paragraph anchor contract is verified in the WeChat editor. The visual `section` owns the frame and blank height; its direct child `<p>` exists only to provide a caret. The rounded frame language works well for warm, service-oriented, or lifestyle articles, but is not the universal default for every visual register. Re-test each final styled slot in the real editor before publication.

```html
<section style="box-sizing:border-box;min-height:116px;margin:30px 8px 0;padding:10px;border-radius:30px;background:#ffffff;border:2px solid {{BRAND_PRIMARY}};overflow:hidden;text-align:center;">
  <p style="margin:0;padding:0;font-size:1px;line-height:1px;color:transparent;">&nbsp;</p>
</section>
<p style="margin:11px 10px 0;font-size:12px;line-height:1.8;color:rgba(22,34,28,0.58);text-align:center;">caption</p>
```

Key design choices:

- `border:2px solid {{BRAND_PRIMARY}}` — 2px solid primary color, doubled thickness for visibility on white background.
- `border-radius:30px` — large rounded corners for a premium look.
- `margin:30px 8px 0` — very small horizontal margin (4-8px) so the frame fills the column.
- `min-height:116px` belongs to the visual section, keeping the blank frame easy to click without cloning a large empty paragraph around the inserted image.
- A direct-child `<p>` with `font-size:1px`, `line-height:1px`, and one `&nbsp;` acts as the invisible editing anchor. Keep it free of `min-height`, padding, border, and background.
- Do not substitute a `span` or another `section` for the anchor paragraph. Those nodes did not provide a reliable WeChat caret target in real-editor testing.
- Caption uses `rgba(22,34,28,0.58)` semi-transparent gray to soften hierarchy.
- No `box-shadow`, no `linear-gradient`, no `position` properties.

Important insertion instruction for the final answer:

1. Paste the full article fragment into WeChat.
2. Click once in the blank area of the frame until the caret is active.
3. Insert or paste the photo directly. Do not select all, press Backspace, or delete the invisible anchor first.
4. Check that the image remains inside the same frame with no full-height blank block above or below it.

Keep placement labels and filename maps in the delivery guide or HTML comments, outside the editable image container. Do not place a large padded text block around the future image; the frame should provide the only persistent padding.

For modern institutional and public-interest articles, prefer the square, cool-neutral placeholder in `references/modern-institutional-public-interest.md` or `references/snippets.md`. Do not mix both frame languages in one article.

## Width and Alignment Rule

Choose an intentional horizontal system from the design fingerprint instead of forcing every article to `8px`.

- Use `8px` for immersive full-column cards and photo frames, `16-20px` for editorial reading columns, or a deliberate mix with one outer baseline and one inset baseline.
- Align comparable blocks to the same baseline. A hero may be wider than long-form copy, but repeated cards should not drift by arbitrary margins.
- Keep the narrowest content readable at 320px. Avoid fixed widths that can exceed the article column.
- Preserve the design fingerprint's edge language: flush dark panels, inset newspaper columns, or spacious minimal text are all valid.

## White-Interior Accent-Edge Rule

Prefer a solid white card interior with a neutral 1px outer border and a `4-5px` colored edge when the brief asks for a clean, fresh, poster-matched interface.

- Sample no more than three accent colors from the authoritative poster or main visual.
- Keep body text near-black and card interiors `#ffffff`; use color only on short edge rules, labels, and small emphasis marks.
- Group related rows inside one outer card and separate them with neutral 1px dividers.
- Assign colors consistently: primary for the main flow, secondary for time or the first item, and tertiary for warnings or the third item.
- Keep every top-level card, heading, and photo frame on the same `8px` horizontal baseline.
- Prefer this pattern over faux glass for direct WeChat delivery. `backdrop-filter` is unreliable, while alpha-only glass depends on a background color the editor may strip or rewrite.
- Do not simulate glass with gradients, shadows, stacked translucent panels, positioning, or gray page backgrounds.

Use the complete grouped-card snippet in `references/snippets.md`.

## Top Spacing Rule

The WeChat editor already separates its title/author fields from the article body. Avoid accidental blank space, but do not ban intentional opening whitespace.

- Start immersive hero templates at `padding-top:0` when the first visual surface should meet the article edge.
- Allow approximately `18-40px` top padding for editorial, ink, creamy, and quiet minimal openers when that whitespace is part of the selected composition.
- Do not stack an empty wrapper, a large top margin, and large top padding before the first visible text.
- Judge the first screen in phone preview: the opener must read as designed space, not missing content.

## Dense Repeated Photo Sections

When a section repeats 6+ people/items and each card needs a photo placeholder plus text, default to a **single-column card flow** in WeChat.

Rules:
- Browser-safe is not WeChat-safe. A 3-column wall can clip, overflow, or show only a partial next card after pasting into the editor.
- If each item includes photo + department + name + topic, start with one card per row and only densify after a real editor test with real inserted photos.
- If the requirement is simply to show every participant, crop portraits consistently and assemble them into **one bitmap** before insertion. A single 4:5 portrait-wall image is safer than many HTML image cells.
- For a 4:5 portrait wall, use a square matrix of 4:5 crops: `3 x 3` for up to 9 people or `4 x 4` for up to 16. Split larger groups across two labeled walls instead of shrinking faces below mobile readability.
- Keep names outside the composite unless the exported wall has been tested at phone width and the smallest label remains readable. Photo-only walls plus one short caption are usually cleaner.
- Small square assets in dark footers (QR codes, badges, poster thumbnails) should use a **narrow centered frame** (`width:170px;max-width:100%` works well), not a full-width row wrapper.
- Do not create photo space with huge top/bottom text padding. Use the editable-paragraph-anchor frame selected for the article's visual register and put replacement instructions outside the final article HTML.

### Manual horizontal swipe gallery exception

Use a manual swipe gallery only when the project explicitly prefers individual images over a baked portrait wall and the exact final block can be tested in the real WeChat editor.

- This is touch scrolling, not an autoplay carousel: outer `overflow-x:auto`, one oversized inner strip, and `inline-block` items. Do not add JavaScript.
- Let `N` be the final item count and `V` the desired item width as a percentage of the visible column. Set inner width to `N * V%` and each item width inside that strip to `100 / N%`.
- For compact portraits, `V=36` shows about 2.78 items per screen and leaves a visible next-card cue. Example: `N=38` gives inner width `1368%` and item width `2.63158%`.
- For uncropped landscape originals, `V=90` keeps each image readable and leaves a 10% next-card cue. Example: `N=38` gives one continuous `3420%` strip while item width remains `2.63158%`.
- Preserve the source aspect ratio by using `min-height` only for the empty placeholder. Do not keep a fixed `height` or `max-height` after insertion; let the image expand the frame naturally at `max-width:100%`.
- A very long single strip is slower to traverse than several shorter strips. If the project explicitly requires one strip, record that decision and test long-distance touch scrolling and image loading on a real phone.
- Mobile WebViews often hide the native horizontal scrollbar while idle. Add an always-visible HTML cue below the gallery: a flat track, a contrasting short thumb, and a concise left/right swipe label. Build it from flow `section` elements and solid fills.
- Without JavaScript or scroll-linked CSS, that custom thumb is a static affordance, not live progress. Do not imply that it tracks the current slide.
- Keep the final count explicit before building the strip. Each placeholder should carry a stable sequence number and source filename so replacements do not change item order.
- Keep one direct-child 1px `<p>` with a single `&nbsp;` inside every blank gallery item. Paste each photo without first deleting or selecting the anchor.
- Use a consistent 4:5 crop. Avoid names or long captions inside narrow cards unless they remain readable at 320px.
- Do not combine the swipe exception with tables, grid, scripts, or local image paths.
- A published reference may prove the mechanism is possible, but it does not prove a new block will survive editing. Paste the exact final block with real images into the draft box and test on a phone.

## Visual Direction

For deliberate, mobile-friendly articles on any topic:

- Use the supplied main visual as the palette source. Preserve its actual contrast and material cues instead of forcing a light, muted house style.
- Let the design fingerprint decide whether photos, typography, color fields, editorial rules, or negative space carry the design.
- Deep backgrounds, high contrast, gradients, shadows, and dramatic closing panels are valid in Creative mode when they fit the topic and degrade gracefully.
- Use title sizes around `38-40px` only for the opening hero. Use `27-30px` for section headings.
- Keep body copy around `15-16px` with `line-height:1.9-2`.
- Use `44-60px` before a new chapter, `20-28px` between copy and its photo, and `28-36px` between consecutive photo groups. **For WeChat, use 8px horizontal margin and let vertical whitespace create breathing room.**
- Keep one core idea per section and normally no more than two short paragraphs before the next image or divider. Mobile rhythm matters more than filling the page.
- Let one strong photo lead each chapter. After 2-3 consecutive images, insert a chapter header, node divider, or short caption before adding more media.
- Keep cards un-nested where possible. Use cards for repeated items and emphasis, not every paragraph.
- Treat visual register as a first-class decision. “Premium” does not always mean large rounded cards, warm neutrals, serif type, or decorative gold.
- If feedback says “too simple”, change composition first: strengthen the opener, contrast, section geometry, numbering, image rhythm, or editorial alignment before adding more copy or ornaments.
- If feedback says “old-fashioned”, remove serif-heavy typography, ivory/gold combinations, seal motifs, formal numerals, and imitation-newspaper composition unless the brief explicitly calls for them.
- See `references/modern-institutional-public-interest.md` for modern, solemn public-service work.
- **Reader age band** (replace `{{READER_AGE}}` per project):
  - For older readers (e.g. 中老年): bump body to 16-17px, caption to 13px, and minimum color contrast ratio to 4.5:1.
  - For general adult readers: keep body at 15-16px and caption at 12px; contrast ratio 4.5:1 minimum.
  - For younger readers: body can drop to 14-15px and caption to 11-12px; contrast ratio 4.0:1 acceptable.

## Self-Audit Before Delivery

Before handing over the HTML, run this mode-aware checklist. **Do not skip it.**

1. **Delivery boundary** - no `<script>`, event handlers, external CSS, `<style>`, or web-font dependency in the copied article fragment.
2. **Unverified layout** - zero `position:absolute`, `position:relative`, or CSS Grid declarations.
3. **Local assets** - zero local, relative, or `file:` image paths. Hosted images are allowed when the workflow requires them.
4. **Tables by default** - zero table markup unless a documented exact-block real-editor exception exists.
5. **Tag balance** - `<section>`, `<p>`, and `<span>` open/close counts match.
6. **Steady mode** - gradients and shadows are absent; flex, inline-block, large radii, and documented swipe overflow remain allowed.
7. **Creative mode** - every gradient has a solid background fallback on the same element; shadows are nonessential; the fragment remains organized when both effects are removed.
8. **Flex, overflow, and photo anchors** - compact flex rows do not squeeze text at 320px; swipe strips use intentional `overflow-x:auto`, stable item counts, and no autoplay claim; every manual image slot keeps frame styles on a `section`, uses one direct-child 1px `<p>` anchor, and has no padded instruction paragraph.
9. **Top spacing** - the first visible screen reads as an intentional opener; no accidental stack of empty wrapper, top margin, and top padding.
10. **Width alignment** - comparable blocks share deliberate baselines, and no fixed width exceeds the mobile column.
11. **Risk-word scan** - review every project-specific promise, outcome claim, and institutional term; allow a term in a disclaimer only when its use is intentional.
12. **Brand-name consistency** - follow the project's legal-name, short-name, subsidiary, and signature rules.
13. **Institutional evidence** - government designations, “唯一” claims, official logos, seals, certificates, incentives, and generated images match verified scope and cannot be mistaken for fabricated proof.
14. **Originality** - the result passes `references/original-style-synthesis.md`: no full starter skeleton, at least three content-specific decisions, at least two structural departures from the nearest library example, and no reused example names, dates, claims, prices, filenames, or mechanically repeated card stack.
15. **Phone preview** - inspect approximately 320px, 375px, and 390px widths; for Creative mode, also verify the exact final fragment in the real WeChat phone preview when available.

Fix deterministic failures before delivery. Do not make the user discover tag, path, overflow, or fallback defects for you.

## Industry-Specific Risk Words

Every industry has words that can trigger compliance review or reader backlash. Before writing, build a substitution table for the project's industry. Below are common starting points — replace with the project's own `{{RISK_KEYWORDS}}` and add domain-specific terms.

| Industry | Words to avoid | Why | Use instead |
|---|---|---|---|
| Medical / health | 医院 / 医生 / 治愈 / 包好 / 100% 有效 | Implies institutional affiliation or efficacy promises | 提个醒 / 多关注 / 通常 / 建议咨询专业医师 |
| Finance | 保证收益 / 零风险 / 100% 本金 | Regulatory prohibition on guaranteed returns | 仅供参考 / 历史业绩不代表未来 / 请审慎评估 |
| Education | 保过 / 一定考上 / 短期提分 | Outcome promises | 通常 / 多数学员 / 视个人基础而定 |
| Food / supplements | 治疗 / 预防 / 增强免疫力 | Health-claim regulation | 日常饮用 / 营养补充 / 详见产品说明 |
| Real estate | 升值 / 稳赚 / 包租 | Investment promises | 参考周边 / 长期持有 / 视市场情况 |
| Cosmetics | 祛斑 / 抗皱 / 永久 | Cosmetic-effect claims | 护肤 / 改善 / 持续使用效果因人而异 |
| Recruitment | 100% 录取 / 月入过万 | Outcome promises | 视个人能力 / 仅供参考 |

Build the table by grepping the article for any term that implies an outcome, a promise, or institutional affiliation. Update `{{RISK_KEYWORDS}}` for the project accordingly.

## Image Workflow

When local photos are present:

1. List image files with `rg --files` or a directory listing.
2. Inspect each image visually.
3. Inspect the supplied main visual first and record the sampled palette before styling the article.
4. Assign each photo a narrative role, such as opener, environment, interaction, detail, portrait wall, or closing group image.
5. If using HTML placeholders, do not put the actual images into the final WeChat fragment unless the user explicitly wants prefilled images.
6. If using baked frames, run the script and reference the framed outputs.
7. Separate evidence images from supporting illustrations. A real document or real service photo can support a factual claim; an AI-generated illustration cannot.
8. For government/public-interest illustrations, prohibit readable text, official emblems, seals, certificates, flags, brand-name rendering, and watermarks unless a verified asset is supplied as an explicit input.

Use `references/snippets.md` when a reusable WeChat HTML snippet, troubleshooting wording, or final checklist is needed.

## Optional Baked Image Frames

Use `scripts/bake_image_frame.py` only when the frame must be part of the bitmap.

Basic example (uses default colors):

```bash
python scripts/bake_image_frame.py input.png --out framed.png
```

Custom colors (override the default canvas and border to match a different brand palette):

```bash
python scripts/bake_image_frame.py input.png --out framed.png \
  --canvas-bg "#f4faf6" \
  --frame-border "#1f7b5d"
```

This creates a PNG with a white rounded frame, soft border, and a gentle shadow. It is useful for copying a standalone image, but it is not ideal when the user wants to insert a clean photo into an HTML frame.

Color customization supports `#rrggbb` and `#rrggbbaa` formats. The shadow color is fixed (a soft green-tinted blur) — change `parse_hex_color` calls in the script if a different shadow tint is needed.

## Validation Commands

For an HTML file:

```powershell
$html = Get-Content -LiteralPath 'article.html' -Encoding UTF8 -Raw
[ordered]@{
  HasScript = ($html -match '<script')
  HasStyleBlock = ($html -match '<style')
  HasEventHandler = ($html -match '\son[a-z]+\s*=')
  HasGradient = ($html -match 'linear-gradient|radial-gradient')
  HasBoxShadow = ($html -match 'box-shadow')
  HasFlex = ($html -match 'display\s*:\s*flex')
  HasInlineBlock = ($html -match 'display\s*:\s*inline-block')
  HasOverflowX = ($html -match 'overflow-x\s*:\s*auto')
  HasPositioning = ($html -match 'position\s*:\s*(absolute|relative|fixed|sticky)')
  HasGrid = ($html -match 'display\s*:\s*(inline-)?grid')
  HasLocalImg = ($html -match '<img[^>]+src\s*=\s*["''](?:file:|[A-Za-z]:\\|\.{0,2}/)')
  HasTable = ($html -match '<table|<tbody|<tr\b|<td\b')
  ImgCount = ([regex]::Matches($html,'<img\b')).Count
  SectionOpen = ([regex]::Matches($html,'<section\b')).Count
  SectionClose = ([regex]::Matches($html,'</section>')).Count
  POpen = ([regex]::Matches($html,'<p\b')).Count
  PClose = ([regex]::Matches($html,'</p>')).Count
  SpanOpen = ([regex]::Matches($html,'<span\b')).Count
  SpanClose = ([regex]::Matches($html,'</span>')).Count
}
```

Always fix `HasScript`, `HasStyleBlock`, `HasEventHandler`, `HasPositioning`, `HasGrid`, and `HasLocalImg`. `HasTable` may remain true only for a documented exception verified with the exact final block in the real WeChat editor.

Do not treat `HasFlex`, `HasInlineBlock`, or `HasOverflowX` as failures; validate their documented patterns. In Steady mode, remove gradients and shadows. In Creative mode, keep them when every gradient has a solid fallback, shadows are nonessential, and phone-preview checks pass.

If `SectionOpen != SectionClose`, `POpen != PClose`, or `SpanOpen != SpanClose`, fix the HTML before delivery.

## Common Pitfalls (Lessons Learned)

- **The WeChat editor's empty top space comes from the editor's default spacing**, not from your content. Don't add `padding-top` to compensate.
- **Local image paths silently break the whole block.** If the user reports "photo frame disappeared", check whether there's an `<img src="local...">` that failed to load and took the parent container with it.
- **Deleting the placeholder can delete the photo frame.** Keep the visual frame on a `min-height` section and put one unstyled 1px `<p>` anchor directly inside it; paste without deleting first. A section/span-only slot sends the image outside the frame, while putting frame height on the paragraph makes WeChat clone blank blocks above and below the image.
- **Dense three-column speaker walls are fragile in WeChat.** If each card carries a real photo plus text, the editor may clip the next card or leave a partial column edge. Default to single-column speaker cards unless a denser layout has been verified in the editor with real images.
- **Tables can deform even when the browser preview is perfect.** WeChat may inject horizontal scrolling and reset `td` widths. Replace asymmetric tables with `section` / `p` / `span` flow; do not keep layering width fixes onto the table.
- **Footer QR placeholders can accidentally expand to full width.** Keep the square asset inside a narrow centered `section`, not a row-level layout wrapper.
- **Horizontal margin inconsistency is a visual tax.** Cards at 18px and text at 24px look like they belong to different articles. Pick one value (8px works well) and use it everywhere.
- **Adding decoration does not fix under-designed hierarchy.** A stronger opener, section numbering, image rhythm, and alignment usually solve “too simple” more cleanly than extra cards.
- **Traditional signals can create accidental nostalgia.** Serif headlines, ivory/gold palettes, seals, and formal numerals should be intentional, not a shortcut for authority.
- **AI art is not institutional evidence.** Never use a generated certificate, seal, government logo, or official-looking document to prove a designation.
- **Self-audit is not optional.** The user is the final reviewer, but if you can catch issues before they see it, you save a round trip.

## When to escalate to a human reviewer

- Industry-specific risk words (medical, financial, legal) — get a domain reviewer to sign off the risk-word substitution table.
- 中老年 audience — get a reader over 60 to do a 30-second skim test before publishing.
- Multi-language versions — get a native speaker for each target language.
- Brand-sensitive projects — get a brand guardian to confirm the color palette matches the official brand book.

## Related skills

- For project-specific knowledge bases (brand positioning, narrative structure, project risk words), see companion knowledge-base skills such as `llm-wiki`.
- For modern government-guided or public-interest layouts, see `references/modern-institutional-public-interest.md`.
- For general HTML/CSS best practices, see web-design or frontend-design skills.
- For accessibility audits, see accessibility-review skills.
