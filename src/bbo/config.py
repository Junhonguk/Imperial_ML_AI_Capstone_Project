"""Per-function regimes - the whole strategy, expressed as data.

Edit THIS file each week as calibration results come in; the code elsewhere
never changes. Regimes:
  'ei'            standard EI over the full domain
  'trust_region'  EI in a box around the incumbent (capped lengthscales)
  'face'          EI with some dimensions fixed (edge/face restriction)
  'triangulate'   query the parametric fit centre (needle peaks)
  'mean_argmax'   posterior-mean argmax (noisy endgame)
  'bank'          re-query the best-known point (final weeks)
"""

CONFIG = {
    1: dict(dim=2, regime="triangulate", transform="logabs", value_fit_near_peak=True,
            note="solved: peak (0.628534, 0.628592), f -> 2.0"),
    2: dict(dim=2, regime="mean_argmax", noisy=True, box=([0.64, 0.92], [0.75, 1.0]),
            note="noise sd ~ 0.06 measured; replicate-average the best region"),
    3: dict(dim=3, regime="trust_region", box_half=0.03, xi=0.002,
            note="incumbent (0.484, 0.760, 0.488); quadratic locally imperfect"),
    4: dict(dim=4, regime="triangulate", transform="raw", radius=0.13,
            note="converged: centre (0.4088, 0.4008, 0.3650, 0.4114), peak ~ 0.60"),
    5: dict(dim=4, regime="bank", best=[1 - 1e-6] * 4,
            note="corner is the max; 3 interaction probes all lost"),
    6: dict(dim=5, regime="trust_region", box_half=0.08, xi=0.003, ls_hi=1.0,
            note="momentum: -0.714 -> -0.137 and climbing"),
    7: dict(dim=6, regime="trust_region", box_half=0.04, xi=0.002, ls_hi=2.0,
            note="plateau 2.79 after 4 records"),
    8: dict(dim=8, regime="trust_region", box_half=0.03, xi=0.001, ls_hi=4.0,
            note="plateau cracked at 9.9347; keep tight"),
}

# Exploration-margin schedule used over the campaign (for the report):
# weeks 1-3: xi 0.01-0.05 by function difficulty; weeks 4-7: 0.005-0.02;
# weeks 8+: <= 0.005 (exploit), noisy functions switch to mean_argmax.
