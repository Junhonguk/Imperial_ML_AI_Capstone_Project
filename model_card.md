# Model card: regime-switching Bayesian optimisation for the BBO capstone

| | |
|---|---|
| **Version** | 1.0.0 (`src/bbo/__init__.py`). Snapshot after 9 graded rounds; week 10 submitted, results pending |
| **Type** | Sequential decision procedure: a GP surrogate with Expected Improvement, plus trust-region, parametric-fit, posterior-mean and bank regimes |
| **Code** | `src/bbo/` (package), `scripts/weekly_run.py` (driver), `src/bbo/config.py` (per-function regimes) |
| **Data** | `data/function_{1..8}/`, documented in [`datasheets/`](datasheets/README.md) |
| **Dependencies** | numpy 2.4.4, scipy 1.16.3, scikit-learn 1.8.0 |

## Overview

The "model" here is a procedure, not one fitted predictor. Each week it takes
all observations of a black-box function so far and returns two things:

- one point to query next;
- a prediction (mean ± sd) for that point, which the following week's result
  grades.

It runs on eight functions of dimension 2 to 8, each maximised over [0, 1]^d.
The budget is 13 queries per function, one per week, and each result takes 7
days to return.

## Intended use

**In scope**
- Maximising expensive black-box functions that are noisy or noise-free, in
  low dimensions (d ≤ 8), on a box domain.
- Tight budgets of about 10–50 evaluations on top of an initial design, with
  a person reviewing each proposal before it is submitted.
- Settings that need an audit trail. Every query can be reproduced from
  `config.py`, the data snapshot and a pinned seed, and it comes with a
  written prediction.

**Out of scope**
- **Fully automatic use.** A person chooses the regime switches (trust
  region, triangulation, posterior mean, bank) by reading the calibration
  record.
- **Batch or parallel evaluation, constraints, or several objectives.** None
  of these are supported.
- **High dimensions** (d well above 8) or large datasets. Exact GP inference
  costs O(n³), and the candidate sweep is uniform random.
- **Safety-critical settings** where a bad query does harm. The procedure
  deliberately takes exploratory risks.

## Model description

**Inputs**
- All observations so far for one function: the supplied design plus the
  graded queries, as `(X, y)` with `X` in [0, 1]^d.
- That function's entry in `config.py`: regime, output transform, noise flag,
  lengthscale cap, trust-region half-width or fixed box, and ξ.

**Outputs**
- One query point, clipped to [1e-6, 1 − 1e-6] and formatted for the portal
  with six decimals per coordinate.
- A predicted mean and standard deviation. In the triangulate regime, it is a
  fitted peak value and R² instead.

**Architecture.** There are four layers, and each is used only where the one
before it failed.

| Layer | Component | Used for |
|---|---|---|
| 1. Surrogate | GP with a Matérn 5/2 ARD kernel, `normalize_y`, and maximum-likelihood hyperparameters (10 restarts). Optional WhiteKernel, output transform (`log`, `logabs`) and lengthscale cap | All functions, every week |
| 2. Acquisition | Expected Improvement with ξ decaying over time, maximised by a 50k random sweep plus 10 L-BFGS-B restarts. Optional trust-region box, fixed box, or face (some inputs fixed). Posterior-mean objective for noisy functions | Global search in weeks 1–3; local search after that |
| 3. Parametric fit | Isotropic quadratic `a + b·x + c·‖x‖²`, fitted by least squares on `log\|y\|` far from the peak and on raw `y` near it, with a consensus check across top-k subsets | Needle-like peaks: F1, F4 |
| 4. Calibration controller | A written prediction for every query, graded when the result returns. A hard miss, or two misses in a row, triggers a regime change. The box grows about 1.5× after a record and shrinks about 0.5× after a miss | All functions |

**Current regime for each function** (`config.py`, used for the week-10 queries):

| Fn | Regime | Settings |
|---|---|---|
| F1 | `triangulate` | value fit near the peak |
| F2 | `mean_argmax` | noisy; box `[0.64, 0.75] × [0.92, 1.0]` |
| F3 | `trust_region` | half-width 0.03 |
| F4 | `triangulate` | radius 0.13 |
| F5 | `bank` | the corner (1, 1, 1, 1) |
| F6 | `trust_region` | half-width 0.08, `ls_hi` 1.0 |
| F7 | `trust_region` | half-width 0.04, `ls_hi` 2.0 |
| F8 | `trust_region` | half-width 0.03, `ls_hi` 4.0 |

## Performance

Four measures are used:

- **Best observed value.** This is how the task is scored.
- **Improvement over the supplied design.** This attributes the result to the
  search rather than to the starting data.
- **Calibration hit rate.** The share of written predictions that fall inside
  their stated range. This is the only test of the surrogate where it is
  actually used: extrapolation to a point not yet seen.
- **Headline prediction error.** How far the main predictions were from what
  came back.

