# Model card: regime-switching Bayesian optimisation for the BBO capstone

| | |
|---|---|
| **Version** | 1.1.0 (`src/bbo/__init__.py`), final - campaign complete, all 13 rounds graded |
| **Type** | Sequential decision procedure: GP surrogate + Expected Improvement, with trust-region and parametric-fit regimes |
| **Code** | `src/bbo/` (package), `scripts/weekly_run.py` (driver), `src/bbo/config.py` (per-function regimes) |
| **Data** | `data/function_{1..8}/`, documented in [`datasheets/`](datasheets/README.md) |
| **Dependencies** | numpy 2.4.4, scipy 1.16.3, scikit-learn 1.8.0 |

## Overview

The "model" here is a procedure, not one fitted predictor. Each week it takes
every observation of a black-box function so far and outputs one point to
query next. It also outputs a prediction for that point (mean ± sd), which is
graded the following week.

The procedure was used on eight functions of dimension 2 to 8, each
maximised over [0, 1]^d. The budget was 13 queries per function, one per
week, with a 7-day wait for every result.

## Intended use

**In scope**
- Maximising expensive, deterministic or near-deterministic black-box
  functions in low dimensions (d ≤ 8) on a box domain.
- Tight budgets, roughly 10–50 evaluations beyond an initial design, where a
  person reviews every proposal before it is submitted.
- Situations where an audit trail matters. Every query is reproducible from
  `config.py`, the data snapshot and a pinned seed, and it comes with a
  written prediction.

**Out of scope**
- **Fully automatic use.** The regime switches (trust region, triangulation,
  `micro`, `lottery`, `done`) were chosen by a person reading the calibration
  record. Two of them (`micro` and `lottery`) are not implemented as
  automatic proposers at all.
- **Batch or parallel evaluation, constraints, or several objectives.** None
  of these are supported.
- **High dimensions** (d well above 8) or large datasets. Exact GP inference
  costs O(n³) and the candidate sweep is uniform random.
- **Safety-critical settings** where a bad query does harm. The procedure
  deliberately takes exploratory risks.

## Model description

**Inputs**
- Every observation of one function so far: the supplied design plus the
  graded queries, as `(X, y)` with `X` in [0, 1]^d.
- The function's entry in `config.py`: regime, output transform, noise flag,
  lengthscale cap, trust-region half-width, ξ.

**Outputs**
- One query point, formatted for the portal as six decimals per coordinate,
  clipped to [1e-6, 1 − 1e-6].
- A predicted mean and standard deviation for that point. In the triangulate
  regime, a fitted peak value and R² instead.

**Architecture: four layers, each used only where the one before failed.**

| Layer | Component | Used for |
|---|---|---|
| 1. Surrogate | GP, Matérn 5/2 ARD, `normalize_y`, maximum-likelihood hyperparameters (10 restarts). Optional `WhiteKernel`, output transform (`log`, `logabs`) and lengthscale cap | All functions, all weeks |
| 2. Acquisition | Expected Improvement (ξ decaying to 0), maximised by a 50k random sweep plus 10 L-BFGS-B restarts. Optional trust-region box or fixed-input face; posterior-mean objective as an alternative | Global search (weeks 1–3); local search afterwards |
| 3. Parametric fit | Isotropic quadratic `a + b·x + c·‖x‖²` by least squares. On `log\|y\|` far from the peak, raw `y` near it, then 1D parabolas. Consensus check across top-k subsets | Needle-like peaks: F1, F4 |
| 4. Calibration controller | A written prediction for every query, graded on return. One hard miss or two misses in a row trigger a regime change; a trust region grows ×1.5 on a record and shrinks ×0.5 on a miss | All functions |

**Final regime for each function** (from `config.py`):

