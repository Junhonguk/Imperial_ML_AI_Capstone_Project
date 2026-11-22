# Datasheet: Function 8 (8D)

*BBO capstone. This record is final at 12 graded queries; the round-13 query has been submitted and its result is pending.*
*Every number on this page comes from `data/function_8/` and `results/query_log.csv` (sheets generated, then checked against the data).*

---

## 1. Function overview

**Which function is this?**
Function 8, with description hint: *near-linear, plateau*.

**Input dimension and domain**
8D, the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
40: `initial_inputs.npy` with shape (40, 8) and `initial_outputs.npy` with shape (40,).

**What does the output represent?**
A score near 10. The supplied data ranges from 5.59 to 9.60.

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^8. The supplied outputs range from 5.592 to 9.598 (median 7.889). The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x8,y`). There are 52 observations in total (40 supplied + 12 queried).

**How the data changed over the campaign**
One point per week. The supplied design is space-filling, the early queries are spread out (corners, faces, global EI), and the later queries are concentrated within about 0.01-0.05 of the incumbent. The final dataset is therefore dense around the best point and sparse elsewhere. That suits maximisation but makes it a biased sample of the function as a whole.

**Noise and randomness**
Deterministic (campaign-wide replicate).

**Shape of the function, as observed**
Smooth and close to linear over most of the domain, with the optimum at a mix of faces (x4 = 0, x5 and x8 near 1) and interior values. Final lengthscales are long (1.5-4.0), and four inputs are at the cap of 4.0.

## 3. Optimisation strategy

**Methods used**
GP + EI (weeks 1-4); tight trust regions (week 5 onward), ending with half-width 0.015 and cap 4.0.

**Why these methods**
Eight dimensions with 40 supplied points: a global EI step changes all eight inputs at once and overshoots. Weeks 4-6 lost 0.08-0.13 this way. Tight boxes move little along each input, which suits a near-linear surface with a shallow peak.

**Final regime** (`src/bbo/config.py`)
`trust_region`. 5 straight end-phase gains to 9.9481; x5 trending interior.

## 4. Data handling and preprocessing

- Raw outputs; x4 held at 0.000001 from week 5.
- Inputs are not rescaled: the domain is already [0, 1]^8.
- No points were removed or edited. Points that turned out to be bad are kept, because they constrain the surrogate.
- Every query was checked with `bbo.data.validate` before submission (dimension, six decimals, inside (0, 1)).

## 5. Weekly iteration and learning

Plateau at 9.930 from week 2 to week 9. It was broken in week 9, which began four records in a row (9.9347, 9.9405, 9.9408, 9.9481). The calibration hits included 9.941 predicted against 9.94078 observed, and 9.942 against 9.9481.

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
| 10 | `0.092957-0.150582-0.136047-0.000001-0.999999-0.471948-0.203583-0.999999` | 9.940478744 | yes |
| 11 | `0.072957-0.170582-0.156047-0.000001-0.979999-0.491948-0.183583-0.999999` | 9.940775084 | yes |
| 12 | `0.087957-0.155582-0.141047-0.000001-0.964999-0.506948-0.189443-0.984999` | 9.948107032 | yes |
| 13 | `0.095725-0.148082-0.133402-0.000001-0.949999-0.521948-0.190308-0.969999` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best 9.9481070 at (0.087957, 0.155582, 0.141047, 0.000001, 0.964999, 0.506948, 0.189443, 0.984999), week 12. Week 13 continues the trend (x5 moving into the interior); the driver predicts 9.952 ± 0.001.

| Supplied best | Final best | Gain | Best point (week) |
|---:|---:|---:|---|
| 9.598482003 | 9.948107032 | +0.3496 | `0.087957-0.155582-0.141047-0.000001-0.964999-0.506948-0.189443-0.984999` (week 12) |

The surrogate at campaign end: [`reports/figures/surrogate_F8.png`](../reports/figures/surrogate_F8.png).

## 7. Ethical and practical considerations

- With 8 inputs and 52 points, any claim about which inputs 'matter' is weak. Lengthscales that hit their cap mean 'not resolved', not 'irrelevant'.
- **Provenance.** The function and its supplied data come from the course; the true formula is unknown. Scenario descriptions are illustrations, not claims about real systems.
- **Reuse.** This dataset is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
