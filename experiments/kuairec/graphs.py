"""Build user-user (U2U) and item-item (I2I) graphs for KuaiRec, plus null graphs.

Usage (from the repo root, after data.py):
    .venv/bin/python -I experiments/kuairec/graphs.py

Leakage rule: no graph sees an evaluation (user, video) pair. User embeddings use
big-matrix interactions with non-evaluation videos only; video embeddings use
interactions from non-evaluation users only.

Every graph is a symmetric kNN graph (union of each node's k nearest neighbours),
with Laplacian L = D - W scaled so the mean weighted degree is 1. Under this
scaling a random graph has smoothness quotient close to 1 for any signal.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.sparse.linalg import svds

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import CACHE, RESULTS, load_interactions, load_social, raw_file  # noqa: E402

GRAPHS = CACHE / "graphs"
K_DEFAULT = 10
SVD_RANK = 64
SEED = 20261009


# ---------------------------------------------------------------- kNN helpers


def knn_from_similarity(S: np.ndarray, k: int, rng: np.random.Generator) -> sp.csr_matrix:
    """Union kNN graph from a dense similarity matrix; ties broken at random."""
    n = S.shape[0]
    S = S.astype(np.float64) + rng.uniform(0.0, 1e-9, size=S.shape)
    np.fill_diagonal(S, -np.inf)
    nbrs = np.argpartition(-S, k, axis=1)[:, :k]
    rows = np.repeat(np.arange(n), k)
    cols = nbrs.ravel()
    vals = np.maximum(S[rows, cols], 0.0)
    A = sp.csr_matrix((vals, (rows, cols)), shape=(n, n))
    W = A.maximum(A.T).tocsr()
    W.eliminate_zeros()
    return W


def cosine_knn(X: np.ndarray, k: int, rng: np.random.Generator) -> sp.csr_matrix:
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    Xn = np.divide(X, norms, out=np.zeros_like(X), where=norms > 0)
    return knn_from_similarity(Xn @ Xn.T, k, rng)


def jaccard_knn(B: sp.csr_matrix, k: int, rng: np.random.Generator) -> sp.csr_matrix:
    """B is a binary node x attribute matrix."""
    B = B.astype(np.float64)
    inter = (B @ B.T).toarray()
    size = np.asarray(B.sum(axis=1)).ravel()
    union = size[:, None] + size[None, :] - inter
    S = np.divide(inter, union, out=np.zeros_like(inter), where=union > 0)
    return knn_from_similarity(S, k, rng)


def one_hot(df: pd.DataFrame, cols: list[str]) -> sp.csr_matrix:
    blocks = []
    for c in cols:
        codes, _ = pd.factorize(df[c].astype(str))
        blocks.append(sp.csr_matrix((np.ones(len(codes)), (np.arange(len(codes)), codes))))
    return sp.hstack(blocks).tocsr()


def scaled_laplacian(W: sp.csr_matrix) -> sp.csr_matrix:
    W = W.tocsr().astype(np.float64)
    deg = np.asarray(W.sum(axis=1)).ravel()
    scale = W.shape[0] / deg.sum() if deg.sum() > 0 else 1.0
    return (sp.diags(deg * scale) - W * scale).tocsr()


# ---------------------------------------------------------------- null graphs


def upper_edges(W: sp.csr_matrix):
    T = sp.triu(W, k=1).tocoo()
    return T.row.copy(), T.col.copy(), T.data.copy()


def from_edges(n, r, c, w) -> sp.csr_matrix:
    A = sp.csr_matrix((w, (r, c)), shape=(n, n))
    return (A + A.T).tocsr()


def rewire(W: sp.csr_matrix, rng: np.random.Generator, swaps_per_edge: int = 10) -> sp.csr_matrix:
    """Degree-preserving double edge swaps; each edge keeps its weight."""
    n = W.shape[0]
    r, c, w = upper_edges(W)
    m = len(r)
    if m < 2:
        return W.copy()
    present = set(zip(r.tolist(), c.tolist()))
    for _ in range(swaps_per_edge * m):
        i, j = rng.integers(m, size=2)
        a, b, x, d = r[i], c[i], r[j], c[j]
        if rng.random() < 0.5:
            x, d = d, x
        e1, e2 = (min(a, d), max(a, d)), (min(x, b), max(x, b))
        if a == d or x == b or e1 in present or e2 in present or e1 == e2:
            continue
        present.discard((r[i], c[i]))
        present.discard((r[j], c[j]))
        present.update((e1, e2))
        (r[i], c[i]), (r[j], c[j]) = e1, e2
    return from_edges(n, r, c, w)


def erdos_renyi(W: sp.csr_matrix, rng: np.random.Generator) -> sp.csr_matrix:
    """Same node count, edge count and weight multiset; edges placed uniformly."""
    n = W.shape[0]
    _, _, w = upper_edges(W)
    m = len(w)
    chosen: set[tuple[int, int]] = set()
    while len(chosen) < m:
        a, b = rng.integers(n, size=2)
        if a != b:
            chosen.add((min(a, b), max(a, b)))
    r, c = map(np.array, zip(*chosen)) if m else (np.array([], int), np.array([], int))
    return from_edges(n, r, c, rng.permutation(w))


# ---------------------------------------------------------------- embeddings


def pure_svd(df: pd.DataFrame, rank: int):
    """PureSVD on log1p(capped watch ratio); returns row and column factors scaled by singular values."""
    ru, ri = np.unique(df.user_id), np.unique(df.video_id)
    rows, cols = np.searchsorted(ru, df.user_id), np.searchsorted(ri, df.video_id)
    vals = np.log1p(np.minimum(df.watch_ratio.to_numpy(np.float64), 5.0))
    Y = sp.csr_matrix((vals, (rows, cols)), shape=(len(ru), len(ri)))
    U, s, Vt = svds(Y, k=rank, random_state=SEED)
    return ru, U * s, ri, Vt.T * s


def lookup(ids: np.ndarray, keys: np.ndarray, vecs: np.ndarray) -> tuple[np.ndarray, int]:
    out = np.zeros((len(keys), vecs.shape[1]))
    pos = np.searchsorted(ids, keys)
    ok = (pos < len(ids)) & (ids[np.minimum(pos, len(ids) - 1)] == keys)
    out[ok] = vecs[pos[ok]]
    return out, int((~ok).sum())


# ---------------------------------------------------------------- builders


def build_all(k: int = K_DEFAULT) -> dict:
    rng = np.random.default_rng(SEED)
    GRAPHS.mkdir(parents=True, exist_ok=True)
    z = np.load(CACHE / "eval_matrix.npz")
    users, videos = z["users"], z["videos"]
    meta: dict[str, dict] = {}
    graphs: dict[str, sp.csr_matrix] = {}

    # U-soc: friend lists restricted to evaluation users.
    social = load_social()
    upos = {u: i for i, u in enumerate(users.tolist())}
    r, c = [], []
    for u, fr in social.items():
        for v in fr:
            if u in upos and v in upos and u != v:
                r.append(upos[u])
                c.append(upos[v])
    A = sp.csr_matrix((np.ones(len(r)), (r, c)), shape=(len(users), len(users)))
    graphs["U-soc"] = (A.maximum(A.T) > 0).astype(np.float64).tocsr()

    # Embeddings from the big matrix on leakage-free splits.
    big = load_interactions("big_matrix.csv")
    eval_v = np.isin(big.video_id, videos)
    eval_u = np.isin(big.user_id, users)
    ru, uvec, _, _ = pure_svd(big[~eval_v], SVD_RANK)
    _, _, ri, ivec = pure_svd(big[~eval_u], SVD_RANK)
    del big
    Xu, miss_u = lookup(ru, users, uvec)
    Xi, miss_i = lookup(ri, videos, ivec)
    meta["U-mf"] = {"eval_nodes_without_embedding": miss_u}
    meta["I-mf"] = {"eval_nodes_without_embedding": miss_i}
    graphs["U-mf"] = cosine_knn(Xu, k, rng)
    graphs["I-mf"] = cosine_knn(Xi, k, rng)

    # U-feat: one-hot profile fields.
    uf = pd.read_csv(raw_file("user_features.csv")).set_index("user_id").loc[users].reset_index()
    feat_cols = [
        "user_active_degree", "is_lowactive_period", "is_live_streamer", "is_video_author",
        "follow_user_num_range", "fans_user_num_range", "friend_user_num_range", "register_days_range",
    ] + [f"onehot_feat{j}" for j in range(18)]
    graphs["U-feat"] = jaccard_knn(one_hot(uf, feat_cols), k, rng)

    # U-geo and U-demo from the raw user file.
    raw = pd.read_csv(raw_file("user_features_raw.csv")).set_index("user_id").loc[users].reset_index()
    city = pd.factorize(raw["fre_city"].astype(str))[0]
    prov = pd.factorize(raw["fre_province"].astype(str))[0]
    known_city = ~raw["fre_city"].isna().to_numpy()
    known_prov = ~raw["fre_province"].isna().to_numpy()
    S_geo = 1.0 * ((city[:, None] == city[None, :]) & known_city[:, None] & known_city[None, :]) + 0.3 * (
        (prov[:, None] == prov[None, :]) & known_prov[:, None] & known_prov[None, :]
    )
    graphs["U-geo"] = knn_from_similarity(S_geo, k, rng)
    meta["U-geo"] = {"users_with_city": int(known_city.sum()), "distinct_cities": int(len(set(city[known_city])))}
    raw["price_band"] = pd.qcut(raw["mod_price"].rank(method="first"), 5, labels=False).astype(str)
    graphs["U-demo"] = jaccard_knn(one_hot(raw, ["gender", "age_range", "phone_brand", "price_band"]), k, rng)

    graphs["U-soc+mf"] = graphs["U-soc"].maximum(graphs["U-mf"]).tocsr()

    # I-tag: Jaccard on tag sets.
    tags = pd.read_csv(raw_file("item_categories.csv")).set_index("video_id").loc[videos]
    tag_lists = [ast.literal_eval(f) for f in tags["feat"]]
    rr = np.repeat(np.arange(len(videos)), [len(t) for t in tag_lists])
    cc = np.concatenate([np.asarray(t, int) for t in tag_lists])
    graphs["I-tag"] = jaccard_knn(sp.csr_matrix((np.ones(len(rr)), (rr, cc))), k, rng)
    meta["I-tag"] = {"distinct_tags": int(len(np.unique(cc)))}

    # I-cat: three-level category tree.
    cat = pd.read_csv(raw_file("kuairec_caption_category.csv"), on_bad_lines="skip", engine="python")
    cat = cat.drop_duplicates("video_id").set_index("video_id").reindex(videos)
    S_cat = np.zeros((len(videos), len(videos)))
    for col, w in [("first_level_category_id", 0.1), ("second_level_category_id", 0.3), ("third_level_category_id", 1.0)]:
        v = pd.to_numeric(cat[col], errors="coerce").to_numpy()
        ok = ~np.isnan(v) & (v >= 0)
        S_cat += w * ((v[:, None] == v[None, :]) & ok[:, None] & ok[None, :])
        meta.setdefault("I-cat", {})[f"{col}_known"] = int(ok.sum())
    graphs["I-cat"] = knn_from_similarity(S_cat, k, rng)

    # Nulls and caching.
    for name in list(graphs):
        W = graphs[name]
        for tag, G in [("", W), ("~rewired", rewire(W, rng)), ("~er", erdos_renyi(W, rng))]:
            sp.save_npz(GRAPHS / f"{name}{tag}.npz", G.tocsr())
        deg = np.asarray((W > 0).sum(axis=1)).ravel()
        meta.setdefault(name, {}).update(
            nodes=int(W.shape[0]),
            edges=int(sp.triu(W, 1).nnz),
            isolated_nodes=int((deg == 0).sum()),
            mean_degree=float(deg.mean()),
            k=k if name != "U-soc" else None,
        )
    (RESULTS / "graphs_meta.json").write_text(json.dumps(meta, indent=2))
    return meta


def load_graph(name: str) -> sp.csr_matrix:
    return sp.load_npz(GRAPHS / f"{name}.npz").tocsr()


if __name__ == "__main__":
    print(json.dumps(build_all(), indent=2))
