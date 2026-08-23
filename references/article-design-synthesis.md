# Original Style Synthesis

Use this reference for every new full article and substantial redesign. Minor revisions preserve the current system and revisit only affected decisions. The goal is not to select the closest learned page; it is to synthesize an article-specific system from the complete living grammar.

## Read the article before design

Build a private content map:

- target reader and reading context;
- narrator and ownership;
- literal topic and desired action;
- verified facts, evidence images, and claim limits;
- urgent vs reflective, youthful vs mature, ceremonial vs everyday;
- dense information vs visual storytelling;
- image-led, type-led, or evidence-led;
- dominant objects, metaphors, places, dates, routes, materials, or processes;
- expected reading duration and likely points of reader fatigue.

Do not request a visual-template selection when these signals are sufficient.

## Build writing and structure first

1. Read `editorial-writing-grammar.md` and make the unstyled draft establish a defensible promise, reasoning path, and evidence boundary.
2. Read `modular-composition-system.md` and map payload to semantic module roles.
3. Read `typography-system.md` and identify the display, section, item, body, label, caption, and data jobs supported by the copy.
4. Sketch the density curve: where the article declares, proves, pauses, explains, asks, and closes.

Do not choose a surface, card, or source-derived visual move until these decisions exist.

## Synthesize across the living grammar

Read `design-grammar.md`. Evaluate every normalized dimension against the content map:

1. **Visual thesis** - one sentence explaining why the article should look this way.
2. **Palette behavior** - field, ink, primary signal, secondary signal, correction color, and image authority.
3. **Type behavior** - hierarchy, weight contrast, data voice, line rhythm, and label behavior.
4. **Opening mechanism** - literal typographic field, photo-led statement, editorial masthead, evidence preview, numbered prologue, or another content-native device.
5. **Section rhythm** - open prose, evidence ledger, alternating media turns, indexed chapters, full bands, or a custom progression.
6. **Geometry** - one primary edge language and any semantically justified exception.
7. **Image behavior** - evidence frame, full-width pause, portrait study, contact sheet, object sequence, or no image.
8. **Recurring motif** - derive it from the article's subject, never from a generic style label.
9. **Closing device** - resolve the argument, ownership, or action without repeating the opener.
10. **Atmosphere and compatibility behavior** - how place, season, material, pacing, or emotional transition enters the design; the readable static state, likely editor risks, and fallback for each conditional technique.

The living grammar contains only normalized design decisions, not source records. Normal generation must not reconstruct a source catalog or pick a source winner.

## Explore, select, then freeze the private design contract

Use `design-contract.json` as the only editable contract source. Record two or three lightweight directions when useful, select the strongest, and implement that candidate while the contract remains `EXPLORING`. Complete editorial facts, evidence limits, media authority, route decisions, and other information that markup cannot prove. Then run the workspace `plan` command. It extracts machine-observable implementation values from the selected HTML, changes the contract to `PLANNED`, and freezes that design for release. The enforced release command generates `checks.fragment_sha256`, verifies the exact fragment, and promotes it to `READY`. Inspect but never edit the generated `design-contract.md`.

Record all of the following:

| Dimension | Minimum concrete record |
|---|---|
| Exploration | Direction names and theses, signature moves, compatibility risks, selected direction, and selection reason |
| Editorial and evidence | Reader situation, central friction, judgment, reader gain, source facts, evidence boundary, and desired action |
| Composition | Module manifest, one dominant module, reading order, widths, outer baseline, content inset, density curve, and semantic spacing scale |
| Typography | Every used HTML `data-type-role` with one or more observed font-stack, size, line-height, weight, alignment, letter-spacing, and machine-parseable wrapping variants; also record role relationships, body paragraph rhythm, and the default `2em` first-line indent or its exception. Only continuous prose carries `data-indent-role="body-paragraph"`. SVG coordinate text is outside this role contract. |
| Color | Exact hex values for field, ink, primary signal, secondary signal, correction, and image-derived support; state where each is allowed and how contrast survives without effects |
| Media | Each asset's reader job, factual authority, order, crop or aspect behavior, caption/source need, and placeholder or hosted state |
| Geometry and motif | Primary edge language, radius policy, dividers, surface behavior, content-native motif, recurrence limit, and exceptions |
| Effects and motion | Select `none`, static expressive CSS, or SVG/SMIL; state the editorial job, including explanation, atmosphere, pacing, emotional transition, or world-building where relevant, plus the static first state, fallback, compatibility risk, and exact-fragment test obligation |
| Delivery | Backend readiness result, draft or local-preview target, must-keep decisions, avoid decisions, fallback, and stop condition |

