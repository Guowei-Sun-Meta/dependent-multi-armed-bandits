"""Build user-user (U2U) and item-item (I2I) graphs for KuaiRec, plus null graphs.

Usage (from the repo root, after data.py):
    .venv/bin/python -I experiments/kuairec/graphs.py [--k 10]

Leakage rule: no graph sees an evaluation (user, video) pair. User-side signals
use big-matrix interactions with non-evaluation videos only; video-side signals
use interactions from non-evaluation users only.

Each graph is defined by node features (see `node_features`), so it can be
rebuilt on any node subset, as bandit instances need. Every graph is a symmetric
kNN graph (union of each node's k nearest neighbours), with Laplacian L = D - W
scaled so the mean weighted degree is 1. Under this scaling a random graph has
smoothness quotient close to 1 for any signal.
"""

from __future__ import annotations

import argparse
import ast
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.sparse.linalg import svds

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import CACHE, RESULTS, load_social, raw_file  # noqa: E402

GRAPHS = CACHE / "graphs"
FEATURES = CACHE / "node_features.pkl"
K_DEFAULT = 10
SVD_RANK = 64
ENGAGED = 1.0  # watch ratio at or above a full play counts as engagement
SEED = 20261009

DESCRIPTIONS = {
    "U-soc": "Friend lists (social_network.csv)",
    "U-mf": "PureSVD user factors, non-evaluation videos",
    "U-coeng": "Jaccard on sets of fully watched non-evaluation videos",
    "U-coeng-idf": "Cosine on IDF-weighted engagement with non-evaluation videos (popularity down-weighted)",
    "U-coauthor": "Cosine on IDF-weighted engagement aggregated by video author",
    "U-cotag": "Cosine on per-tag taste profile (tag mean watch ratio minus user mean)",
    "U-cotime": "Cosine on hour-of-day activity histogram",
    "U-feat": "Jaccard on one-hot profile fields (user_features.csv)",
    "U-geo": "Same city (1) or province (0.3)",
    "U-demo": "Jaccard on gender, age range, phone brand, price band",
    "U-soc+mf": "Union of U-soc and U-mf",
    "I-mf": "PureSVD video factors, non-evaluation users",
    "I-coeng": "Cosine on IDF-weighted engagement from non-evaluation users",
    "I-coauthor": "Same author",
    "I-tag": "Jaccard on tag sets",
    "I-cat": "Three-level category tree (1 / 0.3 / 0.1)",
}


# ---------------------------------------------------------------- kNN helpers


def knn_from_similarity(S: np.ndarray, k: int, rng: np.random.Generator) -> sp.csr_matrix:
    """Union kNN graph from a dense similarity matrix; ties broken at random."""
    n = S.shape[0]
    k = min(k, n - 1)
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


def cosine_sim(X) -> np.ndarray:
    if sp.issparse(X):
        X = X.tocsr().astype(np.float64)
        norms = np.sqrt(np.asarray(X.multiply(X).sum(axis=1)).ravel())
        Xn = sp.diags(np.divide(1.0, norms, out=np.zeros_like(norms), where=norms > 0)) @ X
        return (Xn @ Xn.T).toarray()
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    Xn = np.divide(X, norms, out=np.zeros_like(X), where=norms > 0)
    return Xn @ Xn.T


def jaccard_sim(B: sp.csr_matrix) -> np.ndarray:
    B = (B > 0).astype(np.float64).tocsr()
    inter = (B @ B.T).toarray()
    size = np.asarray(B.sum(axis=1)).ravel()
    union = size[:, None] + size[None, :] - inter
    return np.divide(inter, union, out=np.zeros_like(inter), where=union > 0)


def one_hot(df: pd.DataFrame, cols: list[str]) -> sp.csr_matrix:
    blocks = []
    for c in cols:
        codes, _ = pd.factorize(df[c].astype(str))
        blocks.append(sp.csr_matrix((np.ones(len(codes)), (np.arange(len(codes)), codes))))
    return sp.hstack(blocks).tocsr()


