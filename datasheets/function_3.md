# Datasheet: Function 3 (3D)

*BBO capstone. This record is final: the campaign is complete at 13 graded queries.*
*Every number on this page comes from `data/function_3/` and `results/query_log.csv` (sheets generated, then checked against the data).*

---

## 1. Function overview

**Which function is this?**
Function 3, with description hint: *drug side-effects (outputs <= 0)*.

**Input dimension and domain**
3D, the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
15: `initial_inputs.npy` with shape (15, 3) and `initial_outputs.npy` with shape (15,).

**What does the output represent?**
Negated side-effect severity: every reading is <= 0, and closer to 0 is better.

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^3. The supplied outputs range from -0.3989 to -0.03484 (median -0.106). The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x3,y`). There are 28 observations in total (15 supplied + 13 queried).

**How the data changed over the campaign**
One point per week. The supplied design is space-filling, the early queries are spread out (corners, faces, global EI), and the later queries are concentrated within about 0.01-0.05 of the incumbent. The final dataset is therefore dense around the best point and sparse elsewhere. That suits maximisation but makes it a biased sample of the function as a whole.

**Noise and randomness**
Deterministic (campaign-wide replicate). Local readings 0.01-0.05 apart differ by up to 0.02, which reflects how sharp the spike is, not noise.

**Shape of the function, as observed**
Mostly smooth and strongly negative toward the corners (down to -0.40), with a narrow spike near (0.484, 0.760, 0.488) where readings approach 0.

## 3. Optimisation strategy

**Methods used**
GP + EI over the full domain with corner sweeps (weeks 1-4); local EI refinement (weeks 5-12); a trust region with half-width 0.006 and lengthscale cap 0.2 at the end.

**Why these methods**
With 15 points in 3D, the early EI proposals went to corners. All four corner probes returned between -0.06 and -0.18, ruling them out. On an EI tie in week 5, a local proposal near an incumbent not yet refined was preferred, which found the spike (-0.00819).

**Final regime** (`src/bbo/config.py`)
`trust_region`. incumbent (0.484, 0.760, 0.488) = narrow spike; best -0.0082.

## 4. Data handling and preprocessing

- Raw outputs. Lengthscales capped at 0.2 so the GP cannot smooth the spike away.
- Inputs are not rescaled: the domain is already [0, 1]^3.
- No points were removed or edited. Points that turned out to be bad are kept, because they constrain the surrogate.
- Every query was checked with `bbo.data.validate` before submission (dimension, six decimals, inside (0, 1)).

## 5. Weekly iteration and learning

Week 6 stepped 0.15 per axis and fell to -0.120: the peak is narrow. Weeks 7-12 stayed within about 0.05 and returned -0.011 to -0.030 without a new record. The calibration record notes an overconfident sd in round 5→6. The final GP slices show that x3 has the shortest lengthscale (0.07).

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
| 10 | `0.513975-0.730029-0.518443` | -0.02996874042 |  |
| 11 | `0.463975-0.780029-0.472488` | -0.02968114034 |  |
| 12 | `0.473975-0.750029-0.495419` | -0.01086008325 |  |
| 13 | `0.489975-0.766029-0.494443` | -0.01123704552 |  |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best -0.0081869 at (0.483975, 0.760029, 0.488443), week 5. One record in 13 weeks. The final trust-region step returned -0.0112 against a prediction of -0.0063 ± 0.0044 - a miss; the week-5 incumbent stands.

| Supplied best | Final best | Gain | Best point (week) |
|---:|---:|---:|---|
| -0.03483531335 | -0.008186858923 | +0.02665 | `0.483975-0.760029-0.488443` (week 5) |

The surrogate at campaign end: [`reports/figures/surrogate_F3.png`](../reports/figures/surrogate_F3.png).

## 7. Ethical and practical considerations

- If this were a real dose-combination study, the lesson would be that a few broad probes can miss a narrow window of low side effects completely, and that 'near the best' doses can be much worse. Real use would need safety constraints on how far any query moves.
- **Provenance.** The function and its supplied data come from the course; the true formula is unknown. Scenario descriptions are illustrations, not claims about real systems.
- **Reuse.** This dataset is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
