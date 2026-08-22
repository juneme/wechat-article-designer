# Core Inline Primitives

Use only the blocks required by the article's module manifest. Replace every bracketed field with final copy, adapt colors and spacing to the article's design contract, and keep Chinese letter spacing at `0`.

## Publishable boundary

```html
<!-- 微信公众号复制开始 -->
<section style="margin:0;padding:0;background:#FFFFFF;color:#202020;">
  <!-- final audience-facing article -->
</section>
<!-- 微信公众号复制结束 -->
```

Only content inside the boundary is synchronized into the server draft payload. The comments are parser markers, not a clipboard feature. Asset maps, replacement instructions, design notes, and validation results stay outside.

## Editable image placeholder

Use during preview preparation before the final image is uploaded through the console server. The frame owns its height and styling. Keep exactly one direct-child 1px paragraph so the editor exposes a caret when manual inspection is necessary.

```html
<section style="height:220px;margin:24px 8px 0;padding:0;background:#F2F2F0;border:1px solid #D8D8D4;overflow:hidden;">
  <p style="margin:0;padding:0;font-size:1px;line-height:1px;letter-spacing:0;">&nbsp;</p>
</section>
```

Provide the intended filename and crop outside the copy boundary. Do not put replacement instructions, filenames, local paths, nested labels, or decorative children inside the frame.

## Hosted image

Use only after the final body image has been uploaded to an approved HTTPS host.

```html
<section style="margin:24px 8px 0;padding:0;">
  <img src="https://mmbiz.qpic.cn/FINAL_ARTICLE_IMAGE" alt="[concise image description]" style="display:block;width:100%;height:auto;margin:0;border:0;" />
</section>
```

Do not ship the example URL. Avoid forced cropping unless the exact image and phone preview have been tested.

## Caption

```html
<p style="margin:8px 8px 0;padding:0;color:#6A6A66;font-size:12px;line-height:1.7;letter-spacing:0;text-align:left;">
  [What the image shows, when needed · source or qualifier]
</p>
```

A caption adds context, source, time, identity, or a limitation. Remove it when it merely restates the image.

## Section heading

```html
<section style="margin:42px 18px 0;padding:0 0 10px;border-bottom:2px solid #202020;">
  <p style="margin:0;color:#76766F;font-size:11px;line-height:1.5;font-weight:700;letter-spacing:0;">
    [Meaningful index, date, or category]
  </p>
  <p style="margin:6px 0 0;padding:0;color:#202020;font-size:24px;line-height:1.45;font-weight:700;letter-spacing:0;">
    [Literal section heading]
  </p>
</section>
```

Omit the label when it adds no orientation. Test the longest real heading at 320px.

## Compact evidence flow

Use repeated rows only for facts that share one schema.

```html
<section style="margin:24px 18px 0;padding:0;border-top:1px solid #CFCFCA;">
  <section style="margin:0;padding:16px 0;border-bottom:1px solid #CFCFCA;">
    <p style="margin:0;color:#6A6A66;font-size:11px;line-height:1.5;font-weight:700;letter-spacing:0;">[LABEL]</p>
    <p style="margin:5px 0 0;color:#202020;font-size:17px;line-height:1.6;font-weight:700;letter-spacing:0;">[Verified fact]</p>
    <p style="margin:5px 0 0;color:#50504C;font-size:14px;line-height:1.8;letter-spacing:0;">[Qualifier, unit, source, or explanation]</p>
  </section>
  <section style="margin:0;padding:16px 0;border-bottom:1px solid #CFCFCA;">
    <p style="margin:0;color:#6A6A66;font-size:11px;line-height:1.5;font-weight:700;letter-spacing:0;">[LABEL]</p>
    <p style="margin:5px 0 0;color:#202020;font-size:17px;line-height:1.6;font-weight:700;letter-spacing:0;">[Verified fact]</p>
    <p style="margin:5px 0 0;color:#50504C;font-size:14px;line-height:1.8;letter-spacing:0;">[Qualifier, unit, source, or explanation]</p>
  </section>
</section>
```

Do not use this structure to make unrelated paragraphs look consistent. Keep units, dates, requirements, and exceptions adjacent to the fact they qualify.

## Action band

