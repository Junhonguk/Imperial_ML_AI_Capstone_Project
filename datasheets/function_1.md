# Datasheet: Function 1 (2D)

*BBO capstone. This record is final at 12 graded queries; the round-13 query has been submitted and its result is pending.*
*Every number on this page comes from `data/function_1/` and `results/query_log.csv` (sheets generated, then checked against the data).*

---

## 1. Function overview

**Which function is this?**
Function 1, with description hint: *point "sources", near-zero field*.

**Input dimension and domain**
2D, the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
10: `initial_inputs.npy` with shape (10, 2) and `initial_outputs.npy` with shape (10,).

**What does the output represent?**
A field strength that is effectively zero everywhere except close to a hidden source. Readings can be slightly negative.

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^2. The supplied outputs range from -0.003606 to 7.711e-16 (median 6.794e-80). The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x2,y`). There are 22 observations in total (10 supplied + 12 queried).

**How the data changed over the campaign**
One point per week. The supplied design is space-filling, the early queries are spread out (corners, faces, global EI), and the later queries are concentrated within about 0.01-0.05 of the incumbent. The final dataset is therefore dense around the best point and sparse elsewhere. That suits maximisation but makes it a biased sample of the function as a whole.

**Noise and randomness**
Deterministic. Readings 1e-5 apart lie on a smooth parabola with no scatter (weeks 9-12), and the campaign-wide replicate on F5 confirmed determinism.

**Shape of the function, as observed**
A single needle. Of the 10 supplied readings, the median magnitude is about 1e-79 and the largest is 7.7e-16; three are slightly negative (smallest -0.0036). Once found, the peak is a smooth, near-isotropic bump of height about 2.0 centred near (0.628534, 0.628540).

## 3. Optimisation strategy

**Methods used**
Parametric triangulation instead of GP+EI. (1) Weeks 1-2: an isotropic quadratic fitted to log|y| of the strongest readings locates the source analytically. (2) Weeks 3-10: the same form fitted to raw values near the peak. (3) Weeks 11-13: 1D parabolas along x2 (`triangulation.parabola_step`).

**Why these methods**
A GP on raw values sees a flat zero surface and has no gradient to follow. On log-magnitudes, a Gaussian-type source becomes a quadratic whose vertex is the source location, which a handful of points determine by least squares. The first log-magnitude fit (week 1) missed. It was refitted on the strongest readings only, with a consensus check across top-k subsets, and week 2 returned 1.989.

**Final regime** (`src/bbo/config.py`)
`micro`. peak (0.628534, 0.628540); best 1.9999998; true max = 2.0.

## 4. Data handling and preprocessing

- Output transform `log(|y| + 1e-300)` for the location phase; raw values once near the peak.
- Inputs are not rescaled: the domain is already [0, 1]^2.
- No points were removed or edited. Points that turned out to be bad are kept, because they constrain the surrogate.
- Every query was checked with `bbo.data.validate` before submission (dimension, six decimals, inside (0, 1)).

## 5. Weekly iteration and learning

The jump from about 2e-11 to 1.989 in week 2 came from changing the model class, not from tuning. Weeks 3-7 drifted between 1.86 and 1.98 while a 2D value quadratic was refitted. The week-8 fit predicted 2.0009 and returned 1.99994. After that each 1D parabola added digits: 1.9999868, 1.9999873, 1.99999946, 1.99999984. The final prediction was 1.99999988, against 1.99999984 observed.

| Week | Query (portal string) | Observed | Record? |
|---:|---|---:|:---:|
| 1 | `0.542786-0.537392` | 2.198501773e-11 | yes |
| 2 | `0.628479-0.627047` | 1.989311983 | yes |
| 3 | `0.631757-0.624063` | 1.859107663 |  |
| 4 | `0.628311-0.626207` | 1.973787555 |  |
| 5 | `0.628327-0.626234` | 1.974414985 |  |
| 6 | `0.628496-0.626447` | 1.979069451 |  |
| 7 | `0.629226-0.626178` | 1.97116122 |  |
| 8 | `0.628527-0.628652` | 1.999938804 | yes |
| 9 | `0.628534-0.628592` | 1.999986767 | yes |
| 10 | `0.628534-0.628591` | 1.999987263 | yes |
| 11 | `0.628534-0.628531` | 1.999999465 | yes |
| 12 | `0.628534-0.628540` | 1.999999837 | yes |
| 13 | `0.628535-0.628540` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best 1.9999998375 at (0.628534, 0.628540), week 12. The fitted peak implies a true maximum of 2.0, so the gap is about 1.6e-7. Week 13 (0.628535, 0.628540) moves x1 by 1e-6 to test the last free axis.

| Supplied best | Final best | Gain | Best point (week) |
|---:|---:|---:|---|
| 7.710875115e-16 | 1.999999837 | +2 | `0.628534-0.628540` (week 12) |

The surrogate at campaign end: [`reports/figures/surrogate_F1.png`](../reports/figures/surrogate_F1.png).

## 7. Ethical and practical considerations

- Read literally as source detection (contamination, radiation), the real lesson is that a smooth surrogate can report 'nothing here' with high confidence when the signal is simply too narrow for it to resolve. A real deployment would need a sensing model that matches the physics.
- **Provenance.** The function and its supplied data come from the course; the true formula is unknown. Scenario descriptions are illustrations, not claims about real systems.
- **Reuse.** This dataset is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
