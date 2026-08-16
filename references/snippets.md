# WeChat HTML Snippets (Brand-Agnostic)

> Reusable HTML patterns for WeChat 公众号 articles. All patterns use placeholder colors (e.g. `#1f7b5d`) and placeholder copy. Replace with your brand's actual colors and content.
>
> For a quick visual reference, see the matching `SKILL.md` sections. For project-specific examples (e.g. a medical brand), see the project knowledge base.

## How to use this file

1. Pick the snippets you need (the index below).
2. Replace every `{{BRAND_*}}` token with the brand's color.
3. Replace every `{{...}}` content placeholder (e.g. `{{TITLE_LINE_1}}`) with the actual copy.
4. Wrap the full fragment with the copy boundary markers.
5. Run the self-audit checklist from `SKILL.md` before delivery.

All snippets default to `section` + `p` + `span`. Do not introduce `table`, `tbody`, `tr`, or `td` unless the exact final block has passed a documented test in the real WeChat editor.

Manual image slots use a protected editing anchor: one `&nbsp;` inside a zero-size span, wrapped by a blank `min-height` container. Click the blank container and paste or upload directly. Never select all or delete the anchor first; deleting the editor's only child can make WeChat normalize away the surrounding frame. Keep filename maps and replacement instructions in the delivery guide or HTML comments, not inside the final image slot.

## Index of snippets

| Snippet | When to use |
|---|---|
| Copy Boundary | Every article — wrap once at the outermost level. |
| Rounded Protected-Anchor Photo Placeholder | Warm, service-oriented, or rounded brand systems. |
| Institutional Photo Placeholder | Modern, solemn, public-interest, or regulated-industry articles. |
| Flow Photo Frame (Event Recap) | A low-decoration, full-width event photo slot with a small index strip. |
| Event Recap Chapter Header | A spacious numbered chapter break for mobile event stories. |
| Node Divider | A light visual pause between dense photo or copy groups. |
| 4:5 Portrait Collage Wall (Single Bitmap) | Show many people as one pre-composed mobile-safe image instead of HTML cells. |
| Repeated Speaker Card (Single-Column) | When a section lists many people and each person needs a photo placeholder plus a short text stack. |
| Centered QR Placeholder (Dark Footer) | When a dark closing section needs a small centered QR or square-asset placeholder. |
| Real Image in HTML Frame | When the HTML references an already-uploaded image URL. |
| Soft Closing Card (Border-Only) | Closing / signature block. |
| Title Section | First section. Has `padding:0`. |
| Sub-title with 4-action + metaphor | Sub-title that combines core actions with a warm metaphor. |
| Card with 3 Bullets | A service card with 3 bullets max. |
| Solid-Color Anchor Block | Visual anchor / slogan after a list of cards. |
| Key Positioning Strip | Highlight a single critical sentence. |
| Section Label | Small uppercase label before a section heading. |
| Tip / Disclaimer Block | Legal disclaimer or important reminder. |
| Photo Caption Color by reader age band | Caption with reader-appropriate contrast. |
| Top-of-Article Minimal Header | Skip top brand composite, use title only. |
| Modern Institutional Hero | Strong official/public-interest opener without retro motifs. |
| Modern Numbered Section Header | Arabic-number hierarchy with a hard divider. |
| Compact Three-Fact Flow (No Table) | Three short facts or actions in a reliable vertical flow. |
| White-Interior Accent-Edge Grouped Card | Clean poster-derived rows with white interiors, neutral dividers, and up to three sampled edge colors. |
| Risk-control Word Substitutions (Generic) | Industry-agnostic substitution patterns; build a per-industry table per project. |

## Placeholder tokens

| Token | Default | Purpose |
|---|---|---|
| `{{BRAND_PRIMARY}}` | `#1f7b5d` | Brand primary color |
| `{{BRAND_ACCENT}}` | `#ee7d2a` | Brand accent color |
| `{{BRAND_TERTIARY}}` | `#5a9fb8` | Brand tertiary color (a third hue, used sparingly for small chips / dots / dividers) |
| `{{BRAND_BG}}` | `#ffffff` | Page background |
| `{{BRAND_TEXT}}` | `#16221c` | Body text |
| `{{BRAND_BORDER}}` | `#1f7b5d` | Card border |
| `{{BRAND_BG_LIGHT}}` | `#f4faf6` | Card soft fill |
| `{{BRAND_CAPTION}}` | `rgba(22,34,28,0.58)` | Photo caption color (raise to `0.78` for older readers) |
| `{{BRAND_DARK}}` | `#092f27` | Dark companion color for institutional opening / closing bands |
| `{{BRAND_DIVIDER}}` | `#9eada6` | Neutral divider and label separator |
| `{{BRAND_SECONDARY_TEXT}}` | `#5b6f79` | Cool supporting-text color |
| `{{BRAND_GRID_BORDER}}` | `#d3ddd8` | Light border for compact information grids |