Use one clear action path. Do not manufacture urgency.

```html
<section style="margin:40px 8px 0;padding:24px 18px;background:#202020;color:#FFFFFF;">
  <p style="margin:0;color:#CFCFCA;font-size:11px;line-height:1.5;font-weight:700;letter-spacing:0;">[ACTION LABEL]</p>
  <p style="margin:7px 0 0;padding:0;color:#FFFFFF;font-size:22px;line-height:1.45;font-weight:700;letter-spacing:0;">[What the reader should do]</p>
  <p style="margin:12px 0 0;color:#F2F2F0;font-size:15px;line-height:1.85;letter-spacing:0;">[Method, deadline, eligibility, contact path, or next step]</p>
</section>
```

If there is no requested reader action, use a quiet closing rather than an artificial call to action.

## Disclaimer or evidence boundary

```html
<section style="margin:24px 18px 0;padding:14px 0 0;border-top:1px solid #D8D8D4;">
  <p style="margin:0;color:#6A6A66;font-size:12px;line-height:1.75;letter-spacing:0;">
    [Necessary scope, source, eligibility, medical/legal qualifier, update time, or final-authority statement]
  </p>
</section>
```

Place the qualifier near the claim it limits when possible. A closing disclaimer must not contradict stronger promises earlier in the article.

## Terminal or code card

Use only for real commands, code, logs, or technical identifiers. Do not set narrative Chinese prose in a terminal style.

```html
<section style="margin:24px 8px 0;padding:0;background:#202020;border:1px solid #3A3A38;border-radius:6px;overflow:hidden;">
  <p style="margin:0;padding:10px 14px;background:#2A2A28;color:#D8D8D4;font-size:12px;line-height:1.5;letter-spacing:0;">
    <span style="color:#FF6B5E;">●</span>
    <span style="color:#F0C84B;">●</span>
    <span style="color:#67C587;">●</span>
    <span style="color:#A8A8A2;"> [Meaningful filename or environment]</span>
  </p>
  <p style="margin:0;padding:16px 14px;color:#F2F2F0;font-size:13px;line-height:1.75;letter-spacing:0;font-family:Menlo,Consolas,monospace;white-space:pre-wrap;word-break:break-all;">[Exact command or code]</p>
</section>
```

Keep commands exact and keep explanations outside the code surface. The colored dots are a quiet file-window cue, not a reason to turn every quote into a terminal.

## Dialogue or interview record

Preserve speaker identity and reading order in ordinary flow. Color may distinguish speakers but cannot be the only identity signal.

```html
<section style="margin:24px 8px 0;padding:0;">
  <section style="margin:0;padding:0 0 0 14px;border-left:3px solid #3155F5;">
    <p style="margin:0;color:#3155F5;font-size:12px;line-height:1.5;font-weight:700;letter-spacing:0;">采访者 · [姓名或角色]</p>
    <p style="margin:7px 0 0;color:#202020;font-size:15px;line-height:1.85;letter-spacing:0;">[问题]</p>
  </section>
  <section style="margin:18px 0 0;padding:0 0 0 14px;border-left:3px solid #67A57B;">
    <p style="margin:0;color:#477A57;font-size:12px;line-height:1.5;font-weight:700;letter-spacing:0;">受访者 · [姓名或角色]</p>
    <p style="margin:7px 0 0;color:#202020;font-size:15px;line-height:1.85;letter-spacing:0;">[回答]</p>
  </section>
</section>
```

Use quotation marks only for verbatim speech. Do not rewrite a summary as a fabricated direct quote.

## Timeline milestone

Use repeated single-column rows. Each row owns its line, so editor rewriting cannot displace a separately positioned axis.

