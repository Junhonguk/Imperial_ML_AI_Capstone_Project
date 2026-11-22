# Datasheet: Function 1 (2D)

*BBO capstone. Snapshot after 9 graded queries. The week-10 query has been submitted and its result is pending.*
*All numbers come from `data/function_1/` and `results/query_log.csv`.*

---

## 1. Function overview

**Which function?**
Function 1. Description hint: *point "sources", near-zero field*.

**Input dimension and domain**
2D, on the unit hypercube. Queries are submitted with six decimals and clipped to [0.000001, 0.999999].

**How many supplied points?**
10 points: `initial_inputs.npy` has shape (10, 2) and `initial_outputs.npy` has shape (10,).

**What does the output represent?**
Field strength. It is effectively zero everywhere except close to a hidden source, and some readings are slightly negative.

**Objective**
Maximise.

## 2. Nature of the data

**Structure**
Inputs are `float64` in [0, 1]^2. Supplied outputs range from -0.003606 to 7.711e-16, with median 6.794e-80.

The supplied files are kept unmodified. Each graded query is appended as one row of `observations.csv` (`x1..x2,y`). There are 19 observations so far: 10 supplied and 9 queried.

**How the data evolves**
One point is added per week. The supplied design is space-filling. Early queries spread out (corners, faces, global EI), and later queries cluster within about 0.01–0.08 of the incumbent.

The dataset is therefore becoming dense around the best point and stays sparse elsewhere. That is the right allocation for maximisation, but it makes the data a biased sample of the function as a whole.

**Noise and randomness**
Treated as noise-free. Near-peak readings fall on a smooth quadratic: the value fit gives R² = 1.000 on the current data.

**Observed shape**
A single needle. Among the 10 supplied readings, the median magnitude is about 1e-79 and the largest is 7.7e-16. Three are slightly negative; the smallest is -0.0036. Near the source the peak is a smooth, nearly isotropic bump of height about 2.0, centred near (0.62853, 0.62859).

## 3. Optimisation strategy

**Methods used**
Parametric triangulation instead of GP + EI. Weeks 1–2: an isotropic quadratic fitted to log|y| of the strongest readings locates the source analytically. Weeks 3–9: the same form fitted to raw values of the readings above half the current best (`value_fit_near_peak`).

**Why these methods**
A GP on raw values sees a flat surface at zero and has no gradient to follow. On log-magnitudes a Gaussian-type source becomes a quadratic, and its vertex (the source location) is fixed by a handful of points through least squares. The week-1 log-magnitude fit missed. It was refitted on the strongest readings only, with a consensus check across top-k subsets, and week 2 returned 1.989.

**Current regime** (`src/bbo/config.py`)
`triangulate`. solved: peak (0.628534, 0.628592), f -> 2.0.

## 4. Data handling and preprocessing

- During the location phase the output is transformed to `log(|y| + 1e-300)`. Once the queries were near the peak, raw values are used.
- Inputs are not rescaled, because the domain is already [0, 1]^2.
- No points have been removed or edited. Bad points are kept, because they constrain the surrogate.
- Every query is checked with `bbo.data.validate` before submission: dimension, six decimals, and inside (0, 1).

## 5. Weekly iteration and learning

The week-2 jump from about 2e-11 to 1.989 came from changing the model class, not from tuning it. In weeks 3–7 the 2D value quadratic was refitted and readings drifted between 1.86 and 1.98. The week-8 fit predicted 2.0009 and returned 1.99994. Week 9 predicted about 2.00001 and returned 1.999987.

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
| 10 | `0.628534-0.628591` | *pending* | |

*Record* means the reading beat every earlier observation, including the supplied data.

## 6. Performance and results

Best is 1.9999868 at (0.628534, 0.628592), week 9. The fitted peak is about 2.0. The week-10 query (0.628534, 0.628591) is the latest value-fit centre.

| Supplied best | Best after week 9 | Gain | Best point (week) |
|---:|---:|---:|---|
| 7.710875115e-16 | 1.999986767 | +2 | `0.628534-0.628592` (week 9) |

The surrogate behind the week-10 query is plotted in [`reports/figures/surrogate_F1.png`](../reports/figures/surrogate_F1.png).

## 7. Ethical and practical considerations

- Read literally as source detection, for example contamination or radiation, the lesson is this: a smooth surrogate can say 'nothing here' with high confidence when the signal is simply too narrow for it to resolve. A sensing model has to match the physics.
- **Provenance.** The function and its supplied data come from the course, and the true formula is unknown. The scenario hints are illustrations, not claims about real systems.
- **Reuse.** The data is useful for testing optimisers on the same function. It is not a representative sample of the function (see section 2), so it should not be used to train a global regression model without reweighting.
