# Datasheet: Function 5 (4D)

*BBO capstone. Snapshot after 9 graded queries. The week-10 query has been submitted and its result is pending.*
*All numbers come from `data/function_5/` and `results/query_log.csv`.*

---

## 1. Function overview

**Which function?**
Function 5. Description hint: *chemical yield (log-scale)*.

**Input dimension and domain**
4D, on the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
20 points: `initial_inputs.npy` has shape (20, 4) and `initial_outputs.npy` has shape (20,).

**What does the output represent?**
A positive yield spanning five orders of magnitude (0.11 to 8662).

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^4. Supplied outputs range from 0.1129 to 1089, with median 63.95.

The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x4,y`). There are 29 observations so far: 20 supplied and 9 queried.

**How the data evolves**
One point is added per week. The supplied design is space-filling. Early queries spread out (corners, faces, global EI), and later queries cluster within about 0.01–0.08 of the incumbent.

The dataset is therefore becoming dense around the best point and stays sparse elsewhere. That is the right allocation for maximisation, but it makes the data a biased sample of the function as a whole.

**Noise and randomness**
Treated as noise-free. The week-10 query repeats the corner exactly, so its result also tests whether repeat readings are identical.

**Observed shape**
Unimodal and increasing toward the (1, 1, 1, 1) corner, close to log-linear in each input, with interactions between inputs.

## 3. Optimisation strategy

**Methods used**
GP + EI on log(y), following the trend to the corner in weeks 1–7. Then probes stepping back from the corner along single inputs (weeks 8–9). Now `bank`.

**Why these methods**
On the raw scale a GP is dominated by the few large values. On log y the surface is smooth and close to linear, and EI follows the trend. A corner proposal in week 5 was refused as uncertainty-bait, because its mean was below the incumbent. It was re-admitted once evidence lifted its mean above the incumbent, and in week 7 it returned 8662, a 44% gain.

**Current regime** (`src/bbo/config.py`)
`bank`. corner is the max; 3 interaction probes all lost.

## 4. Data handling and preprocessing

- Output transform `log(y)`; all outputs are positive.
- Inputs are not rescaled, because the domain is already [0, 1]^4.
- No points have been removed or edited. Bad points are kept, because they constrain the surrogate.
- Every query is checked with `bbo.data.validate` before submission: dimension, six decimals, and inside (0, 1).

## 5. Weekly iteration and learning

The single-input step-backs in the log lost value each time: x2 at 0.85 gave 6495, and x3 at 0.90 gave 7073. The x1 direction was covered by the climb in weeks 5–6 (x1 = 0.4 gave 4540; 0.8 gave 6028). The corner is therefore treated as the maximum in the box.

| Week | Query (portal string) | Observed | Record? |
|---:|---|---:|:---:|
| 1 | `0.000001-0.581912-0.882310-0.999999` | 1095.325078 | yes |
| 2 | `0.000001-0.014008-0.197475-0.999999` | 192.0910178 |  |
| 3 | `0.000001-0.824963-0.999999-0.999999` | 2767.770191 | yes |
| 4 | `0.000001-0.999999-0.999999-0.999999` | 4440.480874 | yes |
| 5 | `0.400000-0.999999-0.999999-0.999999` | 4540.337719 | yes |
| 6 | `0.800000-0.999999-0.999999-0.999999` | 6027.724406 | yes |
| 7 | `0.999999-0.999999-0.999999-0.999999` | 8662.405001 | yes |
| 8 | `0.999999-0.850000-0.999999-0.999999` | 6495.031574 |  |
| 9 | `0.999999-0.999999-0.900000-0.999999` | 7073.392997 |  |
| 10 | `0.999999-0.999999-0.999999-0.999999` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best is 8662.405001 at (1, 1, 1, 1), clipped to 0.999999, week 7. The week-10 query re-queries the corner to bank it.

| Supplied best | Best after week 9 | Gain | Best point (week) |
|---:|---:|---:|---|
| 1088.859618 | 8662.405001 | +7574 | `0.999999-0.999999-0.999999-0.999999` (week 7) |

The surrogate behind the week-10 query is plotted in [`reports/figures/surrogate_F5.png`](../reports/figures/surrogate_F5.png).

## 7. Ethical and practical considerations

- Running a real process at the corner of its allowed operating box would deserve a safety review: the optimum may lie beyond the stated limits, and the model knows nothing outside the box.
- **Provenance.** The function and its supplied data come from the course, and the true formula is unknown. The scenario hints are illustrations, not claims about real systems.
- **Reuse.** The data is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
