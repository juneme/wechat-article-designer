# Progressive Enhancement Lab for WeChat Articles

Use this reference when exploring Web techniques for a WeChat Official Account article without confusing browser capability with publishable article capability.

## Two-lane architecture

Keep two artifacts with different contracts:

1. **Delivery fragment**: the exact copy-boundary HTML intended for the WeChat editor, containing only article-safe flow markup and inline styles.
2. **Experiment host**: a local browser page for width switching, comparison, copying, audit output, and fallback simulation. JavaScript and a style block are acceptable because host markup never enters the article.

Never use a successful experiment-host render as evidence that host scripts, style blocks, preview wrappers, or browser controls can enter the article body.

## Capability layers

| Layer | Typical capabilities | Delivery rule |
|---|---|---|
| Core | `section / p / span`, inline style, solid fills, borders, spacing, type hierarchy | May enter the final fragment after deterministic audit. |
| Conditional enhancement | Compact `display:flex`, `display:inline-block`, intentional `overflow-x:auto` strip | Keep content short, use direct children without oversized widths, prepare a separate single-column version, and verify the exact final block in the real editor. |

## Degradation contract

Every conditional enhancement needs an explicit degradation contract before use:

- Removing `flex` must preserve item order and turn the row into a readable stack.
- Manual swipe has no reliable CSS-only fallback after selective editor sanitization. Keep a separate single-column artifact and use it whenever the exact swipe block fails the real-editor test.
- Removing color, gradients, or shadows must not erase hierarchy or labels.
- Removing text stroke, balanced wrapping, gradient borders, or patterned backgrounds must leave a readable solid-color and ordinary-border composition.
- A failure may make the article plainer but must not hide content, change narrative order, or clip text.

Build and inspect the fallback version alongside the enhanced version. Do not wait for an editor failure to discover whether a fallback exists.

## Evidence ladder

Record the strongest evidence actually obtained:

1. **Static audit**: forbidden markup, local paths, tag balance, and capability counts.
2. **Browser width test**: approximately 320px, 375px, and 390px; inspect outer overflow, text wrapping, and fallback order.
3. **Real-editor paste test**: paste the exact final fragment into the WeChat draft box.
4. **Phone preview**: verify the exact final copy and real images on the target widths/devices.
5. **Published regression**: record editor version, device, screenshots, and any rewrite observed.

Browser checks prove only browser behavior. A successful browser run must remain labeled `real-editor pending` until steps 3 and 4 pass.

A complete-fragment usability result is valid scoped evidence for that exact fragment. If the editor version, device, declaration preservation, or published result is missing, record those fields as unknown and do not promote every property in the fragment to universal support.

## Manual swipe experiment

Put every card directly inside the scroll container and give each card the desired visible width `V%`, normally `84-90%`. The container uses `white-space:nowrap;font-size:0`; each direct child restores ordinary text flow with `display:inline-block;vertical-align:top;white-space:normal`.

Do not add an intermediate strip with `width:N * V%`, do not use any percentage width above `100%`, and do not put `overflow:hidden` on an ancestor of the scroll container. WeChat can rewrite one declaration without rewriting the dependent declarations: clamping a `900%` strip to `100%` while retaining `10%` children reduces each card to one tenth of the visible column, and a clipping ancestor then hides the overflow.

Add a static HTML swipe affordance because mobile WebViews may hide the native scrollbar. The affordance is not live progress. If the exact final block fails in the editor, replace it with the separately maintained single-column version; do not claim that sanitization will automatically create the fallback.

## Recommended lab outputs

- exact delivery fragment with copy boundaries;
- generated browser preview derived from that single source;
- deterministic audit script;
- enhanced and fallback screenshots at 320px, 375px, and 390px;
- compatibility matrix separating completed checks from real-editor pending work.

Do not duplicate the article source manually inside the preview host. Generate or inject content from one canonical file so the preview cannot silently drift from the delivered fragment.
