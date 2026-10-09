"""Phase 1: how well does each graph align with KuaiRec's true rewards?

Usage (from the repo root, after graphs.py):
    .venv/bin/python -I experiments/kuairec/alignment.py [--model R1]

I2I graphs are scored on each user's row of means (a signal over videos).
U2U graphs are scored on each video's column of means (a signal over users),
and their smoothing test asks whether pooling across users keeps each user's
best video. Every real graph is compared with its degree-preserving rewiring
and an Erdos-Renyi graph with the same edges and weights.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.sparse.linalg import splu

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import RESULTS, load_eval  # noqa: E402
from graphs import K_DEFAULT, graph_dir, load_graph, scaled_laplacian  # noqa: E402

LAMBDAS = (0.1, 1.0, 10.0)
RANDOM_PAIRS = 20_000
SEED = 20261009


def graph_names(k: int) -> list[str]:
    return sorted(p.stem for p in graph_dir(k).glob("*.npz"))


def smoothness(X: np.ndarray, L: sp.csr_matrix) -> np.ndarray:
    """Quotient per column of X (nodes along rows); about 1 for a random graph."""
    energy = np.einsum("ij,ij->j", X, L @ X)
    var = ((X - X.mean(axis=0)) ** 2).sum(axis=0)
    return energy / var


def homophily(X: np.ndarray, W: sp.csr_matrix, rng: np.random.Generator) -> tuple[float, float]:
    """Mean correlation of node profiles over edges, and over random node pairs."""
    Z = X - X.mean(axis=1, keepdims=True)
    Z /= np.linalg.norm(Z, axis=1, keepdims=True) + 1e-12
    T = sp.triu(W, 1).tocoo()
    edge = float(np.einsum("ij,ij->i", Z[T.row], Z[T.col]).mean()) if T.nnz else np.nan
    a, b = rng.integers(X.shape[0], size=(2, RANDOM_PAIRS))
    keep = a != b
    rand = float(np.einsum("ij,ij->i", Z[a[keep]], Z[b[keep]]).mean())
    return edge, rand


def choice_quality(M: np.ndarray, S: np.ndarray) -> dict[str, float]:
    """Compare each user's best video under smoothed means S with the truth M (users x videos)."""
    best = M.argmax(axis=1)
    pick = S.argmax(axis=1)
    rows = np.arange(M.shape[0])
    spread = M.max(axis=1) - M.mean(axis=1)
    top10_true = np.argpartition(-M, 10, axis=1)[:, :10]
    top10_s = np.argpartition(-S, 10, axis=1)[:, :10]
    overlap = np.mean([len(np.intersect1d(x, y)) / 10 for x, y in zip(top10_true, top10_s)])
    return {
        "top1_kept": float((best == pick).mean()),
        "top10_overlap": float(overlap),
        "choice_regret": float(((M[rows, best] - M[rows, pick]) / spread).mean()),
    }


def score(name: str, M: np.ndarray, rng: np.random.Generator, k: int) -> tuple[dict, np.ndarray]:
    W = load_graph(name, k)
    L = scaled_laplacian(W)
    axis = "I2I" if name.startswith("I-") else "U2U"
    X = M.T if axis == "I2I" else M  # graph nodes along rows
    q = smoothness(X, L)
    edge_corr, rand_corr = homophily(X, W, rng)
    deg = np.asarray((W > 0).sum(axis=1)).ravel()
    base, _, null = name.partition("~")
    # Personal signal only: remove each user's activity level and each video's popularity.
    D = M - M.mean(axis=1, keepdims=True) - M.mean(axis=0, keepdims=True) + M.mean()
    Xd = D.T if axis == "I2I" else D
    edge_dc, rand_dc = homophily(Xd, W, rng)
    row = {
        "graph": base,
        "k": k,
        "null": null or "real",
        "axis": axis,
        "nodes": W.shape[0],
        "edges": int(sp.triu(W, 1).nnz),
        "isolated": int((deg == 0).sum()),
        "quotient_median": float(np.median(q)),
        "quotient_mean": float(q.mean()),
        "edge_corr": edge_corr,
        "random_pair_corr": rand_corr,
        "quotient_dc_median": float(np.median(smoothness(Xd, L))),
        "edge_corr_dc": edge_dc,
        "random_pair_corr_dc": rand_dc,
    }
    eye = sp.identity(W.shape[0], format="csc")
    for lam in LAMBDAS:
        lu = splu((eye + lam * L).tocsc())
        Xs = lu.solve(np.asfortranarray(X))
        S = Xs.T if axis == "I2I" else Xs
        for key, val in choice_quality(M, S).items():
            row[f"{key}@{lam:g}"] = val
    return row, q


def main(model: str, k: int) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    _, _, M = load_eval(model)
    M = M.astype(np.float64)
    M = np.where(np.isnan(M), np.nanmean(M, axis=1, keepdims=True), M)  # 0.4% blocked pairs
    rows, signals = [], []
    for name in graph_names(k):
        row, q = score(name, M, rng, k)
        rows.append(row)
        signals.append(pd.DataFrame({"graph": row["graph"], "null": row["null"], "quotient": q}))
        print(f"{name:22s} quotient={row['quotient_median']:.3f} top1@1={row['top1_kept@1']:.3f}", flush=True)
    out = pd.DataFrame(rows).sort_values(["axis", "graph", "null"])
    out.to_csv(RESULTS / f"alignment_summary_{model}_k{k}.csv", index=False)
    pd.concat(signals).to_csv(RESULTS / f"alignment_signals_{model}_k{k}.csv.gz", index=False)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="R1", choices=["R1", "R2", "R3"])
    ap.add_argument("--k", type=int, default=K_DEFAULT)
    args = ap.parse_args()
    main(args.model, args.k)
