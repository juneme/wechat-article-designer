# WeChat CSS Capability and Fallback Rules

Use one capability model for every article. Do not classify a whole design by a conservative or expressive label. Evaluate each technique by its semantic job, readable initial state, fallback, and behavior in the exact WeChat editor result.

Browser rendering proves only browser behavior. Local audits detect known hazards but do not prove that the WeChat editor preserves a declaration. The final draft and phone preview remain the rendering authority for conditional techniques.

## Required effects decision

Every new full article and substantial redesign records one of these implementation outcomes in `design-contract.json`:

| Outcome | Choose when |
|---|---|
| `none` | Type, spacing, color, rules, and media already carry the reading job |
| Static expressive CSS | A gradient, shadow, outline, transform, or related treatment materially supports hierarchy and has a readable solid fallback |
| SVG/SMIL | Motion or vector composition materially supports explanation, atmosphere, pacing, emotional transition, seasonal change, narrative world-building, or emphasis and follows `svg-design-genes.md` |

The decision is mandatory; an effect is not. The `plan` command derives the outcome from the selected HTML. Record or retain the semantic job, static state, fallback, compatibility risk, and test obligation. Do not add a technique merely because it is available.

CSS keyframe animation is excluded because publishable fragments cannot contain a `style` block or `@keyframes`, and the editor may rewrite them. Use the established inline SVG/SMIL vocabulary when meaningful motion is required.

## Unified capability matrix

| Capability | Suitable techniques | Delivery rule |
|---|---|---|
| Core inline flow | Blocks, solid colors, type size/weight/leading, spacing, borders, radii, mobile-safe widths, ordinary images | Use freely when it serves the article; inspect final mobile widths |
| Conditional layout | Compact flex rows, `inline-block`, manual overflow, unusual crops, `aspect-ratio`, real data tables | Keep information readable after rewrite and inspect the exact final copy |
| Expressive presentation | Gradients, shadows, outlines, transforms, writing-mode, text emphasis, advanced decoration | Provide a readable solid or ordinary-flow state; editor uncertainty is a warning, not a reason to downgrade the whole article |
| SVG editorial | Inline SVG and SMIL using `svg-design-genes.md` | Preserve essential meaning in the initial state or surrounding prose and use the normal article checks |
| Excluded | Scripts, event handlers, external CSS/fonts, hover-only content, CSS Grid, positioned layout, sticky behavior, iframes/embeds, oversized strips, interaction-required information | Do not ship |

Tables are excluded from visual layout. Use a table only when the content is truly tabular and the exact result has passed editor and phone testing; otherwise use labeled flow rows.

## Selection rules

Use any allowed capability when it materially supports the article's visual thesis. Institutional, evidence-heavy, and service content may still use expressive treatments; poetic or promotional content may still be restrained. Atmosphere and emotional pacing are valid editorial jobs, not decoration by definition. Risk follows the declaration and fallback, not an article label.

For every nonessential effect:

1. place a readable solid declaration before an expressive declaration when CSS fallback order applies;
2. keep text contrast adequate on the solid fallback;
3. remove the effect mentally and confirm hierarchy, order, facts, and action still work;
4. test final content rather than a demonstration string;
5. report unverified editor behavior as a warning for the user's final draft review.

Use as many supporting signals and SVG scenes as the composition genuinely needs, but give each one a distinct job. Repetition, rhythm, atmosphere, and visual peaks should come from the article rather than a fixed effect quota.

## Fragile patterns

### Compact flex

Use flex for bounded relationships such as a number plus a short label. Long headings, salary strings, contacts, URLs, and translated text should stack. The fallback is ordinary vertical flow.

### Manual horizontal swipe

Prefer vertical flow when it communicates the same relationship. If swipe is necessary:

- the scroll container owns `overflow-x:auto`;
- slide items are direct children;
- each item has a mobile-safe width;
- no ancestor clips horizontal overflow;
- there is no intermediate strip wider than `100%`;
- a complete vertical reading order remains available.

### Alpha, gradient, and shadow

Alpha layers must not be the sole source of contrast. A gradient needs a solid field fallback. A shadow may indicate depth but must not define the only visible boundary. Contrast over an image, gradient, or unparseable layer produces a manual-review warning; it does not require a capability exception before drafting.

### Crop and ratio

Reserve stable dimensions so replacement images do not shift the layout. For manual placeholders, the frame owns height. For hosted images, prefer natural dimensions unless a tested crop serves the narrative.

### SVG editorial components

Use SVG for a clear editorial job and keep its first frame meaningful. Atmospheric jobs such as wind, drifting leaves, birds, steam, light, and seasonal transition are valid when they establish place or pace instead of obscuring copy. Essential facts, qualifiers, deadlines, contacts, and actions belong in the initial state or surrounding HTML. Follow `svg-design-genes.md`; no separate SVG validation workflow or duplicate fallback wrapper is needed.

## Release behavior

- Without prior real-editor testing, create the readable-fallback draft and report a review warning; the user decides whether to retain or simplify the technique.
- If the editor strips optional presentation, retain the readable fallback.
- If the editor changes structure or hides content, remove the failing pattern.
- If a pattern needs user explanation to reveal essential information, replace it with visible reading order.
- If the selected fragment changes after `plan`, rerun `plan` before release.