| Fn | Regime | Key settings |
|---|---|---|
| F1 | `micro` | 1D parabola steps |
| F2 | `lottery` | periodic micro-spikes, period 2.71e-4 |
| F3 | `trust_region` | half-width 0.006, `ls_hi` 0.2 |
| F4 | `triangulate` | radius 0.13, raw values |
| F5 | `done` | corner (1, 1, 1, 1) |
| F6 | `trust_region` | half-width 0.02, `ls_hi` 0.5 |
| F7 | `trust_region` | half-width 0.008, `ls_hi` 2.0 |
| F8 | `trust_region` | half-width 0.015, `ls_hi` 4.0 |

## Performance

Four measures are used, because no single one tells the whole story.

1. **Best observed value.** This is how the course scores the task.
2. **Improvement over the supplied design.** It shows how much came from the
   search rather than from the free sample.
3. **Calibration hit rate.** The share of written predictions that landed
   inside their stated range. It is the only measure that tests the
   surrogate where it is actually used, which is extrapolation to a point
   not yet seen.
4. **Headline prediction error.** The gap between the predicted and realised
   value on the key queries.

| Fn | Dim | Supplied best | Final best | Gain | Records (weeks) |
|----|-----|-------------:|-----------:|-----:|-----------------|
| 1 | 2 | 7.7e-16 | 1.9999998885 | +2.0 (true max 2.0; gap 1.1e-7) | 8 (1, 2, 8–13) |
| 2 | 2 | 0.6112 | 0.7472264 | +0.136 | 4 (4, 8, 9, 13) |
| 3 | 3 | -0.03484 | -0.0081869 | +0.027 | 1 (5) |
| 4 | 4 | -4.0255 | 0.6023985 | +4.63 | 9 (1, 2, 7–13) |
| 5 | 4 | 1088.86 | 8662.405001248297 | ×7.96 (proven max) | 6 (1, 3–7) |
| 6 | 5 | -0.71427 | -0.0610978 | +0.653 | 6 (1, 2, 7, 9, 12, 13) |
| 7 | 6 | 1.36497 | 2.8264462 | +1.46 (×2.07) | 6 (1, 4, 6, 7, 11, 13) |
| 8 | 8 | 9.59848 | 9.9518160 | +0.353 | 7 (1, 2, 9–13) |

- **Calibration:** 82 of 103 predictions (80%) landed inside their stated
  range. The rate per round ran from 5/8 to 8/8, with one perfect round
  (7->8). See [`results/calibration.md`](results/calibration.md) and
  [`reports/figures/calibration_hits.png`](reports/figures/calibration_hits.png).
- **Headline prediction errors:**

  | Fn | Predicted | Realised | Error |
  |---|---|---|---|
  | F1 | 1.99999988 | 1.99999984 | 4e-8 |
  | F1 | 2.0009 | 1.99994 | 1e-3 |
  | F8 | 9.952 | 9.9518 | 2e-4 |
  | F8 | 9.942 | 9.9481 | 6e-3 |
  | F7 | 2.799 | 2.7945 | 5e-3 |
  | F6 | -0.063 | -0.0611 | 2e-3 |

  F4's triangulated centre predicted about 0.6. Its seven refinements returned
  0.572, 0.598, 0.600, 0.601, 0.602, 0.602 and 0.602.

## Assumptions

- **Smoothness at the scale the GP can resolve.** This failed in two
  places: F1 and F4, which have needle-like peaks, and F2, which has
  sub-1e-4 micro-structure. Those cases are why layers 3 and 4 exist.
- **Determinism.** It was first assumed to be uncertain, then tested in week
  10 and confirmed. F2 was modelled as noisy until then.
- **Optima inside or on the box.** Boundary optima are allowed through
  clipping to [1e-6, 1 − 1e-6]. F5's maximum is at a corner; F7 and F8 sit on
  faces.

## Limitations

- **GPs cannot see needles.** For the first rounds on F1, the full-domain GP
  predicted near-zero everywhere. Progress only came from switching to a
  parametric fit on log-magnitudes, which jumped from about 2e-11 to 1.989 in
  week 2.
