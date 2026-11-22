# Datasheet: Function 2 (2D)

*BBO capstone. Snapshot after 9 graded queries. The week-10 query has been submitted and its result is pending.*
*All numbers come from `data/function_2/` and `results/query_log.csv`.*

---

## 1. Function overview

**Which function?**
Function 2. Description hint: *noisy log-likelihood*.

**Input dimension and domain**
2D, on the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
10 points: `initial_inputs.npy` has shape (10, 2) and `initial_outputs.npy` has shape (10,).

**What does the output represent?**
A log-likelihood-like score. Higher is better.

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^2. Supplied outputs range from -0.06562 to 0.6112, with median 0.2298.

The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x2,y`). There are 19 observations so far: 10 supplied and 9 queried.

**How the data evolves**
One point is added per week. The supplied design is space-filling. Early queries spread out (corners, faces, global EI), and later queries cluster within about 0.01–0.08 of the incumbent.

The dataset is therefore becoming dense around the best point and stays sparse elsewhere. That is the right allocation for maximisation, but it makes the data a biased sample of the function as a whole.

**Noise and randomness**
Treated as noisy. Measured noise sd is about 0.06: the week-5 query, about 0.004 from the week-4 record, returned 0.489 against 0.646. The GP carries a WhiteKernel, and the endgame objective is the posterior mean rather than EI.

**Observed shape**
A broad ridge along x1 ≈ 0.69, highest on the x2 = 1 edge. Readings near the best point vary sharply, by up to 0.16 between points about 0.004 apart.

## 3. Optimisation strategy

**Methods used**
Noise-aware GP + EI for weeks 1–3, using corner and edge probes. From week 4, a local search along the x2 = 1 edge. Now it maximises the posterior mean inside the box [0.64, 0.75] × [0.92, 1.0] (`mean_argmax`).

**Why these methods**
Week 4 found the x2 = 1 edge (0.646). The following readings scattered widely, so it is risky to chase a single high reading. The posterior-mean argmax averages over nearby replicates instead.

**Current regime** (`src/bbo/config.py`)
`mean_argmax`. noise sd ~ 0.06 measured; replicate-average the best region.

## 4. Data handling and preprocessing

- Raw outputs. Every query since week 4 has x2 near 1.
- Inputs are not rescaled, because the domain is already [0, 1]^2.
- No points have been removed or edited. Bad points are kept, because they constrain the surrogate.
- Every query is checked with `bbo.data.validate` before submission: dimension, six decimals, and inside (0, 1).

## 5. Weekly iteration and learning

The week-5 miss right beside the incumbent measured the noise level and moved the regime to posterior-mean replicates. Weeks 8–9 then set two records, 0.657 and 0.661, about 3e-4 apart in x1.

| Week | Query (portal string) | Observed | Record? |
|---:|---|---:|:---:|
| 1 | `0.961325-0.990488` | 0.04441342481 |  |
| 2 | `0.734696-0.000001` | 0.429831197 |  |
| 3 | `0.690599-0.000001` | 0.5330034019 |  |
| 4 | `0.684108-0.999999` | 0.6463582149 | yes |
| 5 | `0.680101-0.999926` | 0.4891445328 |  |
| 6 | `0.697043-0.999999` | 0.5272164174 |  |
| 7 | `0.692868-0.999999` | 0.5699647649 |  |
| 8 | `0.691339-0.999999` | 0.6572612055 | yes |
| 9 | `0.691610-0.999999` | 0.6612264043 | yes |
| 10 | `0.691909-0.999999` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best is 0.6612264 at (0.691610, 0.999999), week 9. The week-10 query (0.691909, 0.999999) is the posterior-mean argmax; the driver predicts 0.592 ± 0.064.

| Supplied best | Best after week 9 | Gain | Best point (week) |
|---:|---:|---:|---|
| 0.6112052158 | 0.6612264043 | +0.05002 | `0.691610-0.999999` (week 9) |

The surrogate behind the week-10 query is plotted in [`reports/figures/surrogate_F2.png`](../reports/figures/surrogate_F2.png).

## 7. Ethical and practical considerations

- Under noise, a single best reading is an optimistic estimate of the true best (the winner's curse). Reporting the posterior mean alongside the best reading keeps the claim honest.
- **Provenance.** The function and its supplied data come from the course, and the true formula is unknown. The scenario hints are illustrations, not claims about real systems.
- **Reuse.** The data is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
