#!/usr/bin/env python3
"""Weekly driver: refit every function and print next queries + predictions.

Usage:  python scripts/weekly_run.py [--data DATA_DIR]
Append last week's results to data/function_N/observations.csv first
(or use bbo.data.append).
"""
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bbo import acquisition, data, surrogates, triangulation
from bbo.config import CONFIG


def run(data_dir):
    for i, cfg in CONFIG.items():
        X, y = data.load(data_dir, i)
        regime = cfg["regime"]
        if regime == "bank":
            q = np.asarray(cfg["best"], float)
            print(f"F{i}: {data.portal_format(q)}   (bank best-known point)")
            continue
        if regime == "triangulate":
            inc = X[np.argmax(y)]
            if cfg.get("value_fit_near_peak"):
                m = y > 0.5 * y.max()
                c, pk, r2, ok = triangulation.isotropic_fit(X[m], y[m])
            else:
                c, pk, r2, ok = triangulation.triangulate(
                    X, y, radius=cfg.get("radius"), anchor=inc,
                    use_log_magnitude=(cfg.get("transform") == "logabs"))
            assert ok, f"F{i}: fit is not a peak - fall back to trust region"
            print(f"F{i}: {data.portal_format(c)}   (triangulated centre, "
                  f"predicted peak ~ {pk:.4g}, R2 = {r2:.3f})")
            continue
        z = surrogates.transform(y, cfg.get("transform", "raw"))
        gp = surrogates.fit_gp(X, z, noisy=cfg.get("noisy", False),
                               ls_hi=cfg.get("ls_hi", 10.0))
        inc = X[np.argmax(z)]
        lo = hi = None
        if "box_half" in cfg:
            lo, hi = inc - cfg["box_half"], inc + cfg["box_half"]
        elif "box" in cfg:
            lo, hi = np.asarray(cfg["box"][0]), np.asarray(cfg["box"][1])
        q, _ = acquisition.propose(
            gp, cfg["dim"], z.max(), xi=cfg.get("xi", 0.01), lo=lo, hi=hi,
            fixed=cfg.get("fixed"),
            objective=("mean" if regime == "mean_argmax" else "ei"))
        mu, sd = gp.predict(q.reshape(1, -1), return_std=True)
        print(f"F{i}: {data.portal_format(q)}   (mu = {mu[0]:.4g} "
              f"+/- {sd[0]:.4g}, regime = {regime})")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data")
    run(p.parse_args().data)
