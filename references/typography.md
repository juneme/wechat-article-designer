# Adaptive Chinese Typography Boundaries

These are readability boundaries, not a typography preset. Choose type, spacing, and alignment from the article; use the values below only as conventional fallbacks when the content offers no stronger direction, then verify the result after WeChat sanitization.

## Continuous prose

- For conventional connected Chinese prose, a first-line indent around 1.5-2em is a useful fallback range when indentation improves reading. Choose left, justified, or another alignment according to line length, density, rhythm, and natural Chinese reading habits; neither indentation nor justification is universal.
- Do not fake indentation with full-width spaces, repeated spaces, or `&nbsp;`. Those break under font and viewport changes.
- Do not indent titles, headings, labels, list items, quotations, captions, dialogue lines, centered text, short display statements, or the first paragraph immediately following a heading when the design intentionally uses a flush opening.
- For ordinary adult-audience body copy, 15-17px type, 400-500 weight, and 1.7-2.0 line-height are useful fallback ranges only. Adapt within or beyond them when the audience, voice, density, and composition support it.
- Give paragraphs and mobile side edges enough space for comfortable reading. Their exact rhythm and width belong to the composition; avoid dense unbroken walls and unnecessary boxes around every paragraph.

## Hierarchy and emphasis

- Make hierarchy visible through size, weight, line-height, spacing, color, and position together. Do not rely on color alone.
- Article titles may be expressive but must remain legible and fit the mobile content width. Headings should separate clearly from body copy; captions and metadata may be smaller without becoming hard to read.
- Headings often benefit from tighter line-height or stronger weight than prose, while long body text should normally remain regular. Use bold emphasis selectively rather than turning long passages into heavy text.
- Limit simultaneous font sizes and weights to the few roles the article actually needs. Preserve meaningful contrast between title, section heading, body, quotation, label, and caption without turning every paragraph into a new style.
- Keep tracking close to neutral for continuous Chinese prose. Adjust it for headings, short labels, or display text when that improves legibility and the intended rhythm.

## Alignment and rhythm

- Choose alignment from the natural reading flow, line length, content type, and composition. Multi-line prose may be left-aligned or justified; headings, lists, metadata, captions, and quotations may use any alignment that remains easy to follow.
- Do not justify very short lines, forced line-break poetry, or mixed Chinese/URL/code strings that would produce disruptive gaps.
- Use explicit paragraph margins, line-height, font-size, font-weight, text alignment, and indentation inline. Do not depend on browser defaults or a `<style>` block.
- Prevent manual `<br>` tags from controlling ordinary prose wrapping. Reserve them for intentional display lines, quotations, poetry, addresses, or other semantic line breaks.

## Verification

- Inspect the local comparison HTML at representative narrow mobile widths for clipping, awkward word gaps, uneven hierarchy, and excessive density.
- Fetch the created or updated WeChat draft and confirm that indentation, alignment, sizes, weights, line-heights, and paragraph intervals survive. If WeChat removes a property, restore the intended reading rhythm with retained inline CSS rather than whitespace characters.
- The actual mobile draft remains authoritative. Readability must survive with animations paused and decorative media removed.
