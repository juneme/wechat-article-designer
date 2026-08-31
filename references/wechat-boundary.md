# Verified WeChat Publishing Boundaries

These are compatibility constraints, not a style guide. Everything not constrained here remains an independent design decision.

## Content fragment

- Supply the article body as an HTML fragment accepted by the WeChat editor or draft API, not as a complete HTML document.
- Put required styling on elements with inline `style` attributes. Do not depend on `<style>` blocks, external stylesheets, external fonts, scripts, event handlers, forms, iframes, or other active embeds.
- WeChat may remove or reinterpret HTML elements and CSS properties. Essential meaning, reading order, and controls must survive sanitization; animation and interaction cannot carry essential information.

## Combined media

- HTML structure, inline CSS, inline SVG/SMIL, WeChat-hosted raster images, animated images, and other accepted media may work together in one article. They are complementary layers, not competing output modes.
- Keep semantic layout and text in HTML/CSS, but do not make essential first-viewport artwork depend on empty positioned elements whose only content is a CSS shape. A 2026-08-30 real-draft preview retained the background and text while losing such CSS-only decorative elements. Render a critical CSS-designed scene to a raster asset, upload it in `article` mode, and use that HTTPS image in the body while the remaining HTML/CSS, SVG/SMIL, and media continue to serve their own roles.
- SVG and SMIL support depends on the exact elements and attributes retained by WeChat. Keep all essential text and reading order outside the animated layer, provide a meaningful static first frame or equivalent fallback, and verify the sanitized draft on target mobile clients.
- Do not describe an SVG/SMIL technique as verified until that exact technique survives Yunoe Console draft creation and the target WeChat client. If sanitization removes it, replace only the incompatible technique rather than discarding the combined-media design.
- Draft API verification on 2026-08-30 retained inline `svg`, `rect`, `circle`, `path`, and `ellipse`, plus SMIL `animate` targeting `opacity` with `values`, `dur`, and `repeatCount`. The same sanitizer removed `animate` targeting geometry attributes `rx` and `cy`, and removed the image `referrerpolicy` attribute. This proves draft-API retention only; mobile-client rendering still requires preview.

## Responsive rendering

- The fragment must fit the article content viewport without horizontal scrolling, clipped content, or accidental overlap at narrow mobile widths.
- Media and visual constructions must not render wider than their containing article column.
- Text must remain legible and distinguishable from its background after WeChat processing. Decorative layers must not obscure content.
- The actual sanitized WeChat draft on mobile is the rendering authority. Browser previews and source HTML alone are insufficient. If the draft strips or changes a technique, redesign that part within supported behavior.
- Keep the exact submitted body as a local HTML comparison file so sanitization differences can be identified rather than guessed.

## Media

- Body raster images submitted directly through the draft API must use WeChat-hosted article image URLs returned by Yunoe Console's `article` upload mode. WeChat may return either `http://mmecoa.qpic.cn` or `http://mmbiz.qpic.cn`; the Yunoe client and server normalize both to the canonical `https://mmbiz.qpic.cn` host while preserving the returned path and query string.
- A cover must be uploaded as permanent WeChat material, and its returned `media_id` must be supplied as `thumb_media_id`.
- Do not rely on a local path, data URL, temporary object URL, or inaccessible external URL in the submitted article.
