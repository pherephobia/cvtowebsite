#!/usr/bin/env python3
"""Generate a sample public/cv.docx and public/cv.pdf for the workshop starter.

Both files are constructed with only the Python standard library so the
workshop has working sample inputs without requiring any pip installs.

Run:
    python3 scripts/cv/make_sample_cv.py

Re-running overwrites the sample files. Participants are expected to replace
these with their own CVs.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _p(text: str, *, style: str | None = None) -> str:
    pPr = f"<w:pPr><w:pStyle w:val=\"{style}\"/></w:pPr>" if style else ""
    return f"<w:p>{pPr}<w:r><w:t xml:space=\"preserve\">{escape(text)}</w:t></w:r></w:p>"


def _heading(text: str) -> str:
    return _p(text, style="Heading1")


def _build_document_xml() -> str:
    body_parts: list[str] = []
    # Header block
    body_parts += [
        _p("Jane Q. Researcher", style="Title"),
        _p("Assistant Professor of Political Science"),
        _p("Example University"),
        _p("jane.researcher@example.edu"),
    ]
    # Sections
    body_parts.append(_heading("EMPLOYMENT"))
    body_parts += [
        _p("Assistant Professor, Department of Political Science, Example University, 2023–present"),
        _p("Postdoctoral Fellow, Center for Policy Studies, Another University, 2021–2023"),
    ]
    body_parts.append(_heading("EDUCATION"))
    body_parts += [
        _p("Ph.D. in Political Science, Big State University, 2021"),
        _p("M.A. in Political Science, Big State University, 2017"),
        _p("B.A. in Political Science, Liberal Arts College, 2015"),
    ]
    body_parts.append(_heading("RESEARCH AREAS"))
    body_parts += [
        _p("Comparative politics, political economy, democratic backsliding, causal inference"),
    ]
    body_parts.append(_heading("PUBLICATIONS"))
    body_parts += [
        _p("Researcher, J. Q. (2024). Institutional drift in young democracies. Journal of Politics, 86(3), 1234–1250."),
        _p("Researcher, J. Q., & Coauthor, A. (2023). Polarization and policy gridlock. American Political Science Review, 117(2), 555–572."),
        _p("Researcher, J. Q. (2022). Measuring democratic erosion. Comparative Political Studies, 55(8), 999–1025."),
    ]
    body_parts.append(_heading("WORK IN PROGRESS"))
    body_parts += [
        _p("Researcher, J. Q. Elite signaling and democratic norms. Manuscript under review."),
        _p("Researcher, J. Q., & Coauthor, B. The local roots of national populism. Working paper, 2024."),
    ]
    body_parts.append(_heading("TEACHING"))
    body_parts += [
        _p("Comparative Political Institutions (undergraduate), Example University"),
        _p("Research Design for Political Science (graduate), Example University"),
    ]
    body_parts.append(_heading("INVITED TALKS"))
    body_parts += [
        _p("Comparative Politics Workshop, Peer University, 2024"),
        _p("Annual Meeting of the American Political Science Association, 2023"),
    ]
    body_parts.append(_heading("HONORS AND GRANTS"))
    body_parts += [
        _p("National Science Foundation Dissertation Improvement Grant, 2020"),
        _p("Best Graduate Paper Award, Comparative Politics Section, APSA, 2019"),
    ]
    body_parts.append(_heading("SERVICE"))
    body_parts += [
        _p("Reviewer: American Political Science Review, Journal of Politics, Comparative Political Studies"),
        _p("Graduate Admissions Committee, Department of Political Science, 2024"),
    ]

    body_xml = "".join(body_parts)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W}">'
        f"<w:body>{body_xml}<w:sectPr/></w:body>"
        "</w:document>"
    )


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""


def write_docx(path: Path) -> None:
    doc_xml = _build_document_xml()
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES)
        zf.writestr("_rels/.rels", ROOT_RELS)
        zf.writestr("word/document.xml", doc_xml)


def write_pdf(path: Path) -> None:
    """Write a tiny but valid single-page PDF placeholder."""
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        None,  # filled below — needs to come after content is known
    ]
    content_stream = (
        b"BT /F1 18 Tf 72 720 Td (Sample CV - replace public/cv.pdf with your real CV.) Tj ET"
    )
    objects[4] = (
        b"<< /Length " + str(len(content_stream)).encode("ascii") + b" >>\nstream\n"
        + content_stream + b"\nendstream"
    )

    out = bytearray()
    out += b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets: list[int] = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode("ascii") + body + b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode("ascii")
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n"
    ).encode("ascii")
    path.write_bytes(bytes(out))


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    docx_path = PUBLIC / "cv.docx"
    pdf_path = PUBLIC / "cv.pdf"
    write_docx(docx_path)
    write_pdf(pdf_path)
    print(f"Wrote {docx_path}")
    print(f"Wrote {pdf_path}")


if __name__ == "__main__":
    main()
