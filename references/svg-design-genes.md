# SVG Design Genes

Use this reference to compose SVG editorial components for WeChat articles. It contains only reusable design decisions; implementation history and per-article working artifacts stay outside the Skill.

## Core thesis

- Treat SVG as an editorial micro-interaction, not as the article's layout system.
- Give each SVG one semantic job: reveal, compare, trace, emphasize, transform, or cycle.
- Keep essential facts and actions understandable in the SVG's initial state or the surrounding article prose. Do not require a duplicated fallback component.
- Use motion to clarify sequence or state. Do not add continuous movement when it does not improve understanding.

## Construction grammar

- Use one responsive outer `svg` with a mobile-first `viewBox`, normally `0 0 360 H`, and `style="display:block;width:100%;height:auto;margin:0;"`.
- Use inline presentation attributes, simple geometry, direct SVG text, solid fills, and unique element IDs.
- Add `role="img"`, a concise `title`, and a `desc` that explains the visible behavior without depending on it.
- Keep the SVG free of scripts, event attributes, `foreignObject`, external styles, and web fonts.
- Use final HTTPS WeChat image URLs when an SVG `<image>` is needed. Do not use local, relative, temporary, or non-WeChat asset paths.
- Use unique IDs only where animation targets or accessibility labels require them. Do not add experiment or evidence attributes.

## Motion vocabulary

| Editorial intent | Preferred primitive | Rewrite or exclude |
|---|---|---|
| Click to reveal | Animate `opacity` on one complete detail layer | Keep the prompt and essential conclusion readable before interaction |
| Click to change state | Animate one target's `fill`, radius, scale, or layer opacity from the same click | Replace delayed multi-element chains with one direct state change |
| Click to switch image | Crossfade two `<image>` layers or move one opaque cover | Use final hosted images and keep identity or conclusion in nearby HTML |
| Horizontal sequence | Translate an ordinary group with `animateTransform` | Do not move text with `textPath` |
| Direction or shape change | Morph path `d` or polygon `points` | Replace rotation-dependent storytelling with explicit shape states |
| Draw or pulse emphasis | Animate `stroke-dashoffset`, `stroke-dasharray`, or `stroke-opacity` on a solid stroke | Avoid gradient strokes |
| Wipe reveal | Animate the width of an opaque cover rectangle | Do not use animated masks |
| Aperture or expansion | Morph a visible path between compact and expanded shapes | Do not use animated `clipPath` |
| Color movement | Animate solid fills across a small set of color bands | Do not depend on SVG gradients or animated gradient stops |
| Focus simulation | Crossfade stacked crisp and offset text or shapes | Do not use blur filters |
| Object travel | Prefer a simple one-axis group translation | Exclude `animateMotion` and coordinated `cx` plus `cy` orbit animation |

## Composition and pacing

- Use at most one primary SVG behavior in an ordinary article.
- Keep click feedback short and decisive; finish in a stable readable state with `fill="freeze"` when appropriate.
- Keep ambient loops slow enough to read and make the first frame meaningful.
- Repeat the first visual state at the end of a loop when a reset would otherwise flash or jump.
- Keep moving labels short. Put paragraphs, evidence, and instructions in HTML rather than SVG text.
- Prefer one dominant shape, one supporting label, and one restrained accent over a dense miniature poster.

## Color and typography

- Use two to four solid colors with sufficient text contrast; color cannot be the only state cue.
- Use direct `text` elements with explicit `x`, `y`, `fill`, `font-size`, and optional `font-weight`.
- Avoid `textPath`, filters, gradients, and font-dependent visual tricks.
- Keep long Chinese copy in ordinary HTML so editor font substitution or fixed SVG coordinates cannot damage reading.

## Content contract

- Interaction may enrich sequence, comparison, or discovery, but it cannot be the sole carrier of a deadline, condition, warning, contact, source, or required action.
- The first frame must be meaningful and must make the interaction legible without instructional paragraphs.
- Put evidence, qualifiers, captions, and long explanations in the surrounding HTML reading flow.
- Removing motion should leave a coherent SVG state and correct article reading order.

## Delivery boundary

Components built from these genes use the standard article quality gates: content integrity, mobile width, typography, contrast, hosted assets, and draft validation. Do not add a separate SVG validation workflow. A genuinely new mechanism outside this vocabulary may be explored only when requested, and its working artifacts stay outside the Skill.