When a main visual is supplied, sample it before using these defaults. Map the visual's light field, readable dark, dominant rule/headline color, and small accent to the tokens by role. Do not force the fallback green or an invented dark color onto an established visual. When no authoritative visual exists, use the fallback or derive a restrained accent from the brand logo.

## Copy Boundary

Wrap your article in a copy boundary so the team can paste the whole fragment into the WeChat editor without manual selection.

```html
<!-- 微信公众号复制开始 -->
<section style="box-sizing:border-box;max-width:677px;margin:0 auto;padding:0 0 38px;background:{{BRAND_BG}};color:{{BRAND_TEXT}};font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',Arial,sans-serif;line-height:1.86;letter-spacing:0;">
  ...
</section>
<!-- 微信公众号复制结束 -->
```

The `max-width:677px` matches the WeChat editor's content column on mobile. Do not change it.

## Rounded Protected-Anchor Photo Placeholder

Use when the user wants to paste or upload photos manually in the WeChat editor.

```html
<section style="box-sizing:border-box;margin:30px 8px 0;padding:10px;border-radius:30px;background:#ffffff;border:2px solid {{BRAND_PRIMARY}};overflow:hidden;">
  <section style="box-sizing:border-box;min-height:96px;margin:0;padding:0;border-radius:22px;background:#ffffff;border:2px dashed transparent;overflow:hidden;text-align:center;font-size:0;line-height:0;">
    <span style="font-size:0;line-height:0;">&nbsp;</span>
  </section>
</section>
<p style="margin:11px 10px 0;font-size:12px;line-height:1.8;color:{{BRAND_CAPTION}};text-align:center;">caption</p>
```

Insertion workflow:

1. Paste the full article fragment into WeChat.
2. Click once in the blank inner area.
3. Insert or paste the photo directly without selecting or deleting anything first.
4. Confirm that the frame remains and the photo touches the intended inner edge.

If the user sees a caret but the image does not insert, click the same blank area once more and use WeChat's image-upload command. Do not repair the slot by adding visible spaces or a padded instruction paragraph.

Use this rounded variant only when it matches the selected visual register. Do not treat 30px rounding as a universal premium default.

## Institutional Photo Placeholder

Use for modern institutional, public-interest, environmental, public-health, or regulated-industry articles.

```html
<section style="box-sizing:border-box;margin:28px 8px 0;padding:0;background:#eef3f0;border:1px solid #cbd7d1;border-top:4px solid {{BRAND_PRIMARY}};text-align:center;overflow:hidden;">
  <section style="box-sizing:border-box;min-height:96px;margin:0;padding:0;font-size:0;line-height:0;overflow:hidden;">
    <span style="font-size:0;line-height:0;">&nbsp;</span>
  </section>
</section>
<p style="margin:9px 8px 0;font-size:12px;line-height:1.7;color:{{BRAND_CAPTION}};text-align:center;">{{CAPTION}}</p>
```

Design rules:
- Use 0-4px radius, a cool-neutral fill, a narrow border, and one strong top rule.
- Keep the same direct-paste protected-anchor workflow as the rounded variant.
- Do not mix this frame with the 30px rounded frame in one article.

## Flow Photo Frame (Event Recap)

Use for a wide event photo when the page needs a little structure but should remain airy. The template contains only `section`, `p`, and `span`.

```html
<section style="box-sizing:border-box;margin:28px 8px 0;padding:0;border:1px solid {{BRAND_GRID_BORDER}};background:#ffffff;overflow:hidden;">
  <p style="margin:0;padding:10px 13px;border-bottom:1px solid {{BRAND_GRID_BORDER}};font-size:0;line-height:1;">
    <span style="display:inline-block;font-size:11px;line-height:1;color:{{BRAND_PRIMARY}};font-weight:800;vertical-align:middle;">{{PHOTO_ORDER}}</span>
    <span style="display:inline-block;margin-left:10px;font-size:11px;line-height:1;color:{{BRAND_SECONDARY_TEXT}};font-weight:600;vertical-align:middle;">{{PHOTO_ROLE}}</span>
  </p>
  <section style="box-sizing:border-box;min-height:96px;margin:0;padding:0;background:{{BRAND_BG_LIGHT}};text-align:center;overflow:hidden;font-size:0;line-height:0;">
    <span style="font-size:0;line-height:0;">&nbsp;</span>
  </section>
</section>
<p style="margin:9px 8px 0;font-size:12px;line-height:1.7;color:{{BRAND_CAPTION}};text-align:center;">{{CAPTION}}</p>
```

