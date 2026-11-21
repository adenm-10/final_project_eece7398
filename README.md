# RoCktNet Extension

Datasets for EECE7398 Final Project Topic 1: Part A (analog circuit paper → JSON design task) and Part B Option 1 (block diagram → graph).

| Path | Purpose |
|---|---|
| `output_specs.md` | The assignment's requirements for both parts and the proposed JSON output schema for each |
| `datasets/` | Paper sets the pipelines run on |
| `datasets/intro/` | Pilot set (10 Part A papers, 10 Part B diagrams) for bringing both pipelines up end to end |
| `datasets/full/` | Full set (30 Part A papers, 29 Part B diagrams), including every intro item |
| `datasets/*/papers.csv` | One row per source: bibliographic data, circuit type, Part B figure and difficulty, manual-check result |
| `datasets/*/README.txt` | Summary of what the set contains |
| `datasets/*/pdfs/` | Paper PDFs, named `<paper_id>.pdf` |
| `datasets/*/figures/` | Extracted Part B figures, named `<paper_id>_fig.png` |
| `scripts/` | Tools used to build the datasets |
| `scripts/ingest_pdfs.py` | Lists papers missing a PDF, opens them in the browser, and files downloaded PDFs into the datasets |
| `scripts/extract_figure.py` | Saves a Part B figure from a paper PDF as a PNG |
