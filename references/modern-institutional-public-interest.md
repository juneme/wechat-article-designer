# Modern Institutional / Public-Interest WeChat Direction

Use this reference for government-guided public services, corporate social responsibility, public health, environmental protection, regulated-industry education, and any article whose requested tone is “现代、庄重、可信、不浮夸”.

This is a visual register, not a fixed brand template. Keep the project palette and claim rules authoritative.

## Diagnose the feedback before redesigning

| Feedback | Actual problem | First response |
|---|---|---|
| “页面很乱” | Too much copy, repeated claims, nested cards, too many visual levels | Cut repetition, merge sections, reduce card count |
| “文案太多” | Reader cannot find the main action | Keep one core sentence per section and move policy detail to one note |
| “页面过于简单” | Copy is clear but lacks hierarchy and rhythm | Add a strong opener, section numbering, grid alignment, image rhythm, and one closing anchor |
| “太浮夸” | Too many colors, ornaments, rounded cards, slogans, or effects | Reduce colors and decoration; use whitespace and rules |
| “很有年代感” | Serif-heavy type, ivory/gold palette, seal motifs, formal numerals, newspaper nostalgia | Switch to system sans, cool neutrals, Arabic numbering, harder dividers |

Do not solve all five comments by adding more decoration. “乱” and “简单” are separate problems: copy reduction solves the first; hierarchy solves the second.

## Visual grammar

Recommended structure:

1. Deep, solid-color opening band with one literal title and one verified institutional line.
2. White or cool-neutral middle with strict alignment and short sections.
3. Arabic section numbers (`01 / 02 / 03`) and straight dividers.
4. Compact vertical fact flow when each item has a short title and one short supporting line.
5. One or two wide images that show the real service or public action.
6. Solid-color closing band that repeats the public action, not every earlier claim.

Recommended visual characteristics:

- System sans-serif typography; use weight and spacing for authority.
- Colors sampled from the supplied main visual + a light reading surface + near-black text.
- Square or 0-4px-radius containers unless the brand system is explicitly rounded.
- Thin borders, hard dividers, and regular grid alignment.
- Large color fields only at the opening and closing; keep the middle quiet.
- Body copy around 15-16px and line-height around 1.9.

## Palette from the main visual

When a main visual, campaign poster, or event key art exists, use it as the palette authority.

- Sample the actual large fields, headline/rule color, readable dark, and small accent before assigning tokens.
- Keep 60-75% of the mobile article light, reserve 15-25% for sampled primary/accent surfaces, and keep very dark color near 5-10% unless the source visual is intentionally dark.
- A deep sampled brown, green, blue, or red does not automatically belong on every heading or large block. Use the deepest tone for a short rule, number, label, or closing anchor when a full field feels heavy.
- Build light fills from pale variants of the sampled palette instead of introducing an unrelated default theme.
- Judge palette fidelity and reading contrast separately: body copy still needs a high-contrast neutral.

## Mobile spacing and photo density

Use whitespace to separate chapters instead of stacking more containers:

- `44-60px` before a new chapter header;
- `20-28px` from a short copy block to its related photo;
- `28-36px` between consecutive photo groups;
- one core sentence and normally no more than two short paragraphs before the next visual break;
- one leading image per chapter, with a node divider or short header after every 2-3 consecutive images.

When every participant must appear, assemble consistently cropped portraits into one bitmap rather than an HTML grid. A square matrix of 4:5 portrait cells produces a 4:5 wall: use `3 x 3` for up to 9 people or `4 x 4` for up to 16, then split larger groups into two labeled walls.

## Avoid accidental nostalgia

These signals can be valid independently, but combining several often creates an unintended period-publication look:

- large Songti / serif headlines;
- ivory, cream, or sepia page backgrounds;
- muted gold rules on every section;
- seal or stamp motifs;
- formal Chinese numerals such as “壹 / 贰 / 叁”;
- imitation newspaper or commemorative-book layouts.

Use them only when the brief explicitly calls for historical, ceremonial, archival, or traditional-cultural expression.

## Copy architecture for public-interest articles

A reliable public-facing sequence is:

1. **Authority / responsibility**: who is doing the work and under what verified basis.
2. **Why it matters**: no more than three public benefits.
3. **Organization action**: where the service appears, how it is managed, how it continues.
4. **Public action**: three short steps that a broad audience can perform.
5. **Long-term close**: government guidance, organizational execution, and public participation.

Address the audience broadly (“广大群众”, “社会公众”) while keeping the accepted item or service scope technically precise.

## Government and institutional claims

Before emphasizing “指定 / 授权 / 唯一 / 官方”: 

- verify the authority name, geography, duration, named organization, and business scope;
- attach “唯一” to the exact service, not to the company as a whole;
- do not translate a single-service designation into a general government endorsement;
- use a real document photo when the article needs evidence;
- never use an AI-generated certificate, seal, emblem, or government logo as proof.

## Evidence images vs generated illustrations

Keep two roles separate:

- **Evidence image**: real authorization document, real storefront sign, real service box, real event photo.
- **Supporting illustration**: explains a scene or process when a real photo is unavailable.

For generated supporting illustrations:

- show the service environment, staff action, public participation, and relevant objects;
- prohibit readable text, brand names, official emblems, seals, flags, certificates, and watermarks;
- avoid retro propaganda aesthetics unless explicitly requested;
- keep a consistent landscape ratio and shared style across the article;
- do not use generated art to substantiate a factual government relationship.

## Mobile verification

Default to `section` + `p` + `span` flow. Do not use `table`, `tbody`, `tr`, or `td`: WeChat may add a horizontal scroll wrapper and reset cell widths after paste, which deforms both equal and unequal column layouts.

For any compact fact group or horizontal-looking process:

- render items as a vertical flow unless the exact final block has passed a real WeChat editor test;
- keep headings to 2-4 Chinese characters and supporting copy to one short sentence;
- validate around both 375px and 390px width;
- if a block gains horizontal scrolling, equalized columns, unexpected wrapping, or clipping after paste, replace the entire structure with flow blocks instead of adding more width rules.

Check `scrollWidth <= clientWidth` for all visible layout elements and inspect a full-page screenshot before delivery.