Design rules:
- Click the blank protected-anchor area and insert the photo directly. Do not delete the inner section or its anchor.
- Use one leading photo per chapter. Keep `20-28px` between its preceding copy and the frame.
- Keep the frame square or nearly square-cornered; let the photograph provide the visual energy.

## Event Recap Chapter Header

Use to separate event phases without crowding the page with cards. This is a flow-only replacement for unequal two-cell chapter rows.

```html
<section style="box-sizing:border-box;margin:54px 8px 0;padding:0 0 18px;border-bottom:2px solid {{BRAND_PRIMARY}};">
  <p style="margin:0;font-size:0;line-height:1;">
    <span style="display:inline-block;padding:7px 10px;background:{{BRAND_PRIMARY}};font-size:12px;line-height:1;color:#ffffff;font-weight:800;vertical-align:middle;">{{ORDER}}</span>
    <span style="display:inline-block;margin-left:12px;font-size:11px;line-height:1;color:{{BRAND_SECONDARY_TEXT}};font-weight:700;vertical-align:middle;">{{CHAPTER_LABEL}}</span>
  </p>
  <p style="margin:13px 0 0;font-size:25px;line-height:1.45;color:{{BRAND_TEXT}};font-weight:800;">{{CHAPTER_TITLE}}</p>
  <p style="margin:9px 0 0;font-size:15px;line-height:1.9;color:{{BRAND_SECONDARY_TEXT}};">{{CHAPTER_LEAD}}</p>
</section>
```

Keep `{{CHAPTER_LEAD}}` to one sentence. The `54px` top margin is intentional breathing room on mobile.

## Node Divider

Use as a quiet pause after 2-3 consecutive photos or between two short narrative beats.

```html
<section style="box-sizing:border-box;margin:42px 8px 0;padding:0;font-size:0;line-height:1;text-align:center;">
  <span style="display:inline-block;width:34%;height:1px;background:{{BRAND_DIVIDER}};vertical-align:middle;"></span>
  <span style="display:inline-block;width:8px;height:8px;margin:0 12px;border:2px solid {{BRAND_PRIMARY}};border-radius:50%;background:#ffffff;vertical-align:middle;"></span>
  <span style="display:inline-block;width:34%;height:1px;background:{{BRAND_DIVIDER}};vertical-align:middle;"></span>
</section>
```

Do not add explanatory copy inside the divider. Its job is rhythm, not another content layer.

## 4:5 Portrait Collage Wall (Single Bitmap)

Use when every participant needs to appear but the user will crop and compose the portraits before insertion. The HTML holds one finished bitmap, not a grid of individual image cells.

```html
<section style="box-sizing:border-box;margin:30px 8px 0;padding:0;border:1px solid {{BRAND_GRID_BORDER}};border-top:4px solid {{BRAND_PRIMARY}};background:#ffffff;overflow:hidden;">
  <p style="margin:0;padding:11px 13px;border-bottom:1px solid {{BRAND_GRID_BORDER}};font-size:0;line-height:1;">
    <span style="display:inline-block;font-size:11px;line-height:1;color:{{BRAND_PRIMARY}};font-weight:800;vertical-align:middle;">{{WALL_LABEL}}</span>
    <span style="display:inline-block;margin-left:10px;font-size:11px;line-height:1;color:{{BRAND_SECONDARY_TEXT}};font-weight:600;vertical-align:middle;">{{PORTRAIT_COUNT}} PEOPLE</span>
  </p>
  <section style="box-sizing:border-box;min-height:120px;margin:0;padding:0;background:{{BRAND_BG_LIGHT}};text-align:center;overflow:hidden;font-size:0;line-height:0;">
    <span style="font-size:0;line-height:0;">&nbsp;</span>
  </section>
</section>
<p style="margin:10px 8px 0;font-size:12px;line-height:1.7;color:{{BRAND_CAPTION}};text-align:center;">{{WALL_CAPTION}}</p>
```

Composition rules:
- Crop every portrait to the same 4:5 cell ratio, then assemble a square matrix. `3 x 3` yields a 4:5 wall for up to 9 people; `4 x 4` yields a 4:5 wall for up to 16.
- Above 16 people, use two labeled 4:5 walls. Do not reduce faces until they become thumbnails on a 375px phone.
- Keep face scale, eye line, background treatment, and gutter width consistent. Put detailed names in surrounding copy or a separate list unless in-image labels remain legible at phone width.
- Export the wall at about `1200 x 1500 px`, click the blank protected-anchor area, and insert it directly without deleting the anchor first.

## Repeated Speaker Card (Single-Column)

Use when a section lists many people and each person needs a photo placeholder plus a short text stack.