- **Deterministic micro-structure was misread as noise.** From week 4 to
  week 10, F2's scatter between nearby points was modelled as noise (sd
  about 0.06). The F5 replicate in week 10 showed the functions are
  deterministic. After that, F2's structure was recognised as periodic
  spikes, with only two queries left to exploit it. The first confirmed the
  predicted spike position (0.643); the second landed on a spike far taller
  than any seen (0.7472, +13%). Had determinism been tested earlier, more of
  that structure could have been mined.
- **The budget ran out while F6 was still climbing.** F6 set records in
  weeks 12 and 13 (-0.0975, then -0.0611), and the final surrogate slice
  ([`surrogate_F6.png`](reports/figures/surrogate_F6.png)) still shows an
  upward slope along x5 toward 0. The F6 result is a lower bound on what the
  method could reach.
- **F3 stalled after week 5.** One record in 13 weeks. The local queries
  from week 7 onward returned values between -0.011 and -0.030, the final
  one missing its predicted -0.0063 ± 0.0044. The peak is narrower than the
  capped lengthscale of 0.2 can represent.
- **Some regimes are manual.** `micro` and `lottery` were chosen by a person,
  and the regime switches themselves were judgement calls guided by rules.
  The procedure is auditable but not a turnkey optimiser.
- **Cross-validation was not used to choose surrogates.** The calibration
  record measures performance on new points. A leave-one-out comparison
  across surrogate families would have been a cheap extra check, and it is
  the first thing to add.

## Trade-offs

- **Local regimes vs exploring the whole domain.** Trust regions and
  triangulation gave steady records on F4, F7 and F8. The cost is that once a
  function entered a local regime, nothing outside the box was queried
  again. If a better optimum existed elsewhere, it would have been missed.
- **Spending queries to learn vs to score.** One query (F5, week 10) went on
  a pure replicate that could not possibly score higher. It settled
  determinism for the rest of the campaign. The F5 "audit" probes in weeks
  8, 9 and 11 stepped back from the corner along x2, x3 and x4 (the climb in
  weeks 5–6 had already covered x1). They also scored below the corner, but
  they proved it was the maximum.
- **Capped lengthscales vs a better fit.** Capping `ls_hi` stops ARD from
  calling an input irrelevant. The cost is a worse marginal likelihood:
  scikit-learn warns that several lengthscales sit at their cap.
- **Being able to read the model vs being able to model anything.**
  Isotropic quadratics are crude, but they have a closed-form vertex and a
  fit quality you can check. Within their small region they predicted far
  better than the GP did.

## Where performance degrades

- Narrow peaks relative to the spacing of the data: F1, F3 and F4 before
  their regime switches.
- Outputs over many orders of magnitude without a transform: F5 on a raw
  scale, and F1.
- Structure below the 1e-6 query resolution, or near it: F2.
- Higher dimensions with a small trust region. In F8 (8D), each step moves
  only a little along the inputs that matter, so the gains became small
  (+0.0003 in week 11).

## Ethical considerations and reproducibility

- **No personal or sensitive data.** The functions are synthetic, provided
  by the course. The scenario descriptions ("drug side-effects", "chemical
  yield") are illustrations only; nothing here should be read as a claim
  about real chemistry or medicine.
- **Honest reporting.** Every query is reported, including misses and
  wasted probes. The calibration record shows predictions that failed as
  well as those that succeeded. The two hand-made regimes are labelled as
  such.
- **Reproducibility.** Dependencies and seeds are pinned, and the supplied
  data is kept unmodified. On the final data, `weekly_run.py` regenerates the
  submitted round-13 queries exactly for F3, F4, F5, F6 and F7, and for F8 to
  within 4e-6 per coordinate.
- **Transfer to real use.** If this procedure were applied to a real
  experiment (a lab process, say), the exploratory queries would carry real
  cost and risk. The human review step and the written predictions should be
  kept, and a safety constraint added to the proposer.

## Related documents

- [`README.md`](README.md): overview, results, how to reproduce.
- [`datasheets/`](datasheets/README.md): data provenance and composition.
- [`results/calibration.md`](results/calibration.md): the weekly record of predictions against results.
- [`docs/literature.md`](docs/literature.md): the methods each component is based on.
