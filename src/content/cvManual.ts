// Hand-edited CV content used when there is no public/cv.docx to parse.
//
// Edit these values to match your CV. When the homepage / research / teaching
// pages render, any section that is empty in the generated JSON falls back to
// the values defined here, so you can maintain this file as the source of
// truth while still working PDF-only.
//
// If you later add a Word CV at public/cv.docx, the parser output will take
// precedence section-by-section automatically.

import type { CvData } from './cvGenerated'; // eslint-disable-line import/no-cycle

export const cvManual: CvData = {
  meta: { source: 'src/content/cvManual.ts', generatedAt: '', missing: false },
  header: {
    name: 'Your Name',
    title: 'Your Title',
    affiliation: 'Your Affiliation',
    email: 'you@example.edu',
  },
  sections: {
    employment: [
      // 'Assistant Professor, Department of X, Y University, 2023–present',
    ],
    education: [
      // 'Ph.D. in Field, University, Year',
    ],
    research_areas: [
      // 'Comparative politics',
      // 'Political economy',
    ],
    publications: [
      // { citation: 'Author. (Year). Title. Journal, Vol(Issue), pp.', year: 'YYYY' },
    ],
    work_in_progress: [
      // { citation: 'Author. Title. Manuscript under review.', year: '' },
    ],
    teaching: [
      // 'Course Name (level), Institution',
    ],
    invited_talks: [],
    honors: [],
    service: [],
  },
  other: {},
};
