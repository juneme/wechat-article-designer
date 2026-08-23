# SVG Design Genes

Use this reference to compose SVG editorial components for WeChat articles. It contains only reusable design decisions; implementation history and per-article working artifacts stay outside the Skill.

## Core thesis

- Treat SVG as an editorial scene or micro-interaction, not as the article's layout system.
- Give each SVG one primary editorial job: reveal, compare, trace, emphasize, transform, establish atmosphere, pace a transition, or build a seasonal narrative world.
- Keep essential facts and actions understandable in the SVG's initial state or the surrounding article prose. Do not require a duplicated fallback component.
- Use motion to clarify sequence or state, or to create a content-specific sense of air, light, material, weather, distance, or time. Ambient movement is valid when its pace supports reading and its absence does not erase meaning.

## Construction grammar

- Use one responsive outer `svg` per scene with a mobile-first `viewBox`, normally `0 0 360 H`, and `style="display:block;width:100%;height:auto;margin:0;"`. Values such as `width="360"` on inner SVG geometry are viewBox coordinates, not CSS pixels; the rendered outer width remains within the 320px article column.
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
| Ambient atmosphere | Slowly translate, fade, or reshape a small number of leaves, birds, steam lines, light bands, rain marks, or related content-native forms | Keep the first frame composed and avoid motion that competes with reading |
| Wipe reveal | Animate the width of an opaque cover rectangle | Do not use animated masks |
| Aperture or expansion | Morph a visible path between compact and expanded shapes | Do not use animated `clipPath` |
| Color movement | Animate solid fills across a small set of color bands | Do not depend on SVG gradients or animated gradient stops |
| Focus simulation | Crossfade stacked crisp and offset text or shapes | Do not use blur filters |
| Object travel | Prefer a simple one-axis group translation | Exclude `animateMotion` and coordinated `cx` plus `cy` orbit animation |

## Composition and pacing

- Use one primary behavior per SVG scene. Multiple scenes are valid when each advances a different narrative beat and open reading space separates them; do not impose a scene-count quota.
- Keep click feedback short and decisive; finish in a stable readable state with `fill="freeze"` when appropriate.
- Keep ambient loops slow enough to read and make the first frame meaningful.
- Repeat the first visual state at the end of a loop when a reset would otherwise flash or jump.
- Keep moving labels short. Put paragraphs, evidence, and instructions in HTML rather than SVG text.
- Establish a clear focal relationship inside each scene. Quiet scenes may use one dominant shape; a deliberate miniature poster or layered landscape may use richer geometry when the mobile silhouette remains legible.

## Color and typography

- Use a coherent solid-color hierarchy with sufficient text contrast; there is no fixed color-count quota. Related shades, seasonal transitions, and image-derived colors are valid when field, ink, signal, and atmosphere remain distinguishable. Color cannot be the only state cue.
- Use direct `text` elements with explicit `x`, `y`, `fill`, and concise native SVG `font-*` attributes. SVG coordinate text is not an HTML flow-text role and does not need `data-type-role`, paragraph wrapping, `text-indent`, or the full HTML typography signature. Accessibility-only `title` and `desc` need no visible typography.
- Avoid `textPath`, filters, gradients, and font-dependent visual tricks.
- Keep long Chinese copy in ordinary HTML so editor font substitution or fixed SVG coordinates cannot damage reading.

## Content contract

- Interaction may enrich sequence, comparison, or discovery, but it cannot be the sole carrier of a deadline, condition, warning, contact, source, or required action.
- The first frame must be meaningful and must make the interaction legible without instructional paragraphs.
- Put evidence, qualifiers, captions, and long explanations in the surrounding HTML reading flow.
- Removing motion should leave a coherent SVG state and correct article reading order.

## Delivery boundary

Components built from these genes use the standard article quality gates: content integrity, rendered outer mobile width, contrast, hosted assets, and draft validation. SVG child geometry is audited as viewBox coordinates, while surrounding HTML remains under the normal typography contract. Do not add a separate SVG validation workflow. A genuinely new mechanism outside this vocabulary may be explored when it serves the article, and its working artifacts stay outside the Skill.
