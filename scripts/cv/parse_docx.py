#!/usr/bin/env python3
"""Parse an academic Word CV into structured JSON.

Reads a .docx file (which is a ZIP of XML) using only the Python standard
library, so the workshop does not require pip installs. The output is written
as JSON consumed by the Next.js site.

Usage:
    python3 scripts/cv/parse_docx.py \
        --input public/cv.docx \
        --output src/generated/cv-data.json

Design notes:
- Section detection prefers paragraph style names ("Heading1", "Heading2")
  but falls back to ALL-CAPS short paragraphs, which is the common
  convention in academic CVs.
- Section labels are normalized to canonical keys (employment, education,
  research_areas, publications, work_in_progress, teaching, invited_talks,
  honors, service). Anything we cannot map is preserved under `other`.
- No network calls, no secrets, no third-party packages.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NSMAP = {"w": W_NS}


# ---------------------------------------------------------------------------
# DOCX -> ordered (style, text) paragraphs
# ---------------------------------------------------------------------------

def _read_document_xml(docx_path: Path) -> bytes:
    with zipfile.ZipFile(docx_path) as zf:
        with zf.open("word/document.xml") as f:
            return f.read()


def _paragraph_text(p_el: ET.Element) -> str:
    parts: List[str] = []
    for node in p_el.iter():
        tag = node.tag.split("}", 1)[-1]
        if tag == "t" and node.text:
            parts.append(node.text)
        elif tag == "tab":
            parts.append("\t")
        elif tag == "br":
            parts.append("\n")
    return "".join(parts).strip()


def _paragraph_style(p_el: ET.Element) -> Optional[str]:
    style = p_el.find("w:pPr/w:pStyle", NSMAP)
    if style is not None:
        return style.attrib.get(f"{{{W_NS}}}val")
    return None


def extract_paragraphs(docx_path: Path) -> List[Tuple[Optional[str], str]]:
    """Return ordered (style, text) pairs for every non-empty paragraph."""
    xml_bytes = _read_document_xml(docx_path)
    root = ET.fromstring(xml_bytes)
    body = root.find("w:body", NSMAP)
    if body is None:
        return []

    out: List[Tuple[Optional[str], str]] = []
    for p_el in body.iter(f"{{{W_NS}}}p"):
        text = _paragraph_text(p_el)
        if not text:
            continue
        out.append((_paragraph_style(p_el), text))
    return out


# ---------------------------------------------------------------------------
# Section detection
# ---------------------------------------------------------------------------

# Canonical key -> list of patterns (case-insensitive) that map to it.
SECTION_PATTERNS: List[Tuple[str, List[str]]] = [
    ("employment", ["employment", "academic appointments", "positions", "experience"]),
    ("education", ["education"]),
    ("research_areas", ["research areas", "research interests", "areas of interest", "fields of interest"]),
    ("publications", ["publications", "peer-reviewed publications", "refereed publications", "journal articles"]),
    ("work_in_progress", ["work in progress", "working papers", "manuscripts in progress", "under review"]),
    ("teaching", ["teaching", "courses taught", "teaching experience"]),
    ("invited_talks", ["invited talks", "presentations", "conference presentations", "talks"]),
    ("honors", ["honors", "awards", "grants", "fellowships", "honors and awards", "grants and awards"]),
    ("service", ["service", "professional service", "departmental service"]),
]


def _classify_heading(text: str) -> Optional[str]:
    norm = re.sub(r"[^a-z\s]", " ", text.lower()).strip()
    norm = re.sub(r"\s+", " ", norm)
    for key, patterns in SECTION_PATTERNS:
        for pat in patterns:
            if norm == pat or norm.startswith(pat + " ") or pat in norm.split(" - "):
                return key
    return None


def _looks_like_heading(style: Optional[str], text: str) -> bool:
    if style and style.lower().startswith("heading"):
        return True
    if style and style.lower() in {"title", "subtitle"}:
        return False  # treated as metadata, not section
    if len(text) <= 60 and text == text.upper() and any(ch.isalpha() for ch in text):
        # All-caps short line — typical academic CV section heading.
        return True
    return False


# ---------------------------------------------------------------------------
# Top-of-CV metadata heuristic
# ---------------------------------------------------------------------------

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def _extract_header(paragraphs: List[Tuple[Optional[str], str]]) -> Dict[str, str]:
    """Pull name / title / affiliation / email from the first few paragraphs.

    Heuristic: the first non-heading paragraph is the name. The next 1-3
    paragraphs (before any section heading) are scanned for a title/affiliation
    line and an email address.
    """
    header: Dict[str, str] = {}
    title_keywords = (
        "professor", "assistant", "associate", "lecturer", "fellow",
        "researcher", "scientist", "candidate", "ph.d", "phd",
    )
    for style, text in paragraphs[:8]:
        if _looks_like_heading(style, text) and _classify_heading(text):
            break
        if not header.get("name") and not _looks_like_heading(style, text):
            header["name"] = text
            continue
        m = EMAIL_RE.search(text)
        if m and not header.get("email"):
            header["email"] = m.group(0)
        lower = text.lower()
        if not header.get("title") and any(k in lower for k in title_keywords):
            header["title"] = text
        elif not header.get("affiliation") and ("university" in lower or "college" in lower or "institute" in lower):
            header["affiliation"] = text
    return header


# ---------------------------------------------------------------------------
# Section grouping
# ---------------------------------------------------------------------------

def group_sections(paragraphs: List[Tuple[Optional[str], str]]) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """Walk paragraphs, splitting into canonical and unmapped section buckets."""
    canonical: Dict[str, List[str]] = {key: [] for key, _ in SECTION_PATTERNS}
    other: Dict[str, List[str]] = {}
    current_key: Optional[str] = None
    current_other: Optional[str] = None

    for style, text in paragraphs:
        if _looks_like_heading(style, text):
            mapped = _classify_heading(text)
            if mapped:
                current_key, current_other = mapped, None
            else:
                current_key, current_other = None, text.strip()
                other.setdefault(current_other, [])
            continue
        if current_key is not None:
            canonical[current_key].append(text)
        elif current_other is not None:
            other[current_other].append(text)
    return canonical, other


# ---------------------------------------------------------------------------
# Light enrichment for specific sections
# ---------------------------------------------------------------------------

YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


def _split_research_areas(lines: List[str]) -> List[str]:
    """Research areas often appear as one comma-separated line or bullets."""
    if len(lines) == 1 and "," in lines[0]:
        return [s.strip(" .;") for s in lines[0].split(",") if s.strip()]
    return [line.strip(" .;") for line in lines if line.strip()]


def _parse_publication(line: str) -> Dict[str, str]:
    """Best-effort split of a publication line into year + citation."""
    year_match = YEAR_RE.search(line)
    return {
        "citation": line.strip(),
        "year": year_match.group(0) if year_match else "",
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _resolve_input(input_arg: str) -> Path:
    candidate = Path(input_arg)
    if candidate.is_file():
        return candidate
    # Backwards compatibility: fall back between cv.docx <-> public/cv.docx.
    fallback = Path("public/cv.docx") if candidate.name == "cv.docx" and candidate.parent == Path(".") else Path("cv.docx")
    if candidate != fallback and fallback.is_file():
        return fallback
    return candidate  # let the caller raise


def parse(input_path: Path) -> Dict[str, object]:
    paragraphs = extract_paragraphs(input_path)
    header = _extract_header(paragraphs)
    canonical, other = group_sections(paragraphs)

    publications = [_parse_publication(line) for line in canonical["publications"]]
    work_in_progress = [_parse_publication(line) for line in canonical["work_in_progress"]]
    research_areas = _split_research_areas(canonical["research_areas"])

    return {
        "meta": {
            "source": str(input_path).replace(os.sep, "/"),
            "generatedAt": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        },
        "header": header,
        "sections": {
            "employment": canonical["employment"],
            "education": canonical["education"],
            "research_areas": research_areas,
            "publications": publications,
            "work_in_progress": work_in_progress,
            "teaching": canonical["teaching"],
            "invited_talks": canonical["invited_talks"],
            "honors": canonical["honors"],
            "service": canonical["service"],
        },
        "other": other,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Parse a Word CV into JSON.")
    parser.add_argument("--input", default="public/cv.docx", help="Path to the .docx CV.")
    parser.add_argument("--output", default="src/generated/cv-data.json", help="Path to the JSON output.")
    args = parser.parse_args(argv)

    input_path = _resolve_input(args.input)
    if not input_path.is_file():
        sys.stderr.write(
            f"ERROR: CV file not found at '{args.input}'.\n"
            f"Place a Word CV at 'public/cv.docx' (or pass --input PATH) and re-run.\n"
        )
        return 2

    try:
        data = parse(input_path)
    except zipfile.BadZipFile:
        sys.stderr.write(f"ERROR: '{input_path}' is not a valid .docx file (bad zip).\n")
        return 3
    except ET.ParseError as e:
        sys.stderr.write(f"ERROR: failed to parse document.xml in '{input_path}': {e}\n")
        return 3

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sys.stdout.write(f"Wrote {output_path} from {input_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
