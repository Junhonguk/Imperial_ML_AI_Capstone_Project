#!/usr/bin/env python3
"""Phase-3 derivation: parametric peak fitting (F1 and F4).

Week 1-2 (F1): isotropic quadratic on LOG-MAGNITUDES of the strongest
readings locates a hidden Gaussian-type source (consensus across top-k
subsets guards against the week-1 failure mode).
Weeks 7+ (F1, F4): the same isotropic form on RAW values refines the peak.
Weeks 11-13 (F1): 1D parabolas along one axis squeeze the final digits.
"""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bbo import data
from bbo.triangulation import consensus_centre, triangulate, parabola_step

if __name__ == "__main__":
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"

    # F1: source location from log-magnitudes (early weeks)
    X, y = data.load(data_dir, 1)
    centre = consensus_centre(X, y, use_log_magnitude=True)
    print(f"F1 source (log-magnitude consensus): {data.portal_format(centre)}")

    # F1: near-peak refinement on raw values (later weeks)
    m = y > 0.5 * max(y.max(), 1e-9)
    if m.sum() >= 5:
        c, pk, r2, ok = triangulate(X[m], y[m], k=m.sum(), use_log_magnitude=False)
        if ok:
            print(f"F1 value-fit centre: {data.portal_format(c)}  peak~{pk:.6f} R2={r2:.3f}")

    # F4: near-peak isotropic fit on raw values
    X, y = data.load(data_dir, 4)
    inc = X[np.argmax(y)]
    c, pk, r2, ok = triangulate(X, y, radius=0.13, anchor=inc, use_log_magnitude=False)
    if ok:
        print(f"F4 triangulated centre: {data.portal_format(c)}  peak~{pk:.3f} R2={r2:.3f}")

    # F1 endgame example: 1D parabola along x2 through the 3 closest readings
    # (xs, ys) from the final weeks:
    v, pred = parabola_step([0.628531, 0.628540, 0.628591],
                            [1.999999464523327, 1.9999998374550185, 1.9999867666124296])
    print(f"F1 final parabola vertex: x2={v:.6f}, predicted y={pred:.9f}")