Machine relationships are explicit in HTML markers. Give modules `data-module-id` and `data-density`; mark one horizontal-padding implementation each for `data-layout-role="outer-baseline"` and `"content-inset"`; identify representative semantic spacing and important recurring geometry with `data-spacing-role` and `data-geometry-role`; and place `data-type-role` on visible HTML text-role roots. A spacing role may contain several pixel values when they form a deliberate density scale, and a text role may contain several observed variants when their relationship is intentional. SVG coordinate text uses native SVG typography without an HTML type role. Mark only continuous prose paragraphs with `data-indent-role="body-paragraph"`; every unmarked role and container uses `text-indent:0`. Each media record still requires authored authority and reader-job metadata; body placements use the same `data-media-id` and a machine-readable `data-media-crop`. A real caption follows the image with `data-caption-for`. During `plan`, the parser writes the implemented module order, density, dimensions, fixed widths, spacing scales, descriptive geometry observations, typography variants, prose indent, palette membership, media order/crops/captions, and effect kind into the contract. The release command generates `checks.fragment_sha256` so later unverified edits invalidate the relationship.

Typography and color require actual values, not adjectives such as "large", "airy", "warm", or "high contrast". Layout requires explicit relationships, not a component name. Effects require a decision even when the answer is `none`; the contract never creates a quota for decoration.

This contract belongs to the article. Do not copy a learned source's complete order into it. If the selected implementation changes, rerun `plan` so the extracted contract changes with it. Keep it `PLANNED` until the release command rechecks the final fragment and restores `READY`; do not change status merely to pass synchronization.

## Anti-template gates

Safety, factual-integrity, WeChat-compatibility, width, body-readability, and publishing-state errors block release. The following design checks are review guidance; a deliberate exception may be recorded without preventing delivery:

- The contract contains no unresolved factual or delivery placeholder, its status is `READY`, and each conditional `N/A` includes a content-based reason.
- The opener is justified by the article's literal topic, not by the nearest sample.
- The module order follows the argument and evidence, not an asset's placeholder order.
- The title, opening, headings, comparisons, and closing expose the real reasoning path without relying on components.
- Typography has a content-specific hierarchy; changing only colors and radii is not a new design.
- At least one motif, media behavior, or section transition comes from the article's subject.
- One module is visually dominant and the density rises and falls deliberately.
- Repeated containers hold genuinely comparable records with the same schema.
- The closing performs a different reader job from the opener.
- Removing gradients, shadows, and decorative marks preserves reading order and action.
- Without an explicit close-reference request, the result differs meaningfully from recognizable references or prior articles instead of merely replacing their copy.
- No finite theme catalog, source theme name, or theme selector is used to generate the design contract.
- The final fragment preserves the recorded type relationships, palette roles, spacing scales, media behavior, effects decision, and fallback. The exact fragment digest binds authored decorative detail; the contract describes its system instead of enumerating every CSS declaration.

If no close-reference request exists and the result still looks like one reference page or prior article with new copy, revise the contract before writing or delivering HTML.

## Explicit visual reference

When the user explicitly requests close visual correspondence, reproduce the reference as closely as the final content, evidence, 320px limit, inline-style boundary, and editor compatibility allow. Preserve its thesis, palette behavior, type relationships, spatial rhythm, and signature moves; change only relationships that conflict with those constraints. Exact unsupported web interaction and complete DOM reproduction are not implied.

## Handoff

State the synthesized style name and its one-line thesis. Keep source comparison, internal scoring, and learning history outside the publishable article.
