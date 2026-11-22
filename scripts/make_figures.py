#!/usr/bin/env python3
"""Regenerate every figure in reports/figures/ from data/ and results/.

Usage:  python scripts/make_figures.py [--data DATA_DIR] [--out OUT_DIR]

Figures
  best_so_far.png      best value found vs week, one panel per function
  calibration_hits.png share of predictions landing inside their stated range, per round
  surrogate_F{n}.png   the GP surrogate behind the week-10 queries: a mean contour
                       for the 2D functions, 1D slices through the incumbent otherwise
"""
import argparse
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bbo import data, surrogates  # noqa: E402
from bbo.config import CONFIG  # noqa: E402

# Palette roles (reference data-viz palette, light mode).
BLUE = "#2a78d6"      # categorical slot 1: the one data series
INK = "#0b0b0b"       # primary text
INK_2 = "#52514e"     # secondary text / axes
GRID = "#e4e3df"      # recessive grid
READING = "#a8a7a2"   # individual readings (context, not the story)

# Output transform the surrogate needs per function (see README "Method").
# config.py carries it for live regimes; F5 is banked, so its log-GP is named here.
TRANSFORM = {1: "logabs", 5: "log"}

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": INK_2, "axes.labelcolor": INK_2,
    "xtick.color": INK_2, "ytick.color": INK_2, "axes.titlecolor": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.dpi": 160, "savefig.bbox": "tight",
})


def initial_count(data_dir, i):
    return len(np.load(Path(data_dir) / f"function_{i}" / "initial_outputs.npy").ravel())


def best_so_far(data_dir, out):
    fig, axes = plt.subplots(2, 4, figsize=(13, 5.6))
    for ax, i in zip(axes.ravel(), CONFIG):
        _, y = data.load(data_dir, i)
        n0 = initial_count(data_dir, i)
        init_best, weekly = y[:n0].max(), y[n0:]
        weeks = np.arange(1, len(weekly) + 1)
        running = np.maximum.accumulate(np.concatenate([[init_best], weekly]))

        # Keep the axis on the story: from just below the initial best to the top.
        top = running[-1]
        span = max(top - init_best, abs(top) * 1e-3, 1e-12)
        lo, hi = init_best - 0.15 * span, top + 0.12 * span
        inside = weekly >= lo
        ax.scatter(weeks[inside], weekly[inside], s=18, color=READING,
                   zorder=2, label="weekly reading")
        if (~inside).any():
            ax.scatter(weeks[~inside], np.full((~inside).sum(), lo + 0.02 * span),
                       marker="v", s=18, color=READING, zorder=2,
                       label="reading below axis")
        ax.step(np.arange(0, len(weekly) + 1), running, where="post",
                color=BLUE, lw=2, zorder=3, label="best so far")
        ax.axhline(init_best, color=INK_2, lw=1, ls=(0, (4, 3)), zorder=1,
                   label="best in initial data")
        ax.set_ylim(lo, hi)
        ax.set_xlim(-0.3, len(weekly) + 0.5)
        ax.set_xticks(range(0, len(weekly) + 1, 3))
        ax.set_title(f"F{i} ({CONFIG[i]['dim']}D)   best {top:.8g}", loc="left",
                     fontsize=9.5)
        ax.ticklabel_format(axis="y", useOffset=False)
    for ax in axes[1]:
        ax.set_xlabel("week (0 = initial data)")
    handles, labels = [], []
    for ax in axes.ravel():
        for h, l in zip(*ax.get_legend_handles_labels()):
            if l not in labels:
                handles.append(h)
                labels.append(l)
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False,
               bbox_to_anchor=(0.5, -0.04))
    fig.suptitle(f"Best value found per function over {len(weekly)} graded weeks",
                 x=0.01, ha="left", color=INK, fontsize=11)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    fig.savefig(out / "best_so_far.png")
    plt.close(fig)


def calibration_hits(results_dir, out):
    rows = re.findall(r"^\|\s*(\d+\s*->\s*\d+)\s*\|\s*(\d+)/(\d+)[^|]*\|",
                      (Path(results_dir) / "calibration.md").read_text(),
                      flags=re.M)
    labels = [str(k + 1) for k in range(len(rows))]
    hit = np.array([int(r[1]) for r in rows])
    tot = np.array([int(r[2]) for r in rows])
    fig, ax = plt.subplots(figsize=(8, 3.2))
    x = np.arange(len(rows))
    ax.bar(x, hit / tot, width=0.62, color=BLUE, zorder=2)
    for xi, h, t in zip(x, hit, tot):
        ax.text(xi, h / t + 0.02, f"{h}/{t}", ha="center", va="bottom",
                fontsize=8, color=INK_2)
    overall = hit.sum() / tot.sum()
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1.12)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_xlabel("graded round (rows of results/calibration.md, in order)")
    ax.set_ylabel("inside predicted range")
    ax.grid(axis="x", visible=False)
    ax.set_title("How often a written prediction landed inside its stated range"
                 f"  (overall {hit.sum()}/{tot.sum()} = {overall:.0%})",
                 loc="left", fontsize=10)
    fig.savefig(out / "calibration_hits.png")
    plt.close(fig)


def fit_final_gp(data_dir, i):
    X, y = data.load(data_dir, i)
    how = CONFIG[i].get("transform") or TRANSFORM.get(i, "raw")
    z = surrogates.transform(y, how)
    gp = surrogates.fit_gp(X, z, noisy=CONFIG[i].get("noisy", False),
                           ls_hi=CONFIG[i].get("ls_hi", 10.0))
    return X, y, z, gp, how


