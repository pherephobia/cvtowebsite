# 60-Minute Tutorial Plan

## Title

CV를 업데이트하면 자동으로 반영되는 학술 홈페이지 만들기

## Learning goal

By the end of the session, participants should understand how to use an AI coding agent to set up a CV-driven academic website workflow:

```text
DOCX CV → parser → generated data → website → GitHub Pages
```

They do not need to write the parser or site code manually.

## 0–5 min: Show the final outcome

Show a working academic website with:

- homepage bio
- selected publications
- work in progress
- CV page with embedded PDF
- GitHub Pages deployment

Core message:

> The website is not manually retyped from the CV. The website reads structured data generated from the Word CV.

## 5–12 min: Explain the architecture

Use this diagram:

```text
public/cv.docx
  → scripts/cv/parse_docx.py
  → src/generated/cv-data.json
  → src/content/cvGenerated.ts
  → homepage/publications rendering

public/cv.pdf
  → src/content/site.ts
  → src/pages/cv.tsx
```

Define three ideas:

1. Canonical input: the file humans update.
2. Parser: the script that turns the CV into structured data.
3. Deployment: GitHub Actions builds and publishes the site.

## 12–20 min: Open the repository

Participants should either:

- fork the starter repository, or
- create a copy from a template repository.

Point out files they are allowed to edit:

- `public/cv.docx`
- `public/cv.pdf`
- `src/content/site.ts`
- `src/content/research.ts`
- `src/content/teaching.ts`
- `public/headshot.jpg`

## 20–35 min: Use Codex or Claude Code

Participants paste `AGENT_SPEC_CV_WEBSITE.md` into their coding agent.

The instructor should emphasize:

- Give the agent a concrete architecture.
- Give forbidden changes.
- Give validation commands.
- Do not accept changes until the build passes.

## 35–45 min: Validate locally or in Codespaces

Run:

```bash
npm install
npm run generate:cv
npm run build
```

Check:

- generated JSON exists
- build succeeds
- output directory exists
- no watcher/cron/auto-commit was added

## 45–53 min: Push and deploy

Participants commit and push. Then open GitHub Actions and confirm that the Pages deployment runs successfully.

Deployment checklist:

- Actions tab shows successful workflow.
- Pages URL is available.
- Homepage loads.
- CV page loads.

## 53–58 min: Simulate a CV update

Make one small change in `public/cv.docx`, such as adding a test work-in-progress item.

Then run:

```bash
npm run generate:cv
npm run build
```

Commit only CV inputs if using build-time generation policy:

```bash
git add public/cv.docx public/cv.pdf
git commit -m "Update CV"
git push
```

## 58–60 min: Wrap-up

Final principle:

> Do not maintain CV content in two places. Maintain the CV, regenerate the website, and verify the build.
