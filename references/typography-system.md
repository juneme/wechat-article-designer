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
| Code | 12-14px | 1.6-1.8 | Exact command, code, log, or technical identifier |
| Data numeral | 28-52px | 1.0-1.2 | One verified number with an adjacent unit and explanation |

These are hard delivery ranges for the corresponding machine roles. A value outside its role range blocks delivery; choose another supported role when the copy has a different job. Preserve a clear ratio between adjacent roles and test the actual longest text.

Record the actual value used for each present role in `design-contract.json`. Do not leave the plan as a range. Every role object records its font stack, font size, line height, weight, alignment, zero letter spacing, and one machine-parseable wrapping declaration. Put that role name in `data-type-role` on the HTML role root. The generated `design-contract.md` is for reading only. Omit a role only when the final copy does not contain it.

## Role relationships

- Use the system sans stack for dependable Chinese rendering. Express serif, condensed, or monospace influence through role, weight, scale, rules, and spacing when the real font cannot ship.
- Use at most three visible type voices: primary reading, display contrast, and optional data/label voice.
- Give only one phrase per viewport display-level weight. Section titles support it; they do not compete with it.
- Use weight and spacing before adding a colored container. A section does not need a card to become a section.
- Reserve monospace-like treatment for codes, dates, counts, coordinates, or technical labels. Do not set narrative Chinese body copy as pseudo-terminal text.

## Chinese composition

- Keep letter spacing at `0` for every machine role, including short Latin labels.
- Do not use negative tracking. Web samples that depend on tight tracking must be translated through size, weight, and line breaks.
- Do not justify body copy by default; uneven mobile spacing is harder to read than a natural rag.
- Avoid manually inserting spaces between Chinese characters.
- Body paragraphs default to `text-indent:2em`. Apply `text-indent:0` to every non-body role, including titles, leads, lists, quotes, captions, labels, and data rows.
- A service, notice, promotional, interview, list-heavy, or short-paragraph article may use body `text-indent:0` only when `design-contract.json` records a `body-first-line-indent` exception with the article-specific reason.
- Never simulate first-line indentation with full-width spaces, nonbreaking spaces, or repeated ordinary spaces. Keep the paragraph gap consistent with the recorded indentation convention.
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
- Treat those values as a semantic scale, not a metronome. Distance should grow from same-thought grouping to continuation, turn, chapter, and closing pause.
- Do not use a border, background, label, or card when spacing and type hierarchy already express the relationship.

## Emphasis budget

Choose one primary emphasis and at most two supporting signals:

- primary: display scale, dark/light inversion, or dominant image;
- supporting: accent rule, number, label, or one secondary field;
- correction: a rare warning or editorial mark.

Bold, color, border, background, shadow, and oversized type must not all emphasize the same sentence.

Review emphasis at viewport level: about two strong moments in one mobile screen is usually enough. This is a warning threshold rather than a required count; evidence-heavy passages may differ, but consecutive strong treatments still need a clear hierarchy.

## Typography review

Before delivery:

1. Read the article without color. The heading order and argument must remain clear.
2. Check the longest title, section heading, label, contact string, and URL at 320px.
3. Run `audit_wechat_typography.py` with the READY JSON contract; any role-range or implementation mismatch blocks delivery.
4. Confirm the implemented first-line indent and paragraph gap match the recorded policy and contain no manual-space indentation.
5. Confirm labels are meaningful and Chinese tracking is zero.
6. Confirm no body paragraph is centered, boxed, or tinted solely for decoration.
7. Confirm repeated items use the same type schema and unlike roles do not.
8. Confirm the closing is quieter than the opener unless the final action is the article's purpose.
