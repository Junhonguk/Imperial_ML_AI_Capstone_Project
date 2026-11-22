# Datasheet: Function 6 (5D)

*BBO capstone. This record is final at 12 graded queries; the round-13 query has been submitted and its result is pending.*
*Every number on this page comes from `data/function_6/` and `results/query_log.csv` (sheets generated, then checked against the data).*

---

## 1. Function overview

**Which function is this?**
Function 6, with description hint: *recipe score (outputs <= 0)*.

**Input dimension and domain**
5D, the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
20: `initial_inputs.npy` with shape (20, 5) and `initial_outputs.npy` with shape (20,).

**What does the output represent?**
A negated quality loss: every reading is <= 0, closer to 0 is better.

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^5. The supplied outputs range from -2.571 to -0.7143 (median -1.446). The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x5,y`). There are 32 observations in total (20 supplied + 12 queried).

**How the data changed over the campaign**
One point per week. The supplied design is space-filling, the early queries are spread out (corners, faces, global EI), and the later queries are concentrated within about 0.01-0.05 of the incumbent. The final dataset is therefore dense around the best point and sparse elsewhere. That suits maximisation but makes it a biased sample of the function as a whole.

**Noise and randomness**
Deterministic (campaign-wide replicate). The large drops in weeks 3, 5 and 11 come from moves that were too long, not noise.

**Shape of the function, as observed**
Smooth, with one dominant basin. The supplied data ranges from -2.57 to -0.71. x4 has the shortest final lengthscale (0.19); the others are at or near their 0.5 cap.

## 3. Optimisation strategy

**Methods used**
GP + EI (weeks 1-5); a trust-region hill climb with lengthscale cap 0.5 and half-width 0.02 at the end (weeks 6-13).

**Why these methods**
With 20 points in 5D the global GP was too smooth: multi-input EI steps in weeks 3 and 5 fell 0.28-0.36 below the incumbent. A trust region with capped lengthscales keeps each step inside the region where the model can be trusted.

**Final regime** (`src/bbo/config.py`)
`trust_region`. still climbing at campaign end: -0.714 -> -0.0975.

## 4. Data handling and preprocessing

- Raw outputs; lengthscales capped at 0.5.
- Inputs are not rescaled: the domain is already [0, 1]^5.
- No points were removed or edited. Points that turned out to be bad are kept, because they constrain the surrogate.
- Every query was checked with `bbo.data.validate` before submission (dimension, six decimals, inside (0, 1)).

## 5. Weekly iteration and learning

The improvement came in steps: -0.564 (week 1), -0.355 (2), -0.256 (7), -0.137 (9), -0.0975 (12). A record still came in week 12. The final GP slice along x5 still slopes upward toward x5 = 0, so the budget ran out before this function converged.

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
| 10 | `0.427581-0.382223-0.730707-0.724506-0.110571` | -0.1400928274 |  |
| 11 | `0.446100-0.387711-0.689105-0.714091-0.198789` | -0.3383464059 |  |
| 12 | `0.459225-0.362711-0.668900-0.769091-0.175571` | -0.0974975397 | yes |
| 13 | `0.439225-0.342711-0.688900-0.766119-0.155571` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best -0.0974975 at (0.459225, 0.362711, 0.668900, 0.769091, 0.175571), week 12. Week 13 is a trust-region step; the driver predicts -0.063 ± 0.031.

| Supplied best | Final best | Gain | Best point (week) |
|---:|---:|---:|---|
| -0.7142649478 | -0.0974975397 | +0.6168 | `0.459225-0.362711-0.668900-0.769091-0.175571` (week 12) |

The surrogate at campaign end: [`reports/figures/surrogate_F6.png`](../reports/figures/surrogate_F6.png).

## 7. Ethical and practical considerations

- Recipe optimisation is low-stakes. The practical caveat is that a 'best recipe' found by local search depends on where the search started, and others may exist elsewhere.
- **Provenance.** The function and its supplied data come from the course; the true formula is unknown. Scenario descriptions are illustrations, not claims about real systems.
- **Reuse.** This dataset is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
