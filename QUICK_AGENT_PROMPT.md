# Quick Agent Prompt

Use this shorter prompt if time is limited.

```text
You are modifying an academic Next.js website repo. Make the site CV-driven.

Use public/cv.docx as the canonical structured CV source. It should be parsed by scripts/cv/parse_docx.py into src/generated/cv-data.json. Ensure npm run generate:cv performs that parse, and ensure npm run dev and npm run build run generate:cv first.

Use public/cv.pdf as the public downloadable/embeddable CV. Ensure src/content/site.ts exposes the PDF URL and src/pages/cv.tsx embeds the PDF, has a download button, and has an open-in-new-tab link.

GitHub Pages deploy should run npm run build on pushes to main and workflow_dispatch.

Do not add watchers, cron jobs, LaunchAgents, background auto-commit scripts, or any cloud API calls for parsing CV content.

Run npm install, npm run generate:cv, and npm run build before finalizing. Report files changed and validation results.
```
