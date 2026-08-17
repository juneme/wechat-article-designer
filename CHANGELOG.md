# Changelog

## 1.1.1 - 2026-08-18

- Allow direct remote HTTP console access for deployments without a domain or SSH tunnel.
- Return a structured transport-security warning while keeping API keys out of command output.
- Create a validated WeChat draft automatically when the user chooses the full direct-publishing workflow, without a second confirmation.
- Keep preview-only and preparation-only requests non-mutating, and distinguish draft creation from final publication.

## 1.1.0 - 2026-08-18

- Add console API commands for body images, permanent cover material, validation, and draft creation.
- Require explicit user confirmation before creating a WeChat draft.
- Handle pending and ambiguous results without reporting false success or automatically retrying.
- Upload images one at a time to keep client memory use bounded.

## 1.0.2 - 2026-08-16

- Replace section/span-only photo anchors with a real-editor-verified direct-child 1px paragraph anchor.
- Keep `min-height`, padding, border, and background on the visual section so WeChat paragraph splitting cannot create full-height blank frames above and below inserted photos.
- Update rounded, institutional, event, collage, speaker, QR, recruitment, and anniversary slots, plus troubleshooting for both observed failure modes.

## 1.0.1 - 2026-08-16

- Replace removable text photo placeholders with persistent invisible `&nbsp;` anchors.
- Update rounded, institutional, event, collage, speaker, QR, recruitment, and anniversary image slots to accept direct paste without removing their wrappers.
- Add troubleshooting and publishing checks for accidental frame deletion and legacy padded placeholders.

## 1.0.0 - 2026-08-16

- Publish the 24-style visual DNA library.
- Include original-style synthesis, Steady and Creative delivery modes, and mobile publishing QA.
- Add Paper Cut Artbook, Contour Field Notes, Still-frame Cinema, Chromatic Folio, Botanical Press, Cut-Paper Atlas, Conservation Folio, Poetic Zine, and Material Board references.
- Remove motion and stateful interaction workflows while retaining the verified manual swipe pattern.
