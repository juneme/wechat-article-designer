# Hard-Edge Dopamine Recruitment Pattern

Use this pattern when a WeChat recruitment article needs to feel direct, youthful, energetic, and editorial rather than soft, corporate, ceremonial, or App-like. Start from `assets/dopamine-editorial-recruitment-article.html` and replace every `{{PLACEHOLDER}}` with verified project copy.

## Selection boundary

Use this register for a clear hiring call, a small number of roles, a younger or broad adult audience, and factual application details that benefit from strong hierarchy. Do not make it the new default for every recruitment post. Rotate visual registers between campaigns, and avoid it for legal notices, formal institutional announcements, or topics that require a restrained public-service tone.

## Visual contract

Use one saturated cool primary, two warm accents, one warm-white reading surface, and one near-black ink:

| Token | Example | Role |
|---|---|---|
| Primary | `#3155F5` | Hero, chapter rule, high-priority fact band |
| Accent A | `#FFD84D` | Date strip, role header, graduate fact band |
| Accent B | `#FF6B5E` | Top rule, salary, image frame, secondary emphasis |
| Surface | `#FFFDF8` / `#FFFFFF` | Article canvas and reading cards |
| Ink | `#151836` | Borders, headings, primary body copy |

Keep radius tight: `4-8px` for hero, job cards, fact bands, and footer groups. Use hard 2px ink borders and generous vertical spacing. The Steady variant uses flat fills; the Creative variant may add controlled gradients and shadows with solid fallbacks. Flex and inline-block are compatible but should serve a specific compact row or marker rather than soften the hard-edge register. Keep positioning, Grid, and tables out of the final fragment.

## Article sequence

1. High-saturation hero with a short eyebrow, literal role headline, two-line value statement, and date/position strip.
2. One full-width recruitment scene placeholder in a colored outer frame.
3. Numbered open-position chapter.
4. One single-column job card per role: role, salary, priority facts, requirements, and preference note.
5. Benefits chapter with three simple stacked rows.
6. One short culture or invitation statement.
7. Dark application band with a narrow centered QR placeholder.
8. Separate contact, phone, and interview-address rows.
9. Salary/benefit disclaimer and publication date.

## Image-role split

Treat cover art and article art as different compositions:

- A 2.35:1 cover may reserve negative space for a deterministic title overlay.
- A body image has no title overlay and must look balanced edge to edge. Fill intentional cover whitespace with real scene content when adapting it for the article.
- Generated body art supports the theme; it does not prove employment conditions, official affiliation, or workplace reality.

## Protected-anchor image frame

Keep the persistent inner image container unpadded and give it one invisible editing anchor:

```html
<section style="box-sizing:border-box;margin:20px 8px 0;padding:8px;background:#FF6B5E;border:2px solid #151836;border-radius:8px;overflow:hidden;">
  <section style="box-sizing:border-box;min-height:96px;margin:0;padding:0;background:#FFFDF8;border:2px solid #151836;border-radius:4px;text-align:center;overflow:hidden;font-size:0;line-height:0;">
    <span style="font-size:0;line-height:0;">&nbsp;</span>
  </section>
</section>
```

Tell the publisher to click the blank inner area and insert the image directly without selecting or deleting anything first. The invisible `&nbsp;` keeps the editable wrapper alive while the image touches the inner border. Put filenames and placement instructions in the delivery guide or HTML comments. Do not put decorative badges such as `TEAM & STORE` inside the photo frame unless the brief explicitly asks for one.

## High-priority recruitment facts

Put hiring scope, location coverage, graduate cohorts, urgent deadlines, or other decision-critical facts immediately below salary as full-width contrast bands. Do not bury them in the small preference note.

```html
<p style="box-sizing:border-box;margin:16px 0 0;padding:12px 13px;background:#3155F5;border:2px solid #151836;border-radius:4px;font-size:12px;line-height:1.5;font-weight:900;color:#FFD84D;">{{FACT_LABEL}}<br><span style="font-size:18px;line-height:1.7;color:#FFFFFF;font-weight:900;">{{FACT_VALUE}}</span></p>
```

Keep legal qualifiers in the same band when they materially change the claim, for example `同等条件下优先`. Keep other preference groups in the smaller note below requirements to avoid duplication.

## Application and title rules

- Keep the QR placeholder narrow and centered (`width:180px;max-width:100%`).
- Put contact name, phone, and interview address in separate stacked rows so each field remains scannable.
- Use a factual public title formula: `【{{BRAND_SHORT_NAME}}】招聘 | {{SCOPE_OR_ROLE}}, {{AUDIENCE_HOOK}}`.
- Avoid `100%录取`, guaranteed income, or other outcome promises. Salary and benefits should carry a source-bound disclaimer when final conditions may change.

## Surgical revision rule

When feedback identifies one extra badge, spacing defect, or single misplaced element, change only that element and preserve the approved frame, color roles, copy, and surrounding structure. Re-render the affected mobile viewport before making broader visual changes.

## Validation

Run the standard `SKILL.md` article audit, then check 375px and 390px previews. Confirm that:

- priority bands fit without clipping;
- salary stays on one line;
- inserted body art touches the inner frame after direct paste and the protected anchor remains;
- the QR placeholder stays narrow;
- contact and address copy wrap without horizontal overflow;
- the final WeChat fragment has zero local image paths and balanced `section`, `p`, and `span` tags.
