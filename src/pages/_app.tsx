import type { AppProps } from 'next/app';
import Link from 'next/link';
import Head from 'next/head';
import '@/styles/globals.css';
import { site } from '@/content/site';
import { cv } from '@/content/cvGenerated';

export default function App({ Component, pageProps }: AppProps) {
  const displayName = cv.header.name ?? site.name;
  return (
    <>
      <Head>
        <title>{displayName}</title>
        <meta name="description" content={site.description} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <div className="container">
        <header className="site-header">
          <h1>
            <Link href="/">{displayName}</Link>
          </h1>
          <nav className="site-nav">
            <Link href="/">Home</Link>
            <Link href="/research/">Research</Link>
            <Link href="/teaching/">Teaching</Link>
            <Link href="/cv/">CV</Link>
          </nav>
        </header>
        <Component {...pageProps} />
        <footer className="site-footer">
          Generated from{' '}
          <code>{cv.meta.source}</code> on {cv.meta.generatedAt}.
        </footer>
      </div>
    </>
  );
}