```html
<section style="margin:24px 8px 0;padding:0;">
  <section style="margin:0;padding:0 0 20px 16px;border-left:2px solid #202020;">
    <p style="margin:0;color:#6A6A66;font-size:12px;line-height:1.5;font-weight:700;letter-spacing:0;">[DATE OR VERSION]</p>
    <p style="margin:6px 0 0;color:#202020;font-size:18px;line-height:1.55;font-weight:700;letter-spacing:0;">[Milestone]</p>
    <p style="margin:7px 0 0;color:#50504C;font-size:14px;line-height:1.8;letter-spacing:0;">[Verified outcome, scope, or qualifier]</p>
  </section>
  <section style="margin:0;padding:0 0 0 16px;border-left:2px solid #CFCFCA;">
    <p style="margin:0;color:#6A6A66;font-size:12px;line-height:1.5;font-weight:700;letter-spacing:0;">[DATE OR VERSION]</p>
    <p style="margin:6px 0 0;color:#202020;font-size:18px;line-height:1.55;font-weight:700;letter-spacing:0;">[Milestone]</p>
    <p style="margin:7px 0 0;color:#50504C;font-size:14px;line-height:1.8;letter-spacing:0;">[Verified outcome, scope, or qualifier]</p>
  </section>
</section>
```

Dates, versions, and causal claims must come from the supplied evidence. Do not imply continuous progress merely because events are shown on a timeline.

## Progress bar

Keep the numeric value visible as text. Set the inner bar width to the same verified percentage and never use visual length as the only data carrier.

```html
<section style="margin:24px 8px 0;padding:0;">
  <p style="margin:0;color:#202020;font-size:15px;line-height:1.6;font-weight:700;letter-spacing:0;">[Metric] · 68%</p>
  <section style="height:8px;margin:9px 0 0;padding:0;background:#E5E5E1;overflow:hidden;">
    <section style="width:68%;height:8px;margin:0;padding:0;background:#3155F5;">
      <p style="margin:0;padding:0;font-size:1px;line-height:1px;letter-spacing:0;">&nbsp;</p>
    </section>
  </section>
  <p style="margin:7px 0 0;color:#6A6A66;font-size:12px;line-height:1.7;letter-spacing:0;">[Unit, sample, date, source, or interpretation boundary]</p>
</section>
```

## Minimal rating card

Use only when the scale and scoring method are meaningful. A rating without a denominator or source is decorative, not evidence.

```html
<section style="margin:24px 8px 0;padding:16px 0;border-top:1px solid #CFCFCA;border-bottom:1px solid #CFCFCA;">
  <p style="margin:0;color:#6A6A66;font-size:11px;line-height:1.5;font-weight:700;letter-spacing:0;">[RATING LABEL]</p>
  <p style="margin:6px 0 0;color:#202020;font-size:28px;line-height:1.35;font-weight:700;letter-spacing:0;">8.6 <span style="color:#76766F;font-size:14px;font-weight:400;">/ 10</span></p>
  <p style="margin:7px 0 0;color:#50504C;font-size:13px;line-height:1.75;letter-spacing:0;">[Scoring method, sample, source, and date]</p>
</section>
```

## Pre-publish checklist

### Copy boundary

- The publishable fragment contains no user request, workflow narration, design rationale, local path, validation result, placeholder instruction, or approval language.
- Every visible name, date, number, requirement, quote, contact, and claim is supplied or verified.
- Generated visuals are not presented as institutional or real-world evidence.

### Structure and typography

- The opener names the literal topic; the close resolves ownership or action.
- One module is dominant, density changes deliberately, and unrelated content is not forced into equal cards.
- Body copy is normally 15-16px with at least 1.85 leading.
- Chinese letter spacing is `0`; long labels, URLs, and identifiers wrap at 320px.
- Centered prose is short; captions and disclaimers remain readable.

### Markup and media

- Styling is inline and the fragment contains no script, event handler, external CSS/font, positioned layout, Grid, iframe, embed, or interaction-only information.
- All tags balance and no width exceeds the mobile column.
- Direct-delivery images use final HTTPS article URLs; manual delivery uses editable placeholders with asset mapping outside the boundary.
- Every image has a narrative or evidence role and an appropriate caption when identity, source, time, or scope matters.
- Manual swipe, if retained, has direct-child items, no oversized strip, no clipping ancestor, exact-fragment testing, and a vertical fallback.

### Validation

```powershell
python scripts/audit_audience_boundary.py article.html
python scripts/audit_wechat_widths.py article.html
python scripts/audit_wechat_typography.py article.html
python scripts/audit_wechat_contrast.py article.html
```

Resolve every finding. Then inspect approximately 320px, 375px, and 390px widths and use the real WeChat editor and phone preview for the final rendering decision.
