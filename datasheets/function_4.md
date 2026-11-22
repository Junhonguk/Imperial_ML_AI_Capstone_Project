# Datasheet: Function 4 (4D)

*BBO capstone. Snapshot after 9 graded queries. The week-10 query has been submitted and its result is pending.*
*All numbers come from `data/function_4/` and `results/query_log.csv`.*

---

## 1. Function overview

**Which function?**
Function 4. Description hint: *multi-modal, sharp peak*.

**Input dimension and domain**
4D, on the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
30 points: `initial_inputs.npy` has shape (30, 4) and `initial_outputs.npy` has shape (30,).

**What does the output represent?**
A score that is strongly negative over most of the domain (supplied median -16, minimum -32.6), with a sharp positive peak.

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^4. Supplied outputs range from -32.63 to -4.026, with median -16.04.

The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x4,y`). There are 39 observations so far: 30 supplied and 9 queried.

**How the data evolves**
One point is added per week. The supplied design is space-filling. Early queries spread out (corners, faces, global EI), and later queries cluster within about 0.01–0.08 of the incumbent.

The dataset is therefore becoming dense around the best point and stays sparse elsewhere. That is the right allocation for maximisation, but it makes the data a biased sample of the function as a whole.

**Noise and randomness**
Treated as noise-free. The three triangulated refinements rose steadily: 0.572, 0.598, 0.600.

**Observed shape**
Multi-modal, with a sharp, nearly isotropic peak of height about 0.60 near (0.4088, 0.4008, 0.3650, 0.4114). A move of under 0.1 from the peak (week 5) lost 1.5.

## 3. Optimisation strategy

**Methods used**
GP + EI in weeks 1–4. A trust region in weeks 5–6. Local isotropic triangulation on raw values, within radius 0.13 of the incumbent, from week 7.

**Why these methods**
Weeks 1–2 quickly found the peak region (0.26, then 0.47). Weeks 3 and 4 were misses (0.169 and -0.070) and triggered a trust region. Week 5 crashed to -0.889, and the box was shrunk to ±0.02. That showed the GP's lengthscales were much wider than the peak. A 6-coefficient isotropic quadratic fitted to the local readings then predicted the centre directly.

**Current regime** (`src/bbo/config.py`)
`triangulate`. converged: centre (0.4088, 0.4008, 0.3650, 0.4114), peak ~ 0.60.

## 4. Data handling and preprocessing

- Raw outputs. Only points within 0.13 of the incumbent enter the triangulation.
- Inputs are not rescaled, because the domain is already [0, 1]^4.
- No points have been removed or edited. Bad points are kept, because they constrain the surrogate.
- Every query is checked with `bbo.data.validate` before submission: dimension, six decimals, and inside (0, 1).

## 5. Weekly iteration and learning

This is the clearest case of calibration driving the choice of model class. Two misses led to a trust region, a crash led to a smaller box, and the GP kept failing, so a parametric fit replaced it. The result was three records in a row, each smaller than the last (+0.105, +0.026, +0.0025), as expected when converging on a smooth peak.

| Week | Query (portal string) | Observed | Record? |
|---:|---|---:|:---:|
| 1 | `0.440421-0.425453-0.378356-0.397100` | 0.2598840746 | yes |
| 2 | `0.409500-0.416081-0.348311-0.437492` | 0.4674901721 | yes |
| 3 | `0.383315-0.410910-0.393707-0.439291` | 0.1688146679 |  |
| 4 | `0.410939-0.441891-0.324933-0.422608` | -0.06993559219 |  |
| 5 | `0.463711-0.353735-0.359057-0.461397` | -0.8894640041 |  |
| 6 | `0.429500-0.430618-0.368311-0.457492` | -0.1025088256 |  |
| 7 | `0.409183-0.395688-0.362953-0.410446` | 0.5720967052 | yes |
| 8 | `0.408926-0.400164-0.364793-0.411312` | 0.5978070384 | yes |
| 9 | `0.408848-0.400632-0.364958-0.411368` | 0.6003520836 | yes |
| 10 | `0.408815-0.400815-0.365021-0.411389` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best is 0.6003521 at (0.408848, 0.400632, 0.364958, 0.411368), week 9. The week-10 query is the next triangulated centre (fitted peak about 0.61, R² 0.993).

| Supplied best | Best after week 9 | Gain | Best point (week) |
|---:|---:|---:|---|
| -4.025542282 | 0.6003520836 | +4.626 | `0.408848-0.400632-0.364958-0.411368` (week 9) |

The surrogate behind the week-10 query is plotted in [`reports/figures/surrogate_F4.png`](../reports/figures/surrogate_F4.png).

## 7. Ethical and practical considerations

- As a placement analogy: the steep fall-off around the peak means that small errors in carrying out the solution are costly. That robustness is worth reporting alongside the best value.
- **Provenance.** The function and its supplied data come from the course, and the true formula is unknown. The scenario hints are illustrations, not claims about real systems.
- **Reuse.** The data is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
