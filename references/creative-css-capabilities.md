# Evidence-Based CSS Capabilities

Use this reference when a template or brief calls for expressive styling, or when deciding whether CSS must be removed from a WeChat article fragment.

## Evidence boundary

The local compatibility corpus contains real copy-boundary fragments and visual preview hosts. Treat CSS inside `<!-- 微信公众号复制开始 -->` / `<!-- 微信公众号复制结束 -->` as article evidence. For an unmarked preview document that was tested as a complete article, treat the inner article `<section>` inside the phone wrapper as evidence. Do not treat the preview host's `<style>`, fixed phone width, page shadow, or browser-only wrapper as publishable article markup.

### Scoped compatibility evidence

The complete `Visual Web Lab / 02` copy-boundary fragment passed a WeChat compatibility check. That exact fragment combines solid fallbacks, gradients, shadows, advanced underline, tabular numerals, `box-decoration-break`, outline, scroll snap, `text-emphasis`, vertical writing, a small rotation, and an `aspect-ratio` placeholder. Editor entry, editor version, device width, and declaration-level preservation remain unknown.

Treat this as exact-fragment evidence, not universal property support. New copy, nesting, images, editor versions, or devices still require a fresh paste and phone-preview regression.

The complete `Signal Editorial / 03` fragment also passed a WeChat compatibility check. That exact fragment adds radial and repeating gradients, solid-fill `-webkit-text-stroke`, `text-wrap:balance`, gradient `border-image`, short flex composition, a vertical label, and mixed 4:5 / 16:9 media placeholders. Editor and device details remain unknown, so the same exact-fragment boundary applies.

The complete `Paper Cut Artbook / 06` fragment passed a WeChat compatibility check. That exact fragment replaces the earlier dark numbered editorial skeleton with a cool-white art-book composition: multi-line cloned highlights, an arch-shaped lead placeholder, short vertical marginalia, a folded-corner quote, deliberately alternating dense and sparse fields, asymmetric image corners, and a manual contact-sheet swipe strip. The palette uses graphite and white as the reading field, muted lavender and sage as the two accent families, and coral only as a small correction color. Treat this as exact-fragment evidence; the compatibility claim does not promote `clip-path`, `writing-mode`, `box-decoration-break`, or scroll snap to universal support outside the tested nesting and copy.

The complete `Contour Index / 07` fragment passed a WeChat compatibility check. That exact fragment adds repeating radial contour fields, an organic lead placeholder, stepped flex rows, a circular image placeholder, repeated numeric labels, and a manual sample-drawer strip. Treat the compatibility result as exact-fragment evidence. Originality status remains insufficient because the mobile silhouette stays too close to Paper Cut: white reading field, large left-aligned title, one large organic lead image, sequential open editorial chapters, a rounded secondary image, swipe strip, and open typographic ending. Keep compatibility success and originality failure separate.

## Delivery modes

### Steady mode

Use inline styles, flow layout, solid fills, borders, alpha colors, large or pill radii, `inline-block`, compact `flex`, and verified manual `overflow-x:auto` strips. Prefer this mode when the brief emphasizes predictable editing, regulated information, or many future copy changes.

### Creative mode

Allow everything in Steady mode plus controlled `linear-gradient` / `radial-gradient` and `box-shadow`. Use a solid `background` immediately before every gradient as a fallback. Keep shadows decorative rather than structural, and ensure the design remains legible if WeChat removes either effect. Validate the exact final fragment in phone preview.

Creative mode is a supported delivery mode, not an error condition. Use Creative mode for bold, original, experimental, launch, youth, culture, fashion, technology, and strong-brand work when beneficial to the requested visual impact.

## Capability matrix

