"""Expected Improvement and constrained proposal search."""
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm

EPS = 1e-6


def expected_improvement(gp, Xc, z_best, xi):
    mu, sd = gp.predict(Xc, return_std=True)
    sd = np.maximum(sd, 1e-12)
    imp = mu - z_best - xi
    z = imp / sd
    return imp * norm.cdf(z) + sd * norm.pdf(z)


def propose(gp, d, z_best, xi=0.01, lo=None, hi=None, fixed=None,
            objective="ei", n_candidates=50_000, n_restarts=10, seed=0):
    """Maximise an objective over an optional box with optional fixed dims.

    objective: 'ei' (default) or 'mean' (posterior-mean argmax - the endgame
    objective for noisy functions). lo/hi give a trust-region box; `fixed`
    maps dim index -> value for face/edge-restricted searches.
    Returns (point, objective value).
    """
    rng = np.random.default_rng(seed)
    lo = np.full(d, EPS) if lo is None else np.clip(lo, EPS, 1 - EPS)
    hi = np.full(d, 1 - EPS) if hi is None else np.clip(hi, EPS, 1 - EPS)
    score = ((lambda Xc: expected_improvement(gp, Xc, z_best, xi))
             if objective == "ei" else (lambda Xc: gp.predict(Xc)))
    cand = rng.uniform(lo, hi, size=(n_candidates, d))
    if fixed:
        for j, v in fixed.items():
            cand[:, j] = v
    free = [j for j in range(d) if not fixed or j not in fixed]
    starts = cand[np.argsort(score(cand))[-n_restarts:]][:, free]

    def assemble(xf):
        x = np.empty(d)
        x[free] = xf
        if fixed:
            for j, v in fixed.items():
                x[j] = v
        return x

    def neg(xf):
        return -score(assemble(xf).reshape(1, -1))[0]

    best, bv = None, np.inf
    for s in starts:
        r = minimize(neg, s, bounds=list(zip(lo[free], hi[free])),
                     method="L-BFGS-B")
        if r.fun < bv:
            best, bv = r.x, r.fun
    return np.clip(assemble(best), EPS, 1 - EPS), -bv
