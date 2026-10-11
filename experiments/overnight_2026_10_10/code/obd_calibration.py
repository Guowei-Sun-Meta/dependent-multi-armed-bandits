"""Chronological OBD range calibration and held-out rate uncertainty sensitivity."""
from pathlib import Path
import hashlib
import json
import time

import numpy as np
import pandas as pd
from scipy.stats import beta
from sklearn.cluster import KMeans

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
DATA = ROOT / "data/obd/open_bandit_dataset/random"
OUT = HERE / "results/obd_calibration"
SEED, DRAWS, DELTA = 20261011, 5000, .05


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    rows, rankrows, itemrows, sources = [], [], [], {}
    for campaign in ["all", "women"]:
        path = DATA / campaign / f"{campaign}.csv"
        sources[str(path.relative_to(ROOT))] = digest(path)
        df = pd.read_csv(path, usecols=["timestamp", "item_id", "position", "click", "user_feature_0"])
        ts = pd.to_datetime(df.timestamp, utc=True, format="ISO8601")
        df["day"] = (ts - ts.min().normalize()).dt.days
        assert set(df.day.unique()) == set(range(7))
        ctx = pd.read_csv(DATA / campaign / "item_context.csv", index_col=0).set_index("item_id")
        for position in ["pooled", "position1"]:
            data = df if position == "pooled" else df[df.position == 1]
            items = np.sort(data.item_id.unique())
            K = len(items)
            attr = pd.factorize(ctx.reindex(items).item_feature_1)[0]
            assert (attr >= 0).all()
            C = int(attr.max() + 1)
            for cut in [2, 3, 4]:
                pre, post = data[data.day < cut], data[data.day >= cut]
                pg = pre.groupby("item_id").click.agg(["sum", "size"]).reindex(items)
                hg = post.groupby("item_id").click.agg(["sum", "size"]).reindex(items)
                assert pg.notna().all().all() and hg.notna().all().all()
                pc, pn = pg["sum"].to_numpy(), pg["size"].to_numpy()
                hc, hn = hg["sum"].to_numpy(), hg["size"].to_numpy()
                ppre, held = pc / pn, hc / hn
                tail = DELTA / (2 * K)
                low = np.where(pc == 0, 0, beta.ppf(tail, np.maximum(pc, 1), pn - pc + 1))
                high = np.where(pc == pn, 1, beta.ppf(1 - tail, pc + 1, np.maximum(pn - pc, 1)))
                rng = np.random.default_rng([SEED, 0 if campaign == "all" else 1,
                                             0 if position == "pooled" else 1, cut])
                draws = rng.beta(hc + .5, hn - hc + .5, size=(DRAWS, K))
                best = int(np.argmax(held))
                winprob = np.bincount(np.argmax(draws, axis=1), minlength=K) / DRAWS
                rankrows.append({"campaign": campaign, "position": position, "prefix_days": cut,
                                 "items": K, "empirical_best_item": int(items[best]),
                                 "empirical_best_ctr": float(held[best]),
                                 "posterior_prob_empirical_best_is_best": float(winprob[best]),
                                 "items_with_p_best_above_1pct": int((winprob > .01).sum())})
                for i, item in enumerate(items):
                    itemrows.append({"campaign": campaign, "position": position, "prefix_days": cut,
                                     "item": int(item), "prefix_clicks": int(pc[i]), "prefix_impressions": int(pn[i]),
                                     "heldout_clicks": int(hc[i]), "heldout_impressions": int(hn[i]),
                                     "prefix_ctr": float(ppre[i]), "heldout_ctr": float(held[i]),
                                     "prefix_simultaneous_lower": float(low[i]),
                                     "prefix_simultaneous_upper": float(high[i]),
                                     "posterior_best_probability": float(winprob[i])})
                seg = pre.groupby(["item_id", "user_feature_0"]).click.agg(["sum", "size"]).unstack().reindex(items)
                m = float(pre.click.mean())
                profile = np.log((seg["sum"].fillna(0) + 20 * m) /
                                 (seg["size"].fillna(0) - seg["sum"].fillna(0) + 20 * (1 - m))).to_numpy()
                profile = (profile - profile.mean(0)) / np.maximum(profile.std(0), 1e-8)
                audience = KMeans(n_clusters=C, n_init=20, random_state=SEED).fit_predict(profile)
                graphs = {"attr": attr, "audience": audience, "attr_shuffled": rng.permutation(attr)}
                for graph, labels in graphs.items():
                    members = [np.flatnonzero(labels == c) for c in np.unique(labels)]
                    raw = np.array([np.ptp(ppre[s]) for s in members])
                    conservative = np.array([min(1., high[s].max() - low[s].min()) for s in members])
                    truth = np.array([np.ptp(held[s]) for s in members])
                    range_draws = np.stack([np.ptp(draws[:, s], axis=1) for s in members], axis=1)
                    assert np.isfinite(range_draws).all() and (conservative + 1e-12 >= raw).all()
                    for kind, width in [("raw_prefix", raw), ("simultaneous_binomial", conservative)]:
                        cover = range_draws <= width[None, :] + 1e-12
                        rows.append({"campaign": campaign, "position": position, "prefix_days": cut,
                                     "graph": graph, "width": kind, "components": len(members),
                                     "median_width": float(np.median(width)),
                                     "covers_heldout_point_range_share": float((width + 1e-12 >= truth).mean()),
                                     "posterior_component_coverage_mean": float(cover.mean()),
                                     "posterior_all_components_covered_probability": float(cover.all(1).mean())})
                print(campaign, position, "prefix", cut, "complete", flush=True)
    table, ranks = pd.DataFrame(rows), pd.DataFrame(rankrows)
    table.to_csv(OUT / "calibration.csv", index=False)
    ranks.to_csv(OUT / "ranking_uncertainty.csv", index=False)
    pd.DataFrame(itemrows).to_csv(OUT / "item_counts.csv", index=False)
    (OUT / "metadata.json").write_text(json.dumps({"seed": SEED, "posterior_draws": DRAWS,
        "posterior": "independent Jeffreys Beta(clicks+0.5, impressions-clicks+0.5) on held-out counts",
        "prefix_bounds": "Clopper-Pearson, Bonferroni over K items, family alpha=0.05",
        "scope": "Sensitivity analysis under pooled binomial rates; no future-drift guarantee or new policy runs",
        "sources_sha256": sources, "seconds": time.perf_counter() - started}, indent=2) + "\n")
    report = ["# OBD calibration and truth uncertainty sensitivity", "",
        "All/Women campaigns; pooled positions and position 1; first 2, 3 or 4 days as prefix.",
        "Graphs and widths use only the prefix. Held-out rates use the remaining days.", "",
        "Raw prefix ranges ignore sampling uncertainty. The alternative uses simultaneous exact",
        "binomial item intervals, then max upper minus min lower in each component. Those bounds",
        "cover stationary prefix rates under the binomial model; future drift is outside that guarantee.", "",
        "Posterior coverage integrates 5,000 independent Jeffreys posterior draws of held-out rates.",
        "This is a sensitivity measure conditional on a stationary pooled-rate model, not frequentist",
        "coverage under temporal dependence. Attribute groups use released retrospective metadata.", "",
        "This audit adds no new bandit-policy results. Existing policy comparisons remain in",
        "`../../oct10_runs/results/obd_pooling/tables.md` and use fixed held-out point estimates as truth.", "",
        "## Uncertainty about the empirically best item", "", ranks.round(5).to_markdown(index=False), "",
        "## Component range calibration", "", table.round(5).to_markdown(index=False), ""]
    (OUT / "tables.md").write_text("\n".join(report))


if __name__ == "__main__":
    main()
