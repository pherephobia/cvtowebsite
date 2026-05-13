import { research } from '@/content/research';
import { cv } from '@/content/cvGenerated';

export default function ResearchPage() {
  const { research_areas, publications, work_in_progress } = cv.sections;
  return (
    <main>
      <h2>Research</h2>
      <p className="lead">{research.intro}</p>

      {research_areas.length > 0 && (
        <>
          <h3>Areas</h3>
          <ul className="tag-list">
            {research_areas.map((area) => (
              <li key={area}>{area}</li>
            ))}
          </ul>
        </>
      )}

      <h3>Ongoing projects</h3>
      <ul className="clean">
        {research.projects.map((project) => (
          <li key={project.title}>
            <strong>{project.title}.</strong> {project.summary}
          </li>
        ))}
      </ul>

      {publications.length > 0 && (
        <>
          <h3>Publications</h3>
          <ul className="clean">
            {publications.map((pub) => (
              <li key={pub.citation}>{pub.citation}</li>
            ))}
          </ul>
        </>
      )}

      {work_in_progress.length > 0 && (
        <>
          <h3>Work in progress</h3>
          <ul className="clean">
            {work_in_progress.map((pub) => (
              <li key={pub.citation}>{pub.citation}</li>
            ))}
          </ul>
        </>
      )}
    </main>
  );
}
