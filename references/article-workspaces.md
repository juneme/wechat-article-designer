# Article Workspaces

Use one versioned workspace per article so assets, preview state, draft payloads, and revisions do not overwrite another article.

## Create

Create the workspace before generating article assets:

```powershell
python scripts/article_workspace.py create --title '文章标题' --date 'YYYY-MM-DD'
```

The command creates the next available path under `articles/`:

```text
articles/YYYY-MM-DD_标题/
├── article.json
├── fragment.html
├── preview.html
├── manifest.json
├── assets/
└── revisions/
```

The directory name is safe on Windows. A repeated title receives a numeric suffix instead of reusing or overwriting an existing article.

## Work in one source of truth

- Write publishable HTML in `fragment.html`, inside the two boundary comments.
- Store local source images in `assets/`; final body image URLs still come from the console server.
- Edit title, author, digest, comment flags, and cover `media_id` in `article.json`.
- Treat `preview.html` as generated output. It intentionally has no clipboard controls or scripts.
- Never store console credentials in any workspace file.

The boundary comments are extraction markers for local audits and workspace synchronization. They do not imply a clipboard workflow.

## Synchronize and version

After changing the fragment or article metadata, run:

```powershell
python scripts/article_workspace.py sync '.\articles\日期_标题'
```

Synchronization:

1. extracts the publishable fragment into `article.json.content`;
2. regenerates `preview.html` without altering the fragment;
3. computes the draft payload hash;
4. creates a new idempotent `request_id` only when draft data changed;
5. stores the prepared state under `revisions/rNNN_<timestamp>/`.

Running sync again without a payload change preserves the existing `request_id` and does not create a duplicate revision. This permits a safe retry of the same draft request.

## Validate and deliver

Run the standard audits against `fragment.html`, then validate the synchronized payload:

```powershell
python scripts/audit_audience_boundary.py '.\articles\...\fragment.html'
python scripts/audit_wechat_widths.py '.\articles\...\fragment.html'
python scripts/audit_wechat_typography.py '.\articles\...\fragment.html'
python scripts/audit_wechat_contrast.py '.\articles\...\fragment.html'
python scripts/wechat_console_api.py validate-draft --article '.\articles\...\article.json'
```

SVG components follow `references/svg-design-genes.md` and use the same workspace, synchronization, and draft-validation path as the rest of the article. Draft creation remains governed by `references/direct-publishing.md`.
