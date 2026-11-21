#!/usr/bin/env python3
"""Download helper for the paper PDFs listed in datasets/full/papers.csv.

  python scripts/ingest_pdfs.py list   [--only ID,ID]   print the papers that still need a PDF
  python scripts/ingest_pdfs.py open   [--only ID,ID]   open each of them in the browser
  python scripts/ingest_pdfs.py ingest [--only ID,ID]   match PDFs in ~/Downloads to papers and copy them in

`ingest` matches a PDF to a paper by comparing its first two pages with the paper's title,
so downloaded file names do not matter. It updates both datasets/full and datasets/intro.
Requires pdftotext (poppler-utils).
"""
import argparse, csv, os, re, shutil, subprocess, unicodedata, webbrowser
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "datasets"


def read_csv(dataset):
    with open(DATA / dataset / "papers.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(dataset, rows):
    with open(DATA / dataset / "papers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def missing_papers(only):
    return [r for r in read_csv("full")
            if r["pdf_status"] != "present" and (not only or r["paper_id"] in only)]


def pdf_url(row, proxy):
    # ids like "1253849" or "ieee_10398190" are IEEE article numbers; others use the DOI link
    m = re.fullmatch(r"(?:ieee_)?(\d{5,})", row["paper_id"])
    url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber={m.group(1)}" if m else row["link"]
    return proxy + url


def word_pairs(text):
    """Set of consecutive word pairs; pairs are far more distinctive than single words."""
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"-\s*\n\s*", "", text)  # rejoin words hyphenated across lines
    words = [w for w in re.sub(r"[^a-z0-9]+", " ", text).split() if len(w) > 1]
    return set(zip(words, words[1:]))


def first_pages_text(pdf):
    result = subprocess.run(["pdftotext", "-l", "2", str(pdf), "-"], capture_output=True, text=True)
    return result.stdout


def cmd_list(only, proxy):
    papers = missing_papers(only)
    print(f"{len(papers)} papers need a PDF\n")
    for r in papers:
        print(f"{r['paper_id']}  (part {r['part']})\n  {r['title']}\n  {pdf_url(r, proxy)}\n")


def cmd_open(only, proxy):
    papers = missing_papers(only)
    devnull = os.open(os.devnull, os.O_WRONLY)
    saved = os.dup(2)
    os.dup2(devnull, 2)  # hide the browser's harmless startup warnings
    try:
        for r in papers:
            webbrowser.open_new_tab(pdf_url(r, proxy))
    finally:
        os.dup2(saved, 2)
    print(f"Opened {len(papers)} tabs. Save each PDF into ~/Downloads, then run: ingest")


def cmd_ingest(only, downloads, dry_run, move):
    titles = {r["paper_id"]: word_pairs(r["title"]) for r in missing_papers(only)}
    found = {}  # paper_id -> downloaded file

    newest_first = sorted(Path(downloads).expanduser().glob("*.pdf"), key=lambda p: -p.stat().st_mtime)
    for pdf in newest_first:
        with open(pdf, "rb") as f:
            if f.read(5) != b"%PDF-":
                print(f"skip, not a PDF (probably a login page): {pdf.name}")
                continue
        text = word_pairs(first_pages_text(pdf))
        scores = sorted(((len(pairs & text) / max(len(pairs), 1), pid)
                         for pid, pairs in titles.items() if pid not in found), reverse=True)
        if not scores:
            break
        best, pid = scores[0]
        runner_up = scores[1][0] if len(scores) > 1 else 0
        if best >= 0.7 and best - runner_up >= 0.3:  # accept only a clear winner
            found[pid] = pdf
            print(f"match {best:.2f}  {pdf.name}  ->  {pid}")

    if not dry_run:
        for dataset in ("full", "intro"):
            rows = read_csv(dataset)
            for r in rows:
                if r["paper_id"] in found:
                    shutil.copy2(found[r["paper_id"]], DATA / dataset / "pdfs" / f"{r['paper_id']}.pdf")
                    r["pdf_status"] = "present"
                    r["pdf_note"] = "IEEE Xplore (NEU library)"
            write_csv(dataset, rows)
        if move:
            for pdf in found.values():
                pdf.unlink()

    left = [pid for pid in titles if pid not in found]
    print(f"\n{len(found)} ingested{' (dry run)' if dry_run else ''}; still missing: {', '.join(left) or 'none'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["list", "open", "ingest"])
    ap.add_argument("--only", help="comma-separated paper_ids")
    ap.add_argument("--proxy", default="", help='library proxy prefix, e.g. "https://ezproxy.neu.edu/login?url="')
    ap.add_argument("--downloads", default="~/Downloads")
    ap.add_argument("--dry-run", action="store_true", help="show matches without copying")
    ap.add_argument("--move", action="store_true", help="delete matched files from the downloads folder")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None

    if a.command == "list":
        cmd_list(only, a.proxy)
    elif a.command == "open":
        cmd_open(only, a.proxy)
    else:
        cmd_ingest(only, a.downloads, a.dry_run, a.move)


if __name__ == "__main__":
    main()
