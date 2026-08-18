# Soft App Recruitment Article Pattern

Use this pattern when a WeChat recruitment article should feel light, contemporary, and approachable rather than corporate, ceremonial, or poster-like. The pattern supports job lists, salary ranges, benefits, team photos, and an application CTA.

Start from `assets/soft-app-recruitment-article.html`. Replace every `{{PLACEHOLDER}}`, duplicate the job card as needed, and keep all styles inline. Treat the asset as a candidate source rather than a drop-in guarantee: compact flex rows require a fresh WeChat editor regression with the final copy.

## Visual contract

Build a pale mobile canvas with restrained App-like surfaces:

| Token | Default | Role |
|---|---|---|
| Canvas | `#F5F6FC` | Cool near-white page background |
| Surface | `#FFFFFF` | Job cards and content surfaces |
| Ink | `#172153` | Headlines and primary copy; softer than black |
| Muted | `#70789A` | Labels, captions, supporting copy |
| Primary | `#7C73E8` | Main action and section emphasis |
| Lavender | `#EEEAFE` | Hero and pharmacist/office job accent |
| Mint | `#DDF6EC` | Positive chips, benefits, retail/service accent |
| Sky | `#E7F1FF` | Marketing/operations accent |
| Rose | `#F9E9F0` | Care/wellness accent |
| Border | `#DDE1EF` | Quiet 1px dividers and card outlines |

Keep the canvas light. Do not use pure black as the page background. Use one primary color plus two or three pale companion tints; do not turn every surface into a variation of one hue. The Steady variant uses solid fills; the Creative variant may add a subtle gradient or shadow while preserving the light App-like character and a solid fallback.

Use rounded corners with hierarchy:

- Hero or application band: `20-24px`.
- Job card: `16-20px`.
- Photo placeholder: `14-18px`.
- Salary and category pills: fully rounded (`999px`).

Large radii soften the composition, but spacing and type hierarchy must still do most of the work. Do not nest decorative cards inside other cards.

## Article structure

Use this sequence:

1. Split hero: brand/recruitment message on the left, open-position count on the right.
2. One full-width team or workplace photo placeholder.
3. Section heading plus compact category chips.
4. One single-column card per role.
5. Full-width application band with a narrow QR-code placeholder.

Keep repeated roles single-column. A WeChat body is narrow, and salary, title, and sequence number must remain readable without horizontal scrolling.

## Conditional compact flex structure

For compact role headers, the candidate template uses `section` elements with inline flex styles. Do not use `table`, `thead`, `tbody`, `tr`, `th`, or `td` anywhere in this pattern. WeChat may apply editor-defined cell borders, row sizing, and column widths after paste, producing visible spreadsheet grids absent from a browser preview.

Compact flex is a proven capability, but the exact final copy still needs mobile regression because long titles and fixed pills can squeeze each other. If the editor rewrites the row, stack the number, title, and salary as single-column `section + p + span` flow blocks; for dense repeated visuals, export one bitmap instead.

Use this role header structure:

```html
<section style="display:flex;align-items:center;box-sizing:border-box;width:100%;">
  <span style="display:block;flex:0 0 46px;width:46px;height:46px;line-height:46px;border-radius:14px;text-align:center;background:#7C73E8;color:#FFFFFF;font-weight:800;">01</span>
  <section style="display:block;flex:1 1 auto;min-width:0;margin-left:12px;">
    <p style="margin:0;color:#70789A;font-size:10px;line-height:1.4;font-weight:700;">{{ROLE_EN}}</p>
    <p style="margin:2px 0 0;color:#172153;font-size:19px;line-height:1.35;font-weight:800;">{{ROLE_NAME}}</p>
  </section>
  <section style="display:block;flex:0 0 88px;width:88px;margin-left:10px;padding:8px 8px;box-sizing:border-box;border-radius:999px;background:#EEEAFE;text-align:center;white-space:nowrap;word-break:keep-all;">
    <span style="font-size:14px;line-height:1;color:#5349C8;font-weight:800;white-space:nowrap;word-break:keep-all;">{{SALARY}}</span>
  </section>
</section>
```

