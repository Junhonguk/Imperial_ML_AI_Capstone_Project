# Datasheet: Function 6 (5D)

*BBO capstone. Snapshot after 9 graded queries. The week-10 query has been submitted and its result is pending.*
*All numbers come from `data/function_6/` and `results/query_log.csv`.*

---

## 1. Function overview

**Which function?**
Function 6. Description hint: *recipe score (outputs <= 0)*.

**Input dimension and domain**
5D, on the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
20 points: `initial_inputs.npy` has shape (20, 5) and `initial_outputs.npy` has shape (20,).

**What does the output represent?**
A negated quality loss. Every reading is <= 0, and closer to 0 is better.

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^5. Supplied outputs range from -2.571 to -0.7143, with median -1.446.

The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x5,y`). There are 29 observations so far: 20 supplied and 9 queried.

**How the data evolves**
One point is added per week. The supplied design is space-filling. Early queries spread out (corners, faces, global EI), and later queries cluster within about 0.01–0.08 of the incumbent.

The dataset is therefore becoming dense around the best point and stays sparse elsewhere. That is the right allocation for maximisation, but it makes the data a biased sample of the function as a whole.

**Noise and randomness**
Treated as noise-free. The large drops in weeks 3, 5 and 8 come from steps that were too long.

**Observed shape**
Smooth, with one dominant basin. The supplied data ranges from -2.57 to -0.71.

## 3. Optimisation strategy

**Methods used**
GP + EI in weeks 1–5. From week 6, a trust-region hill climb, now with half-width 0.08, lengthscale cap 1.0 and ξ = 0.003.

**Why these methods**
With 20 points in 5D the global GP was too smooth. Multi-input EI steps in weeks 3 and 5 fell 0.28–0.36 below the incumbent. A trust region with capped lengthscales keeps each step where the model can be trusted.

**Current regime** (`src/bbo/config.py`)
`trust_region`. momentum: -0.714 -> -0.137 and climbing.

## 4. Data handling and preprocessing

- Raw outputs. Lengthscales capped at 1.0.
- Inputs are not rescaled, because the domain is already [0, 1]^5.
- No points have been removed or edited. Bad points are kept, because they constrain the surrogate.
- Every query is checked with `bbo.data.validate` before submission: dimension, six decimals, and inside (0, 1).

## 5. Weekly iteration and learning

Progress came in steps: -0.564 (week 1), -0.355 (week 2), -0.256 (week 7), -0.137 (week 9). Week 9 broke above its predicted band, and the function is still climbing.

| Week | Query (portal string) | Observed | Record? |
|---:|---|---:|:---:|
| 1 | `0.464269-0.241724-0.574975-0.999999-0.000001` | -0.5644528109 | yes |
| 2 | `0.546767-0.322574-0.589212-0.854091-0.124893` | -0.3548887976 | yes |
| 3 | `0.483658-0.276411-0.999999-0.873521-0.271362` | -0.7189668404 |  |
| 4 | `0.511139-0.339217-0.494996-0.688240-0.027501` | -0.454036288 |  |
| 5 | `0.513885-0.485884-0.475695-0.981451-0.164695` | -0.6399368475 |  |
| 6 | `0.581181-0.224619-0.610709-0.822991-0.024893` | -0.4693331693 |  |
| 7 | `0.496767-0.304397-0.603900-0.804091-0.174893` | -0.2561692687 | yes |
| 8 | `0.418685-0.224397-0.568065-0.783996-0.221245` | -0.361342329 |  |
| 9 | `0.474225-0.347711-0.653900-0.754091-0.190571` | -0.1368004803 | yes |
| 10 | `0.427581-0.382223-0.730707-0.724506-0.110571` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best is -0.1368005 at (0.474225, 0.347711, 0.653900, 0.754091, 0.190571), week 9. The week-10 query is a trust-region step, and the driver predicts -0.089 ± 0.061.

| Supplied best | Best after week 9 | Gain | Best point (week) |
|---:|---:|---:|---|
| -0.7142649478 | -0.1368004803 | +0.5775 | `0.474225-0.347711-0.653900-0.754091-0.190571` (week 9) |

The surrogate behind the week-10 query is plotted in [`reports/figures/surrogate_F6.png`](../reports/figures/surrogate_F6.png).

## 7. Ethical and practical considerations

- Recipe optimisation is low-stakes. The practical caveat is that a 'best recipe' found by local search depends on where the search started.
- **Provenance.** The function and its supplied data come from the course, and the true formula is unknown. The scenario hints are illustrations, not claims about real systems.
- **Reuse.** The data is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
