/** @type {import('next').NextConfig} */
const repo = process.env.GITHUB_REPOSITORY?.split('/')[1] ?? '';
const isUserSite = repo.endsWith('.github.io');
const basePath = process.env.NEXT_PUBLIC_BASE_PATH
  ?? (process.env.GITHUB_ACTIONS && repo && !isUserSite ? `/${repo}` : '');

const nextConfig = {
  output: 'export',
  reactStrictMode: true,
  trailingSlash: true,
  images: { unoptimized: true },
  basePath: basePath || undefined,
  assetPrefix: basePath || undefined,
  env: {
    NEXT_PUBLIC_BASE_PATH: basePath || '',
  },
};

module.exports = nextConfig;