```html
<section style="box-sizing:border-box;margin:12px 8px 0;padding:16px 14px 18px;border-radius:18px;background:#ffffff;border:1px solid #e9ece6;">
  <p style="margin:0;font-size:11px;line-height:1.6;color:{{CHIP_COLOR}};font-weight:700;letter-spacing:1px;">{{ORDER}} · {{TEAM_LABEL}}</p>
  <p style="margin:4px 0 0;font-size:19px;line-height:1.4;color:{{BRAND_TEXT}};font-weight:800;">{{NAME}}</p>
  <p style="margin:4px 0 0;font-size:13px;line-height:1.8;color:rgba(22,34,28,0.62);">{{TOPIC}}</p>
  <section style="box-sizing:border-box;margin:14px 0 0;padding:10px;border-radius:24px;background:#ffffff;border:2px solid {{BRAND_PRIMARY}};overflow:hidden;">
    <section style="box-sizing:border-box;min-height:88px;margin:0;padding:0;border-radius:18px;background:#ffffff;border:2px dashed transparent;overflow:hidden;text-align:center;font-size:0;line-height:0;">
      <span style="font-size:0;line-height:0;">&nbsp;</span>
    </section>
  </section>
</section>
```

Design rules:
- One card per row by default. Repeat the card 6-20 times if needed.
- Use `{{CHIP_COLOR}}` for the department / category label only. Let the frame keep the unified `{{BRAND_PRIMARY}}` border.
- This pattern is safer than a dense 3-column speaker wall when real photos will be inserted in the WeChat editor.

## Centered QR Placeholder (Dark Footer)

Use when a dark closing section needs a small centered QR or square-asset placeholder.

```html
<section style="box-sizing:border-box;margin:18px auto 0;width:170px;max-width:100%;padding:10px;border-radius:30px;background:#ffffff;border:2px solid rgba(255,255,255,0.68);overflow:hidden;">
  <section style="box-sizing:border-box;min-height:112px;margin:0;padding:0;border-radius:22px;background:#ffffff;border:2px dashed transparent;overflow:hidden;text-align:center;font-size:0;line-height:0;">
    <span style="font-size:0;line-height:0;">&nbsp;</span>
  </section>
</section>
<p style="margin:11px 10px 0;font-size:12px;line-height:1.8;color:rgba(255,255,255,0.72);text-align:center;">{{QR_CAPTION}}</p>
```

Design rules:
- Keep the wrapper narrow and centered. Do not let a row-level wrapper become the visual square.
- If the footer background is light, change the border/text colors accordingly.
- Use the same direct-paste protected-anchor workflow as the main photo placeholders.

## Real Image in HTML Frame

Use only when the HTML should reference an already-uploaded image directly (e.g. a WeChat-hosted image URL).

```html
<section style="box-sizing:border-box;margin:30px 8px 0;padding:10px;border-radius:30px;background:#ffffff;border:2px solid {{BRAND_PRIMARY}};overflow:hidden;">
  <img src="https://your-cdn.example.com/photo.jpg" alt="场景照片" style="display:block;width:100%;height:auto;border-radius:22px;">
</section>
```

If the user copies the image alone, the frame will not follow. Copy the full HTML section or bake the frame into the image.

## Soft Closing Card (Border-Only)

A soft, bordered closing block. Solid color, no gradient, no shadow.

```html
<section style="box-sizing:border-box;margin:42px 8px 0;padding:30px 24px;border-radius:30px;background:#ffffff;border:1px solid {{BRAND_BORDER}};">
  <p style="margin:0;font-size:12px;color:{{BRAND_PRIMARY}};font-weight:800;letter-spacing:1px;">{{CLOSING_LABEL}}</p>
  <p style="margin:11px 0 0;font-size:30px;line-height:1.32;color:{{BRAND_TEXT}};font-weight:800;">{{CLOSING_HEADING}}</p>
  <p style="margin:6px 0 0;font-size:30px;line-height:1.32;color:{{BRAND_PRIMARY}};font-weight:800;">{{CLOSING_TAGLINE}}</p>
  <p style="margin:21px 0 0;font-size:15px;line-height:2;color:rgba(22,34,28,0.78);">{{CLOSING_BODY}}</p>
</section>
```

## Title Section

First section in the article. Has `padding:0` (do not add `padding-top`).

