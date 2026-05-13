import { site, withBasePath } from '@/content/site';

export default function CvPage() {
  const pdfUrl = withBasePath(site.cvUrl);
  return (
    <main>
      <h2>Curriculum Vitae</h2>
      <div className="cv-actions">
        <a className="btn" href={pdfUrl} download>
          Download PDF
        </a>
        <a className="btn" href={pdfUrl} target="_blank" rel="noopener noreferrer">
          Open in new tab
        </a>
      </div>
      <object className="pdf-embed" data={pdfUrl} type="application/pdf" aria-label="Embedded CV PDF">
        <p>
          Your browser cannot display the embedded PDF.{' '}
          <a href={pdfUrl}>Download the CV instead.</a>
        </p>
      </object>
    </main>
  );
}
