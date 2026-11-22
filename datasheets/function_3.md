# Datasheet: Function 3 (3D)

*BBO capstone. Snapshot after 9 graded queries. The week-10 query has been submitted and its result is pending.*
*All numbers come from `data/function_3/` and `results/query_log.csv`.*

---

## 1. Function overview

**Which function?**
Function 3. Description hint: *drug side-effects (outputs <= 0)*.

**Input dimension and domain**
3D, on the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
15 points: `initial_inputs.npy` has shape (15, 3) and `initial_outputs.npy` has shape (15,).

**What does the output represent?**
Negated side-effect severity. Every reading is <= 0, and closer to 0 is better.

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^3. Supplied outputs range from -0.3989 to -0.03484, with median -0.106.

The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x3,y`). There are 24 observations so far: 15 supplied and 9 queried.

**How the data evolves**
One point is added per week. The supplied design is space-filling. Early queries spread out (corners, faces, global EI), and later queries cluster within about 0.01–0.08 of the incumbent.

The dataset is therefore becoming dense around the best point and stays sparse elsewhere. That is the right allocation for maximisation, but it makes the data a biased sample of the function as a whole.

**Noise and randomness**
Treated as noise-free. Readings within about 0.12 of the best point are 0.005–0.022 below it, which reflects how sharp the spike is.

**Observed shape**
Mostly smooth, and strongly negative toward the corners (down to -0.40). There is a narrow spike near (0.484, 0.760, 0.488) where readings approach 0.

## 3. Optimisation strategy

**Methods used**
GP + EI over the full domain with corner sweeps in weeks 1–4. From week 5, local EI refinement. Now a trust region of half-width 0.03 with ξ = 0.002.

**Why these methods**
With 15 points in 3D, the early EI proposals went to corners. All four corner probes returned between -0.06 and -0.18, which ruled them out. In week 5 an EI tie was broken in favour of a local proposal near an incumbent that had not yet been refined. That query found the spike (-0.00819).

**Current regime** (`src/bbo/config.py`)
`trust_region`. incumbent (0.484, 0.760, 0.488); quadratic locally imperfect.

## 4. Data handling and preprocessing

- Raw outputs.
- Inputs are not rescaled, because the domain is already [0, 1]^3.
- No points have been removed or edited. Bad points are kept, because they constrain the surrogate.
- Every query is checked with `bbo.data.validate` before submission: dimension, six decimals, and inside (0, 1).

## 5. Weekly iteration and learning

Week 6 stepped 0.15 per axis and fell to -0.120, which showed the peak is narrow. Weeks 7–9 stayed closer and returned -0.030, -0.021 and -0.013 without a new record. The calibration record notes an overconfident sd in round 5→6.

| Week | Query (portal string) | Observed | Record? |
|---:|---|---:|:---:|
| 1 | `0.999999-0.999999-0.402885` | -0.06048192489 |  |
| 2 | `0.999999-0.000001-0.000001` | -0.1759094303 |  |
| 3 | `0.999999-0.999999-0.858999` | -0.07458897931 |  |
| 4 | `0.000001-0.000001-0.522685` | -0.07661585113 |  |
| 5 | `0.483975-0.760029-0.488443` | -0.008186858923 | yes |
| 6 | `0.333975-0.910029-0.638443` | -0.1202430952 |  |
| 7 | `0.403975-0.840029-0.512796` | -0.03029773478 |  |
| 8 | `0.523975-0.720029-0.448443` | -0.02143914069 |  |
| 9 | `0.442209-0.716463-0.428609` | -0.01278218303 |  |
| 10 | `0.513975-0.730029-0.518443` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best is -0.0081869 at (0.483975, 0.760029, 0.488443), week 5. The week-10 query is a trust-region step, and the driver predicts -0.0102 ± 0.0122.

| Supplied best | Best after week 9 | Gain | Best point (week) |
|---:|---:|---:|---|
| -0.03483531335 | -0.008186858923 | +0.02665 | `0.483975-0.760029-0.488443` (week 5) |

The surrogate behind the week-10 query is plotted in [`reports/figures/surrogate_F3.png`](../reports/figures/surrogate_F3.png).

## 7. Ethical and practical considerations

- As a dose-combination analogy: a few broad probes can miss a narrow low-side-effect window entirely, and doses 'near the best' can be much worse. A real study would need safety constraints on how far each query moves.
- **Provenance.** The function and its supplied data come from the course, and the true formula is unknown. The scenario hints are illustrations, not claims about real systems.
- **Reuse.** The data is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
