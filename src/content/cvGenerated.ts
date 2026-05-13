// CV content consumed by the site.
//
// Source-of-truth precedence (section-by-section):
//   1. src/generated/cv-data.json  -- produced by `npm run generate:cv`
//                                     from public/cv.docx, when present.
//   2. src/content/cvManual.ts     -- hand-edited fallback.
//
// If you only maintain a PDF CV, leave public/cv.docx absent: the parser
// writes a stub JSON, and the manual file in cvManual.ts is what renders.

import data from '@/generated/cv-data.json';
import { cvManual } from './cvManual';

export type Publication = {
  citation: string;
  year: string;
};

export type CvData = {
  meta: { source: string; generatedAt: string; missing?: boolean };
  header: {
    name?: string;
    title?: string;
    affiliation?: string;
    email?: string;
  };
  sections: {
    employment: string[];
    education: string[];
    research_areas: string[];
    publications: Publication[];
    work_in_progress: Publication[];
    teaching: string[];
    invited_talks: string[];
    honors: string[];
    service: string[];
  };
  other: Record<string, string[]>;
};

const generated = data as CvData;

function pickStringList(a: string[], b: string[]): string[] {
  return a.length > 0 ? a : b;
}

function pickPubList(a: Publication[], b: Publication[]): Publication[] {
  return a.length > 0 ? a : b;
}

function pickField<T extends string | undefined>(a: T, b: T): T {
  return a && a.trim() !== '' ? a : b;
}

export const cv: CvData = {
  meta: generated.meta,
  header: {
    name: pickField(generated.header.name, cvManual.header.name),
    title: pickField(generated.header.title, cvManual.header.title),
    affiliation: pickField(generated.header.affiliation, cvManual.header.affiliation),
    email: pickField(generated.header.email, cvManual.header.email),
  },
  sections: {
    employment: pickStringList(generated.sections.employment, cvManual.sections.employment),
    education: pickStringList(generated.sections.education, cvManual.sections.education),
    research_areas: pickStringList(generated.sections.research_areas, cvManual.sections.research_areas),
    publications: pickPubList(generated.sections.publications, cvManual.sections.publications),
    work_in_progress: pickPubList(generated.sections.work_in_progress, cvManual.sections.work_in_progress),
    teaching: pickStringList(generated.sections.teaching, cvManual.sections.teaching),
    invited_talks: pickStringList(generated.sections.invited_talks, cvManual.sections.invited_talks),
    honors: pickStringList(generated.sections.honors, cvManual.sections.honors),
    service: pickStringList(generated.sections.service, cvManual.sections.service),
  },
  other: generated.other,
};
