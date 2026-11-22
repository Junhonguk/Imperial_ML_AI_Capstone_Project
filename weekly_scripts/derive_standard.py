#!/usr/bin/env python3
"""Phase-1 derivation (weeks 1-3): full-domain GP + EI per function.

Reproduces the early-campaign query selection given a data snapshot:
truncate data/function_N/observations.csv to the rows available that week.
"""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bbo import acquisition, data, surrogates

# per-function week-1 settings (see reports): transform, noise, xi
SETTINGS = {
    1: dict(transform="logabs", xi=0.0),   # replaced by triangulation in practice
    2: dict(noisy=True, xi=0.05),
    3: dict(xi=0.01),
    4: dict(xi=0.05),
    5: dict(transform="log", xi=0.01),
    6: dict(xi=0.02),
    7: dict(xi=0.02),
    8: dict(xi=0.01),
}

if __name__ == "__main__":
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    for i, cfg in SETTINGS.items():
        X, y = data.load(data_dir, i)
        z = surrogates.transform(y, cfg.get("transform", "raw"))
        gp = surrogates.fit_gp(X, z, noisy=cfg.get("noisy", False))
        q, ei = acquisition.propose(gp, X.shape[1], z.max(), xi=cfg["xi"])
        mu, sd = gp.predict(q.reshape(1, -1), return_std=True)
        print(f"F{i}: {data.portal_format(q)}  mu={mu[0]:.4g} sd={sd[0]:.4g} EI={ei:.4g}")