def idf_weight(Y: sp.csr_matrix) -> sp.csr_matrix:
    """Down-weight columns (videos or authors) that many rows engage with."""
    df = np.asarray((Y > 0).sum(axis=0)).ravel()
    idf = np.log((1 + Y.shape[0]) / (1 + df))
    return (Y @ sp.diags(idf)).tocsr()


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


# ---------------------------------------------------------------- node features


def sparse_matrix(df: pd.DataFrame, row_key: str, row_ids: np.ndarray, col_key: str, values: np.ndarray,
                  col_ids: np.ndarray | None = None) -> sp.csr_matrix:
    """Rows = row_ids (in order), columns = col_ids (default: all values seen); duplicates add up."""
    rk, ck = df[row_key].to_numpy(), df[col_key].to_numpy()
    col_ids = np.unique(ck) if col_ids is None else col_ids
    keep = np.isin(rk, row_ids) & np.isin(ck, col_ids)
    r, c = np.searchsorted(row_ids, rk[keep]), np.searchsorted(col_ids, ck[keep])
    return sp.csr_matrix((values[keep], (r, c)), shape=(len(row_ids), len(col_ids)))


def pure_svd(Y: sp.csr_matrix, rank: int) -> np.ndarray:
    U, s, _ = svds(Y.astype(np.float64), k=rank, random_state=SEED)
    return U * s


