"""Per-function regimes at campaign end - the strategy, as data.

Regimes: 'ei' | 'trust_region' | 'face' | 'triangulate' | 'micro' (1D
parabola steps) | 'lottery' (structure below resolution) | 'done' (proven).
"""

CONFIG = {
    1: dict(dim=2, regime="micro",
            note="peak (0.628534, 0.628540); best 1.9999998; true max = 2.0"),
    2: dict(dim=2, regime="lottery",
            note="periodic micro-spikes, period 2.71e-4, heights rising with x1; best 0.6612"),
    3: dict(dim=3, regime="trust_region", box_half=0.006, ls_hi=0.2, xi=0.0,
            note="incumbent (0.484, 0.760, 0.488) = narrow spike; best -0.0082"),
    4: dict(dim=4, regime="triangulate", transform="raw", radius=0.13,
            note="centre converged; 6 straight records to 0.60219"),
    5: dict(dim=4, regime="done", best=[1 - 1e-6] * 4,
            note="corner proven max 8662.405001248297 (4-direction audit; 3x bit-identical)"),
    6: dict(dim=5, regime="trust_region", box_half=0.02, ls_hi=0.5, xi=0.0,
            note="still climbing at campaign end: -0.714 -> -0.0975"),
    7: dict(dim=6, regime="trust_region", box_half=0.008, ls_hi=2.0, xi=0.0,
            note="best 2.8093; plateau cracked twice by tightening"),
    8: dict(dim=8, regime="trust_region", box_half=0.015, ls_hi=4.0, xi=0.0,
            note="5 straight end-phase gains to 9.9481; x5 trending interior"),
}

# Exploration-margin schedule used over the campaign (for the report):
# weeks 1-3: xi 0.01-0.05 by function difficulty; weeks 4-7: 0.005-0.02;
# weeks 8+: <= 0.005 (exploit), noisy functions switch to mean_argmax.
