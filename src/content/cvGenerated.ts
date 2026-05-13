// Typed re-export of the generated CV JSON.
// Run `npm run generate:cv` to refresh src/generated/cv-data.json from
// public/cv.docx. Do not hand-edit cv-data.json.

import data from '@/generated/cv-data.json';

export type Publication = {
  citation: string;
  year: string;
};

export type CvData = {
  meta: { source: string; generatedAt: string };
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

export const cv = data as CvData;