def node_features() -> dict:
    """Features defining every graph, for the evaluation users and videos (in matrix order)."""
    z = np.load(CACHE / "eval_matrix.npz")
    users, videos = z["users"], z["videos"]
    feats: dict[str, tuple] = {}

    big = pd.read_csv(
        raw_file("big_matrix.csv"),
        usecols=["user_id", "video_id", "watch_ratio", "timestamp"],
        dtype={"user_id": np.int32, "video_id": np.int32, "watch_ratio": np.float32, "timestamp": np.float64},
    )
    authors = (
        pd.read_csv(raw_file("item_daily_features.csv"), usecols=["video_id", "author_id"])
        .drop_duplicates("video_id")
        .set_index("video_id")["author_id"]
    )
    tag_lists = (
        pd.read_csv(raw_file("item_categories.csv")).set_index("video_id")["feat"].map(ast.literal_eval)
    )

    # ---- user side: interactions of evaluation users with non-evaluation videos
    ub = big[~np.isin(big.video_id, videos)]
    log_wr = np.log1p(np.minimum(ub.watch_ratio.to_numpy(np.float64), 5.0))
    engaged = (ub.watch_ratio.to_numpy() >= ENGAGED).astype(np.float64)
    all_u = np.unique(ub.user_id)
    Y_all = sparse_matrix(ub, "user_id", all_u, "video_id", log_wr)
    feats["U-mf"] = ("cos", pure_svd(Y_all, SVD_RANK)[np.searchsorted(all_u, users)])
    E = sparse_matrix(ub, "user_id", users, "video_id", engaged)
    feats["U-coeng"] = ("jac", E)
    feats["U-coeng-idf"] = ("cos", idf_weight(E))
    ub_auth = ub.assign(video_id=authors.reindex(ub.video_id).fillna(-1).astype(np.int64).to_numpy())
    auth_ids = np.unique(ub_auth.video_id[ub_auth.video_id >= 0])
    feats["U-coauthor"] = ("cos", idf_weight(sparse_matrix(ub_auth, "user_id", users, "video_id", engaged, auth_ids)))

    # tag taste: mean log watch ratio per tag, minus the user's overall mean
    tags = tag_lists.reindex(ub.video_id).to_numpy()
    rep = np.array([len(t) if isinstance(t, list) else 0 for t in tags])
    flat = np.concatenate([np.asarray(t, int) for t in tags if isinstance(t, list) and t])
    r = np.searchsorted(users, np.repeat(ub.user_id.to_numpy(), rep))
    keep = np.isin(np.repeat(ub.user_id.to_numpy(), rep), users)
    n_tags = int(flat.max()) + 1
    val = np.repeat(log_wr, rep)
    S_sum = sp.csr_matrix((val[keep], (r[keep], flat[keep])), shape=(len(users), n_tags)).toarray()
    S_cnt = sp.csr_matrix((np.ones(keep.sum()), (r[keep], flat[keep])), shape=(len(users), n_tags)).toarray()
    tag_mean = np.divide(S_sum, S_cnt, out=np.zeros_like(S_sum), where=S_cnt > 0)
    user_mean = S_sum.sum(1, keepdims=True) / np.maximum(S_cnt.sum(1, keepdims=True), 1)
    feats["U-cotag"] = ("cos", np.where(S_cnt > 0, tag_mean - user_mean, 0.0))

    # hour-of-day activity (UTC+8, Kuaishou's home time zone)
    hours = ((ub.timestamp.to_numpy() // 3600 + 8) % 24).astype(int)
    ok = ~np.isnan(ub.timestamp.to_numpy()) & np.isin(ub.user_id, users)
    H = sp.csr_matrix((np.ones(ok.sum()), (np.searchsorted(users, ub.user_id[ok]), hours[ok])), shape=(len(users), 24))
    H = H.toarray()
    feats["U-cotime"] = ("cos", H / np.maximum(H.sum(1, keepdims=True), 1) - (H.sum(0) / H.sum()))
    del ub

    # ---- video side: interactions of non-evaluation users with evaluation videos
    vb = big[~np.isin(big.user_id, users)]
    log_wr_v = np.log1p(np.minimum(vb.watch_ratio.to_numpy(np.float64), 5.0))
    engaged_v = (vb.watch_ratio.to_numpy() >= ENGAGED).astype(np.float64)
    all_v = np.unique(vb.video_id)
    Yv = sparse_matrix(vb, "video_id", all_v, "user_id", log_wr_v)
    feats["I-mf"] = ("cos", pure_svd(Yv, SVD_RANK)[np.searchsorted(all_v, videos)])
    Ev = sparse_matrix(vb, "video_id", videos, "user_id", engaged_v)
    feats["I-coeng"] = ("cos", idf_weight(Ev))
    del vb, big

    a = authors.reindex(videos).fillna(-1).to_numpy()
    feats["I-coauthor"] = ("eq", a)

    tl = tag_lists.reindex(videos)
    rr = np.repeat(np.arange(len(videos)), [len(t) for t in tl])
    cc = np.concatenate([np.asarray(t, int) for t in tl])
    feats["I-tag"] = ("jac", sp.csr_matrix((np.ones(len(rr)), (rr, cc))))

    cat = pd.read_csv(raw_file("kuairec_caption_category.csv"), on_bad_lines="skip", engine="python")
    cat["video_id"] = pd.to_numeric(cat["video_id"], errors="coerce")  # a few multi-line captions break rows
    cat = cat.dropna(subset=["video_id"]).astype({"video_id": int}).drop_duplicates("video_id")
    cat = cat.set_index("video_id").reindex(videos)
    levels = []
    for col, w in [("first_level_category_id", 0.1), ("second_level_category_id", 0.3), ("third_level_category_id", 1.0)]:
        v = pd.to_numeric(cat[col], errors="coerce").to_numpy()
        levels.append((np.where(np.isnan(v) | (v < 0), np.nan, v), w))
    feats["I-cat"] = ("levels", levels)

    # ---- profile, location, demographic, social
    uf = pd.read_csv(raw_file("user_features.csv")).set_index("user_id").loc[users].reset_index()
    feat_cols = [
        "user_active_degree", "is_lowactive_period", "is_live_streamer", "is_video_author",
        "follow_user_num_range", "fans_user_num_range", "friend_user_num_range", "register_days_range",
    ] + [f"onehot_feat{j}" for j in range(18)]
    feats["U-feat"] = ("jac", one_hot(uf, feat_cols))
    raw = pd.read_csv(raw_file("user_features_raw.csv")).set_index("user_id").loc[users].reset_index()
    city = pd.to_numeric(pd.Series(pd.factorize(raw["fre_city"])[0]), errors="coerce").to_numpy(float)
    prov = pd.to_numeric(pd.Series(pd.factorize(raw["fre_province"])[0]), errors="coerce").to_numpy(float)
    feats["U-geo"] = ("levels", [(np.where(city < 0, np.nan, city), 1.0), (np.where(prov < 0, np.nan, prov), 0.3)])
    raw["price_band"] = pd.qcut(raw["mod_price"].rank(method="first"), 5, labels=False).astype(str)
    feats["U-demo"] = ("jac", one_hot(raw, ["gender", "age_range", "phone_brand", "price_band"]))

    social = load_social()
    upos = {u: i for i, u in enumerate(users.tolist())}
    pairs = [(upos[u], upos[v]) for u, fr in social.items() for v in fr if u in upos and v in upos and u != v]
    r, c = zip(*pairs) if pairs else ((), ())
    A = sp.csr_matrix((np.ones(len(r)), (r, c)), shape=(len(users), len(users)))
    feats["U-soc"] = ("fixed", (A.maximum(A.T) > 0).astype(np.float64).tocsr())
    return feats


def load_features() -> dict:
    if not FEATURES.exists():
        with open(FEATURES, "wb") as f:
            pickle.dump(node_features(), f)
    with open(FEATURES, "rb") as f:
        return pickle.load(f)


def build(feats: dict, name: str, k: int, rng: np.random.Generator, nodes: np.ndarray | None = None) -> sp.csr_matrix:
    """kNN graph `name` on the given node subset (indices into the evaluation order)."""
    if name == "U-soc+mf":
        return build(feats, "U-soc", k, rng, nodes).maximum(build(feats, "U-mf", k, rng, nodes)).tocsr()
    kind, f = feats[name]
    pick = (lambda X: X) if nodes is None else (lambda X: X[nodes])
    if kind == "fixed":
        return f if nodes is None else f[nodes][:, nodes].tocsr()
    if kind == "cos":
        return knn_from_similarity(cosine_sim(pick(f)), k, rng)
    if kind == "jac":
        return knn_from_similarity(jaccard_sim(pick(f)), k, rng)
    if kind == "eq":
        a = pick(f)
        return knn_from_similarity(((a[:, None] == a[None, :]) & (a[:, None] >= 0)).astype(float), k, rng)
    if kind == "levels":
        S = 0.0
        for v, w in f:
            v = pick(v)
            S = S + w * ((v[:, None] == v[None, :]) & ~np.isnan(v)[:, None])
        return knn_from_similarity(np.asarray(S, dtype=float), k, rng)
    raise ValueError(kind)


def graph_dir(k: int) -> Path:
    return GRAPHS / f"k{k}"


def build_all(k: int = K_DEFAULT) -> dict:
    rng = np.random.default_rng(SEED + k)
    out = graph_dir(k)
    out.mkdir(parents=True, exist_ok=True)
    feats = load_features()
    meta: dict[str, dict] = {}
    for name in DESCRIPTIONS:
        W = build(feats, name, k, rng)
        for tag, G in [("", W), ("~rewired", rewire(W, rng)), ("~er", erdos_renyi(W, rng))]:
            sp.save_npz(out / f"{name}{tag}.npz", G.tocsr())
        deg = np.asarray((W > 0).sum(axis=1)).ravel()
        meta[name] = {
            "description": DESCRIPTIONS[name],
            "nodes": int(W.shape[0]),
            "edges": int(sp.triu(W, 1).nnz),
            "isolated_nodes": int((deg == 0).sum()),
            "mean_degree": float(deg.mean()),
        }
        print(f"k={k} {name:12s} edges={meta[name]['edges']:6d} isolated={meta[name]['isolated_nodes']}", flush=True)
    (RESULTS / f"graphs_meta_k{k}.json").write_text(json.dumps(meta, indent=2))
    return meta


def load_graph(name: str, k: int = K_DEFAULT) -> sp.csr_matrix:
    return sp.load_npz(graph_dir(k) / f"{name}.npz").tocsr()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, nargs="+", default=[K_DEFAULT])
    for k in ap.parse_args().k:
        build_all(k)
