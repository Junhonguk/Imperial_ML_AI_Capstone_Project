# Datasheet: Function 7 (6D)

*BBO capstone. Snapshot after 9 graded queries. The week-10 query has been submitted and its result is pending.*
*All numbers come from `data/function_7/` and `results/query_log.csv`.*

---

## 1. Function overview

**Which function?**
Function 7. Description hint: *hyperparameter surface*.

**Input dimension and domain**
6D, on the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
30 points: `initial_inputs.npy` has shape (30, 6) and `initial_outputs.npy` has shape (30,).

**What does the output represent?**
A validation-style score. Higher is better.

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^6. Supplied outputs range from 0.002701 to 1.365, with median 0.07863.

The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x6,y`). There are 39 observations so far: 30 supplied and 9 queried.

**How the data evolves**
One point is added per week. The supplied design is space-filling. Early queries spread out (corners, faces, global EI), and later queries cluster within about 0.01–0.08 of the incumbent.

The dataset is therefore becoming dense around the best point and stays sparse elsewhere. That is the right allocation for maximisation, but it makes the data a biased sample of the function as a whole.

**Noise and randomness**
Treated as noise-free.

**Observed shape**
Mostly near zero (supplied median 0.079), with one sharp ridge next to the x1 = 0 face.

## 3. Optimisation strategy

**Methods used**
GP + EI in weeks 1–3. From week 4, a trust region with capped lengthscales, now with half-width 0.04, cap 2.0 and ξ = 0.002.

**Why these methods**
Week 1 nearly doubled the supplied best, from 1.365 to 2.42, by moving onto the x1 = 0 face. ARD then declared one input irrelevant. Week 2 tested that verdict and got 1.18, which reversed it. Weeks 2–3 showed that moving several inputs at once on a sharp ridge loses value, so F7 was the first function to get a trust region.

**Current regime** (`src/bbo/config.py`)
`trust_region`. plateau 2.79 after 4 records.

## 4. Data handling and preprocessing

- Raw outputs. x1 held at 0.000001 since week 1. Lengthscales capped.
- Inputs are not rescaled, because the domain is already [0, 1]^6.
- No points have been removed or edited. Bad points are kept, because they constrain the surrogate.
- Every query is checked with `bbo.data.validate` before submission: dimension, six decimals, and inside (0, 1).

## 5. Weekly iteration and learning

Records came in weeks 4, 6 and 7. The prediction for the week-7 record was nearly exact: 2.799 predicted, 2.7945 observed. Weeks 8–9 plateaued at 2.766–2.770.

| Week | Query (portal string) | Observed | Record? |
|---:|---|---:|:---:|
| 1 | `0.000001-0.176669-0.455943-0.215068-0.373093-0.750100` | 2.419503794 | yes |
| 2 | `0.000001-0.089791-0.505415-0.036984-0.360282-0.873867` | 1.175529736 |  |
| 3 | `0.000001-0.080722-0.381326-0.000001-0.381189-0.747101` | 1.220995933 |  |
| 4 | `0.000001-0.144836-0.493854-0.253681-0.360242-0.729982` | 2.621573656 | yes |
| 5 | `0.000001-0.086725-0.544529-0.290773-0.353476-0.715675` | 2.615233144 |  |
| 6 | `0.000001-0.141715-0.495743-0.272220-0.335230-0.706289` | 2.762466682 | yes |
| 7 | `0.000001-0.173591-0.443617-0.288725-0.314743-0.691965` | 2.794472623 | yes |
| 8 | `0.000001-0.171773-0.563617-0.270253-0.320534-0.648690` | 2.770098217 |  |
| 9 | `0.000001-0.144271-0.383617-0.265099-0.310928-0.673297` | 2.766417367 |  |
| 10 | `0.000001-0.165421-0.483617-0.274693-0.302544-0.712794` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best is 2.7944726 at (0.000001, 0.173591, 0.443617, 0.288725, 0.314743, 0.691965), week 7. The week-10 query is a trust-region step, and the driver predicts 2.781 ± 0.041.

| Supplied best | Best after week 9 | Gain | Best point (week) |
|---:|---:|---:|---|
| 1.364968304 | 2.794472623 | +1.43 | `0.000001-0.173591-0.443617-0.288725-0.314743-0.691965` (week 7) |

The surrogate behind the week-10 query is plotted in [`reports/figures/surrogate_F7.png`](../reports/figures/surrogate_F7.png).

## 7. Ethical and practical considerations

- As a hyperparameter-tuning analogy: chasing the third decimal of a validation score is classic overfitting to the validation set. Gains like that would need confirming on held-out data.
- **Provenance.** The function and its supplied data come from the course, and the true formula is unknown. The scenario hints are illustrations, not claims about real systems.
- **Reuse.** The data is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
