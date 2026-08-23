# WeChat CSS Capability and Fallback Rules

Use this reference to choose Steady or Creative delivery and to decide what must survive editor rewriting.

Browser rendering proves only browser behavior. Local audits detect known hazards but do not prove that the WeChat editor preserves a declaration. The exact final fragment and phone preview are the authority for any conditional capability.

## Required effects decision

Every new full article and substantial redesign must record one of these outcomes in `design-contract.json`:

| Outcome | Choose when |
|---|---|
| `none` | Type, spacing, color, rules, and media already carry the reading job; motion or expressive effects would be decorative or cannot be tested |
| Static expressive CSS | A gradient, shadow, outline, transform, or related visual treatment materially supports hierarchy and has a readable solid fallback |
| SVG/SMIL | Motion materially clarifies one sequence, comparison, reveal, state change, or emphasis and follows `svg-design-genes.md` |

The decision is mandatory; the effect is not. Record the semantic job, static state, fallback, compatibility risk, and test obligation. Do not add an effect only because Creative capability exists. Conditional CSS and real tables require a recorded exception and readable fallback before draft creation; the user may perform the exact editor and phone review on the resulting Creative draft.

CSS keyframe animation is excluded from publishable fragments because it depends on a `style` block and `@keyframes`, which the article contract forbids and the editor may rewrite. Use the established inline SVG/SMIL vocabulary when meaningful motion is required.

## Capability matrix

| Tier | Suitable techniques | Rule |
|---|---|---|
| Baseline | Inline block flow, solid color, font size/weight/line-height, spacing, borders, moderate radius, fixed or percentage widths within the column, ordinary images | Safe basis for both modes; still inspect mobile widths |
| Conditional | Compact flex rows, alpha colors, `inline-block`, manual overflow, unusual image crops, `aspect-ratio` | Use only when information remains readable after rewrite; test the exact final copy |
| Expressive | Gradients, shadows, outlines, transforms, writing-mode, text emphasis, advanced decoration | Creative mode only; provide a solid static fallback and real-editor preview |
| SVG editorial | Inline SVG and SMIL using the vocabulary in `svg-design-genes.md` | Creative mode; preserve essential meaning in the initial state or surrounding prose and use the standard article checks |
| Excluded | Scripts, event handlers, external CSS/fonts, hover-only content, CSS Grid, positioned layout, sticky behavior, iframes/embeds, oversized strips, interaction-required information | Do not ship |

Tables are excluded from visual layout. Use a table only when the content is truly tabular and the exact final result has passed editor and phone testing; otherwise use labeled flow rows.

## Steady mode

Choose Steady when the article is institutional, high-risk, evidence-heavy, or frequently edited after handoff. Lack of a prior real-editor test alone does not force Steady when a safe Creative draft can be created for user review.

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

Creative mode may use SVG when the component materially supports the article and follows `svg-design-genes.md`. Do not introduce a separate experiment or evidence workflow for the established vocabulary.

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

### SVG editorial components

Use SVG for one clear editorial job and keep the first frame meaningful. Essential facts, qualifiers, deadlines, contacts, and actions belong in the initial state or surrounding HTML. Follow the construction and motion vocabulary in `svg-design-genes.md`; no separate SVG validation workflow or duplicate fallback wrapper is needed.

## Release gate

Use the stricter outcome whenever evidence is incomplete:

- no prior real-editor test: create only a readable-fallback Creative draft, then let the user decide whether to retain or simplify it;
- editor strips an optional effect: keep the readable fallback;
- editor changes structure or hides content: remove the pattern;
- a pattern needs user explanation to work: replace it with visible static reading order.
- the effects plan is missing or differs from the fragment: return to the design contract before delivery.
