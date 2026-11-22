#!/usr/bin/env python3
"""Phase-2 derivation (weeks 4+): trust-region EI with capped lengthscales.

Adopted after calibration misses proved peaks sharper than the GP assumed.
Policy: adopt on one hard (or two consecutive) misses; grow the box ~1.5x on
a new best, shrink ~0.5x on a miss or stagnation.
"""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bbo import acquisition, data, surrogates

# example settings as of the final weeks (see src/bbo/config.py for canon)
BOX = {3: (0.006, 0.2), 6: (0.02, 0.5), 7: (0.008, 2.0), 8: (0.015, 4.0)}

if __name__ == "__main__":
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    for i, (half, ls_hi) in BOX.items():
        X, y = data.load(data_dir, i)
        gp = surrogates.fit_gp(X, y, ls_hi=ls_hi)
        inc = X[np.argmax(y)]
        q, _ = acquisition.propose(gp, X.shape[1], y.max(), xi=0.0,
                                   lo=inc - half, hi=inc + half)
        mu, sd = gp.predict(q.reshape(1, -1), return_std=True)
        print(f"F{i}: {data.portal_format(q)}  mu={mu[0]:.4g} sd={sd[0]:.4g} "
              f"dist={np.linalg.norm(q-inc):.4f}")
