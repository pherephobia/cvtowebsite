# CV-Driven Academic Website Starter Pack

## Purpose

This starter pack is for a 60-minute workshop where participants use an AI coding agent such as Codex or Claude Code to build or adapt an academic website whose homepage content is generated from a Word CV.

The central idea is:

```text
Word CV → parser → structured JSON → website content → GitHub Pages
```

Participants do not need to write the code themselves. They need to understand the workflow, give the coding agent a precise task, and verify that the generated site behaves correctly.

## Recommended participant workflow

1. Fork or copy the starter repository.
2. Replace the sample CV files:
   - `public/cv.docx`
   - `public/cv.pdf` or the participant's equivalent PDF filename.
3. Ask Codex or Claude Code to apply `AGENT_SPEC_CV_WEBSITE.md`.
4. Run the validation commands:

```bash
npm install
npm run generate:cv
npm run build
```

5. Commit and push.
6. Confirm that GitHub Pages deploys successfully.
7. Visit the live URL and check that publications, work in progress, bio details, and the CV page reflect the current CV.

## What participants should edit after setup

Routine edits should be limited to:

| Task | File |
|---|---|
| Update the canonical Word CV | `public/cv.docx` |
| Replace downloadable CV PDF | `public/cv.pdf` or configured PDF path |
| Update research narrative | `src/content/research.ts` |
| Update teaching narrative | `src/content/teaching.ts` |
| Update profile links | `src/content/site.ts` |
| Replace headshot | `public/headshot.jpg` |

Generated files should not be hand-edited unless the repository policy explicitly commits generated output.

## What not to build in the workshop

Do not add:

- file watchers
- cron jobs
- LaunchAgents
- background auto-commit scripts
- automatic parsing of arbitrary PDF CVs
- unpublished manuscript or student-data ingestion

The workshop should teach a controlled, explicit update workflow, not an always-on automation system.
