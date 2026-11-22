# Datasheet: Function 5 (4D)

*BBO capstone. This record is final at 12 graded queries; the round-13 query has been submitted and its result is pending.*
*Every number on this page comes from `data/function_5/` and `results/query_log.csv` (sheets generated, then checked against the data).*

---

## 1. Function overview

**Which function is this?**
Function 5, with description hint: *chemical yield (log-scale)*.

**Input dimension and domain**
4D, the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
20: `initial_inputs.npy` with shape (20, 4) and `initial_outputs.npy` with shape (20,).

**What does the output represent?**
A positive yield spanning five orders of magnitude (0.11 to 8662).

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^4. The supplied outputs range from 0.1129 to 1089 (median 63.95). The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x4,y`). There are 32 observations in total (20 supplied + 12 queried).

**How the data changed over the campaign**
One point per week. The supplied design is space-filling, the early queries are spread out (corners, faces, global EI), and the later queries are concentrated within about 0.01-0.05 of the incumbent. The final dataset is therefore dense around the best point and sparse elsewhere. That suits maximisation but makes it a biased sample of the function as a whole.

**Noise and randomness**
Deterministic, proven. The corner returned 8662.405001248297 bit-for-bit in weeks 7, 10 and 12.

**Shape of the function, as observed**
Unimodal and increasing toward the (1, 1, 1, 1) corner, close to log-linear in each input, with interaction between inputs.

## 3. Optimisation strategy

**Methods used**
GP + EI on log(y), riding the trend to the corner (weeks 1-7), then a 4-direction audit around it (weeks 8, 9 and 11, with x1 covered by the climb in weeks 5-6). The regime is `done`.

**Why these methods**
On the raw scale a GP is dominated by the few large values. On log y the surface is smooth and close to linear, and EI follows the trend. A corner proposal in week 5 was refused as uncertainty-bait because its mean was below the incumbent. It was re-admitted once the evidence lifted its mean above the incumbent, and in week 7 it returned 8662, a 44% gain.

**Final regime** (`src/bbo/config.py`)
`done`. corner proven max 8662.405001248297 (4-direction audit; 3x bit-identical).

## 4. Data handling and preprocessing

- Output transform `log(y)` (all outputs are positive).
- Inputs are not rescaled: the domain is already [0, 1]^4.
- No points were removed or edited. Points that turned out to be bad are kept, because they constrain the surrogate.
- Every query was checked with `bbo.data.validate` before submission (dimension, six decimals, inside (0, 1)).

## 5. Weekly iteration and learning

Stepping back from the corner along each input lost value every time (x2 0.85: 6495; x3 0.90: 7073; x4 0.95: 7786), so the corner is the maximum within the box. The week-10 replicate was spent deliberately: it settled determinism for all eight functions and changed how F2 was modelled.

| Week | Query (portal string) | Observed | Record? |
|---:|---|---:|:---:|
| 1 | `0.000001-0.581912-0.882310-0.999999` | 1095.325078 | yes |
| 2 | `0.000001-0.014008-0.197475-0.999999` | 192.0910178 |  |
| 3 | `0.000001-0.824963-0.999999-0.999999` | 2767.770191 | yes |
| 4 | `0.000001-0.999999-0.999999-0.999999` | 4440.480874 | yes |
| 5 | `0.400000-0.999999-0.999999-0.999999` | 4540.337719 | yes |
| 6 | `0.800000-0.999999-0.999999-0.999999` | 6027.724406 | yes |
| 7 | `0.999999-0.999999-0.999999-0.999999` | 8662.405001 | yes |
| 8 | `0.999999-0.850000-0.999999-0.999999` | 6495.031574 |  |
| 9 | `0.999999-0.999999-0.900000-0.999999` | 7073.392997 |  |
| 10 | `0.999999-0.999999-0.999999-0.999999` | 8662.405001 |  |
| 11 | `0.999999-0.999999-0.999999-0.950000` | 7786.316251 |  |
| 12 | `0.999999-0.999999-0.999999-0.999999` | 8662.405001 |  |
| 13 | `0.999999-0.999999-0.999999-0.999999` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best 8662.405001248297 at (1, 1, 1, 1) clipped to 0.999999, first found in week 7. Proven maximum. Week 13 repeats the corner.

| Supplied best | Final best | Gain | Best point (week) |
|---:|---:|---:|---|
| 1088.859618 | 8662.405001 | +7574 | `0.999999-0.999999-0.999999-0.999999` (week 7) |

The surrogate at campaign end: [`reports/figures/surrogate_F5.png`](../reports/figures/surrogate_F5.png).

## 7. Ethical and practical considerations

- A real process run at the corner of its allowed operating box would deserve a safety review, since the optimum may lie beyond the stated limits. The model has no knowledge of what lies outside the box.
- **Provenance.** The function and its supplied data come from the course; the true formula is unknown. Scenario descriptions are illustrations, not claims about real systems.
- **Reuse.** This dataset is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