```html
<section style="box-sizing:border-box;margin:0 8px;padding:0;">
  <p style="margin:0 0 18px;line-height:1;font-size:0;">
    <span style="display:inline-block;width:8px;height:8px;margin-right:6px;background:{{BRAND_PRIMARY}};border-radius:50%;"></span>
    <span style="display:inline-block;width:8px;height:8px;margin-right:6px;background:{{BRAND_ACCENT}};border-radius:50%;"></span>
    <span style="display:inline-block;width:8px;height:8px;background:{{BRAND_TERTIARY}};border-radius:50%;"></span>
  </p>
  <p style="margin:0;font-size:40px;line-height:1.2;color:{{BRAND_TEXT}};font-weight:800;letter-spacing:1px;">{{TITLE_LINE_1}}</p>
  <p style="margin:6px 0 0;font-size:40px;line-height:1.2;color:{{BRAND_PRIMARY}};font-weight:800;letter-spacing:1px;">{{TITLE_LINE_2}}</p>
  <p style="margin:24px 0 0;font-size:16px;line-height:1.9;color:rgba(22,34,28,0.78);">{{SUBTITLE}}</p>
</section>
```

## Sub-title with 4-action + metaphor

Use when the sub-title needs to express more than one category (e.g. core service + secondary) and end on a warm metaphor.

```html
<p style="margin:24px 0 0;font-size:16px;line-height:1.9;color:rgba(22,34,28,0.78);">{{ACTION_1}}、{{ACTION_2}}、{{ACTION_3}}、{{ACTION_4}}——这是{{METAPHOR}}。</p>
```

Design rules:
- 4 short actions, comma-separated, then a 破折号 and a metaphor.
- Avoid technical/functional phrasing like "把…搬到…让您…" — it reads like an installation manual.
- The metaphor must be **different** from the main title's product name (avoid 驿站 if title is 健康驿站).
- Keep total length under 30 characters for mobile readability.

## Card with 3 Bullets

Use when a service has been over-explained with 4+ bullets. Cut to 3 bullets and let the summary block carry the punchline.

```html
<section style="box-sizing:border-box;padding:24px 0;border-bottom:1px solid #eef2ee;">
  <p style="margin:0;line-height:1;">
    <span style="display:inline-block;vertical-align:middle;font-family:Georgia,serif;font-size:22px;color:{{BRAND_PRIMARY}};font-weight:800;letter-spacing:1px;">01</span>
    <span style="display:inline-block;vertical-align:middle;margin-left:12px;font-size:13px;color:{{BRAND_PRIMARY}};font-weight:800;letter-spacing:1.5px;">{{KEY_CHAR}}</span>
    <span style="display:inline-block;vertical-align:middle;margin-left:8px;font-size:18px;color:{{BRAND_TEXT}};font-weight:800;">{{CARD_TITLE}}</span>
  </p>
  <p style="margin:8px 0 0;font-size:15px;line-height:1.9;color:{{BRAND_TEXT}};font-weight:700;">{{CARD_SUMMARY}}</p>
  <section style="box-sizing:border-box;margin:12px 0 0;padding:12px 14px;background:{{BRAND_BG_LIGHT}};border-radius:12px;">
    <p style="margin:0;font-size:14px;line-height:2;color:rgba(22,34,28,0.78);"><span style="color:{{BRAND_PRIMARY}};font-weight:800;">{{LABEL_1}} · </span>{{BODY_1}}</p>
    <p style="margin:4px 0 0;font-size:14px;line-height:2;color:rgba(22,34,28,0.78);"><span style="color:{{BRAND_PRIMARY}};font-weight:800;">{{LABEL_2}} · </span>{{BODY_2}}</p>
    <p style="margin:4px 0 0;font-size:14px;line-height:2;color:rgba(22,34,28,0.78);"><span style="color:{{BRAND_PRIMARY}};font-weight:800;">{{LABEL_3}} · </span>{{BODY_3}}</p>
  </section>
</section>
```

Design rules:
- 3 bullets max per card. Anything more → cut.
- Each bullet has a colored label (`{{LABEL}} · `) and a one-line body.
- The summary line sits between the title and the bullet box.

## Solid-Color Anchor Block

Use as a visual anchor after a list of cards. The slogan becomes a solid block with contrasting text — it pulls the eye and locks the message in memory.

```html
<section style="box-sizing:border-box;margin:30px 8px 0;padding:22px 22px 24px;background:{{BRAND_PRIMARY}};border-radius:18px;">
  <p style="margin:0;font-size:12px;color:rgba(255,255,255,0.7);font-weight:800;letter-spacing:1.5px;">{{ANCHOR_LABEL}}</p>
  <p style="margin:12px 0 0;font-size:20px;line-height:1.6;color:#ffffff;font-weight:800;letter-spacing:0.5px;">{{ANCHOR_TEXT}}</p>
</section>
```

Design rules:
- Use the brand primary color as background.
- The label uses a 70%-opacity white for hierarchy without breaking the block.
- The slogan is white, 20px, 800 weight.
- Place after a series of cards, before the CTA.

## Key Positioning Strip

Use to highlight a single critical sentence in the article (e.g. a brand positioning statement).

