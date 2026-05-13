#!/usr/bin/env python3
"""Parse an academic LaTeX CV into the same JSON shape as parse_docx.py.

Designed for a CV whose sections are marked with patterns like

    \\begin{large}{\\bf SECTION TITLE}

and whose publications are listed with `\\item[N.]` inside an `itemize`
block. Uses only the Python standard library (no `pylatexenc` dependency)
to keep the workshop install lightweight.

Usage:
    python3 scripts/cv/parse_tex.py --input public/cv.tex \\
        --output src/generated/cv-data.json
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# LaTeX -> plain text
# ---------------------------------------------------------------------------

URL_RE = re.compile(r"https?://[^\s}]+")


def _strip_latex(s: str) -> str:
    """Best-effort plain-text reduction of a LaTeX fragment."""
    if not s:
        return ""
    # Drop sizing/spacing commands that take a dimension argument so their
    # numeric arguments don't leak into the output (\vspace{3pt} -> nothing).
    s = re.sub(
        r"\\(?:vspace|hspace|vskip|hskip|setlength|addtolength)\*?\s*\{[^{}]*\}",
        " ",
        s,
    )
    # \href{URL}{TEXT} -> TEXT
    s = re.sub(r"\\href\s*\{[^{}]*\}\s*\{([^{}]*)\}", r"\1", s)
    # Inline formatting wrappers: keep the inside.
    s = re.sub(
        r"\\(?:textbf|textit|emph|texttt|textsc|textrm|mbox)\s*\{([^{}]*)\}",
        r"\1",
        s,
    )
    # `{\bf ...}` and `{\it ...}` -> ...
    s = re.sub(r"\{\\(?:bf|it|em|tt|sc|sl)\s+([^{}]*)\}", r"\1", s)
    # Drop environment delimiters, including any optional `[...]` arg AND
    # required dimension arg `{0.6\textwidth}`. This prevents `[c]{0.6}` from
    # leaking through when we strip the environment. Allow whitespace between
    # `\begin`/`\end` and the `{name}` block — some hand-written LaTeX
    # introduces line breaks there.
    s = re.sub(r"\\begin\s*\{[^}]+\}(\s*\[[^\]]*\])?(\s*\{[^{}]*\})?", " ", s)
    s = re.sub(r"\\end\s*\{[^}]+\}", " ", s)
    s = re.sub(r"\\item\b\s*\[[^\]]*\]", " ", s)
    s = re.sub(r"\\item\b", " ", s)
    # Drop remaining single-argument commands by unwrapping their argument.
    for _ in range(4):
        s = re.sub(r"\\[a-zA-Z]+\*?\s*\{([^{}]*)\}", r"\1", s)
    # Drop bare commands (with optional arguments) that have no remaining body.
    s = re.sub(r"\\[a-zA-Z]+\*?(\s*\[[^\]]*\])*", " ", s)
    # Drop stray dimension tokens that were arguments to layout commands.
    s = re.sub(r"\b\d+(?:\.\d+)?\s*(?:pt|cm|mm|em|ex|in|sp|bp|dd|pc)\b", " ", s)
    # Character escapes & misc.
    replacements = {
        "~": " ",
        "\\&": "&",
        "\\$": "$",
        "\\%": "%",
        "\\#": "#",
        "\\_": "_",
        "\\{": "{",
        "\\}": "}",
        "\\\\": " ",
        "``": '"',
        "''": '"',
        "\\'": "'",
        "\\`": "'",
        "—": "—",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    s = re.sub(r"\s+", " ", s).strip(" .,;-—")
    return s


# ---------------------------------------------------------------------------
# Sectioning
# ---------------------------------------------------------------------------

# Map LaTeX section titles -> canonical keys (multi-source sections are merged).
SECTION_MAP: List[Tuple[str, re.Pattern[str]]] = [
    ("employment", re.compile(r"^ACADEMIC APPOINTMENTS\b", re.I)),
    ("education", re.compile(r"^EDUCATION\b", re.I)),
    ("research_areas", re.compile(r"^RESEARCH INTERESTS?\b", re.I)),
    ("teaching_interests", re.compile(r"^TEACHING INTERESTS?\b", re.I)),
    ("publications", re.compile(r"^PEER-?REVIEWED ARTICLES?\b", re.I)),
    ("publications", re.compile(r"^OTHER PUBLICATIONS?\b", re.I)),
    ("work_in_progress", re.compile(r"^UNDER REVIEWS?\b", re.I)),
    ("work_in_progress", re.compile(r"^WORKS? IN PROGRESS\b", re.I)),
    ("invited_talks", re.compile(r"^INVITED TALKS?\b", re.I)),
    ("honors", re.compile(r"^HONORS?(\b|,)", re.I)),
    ("research_experience", re.compile(r"^RESEARCH EXPERIENCE\b", re.I)),
    ("teaching_experience", re.compile(r"^TEACHING EXPERIENCE\b", re.I)),
    ("service", re.compile(r"^PROFESSIONAL SERVICE\b", re.I)),
    ("affiliations", re.compile(r"^PROFESSIONAL AFFILIATION", re.I)),
    ("skills", re.compile(r"^EXTRA CURRICULUM", re.I)),
    ("references", re.compile(r"^REFERENCES?\b", re.I)),
]


# A section heading looks like `\begin{large}` (with optional whitespace and
# inner braces) followed by `{\bf TITLE}` where TITLE is largely uppercase.
SECTION_HEAD_RE = re.compile(
    r"\\begin\{large\}\s*(?:\\vspace[^{}]*\{[^}]*\}\s*)?"
    r"\{\\bf\s+([^}]+)\}([^\n]*)",
)


def _canonical_key(title: str) -> Optional[str]:
    title = title.strip()
    for key, pat in SECTION_MAP:
        if pat.search(title):
            return key
    return None


def _split_sections(body: str) -> List[Tuple[str, str, str]]:
    """Return (raw_title, canonical_key_or_'', content) tuples in order."""
    matches = list(SECTION_HEAD_RE.finditer(body))
    out: List[Tuple[str, str, str]] = []
    for i, m in enumerate(matches):
        title = (m.group(1) + " " + (m.group(2) or "")).strip()
        title = re.sub(r"\\[a-zA-Z]+\*?", "", title)
        title = re.sub(r"[\\{}]", "", title)
        title = re.sub(r"\s+", " ", title).strip()
        # Section titles are dominantly upper-case. Skip non-headings (institution names).
        head_text = m.group(1).strip()
        if not re.search(r"[A-Z]{3,}", head_text):
            continue
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        content = body[start:end]
        out.append((title, _canonical_key(title) or "", content))
    return out


# ---------------------------------------------------------------------------
# Itemize extraction (publications, talks, etc.)
# ---------------------------------------------------------------------------

ITEMIZE_RE = re.compile(r"\\begin\{itemize\}(.*?)\\end\{itemize\}", re.DOTALL)
ITEM_RE = re.compile(r"\\item(?:\[[^\]]*\])?")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


FLUSH_LR_RE = re.compile(
    r"\\begin\s*\{(flushleft|flushright)\}(.*?)\\end\s*\{\1\}",
    re.DOTALL,
)


def _pair_lines_from_section(content: str) -> List[str]:
    """Convert flushleft/flushright two-column pairs to plain-text lines.

    Used for employment / education / honors blocks that use minipage layouts
    instead of `itemize`. Matches are scanned in document order; consecutive
    (left, right) pairs are joined as `left — right`.
    """
    matches = list(FLUSH_LR_RE.finditer(content))
    lines: List[str] = []
    i = 0
    while i < len(matches):
        side = matches[i].group(1)
        text = _strip_latex(matches[i].group(2))
        if side == "flushleft" and i + 1 < len(matches) and matches[i + 1].group(1) == "flushright":
            right = _strip_latex(matches[i + 1].group(2))
            combined = " — ".join(p for p in (text, right) if p)
            if combined:
                lines.append(combined)
            i += 2
        else:
            if text:
                lines.append(text)
            i += 1
    return lines


def _items_from_section(content: str) -> List[str]:
    """Extract `\\item ...` entries (across all itemize blocks) as plain text."""
    items: List[str] = []
    for block_match in ITEMIZE_RE.finditer(content):
        block = block_match.group(1)
        # Split on \item, keeping the chunks after each.
        chunks = ITEM_RE.split(block)
        for chunk in chunks[1:]:  # first chunk is preamble before any \item
            text = _strip_latex(chunk)
            if text:
                items.append(text)
    return items


def _parse_publication(line: str) -> Dict[str, str]:
    year_match = YEAR_RE.search(line)
    return {
        "citation": line.strip(),
        "year": year_match.group(0) if year_match else "",
    }


# ---------------------------------------------------------------------------
# Header (name, email, links)
# ---------------------------------------------------------------------------

NAME_RE = re.compile(r"\\begin\{huge\}.*?\{\\bf\s+([^}]+)\}", re.DOTALL)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
HREF_RE = re.compile(r"\\href\{([^}]+)\}")


def _extract_header(full_tex: str, body: str) -> Dict[str, str]:
    header: Dict[str, str] = {}
    m = NAME_RE.search(full_tex)
    if m:
        name = _strip_latex(m.group(1))
        # The CV uses ALL CAPS bold for the name; convert to title case.
        if name.isupper():
            name = " ".join(part.capitalize() for part in name.split())
        header["name"] = name

    # Search the area between the name and the first section heading for
    # contact details (email + relevant URLs).
    first_section = SECTION_HEAD_RE.search(body)
    top = body[: first_section.start()] if first_section else body[:2000]

    em = EMAIL_RE.search(top)
    if em:
        header["email"] = em.group(0)

    links: Dict[str, str] = {}
    for href_match in HREF_RE.finditer(top):
        target = href_match.group(1).strip()
        if "github.com" in target:
            links["github"] = target if target.startswith("http") else f"https://{target}"
        elif target.startswith("mailto:") or "@" in target:
            continue
        elif target.startswith("http") or "." in target:
            url = target if target.startswith("http") else f"https://{target}"
            links.setdefault("website", url)
    if links:
        header["links"] = links  # type: ignore[assignment]

    return header


# ---------------------------------------------------------------------------
# Top-level
# ---------------------------------------------------------------------------

_COMMENT_RE = re.compile(r"(?<!\\)%.*?$", re.MULTILINE)


def _strip_tex_comments(s: str) -> str:
    """Remove LaTeX line comments, preserving escaped `\\%`."""
    return _COMMENT_RE.sub("", s)


def parse(input_path: Path) -> Dict[str, object]:
    full_tex = input_path.read_text(encoding="utf-8")
    full_tex = _strip_tex_comments(full_tex)
    doc_start = full_tex.find(r"\begin{document}")
    body = full_tex[doc_start:] if doc_start != -1 else full_tex

    header = _extract_header(full_tex, body)
    sections = _split_sections(body)

    canonical: Dict[str, List[str]] = {}
    other: Dict[str, List[str]] = {}
    # Sections that use two-column flushleft/flushright layouts rather than
    # itemize. We extract pairs and *also* keep any itemize bullets that
    # might appear inside (e.g. fellowship details under HONORS).
    PAIR_SECTIONS = {"employment", "education", "honors"}
    for title, key, content in sections:
        if key in PAIR_SECTIONS:
            pair_lines = _pair_lines_from_section(content)
            bullet_lines = _items_from_section(content)
            items = pair_lines + bullet_lines
        else:
            items = _items_from_section(content)
            if not items:
                stripped = _strip_latex(content)
                for chunk in re.split(r"(?:\n\s*\n|\s\s\s+|(?<=Present)\s)", stripped):
                    chunk = chunk.strip(" .,;")
                    if len(chunk) > 4:
                        items.append(chunk)
        if key:
            canonical.setdefault(key, []).extend(items)
        else:
            other.setdefault(title, []).extend(items)

    # Build canonical structure with proper types.
    def _str_list(key: str) -> List[str]:
        return canonical.get(key, [])

    def _pub_list(key: str) -> List[Dict[str, str]]:
        return [_parse_publication(line) for line in canonical.get(key, [])]

    # Research areas: the LaTeX lists multiple subfields per paragraph; flatten
    # by splitting on commas if we ended up with one big string.
    raw_areas = _str_list("research_areas")
    research_areas: List[str] = []
    for entry in raw_areas:
        for piece in re.split(r",\s*", entry):
            piece = piece.strip(" .;")
            if piece:
                research_areas.append(piece)

    teaching = _str_list("teaching_experience") + _str_list("teaching_interests")

    # Derive title/affiliation from the current academic appointment when
    # possible. The CV's first ACADEMIC APPOINTMENTS entry uses pairs of
    # "Institution — Date" then "Role — Location".
    employment = _str_list("employment")
    if employment and not header.get("affiliation"):
        first = employment[0].split(" — ", 1)[0].strip()
        if first:
            header["affiliation"] = first
    if len(employment) > 1 and not header.get("title"):
        second = employment[1].split(" — ", 1)[0].strip()
        if second:
            header["title"] = second

    return {
        "meta": {
            "source": str(input_path).replace(os.sep, "/"),
            "generatedAt": _dt.datetime.now(_dt.timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
            "parser": "tex",
        },
        "header": header,
        "sections": {
            "employment": _str_list("employment"),
            "education": _str_list("education"),
            "research_areas": research_areas,
            "publications": _pub_list("publications"),
            "work_in_progress": _pub_list("work_in_progress"),
            "teaching": teaching,
            "invited_talks": _str_list("invited_talks"),
            "honors": _str_list("honors"),
            "service": _str_list("service"),
        },
        "other": other,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Parse a LaTeX CV into JSON.")
    parser.add_argument("--input", default="public/cv.tex", help="Path to the .tex CV.")
    parser.add_argument("--output", default="src/generated/cv-data.json",
                        help="Path to the JSON output.")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.is_file():
        sys.stderr.write(
            f"WARNING: LaTeX CV not found at '{args.input}'. "
            f"Writing empty stub; the site will use src/content/cvManual.ts.\n"
        )
        stub = {
            "meta": {
                "source": str(input_path).replace(os.sep, "/"),
                "generatedAt": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
                "parser": "tex",
                "missing": True,
            },
            "header": {},
            "sections": {
                "employment": [], "education": [], "research_areas": [],
                "publications": [], "work_in_progress": [], "teaching": [],
                "invited_talks": [], "honors": [], "service": [],
            },
            "other": {},
        }
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(stub, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return 0

    data = parse(input_path)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sys.stdout.write(f"Wrote {out} from {input_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
