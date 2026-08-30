# Adaptive Chinese Typography Boundaries

These are readability and hierarchy constraints, not a template, theme, or default composition. Choose the visual language from the article itself, but make the exact inline typography deliberate and verify it after WeChat sanitization.

## Continuous prose

- For connected Chinese prose, use `text-indent:2em` and `text-align:justify` by default. Keep the final line naturally aligned left when the retained CSS permits it.
- Do not fake indentation with full-width spaces, repeated spaces, or `&nbsp;`. Those break under font and viewport changes.
- Do not indent titles, headings, labels, list items, quotations, captions, dialogue lines, centered text, short display statements, or the first paragraph immediately following a heading when the design intentionally uses a flush opening.
- Body copy should normally remain within 15-17px, use a regular 400 weight, and a 1.75-2.0 line-height. Choose the exact values for the audience and density; smaller type requires proportionally more line-height.
- Separate prose paragraphs with a stable vertical interval, normally about 0.9-1.3 body line-heights. Avoid both dense unbroken walls and a card-like box around every paragraph.
- Use readable side padding at narrow mobile widths. At a roughly 375px article viewport, 18-28px is usually sufficient; media can use a different edge treatment when the composition requires it.

## Hierarchy and emphasis

- Make hierarchy visible through size, weight, line-height, spacing, color, and position together. Do not rely on color alone.
- Article display titles may be expressive, but must remain legible and fit the mobile content width. Section headings should be clearly larger or heavier than body copy; captions and metadata may be smaller but should normally remain at least 11-13px.
- Keep heading line-height tighter than prose, usually 1.2-1.5. Use 600-700 for strong headings when the chosen system font renders it cleanly. Reserve 500-700 body emphasis for short phrases; do not set long prose in bold.
- Limit simultaneous font sizes and weights to the few roles the article actually needs. Preserve meaningful contrast between title, section heading, body, quotation, label, and caption without turning every paragraph into a new style.
- Keep `letter-spacing:0` for normal Chinese prose and headings unless a short label or deliberate display treatment demonstrably benefits from tracking.

## Alignment and rhythm

- Justification is for multi-line continuous prose, not every text element. Use left alignment for headings, lists, metadata, captions, and most quotations unless the composition gives another alignment a clear purpose.
- Do not justify very short lines, forced line-break poetry, or mixed Chinese/URL/code strings that would produce disruptive gaps.
- Use explicit paragraph margins, line-height, font-size, font-weight, text alignment, and indentation inline. Do not depend on browser defaults or a `<style>` block.
- Prevent manual `<br>` tags from controlling ordinary prose wrapping. Reserve them for intentional display lines, quotations, poetry, addresses, or other semantic line breaks.

## Verification

- Inspect the local comparison HTML at representative narrow mobile widths for clipping, awkward word gaps, uneven hierarchy, and excessive density.
- Fetch the created or updated WeChat draft and confirm that `text-indent`, justification, sizes, weights, line-heights, and paragraph intervals survive. If WeChat removes a property, restore the intended reading rhythm with retained inline CSS rather than whitespace characters.
- The actual mobile draft remains authoritative. Readability must survive with animations paused and decorative media removed.
