#!/usr/bin/env python3
"""Documentation quality checks for the Valtoryn repository (stdlib only).

Checks performed:
  * every relative Markdown link resolves to an existing file (and heading anchor, if given);
  * every source citation like [R03-S07] used anywhere in the docs has a row in a research
    document's Sources table, and no research document defines the same ID twice;
  * every Sources-table row is cited at least once (warning only);
  * research documents carry the required status header and the evidence legend;
  * optional (--external): every URL listed in a Sources table responds (HTTP errors are
    reported; 401/403/429/999 are reported as "blocked" warnings because many sites reject
    automated clients, which does not prove the URL is wrong);
  * optional (--build-sources): regenerate docs/references/SOURCES.md from the Sources tables.

Usage:
  python tools/check_docs.py                  # structural checks
  python tools/check_docs.py --external       # plus URL reachability
  python tools/check_docs.py --build-sources  # regenerate docs/references/SOURCES.md, then check

Exit status is non-zero if any error (not warning) is found.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESEARCH_DIR = ROOT / "docs" / "research"
SOURCES_MD = ROOT / "docs" / "references" / "SOURCES.md"

CITE_RE = re.compile(r"\bR\d{2}-S\d{2,3}\b")
ROW_RE = re.compile(r"^\|\s*(R\d{2}-S\d{2,3})\s*\|(.*)\|\s*$")
LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
URL_RE = re.compile(r"https?://[^\s<>)\]|]+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
REQUIRED_RESEARCH_MARKERS = ["**Status:**", "[FACT]", "[REC]", "[UNRESOLVED]"]


def md_files() -> list[Path]:
    skip = {".git", "node_modules", "scratch", "tmp"}
    out = []
    for p in ROOT.rglob("*.md"):
        if any(part in skip for part in p.relative_to(ROOT).parts):
            continue
        out.append(p)
    return sorted(out)


def slugify(heading: str) -> str:
    """Approximate GitHub's heading-anchor algorithm."""
    s = re.sub(r"[`*_]", "", heading.strip().lower())
    s = re.sub(r"[^\w\- ]", "", s, flags=re.UNICODE)
    return s.replace(" ", "-")


def anchors_of(path: Path) -> set[str]:
    seen: dict[str, int] = {}
    out: set[str] = set()
    in_code = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = HEADING_RE.match(line)
        if m:
            slug = slugify(m.group(2))
            n = seen.get(slug, 0)
            seen[slug] = n + 1
            out.add(slug if n == 0 else f"{slug}-{n}")
    return out


def strip_code(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def parse_sources() -> tuple[dict[str, dict], list[str]]:
    """Return ({id: row-dict}, errors) from all research docs' Sources tables."""
    rows: dict[str, dict] = {}
    errors: list[str] = []
    for p in sorted(RESEARCH_DIR.glob("*.md")) if RESEARCH_DIR.exists() else []:
        for line in p.read_text(encoding="utf-8").splitlines():
            m = ROW_RE.match(line)
            if not m:
                continue
            sid = m.group(1)
            cells = [c.strip() for c in ("| " + m.group(2)).split("|")[1:]]
            if len(cells) != 6:
                errors.append(f"{p.relative_to(ROOT)}: row {sid} has {len(cells)} cells after the ID, expected 6")
                continue
            if sid in rows:
                errors.append(f"{p.relative_to(ROOT)}: duplicate source ID {sid} (also in {rows[sid]['file']})")
                continue
            url_m = URL_RE.search(cells[2])
            rows[sid] = {
                "id": sid, "file": str(p.relative_to(ROOT)), "title": cells[0], "org": cells[1],
                "url": url_m.group(0).rstrip(".,;") if url_m else "", "date": cells[3],
                "accessed": cells[4], "supports": cells[5],
            }
            if not rows[sid]["url"]:
                errors.append(f"{p.relative_to(ROOT)}: source {sid} has no URL")
    return rows, errors


def check_links(files: list[Path]) -> list[str]:
    errors = []
    anchor_cache: dict[Path, set[str]] = {}
    for f in files:
        text = strip_code(f.read_text(encoding="utf-8"))
        for target in LINK_RE.findall(text):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):  # http:, mailto:, etc.
                continue
            path_part, _, frag = target.partition("#")
            dest = (f.parent / path_part).resolve() if path_part else f
            if not dest.exists():
                errors.append(f"{f.relative_to(ROOT)}: broken link -> {target}")
                continue
            if frag and dest.suffix == ".md":
                anchors = anchor_cache.setdefault(dest, anchors_of(dest))
                if frag.lower() not in anchors:
                    errors.append(f"{f.relative_to(ROOT)}: missing anchor -> {target}")
    return errors