| Fn | Dim | Supplied best | Best after week 9 | Gain | Records (weeks) |
|----|-----|-------------:|------------------:|-----:|-----------------|
| 1 | 2 | 7.7e-16 | 1.9999868 | +2.0 (apparent max 2.0; gap 1.3e-5) | 4 (1, 2, 8, 9) |
| 2 | 2 | 0.6112 | 0.6612264 | +0.050 | 3 (4, 8, 9) |
| 3 | 3 | -0.03484 | -0.0081869 | +0.027 | 1 (5) |
| 4 | 4 | -4.0255 | 0.6003521 | +4.63 | 5 (1, 2, 7, 8, 9) |
| 5 | 4 | 1088.86 | 8662.405001 | ×7.96 | 6 (1, 3–7) |
| 6 | 5 | -0.71427 | -0.1368005 | +0.577 | 4 (1, 2, 7, 9) |
| 7 | 6 | 1.36497 | 2.7944726 | +1.43 (×2.05) | 4 (1, 4, 6, 7) |
| 8 | 8 | 9.59848 | 9.9347415 | +0.336 | 3 (1, 2, 9) |

**Calibration.** 58 of 71 predictions (82%) landed inside their stated
range. The rate per round ran from 5/7 to 8/8, and round 7 was perfect. See
[`results/calibration.md`](results/calibration.md) and
[`reports/figures/calibration_hits.png`](reports/figures/calibration_hits.png).

**Headline errors**

| Fn | Predicted | Observed | Error |
|---|---|---|---|
| F1 | 2.0009 | 1.99994 | 1e-3 |
| F1 | 2.00001 | 1.999987 | 2e-5 |
| F7 | 2.799 | 2.7945 | 5e-3 |

F4's triangulated centre predicted about 0.6. Three refinements returned
0.572, 0.598 and 0.600.

## Assumptions

- **The surface is smooth at the scale the GP can resolve.** This fails for
  the needle-like peaks of F1 and F4, which is why layer 3 exists.
- **Noise is assumed only where measured.** F2 is modelled with noise sd of
  about 0.06, because nearby replicate queries returned very different
  values. Every other function is fitted as noise-free.
- **Optima may lie inside the box or on its boundary.** Boundary optima are
  reachable through clipping to [1e-6, 1 − 1e-6]. F5's best point is at a
  corner; F2, F7 and F8 sit on faces.

## Limitations

- **GPs cannot see needles.** For the first rounds, the full-domain GP on F1
  predicted near zero everywhere. Progress only came from switching to a
  parametric fit on log-magnitudes, which jumped from about 2e-11 to 1.989
  in week 2.
- **The F2 noise model is not yet confirmed.** Two readings about 0.004 apart
  near the best point (weeks 4 and 5) returned 0.646 and 0.489. The current regime treats this as
  noise and maximises the posterior mean. A replicate query is the cheapest
  way to test that assumption.
- **F3 has stalled since week 5.** It has one record in nine weeks. Local
  queries in weeks 7–9 returned -0.013 to -0.030, so the peak is narrower
  than the GP's lengthscales.
- **Regime choice is manual.** The regime switches are rule-guided
  judgement, not code. The procedure is auditable but not a turnkey
  optimiser.
- **No cross-validation for surrogate choice.** The calibration record
  measures performance on new points. A leave-one-out comparison across
  surrogate families would be a cheap extra check, and it is the first thing
  to add.

## Trade-offs

- **Local regimes vs exploring the whole space.** Trust regions and
  triangulation have produced steady records on F4, F6 and F8. The cost is
  that once a function is in a local regime, nothing outside the box is
  queried, so a better optimum elsewhere would be missed.
- **Spending queries on information vs on score.** F5's probes stepping back
  from the corner (weeks 8 and 9) scored below it, but they support the
  corner as the maximum. Week 10 re-queries the corner, which banks the
  value and also tests whether repeat readings are identical.
- **Capped lengthscales vs fit.** Capping `ls_hi` stops ARD from declaring an
  input irrelevant, but it costs marginal likelihood. Several fitted
  lengthscales sit at their caps.
- **Interpretability vs flexibility.** Isotropic quadratics are crude, but
  they give a closed-form vertex and a fit quality you can check. Within
  their small region they have predicted much better than the GP.

## Where performance degrades

- Peaks that are narrow relative to the data spacing: F1, F3 and F4 before
  their regime switches.
- Outputs spanning many orders of magnitude without a transform: F5 on the
  raw scale, and F1.
- High dimension combined with a small trust region. In F8 (8D), the value
  sat at 9.930 from week 2 until week 9.

## Ethical considerations and reproducibility

- **No personal or sensitive data.** The functions are synthetic and come
  from the course. Scenario hints such as "drug side-effects" and "chemical
  yield" are illustrations only.
- **Honest reporting.** Every query is reported, including misses, and the
  calibration record shows failed predictions as well as successful ones.
- **Reproducibility.** Dependencies and seeds are pinned, and the supplied
  data is kept unmodified. On this snapshot, `weekly_run.py` regenerates the
  submitted week-10 queries exactly for F1–F6, and for F7 and F8 to within
  2e-6 per coordinate.
- **Transfer to real use.** On a real experiment, exploratory queries carry
  real cost and risk. The human review step and the written predictions
  should stay, and a safety constraint should be added to the proposer.

## Related documents

- [`README.md`](README.md): overview, results and workflow.
- [`datasheets/`](datasheets/README.md): data provenance and composition.
- [`results/calibration.md`](results/calibration.md): predictions against results, week by week.
- [`docs/literature.md`](docs/literature.md): the methods each component is based on.