def surrogate_2d(data_dir, i, out):
    X, y, z, gp, how = fit_final_gp(data_dir, i)
    n0 = initial_count(data_dir, i)
    g = np.linspace(0, 1, 160)
    G1, G2 = np.meshgrid(g, g)
    mu = gp.predict(np.column_stack([G1.ravel(), G2.ravel()])).reshape(G1.shape)
    fig, ax = plt.subplots(figsize=(5.4, 4.6))
    cs = ax.contourf(G1, G2, mu, levels=14, cmap="Blues")
    cb = fig.colorbar(cs, ax=ax, shrink=0.85)
    cb.set_label("GP mean of log|y|" if how == "logabs" else "GP mean of y")
    ax.scatter(X[:n0, 0], X[:n0, 1], s=22, facecolor="white", edgecolor=INK,
               lw=0.8, label="initial data", zorder=3)
    ax.scatter(X[n0:, 0], X[n0:, 1], s=26, color="#eb6834", edgecolor="white",
               lw=0.8, label="weekly queries", zorder=4)
    b = X[np.argmax(y)]
    ax.scatter(*b, marker="*", s=180, color=INK, edgecolor="white", lw=0.8,
               label=f"best ({b[0]:.4f}, {b[1]:.4f})", zorder=5)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.grid(False)
    ax.legend(loc="upper left", fontsize=7.5, framealpha=0.9)
    near = np.abs(X[n0:] - b).max(axis=1) < 0.01
    if near.sum() >= 3:  # late queries hide under the star: zoom in on them
        r = max(np.abs(X[n0:][near] - b).max() * 1.6, 1e-4)
        ins = ax.inset_axes([0.60, 0.04, 0.37, 0.37])
        ins.scatter(X[n0:][near, 0], X[n0:][near, 1], s=16, color="#eb6834",
                    edgecolor="white", lw=0.6, zorder=3)
        ins.scatter(*b, marker="*", s=110, color=INK, edgecolor="white", lw=0.6,
                    zorder=4)
        ins.set_xlim(b[0] - r, b[0] + r)
        ins.set_ylim(b[1] - r, b[1] + r)
        ins.set_xticks([])
        ins.set_yticks([])
        ins.set_facecolor("white")
        ins.text(0.5, 0.04, f"zoom: {near.sum()} queries within ±{r:.1g}",
                 transform=ins.transAxes, ha="center", fontsize=7, color=INK_2)
        ax.indicate_inset_zoom(ins, edgecolor=INK_2)
    label = "log|y|" if how == "logabs" else "y"
    extra = " (with noise term)" if CONFIG[i].get("noisy") else ""
    ax.set_title(f"F{i}: GP surrogate of {label} after week 9{extra}", loc="left",
                 fontsize=10)
    fig.savefig(out / f"surrogate_F{i}.png")
    plt.close(fig)


def surrogate_slices(data_dir, i, out):
    X, y, z, gp, how = fit_final_gp(data_dir, i)
    d = X.shape[1]
    inc = X[np.argmax(y)]
    ncol = min(d, 4)
    nrow = int(np.ceil(d / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.0 * ncol, 2.5 * nrow),
                             sharey=True, squeeze=False)
    t = np.linspace(0, 1, 301)
    for j in range(nrow * ncol):
        ax = axes.ravel()[j]
        if j >= d:
            ax.set_visible(False)
            continue
        P = np.tile(inc, (len(t), 1))
        P[:, j] = t
        mu, sd = gp.predict(P, return_std=True)
        ax.fill_between(t, mu - 2 * sd, mu + 2 * sd, color=BLUE, alpha=0.18,
                        lw=0, label="mean ± 2 sd")
        ax.plot(t, mu, color=BLUE, lw=2, label="GP mean")
        ax.axvline(inc[j], color=INK_2, lw=1, ls=(0, (4, 3)),
                   label="best point")
        ax.set_xlim(0, 1)
        ax.set_title(f"x{j + 1}  (best at {inc[j]:.3f})", loc="left", fontsize=8.5)
    for ax in axes[:, 0]:
        ax.set_ylabel("log y" if how == "log" else "y")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, -0.06))
    ls = getattr(getattr(gp.kernel_, "k2", None), "length_scale", None)
    sub = ("lengthscales " + ", ".join(f"{v:.2g}" for v in np.atleast_1d(ls))
           if ls is not None else "")
    fig.suptitle(f"F{i}: GP surrogate after week 9, one input varied at a time through "
                 f"the best point   [{sub}]", x=0.01, ha="left", fontsize=10,
                 color=INK)
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))
    fig.savefig(out / f"surrogate_F{i}.png")
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default=str(ROOT / "data"))
    p.add_argument("--results", default=str(ROOT / "results"))
    p.add_argument("--out", default=str(ROOT / "reports" / "figures"))
    a = p.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    best_so_far(a.data, out)
    calibration_hits(a.results, out)
    for i, cfg in CONFIG.items():
        (surrogate_2d if cfg["dim"] == 2 else surrogate_slices)(a.data, i, out)
    print("figures written to", out)


if __name__ == "__main__":
    import warnings
    from sklearn.exceptions import ConvergenceWarning
    warnings.filterwarnings("ignore", category=ConvergenceWarning)
    main()
