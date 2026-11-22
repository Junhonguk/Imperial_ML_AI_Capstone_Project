# Datasheet: BBO capstone dataset (all eight functions)

This follows the *Datasheets for Datasets* structure (Gebru et al., 2021).
Per-function detail is in `function_N.md`. This is a snapshot after 9 graded
rounds; the week-10 results are pending.

## Motivation

**Why was the dataset created?**
To record a sequential black-box optimisation campaign: eight unknown
functions, each maximised with one evaluation per week. The record is the
evidence behind the results, and it makes every decision reproducible.

**Who created it?**
- The supplied designs come from the course.
- The queried points were chosen by the author using the procedure in
  `src/bbo/`.
- Their values come back from the course portal.

## Composition

**What do the instances represent?**
One evaluation each: an input vector `x` in [0, 1]^d and a scalar output `y`.

**How many instances?**

| Fn | d | Supplied | Queried (graded) | Pending (week 10) | Total graded |
|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 10 | 9 | 1 | 19 |
| 2 | 2 | 10 | 9 | 1 | 19 |
| 3 | 3 | 15 | 9 | 1 | 24 |
| 4 | 4 | 30 | 9 | 1 | 39 |
| 5 | 4 | 20 | 9 | 1 | 29 |
| 6 | 5 | 20 | 9 | 1 | 29 |
| 7 | 6 | 30 | 9 | 1 | 39 |
| 8 | 8 | 40 | 9 | 1 | 49 |
| **All** | | **175** | **72** | **8** | **247** |

**Is anything missing?**
Only the 8 week-10 results, which have not been returned yet. Their inputs
are in `results/query_log.csv` with `observed` left blank. Nothing has been
imputed.

**Labels and targets**
`y` is the target. There are no other labels.

**Noise**
Function 2 is treated as noisy, with measured noise sd of about 0.06. The
other functions are fitted as noise-free.

The week-10 F5 query repeats an earlier point exactly, so its result will
also test whether repeat readings are identical.

**Confidential or personal data**
None. All values are synthetic.

## Collection process

**How was the data acquired?**
- *Supplied design:* given by the course as NumPy arrays, and apparently
  space-filling.
- *Queried points:* chosen each week by the procedure in
  [`model_card.md`](../model_card.md). Each is submitted as a portal string
  (six decimals, clipped to [0.000001, 0.999999]), and the result comes back
  about 7 days later.

**Sampling strategy**
The queried points are deliberately **not** a random sample. Early queries
spread out to resolve structure, and later queries concentrate near each
function's best point. The data therefore oversamples the neighbourhood of
each optimum.

**Timeframe**
Weekly rounds. Weeks 1–9 are graded and week 10 is pending, out of a
13-week campaign.

## Preprocessing, cleaning and labelling

- **Raw storage.** Everything is stored raw. No point has been removed,
  edited or deduplicated.
- **Transforms belong to the model, not the data.** `log y` (F5) and
  `log|y|` (F1) are applied in `bbo.surrogates.transform` at fit time.
- **Rounding.** Query inputs are rounded to six decimals before submission,
  and `observations.csv` stores exactly the inputs that were submitted.

## Uses

**Current uses**
- Fitting the GP surrogates and parametric fits that choose each query.
- The figures in `reports/figures/`.
- `notebooks/BBO_results.ipynb`.

**Other suitable uses**
- Benchmarking other optimisers on the same eight functions.
- Teaching examples of where GPs struggle: needle-shaped peaks, noisy
  functions, and outputs spanning orders of magnitude.

**Uses to avoid**
- **Training a global regression model without reweighting.** The sampling
  is heavily concentrated near the optima.
- **Drawing conclusions about the scenarios named in the hints.** "Drug
  side-effects", "chemical yield" and the like are illustrations only.

## Distribution

The data ships with this repository:
- `data/function_N/initial_*.npy`: the supplied data, unmodified.
- `data/function_N/observations.csv`: the queried points.
- `results/query_log.csv`: every submission.

The supplied designs remain under the course's terms.

## Maintenance

**Maintainer:** the repository author.

**Each week:**
1. Append each result as a new row of `data/function_N/observations.csv`.
2. Fill in the `observed` column of `results/query_log.csv`.
3. Re-run `scripts/make_figures.py` and the results notebook.

The supplied `.npy` files must never be overwritten, and `observations.csv`
is append-only.
