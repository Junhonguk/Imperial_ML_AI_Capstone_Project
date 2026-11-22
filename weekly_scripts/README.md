# Weekly derivation scripts

One consolidated script per campaign phase, reconstructing how each week's
submitted queries were derived (the full per-week standalone scripts were
delivered during the weekly sessions; these are the canonical versions).

- `derive_standard.py`  - the GP + EI loop used from week 1 (full-domain EI,
  per-function transforms and noise terms, per-function exploration margin).
- `derive_trust_region.py` - the boxed/capped variant adopted from week 4
  (F7), week 5 (F4, F8), week 6 (F6), with grow/shrink rules.
- `derive_triangulation.py` - the parametric path: F1 source location
  (log-magnitude, weeks 1-2), F1/F4 near-peak value fits (weeks 7+),
  final 1D parabola steps (weeks 11-13).

Every submitted query and its result is in ../results/query_log.csv;
data snapshots per week are reproducible by truncating
../data/function_N/observations.csv to the first N rows.
