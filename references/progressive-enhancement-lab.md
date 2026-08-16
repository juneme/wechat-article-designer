# Progressive Enhancement Lab for WeChat Articles

Use this reference when exploring Web techniques for a WeChat Official Account article without confusing browser capability with publishable article capability.

## Two-lane architecture

Keep two artifacts with different contracts:

1. **Delivery fragment**: the exact copy-boundary HTML intended for the WeChat editor. It contains only article-safe flow markup and inline styles.
2. **Experiment host**: a local browser page for width switching, comparison, copying, audit output, and fallback simulation. It may use JavaScript and a style block because none of that host markup is copied into the article.

Never use a successful experiment-host render as evidence that its scripts, style blocks, preview wrappers, or browser controls can enter the article body.

## Capability layers

| Layer | Typical capabilities | Delivery rule |
|---|---|---|
| Core | `section / p / span`, inline style, solid fills, borders, spacing, type hierarchy | May enter the final fragment after deterministic audit. |
| Conditional enhancement | Compact `display:flex`, `display:inline-block`, intentional `overflow-x:auto` strip | Keep content short, define a single-column fallback, and verify the exact final block in the real editor. |

## Degradation contract

Every conditional enhancement needs an explicit degradation contract before it is used:

- Removing `flex` must preserve item order and turn the row into a readable stack.
- Removing horizontal overflow and oversized strip widths must turn the gallery into a readable single column.
- Removing color, gradients, or shadows must not erase hierarchy or labels.
- Removing text stroke, balanced wrapping, gradient borders, or patterned backgrounds must leave a readable solid-color and ordinary-border composition.
- A failure may make the article plainer; it must not hide content, change narrative order, or clip text.

Build and inspect the fallback version alongside the enhanced version. Do not wait for an editor failure to discover whether a fallback exists.

## Evidence ladder

Record the strongest evidence actually obtained:

1. **Static audit**: forbidden markup, local paths, tag balance, and capability counts.
2. **Browser width test**: approximately 320px, 375px, and 390px; inspect outer overflow, text wrapping, and fallback order.
3. **Real-editor paste test**: paste the exact final fragment into the WeChat draft box.
4. **Phone preview**: verify the exact final copy and real images on the target widths/devices.
5. **Published regression**: record editor version, device, screenshots, and any rewrite observed.

Browser checks prove only browser behavior. A successful browser run must remain labeled `real-editor pending` until steps 3 and 4 pass.

An operator report that an entire fragment is "usable" is valid scoped evidence for that exact fragment. If the editor version, device, declaration preservation, or published result is missing, record those fields as unknown and do not promote every property in the fragment to universal support.

## Manual swipe experiment

For `N` cards where each card should occupy `V%` of the visible column:

- oversized strip width = `N * V%`;
- child width inside the strip = `100 / N%`.

Example: four cards at `V = 86` use a `344%` strip and `25%` children. This leaves a 14% next-card cue. Add a static HTML swipe affordance because mobile WebViews may hide the native scrollbar. The affordance is not live progress.

The fallback removes `overflow-x:auto`, resets the strip to `100%`, and makes every child `display:block;width:100%` in source order.

## Recommended lab outputs

- exact delivery fragment with copy boundaries;
- generated browser preview derived from that single source;
- deterministic audit script;
- enhanced and fallback screenshots at 320px, 375px, and 390px;
- compatibility matrix separating completed checks from real-editor pending work.

Do not duplicate the article source manually inside the preview host. Generate or inject it from one canonical file so the preview cannot silently drift from the delivered fragment.
