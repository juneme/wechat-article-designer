# Modular Article Composition

Use this reference for new full articles and substantial structural redesigns. It turns payload, type, and the living grammar into an editable source-module system without treating a complete example page as a locked template.

## Separate the five layers

1. **Payload**: verified facts, narrative copy, images, captions, and the requested reader action.
2. **Module role**: the semantic job a block performs in the reading path.
3. **Type role**: display, section, item, body, label, caption, or data behavior from `typography-system.md`.
4. **Design grammar**: palette behavior, edge language, image silhouette, density, and rhythm.
5. **Implementation pattern**: the copy-safe inline HTML used to render that module in WeChat.

Do not choose an implementation pattern before the payload and module role are clear. A rounded card, numbered row, or dark band is a rendering choice, not a content reason.

## Build the private manifest

Write one row for each required module before composing HTML:

| Field | Record |
|---|---|
| Role | One semantic role from the catalog below |
| Reader job | What the reader should understand, trust, see, compare, or do |
| Source | The exact facts, paragraphs, or asset assigned to the block |
| Weight | Dominant, supporting, or quiet |
| Width | Full band, standard inset, or narrow inset |
| Type role | The text hierarchy required by this payload |
| Pattern | A core inline primitive or grammar capability, selected after the preceding fields |
| Fallback | The readable Steady-mode form if an expressive effect is stripped |

The manifest is private workflow context. Do not publish role codes, source notes, or fallback instructions in the article.

## Role catalog

| Code | Role | Use when |
|---|---|---|
| `O` | Opener | Establish the literal topic, ownership, and emotional register. Use one opener. |
| `N` | Orientation | Give a reading map, date line, scope, or short index when it materially improves scanning. |
| `E` | Evidence | Present verified facts, requirements, comparisons, proof images, or source-linked claims. |
| `S` | Story | Explain context, sequence, interpretation, or human experience in open prose or chapters. |
| `M` | Media | Carry a photograph, illustration, diagram, portrait sequence, or captioned evidence asset. |
| `A` | Action | State the one next action, method, deadline, contact path, or risk-aware CTA. |
| `C` | Closing | Resolve the article with ownership, a final line, credits, or a deliberate visual stop. Use one closing. |

Not every article needs every role. A reflective essay may be `O-S-M-S-C`; a service notice may be `O-N-E-E-A-C`; an event recap may be `O-S-M-S-M-C`.

## Assembly rules

- Give one module visual dominance. Other modules support it through contrast, spacing, or quieter surfaces.
- Let density change across the page. Follow a dense fact block with open prose, an image pause, or a clear section break.
- Repeat one container only for genuinely comparable records. When content roles change, change the block treatment instead of extending a card stack.
- Keep cards as individual repeated items, not page-section wrappers. Do not put a decorative card inside another card.
- Use a stable outer baseline and one intentional inset baseline. Add a third width only when it creates a clear emphasis or caption relationship.
- Keep one primary reading order. Static WeChat content must not require hover, tab state, drag state, or animation to reveal information.
- Use visible labels only when they help the reader. Do not expose internal component names or template instructions.

## Translate interactive interface ideas safely

Web component libraries are useful for hierarchy and modularity, but their interaction patterns are not automatically publishable in WeChat.

| Web pattern | WeChat translation |
|---|---|
| Tabs or segmented filters | A short static reading map followed by labeled sections; remove inactive-state behavior. |
| Hover preview | Place the preview image and explanation directly in the reading flow. |
| Carousel | Prefer a vertical media sequence; use the exact-block manual swipe pattern only when real-editor testing is available. |
| Masonry or dense grid | Use a single prepared bitmap or a single-column sequence with stable captions. |
| Animated hero | Capture its hierarchy in a static opener: one dominant phrase, one supporting line, and one controlled visual field. |
| Glass or translucent surface | Use a solid readable field with a border; decoration must not depend on backdrop effects. |
| Interactive code/demo panel | Convert it to a numbered process, annotated screenshot, or compact fact flow. |

## Module selection test

Before keeping a block, answer all four:

1. What reader job does it perform?
2. Which source content belongs inside it?
3. Why does its visual weight fit that job?
4. What remains when gradients, shadows, or experimental declarations are removed?

Delete or merge a block that exists only to add decoration. Split a block when it mixes evidence, narrative, and action so densely that none can be scanned.

## Originality and quality gates

- Compare the new manifest with the nearest learned source. Change at least two meaningful aspects of module sequence, role treatment, or density curve when claiming an original composition.
- Confirm that every visible module maps to verified payload or a necessary reader action.
- Confirm that repeated blocks share one semantic schema; visual similarity alone is not a reason to group unlike content.
- Confirm that removing decoration preserves hierarchy, labels, reading order, and the action path.
- Run the normal audience, width, tag-balance, mobile-width, and real-editor checks after the manifest is rendered.
