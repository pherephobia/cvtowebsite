import Link from 'next/link';
import { cv } from '@/content/cvGenerated';
import { site, withBasePath } from '@/content/site';

export default function Home() {
  const { header, sections } = cv;
  const selectedPublications = sections.publications.slice(0, 5);
  const workInProgress = sections.work_in_progress;

  return (
    <main>
      <section>
        {header.title && <p className="lead">{header.title}</p>}
        {header.affiliation && <p className="muted">{header.affiliation}</p>}
        {header.email && (
          <p>
            <a href={`mailto:${header.email}`}>{header.email}</a>
          </p>
        )}
        <p>
          <Link className="btn" href="/cv/">View CV</Link>{' '}
          <a className="btn" href={withBasePath(site.cvUrl)} download>
            Download PDF
          </a>
        </p>
      </section>

      {sections.research_areas.length > 0 && (
        <section>
          <h2>Research areas</h2>
          <ul className="tag-list">
            {sections.research_areas.map((area) => (
              <li key={area}>{area}</li>
            ))}
          </ul>
        </section>
      )}

      {selectedPublications.length > 0 && (
        <section>
          <h2>Selected publications</h2>
          <ul className="clean">
            {selectedPublications.map((pub) => (
              <li key={pub.citation}>{pub.citation}</li>
            ))}
          </ul>
        </section>
      )}

      {workInProgress.length > 0 && (
        <section>
          <h2>Work in progress</h2>
          <ul className="clean">
            {workInProgress.map((pub) => (
              <li key={pub.citation}>{pub.citation}</li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
