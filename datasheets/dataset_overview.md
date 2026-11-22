# Datasheet: BBO capstone dataset (all eight functions)

This follows the *Datasheets for Datasets* structure (Gebru et al., 2021).
The per-function detail is in `function_N.md`.

## Motivation

**Why was the dataset created?**
To record a sequential black-box optimisation campaign: eight unknown
functions, each to be maximised with one evaluation per week. It serves as
the evidence behind the results, and it makes every decision reproducible.

**Who created it?**
- The supplied designs come from the course.
- The queried points were chosen by the author with the procedure in
  `src/bbo/`.
- The values for the queried points were returned by the course portal.

## Composition

**What do the instances represent?**
Each instance is one evaluation: an input vector `x` in [0, 1]^d and a scalar
output `y`.

**How many instances?**

| Fn | d | Supplied | Queried (graded) | Pending (round 13) | Total graded |
|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 10 | 12 | 1 | 22 |
| 2 | 2 | 10 | 12 | 1 | 22 |
| 3 | 3 | 15 | 12 | 1 | 27 |
| 4 | 4 | 30 | 12 | 1 | 42 |
| 5 | 4 | 20 | 12 | 1 | 32 |
| 6 | 5 | 20 | 12 | 1 | 32 |
| 7 | 6 | 30 | 12 | 1 | 42 |
| 8 | 8 | 40 | 12 | 1 | 52 |
| **All** | | **175** | **96** | **8** | **271** |

**Is anything missing?**
The 8 round-13 results, which had not been returned when the record was
finalised. Their inputs are in `results/query_log.csv` with `observed` left
blank. Nothing else is missing, and no values were imputed.

**Labels and targets**
`y` is the target. There are no other labels.

**Noise**
None. The functions are deterministic: one point queried four times
returned identical values to the last bit (F5, weeks 7, 10, 12 and 13).

**Confidential or personal data**
None. All values are synthetic.

## Collection process

**How was the data acquired?**
- *Supplied design:* given by the course as NumPy arrays, apparently
  space-filling.
- *Queried points:* chosen each week by the procedure described in
  [`model_card.md`](../model_card.md), submitted as a portal string (six
  decimals, clipped to [0.000001, 0.999999]), and returned about 7 days later.

**Sampling strategy**
The queried points are deliberately **not** a random sample. Early queries
spread out to resolve structure. Later queries concentrate near each
function's best point. As a result, the data oversamples the neighbourhood of
each optimum.

**Timeframe**
13 weekly rounds, all graded. The campaign is complete.

## Preprocessing, cleaning and labelling

- **Stored raw.** No point was removed, edited or deduplicated. The
  replicates in F5 are kept on purpose, as the evidence of determinism.
- **Transforms belong to the model, not the data.** `log y` (F5) and
  `log|y|` (F1, early weeks) are applied in `bbo.surrogates.transform` at
  fit time. The stored values are untouched.
- **Rounding.** Query inputs are rounded to six decimals before submission,
  and `observations.csv` stores exactly the inputs that were submitted.

## Uses

**Already used for**
Fitting the GP surrogates and parametric fits that chose every query. Also
for the figures in `reports/figures/` and the analysis in
`notebooks/BBO_results.ipynb`.

**Other suitable uses**
- Benchmarking other optimisers on the same eight functions, for example by
  replaying the campaign from the supplied designs.
- Teaching examples of where GPs fail: needles, structure below the model's
  resolution, and outputs over many orders of magnitude.

**Uses to avoid**
- Training a global regression model of any function without reweighting.
  The sampling is heavily concentrated near the optima.
- Drawing conclusions about the real-world scenarios named in the hints
  ("drug side-effects", "chemical yield"). Those are illustrations only.

## Distribution

The dataset ships with this repository:
- `data/function_N/initial_*.npy`: the supplied data, unmodified.
- `data/function_N/observations.csv`: the queried points.
- `results/query_log.csv`: every submission, including round 13.

The supplied designs remain under the course's terms.

## Maintenance

- **Who maintains it?** The repository author.
- **Round-13 results:** append each value as a final row of
  `data/function_N/observations.csv`, fill in the `observed` column of
  `results/query_log.csv`, then re-run `scripts/make_figures.py` and the
  results notebook.
- **Protected files:** the supplied `.npy` files must never be overwritten.
  `observations.csv` is only ever appended to.
