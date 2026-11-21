INTRO DATASET
Pilot set for running both pipelines end to end. Every item is also in ../full/.

20 rows: 10 Part A papers + 10 Part B diagrams. All checked by hand (check_status, check_note).
19 PDFs (the handout PDF holds both handout figures), 10 figures.

Part A
  5 circuit types x 2 papers: op-amp, LDO, bandgap, LNA, TIA
  each paper proposes one circuit block and reports its specs in the abstract and a summary/comparison table
  2 pass_note: 1214729 (table covers 2 designs), 1302265 (confirm which TIA is the proposed one)

Part B
  6 T1-simple, 4 T2-medium; 7 box, 3 hybrid
  few blocks, arrowheads or obvious flow, at most one boundary
  4 contain feedback loops: 1233753, 1004575, 1158777, 1233754
  handout_fig1a has official ground truth; handout_fig1b is the closest match to the course test style
  figures/ holds each figure at native resolution, black on white

Sources: RoCktNet paper set (github.com/xz-group/RoCktNet), 2001-2012 IEEE papers, plus the course handout.
