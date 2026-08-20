# WeChat CSS Capability and Fallback Rules

Use this reference to choose Steady or Creative delivery and to decide what must survive editor rewriting.

Browser rendering proves only browser behavior. Local audits detect known hazards but do not prove that the WeChat editor preserves a declaration. The exact final fragment and phone preview are the authority for any conditional capability.

## Capability matrix

| Tier | Suitable techniques | Rule |
|---|---|---|
| Baseline | Inline block flow, solid color, font size/weight/line-height, spacing, borders, moderate radius, fixed or percentage widths within the column, ordinary images | Safe basis for both modes; still inspect mobile widths |
| Conditional | Compact flex rows, alpha colors, `inline-block`, manual overflow, unusual image crops, `aspect-ratio` | Use only when information remains readable after rewrite; test the exact final copy |
| Expressive | Gradients, shadows, outlines, transforms, writing-mode, text emphasis, advanced decoration | Creative mode only; provide a solid static fallback and real-editor preview |
| Excluded | Scripts, event handlers, external CSS/fonts, hover-only content, CSS Grid, positioned layout, sticky behavior, iframes/embeds, oversized strips, interaction-required information | Do not ship |

Tables are excluded from visual layout. Use a table only when the content is truly tabular and the exact final result has passed editor and phone testing; otherwise use labeled flow rows.

## Steady mode

Choose Steady when the article is institutional, high-risk, evidence-heavy, frequently edited after handoff, or cannot be tested in the real editor.

- Use solid fields, ordinary borders, stable single-column flow, and restrained radii.
- Prefer type, spacing, rules, and image rhythm over decorative containers.
- Keep every fact, qualifier, caption, and action visible without interaction.
- Stack compact rows when the longest real text could squeeze.

## Creative mode

Choose Creative only when the expressive treatment supports the article's thesis and the final fragment can be previewed.

For every nonessential effect:

1. place a readable solid declaration before the expressive declaration when CSS fallback order applies;
2. keep text contrast adequate on the solid fallback;
3. remove the effect mentally and confirm hierarchy, order, and action still work;
4. test the final content rather than a demonstration string.

Creative mode is not permission for more effects. Use one primary expressive behavior and at most a small number of supporting signals.

## Fragile patterns

### Compact flex

Use flex only for a short, bounded row such as a number plus a short label. Long headings, salary strings, contacts, URLs, or translated text should stack. The fallback is ordinary vertical flow.

### Manual horizontal swipe

Prefer vertical flow. If swipe is necessary:

- the scroll container owns `overflow-x:auto`;
- slide items are its direct children;
- each item has a mobile-safe width;
- no ancestor clips horizontal overflow;
- there is no intermediate strip wider than `100%`;
- a complete vertical version is available.

### Alpha, gradient, and shadow

Alpha layers must not be the sole source of contrast. A gradient needs a solid field fallback. A shadow may indicate depth but must not define the only visible boundary.

### Crop and ratio

Reserve a stable frame size so replacement images cannot shift the layout. For manual placeholders, the frame owns height. For hosted images, prefer natural image dimensions unless a tested crop is essential.

## Release gate

Use the stricter outcome whenever evidence is incomplete:

- no real-editor test: ship Steady;
- editor strips an optional effect: keep the readable fallback;
- editor changes structure or hides content: remove the pattern;
- a pattern needs user explanation to work: replace it with visible static reading order.
