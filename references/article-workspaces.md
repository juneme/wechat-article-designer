# Article Workspaces

Use one versioned workspace per article so assets, preview state, draft payloads, and revisions do not overwrite another article.

New articles and substantial redesigns must pass the complete writing-and-design workflow. A correction or minor revision reuses the existing contract, updates the affected fields, and reruns every audit affected by the changed body, metadata, contract, asset, or preview state.

## Create

Create the workspace before generating article assets:

```powershell
python scripts/article_workspace.py create --title '文章标题' --date 'YYYY-MM-DD'
```

Resolve backend readiness first. When all console variables are present and `status` is healthy, create the direct-draft workspace without a local preview unless the user explicitly requested one:

```powershell
python scripts/article_workspace.py create --title '文章标题' --date 'YYYY-MM-DD' --no-preview
```

The command creates the next available path under `articles/`:

```text
articles/YYYY-MM-DD_标题/
├── article.json
├── design-contract.json      # canonical machine-readable source
├── design-contract.md        # generated private reading view
├── fragment.html
├── preview.html              # local-preview route only
├── manifest.json
├── assets/
└── revisions/
```

The directory name is safe on Windows. A repeated title receives a numeric suffix instead of reusing or overwriting an existing article.

## Work in one source of truth

- Write publishable HTML in `fragment.html`, inside the two boundary comments. On the first `plan` of each full design cycle, the fragment must still equal the initialized or last `READY` implementation; this prevents styling first and retrofitting the contract afterward.
- Edit only `design-contract.json`. Complete every planning field and check, set `status` to `PLANNED`, and use a reasoned `N/A` for a conditional dimension that does not serve the article. Run `plan` before HTML implementation. The release command alone sets `READY` and generates `checks.fragment_sha256`; never fill that binding manually. `design-contract.md` is regenerated from JSON and must not be edited.
- Store local source images in `assets/`; final body image URLs still come from the console server.
- Edit title, author, digest, comment flags, and cover `media_id` in `article.json`.
- Treat `preview.html` as generated fallback output. It is created for the local-preview route and intentionally has no clipboard controls or scripts.
- Never store console credentials in any workspace file.

The boundary comments are extraction markers for local audits and workspace synchronization. They do not imply a clipboard workflow.

## Migrate an existing workspace

Schema-2 and schema-3 workspaces are preserved through one transactional command:

```powershell
python scripts/article_workspace.py migrate '.\articles\日期_标题'
```

The command upgrades the workspace to schema 4 and the design contract to schema 3, creates a revision snapshot, and never submits a draft. A schema-2 workspace without a prior design contract receives an `INCOMPLETE` substantial-redesign contract. A migrated schema-2 design contract records `legacy-contract-migration`; it may support a minor revision, but remove that exception and complete every new machine relationship on the next substantial redesign.

## Synchronize and version

After completing the writing and design plan, validate and version the `PLANNED` contract:

```powershell
python scripts/article_workspace.py plan '.\articles\日期_标题'
```

After changing the fragment or article metadata, use the enforced delivery entrypoint:

```powershell
python scripts/release_article.py deliver '.\articles\日期_标题'
```

The release command audits local content before any external mutation and then synchronizes:

1. refuses to continue when the canonical JSON contract, recorded plan hash, generated fragment hash, structural markers, publishable metadata, or required gate is incomplete;
2. extracts the publishable fragment into `article.json.content`;
3. regenerates `preview.html` only when the workspace uses the local-preview route;
4. computes the draft payload hash;
5. creates a new idempotent `request_id` only when draft payload data changed;
6. creates a revision when body, metadata, JSON contract, generated Markdown contract, assets, or preview state changed;
7. stores the complete prepared state under `revisions/rNNN_<timestamp>/` through one rollback-capable transaction.

The release command automatically enables fallback when the backend becomes unavailable before draft submission. The following command is a recovery diagnostic, not the normal delivery path:

```powershell
python scripts/article_workspace.py sync '.\articles\日期_标题' --preview
```

Do not use manual sync to bypass release audits. Never switch to local preview or resubmit after an ambiguous draft result.

Before draft submission, the release command writes a `submitting` lock to `manifest.json`. A timeout, interruption, pending result, unknown result, or unconfirmed response leaves the workspace locked. After the user checks the real draft box, resolve it explicitly:

```powershell
python scripts/article_workspace.py resolve-draft '.\articles\日期_标题' --outcome created
python scripts/article_workspace.py resolve-draft '.\articles\日期_标题' --outcome not-created
```

Use exactly one outcome. `not-created` authorizes a later retry; `created` preserves the confirmed result and prevents an unchanged payload from being submitted again.

Running sync again without any tracked change preserves both revision and `request_id`. A contract, asset, or preview-only change creates a revision but preserves `request_id`; a draft payload change creates both a revision and a new ID. Reuse remains subject to the direct-publishing failure rules.

## Validate and deliver

`release_article.py deliver` runs the following audits, including structural contract matching, before validating the synchronized payload:

```powershell
python scripts/audit_wechat_markup.py '.\articles\...\fragment.html' --contract '.\articles\...\design-contract.json'
python scripts/audit_audience_boundary.py '.\articles\...\article.json' --contract '.\articles\...\design-contract.json'
python scripts/audit_wechat_widths.py '.\articles\...\fragment.html' --contract '.\articles\...\design-contract.json'
python scripts/audit_wechat_typography.py '.\articles\...\fragment.html' --contract '.\articles\...\design-contract.json'
python scripts/audit_wechat_contrast.py '.\articles\...\fragment.html' --contract '.\articles\...\design-contract.json'
python scripts/audit_design_contract.py '.\articles\...\fragment.html' --contract '.\articles\...\design-contract.json'
python scripts/wechat_console_api.py validate-draft --article '.\articles\...\article.json'
```

Run `validate-draft` only for a direct route with final hosted body images and cover media. On the preview route, all six local audits and mobile inspection are the delivery gate.

SVG components follow `references/svg-design-genes.md` and use the same workspace, synchronization, and draft-validation path as the rest of the article. Draft creation remains governed by `references/direct-publishing.md`.
