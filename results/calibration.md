# Calibration record — predictions vs results

Every weekly query is submitted with a predicted mu +/- sd from the model that
chose it; the next week's result grades the prediction. In-window rates and the
regime changes each miss triggered:

| Week | In window | Misses and consequences |
|------|-----------|--------------------------|
| 1 -> 2 | 5/7 graded | F4, F7 beat their bands (upside); F1 quadratic MISSED badly -> refit on strongest readings only |
| 2 -> 3 | 6/8 | F7 miss below -> peak sharper than modelled; F5 ridge test bounded the ridge |
| 3 -> 4 | 7/8 | F4 hard miss -> trust region adopted (ls cap, +/-0.08 box) |
| 4 -> 5 | 6/8 | F2 miss at the incumbent's doorstep -> noise sd ~ 0.06 measured; F4 crash -> box shrunk to +/-0.02 |
| 5 -> 6 | 6/8 | F3 sd overconfident; F6 x5-up hurt -> tighter, humbler boxes |
| 6 -> 7 | 7/8 | F5 ABOVE band (+33% record) -> edge sweep accelerated; F7 4th record, nearly exact |
| 7 -> 8 | 8/8 | perfect calibration week; 4 new bests |
| 8 -> 9 | 6/8 | F3/F6 marginal; F1 fit predicted 2.0009, observed 1.99994 |
| 9 -> 10 | 7/8 | F6 broke its band UPWARD (-0.137); F8 plateau cracked |

Headline predictions that landed: F1 predicted ~2.0009 -> 1.99994, then
~2.00001 -> 1.999987 (the true max is almost certainly 2.0 exactly);
F7 predicted 2.799 -> observed 2.7945; F4 triangulated centre predicted
~0.6 -> observed 0.5721 / 0.5978 / 0.6004 across three refinements.

Full per-query record: query_log.csv. Regime history and lessons: README.md.
