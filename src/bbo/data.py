"""Loading, appending and validating observations."""
from pathlib import Path
import csv
import numpy as np

EPS = 1e-6


def load(data_dir, i):
    """Return (X, y): initial data plus all weekly observations for function i."""
    d = Path(data_dir) / f"function_{i}"
    X = np.load(d / "initial_inputs.npy")
    y = np.load(d / "initial_outputs.npy").ravel()
    obs = d / "observations.csv"
    if obs.exists():
        rows = np.loadtxt(obs, delimiter=",", skiprows=1, ndmin=2)
        if rows.size:
            X = np.vstack([X, rows[:, :-1]])
            y = np.concatenate([y, rows[:, -1]])
    return X, y


def append(data_dir, i, x, y):
    """Append one weekly (query, result) row to observations.csv."""
    d = Path(data_dir) / f"function_{i}" / "observations.csv"
    new = not d.exists()
    with open(d, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow([f"x{j+1}" for j in range(len(x))] + ["y"])
        w.writerow(list(x) + [y])


def portal_format(x):
    """Render a point as the portal string: 0.xxxxxx-0.xxxxxx-..."""
    x = np.clip(np.asarray(x, dtype=float), EPS, 1 - EPS)
    return "-".join(f"{v:.6f}" for v in x)


def validate(query, dim):
    """Raise if a portal string is malformed for a d-dimensional function."""
    parts = query.split("-")
    assert len(parts) == dim, f"expected {dim} coords, got {len(parts)}"
    for p in parts:
        assert p.startswith("0."), f"coordinate {p!r} must start with '0.'"
        assert len(p.split(".")[1]) == 6, f"coordinate {p!r} must have 6 decimals"
        v = float(p)
        assert 0 < v < 1, f"coordinate {p!r} out of (0, 1)"
    return True
