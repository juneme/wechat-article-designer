# Mobile WeChat Typography System

Use this reference for every new full article and any redesign that changes hierarchy, density, or reading rhythm. Typography carries the design before decoration.

## Derive type roles from the copy

Sketch the roles before HTML, then let `plan` extract the selected implementation's exact values:

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

These are recommendation ranges. A non-body role outside them produces a design warning and may be retained when the selected composition remains legible. Body remains a hard reading range of 15-16px with 1.85-2.0 leading. Preserve a clear relationship between adjacent roles and test the actual longest text.

Every visible role root uses `data-type-role` and explicit or inherited font stack, size, line height, weight, alignment, letter spacing, indentation, and one machine-parseable wrapping declaration. `plan` records the actual values in `design-contract.json`; it does not leave ranges or adjectives. The generated `design-contract.md` is for reading only. Omit a role only when the final copy does not contain it.

## Role relationships

- Use the system sans stack for dependable Chinese rendering. Express serif, condensed, or monospace influence through role, weight, scale, rules, and spacing when the real font cannot ship.
- Usually keep three or fewer visible type voices: primary reading, display contrast, and optional data/label voice. More is a composition judgment, not a schema failure.
- Give only one phrase per viewport display-level weight. Section titles support it; they do not compete with it.
- Use weight and spacing before adding a colored container. A section does not need a card to become a section.
- Reserve monospace-like treatment for codes, dates, counts, coordinates, or technical labels. Do not set narrative Chinese body copy as pseudo-terminal text.

## Chinese composition

- Keep body letter spacing at `0`. Non-body roles may use restrained tracking when it supports the selected composition; values outside the recommended `-0.5px` to `2.5px` range produce a warning for phone inspection.
- Avoid tight tracking on continuous Chinese copy. Short display or Latin roles may use modest negative tracking when the longest final string remains legible.
- Do not justify body copy by default; uneven mobile spacing is harder to read than a natural rag.
- Avoid manually inserting spaces between Chinese characters.
- Only ordinary continuous prose paragraphs use first-line indentation. Mark those `p` elements with both `data-type-role="body"` and `data-indent-role="body-paragraph"`, then apply the contract value, normally `text-indent:2em`.
- `data-type-role="body"` controls font size and leading only. Without `data-indent-role="body-paragraph"`, it must use `text-indent:0`. Titles, leads, lists, quotes, dialogue, captions, labels, data rows, cards, actions, closings, and every container also use `0`.
- A service, notice, promotional, interview, list-heavy, or short-paragraph article may have no indented prose paragraphs. A marked prose paragraph may use `text-indent:0`, which produces a design warning; record a `body-first-line-indent` exception when the deviation should be explicitly acknowledged.
- Never simulate first-line indentation with full-width spaces, nonbreaking spaces, or repeated ordinary spaces. Keep the paragraph gap consistent with the recorded indentation convention.
- Use deliberate `<br>` only in a short opener or closing after testing the final copy at 320px. Never preserve example line breaks after replacing the title.
- Keep centered prose to about two short lines. Longer reading copy should align left.
- Do not use an English eyebrow merely as decoration. A visible label must add category, date, ownership, or orientation.
- Keep punctuation with its sentence. Do not place isolated punctuation in decorative spans.

## Line length and inset

- Treat one line as the preferred mobile shape for `display` and `section` roles. The typography audit estimates their rendered width against a conservative 288px budget and reports `heading-wrap-risk` without blocking delivery.
- Resolve a risky heading in this order: shorten the visible phrase; move qualifiers into a deck; reduce its size while preserving hierarchy; then reclaim unnecessary heading inset. Keep the full official title in article metadata when the visible display phrase is shortened.
- Never apply `white-space:nowrap` to text that does not demonstrably fit at 320px in the real editor. Preventing wrap by causing clipping or horizontal overflow is a failed layout.
- If the meaning cannot fit on one line, use at most two intentionally balanced lines at a semantic boundary. Avoid a final line containing only one or two Chinese characters. An explicit `<br>` produces a review warning because it must be checked against the final copy.
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
2. Check the longest title and section heading at 320px; prefer one line and inspect every `heading-wrap-risk` or `heading-forced-line-break` warning. Then check labels, contacts, and URLs.
3. Run `audit_wechat_typography.py` with the READY JSON contract; body readability and post-freeze implementation mismatches block delivery, while non-body recommendation ranges remain warnings.
4. Confirm only marked continuous-prose paragraphs use the recorded first-line indent; all other content and containers use `0`, with no manual-space indentation.
5. Confirm labels are meaningful, body tracking is zero, and any display tracking remains legible.
6. Confirm no body paragraph is centered, boxed, or tinted solely for decoration.
7. Confirm repeated items use the same type schema and unlike roles do not.
8. Confirm the closing is quieter than the opener unless the final action is the article's purpose.
