# Mobile WeChat Typography System

Use this reference for every new full article and any redesign that changes hierarchy, density, or reading rhythm. Typography carries the design before decoration.

## Plan type roles from the copy

Build a private type plan before HTML:

| Role | Typical mobile range | Leading | Use |
|---|---:|---:|---|
| Display title | 30-38px | 1.20-1.35 | Literal article topic; reduce to 28-32px for long titles |
| Section heading | 22-27px | 1.35-1.55 | A real change in argument or chapter |
| Item heading | 17-20px | 1.45-1.65 | Comparable records, requirements, or subtopics |
| Deck / lead | 15-17px | 1.75-1.95 | Scope, thesis, or one short orientation paragraph |
| Body | 15-16px | 1.85-2.0 | Continuous Chinese reading |
| Caption / note | 12-13px | 1.6-1.8 | Image context, source, qualifier, or disclaimer |
| Label / index | 10-12px | 1.4-1.6 | Short navigation, chapter, or data label |
| Data numeral | 28-52px | 1.0-1.2 | One verified number with an adjacent unit and explanation |

These are defaults, not a required scale. Preserve a clear ratio between adjacent roles and test the actual longest text.

## Role relationships

- Use the system sans stack for dependable Chinese rendering. Express serif, condensed, or monospace influence through role, weight, scale, rules, and spacing when the real font cannot ship.
- Use at most three visible type voices: primary reading, display contrast, and optional data/label voice.
- Give only one phrase per viewport display-level weight. Section titles support it; they do not compete with it.
- Use weight and spacing before adding a colored container. A section does not need a card to become a section.
- Reserve monospace-like treatment for codes, dates, counts, coordinates, or technical labels. Do not set narrative Chinese body copy as pseudo-terminal text.

## Chinese composition

- Keep Chinese letter spacing at `0`. Short Latin uppercase labels may use up to `1px` when the string remains readable.
- Do not use negative tracking. Web samples that depend on tight tracking must be translated through size, weight, and line breaks.
- Do not justify body copy by default; uneven mobile spacing is harder to read than a natural rag.
- Avoid manually inserting spaces between Chinese characters.
- Use deliberate `<br>` only in a short opener or closing after testing the final copy at 320px. Never preserve example line breaks after replacing the title.
- Keep centered prose to about two short lines. Longer reading copy should align left.
- Do not use an English eyebrow merely as decoration. A visible label must add category, date, ownership, or orientation.
- Keep punctuation with its sentence. Do not place isolated punctuation in decorative spans.

## Line length and inset

- Use one stable outer baseline, usually `8px`, and one reading inset, usually `18-22px`.
- Standard body copy should not be squeezed into decorative narrow columns on mobile.
- A quote, caption, or data note may use a narrower inset when that contrast is intentional.
- Long Latin words, URLs, role names, and generated identifiers need `word-break:break-word;overflow-wrap:anywhere` on the containing line.

## Vertical rhythm

- Paragraph-to-paragraph: usually `8-14px`.
- Heading-to-body: usually `10-16px`.
- New section: usually `34-52px`, adjusted by density.
- Caption after media: usually `8-12px`.
- Dense fact rows: `14-18px` internal vertical padding with neutral dividers.
- Follow a dense list with open prose, a media pause, or a larger section break. Do not repeat equal card gaps through the whole article.

## Emphasis budget

Choose one primary emphasis and at most two supporting signals:

- primary: display scale, dark/light inversion, or dominant image;
- supporting: accent rule, number, label, or one secondary field;
- correction: a rare warning or editorial mark.

Bold, color, border, background, shadow, and oversized type must not all emphasize the same sentence.

## Typography review

Before delivery:

1. Read the article without color. The heading order and argument must remain clear.
2. Check the longest title, section heading, label, contact string, and URL at 320px.
3. Confirm body copy is normally 15-16px with at least 1.85 leading.
4. Confirm labels are meaningful and Chinese tracking is zero.
5. Confirm no body paragraph is centered, boxed, or tinted solely for decoration.
6. Confirm repeated items use the same type schema and unlike roles do not.
7. Confirm the closing is quieter than the opener unless the final action is the article's purpose.
