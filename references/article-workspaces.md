# Article Workspaces

Use one workspace per article so copy, media, metadata, route state, and revisions remain isolated. `work/`, caches, experiments, and unrelated test data are never article or release content.

## Create

Use `--no-preview` only when the three console variables exist and the health check succeeds. Otherwise create the local-preview route.

```powershell
python scripts/article_workspace.py create --title "文章标题" --date YYYY-MM-DD --no-preview
python scripts/article_workspace.py create --title "文章标题" --date YYYY-MM-DD
```

The generated layout is:

```text
articles/YYYY-MM-DD_title/
├── article.json
├── fragment.html
├── release-manifest.json
├── manifest.json
├── preview.html              # local-preview route only
├── assets/
└── revisions/
```

`fragment.html` is the editable publishable source. `article.json` holds WeChat draft metadata. `release-manifest.json` contains only media and delivery operations. It does not describe or constrain typography, palette, geometry, modules, spacing, effects, or visual intent.

## Compose

Write and design directly in `fragment.html` between the two boundary comments. No planning command or design state is required before editing or release. Use `data-media-id` only when a local body image must be uploaded and replaced. Use `data-indent-role="body-paragraph"` only on ordinary prose paragraphs that declare `text-indent:2em`.

If a private design note helps the current task, keep it outside publishable copy. The optional command below generates a descriptive report after composition:

```powershell
python scripts/article_workspace.py inspect '.\articles\日期_标题'
```

The report is versioned but never validated as a design target. The legacy `plan` command is an alias for `inspect` and no longer freezes state.

## Synchronize

The release orchestrator synchronizes automatically. Manual synchronization is available for diagnostics:

```powershell
python scripts/article_workspace.py sync '.\articles\日期_标题'
```

Synchronization:

1. extracts the exact boundary fragment into `article.json.content`;
2. validates operational media fields;
3. creates or removes `preview.html` according to the selected route;
4. increments the article revision when body, metadata, operational media, assets, preview state, optional report, or preserved legacy design files change;
5. rotates `request_id` only when the draft payload changes;
6. writes one complete revision snapshot;
7. restores all root files if writing or snapshot creation fails.

Runtime submission locks are persisted immediately and are not a substitute for a content revision.

## Operational media

Each `release-manifest.json` item contains:

```json
{
  "name": "lead-image",
  "placement": "body",
  "required": true,
  "state": "supplied-local",
  "source_path": "lead.jpg",
  "remote_ref": ""
}
```

Names are unique machine identifiers. `source_path` is relative to `assets/`. A body item maps to exactly one `<img data-media-id="lead-image">`. A cover has `placement:"cover"` and no body marker.

## Legacy migration

Upgrade a v2/v3 workspace before release:

```powershell
python scripts/article_workspace.py migrate '.\articles\日期_标题'
```

Migration creates `release-manifest.json` from the legacy contract's media array, upgrades the workspace manifest, and snapshots the result. Existing `design-contract.json` and `design-contract.md` stay untouched as private history. They no longer need a particular status and cannot block release.

## Draft lock

Before sending a draft, release stores `submitting`. A timeout, `502`, pending, unknown response, interruption, or unconfirmed response becomes `ambiguous`. Both states block synchronization, retry, and preview fallback because a duplicate draft may already exist.

After the user inspects the real draft box:

```powershell
python scripts/article_workspace.py resolve-draft WORKSPACE --outcome created
python scripts/article_workspace.py resolve-draft WORKSPACE --outcome not-created
```

Do not edit `manifest.json` by hand to clear the lock.

## Independent postflight checks

```powershell
python scripts/audit_wechat_markup.py fragment.html
python scripts/audit_audience_boundary.py article.json
python scripts/audit_wechat_widths.py fragment.html
python scripts/audit_wechat_typography.py fragment.html
python scripts/audit_wechat_contrast.py fragment.html
```

Warnings document editor uncertainty or a recommendation. Errors identify an unsafe, unreadable, overflowing, private, or operationally invalid result. Only errors block release.
