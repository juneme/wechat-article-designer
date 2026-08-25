# Inline Primitives

These are low-level implementation reminders, not templates or required components. Change their palette, geometry, scale, spacing, and composition to fit the article. Use only what the content needs.

## Publishable boundary

```html
<!-- 微信公众号复制开始 -->
<section style="margin:0;padding:0;background:#FFFFFF;color:#202020;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif;">
  [final audience-facing article]
</section>
<!-- 微信公众号复制结束 -->
```

Keep all instructions, filenames, paths, prompts, and validation notes outside these comments.

## Continuous body prose

```html
<p data-indent-role="body-paragraph" style="margin:0 18px 14px;padding:0;color:#262626;font-size:16px;line-height:1.9;text-align:left;text-indent:2em;">
  [continuous prose]
</p>
```

This is the only primitive that uses first-line indentation. Do not copy its marker or `text-indent` to a title, deck, label, list, quotation, dialogue, caption, card, action, closing, or container.

## Local body image awaiting upload

```html
<img data-media-id="lead-image" src="wechat-media://lead-image" alt="[concise image description]" style="display:block;width:100%;height:auto;margin:0;border:0;" />
```

Register the matching item in `release-manifest.json`. The release command uploads the source under `assets/` and replaces the temporary scheme with the returned HTTPS article URL. The marker is operational and does not imply a visual role.

## Hosted image and caption

```html
<img src="https://mmbiz.qpic.cn/FINAL_ARTICLE_IMAGE" alt="[concise image description]" style="display:block;width:100%;height:auto;margin:0;border:0;" />
<p style="margin:8px 8px 0;color:#666;font-size:12px;line-height:1.65;text-align:left;text-indent:0;">
  [caption, source, or qualifier]
</p>
```

Use a caption only when it adds information. A caption does not need a data marker unless a separate tool outside this Skill requires one.

## Editorial quotation

```html
<blockquote data-content-kind="quotation" style="margin:24px 18px;padding:2px 0 2px 16px;border-left:3px solid #B7472A;color:#343434;">
  <p style="margin:0;font-size:17px;line-height:1.75;font-weight:600;text-indent:0;">[quotation]</p>
  <p style="margin:8px 0 0;font-size:12px;line-height:1.6;color:#747474;text-indent:0;">[source]</p>
</blockquote>
```

`data-content-kind` exempts genuine quoted or interview speech from the workflow-language detector. It does not exempt invented claims.

## Interview exchange

```html
<section data-content-kind="dialogue" style="margin:24px 16px;padding:18px;background:#F4F4F2;border-left:3px solid #3155F5;">
  <p style="margin:0;color:#3155F5;font-size:12px;line-height:1.5;font-weight:700;text-indent:0;">采访者 · [role]</p>
  <p style="margin:7px 0 0;color:#202020;font-size:15px;line-height:1.8;text-indent:0;">[question]</p>
  <p style="margin:16px 0 0;color:#477A57;font-size:12px;line-height:1.5;font-weight:700;text-indent:0;">受访者 · [role]</p>
  <p style="margin:7px 0 0;color:#202020;font-size:15px;line-height:1.8;text-indent:0;">[answer]</p>
</section>
```

## Evidence pair

```html
<section style="display:flex;gap:10px;margin:24px 14px;padding:0;">
  <section style="flex:1;margin:0;padding:14px;background:#F5F5F3;border-top:3px solid #3155F5;">
    <p style="margin:0;color:#686868;font-size:11px;line-height:1.5;font-weight:700;text-indent:0;">[LABEL]</p>
    <p style="margin:5px 0 0;color:#202020;font-size:19px;line-height:1.45;font-weight:700;text-indent:0;">[verified fact]</p>
    <p style="margin:6px 0 0;color:#555;font-size:13px;line-height:1.65;text-indent:0;">[unit, date, source, or limit]</p>
  </section>
  <section style="flex:1;margin:0;padding:14px;background:#F5F5F3;border-top:3px solid #D84A34;">
    [second comparable fact]
  </section>
</section>
```

Flex requires editor inspection. Change the structure entirely when another comparison language better serves the content.

## Action close

```html
<section style="margin:30px 14px 0;padding:22px 18px;background:#242424;color:#FFFFFF;">
  <p style="margin:0;color:#D7D7D2;font-size:11px;line-height:1.5;font-weight:700;text-indent:0;">[ACTION LABEL]</p>
  <p style="margin:8px 0 0;font-size:22px;line-height:1.4;font-weight:700;text-indent:0;">[reader action]</p>
  <p style="margin:12px 0 0;color:#F1F1EE;font-size:15px;line-height:1.8;text-indent:0;">[method, deadline, eligibility, or contact]</p>
</section>
```

An action close is not mandatory. Reflective, literary, archival, or image-led articles may close through resolution, return, or a final scene instead.

## Final checklist

- All names, dates, numbers, requirements, quotes, contacts, and claims are supplied or verified.
- Publishable text contains no agent offer, approval request, local path, experiment note, or conversation history.
- The boundary comments occur once and contain all publishable content.
- Only continuous body paragraphs carry `data-indent-role="body-paragraph"` and `text-indent:2em`.
- Fixed rendered widths remain at or below 320px; percentages remain at or below 100%.
- Direct-draft body images use final WeChat HTTPS URLs; local placeholders appear only before upload or in local preview.
- Each essential action, qualifier, and warning is readable without interaction or motion.
- The actual draft has been inspected when expressive CSS, complex SVG, gradients, masks, filters, tables, or swipe behavior matter.

```powershell
python scripts/audit_wechat_markup.py article.html
python scripts/audit_audience_boundary.py article.html
python scripts/audit_wechat_widths.py article.html
python scripts/audit_wechat_typography.py article.html
python scripts/audit_wechat_contrast.py article.html
```
