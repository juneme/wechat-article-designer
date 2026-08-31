---
name: yunoe
description: Create original, adaptive WeChat Official Account articles within verified publishing boundaries and stage them as drafts by default through Yunoe Console; also manage existing images and drafts.
---

# 云浪公众号排版

Produce a finished, reader-facing WeChat article and its publishable HTML fragment. Own the writing and visual direction unless the user specifies either. Never invent facts, evidence, people, credentials, dates, results, or institutional claims.

This skill has two capabilities:

1. Autonomous article design within verified WeChat publishing boundaries.
2. Image and draft operations through Yunoe Console (云浪控制台).

At the start of every article task, read [references/wechat-boundary.md](references/wechat-boundary.md) and [references/typography.md](references/typography.md), then check Yunoe Console status while beginning the creative work. The typography reference defines readability boundaries, not a reusable visual system. A missing pairing must not delay writing: prepare the article and local comparison file, open the local pairing client, and continue to the real draft immediately after the user completes local verification.

Build a coordinated multimedia composition from semantic HTML, inline CSS, SVG/SMIL motion, raster imagery, and other compatible media. Let the copy, audience, and distribution context determine which layers carry a useful role. Each included layer must improve visual quality, comprehension, reading comfort, emotional resonance, or shareability; including every possible medium is not itself a goal. Motion and advanced effects must degrade to a coherent static reading experience.

Do not use or reconstruct a layout template, preset composition, predefined theme, house style, component recipe, design token set, example article, or default typography and spacing system. Do not impose a fixed creative workflow. Infer the visual strategy from the specific content, audience, and context. Use the strongest current techniques and contemporary aesthetic judgment that survive the verified platform boundary; create the hierarchy, composition, pacing, type treatment, color, media, and responsive behavior independently. Treat Yunoe Console UI, nearby local HTML, previous articles, and compatibility examples as operational context rather than visual references unless the user requests continuity. Repetition is acceptable when the content independently supports it; do not force novelty or add a design rationale.

The result must remain coherent without this conversation. Keep prompts, source instructions, design reasoning, local paths, credentials, approval language, and tool output outside the article. Always save a local HTML comparison file containing the exact submitted body. Validate it at representative narrow mobile widths, then compare the actual sanitized WeChat draft against it; the real mobile draft is the final rendering authority.

Creating an article with this skill includes staging it in the real WeChat draft box through Yunoe Console by default. Read [references/backend.md](references/backend.md), create or render the required cover, upload required media, and use `scripts/wechat_console.py` to create the draft. If pairing is missing, launch `pair-ui` so the user enters the one-minute code locally; never request or accept the code in chat or place it on a command line. Stop at local output only when the user explicitly asks for it or required account data cannot be determined.

Draft creation is staging, not publication. Never publish or mass-send automatically, expose credentials, or retry a remotely ambiguous write. Use the same backend reference and client to inspect, update, or delete existing images and drafts.
