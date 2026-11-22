# BBO Capstone: Black-Box Optimisation of Eight Hidden Functions

Sequential Bayesian optimisation of eight **deterministic** black-box functions
(2D to 8D) under a hard budget of **one query per function per week** for 13
weeks. Every function is maximised over the unit hypercube. Status: campaign
complete - all 13 rounds graded. The final round set six new records (see
[`reports/README.md`](reports/README.md#week-13-final-results)).

![Best value found per function](reports/figures/best_so_far.png)

## Non-technical explanation

Imagine eight sealed machines, each with a few dials and a single output
gauge. You cannot open them, and you may set the dials and read the gauge only
once a week per machine. The goal is to find the dial settings that give each
machine its highest reading.

The approach was to build, for every machine, a statistical *imitation* of it
from all the readings so far. The imitation gives a best guess for every dial
setting and says how unsure it is. Each week the next setting was chosen where
the imitation saw the best chance of beating the current record. A written
prediction went in with every query, and when the result came back the
prediction was graded. Wrong predictions were treated as information: they
showed when the imitation was too smooth or too confident, and the strategy
for that machine was changed by rule rather than by feel.

By the end, every machine had beaten the best reading in the data we were
given, in most cases by a wide margin. On one machine (F5) the maximum was
proven, and on another (F1) the result was within 0.0000002 of the true peak.

## Data

| Fn | Dim | Description hint | Supplied points | Queried (graded) | Total |
|----|-----|------------------|---------------:|-----------------:|------:|
| 1 | 2 | point "sources", near-zero field | 10 | 13 | 23 |
| 2 | 2 | noisy log-likelihood | 10 | 13 | 23 |
| 3 | 3 | drug side-effects (outputs <= 0) | 15 | 13 | 28 |
| 4 | 4 | multi-modal, sharp peak | 30 | 13 | 43 |
| 5 | 4 | chemical yield (log-scale) | 20 | 13 | 33 |
| 6 | 5 | recipe score (outputs <= 0) | 20 | 13 | 33 |
| 7 | 6 | hyperparameter surface | 30 | 13 | 43 |
| 8 | 8 | near-linear, plateau | 40 | 13 | 53 |

- The supplied designs are stored **unmodified** as
  `data/function_N/initial_inputs.npy` and `initial_outputs.npy`.
- Each graded query is one row of `data/function_N/observations.csv` (`x1..xd,y`).
  This file is only ever appended to, so the supplied points and the queried
  points can always be told apart.
- `results/query_log.csv` holds all 104 submissions: week, function, the
  portal string, the observed value, and a new-best flag.
- Queries use the portal format: hyphen-separated, six decimals per
  coordinate, usable domain `[0.000001, 0.999999]`.
- Determinism was tested directly. The F5 corner was queried four times
  (weeks 7, 10, 12 and 13) and returned `8662.405001248297` bit-for-bit each time.

Full provenance and composition: [`datasheets/`](datasheets/README.md).

## Model

One framework is used for every function. What differs is the **regime**,
chosen per function and recorded as data in
[`src/bbo/config.py`](src/bbo/config.py).

1. **Surrogate: a Gaussian process** (Matérn 5/2 with one ARD lengthscale per
   input, `normalize_y`, fitted by maximum likelihood with 10 restarts).
   - **Output transforms:** `log y` for F5, whose positive output spans 0.11 to
     8662 (five orders of magnitude), and `log|y|` for F1's early field, whose
     magnitudes span 3e-124 to 2.
   - **Noise:** a `WhiteKernel` for F2 while it looked noisy.
   - **Lengthscale caps** (`ls_hi`) where ARD wrongly declared inputs
     irrelevant.

   Code: [`surrogates.py`](src/bbo/surrogates.py).
2. **Acquisition: Expected Improvement.** EI is maximised by a 50,000-point
   random sweep followed by 10 L-BFGS-B restarts. It can be restricted to a
   box around the incumbent (a trust region) or to a face with some inputs
   held fixed. Late in the campaign it can also maximise the posterior mean
   instead of EI. Code: [`acquisition.py`](src/bbo/acquisition.py).
3. **Parametric triangulation.** This handles needle-like peaks that a GP
   cannot represent. An isotropic quadratic `a + b·x + c·|x|²` is fitted by
   least squares to the strongest local readings and its vertex is queried:
   on log-magnitudes far from the peak, on raw values near it, then as 1D
   parabolas for the last digits. A consensus check across top-k subsets
   rejects fits that disagree. Code: [`triangulation.py`](src/bbo/triangulation.py).
4. **Calibration loop.** Every query was submitted with a written prediction
   (mean ± sd), and the next week's result graded it. Misses triggered
   regime changes. The record is in [`results/calibration.md`](results/calibration.md).

**Regime state machine.** Each function moves through these regimes in order:

| Regime | When it moves on |
|---|---|
| Standard EI | one hard miss, or two misses in a row |
| Trust region (lengthscales capped; box around the incumbent, ×1.5 on a new best, ×0.5 on a miss) | the GP keeps failing on a needle |
| Parametric triangulation | the fit converges |
| Bank or `done` | — |

Two special endgames:
- `micro`: 1D parabola steps (F1).
- `lottery`: structure below the model's resolution (F2).

The model card is [`model_card.md`](model_card.md).

## Hyperparameter optimisation

There are two layers.

- **Inside the surrogate.** Kernel amplitude (1e-3 to 1e3), ARD lengthscales
  and, where used, the noise level are refitted every week by maximising the
  log marginal likelihood, with 10 restarts.
- **Around the surrogate.** These were tuned from the calibration record
  rather than by cross-validation, because every query is an extrapolation
  that cross-validation does not test:

  | Setting | How it changed | Final values |
  |---|---|---|
  | Exploration margin ξ | decayed over the campaign | 0 for every trust-region function |
  | Lengthscale caps `ls_hi` | lowered whenever a sharp peak was missed | F3 0.2 · F6 0.5 · F7 2.0 · F8 4.0 |
  | Trust-region half-width | shrunk on misses, grown on records | F3 0.006 · F6 0.02 · F7 0.008 · F8 0.015 |
  | Triangulation radius (F4) | — | 0.13 |
  | Output transform | chosen per function from the output range | — |

  F7 in week 2 shows why the lengthscale caps matter. A cheap test of an
  input that ARD had declared irrelevant returned 1.18, against a week-1
  record of 2.42, which showed the input matters. From then on, no input was
  allowed to be written off by an uncapped lengthscale.

## Results

Final best values over the complete 13-round campaign. These are recomputed
directly from `data/` by `notebooks/BBO_results.ipynb`.

| Fn | Dim | Initial best | Final best | Found in week | Records | Method that found it |
|----|-----|-------------:|-----------:|:-------------:|:-------:|----------------------|
| 1 | 2D | 7.7e-16 | **1.9999998885** | 13 | 8 | log-magnitude triangulation, then value quadratic, then 1D parabolas (true max 2.0) |
| 2 | 2D | 0.6112 | **0.7472264** | 13 | 4 | periodic micro-spikes (period 2.71e-4) characterised; the final two-period extrapolation gained +13% |
| 3 | 3D | -0.03484 | **-0.0081869** | 5 | 1 | local EI refinement after corner sweeps |
| 4 | 4D | -4.0255 | **0.6023985** | 13 | 9 | trust region, then local triangulation (7 records in a row) |
| 5 | 4D | 1088.86 | **8662.405001248297** | 7 | 6 | log-GP trend-riding to the (1,1,1,1) corner; proven maximum |
| 6 | 5D | -0.71427 | **-0.0610978** | 13 | 6 | trust-region hill climb, still improving at the end |
| 7 | 6D | 1.36497 | **2.8264462** | 13 | 6 | trust region with capped lengthscales |
| 8 | 8D | 9.59848 | **9.9518160** | 13 | 7 | tight trust regions (5 records in the last 5 weeks) |

*Records* counts the weeks that beat everything seen before, including the
supplied data. There were 47 records across 104 graded queries - six of them
in the final round.

Across the campaign, 82 of 103 written predictions (80%) landed inside their
stated range ([`calibration_hits.png`](reports/figures/calibration_hits.png)).
The headline predictions:

| Fn | Predicted | Observed |
|---|---|---|
| F1 | 2.0009 | 1.99994 |
| F1 | 1.99999988 | 1.99999984 |
| F7 | 2.799 | 2.7945 |
| F8 | 9.942 | 9.9481 |
| F8 | 9.952 | 9.9518 |
| F6 | -0.063 | -0.0611 |

Final surrogates for each function are in [`reports/figures/`](reports/figures).

## Repository contents

```
bbo-capstone/
|-- README.md                 <- you are here
|-- model_card.md             <- the optimisation approach, documented as a model
|-- datasheets/               <- dataset overview + one datasheet per function
|-- requirements.txt
|-- data/function_{1..8}/     <- supplied .npy (unmodified) + observations.csv (13 graded rows)
|-- src/bbo/
|   |-- config.py             <- final per-function regimes (the strategy, as data)
|   |-- data.py               <- loading, appending, portal formatting and validation
|   |-- surrogates.py         <- GP factory: transforms, noise term, lengthscale caps
|   |-- acquisition.py        <- EI and posterior-mean search with box and face constraints
|   `-- triangulation.py      <- isotropic quadratic fits, consensus guard, parabola steps
|-- scripts/
|   |-- weekly_run.py         <- weekly driver: refit every function, print queries + predictions
|   `-- make_figures.py       <- regenerates reports/figures/
|-- weekly_scripts/           <- phase-by-phase derivations (standard EI, trust region, triangulation)
|-- results/
|   |-- query_log.csv         <- all 104 submissions
|   `-- calibration.md        <- predictions vs results, round by round
|-- notebooks/BBO_results.ipynb  <- start here: results, figures and a walk through each regime
|-- reports/                  <- figures, week-13 tracking sheet
`-- docs/literature.md        <- the methods each component is based on
```

## Reproducing

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/                                  # 7 tests
python scripts/weekly_run.py                   # re-derives the final (round-13) queries
python scripts/make_figures.py                 # rebuilds reports/figures/
jupyter nbconvert --execute --inplace notebooks/BBO_results.ipynb
```

On the final data, `weekly_run.py` reproduces the submitted round-13 queries
exactly for F3, F4, F5, F6 and F7, and for F8 to within 4e-6 per
coordinate (along its flattest inputs). F1 and F2 were in hand-crafted endgames: their steps are recorded in
`results/query_log.csv` and in `weekly_scripts/derive_triangulation.py`.

To reproduce an earlier week, truncate each `observations.csv` to that
week's rows and run the matching script in `weekly_scripts/`. Seeds are pinned.
Coordinates along nearly flat inputs can still move in the last decimals, but
they stay in the same region.

**Weekly workflow, while the campaign ran:**
1. Append last week's results to `data/function_N/observations.csv` (or
   call `bbo.data.append`).
2. Run `python scripts/weekly_run.py`.
3. Review each printed query and its prediction, then submit it through the
   portal.
4. Log the query in `results/query_log.csv`.

## Nine lessons (full context in `results/calibration.md`)

1. **Transform the output first.** The output scale decides whether a
   surrogate can learn at all.
2. **"Irrelevant" according to ARD is only a hypothesis, so test it
   cheaply.** F7 in week 2 is the example.
3. **Reject uncertainty-bait** (proposals whose mean is below the incumbent).
   Re-admit a point when the evidence flips its mean above the incumbent.
   The F5 corner was refused in week 5, submitted in week 7, and gained 44%.
4. **Sharp peaks punish moving several inputs at once.** Use trust regions
   with capped lengthscales.
5. **On EI ties, prefer a local step** near an incumbent that hasn't been
   refined yet. This gave F3 its first gain.
6. **GPs fail on needles; use parametric local fits.** F1 reached 7 decimals,
   and F4 set 6 records in a row.
7. **Spend one query on a replicate.** It settled determinism versus noise
   for good.
8. **"Noise" may be deterministic micro-structure.** Bracket it, then play
   the lottery below resolution. F2's period was confirmed by prediction,
   twice.
9. **A converged model re-proposing a point already measured means you are
   done.**

## Contact

Questions or corrections: open an issue on this repository, or contact the
author through the course platform.
