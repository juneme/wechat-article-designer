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

## Build writing, structure, and type first

1. Read `editorial-writing-grammar.md` and make the unstyled draft establish a defensible promise, reasoning path, and evidence boundary.
2. Read `modular-composition-system.md` and map payload to semantic module roles.
3. Read `typography-system.md` and define display, section, item, body, label, caption, and data roles supported by the copy.
4. Set the density curve: where the article declares, proves, pauses, explains, asks, and closes.

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
10. **Delivery mode** - Steady or Creative with a readable static fallback.

The living grammar contains only normalized design decisions, not source records. Normal generation must not reconstruct a source catalog or pick a source winner.

## Complete the private design contract

Use `design-contract.json` as the only editable contract source. Before HTML, replace every placeholder with an article-specific decision. A conditional dimension may say `none` or `N/A`, but it must explain why that is correct for the content. Complete the planning checks, set `status` to `PLANNED`, and run the workspace `plan` command before implementation. Keep it `PLANNED` while composing; the enforced release command generates `checks.fragment_sha256`, verifies the structural markers, and promotes the exact audited fragment to `READY`. Inspect but never edit the generated `design-contract.md`.

Record all of the following:

| Dimension | Minimum concrete record |
|---|---|
| Editorial and evidence | Reader situation, central friction, judgment, reader gain, source facts, evidence boundary, and desired action |
| Composition | Module manifest, one dominant module, reading order, widths, outer baseline, content inset, density curve, and semantic spacing scale |
| Typography | Every used `data-type-role` with font stack, size, line height, weight, alignment, zero letter spacing, and machine-parseable wrapping; also record role relationships, body paragraph gap, and the default `2em` first-line indent or its exception |
| Color | Exact hex values for field, ink, primary signal, secondary signal, correction, and image-derived support; state where each is allowed and how contrast survives without effects |
| Media | Each asset's reader job, factual authority, order, crop or aspect behavior, caption/source need, and placeholder or hosted state |
| Geometry and motif | Primary edge language, radius policy, dividers, surface behavior, content-native motif, recurrence limit, and exceptions |
| Effects and motion | Select `none`, static expressive CSS, or SVG/SMIL; state the semantic job, static first state, fallback, compatibility risk, and exact-fragment test obligation |
| Delivery | Steady or Creative, backend readiness result, draft or local-preview target, must-keep decisions, avoid decisions, fallback, and stop condition |

Machine relationships are explicit. Make `editorial.module_sequence` exactly match `data-module-id` order and `layout.density_curve` exactly match those modules' `data-density` values. Implement `outer_baseline_px` and `content_inset_px` as horizontal padding on the unique matching `data-layout-role`; list every pixel `width`, `min-width`, and `max-width` in `fixed_widths_px`. List every used spacing token in `layout.used_spacing_roles` and place its matching `data-spacing-role` on an element whose inline value implements the recorded number. List every non-`N/A` geometry decision in `geometry.used_roles`, define its exact inline declarations under `geometry.implementations`, and implement them on the matching `data-geometry-role`. Each media record uses a unique `name`, `order`, `placement`, `required`, state, machine-readable crop, and workspace-relative `source_path`; body placements use the same `data-media-id` and `data-media-crop` in reading order. A real caption follows the image with `data-caption-for` and exact contract text. The release command generates `checks.fragment_sha256` so unverified edits invalidate the complete relationship.

Typography and color require actual values, not adjectives such as "large", "airy", "warm", or "high contrast". Layout requires explicit relationships, not a component name. Effects require a decision even when the answer is `none`; the contract never creates a quota for decoration.

This contract belongs to the article. Do not copy a learned source's complete order into it. If implementation changes one of these decisions, return the contract to `PLANNED`, revise it, and rerun `plan`. Keep it `PLANNED` until the release command rechecks the final fragment and restores `READY`; do not change status merely to pass synchronization.

## Anti-template gates

All gates must pass:

- The contract contains no unresolved placeholder, its status is `READY`, and each conditional `N/A` includes a content-based reason.
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
- The final fragment implements the recorded type values, palette roles, spacing relationships, media behavior, effects decision, and fallback without unrecorded decoration.

If no close-reference request exists and the result still looks like one reference page or prior article with new copy, revise the contract before writing or delivering HTML.

## Explicit visual reference

When the user explicitly requests close visual correspondence, reproduce the reference as closely as the final content, evidence, 320px limit, inline-style boundary, and editor compatibility allow. Preserve its thesis, palette behavior, type relationships, spatial rhythm, and signature moves; change only relationships that conflict with those constraints. Exact unsupported web interaction and complete DOM reproduction are not implied.

## Handoff

State the synthesized style name and its one-line thesis. Keep source comparison, internal scoring, and learning history outside the publishable article.