| Capability | Status | Rules |
|---|---|---|
| Inline `section` / `p` / `span` styling | Proven core | Keep all required styling inline. |
| Solid backgrounds, borders, alpha colors | Proven core | Use freely with readable contrast. |
| Large and pill `border-radius` | Proven core | Values such as `22px`, `30px`, `50%`, and `999px` are allowed. |
| `display:inline-block` | Proven core | Use for markers, inline rules, badges, and compact rows. |
| `display:flex` | Proven core | Use for short two-part heroes, CTA/QR rows, and compact information rows; supply a single-column fallback for copy-heavy or image-heavy content. |
| `overflow-x:auto` + oversized strip | Proven exception | Use only for intentional manual swipe galleries; no autoplay claim or JavaScript. |
| `overflow:hidden` | Proven core | Use for clipped fills, rounded surfaces, and frames. |
| `box-shadow` | Creative | Keep subtle, nonessential, and easy to remove; verify phone preview. |
| Gradients | Creative | Precede with a solid fallback on the same element; verify color and contrast after paste. |
| Radial / repeating gradient fields | Creative candidate | Keep these fields decorative. Use `background`, then `background-color`, then `background-image`; a later `background` shorthand can reset the solid color to transparent. |
| Advanced underline (`text-decoration-thickness`, `text-underline-offset`) | Low-risk candidate / real-editor pending | Use on short phrases; the text must remain readable if the underline details are stripped. |
| `font-variant-numeric:tabular-nums` | Low-risk candidate / real-editor pending | Useful for dates, prices, rankings, and compact data; ordinary proportional numerals are the fallback. |
| `box-decoration-break:clone` | Low-risk candidate / real-editor pending | Use for multi-line inline highlights; keep the underlying background and text readable without cloned edges. |
| `outline` / `outline-offset` | Low-risk candidate / real-editor pending | Use only as a second decorative edge; retain a normal border as the structural fallback. |
| `text-wrap:balance` | Low-risk candidate / real-editor pending | Use only on short headings or pull quotes; ordinary wrapping must remain acceptable. |
| `-webkit-text-stroke` | Experimental / real-editor pending | Keep a readable solid `color`; stroke may add contrast but must never be paired with transparent fill. |
| Gradient `border-image` | Experimental / real-editor pending | Declare an ordinary solid border first; the border must remain meaningful when the image layer is stripped. |
| CSS scroll snap | Experimental / real-editor pending | Add only to an already valid manual `overflow-x:auto` strip. If snap is stripped, ordinary touch scrolling must still work. |
| `text-emphasis` | Experimental / real-editor pending | Limit to short Chinese phrases or headings; never encode meaning only in the emphasis marks. |
| `writing-mode:vertical-rl` | Experimental / real-editor pending | Restrict to short editorial labels that also fit horizontally if the property is removed. |
| Small `transform:rotate(...)` | Experimental / real-editor pending | Use approximately 1-3 degrees on short labels only; do not rotate body copy or required data. |
| `aspect-ratio` | Experimental / real-editor pending | Pair with `min-height`; do not force a fixed height after a real image is inserted. |
| Asymmetric flow composition | Supported | Build with margin, padding, borders, widths, and inline/flex flow, not positioning. |
| `<style>`, external CSS, web fonts | Preview-only / prohibited in delivery | Inline the final styles. |
| `position:absolute` / `position:relative` | Unverified | Do not use until the exact publishing path is proven. |
| CSS Grid | Unverified | Use flow, inline-block, or compact flex instead. |
| `<table>` layout | Fragile exception | Avoid by default; retain only after exact-block editor verification. |
| Script and event handlers | Prohibited | Deliver static HTML or a static bitmap. |

## Candidate promotion protocol

Rendering in Chrome or Edge does not promote candidate properties to proven capabilities.

1. Test one candidate family per small copy-boundary block so failures are attributable.
2. Build a conservative version that removes every candidate declaration before opening the real editor.
3. Verify 320px, 375px, and 390px browser widths for outer overflow, clipping, and content order.
4. Paste the exact final block into the WeChat draft box and check 375px and 390px phone previews.
5. Record whether the declaration was preserved, rewritten, or removed; include screenshots and editor/device context.
6. Promote a candidate to supported only after both the enhanced block and the fallback remain readable through the actual publishing path.

Do not use `background-clip:text` with transparent text, `filter`, `backdrop-filter`, `mix-blend-mode`, `clip-path` on semantic content, `<details>/<summary>`, or complex multi-column layout in the final article fragment. Failure modes can hide content, alter reading order, or depend on browser state that the editor does not preserve.

## Original design rules

### Iteration difference gate

When a new exploration follows an accepted or rejected draft, do not count palette swaps and isolated shape changes as a new direction. Compare the new draft with the nearest prior draft across opener, section sequence, edge geometry, image silhouette, recurring motif, repeated-block treatment, and closing device. Change at least four of those seven dimensions before presenting the result as a new concept.

Component-level differences are necessary but not sufficient. Also apply a **gestalt separation gate** by comparing 320px or 375px full-page screenshots, preferably as small grayscale thumbnails. Compare six whole-page axes: first-screen light/dark mass, dominant text alignment, container archetype, image aspect-ratio rhythm, vertical density curve, and closing mass. Change at least four of the six. Reject the new direction when the thumbnails still share the same large white zones, title position, dominant image mass, chapter cadence, or ending silhouette even if labels, radii, motifs, and CSS properties differ.

For a corrective redesign after gestalt rejection, choose a clearly different composition family before styling. Examples include full-width horizontal color bands instead of an inset white editorial column, centered title cards instead of a large left-aligned headline, hard widescreen frames instead of organic or arched images, continuous cinematic sequences instead of open chapter stacks, or a closed credit panel instead of an airy typographic ending.

Keep palette roles explicit. Use one neutral reading field, one primary accent family, one secondary accent family, and at most one small correction color. Four or more saturated accents competing across large surfaces usually read as an undirected technology poster rather than mature editorial art direction.

- Use the synthesized design fingerprint as a visual grammar, not a locked wireframe. Preserve contrast, type hierarchy, edge language, and rhythm while changing composition to fit the story.
- Do not turn every section into the same rounded card. Mix open text bands, rules, numbered anchors, solid panels, image pauses, asymmetric inset blocks, and one deliberate closing device.
- Let one feature dominate: oversized type, deep color field, editorial rules, irregular rhythm, or one gradient surface. Do not maximize all effects at once.
- Use deep backgrounds when required by the chosen style. Protect readability with high-contrast body text and light content surfaces where long reading begins.
- Keep mobile text stable: no viewport-scaled font sizes, negative letter spacing, or fixed heights around variable copy.
- Every advanced effect must degrade gracefully. Removing gradients and shadows must not erase hierarchy, content, borders, or tap targets.
- For transparent multi-background decoration, do not assume an earlier `background:#color` remains underneath a later `background:<gradients>` shorthand. Preserve the base with an explicit `background-color` and put the effect in `background-image`.

## Verification

For Creative mode, verify at approximately 320px, 375px, and 390px widths and in the real WeChat phone preview when available. Check intended gradient hue, unclipped shadows, stable flex text, working horizontal strips, and complete readability after removing gradient and shadow declarations.