Compatibility details:

- Put `min-width:0` on the flexible title column so long job names wrap instead of pushing the salary out.
- Give salary pills an explicit matching `width` and `flex-basis` (`88px` is the verified default), then add both `white-space:nowrap` and `word-break:keep-all` to the pill and text. Never insert a manual line break into a salary such as `2.5K-5K`.
- Use margins between flex children; do not depend on `gap`, which may be stripped or inconsistently preserved.
- Avoid `position`, fixed heights for text areas, and multi-column job grids.
- Keep body text at `14-16px`, line height at `1.75-1.95`, and metadata at `10-12px`.

## Photo placeholders

Use an HTML placeholder when the editor will receive a real team, store, or workplace photo later:

```html
<section style="margin:16px 8px 0;padding:10px;box-sizing:border-box;border:1px solid #DDE1EF;border-radius:20px;background:#FFFFFF;">
  <section style="min-height:96px;margin:0;padding:0;box-sizing:border-box;border-radius:14px;background:#E7F1FF;text-align:center;overflow:hidden;">
    <p style="margin:0;padding:0;font-size:1px;line-height:1px;color:transparent;">&nbsp;</p>
  </section>
</section>
```

In delivery instructions, require a full-article paste followed by direct photo insertion through the blank inner area without selecting or deleting the 1px paragraph anchor. Keep frame height and visual styles on the containing section. Keep placement instructions outside the final image slot. Do not embed a local file path. Keep a QR-code placeholder narrow and centered to prevent full-width expansion.

## Cover generation

Generate a matching deterministic cover with `scripts/generate_wechat_cover.py`. The default canvas is `1175x500`, exactly `2.35:1`.

The generator requires Python 3.10+ and Pillow. Install the only non-standard dependency when needed:

```powershell
python -m pip install Pillow
```

```powershell
python scripts/generate_wechat_cover.py `
  --out recruitment-cover.png `
  --brand "{{BRAND_NAME}}" `
  --eyebrow "RECRUITMENT" `
  --headline "期待新的同行者" `
  --tagline "多元岗位开放 · 招聘通道开启" `
  --position-count "05" `
  --footer "{{CAMPAIGN_LABEL}}"
```

The script draws the supplied strings directly with a CJK font without translation, summarization, or invented copy. Pass `--font-regular` and `--font-bold` when automatic font discovery is unavailable. Keep the title short enough for two lines; the script reduces font size before failing and never truncates text.

## Validation

Run a browser/mobile check, then test a fresh paste in the WeChat editor. A local browser is not sufficient.

```powershell
$html = Get-Content -Raw -Encoding UTF8 -LiteralPath 'article.html'
[ordered]@{
  HasTableTag = ($html -match '<\/?(?:table|thead|tbody|tr|th|td)\b')
  HasStyleBlock = ($html -match '<style')
  HasScript = ($html -match '<script')
  HasGradient = ($html -match 'gradient\(')
  HasShadow = ($html -match 'box-shadow')
  HasPositioning = ($html -match 'position\s*:')
  HasLocalImage = ($html -match '<img[^>]+src=["''](?:file:|[A-Za-z]:\\)')
  SectionOpen = ([regex]::Matches($html, '<section\b')).Count
  SectionClose = ([regex]::Matches($html, '</section>')).Count
}
```

The pattern passes only when:

- `HasTableTag`, `HasStyleBlock`, `HasScript`, `HasPositioning`, and `HasLocalImage` are all `False`.
- In Steady mode, `HasGradient` and `HasShadow` are `False`. In Creative mode, gradients have solid fallbacks and shadows are nonessential after phone-preview verification.
- Opening and closing `section` counts match.
- A `375px` viewport has no horizontal overflow.
- Every salary stays on one line, including decimal ranges; all repeated salary pills keep the same measured width.
- Long job names wrap without overlapping the salary pill.
- The WeChat editor shows no injected grid borders after a fresh paste.
- Photo and QR placeholders retain the intended width after paste.
