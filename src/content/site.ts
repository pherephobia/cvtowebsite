// Site-wide configuration that is not derived from the CV.
// Edit these values to point to your own profile links and CV PDF.

export const site = {
  name: 'Academic Website',
  description: 'Personal academic website generated from a Word CV.',
  // Public PDF path served from /public. Used by the CV page for embedding
  // and by the homepage as the downloadable link.
  cvUrl: '/cv.pdf',
  links: {
    email: 'mailto:you@example.edu',
    github: 'https://github.com/your-handle',
    googleScholar: 'https://scholar.google.com/citations?user=YOUR_ID',
    orcid: 'https://orcid.org/0000-0000-0000-0000',
  },
} as const;

// Apply the basePath that Next.js uses when deployed to a project Pages site,
// e.g. https://USER.github.io/REPO/. For local dev the base path is empty.
export function withBasePath(path: string): string {
  const base = process.env.NEXT_PUBLIC_BASE_PATH ?? '';
  if (!path.startsWith('/')) return path;
  return `${base}${path}`;
}
