#!/usr/bin/env python3
"""Regenerate sources/README.md — a GitHub-facing index of the source corpus.

Mirrors the YAML frontmatter of every sources/<NN-folder>/*.md file. Run after
editing sources/ (same cadence as build_site.py). Intentionally does NOT recompute
word counts or dates — it reflects whatever the frontmatter records.

    python3 build_readme.py
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "sources")

# Curated human-readable section titles, keyed by folder slug. Folders that are
# not single authors (statements, hubs, topical) get descriptive names.
SECTION_TITLES = {
    "01-ezra-taft-benson": "Ezra Taft Benson",
    "02-d-todd-christofferson": "D. Todd Christofferson",
    "03-quentin-l-cook": "Quentin L. Cook",
    "04-robert-d-hales": "Robert D. Hales",
    "05-jeffrey-r-holland": "Jeffrey R. Holland",
    "06-david-o-mckay": "David O. McKay",
    "07-dallin-h-oaks": "Dallin H. Oaks",
    "08-ronald-a-rasband": "Ronald A. Rasband",
    "09-historical-statements": "Historical Church Statements & First Presidency Letters",
    "10-j-reuben-clark": "J. Reuben Clark Jr.",
    "11-resource-hubs": "Resource Hubs (aggregators)",
    "12-l-tom-perry": "L. Tom Perry",
    "13-w-cleon-skousen": "W. Cleon Skousen",
    "14-marion-g-romney": "Marion G. Romney",
    "15-h-verlan-andersen": "H. Verlan Andersen",
    "16-gordon-b-hinckley": "Gordon B. Hinckley",
    "17-howard-w-hunter": "Howard W. Hunter",
    "18-john-taylor": "John Taylor",
    "19-joseph-smith": "Joseph Smith",
    "20-spencer-w-kimball": "Spencer W. Kimball",
    "21-additional-church-leaders": "Additional Church Leaders",
    "22-supporting-authors": "Supporting Authors & Commentators",
    "23-topical-and-founding-documents": "Topical Compilations & Founding Documents",
}

# status -> (emoji, label). Label is appended after the emoji in the Status column.
STATUS_MAP = {
    "full": ("✅", ""),
    "external-fulltext": ("✅", ""),
    "scripture": ("✅", ""),
    "summary-only": ("⚠️", "summary"),
    "thin": ("⚠️", "thin"),
    "pointer": ("↪️", "pointer"),
    "audio-only": ("🔊", "audio"),
    "hub": ("🗂️", "index"),
}


def parse_frontmatter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"(\w+):\s*(.*)$", line)
        if mm:
            fm[mm.group(1)] = mm.group(2).strip().strip('"')
    return fm


def source_flag(fm):
    coll = fm.get("collection", "")
    sf = fm.get("source_file", "")
    if coll == "research-extended" or sf.startswith("raw/"):
        return " ·R"
    if coll == "tbf-book" or sf.startswith("TBF/"):
        return " ·B"
    return ""


def status_cell(fm):
    emoji, label = STATUS_MAP.get(fm.get("status", ""), ("✅", ""))
    cell = emoji
    if label:
        cell += " " + label
    cell += source_flag(fm)
    return cell


def md_escape(s):
    return (s or "").replace("|", "\\|")


def main():
    folders = sorted(
        d for d in os.listdir(SRC)
        if os.path.isdir(os.path.join(SRC, d)) and re.match(r"\d{2}-", d)
    )

    lines = []
    lines.append("# To Be Free — LDS Sources on Liberty, Freedom & Religious Liberty")
    lines.append("")
    lines.append(
        "A research collection of Latter-day Saint sources on liberty, freedom, and "
        "religious liberty, gathered to understand and validate political and social "
        "principles from a revealed-principles perspective. Builds on the original "
        "*To Be Free* compilation (`../TBF/`) and the curated religious-freedom core."
    )
    lines.append("")
    lines.append(
        "Every file carries standardized YAML frontmatter "
        "(`title, author, date, source_url, source_file, status, word_count, "
        "commentary, tags`). `commentary`/`tags` are placeholders for editorial "
        "blurbs and indexing."
    )
    lines.append("")
    lines.append(
        "**Legend:** ✅ full · ⚠️ thin/summary · 🔊 audio · ↪️ pointer · 🗂️ index · "
        "`·R` = converted from raw/ · `·B` = extracted from the *To Be Free* book."
    )
    lines.append("")

    total_docs = 0
    total_words = 0
    for n, folder in enumerate(folders, 1):
        docs = []
        for path in sorted(glob.glob(os.path.join(SRC, folder, "*.md"))):
            fm = parse_frontmatter(path)
            if fm is None:
                continue
            docs.append((os.path.basename(path), fm))
        if not docs:
            continue

        words = sum(int(fm.get("word_count") or 0) for _, fm in docs)
        total_docs += len(docs)
        total_words += words

        title = SECTION_TITLES.get(folder, folder)
        lines.append(f"## {n}. {title}")
        lines.append(f"*{len(docs)} docs · ~{words:,} words*")
        lines.append("")
        lines.append("| Title | Author | Date | Status | Words | File |")
        lines.append("|---|---|---|---|---|---|")
        for fname, fm in docs:
            lines.append(
                f"| {md_escape(fm.get('title',''))} "
                f"| {md_escape(fm.get('author',''))} "
                f"| {md_escape(fm.get('date',''))} "
                f"| {status_cell(fm)} "
                f"| {fm.get('word_count','')} "
                f"| [`{fname}`]({folder}/{fname}) |"
            )
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"**{total_docs} documents · ~{total_words:,} words total.**")
    lines.append("")
    lines.append("### Notes")
    lines.append("")
    lines.append(
        "- **`·R`** = converted from `../raw/` (HTML via trafilatura, PDF via "
        "pdftotext, EPUB via pandoc). **`·B`** = extracted from `../TBF/To Be "
        "Free.pdf`. Unmarked docs are the hand-verified religious-freedom core."
    )
    lines.append(
        "- **Dates**: some `../raw/` scrapes carried no reliable date; a spurious "
        "site-default year was blanked rather than recorded wrong. Being filled "
        "during curation."
    )
    lines.append(
        "- **Duplicates**: where the same work appears in more than one "
        "source/format, `possible_duplicate_of` in the frontmatter points at the "
        "canonical version."
    )
    lines.append("")
    lines.append("*This file is generated by `build_readme.py` — do not edit by hand.*")
    lines.append("")

    out = os.path.join(SRC, "README.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {out}: {total_docs} docs across {n} sections, ~{total_words:,} words.")


if __name__ == "__main__":
    main()
