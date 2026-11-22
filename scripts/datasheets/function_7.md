# Datasheet: Function 7 (6D)

*BBO capstone. This record is final at 12 graded queries; the round-13 query has been submitted and its result is pending.*
*Every number on this page comes from `data/function_7/` and `results/query_log.csv` (sheets generated, then checked against the data).*

---

## 1. Function overview

**Which function is this?**
Function 7, with description hint: *hyperparameter surface*.

**Input dimension and domain**
6D, the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
30: `initial_inputs.npy` with shape (30, 6) and `initial_outputs.npy` with shape (30,).

**What does the output represent?**
A validation-style score. Higher is better.

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^6. The supplied outputs range from 0.002701 to 1.365 (median 0.07863). The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x6,y`). There are 42 observations in total (30 supplied + 12 queried).

**How the data changed over the campaign**
One point per week. The supplied design is space-filling, the early queries are spread out (corners, faces, global EI), and the later queries are concentrated within about 0.01-0.05 of the incumbent. The final dataset is therefore dense around the best point and sparse elsewhere. That suits maximisation but makes it a biased sample of the function as a whole.

**Noise and randomness**
Deterministic (campaign-wide replicate).

**Shape of the function, as observed**
Mostly near zero (median of the supplied data 0.079), with one sharp ridge near the x1 = 0 face. Every one of the remaining five inputs has a clear interior optimum (final GP slices).

## 3. Optimisation strategy

**Methods used**
GP + EI (weeks 1-3); a trust region with capped lengthscales (week 4 onward), ending with half-width 0.008 and cap 2.0.

**Why these methods**
Week 1 nearly doubled the supplied best (1.365 to 2.42) by moving onto the x1 = 0 face. ARD then declared one input irrelevant. The week-2 test of that verdict returned 1.18, refuting it. Weeks 2-3 showed that moving several inputs at once on a sharp ridge loses value, so the trust region was adopted first on this function.

**Final regime** (`src/bbo/config.py`)
`trust_region`. best 2.8093; plateau cracked twice by tightening.

## 4. Data handling and preprocessing

- Raw outputs. x1 held at 0.000001 from week 1. Lengthscales capped.
- Inputs are not rescaled: the domain is already [0, 1]^6.
- No points were removed or edited. Points that turned out to be bad are kept, because they constrain the surrogate.
- Every query was checked with `bbo.data.validate` before submission (dimension, six decimals, inside (0, 1)).

## 5. Weekly iteration and learning

Records in weeks 4, 6 and 7, followed by a plateau (2.766-2.770 in weeks 8-10). Shrinking the box broke it in week 11 (2.8093). The prediction for the 4th record (week 7) was nearly exact: 2.799 predicted, 2.7945 observed.

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
| 10 | `0.000001-0.165421-0.483617-0.274693-0.302544-0.712794` | 2.768993956 |  |
| 11 | `0.000001-0.157587-0.463617-0.293731-0.319323-0.685665` | 2.809329987 | yes |
| 12 | `0.000001-0.152547-0.478617-0.307971-0.317994-0.686451` | 2.79302872 |  |
| 13 | `0.000001-0.150045-0.470479-0.285731-0.317670-0.677665` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best 2.8093300 at (0.000001, 0.157587, 0.463617, 0.293731, 0.319323, 0.685665), week 11. Week 13 is a trust-region step; the driver predicts 2.820 ± 0.004.

| Supplied best | Final best | Gain | Best point (week) |
|---:|---:|---:|---|
| 1.364968304 | 2.809329987 | +1.444 | `0.000001-0.157587-0.463617-0.293731-0.319323-0.685665` (week 11) |

The surrogate at campaign end: [`reports/figures/surrogate_F7.png`](../reports/figures/surrogate_F7.png).

## 7. Ethical and practical considerations

- As a stand-in for hyperparameter tuning: chasing the 4th decimal of a validation score is classic overfitting to the validation set. In real use, these final gains would need confirming on held-out data.
- **Provenance.** The function and its supplied data come from the course; the true formula is unknown. Scenario descriptions are illustrations, not claims about real systems.
- **Reuse.** This dataset is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
