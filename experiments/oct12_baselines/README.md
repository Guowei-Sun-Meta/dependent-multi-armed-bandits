# Standard Web-bandit baselines, 12–13 October 2026

These are baselines that WWW reviewers expect but the paper lacked: online user clustering (CLUB) and feature-based pooling (LinUCB, linear TS, a hybrid feature prior). Each reuses the instances and common random numbers of an existing KuaiRec experiment, so its runs pair with the policies already there.

| Script | Experiment | Results |
| --- | --- | --- |
| `code/club.py` | Non-contextual CLUB-style TS on Setting B (8 instances, 300 users, 100 videos, T = 100,000). Initial graph complete, U-coeng or rewired; γ ∈ {0.25, 0.5, 1} | `results/club_runs.csv` |
| `code/gbm_daily.py` | Forecast-then-rank: a pooled gradient-boosted regressor on lag features (trained on the prefix with simulated staleness), greedy top k, on the chronological KuaiRec daily slot (15 units, k ∈ {1, 5}, 5 seeds) | `results/gbm_daily_runs.csv` |
| `code/lin_setting_a.py` | LinTS, LinUCB and hybrid feature TS on Setting A v2 (360 instances, T = 20,000), using leakage-free I-mf embeddings. Tuned on 30 tuning users, then frozen | `results/lin_setting_a_*.csv`, `lin_setting_a_tuned.json` |

## Results

**Setting B.** The table gives regret ÷ per-user TS, as the mean over instances.

| Policy | Ratio |
| --- | ---: |
| Population shrinkage (Laplacian-pooled TS, complete graph) | 0.726 |
| CLUB-TS, γ ∈ {0.5, 1}, any initial graph | 0.927–0.962 |
| CLUB-TS, γ = 0.25 (splits every user apart) | 1.00–1.01 |

**Setting A v2.** These are ratios of mean regret, with 95% user-bootstrap intervals over 120 users and 3 subsets each.

| Policy (tuned) | ÷ Beta TS | ÷ fixed-level KL-UCB | Users above 2× TS |
| --- | --- | --- | ---: |
| LinTS (σ = 0.5, d = 64) | 1.212 [0.968, 1.497] | 0.533 [0.427, 0.674] | 30.8% |
| LinUCB (α = 1, d = 16) | 3.389 [2.822, 4.075] | 1.490 [1.224, 1.797] | 60.8% |
| Hybrid feature TS (τ² = 0.02, d = 16) | **0.674** [0.618, 0.738] | 0.296 [0.264, 0.333] | 9.2% |

Further comparisons for hybrid feature TS:
- Against graph-free shrinkage TS (λ = 10): 0.980 [0.902, 1.071], indistinguishable.
- Against Spectral TS on real I-mf: 0.849 [0.753, 0.950].

**Reading.** A pure linear model on the embeddings misspecifies individual taste and leaves a heavy tail. Adding a per-item effect turns it into shrinkage with a feature-informed prior. That ties graph-free shrinkage, so neither features nor graphs add average value beyond shrinkage on KuaiRec.

**Chronological KuaiRec daily slot: forecast, then rank.** Paired with `oct10_evening/results/daily_chrono/test_runs.csv`, using the same two-level bootstrap over windows and panels.

| | k = 1 | k = 5 |
| --- | --- | --- |
| Forecaster ÷ iid TS | 0.562 | 0.637 |
| Against iid TS | −43.8% [−74.2%, −15.1%] | −36.3% [−58.0%, −18.2%] |
| Against last observed value | +14.4% [−16.6%, +170.4%] | **+48.1% [+16.3%, +128.5%]** |
| Against joint filter (greedy) | +19.6% [−5.5%, +157.1%] | **+44.7% [+20.0%, +64.6%]** |

**Reading.** A generic learned forecaster beats iid TS. At five videos a day, though, it is clearly worse than both the last observed value and the joint filter, so a practical forecaster does not recover the persistence gain that simple persistence captures.

## Reproduce

From the repository root, with `data/kuairec_cache` built (`kuairec/code/data.py`, then `graphs.py --k 10`):

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/oct12_baselines/code/club.py --jobs 6           # minutes
OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/oct12_baselines/code/lin_setting_a.py --jobs 4  # about 4 h
OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/oct12_baselines/code/gbm_daily.py --jobs 4       # under a minute; needs oct10_evening daily_chrono units
```
