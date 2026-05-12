# Troubleshooting

## `npm run generate:cv` says CV file not found

Check whether the repo expects:

- `cv.docx` at the repository root, or
- `public/cv.docx`

For workshop use, standardize on `public/cv.docx` and set `generate:cv` accordingly:

```json
"generate:cv": "python3 scripts/cv/parse_docx.py --input public/cv.docx --output src/generated/cv-data.json"
```

## Build succeeds but homepage does not update

Likely causes:

1. The homepage is still reading manually written `publications.ts` data instead of generated CV data.
2. `cvGenerated.ts` is not imported into the relevant page/content file.
3. The CV heading structure changed and the parser did not recognize the section.

Ask the coding agent to trace the data path:

```text
Trace how public/cv.docx data reaches the homepage. Identify whether homepage publications come from src/generated/cv-data.json or from hardcoded content files.
```

## Publications are parsed incorrectly

The parser usually depends on stable CV headings and publication formatting. Keep headings consistent, for example:

- PUBLICATIONS
- WORK IN PROGRESS
- TEACHING
- EMPLOYMENT

If formatting changed, ask the coding agent to update the parser and add a small test fixture.

## GitHub Actions build fails

Check:

1. `npm ci` succeeds.
2. `npm run build` runs locally.
3. Python is available in the workflow.
4. The workflow points to the correct output directory, usually `./out`.
5. `next.config.js` is configured for static export if using Pages artifact deployment.

## CV page shows old PDF

Check:

1. The new PDF replaced the old file path exactly.
2. The browser is not caching the old PDF.
3. `src/content/site.ts` points to the same PDF filename.
4. GitHub Pages deployment completed after the PDF was pushed.

## Agent adds watcher or auto-commit behavior

Reject the change. The workshop pattern should use explicit build/deploy. Ask the agent:

```text
Remove all watcher, cron, LaunchAgent, background auto-commit, and always-on automation behavior. Keep only explicit npm scripts and GitHub Actions deployment on push/workflow_dispatch.
```
