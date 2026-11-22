# Datasheet: Function 4 (4D)

*BBO capstone. This record is final at 12 graded queries; the round-13 query has been submitted and its result is pending.*
*Every number on this page comes from `data/function_4/` and `results/query_log.csv` (sheets generated, then checked against the data).*

---

## 1. Function overview

**Which function is this?**
Function 4, with description hint: *multi-modal, sharp peak*.

**Input dimension and domain**
4D, the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
30: `initial_inputs.npy` with shape (30, 4) and `initial_outputs.npy` with shape (30,).

**What does the output represent?**
A score that is strongly negative over most of the domain (median of the supplied data -16, minimum -32.6), with a sharp positive peak.

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^4. The supplied outputs range from -32.63 to -4.026 (median -16.04). The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x4,y`). There are 42 observations in total (30 supplied + 12 queried).

**How the data changed over the campaign**
One point per week. The supplied design is space-filling, the early queries are spread out (corners, faces, global EI), and the later queries are concentrated within about 0.01-0.05 of the incumbent. The final dataset is therefore dense around the best point and sparse elsewhere. That suits maximisation but makes it a biased sample of the function as a whole.

**Noise and randomness**
Deterministic. The six-step refinement in weeks 7-12 rose monotonically (0.572, 0.598, 0.6004, 0.6013, 0.60186, 0.60219), which is inconsistent with noise.

**Shape of the function, as observed**
Multi-modal, with a sharp, nearly isotropic peak of height about 0.60 near (0.4088, 0.4010, 0.3651, 0.4114). A move of under 0.1 from the peak (week 5) lost 1.5.

## 3. Optimisation strategy

**Methods used**
GP + EI (weeks 1-4); a trust region (weeks 5-6); local isotropic triangulation on raw values within radius 0.13 of the incumbent (weeks 7-12).

**Why these methods**
Weeks 1-2 found the peak region quickly (0.26, then 0.47). Week 3 (0.169) and week 4 (-0.070) were misses and triggered a trust region from week 5. Week 5 crashed to -0.889 and the box was shrunk. This showed the GP's lengthscales were far wider than the peak. A 6-coefficient isotropic quadratic fitted to the local readings then predicted the centre directly.

**Final regime** (`src/bbo/config.py`)
`triangulate`. centre converged; 6 straight records to 0.60219.

## 4. Data handling and preprocessing

- Raw outputs; only points within 0.13 of the incumbent enter the triangulation.
- Inputs are not rescaled: the domain is already [0, 1]^4.
- No points were removed or edited. Points that turned out to be bad are kept, because they constrain the surrogate.
- Every query was checked with `bbo.data.validate` before submission (dimension, six decimals, inside (0, 1)).

## 5. Weekly iteration and learning

This is the clearest case of calibration driving a change of model: two misses meant a trust region, a crash meant a smaller box, and the GP still failing meant a parametric fit. That was followed by six records in a row, each gaining less than the last (+0.026, +0.0025, +0.0010, +0.0005, +0.0003), as you would expect when converging on a smooth peak.

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
| 10 | `0.408815-0.400815-0.365021-0.411389` | 0.6013445058 | yes |
| 11 | `0.408797-0.400911-0.365054-0.411400` | 0.6018624324 | yes |
| 12 | `0.408786-0.400970-0.365073-0.411406` | 0.6021859849 | yes |
| 13 | `0.408778-0.401009-0.365086-0.411411` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best 0.6021860 at (0.408786, 0.400970, 0.365073, 0.411406), week 12. Eight records, more than any other function. Week 13 is the next triangulated centre (fit peak about 0.609, R² 0.994).

| Supplied best | Final best | Gain | Best point (week) |
|---:|---:|---:|---|
| -4.025542282 | 0.6021859849 | +4.628 | `0.408786-0.400970-0.365073-0.411406` (week 12) |

The surrogate at campaign end: [`reports/figures/surrogate_F4.png`](../reports/figures/surrogate_F4.png).

## 7. Ethical and practical considerations

- If this were a real placement problem, the steep fall-off around the peak would mean small errors in carrying out the solution cost a lot. That robustness is worth reporting alongside the best value.
- **Provenance.** The function and its supplied data come from the course; the true formula is unknown. Scenario descriptions are illustrations, not claims about real systems.
- **Reuse.** This dataset is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
