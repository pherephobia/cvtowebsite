# CV Update Checklist

Use this after the starter repo is already configured.

## Routine CV update

1. Replace or edit `public/cv.docx`.
2. Replace `public/cv.pdf` if the downloadable CV changed.
3. Run:

```bash
npm run generate:cv
npm run build
```

4. Check the homepage:
   - selected publications
   - work in progress
   - title/affiliation if generated from CV

5. Check the CV page:
   - PDF embeds correctly
   - download button works
   - open-in-new-tab works

6. Commit and push:

```bash
git add public/cv.docx public/cv.pdf
git commit -m "Update CV"
git push
```

If your repository policy commits generated JSON, also add:

```bash
git add src/generated/cv-data.json
```

## Before public sharing

- Confirm email and profile links in `src/content/site.ts`.
- Confirm no private phone number or home address appears in `cv.docx` or PDF CV.
- Confirm unpublished manuscript titles are safe to display.
- Confirm GitHub Actions deploy succeeded.
