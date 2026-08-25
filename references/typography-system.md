# Typography System

Typography is a compositional language, not a fixed role table. Establish hierarchy through relationships among scale, weight, family, alignment, width, leading, color, and surrounding space. One article may use several heading treatments when their contrast expresses the narrative.

## Readability floor

Ordinary mobile body prose normally begins around 15-16px with 1.75-2.0 leading. The release audit blocks only explicitly styled continuous body prose below 14px or below 1.5 leading. Compact labels, captions, data units, seals, and SVG coordinate text may be smaller when they remain legible and are not carrying paragraph-length information.

These are starting points, not a required scale:

| Use | Common starting range | Notes |
|---|---:|---|
| Major display | 28-44px | Adjust to title length and desired line count |
| Section turn | 20-28px | May change treatment between narrative acts |
| Item heading | 16-20px | Keep the relation to adjacent explanation clear |
| Body prose | 15-16px | Protect sustained reading comfort |
| Caption or label | 11-14px | Keep factual qualifiers readable |
| Data display | 26-56px | Keep unit and meaning adjacent |

Use values outside these ranges when the composition needs them. Do not normalize expressive variation merely because a number differs from an example.

## Body-only indentation

The default prose convention is two Chinese characters:

```html
<p data-indent-role="body-paragraph" style="margin:0 0 14px;color:#252525;font-size:16px;line-height:1.9;text-indent:2em;">
  [continuous prose]
</p>
```

Only ordinary continuous prose uses that marker and indent. The following are not body-indent paragraphs even when implemented with `<p>`:

- title, deck, lead, eyebrow, chapter label, or section heading;
- list item, comparison row, metric, date, or requirement;
- quotation, poem, interview question, dialogue, or testimony;
- image caption, source, footnote, disclaimer, or code;
- card title, button-like action, contact line, closing blessing, or colophon;
- any container.

Those elements use no first-line indent. Never set indentation on an ancestor and rely on descendants to cancel it. Never simulate indentation with full-width spaces, `&nbsp;`, or repeated ordinary spaces.

## Titles on mobile

Prefer a one-line major title or section heading when the full wording and composition permit it. Estimate the real Chinese title at the intended type size, then inspect it at 320px. If an awkward wrap appears, first adjust scale, inset, emphasis distribution, or surrounding composition.

Do not force `white-space:nowrap`, shrink the title into illegibility, or replace distinctive language with generic wording. A deliberate two-line title is valid when the break follows meaning, the two lines balance, and the final line is not an orphaned one- or two-character fragment.

## Rhythm

Build spacing from semantic distance:

- phrase-level details sit close;
- one thought to its explanation uses a modest gap;
- a turn in argument opens more air;
- a chapter, visual scene, or emotional shift may use a large pause;
- the closing should feel intentionally separate from the last evidence block.

Do not force all paragraph gaps or all section gaps to one number. Repeated values create cadence; changes create emphasis and transition.

## Alignment and tracking

Left alignment is the default for sustained reading, but centered, right-aligned, vertical, or mixed alignment can be meaningful in short display passages. Keep long prose easy to track.

Chinese body copy normally uses `letter-spacing:0`. Display tracking may open or compress when the result remains legible. Do not insert spaces between Chinese characters to fake tracking because line wrapping becomes unpredictable.

## Emphasis

Use contrast deliberately. Scale, weight, color, background, border, shadow, alignment, and isolation can all emphasize; they do not all need to fire at once. Let one device lead and the others support unless a deliberate visual climax warrants excess.

Review the full viewport rather than counting bold elements. A dense evidence section and a lyrical transition legitimately need different typographic energy.

## Review

1. Read the article without color and confirm that structure remains clear.
2. Inspect real titles, the longest label, URLs, dates, and mixed Chinese/Latin lines at 320px.
3. Confirm only marked body prose uses `2em` indentation.
4. Confirm paragraph copy remains readable without zoom.
5. Keep SVG text concise enough to survive font substitution and fixed coordinates.
6. Run `audit_wechat_typography.py`; recommendations appear as warnings, while only the readability and indentation boundary blocks.
