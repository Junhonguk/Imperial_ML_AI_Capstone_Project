# Datasheet: Function 8 (8D)

*BBO capstone. Snapshot after 9 graded queries. The week-10 query has been submitted and its result is pending.*
*All numbers come from `data/function_8/` and `results/query_log.csv`.*

---

## 1. Function overview

**Which function?**
Function 8. Description hint: *near-linear, plateau*.

**Input dimension and domain**
8D, on the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
40 points: `initial_inputs.npy` has shape (40, 8) and `initial_outputs.npy` has shape (40,).

**What does the output represent?**
A score near 10. The supplied data ranges from 5.59 to 9.60.

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^8. Supplied outputs range from 5.592 to 9.598, with median 7.889.

The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x8,y`). There are 49 observations so far: 40 supplied and 9 queried.

**How the data evolves**
One point is added per week. The supplied design is space-filling. Early queries spread out (corners, faces, global EI), and later queries cluster within about 0.01–0.08 of the incumbent.

The dataset is therefore becoming dense around the best point and stays sparse elsewhere. That is the right allocation for maximisation, but it makes the data a biased sample of the function as a whole.

**Noise and randomness**
Treated as noise-free.

**Observed shape**
Smooth and close to linear over most of the domain. The optimum combines faces (x4 = 0, x5 near 1) with interior values for the other inputs.

## 3. Optimisation strategy

**Methods used**
GP + EI in weeks 1–4. From week 5, tight trust regions, now with half-width 0.03, cap 4.0 and ξ = 0.001.

**Why these methods**
Eight dimensions with 40 supplied points. A global EI step moves all eight inputs at once and overshoots: weeks 4–6 lost 0.08–0.13 this way. Tight boxes take small steps along each input, which suits a near-linear surface with a shallow peak.

**Current regime** (`src/bbo/config.py`)
`trust_region`. plateau cracked at 9.9347; keep tight.

## 4. Data handling and preprocessing

- Raw outputs. x4 held at 0.000001 since week 5.
- Inputs are not rescaled, because the domain is already [0, 1]^8.
- No points have been removed or edited. Bad points are kept, because they constrain the surrogate.
- Every query is checked with `bbo.data.validate` before submission: dimension, six decimals, and inside (0, 1).

## 5. Weekly iteration and learning

The value plateaued at 9.930 from week 2. Week 9 broke the plateau at 9.9347 after the box was tightened.

| Week | Query (portal string) | Observed | Record? |
|---:|---|---:|:---:|
| 1 | `0.046297-0.000001-0.130573-0.000001-0.999999-0.487887-0.113888-0.011968` | 9.879676349 | yes |
| 2 | `0.092761-0.090582-0.142880-0.000001-0.999999-0.411948-0.203583-0.999999` | 9.929588761 | yes |
| 3 | `0.134897-0.130334-0.188538-0.000001-0.999999-0.534375-0.296844-0.424789` | 9.921389004 |  |
| 4 | `0.000001-0.058953-0.000001-0.433017-0.999999-0.653061-0.206180-0.617011` | 9.79738021 |  |
| 5 | `0.000001-0.000001-0.198333-0.000001-0.999999-0.561948-0.053583-0.849999` | 9.848029623 |  |
| 6 | `0.192761-0.000001-0.042880-0.000001-0.999999-0.311948-0.108347-0.899999` | 9.833857871 |  |
| 7 | `0.032761-0.150582-0.114046-0.000001-0.999999-0.351948-0.248053-0.939999` | 9.909596896 |  |
| 8 | `0.128458-0.050582-0.182880-0.000001-0.999999-0.371948-0.243583-0.959999` | 9.904451764 |  |
| 9 | `0.122761-0.120582-0.158295-0.000001-0.999999-0.441948-0.173583-0.969999` | 9.934741457 | yes |
| 10 | `0.092957-0.150582-0.136047-0.000001-0.999999-0.471948-0.203583-0.999999` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best is 9.9347415 at (0.122761, 0.120582, 0.158295, 0.000001, 0.999999, 0.441948, 0.173583, 0.969999), week 9. The week-10 query is a trust-region step, and the driver predicts 9.946 ± 0.010.

| Supplied best | Best after week 9 | Gain | Best point (week) |
|---:|---:|---:|---|
| 9.598482003 | 9.934741457 | +0.3363 | `0.122761-0.120582-0.158295-0.000001-0.999999-0.441948-0.173583-0.969999` (week 9) |

The surrogate behind the week-10 query is plotted in [`reports/figures/surrogate_F8.png`](../reports/figures/surrogate_F8.png).

## 7. Ethical and practical considerations

- With 8 inputs and 49 points, any claim about which inputs 'matter' is weak. A lengthscale sitting at its cap means 'not resolved', not 'irrelevant'.
- **Provenance.** The function and its supplied data come from the course, and the true formula is unknown. The scenario hints are illustrations, not claims about real systems.
- **Reuse.** The data is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
