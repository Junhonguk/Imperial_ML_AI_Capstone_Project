# Datasheet: Function 2 (2D)

*BBO capstone. This record is final at 12 graded queries; the round-13 query has been submitted and its result is pending.*
*Every number on this page comes from `data/function_2/` and `results/query_log.csv` (sheets generated, then checked against the data).*

---

## 1. Function overview

**Which function is this?**
Function 2, with description hint: *noisy log-likelihood*.

**Input dimension and domain**
2D, the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
10: `initial_inputs.npy` with shape (10, 2) and `initial_outputs.npy` with shape (10,).

**What does the output represent?**
A log-likelihood-like score. Higher is better.

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^2. The supplied outputs range from -0.06562 to 0.6112 (median 0.2298). The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x2,y`). There are 22 observations in total (10 supplied + 12 queried).

**How the data changed over the campaign**
One point per week. The supplied design is space-filling, the early queries are spread out (corners, faces, global EI), and the later queries are concentrated within about 0.01-0.05 of the incumbent. The final dataset is therefore dense around the best point and sparse elsewhere. That suits maximisation but makes it a biased sample of the function as a whole.

**Noise and randomness**
Treated as noisy (WhiteKernel, sd about 0.06) from week 4 to week 10, because nearby points returned very different values. After the week-10 F5 replicate proved determinism, the scatter was reinterpreted as real structure below 1e-3. That reinterpretation is the most important modelling correction in the campaign.

**Shape of the function, as observed**
A broad ridge along x1 ≈ 0.69, highest on the x2 = 1 edge, with deterministic periodic micro-spikes along x1 (period about 2.71e-4) whose heights vary sharply between neighbouring points.

## 3. Optimisation strategy

**Methods used**
Noise-aware GP + EI (weeks 1-3: corner and edge probes); a local search along the x2 = 1 edge (weeks 4-9); a 'lottery' over the periodic spikes (weeks 10-13).

**Why these methods**
Week 4 found the x2 = 1 edge (0.646). Readings less than 1e-3 apart then differed by up to 0.2 (weeks 9 and 10: 0.661 and 0.460, 3e-4 apart), which a smooth GP can only call noise. Once determinism was known, the spacing of the high readings gave a period. The remaining queries were placed at predicted spike positions instead of at the GP's posterior-mean argmax.

**Final regime** (`src/bbo/config.py`)
`lottery`. periodic micro-spikes, period 2.71e-4, heights rising with x1; best 0.6612.

## 4. Data handling and preprocessing

- Raw outputs. x2 pinned to 0.999999 from week 4.
- Inputs are not rescaled: the domain is already [0, 1]^2.
- No points were removed or edited. Points that turned out to be bad are kept, because they constrain the surrogate.
- Every query was checked with `bbo.data.validate` before submission (dimension, six decimals, inside (0, 1)).

## 5. Weekly iteration and learning

The week-11 parabola fit along x1 was refuted (0.481). The period model then predicted a spike at x1 = 0.691068 (= 0.69161 − 2 × 2.71e-4), and week 12 returned 0.643, confirming the position although not beating 0.6612. Week 13 tests the next predicted spike at 0.691881 (+1 period).

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
| 10 | `0.691909-0.999999` | 0.460321852 |  |
| 11 | `0.691481-0.999999` | 0.4814186 |  |
| 12 | `0.691068-0.999999` | 0.6431640269 |  |
| 13 | `0.691881-0.999999` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best 0.6612264 at (0.691610, 0.999999), week 9. The gain over the supplied design (+0.050) is the smallest of the eight functions.

| Supplied best | Final best | Gain | Best point (week) |
|---:|---:|---:|---|
| 0.6112052158 | 0.6612264043 | +0.05002 | `0.691610-0.999999` (week 9) |

The surrogate at campaign end: [`reports/figures/surrogate_F2.png`](../reports/figures/surrogate_F2.png).

## 7. Ethical and practical considerations

- A real likelihood surface with micro-structure like this would point to numerical problems in the likelihood code (quadrature, step size) rather than a real optimum. Optimising over it without checking would be overfitting. The datasheet records the structure; the query choices do not claim more than they show.
- **Provenance.** The function and its supplied data come from the course; the true formula is unknown. Scenario descriptions are illustrations, not claims about real systems.
- **Reuse.** This dataset is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
