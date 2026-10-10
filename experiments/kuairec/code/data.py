"""Load KuaiRec 2.0, run the Step 0 checks, and build the ground-truth reward matrix.

Usage (from the repo root):
    .venv/bin/python -I experiments/kuairec/code/data.py

Raw files are expected under data/kuairec_raw/ (any depth). Cached arrays go to
data/kuairec_cache/ and the Step 0 report to experiments/kuairec/results/.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "kuairec_raw"
CACHE = ROOT / "data" / "kuairec_cache"
RESULTS = Path(__file__).resolve().parents[1] / "results"

WATCH_CAP = 5.0


def raw_file(name: str) -> Path:
    hits = sorted(RAW.rglob(name))
    if not hits:
        raise FileNotFoundError(f"{name} not found under {RAW}")
    return hits[0]


def load_interactions(name: str) -> pd.DataFrame:
    return pd.read_csv(
        raw_file(name),
        usecols=["user_id", "video_id", "watch_ratio"],
        dtype={"user_id": np.int32, "video_id": np.int32, "watch_ratio": np.float32},
    )


def load_social() -> dict[int, list[int]]:
    df = pd.read_csv(raw_file("social_network.csv"))
    return {int(u): [int(v) for v in ast.literal_eval(f)] for u, f in zip(df.user_id, df.friend_list)}


def pair_keys(df: pd.DataFrame) -> np.ndarray:
    return df.user_id.to_numpy(np.int64) * 100_000 + df.video_id.to_numpy(np.int64)


def build_eval_matrix(small: pd.DataFrame):
    """Dense users x videos watch-ratio matrix; NaN where the pair is missing (blocked)."""
    small = small.groupby(["user_id", "video_id"], as_index=False).watch_ratio.mean()
    users = np.sort(small.user_id.unique())
    videos = np.sort(small.video_id.unique())
    W = np.full((len(users), len(videos)), np.nan, dtype=np.float32)
    W[np.searchsorted(users, small.user_id), np.searchsorted(videos, small.video_id)] = small.watch_ratio
    return users, videos, W


def reward_means(W: np.ndarray, model: str = "R1") -> np.ndarray:
    """True arm means. NaN (blocked pairs) stays NaN."""
    capped = np.minimum(W, WATCH_CAP)
    if model == "R1":
        return capped / WATCH_CAP
    if model == "R2":
        return capped
    if model == "R3":
        return np.where(np.isnan(W), np.nan, np.where(W > 2.0, 1.0, 0.1)).astype(np.float32)
    raise ValueError(model)


def load_eval(model: str = "R1"):
    """Cached (users, videos, M) for the chosen reward model."""
    z = np.load(CACHE / "eval_matrix.npz")
    return z["users"], z["videos"], reward_means(z["W"], model)


def step0() -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)

    small = load_interactions("small_matrix.csv")
    big = load_interactions("big_matrix.csv")

    small_keys, big_keys = pair_keys(small), pair_keys(big)
    users, videos, W = build_eval_matrix(small)
    np.savez_compressed(CACHE / "eval_matrix.npz", users=users, videos=videos, W=W)

    big_users, big_videos = np.unique(big.user_id), np.unique(big.video_id)
    shared_pairs = np.isin(small_keys, big_keys)

    social = load_social()
    eval_set = set(users.tolist())
    social_eval = [u for u in social if u in eval_set]
    eval_edges = {tuple(sorted((u, v))) for u in social for v in social[u] if u in eval_set and v in eval_set and u != v}
    with_eval_friend = {u for e in eval_edges for u in e}

    wr = small.watch_ratio.to_numpy()
    report = {
        "small_rows": int(len(small)),
        "small_unique_pairs": int(len(np.unique(small_keys))),
        "small_duplicate_rows": int(len(small) - len(np.unique(small_keys))),
        "eval_users": int(len(users)),
        "eval_videos": int(len(videos)),
        "eval_missing_pairs": int(np.isnan(W).sum()),
        "eval_density": float(1 - np.isnan(W).mean()),
        "big_rows": int(len(big)),
        "big_users": int(len(big_users)),
        "big_videos": int(len(big_videos)),
        "eval_users_in_big": int(np.isin(users, big_users).sum()),
        "eval_videos_in_big": int(np.isin(videos, big_videos).sum()),
        "small_pairs_also_in_big": int(shared_pairs.sum()),
        "big_rows_eval_user_and_eval_video": int(
            (np.isin(big.user_id, users) & np.isin(big.video_id, videos)).sum()
        ),
        "big_rows_eval_user_non_eval_video": int(
            (np.isin(big.user_id, users) & ~np.isin(big.video_id, videos)).sum()
        ),
        "big_rows_non_eval_user_eval_video": int(
            (~np.isin(big.user_id, users) & np.isin(big.video_id, videos)).sum()
        ),
        "social_users": int(len(social)),
        "social_users_in_eval": int(len(social_eval)),
        "social_edges_within_eval": int(len(eval_edges)),
        "eval_users_with_eval_friend": int(len(with_eval_friend)),
        "watch_ratio_quantiles": {
            q: float(np.quantile(wr, float(q))) for q in ["0.01", "0.1", "0.25", "0.5", "0.75", "0.9", "0.99"]
        },
        "watch_ratio_mean": float(wr.mean()),
        "share_watch_ratio_above_2": float((wr > 2).mean()),
        "share_watch_ratio_above_5": float((wr > WATCH_CAP).mean()),
    }
    (RESULTS / "step0_report.json").write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    print(json.dumps(step0(), indent=2))
