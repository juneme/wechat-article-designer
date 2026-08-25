# CSS and SVG Capabilities

There is one expressive surface. Inline HTML/CSS and inline SVG/SMIL may be combined according to the article; they are not separate quality levels.

## Capability boundary

| Confidence | Examples | Treatment |
|---|---|---|
| Stable | block flow, inline text, solid fields, borders, radius, ordinary spacing, width up to 100%, responsive images | Use directly |
| Inspect in editor | flex, gradients, shadows, transforms, filters, clipping, masks, writing mode, horizontal overflow, tables, complex SVG, SMIL | Preserve a readable initial state and inspect the actual draft |
| Do not ship | scripts, event handlers, external styles/fonts, dangerous CSS URLs, CSS Grid, absolute/fixed/sticky layout, hover-only or interaction-required information | Rewrite |

An editor-test warning is not a design failure. Keep the intended composition unless the real editor proves that a feature is removed or materially broken.

## Inline CSS

WeChat fragments cannot carry a reliable `<style>` block, `@keyframes`, `@font-face`, or imported stylesheet. Keep declarations inline. CSS keyframe animation is therefore out of bounds, but static expressive CSS remains available.

Gradients, shadows, opacity, transform, writing mode, filters, and flex layouts may support the composition. Give important text a readable base field and do not let a fragile declaration carry the sole copy, action, or warning.

## SVG and SMIL

Use SVG when coordinate composition or time changes meaningfully improves the article. SMIL can reveal, trace, morph, drift, pulse, crossfade, or cycle without scripts. A meaningful first frame and nearby HTML make the piece resilient if animation is stripped.

The article may use several SVG scenes. Their number, palette, dimensions, and motion style come from the narrative density curve, not a quota.

## Width

The CSS rendered content column has a hard 320px ceiling for fixed dimensions. Prefer percentages up to 100% and content insets. SVG `viewBox="0 0 360 H"` uses internal coordinates and is not a 360px CSS width when the outer SVG is `width:100%`.

Avoid a fixed-width strip wider than 320px even when `max-width:100%` could shrink it; the publishing boundary intentionally rejects that construction. Horizontal swipe is acceptable only with tested direct children, each within the hard limit, and a readable non-swipe order.

## Fallback thinking

Fallback is a property of an effect, not a reason to classify the whole article:

- gradient falls back to a compatible solid field;
- shadow may add depth but does not define the sole boundary;
- animation begins in a coherent state;
- clipped or masked imagery retains an understandable crop if the effect is lost;
- a flex group keeps a sensible source order;
- essential information exists in text, not only in a transformed visual state.

## Review sequence

1. Inspect the exact fragment in a browser at 320px, 375px, and 390px.
2. Check the actual WeChat editor and phone draft whenever conditional features matter.
3. Treat parser warnings as a testing queue, not an instruction to remove creative effects.
4. Fix only observed breakage or a hard safety/width/readability violation.
