# Agent Spec: CV-Driven Academic Website

Paste this into Codex or Claude Code after opening the repository.

## Task

Set up or repair a CV-driven academic website workflow in this repository.

The website should use a Word CV as the canonical source for structured academic data and a PDF CV as the downloadable/embeddable public CV.

## Required architecture

```text
public/cv.docx
  → scripts/cv/parse_docx.py
  → src/generated/cv-data.json
  → src/content/cvGenerated.ts
  → homepage / bio / publications / work-in-progress rendering

public/cv.pdf
  → src/content/site.ts as cvUrl
  → src/pages/cv.tsx
```

If the repository currently uses `cv.docx` at the root, preserve backwards compatibility if useful, but standardize the workshop-facing documentation around `public/cv.docx`.

## Required npm scripts

Ensure `package.json` has scripts equivalent to:

```json
{
  "scripts": {
    "generate:cv": "python3 scripts/cv/parse_docx.py --input public/cv.docx --output src/generated/cv-data.json",
    "dev": "npm run generate:cv && next dev",
    "build": "npm run generate:cv && next build"
  }
}
```

If the parser already has fallback logic from `cv.docx` to `public/cv.docx`, keep it, but make the explicit script path point to `public/cv.docx` for clarity.

## Parser requirements

`scripts/cv/parse_docx.py` should:

1. Read a `.docx` file.
2. Extract structured sections such as employment, education, research areas, publications, work in progress, teaching, invited talks, honors/grants, and service.
3. Write JSON to `src/generated/cv-data.json`.
4. Fail clearly if the input CV is missing.
5. Avoid network calls.
6. Avoid secrets.

## Website requirements

The homepage should consume generated data for at least:

- current title/affiliation, where possible
- research areas
- selected publications
- work in progress

The CV page should provide:

- embedded PDF viewer
- download button
- open-in-new-tab link

The research and teaching pages may remain manually edited narrative pages.

## GitHub Pages deployment requirements

The GitHub Actions deployment workflow should:

1. Trigger on push to `main` and manual `workflow_dispatch`.
2. Run `npm ci`.
3. Run `npm run build`.
4. Upload the static output directory, usually `./out`.
5. Deploy to GitHub Pages.

Do not add deploy secrets unless strictly necessary. Prefer GitHub Pages' built-in OIDC/pages deployment.

## Forbidden changes

Do not add:

- watchers
- cron jobs
- LaunchAgents
- background auto-commit automation
- scripts that automatically commit every repository change
- any code that sends CV content to a cloud LLM or third-party API
- any workflow that ingests unpublished manuscripts or student records

## Acceptance criteria

Before finalizing, run:

```bash
npm install
npm run generate:cv
npm run build
```

Then verify:

- `src/generated/cv-data.json` is created or updated.
- The homepage reflects publication/work-in-progress data from the DOCX CV.
- The CV page embeds the configured PDF file.
- The PDF download link works.
- GitHub Actions deploys successfully on push to `main`.
- No watcher, cron, LaunchAgent, or background auto-commit behavior was introduced.

## Final response format

When done, report:

1. Files changed.
2. Validation commands run and whether they passed.
3. Any assumptions about the CV format.
4. Any remaining manual steps for the user.