def check_citations(files: list[Path], rows: dict[str, dict]) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    cited: set[str] = set()
    for f in files:
        if f == SOURCES_MD:
            continue
        for line in strip_code(f.read_text(encoding="utf-8")).splitlines():
            if ROW_RE.match(line):
                continue  # definition row, not a citation (code examples are ignored too)
            for sid in CITE_RE.findall(line):
                cited.add(sid)
                if sid not in rows:
                    errors.append(f"{f.relative_to(ROOT)}: citation {sid} has no Sources-table row")
    for sid in sorted(set(rows) - cited):
        warnings.append(f"{rows[sid]['file']}: source {sid} is listed but never cited")
    return errors, warnings


def check_research_structure() -> list[str]:
    errors = []
    for p in sorted(RESEARCH_DIR.glob("*.md")) if RESEARCH_DIR.exists() else []:
        text = p.read_text(encoding="utf-8")
        for marker in REQUIRED_RESEARCH_MARKERS:
            if marker not in text:
                errors.append(f"{p.relative_to(ROOT)}: missing required marker {marker!r}")
        if "## Sources" not in text and "## 9. Sources" not in text and not re.search(r"^## .*Sources\b", text, re.M):
            errors.append(f"{p.relative_to(ROOT)}: no 'Sources' section")
    return errors


def build_sources(rows: dict[str, dict]) -> None:
    by_file: dict[str, list[dict]] = {}
    for r in rows.values():
        by_file.setdefault(r["file"], []).append(r)
    out = [
        "# Consolidated source register",
        "",
        "> **Status:** Generated file. Do not edit by hand: run `python tools/check_docs.py --build-sources`.",
        "> Each row is a source that was opened and read for the cited research document. "
        "Source IDs are unique across the repository and are cited inline as `[Rxx-Syy]`.",
        "> The \"Accessed\" column is the date the source was inspected. Publication/revision dates are copied from the "
        "source page where one was visible; \"n/a\" means none was visible.",
        "",
        f"Total sources: **{len(rows)}** across **{len(by_file)}** research documents.",
        "",
    ]
    for fname in sorted(by_file):
        lst = sorted(by_file[fname], key=lambda r: r["id"])
        rel = Path(fname).relative_to("docs").as_posix()
        out += [f"## {rel[len('research/'):] if rel.startswith('research/') else rel} ({len(lst)} sources)", "",
                f"Defined in [{fname}](../{rel}).", "",
                "| ID | Title | Organization / author | URL | Published / revision date | Accessed | What it supports |",
                "|---|---|---|---|---|---|---|"]
        for r in lst:
            out.append(f"| {r['id']} | {r['title']} | {r['org']} | {r['url']} | {r['date']} | {r['accessed']} | {r['supports']} |")
        out.append("")
    SOURCES_MD.parent.mkdir(parents=True, exist_ok=True)
    SOURCES_MD.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"wrote {SOURCES_MD.relative_to(ROOT)} ({len(rows)} sources)")


def probe(url: str) -> tuple[str, str, str]:
    hdrs = {"User-Agent": "valtoryn-docs-linkcheck/1.0 (+https://github.com/valtoryn/warehouse-robotics)"}
    last = ""
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                return url, "ok", str(resp.status)
        except urllib.error.HTTPError as e:
            last = str(e.code)
            if e.code in (401, 403, 429, 999):
                return url, "blocked", last
            if method == "HEAD" and e.code in (400, 404, 405, 501):
                continue  # some servers mishandle HEAD; retry with GET
            return url, "error", last
        except Exception as e:  # noqa: BLE001 - network errors of any kind
            last = type(e).__name__ + ": " + str(e)[:80]
            if method == "HEAD":
                continue
    return url, "error", last


def check_external(rows: dict[str, dict]) -> tuple[list[str], list[str]]:
    urls = sorted({r["url"] for r in rows.values() if r["url"]})
    errors, warnings = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        for url, status, detail in ex.map(probe, urls):
            if status == "error":
                ids = ",".join(r["id"] for r in rows.values() if r["url"] == url)
                errors.append(f"URL check failed ({detail}): {url}  [{ids}]")
            elif status == "blocked":
                warnings.append(f"URL blocked automated check ({detail}), verify manually: {url}")
    print(f"checked {len(urls)} unique URLs")
    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--external", action="store_true", help="also check that source URLs respond")
    ap.add_argument("--build-sources", action="store_true", help="regenerate docs/references/SOURCES.md")
    args = ap.parse_args()

    rows, errors = parse_sources()
    warnings: list[str] = []
    if args.build_sources:
        build_sources(rows)
    files = md_files()
    errors += check_links(files)
    e, w = check_citations(files, rows)
    errors += e
    warnings += w
    errors += check_research_structure()
    if args.external:
        e, w = check_external(rows)
        errors += e
        warnings += w

    for w in warnings:
        print("WARNING:", w)
    for e in errors:
        print("ERROR:  ", e)
    print(f"{len(files)} markdown files, {len(rows)} sources, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
