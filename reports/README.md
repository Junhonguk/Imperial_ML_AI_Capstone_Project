# Reports

Weekly module reflections are submitted separately through the course
platform.

## Figures

To regenerate every figure, run `python scripts/make_figures.py`.

| Figure | What it shows |
|---|---|
| [`figures/best_so_far.png`](figures/best_so_far.png) | Best value found per function by week. Grey dots are weekly readings; the dashed line is the best value in the supplied data. |
| [`figures/calibration_hits.png`](figures/calibration_hits.png) | Share of written predictions that landed inside their stated range, per graded round (58/71 overall). |
| [`figures/surrogate_F1.png`](figures/surrogate_F1.png), [`F2`](figures/surrogate_F2.png) | GP mean contour for the 2D functions after week 9, with supplied and queried points. An inset zooms in on the latest cluster. |
| [`figures/surrogate_F3.png`](figures/surrogate_F3.png) … [`F8`](figures/surrogate_F8.png) | GP mean ± 2 sd after week 9, varying one input at a time through the best point, with the fitted lengthscales. |

## Week 10 (pending)

These queries have been submitted, and their results have not come back
yet. The predictions come from running `python scripts/weekly_run.py` on the
9-week data, which also regenerates the queries themselves.

| Fn | Submitted query | Prediction | Observed | Record? |
|----|-----------------|------------|---------:|:-------:|
| F1 | `0.628534-0.628591` | value-fit peak ≈ 2.0 (R² 1.000) | | |
| F2 | `0.691909-0.999999` | 0.592 ± 0.064 (posterior mean, noisy GP) | | |
| F3 | `0.513975-0.730029-0.518443` | -0.0102 ± 0.0122 | | |
| F4 | `0.408815-0.400815-0.365021-0.411389` | triangulated fit peak 0.6145 (R² 0.993) | | |
| F5 | `0.999999-0.999999-0.999999-0.999999` | 8662.405 (bank the corner; also a replicate test) | | |
| F6 | `0.427581-0.382223-0.730707-0.724506-0.110571` | -0.089 ± 0.061 | | |
| F7 | `0.000001-0.165421-0.483617-0.274693-0.302544-0.712794` | 2.781 ± 0.041 | | |
| F8 | `0.092957-0.150582-0.136047-0.000001-0.999999-0.471948-0.203583-0.999999` | 9.946 ± 0.010 | | |

When the results arrive:
1. Append them to the `observations.csv` files.
2. Fill in `results/query_log.csv`.
3. Add the round to `results/calibration.md`.
4. Re-run `scripts/make_figures.py` and the notebook.