```html
<section style="box-sizing:border-box;margin:30px 8px 0;padding:18px 20px;background:{{BRAND_BG_LIGHT}};border-left:3px solid {{BRAND_PRIMARY}};border-radius:0 12px 12px 0;">
  <p style="margin:0;font-size:15px;line-height:1.9;color:{{BRAND_TEXT}};font-weight:700;">{{KEY_STATEMENT}}</p>
</section>
```

## Section Label

Use a small uppercase label before a section's heading to introduce the topic.

```html
<p style="margin:42px 8px 0;line-height:1;">
  <span style="display:inline-block;vertical-align:middle;font-size:12px;color:{{BRAND_PRIMARY}};font-weight:800;letter-spacing:1.5px;">{{LABEL_CATEGORY}} · {{LABEL_QUESTION}}</span>
</p>
<p style="margin:8px 8px 0;font-size:22px;line-height:1.4;color:{{BRAND_TEXT}};font-weight:800;">{{SECTION_HEADING}}</p>
```

## Tip / Disclaimer Block

Use at the end of an article for legal disclaimers or important reminders.

```html
<section style="box-sizing:border-box;margin:30px 8px 0;padding:16px 18px;background:{{BRAND_BG_LIGHT}};border-radius:14px;">
  <p style="margin:0;font-size:13px;line-height:1.8;color:rgba(22,34,28,0.78);">{{TIP_TEXT}}</p>
</section>
```

## Risk-control Word Substitutions (Generic)

When the article topic has industry-specific risk words, run a substitution pass before publishing. Common patterns:

| Avoid | Use instead |
|---|---|
| Absolute claims (e.g. "100%", "guaranteed", "一定", "必定") | Qualified language (e.g. "通常", "多数情况下", "建议") |
| Affiliation with regulated institutions (medical, financial, legal) | Neutral language (e.g. "提个醒", "多关注", "建议咨询") |
| Price promises ("免费", "best price") | Neutral cost language ("不收费", "合理定价") |
| Outcome promises ("治愈", "包好", "100% 有效") | Process language ("多一份关注", "提个醒") |

To build a project-specific table, grep the article for words that imply outcomes, promises, or institutional affiliation, then build the substitution table per industry.

## Photo Caption Color by reader age band

Photo captions in pale gray (`#8a9990`) are too pale for readers over 60. Use a semi-transparent dark text `rgba(22,34,28,0.78)` for older readers, or a lighter `rgba(22,34,28,0.58)` for younger readers. The `{{BRAND_CAPTION}}` token abstracts this choice — set its value based on the audience.

```html
<p style="margin:11px 10px 0;font-size:13px;line-height:1.7;color:{{BRAND_CAPTION}};text-align:center;">{{CAPTION}}</p>
```

Recommended values:

| Reader age band | `{{BRAND_CAPTION}}` value | Font size |
|---|---|---|
| Older readers (中老年, 60+) | `rgba(22,34,28,0.78)` | 13px |
| General adult readers | `rgba(22,34,28,0.58)` | 12px |
| Younger readers (under 40) | `rgba(22,34,28,0.45)` | 11-12px |

## Top-of-Article Minimal Header

Skip the top logo+brand composite. Let the title be the only opener. This makes the article feel less cluttered and more editorial.

This is one valid option, not a universal rule. A short brand name may appear in a modern institutional hero and closing when the project requires clear ownership. Follow the project naming rule and avoid accidental full-name/short-name mixing or adjacent repetition.

## Modern Institutional Hero

Use for government-guided public services, corporate public-interest actions, and regulated-industry education.

```html
<section style="box-sizing:border-box;margin:0 8px;padding:0;background:{{BRAND_PRIMARY}};border-top:8px solid {{BRAND_DARK}};">
  <p style="margin:0;padding:24px 22px 0;font-size:12px;line-height:1.5;color:rgba(255,255,255,0.78);font-weight:700;">{{SHORT_BRAND}} · {{TOPIC_LABEL}}</p>
  <p style="margin:18px 22px 0;font-size:37px;line-height:1.22;color:#ffffff;font-weight:800;">{{TITLE_LINE_1}}<br>{{TITLE_LINE_2}}</p>
  <p style="margin:22px 22px 0;padding:17px 0 21px;border-top:1px solid rgba(255,255,255,0.24);font-size:14px;line-height:1.8;color:#ffffff;font-weight:700;">{{VERIFIED_INSTITUTIONAL_LINE}}</p>
</section>
```

Use system sans-serif typography. Do not add seals, serif display type, gold ornament, or formal numerals unless the brief explicitly requires a traditional register.

## Modern Numbered Section Header

