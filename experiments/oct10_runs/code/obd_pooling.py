"""Experiment 8b: certified pooling calibrated on Open Bandit Dataset click rates (semi-synthetic).

Usage (from the repo root):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/oct10_runs/code/obd_pooling.py --seeds 20 --horizon 2000000 --jobs 3

Real click rates, simulated Bernoulli feedback; not logged-feedback evidence.
- Truth: each item's click rate on the uniform-random logs of days 4-7 (all positions pooled;
  position effects are under 10% relative, see obd_feasibility). Treated as the true means.
- Components, built from days 1-3 only:
    attr      item_feature_1 groups from the released item features (no timestamp provenance:
              a retrospective metadata graph);
    audience  k-means on each item's smoothed log-odds click profile over the 4 user_feature_0
              segments (days 1-3), k = number of attr groups;
    attr~rw   attr labels randomly permuted across items (same component sizes): the rewired null.
- Certificate widths for SP-KLUCB: oracle (true within-component range), prefix (range of
  days 1-3 estimates within the component: real data, noisy, usually conservative), none (0).
- Policies: klucb (level log t), klucb_ell (fixed level ell, matching SP-KLUCB), ts (Beta(1,1)),
  eb_ts (graph-free empirical-Bayes Beta prior fitted on days 1-3), comp_ts (Beta prior centred
  on the component's running pooled mean: uncertified pooling), sp_klucb (KL SP-UCB from
  kuairec/code/setting_a2.py), all in block form: each
  decision serves 100 impressions (batched updates, as in production recommenders).
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "kuairec" / "code"))
from setting_a2 import kl_upper  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data" / "obd" / "open_bandit_dataset" / "random"
RESULTS = HERE.parent / "results" / "obd_pooling"
SEED = 20261010
CHECKPOINTS = (10_000, 100_000, 250_000, 500_000, 1_000_000, 2_000_000, 5_000_000)
_CACHE = {}


def instance(campaign):
    if campaign in _CACHE:
        return _CACHE[campaign]
    df = pd.read_csv(DATA / campaign / f"{campaign}.csv",
                     usecols=["timestamp", "item_id", "click", "user_feature_0"])
    ts = pd.to_datetime(df["timestamp"], utc=True, format="ISO8601")
    df["day"] = (ts - ts.min().normalize()).dt.days
    items = np.sort(df.item_id.unique())
    K = len(items)
    pre, post = df[df.day < 3], df[df.day >= 3]
    mu = post.groupby("item_id").click.mean().reindex(items).to_numpy()
    g = pre.groupby("item_id").click.agg(["sum", "size"]).reindex(items)
    p_pre = (g["sum"] / g["size"]).to_numpy()
    ctx = pd.read_csv(DATA / campaign / "item_context.csv", index_col=0).set_index("item_id").reindex(items)
    attr = pd.factorize(ctx["item_feature_1"])[0]
    C = attr.max() + 1
    # Audience profile: smoothed log-odds per user_feature_0 segment, days 1-3.
    seg = pre.groupby(["item_id", "user_feature_0"]).click.agg(["sum", "size"]).unstack().reindex(items)
    m0 = pre.click.mean()
    prof = np.log((seg["sum"].fillna(0) + 20 * m0) / (seg["size"].fillna(0) - seg["sum"].fillna(0) + 20 * (1 - m0)))
    prof = prof.to_numpy()
    from sklearn.cluster import KMeans
    aud = KMeans(n_clusters=C, n_init=20, random_state=SEED).fit_predict((prof - prof.mean(0)) / prof.std(0))
    rw = np.random.default_rng(SEED).permutation(attr)
    # Empirical-Bayes Beta prior (graph-free) from days 1-3: method of moments.
    m = g["sum"].sum() / g["size"].sum()
    tau2 = max(p_pre.var(ddof=1) - (m * (1 - m) / g["size"]).mean(), 1e-8)
    conc = m * (1 - m) / tau2 - 1
    out = {"mu": mu, "p_pre": p_pre, "labels": {"attr": attr, "audience": aud, "attr~rw": rw},
           "eb": (m, conc), "K": K, "C": C}
    _CACHE[campaign] = out
    return out


def widths(labels, mu, p_pre, kind):
    C = labels.max() + 1
    if kind == "none":
        return np.zeros(C)
    src = mu if kind == "oracle" else p_pre
    return np.array([np.ptp(src[labels == c]) for c in range(C)])


BLOCK = 100  # impressions per decision: indices are updated after each block


def run_blocked(policy, mu, T, rng, labels=None, width=None, level=None, eb=None):
    """Every policy in block form: each decision serves BLOCK impressions to one item, whose
    clicks are Binomial(BLOCK, mu); the policy updates after the block. Regret per impression."""
    K = len(mu)
    n, w = np.zeros(K), np.zeros(K)
    nb = T // BLOCK
    reg = np.zeros(nb)
    best = mu.max()
    if labels is not None:
        C = labels.max() + 1
        members = [np.flatnonzero(labels == c) for c in range(C)]
        Nc, Wc = np.zeros(C), np.zeros(C)
        pool_up = np.full(C, np.inf)
    arm_up = np.full(K, np.inf)
    for t in range(nb):
        if policy in ("klucb", "klucb_ell"):
            if policy == "klucb":
                arm_up = kl_upper(w / np.maximum(n, 1), n, np.log(max((t + 1) * BLOCK, 2)))
            a = int(np.argmax(arm_up))
        elif policy == "ts":
            a = int(np.argmax(rng.beta(1 + w, 1 + n - w)))
        elif policy == "eb_ts":
            m, conc = eb
            a = int(np.argmax(rng.beta(m * conc + w, (1 - m) * conc + n - w)))
        elif policy == "comp_ts":
            conc = eb[1]
            mc = (Wc[labels] + 1) / (Nc[labels] + 2)
            a = int(np.argmax(rng.beta(mc * conc + w, (1 - mc) * conc + n - w)))
        else:  # sp_klucb: one pull per component first, then the SP-UCB rule
            if t < C:
                a = int(members[t][0])
            else:
                comp_val = np.array([min(arm_up[m].max(), pool_up[c] + width[c]) for c, m in enumerate(members)])
                c = int(np.argmax(comp_val))
                m = members[c]
                a = int(m[np.argmax(arm_up[m])])
        k = rng.binomial(BLOCK, mu[a])
        n[a] += BLOCK
        w[a] += k
        if policy in ("klucb_ell", "sp_klucb"):
            arm_up[a] = kl_upper(np.array([w[a] / n[a]]), np.array([n[a]]), level)[0]
        if labels is not None:
            c = labels[a]
            Nc[c] += BLOCK
            Wc[c] += k
            if policy == "sp_klucb":
                pool_up[c] = kl_upper(np.array([Wc[c] / Nc[c]]), np.array([Nc[c]]), level)[0]
        reg[t] = BLOCK * (best - mu[a])
    return reg


def run(task):
    campaign, seed, policy, graph, width, T = task
    t0 = time.time()
    inst = instance(campaign)
    mu, K, C = inst["mu"], inst["K"], inst["C"]
    rng = np.random.default_rng([SEED, seed, {"all": 0, "men": 1, "women": 2}[campaign]])
    ell = np.log(2 * (K + C) * T / 0.05)
    lab = inst["labels"][graph] if graph != "-" else None
    wid = widths(lab, mu, inst["p_pre"], width) if policy == "sp_klucb" else None
    reg = run_blocked(policy, mu, T, rng, labels=lab, width=wid, level=ell, eb=inst["eb"])
    cum = np.cumsum(reg)
    row = {"campaign": campaign, "seed": seed, "policy": policy, "graph": graph, "width": width, "T": T,
           "regret": float(cum[-1]), "best_share_last_10pct": float((reg[-len(reg) // 10:] == 0).mean()),
           "seconds": round(time.time() - t0, 1)}
    for c in CHECKPOINTS:
        if c <= T:
            row[f"regret@{c}"] = float(cum[c // BLOCK - 1])
    return row


def describe(campaigns):
    rows = []
    for c in campaigns:
        inst = instance(c)
        mu = inst["mu"]
        top = np.sort(mu)[::-1]
        for g, lab in inst["labels"].items():
            best_c = lab[np.argmax(mu)]
            w_or = widths(lab, mu, inst["p_pre"], "oracle")
            w_pre = widths(lab, mu, inst["p_pre"], "prefix")
            v_c = np.array([mu[lab == k].max() for k in range(inst["C"])])
            gap_c = mu.max() - v_c
            rejectable = (gap_c > w_or) & (gap_c > 0)
            rows.append({"campaign": c, "graph": g, "K": inst["K"], "components": inst["C"],
                         "best_ctr": top[0], "gap_2nd": top[0] - top[1], "mean_ctr": mu.mean(),
                         "oracle_width_median": float(np.median(w_or)), "prefix_width_median": float(np.median(w_pre)),
                         "prefix_covers_oracle_share": float((w_pre >= w_or - 1e-12).mean()),
                         "components_rejectable_oracle": int(rejectable.sum()),
                         "arms_in_rejectable_components": int(np.isin(lab, np.flatnonzero(rejectable)).sum()),
                         "best_component_size": int((lab == best_c).sum()),
                         "eb_prior_concentration": inst["eb"][1]})
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "instance.csv", index=False)
    print(df.round(5).to_string())


def tasks(campaigns, seeds, T):
    out = []
    for c in campaigns:
        for s in range(seeds):
            for p in ("klucb", "klucb_ell", "ts", "eb_ts"):
                out.append((c, s, p, "-", "-", T))
            for g in ("attr", "audience", "attr~rw"):
                out.append((c, s, "comp_ts", g, "-", T))
                for w in ("oracle", "prefix", "none"):
                    out.append((c, s, "sp_klucb", g, w, T))
    return out


def main(campaigns, seeds, T, jobs):
    RESULTS.mkdir(parents=True, exist_ok=True)
    describe(campaigns)
    ts = tasks(campaigns, seeds, T)
    print(f"{len(ts)} runs", flush=True)
    rows = []
    t0 = time.time()
    with ProcessPoolExecutor(jobs) as ex:
        for i, r in enumerate(ex.map(run, ts)):
            rows.append(r)
            if (i + 1) % 20 == 0:
                print(f"{i + 1}/{len(ts)} {time.time() - t0:.0f}s", flush=True)
                pd.DataFrame(rows).to_csv(RESULTS / "runs.partial.csv", index=False)
    pd.DataFrame(rows).to_csv(RESULTS / "runs.csv", index=False)
    (RESULTS / "runs.partial.csv").unlink(missing_ok=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaigns", nargs="+", default=["all", "women"])
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--horizon", type=int, default=2_000_000)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    if a.pilot:
        RESULTS.mkdir(parents=True, exist_ok=True)
        describe(a.campaigns)
        for task in [("all", 0, "sp_klucb", "attr", "oracle", 2_000_000), ("all", 0, "klucb", "-", "-", 2_000_000),
                     ("all", 0, "comp_ts", "attr", "-", 2_000_000), ("all", 0, "ts", "-", "-", 2_000_000)]:
            print(run(task))
    else:
        main(a.campaigns, a.seeds, a.horizon, a.jobs)
