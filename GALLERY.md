# Living WeChat Design Grammar

This is a growing system of design decisions, not a template gallery or a finite style list. New articles combine the complete grammar with their own content, evidence, images, and reading goals.

## Decision layers

| Layer | Decides | Source |
|---|---|---|
| Content map | Reader, purpose, evidence, action, mood, density, image roles | Final brief |
| Module manifest | Semantic blocks, order, width, weight, density curve | `references/modular-composition-system.md` |
| Type plan | Display, section, body, label, caption, data hierarchy | `references/typography-system.md` |
| Living grammar | Palette, composition, geometry, media, pacing, close | This file |
| Design contract | Article-specific thesis and must/avoid/fallback rules | `references/original-style-synthesis.md` |
| Implementation | Copy-safe inline blocks | `references/snippets.md` |

## Visual field and color

- **Rationed accent**: neutral field, readable ink, and one primary signal for evidence, services, products, or institutional content.
- **Image-sampled field**: derive field and accents from the authoritative image while keeping body text independently readable.
- **Paper and material**: warm or cool paper fields, rules, labels, and tactile image mounts for cultural, archival, craft, or reflective narratives.
- **Dark signal field**: near-black field with one luminous accent and one correction color only when launch, technical, cinematic, or night content justifies it.
- **Controlled saturation**: one dominant saturated field with quiet reading surfaces; several saturated colors must not compete at equal weight.

Assign every color a role: field, ink, primary signal, secondary signal, correction, or image-derived support. Decoration alone is not a role.

## Typography

- **Functional sans**: dependable hierarchy for services, notices, recruitment, institutional, and data-heavy work.
- **Editorial contrast**: create serif/sans-like contrast with weight, scale, rules, and spacing when external fonts cannot ship.
- **Display plus data**: one expressive title role supported by restrained body copy and a distinct numeric or label role.
- **Condensed energy**: translate narrow web display type into measure, weight, controlled line breaks, and hard rules.
- **Type-led composition**: let one title, quotation, or verified number become the primary image, then quiet subsequent sections.

Apply these relationships through `references/typography-system.md`. Source font names are relationship evidence, not dependencies.

## Composition and density

- **Declaration to evidence**: strong literal opener, compact orientation, dense proof, then open explanation.
- **Photo and chapter turns**: alternate media and prose so neither becomes a continuous wall.
- **Indexed editorial**: use chapter numbers, timestamps, routes, stages, or other content-native indices.
- **Evidence ledger**: aligned labels, neutral dividers, consistent fact schemas, and one dominant proof block.
- **Asymmetric emphasis**: translate unequal desktop masses into one clear mobile reading order.
- **Full-band cadence**: change fields only where the narrative actually changes.
- **Quiet essay**: sparse opener, long-form body, rare rules, and one material or image interruption.

Every article needs a density curve. Repeating equal cards from opener to close is a failed composition.

## Geometry and surfaces

- **Hard and ruled**: square edges, hairlines, double rules, registration marks, or technical labels.
- **Soft utility**: moderate radii for approachable services and compact tools; reserve pills for short labels or actions.
- **Organic silhouette**: one arch, circle, leaf cut, torn edge, or irregular mount derived from the subject.
- **Document frame**: captions, accession labels, photo mounts, issue lines, or archive sleeves.
- **Material mass**: solid bands and strong edges suggesting paper, stone, metal, glass, or clay without decorative texture overload.

Choose one primary edge language. Mix geometries only when their roles explain the contrast.

## Image behavior

- literal evidence image with a nearby caption or source;
- full-width narrative image used as a section turn;
- quiet inset portrait or object study;
- prepared contact sheet or collage bitmap for dense repeated subjects;
- product or object sequence alternating overview, detail, proof, and use;
- illustration for mood or explanation, never as factual proof.

Images must perform a reader job. Remove decorative media that interrupts the argument without adding meaning.

## Translate web interaction to static reading

| Web behavior | WeChat translation |
|---|---|
| Split or opening hero | Layered title, central image, and two quiet edge fields |
| Scroll-linked sequence | Ordered overview, detail, proof, and context blocks |
| Kinetic type | One display field followed by progressively quieter headings |
| Sticky narrative | Visible orientation followed by numbered chapters |
| Draggable deck | Vertical sequence, or tested direct-child swipe with a vertical fallback |
| Hover reveal | Show image and explanation together in reading order |
| Glass depth | Solid field, hairline border, and explicit foreground/background contrast |
| Bento dashboard | Single-column groups with clear label, data, and explanation roles |

Learn hierarchy, reveal order, depth, and sequence. Do not import scripts, hidden states, hover dependence, sticky behavior, or desktop grid geometry.

## Synthesis rules

1. Start from the content map, module manifest, and type plan.
2. Evaluate every grammar dimension against the reader, evidence, images, risk, and desired action.
3. Choose one governing thesis and only the supporting decisions it needs.
4. Resolve conflicts by comprehension, factual authority, mobile legibility, and editor compatibility.
5. Derive at least one motif, media behavior, or transition from the article's literal subject.
6. Give one module dominance and make density rise and fall.
7. Use repeated containers only for records with the same semantic schema.
8. Apply the nearest-source test: if the page still reads as one learned source with different copy, revise the opener, type plan, density curve, media rhythm, or close.

When style exploration is requested, present a few article-specific directions and compare their typography, composition, image behavior, and density. Never imply that the skill offers a fixed number of styles.

## Learning provenance

The latest normalized source study is `references/superdesign-study-2026-08-20.md`; its accountable record list is `references/superdesign-record-index-2026-08-20.md`. These files document coverage and provenance. Normal article generation uses the merged grammar above rather than selecting a source record.