```html
<section style="box-sizing:border-box;margin:44px 8px 0;padding:0 0 14px;border-bottom:2px solid {{BRAND_PRIMARY}};">
  <p style="margin:0;font-size:0;line-height:1;">
    <span style="display:inline-block;font-size:13px;line-height:1;color:{{BRAND_PRIMARY}};font-weight:800;vertical-align:middle;">{{ORDER}}</span>
    <span style="display:inline-block;width:1px;height:13px;margin:0 10px;background:{{BRAND_DIVIDER}};vertical-align:middle;"></span>
    <span style="display:inline-block;font-size:12px;line-height:1;color:{{BRAND_SECONDARY_TEXT}};font-weight:700;vertical-align:middle;">{{SECTION_LABEL}}</span>
  </p>
  <p style="margin:10px 0 0;font-size:26px;line-height:1.45;color:{{BRAND_TEXT}};font-weight:800;">{{SECTION_HEADING}}</p>
</section>
```

## Compact Three-Fact Flow (No Table)

Use for three short facts or actions. The vertical rhythm survives WeChat paste transformations and remains readable at 375px.

```html
<section style="box-sizing:border-box;margin:20px 8px 0;padding:0 16px;border:1px solid {{BRAND_GRID_BORDER}};border-top:4px solid {{BRAND_PRIMARY}};background:#ffffff;">
  <section style="box-sizing:border-box;margin:0;padding:16px 0;border-bottom:1px solid {{BRAND_GRID_BORDER}};">
    <p style="margin:0;font-size:0;line-height:1;"><span style="display:inline-block;width:30px;font-size:12px;line-height:1;color:{{BRAND_PRIMARY}};font-weight:800;vertical-align:middle;">01</span><span style="display:inline-block;font-size:17px;line-height:1;color:{{BRAND_TEXT}};font-weight:800;vertical-align:middle;">{{FACT_1}}</span></p>
    <p style="margin:7px 0 0 30px;font-size:13px;line-height:1.75;color:{{BRAND_SECONDARY_TEXT}};">{{FACT_1_BODY}}</p>
  </section>
  <section style="box-sizing:border-box;margin:0;padding:16px 0;border-bottom:1px solid {{BRAND_GRID_BORDER}};">
    <p style="margin:0;font-size:0;line-height:1;"><span style="display:inline-block;width:30px;font-size:12px;line-height:1;color:{{BRAND_PRIMARY}};font-weight:800;vertical-align:middle;">02</span><span style="display:inline-block;font-size:17px;line-height:1;color:{{BRAND_TEXT}};font-weight:800;vertical-align:middle;">{{FACT_2}}</span></p>
    <p style="margin:7px 0 0 30px;font-size:13px;line-height:1.75;color:{{BRAND_SECONDARY_TEXT}};">{{FACT_2_BODY}}</p>
  </section>
  <section style="box-sizing:border-box;margin:0;padding:16px 0;">
    <p style="margin:0;font-size:0;line-height:1;"><span style="display:inline-block;width:30px;font-size:12px;line-height:1;color:{{BRAND_PRIMARY}};font-weight:800;vertical-align:middle;">03</span><span style="display:inline-block;font-size:17px;line-height:1;color:{{BRAND_TEXT}};font-weight:800;vertical-align:middle;">{{FACT_3}}</span></p>
    <p style="margin:7px 0 0 30px;font-size:13px;line-height:1.75;color:{{BRAND_SECONDARY_TEXT}};">{{FACT_3_BODY}}</p>
  </section>
</section>
```

Keep each body to one short sentence. If the three facts are only labels, remove the body paragraphs instead of converting them to columns.

## White-Interior Accent-Edge Grouped Card

Use when the authoritative poster has two or three bright accents but the article needs a clean, light, copy-paste-safe reading surface. Keep the card and every row white; let narrow edge rules carry the palette.

```html
<section style="box-sizing:border-box;margin:14px 8px 0;padding:0;background:#ffffff;border:1px solid {{BRAND_GRID_BORDER}};border-radius:16px;overflow:hidden;">
  <section style="box-sizing:border-box;margin:0;padding:17px 18px;border-left:5px solid {{BRAND_ACCENT}};border-bottom:1px solid {{BRAND_GRID_BORDER}};">
    <p style="margin:0;font-size:17px;line-height:1.55;color:{{BRAND_TEXT}};font-weight:800;">{{ITEM_1_TITLE}}</p>
    <p style="margin:6px 0 0;font-size:14px;line-height:1.85;color:{{BRAND_SECONDARY_TEXT}};">{{ITEM_1_BODY}}</p>
  </section>
  <section style="box-sizing:border-box;margin:0;padding:17px 18px;border-left:5px solid {{BRAND_PRIMARY}};border-bottom:1px solid {{BRAND_GRID_BORDER}};">
    <p style="margin:0;font-size:17px;line-height:1.55;color:{{BRAND_TEXT}};font-weight:800;">{{ITEM_2_TITLE}}</p>
    <p style="margin:6px 0 0;font-size:14px;line-height:1.85;color:{{BRAND_SECONDARY_TEXT}};">{{ITEM_2_BODY}}</p>
  </section>
  <section style="box-sizing:border-box;margin:0;padding:17px 18px;border-left:5px solid {{BRAND_TERTIARY}};">
    <p style="margin:0;font-size:17px;line-height:1.55;color:{{BRAND_TEXT}};font-weight:800;">{{ITEM_3_TITLE}}</p>
    <p style="margin:6px 0 0;font-size:14px;line-height:1.85;color:{{BRAND_SECONDARY_TEXT}};">{{ITEM_3_BODY}}</p>
  </section>
</section>
```

