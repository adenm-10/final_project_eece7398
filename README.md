# RoCktNet Extension: datasets

Datasets for EECE7398 Final Project Topic 1: Part A (analog circuit paper → JSON design task) and Part B Option 1 (block diagram → graph).

## Contents

| Path | Description |
|---|---|
| `output_specs.md` | The assignment's stated requirements for both parts, and the proposed JSON output schema for each |
| `datasets/intro/` | Pilot set: 10 Part A papers, 10 Part B diagrams |
| `datasets/full/` | Full set: 30 Part A papers, 29 Part B diagrams (3 papers in both). Contains every intro item |
| `scripts/ingest_pdfs.py` | Lists, opens, and files downloaded paper PDFs into the datasets |
| `scripts/extract_figure.py` | Saves a Part B figure from a PDF as a PNG |

## Dataset folders

| Path | Description |
|---|---|
| `papers.csv` | One row per source |
| `README.txt` | What the set contains |
| `pdfs/<paper_id>.pdf` | Paper PDFs |
| `figures/<paper_id>_fig.png` | The Part B figure for each Part B row |

## `papers.csv` columns

| Column | Description |
|---|---|
| `paper_id` | IEEE article number (RoCktNet id); `ieee_<number>` for handout example papers; a DOI suffix for papers without one; `handout_fig1a/b` for the handout figures |
| `part` | `A`, `B`, or `A+B` |
| `title`, `year`, `venue`, `doi`, `link` | Bibliographic data |
| `circuit_type` | Circuit class, from the schema enum in `output_specs.md` |
| `circuit_subtype` | Finer description of the circuit |
| `part_a_tier` | `pilot`, `core`, `stretch`, or `anchor (handout)` (increasing difficulty of spec extraction) |
| `part_b_figure` | Figure number used for Part B |
| `part_b_pdf_page` | PDF page of that figure (1-indexed) |
| `part_b_caption` | Figure caption |
| `part_b_topology` | Graph structure the figure exercises (chain, feedback loop, fan-out, boundary, ...) |
| `part_b_difficulty` | `T1-simple` (≤ 6 blocks, clear flow), `T2-medium` (loops, fan-out, or one boundary), `T3-hard` (dense, nested, many pins, or component-level) |
| `part_b_style` | `box` (blocks only) or `hybrid` (blocks mixed with component symbols) |
| `selection_notes` | Why the source was selected |
| `pdf_file`, `pdf_status`, `pdf_note` | PDF path, `present` / `needs_download`, and where it came from |
| `figure_file` | Path of the extracted Part B figure |
| `check_status` | Result of the manual check: `pass`, `pass_note`, `moved` (re-tiered), `rejected`, `unchecked` |
| `check_note` | What the manual check found |
| `in_intro`, `backup` | `full` only: item is in the intro set / item was an intro replacement candidate |

## Scripts

```bash
python3 scripts/ingest_pdfs.py list                    # papers still missing a PDF
python3 scripts/ingest_pdfs.py open   --proxy "https://ezproxy.neu.edu/login?url="
python3 scripts/ingest_pdfs.py ingest --move           # file PDFs from ~/Downloads into both datasets

python3 scripts/extract_figure.py <paper_id> <page>              # list images on a page
python3 scripts/extract_figure.py <paper_id> <page> --index N    # save one
python3 scripts/extract_figure.py <paper_id> <page> --crop x,y,w,h   # vector figures
```
Requires poppler-utils and Pillow.

## Status
`full/` has 55 of 56 PDFs; `lmwc.2010.2056675` is missing. Every other row has been checked by hand.

## Note
The PDFs are copyrighted IEEE papers. Keep `datasets/*/pdfs/*.pdf` out of any public repository; the DOIs and links in `papers.csv` reproduce the set.
