import { teaching } from '@/content/teaching';
import { cv } from '@/content/cvGenerated';

export default function TeachingPage() {
  const cvCourses = cv.sections.teaching;
  return (
    <main>
      <h2>Teaching</h2>
      <p className="lead">{teaching.statement}</p>

      <h3>Courses</h3>
      <ul className="clean">
        {teaching.courses.map((course) => (
          <li key={course.title}>
            <strong>{course.title}</strong> ({course.level}). {course.summary}
          </li>
        ))}
      </ul>

      {cvCourses.length > 0 && (
        <>
          <h3>Recent course listings (from CV)</h3>
          <ul className="clean">
            {cvCourses.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </>
      )}
    </main>
  );
}