Design rules:
- Sample a maximum of three accents from the authoritative visual; do not invent a rainbow palette.
- Use one accent consistently for the main flow, one for time or the first item, and one for warnings or the third item.
- Keep the outer border and row dividers neutral. Do not tint the row backgrounds.
- Use the same `8px` horizontal margin for the title, cards, photo frames, and closing block.
- Prefer this component over faux glass in WeChat. It does not depend on retained page backgrounds, alpha compositing, `backdrop-filter`, gradients, shadows, or positioning.

## Troubleshooting Wording

Use these exact phrasings when answering the team about common issues:

- **Frame disappears while replacing a placeholder**: "The placeholder node was probably selected and deleted with its wrapper. Restore the protected-anchor frame, click its blank inner area, and paste directly without deleting first."
- **Frame does not travel with a copied image**: "The frame is an HTML wrapper. Copy the whole framed section or use a baked-frame PNG."
- **Photo has too much blank space**: "A legacy padded instruction paragraph survived beside the image. Replace that slot with the protected-anchor version and paste directly."
- **Photo carries background color**: "That background is baked into the bitmap. Use a clean original photo inside an HTML frame."
- **Top of article is empty**: "The WeChat editor adds default spacing above the article body. Set the first section's padding-top to 0."
- **Photo frame doesn't show**: "Local image paths don't work in WeChat. Use a placeholder HTML frame, then upload the photo in the editor."
- **Speaker wall looks cut off**: "The card wall is too dense for the WeChat editor. Switch to a single-column speaker-card flow or a simpler repeated-card layout."
- **Layout stretches or gains horizontal scrolling after paste**: "WeChat wrapped the table in a horizontal scroller and reset its cell widths. Replace the whole table with `section` / `p` / `span` flow; extra `td` width rules will not make the block reliable."
- **QR code area becomes full width**: "The QR placeholder inherited a row-level wrapper. Use a narrow centered `section` as the visual frame."

## Pre-publish Checklist

Run these checks before declaring an article ready:

- [ ] Comparable content blocks follow the design fingerprint's deliberate outer and inset baselines; no fixed width exceeds the mobile column.
- [ ] Opening whitespace is intentional: immersive heroes may start at `padding-top:0`, while editorial or quiet openers may use approximately `18-40px`.
- [ ] Photo frames match one selected visual register; rounded and institutional frame languages are not mixed casually.
- [ ] Every manual photo or QR slot contains one zero-size `&nbsp;` protected anchor, no padded instruction paragraph, and no delete-first handoff wording.
- [ ] Repeated photo-person sections use a verified single-column or editor-tested layout; do not trust browser-only 3-column walls.
- [ ] Participant collages are inserted as one finished bitmap; a 4:5 wall contains no more than 16 readable faces before splitting.
- [ ] Footer QR / square asset placeholders stay narrow and centered in flow layout.
- [ ] Photo captions use `rgba(22,34,28,0.78)` or darker.
- [ ] No `<table>`, `<tbody>`, `<tr>`, or `<td>` unless a real-editor exception is documented.
- [ ] No script, event handler, unverified `position:`, Grid, or local image path. Gradients and shadows follow the selected delivery mode and degrade gracefully.
- [ ] Tag balance: section / p / span open and close counts match.
- [ ] Main visual colors were sampled and assigned by role; fallback colors did not override an authoritative palette.
- [ ] New chapters have `44-60px` breathing room, copy-to-photo gaps are `20-28px`, and no more than 2-3 photos run together without a divider or header.
- [ ] Risk-word scan: 0 matches in body (disclaimer area may have some).
- [ ] Title section matches the synthesized design fingerprint; a 3-color decoration bar is optional, not mandatory.
- [ ] Brand names follow the project’s full-name / short-name rule with no accidental variants or adjacent repetition.
- [ ] Government designations, “唯一” claims, incentive amounts, and official-looking images have verified scope and evidence.
- [ ] AI-generated images do not fabricate logos, seals, certificates, official documents, or institutional proof.
