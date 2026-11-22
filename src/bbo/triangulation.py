"""Parametric local models for needle-like peaks the GP cannot represent.

An isotropic Gaussian bump has log-magnitude a + b.x + c*|x|^2 (a quadratic
with a single curvature coefficient), so its centre is recoverable by linear
least squares from a handful of readings. Near the peak the same form is
fitted to RAW values for final refinement.
"""
import numpy as np


def isotropic_fit(X, z):
    """Fit z ~ a + b.x + c*|x|^2; return (centre, peak_value, r2, ok).

    ok is False when the stationary point is not a maximum (c >= 0).
    Degrees of freedom = len(z) - (d + 2); treat r2 as meaningless at 0 dof.
    """
    X = np.asarray(X, float)
    z = np.asarray(z, float)
    n, d = X.shape
    A = np.column_stack([np.ones(n)] + [X[:, j] for j in range(d)]
                        + [np.sum(X**2, axis=1)])
    coef, *_ = np.linalg.lstsq(A, z, rcond=None)
    a, b, c = coef[0], coef[1:-1], coef[-1]
    if c >= 0:
        return None, None, None, False
    centre = -b / (2 * c)
    peak = a + b @ centre + c * (centre @ centre)
    pred = A @ coef
    ss = np.sum((z - z.mean())**2)
    r2 = 1 - np.sum((z - pred)**2) / ss if ss > 0 else 1.0
    return centre, peak, r2, True


def triangulate(X, y, k=None, radius=None, anchor=None, use_log_magnitude=True):
    """Triangulate a peak from the most informative readings.

    Select points by top-k log-magnitude (far-field source location) or by
    radius around an anchor (near-peak refinement). Set
    use_log_magnitude=False once readings are O(1) near the peak.
    """
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    z = np.log(np.abs(y) + 1e-300) if use_log_magnitude else y
    if radius is not None and anchor is not None:
        m = np.linalg.norm(X - np.asarray(anchor), axis=1) < radius
        return isotropic_fit(X[m], z[m])
    idx = np.argsort(z)[-k:]
    return isotropic_fit(X[idx], z[idx])


def consensus_centre(X, y, ks=(5, 6, 7, 8), use_log_magnitude=True, tol=0.02):
    """Average the centres from several top-k subsets; raise if they disagree.

    The subset-agreement check is the guard that caught the week-1 F1 failure:
    a single unvalidated fit is never trusted on its own.
    """
    centres = []
    for k in ks:
        c, _, _, ok = triangulate(X, y, k=k, use_log_magnitude=use_log_magnitude)
        if ok:
            centres.append(c)
    assert centres, "no subset produced a peak"
    centres = np.array(centres)
    spread = np.ptp(centres, axis=0).max()
    assert spread < tol, f"subsets disagree by {spread:.4f} (> {tol})"
    return centres.mean(axis=0)
