# 10 October runs: first results for experiments 3a, 4, 6 and 8

These are the experiments in [experiment_plan.md](../experiment_plan.md) that could run on 10 October without the KuaiRec raw data. That data is missing from this checkout, so experiments 1, 2, 7 and the KuaiRec half of 3a are not here. Design and deviations: [design.md](design.md). Full tables: `results/*/tables.md`. Everything ran on the laptop in about 1.5 hours of wall time.

## Headlines

1. **Real attention dynamics sit in B2's failure regime, and prefix fits predict by how much.**
   - On Wikipedia, a 7-day block of consecutive observations has 3.6–5.3 times the variance that iid days would give. For a level estimate, it is worth about 1.3–1.9 iid days.
   - AR(7) or AR(20) fits on 2022–2023 predict the 2024–2025 inflation to within 5–10% on the six-community panel, and 10–40% on the one-domain panel.
   - The lag-1 AR(1) shortcut underpredicts by 1.2–3.3×.
   - All fits under-predict for about two-thirds of articles, so a real-data certificate needs a margin.
2. **Innovation certificates (B1″) hold up when the dynamics are estimated from a long prefix.**
   - With a 365-round prefix, violations stay at 0–3%, matching known dynamics and the δ = 0.05 target.
   - A 100-round prefix under-covers at φ = 0.97: 10–40% of runs violate.
   - Adding 2 standard errors to φ̂ cuts that to 3–27%. It helps, but does not fully fix it.
   - Two misspecifications break the certificate:
     - a missed weekly lag (AR(7) truth fitted as AR(1)): 20–73% of runs violate;
     - heavy-tailed t(3) shocks: up to 17%.
   - Ignoring shock correlation did no harm in these worlds.
   - The iid certificate violates in 67–100% of bursty persistent runs.
3. **B2's regret consequence is real, and so is the price of validity.**
   - Under bursty exposure, iid-certified elimination drops the best arm in 28–89% of runs at φ ∈ {0.9, 0.97}. Those runs then lose 0.14–0.26 per round for the rest of the horizon, which is linear regret.
   - The valid certificate never drops it, but at φ ≥ 0.9 it also eliminates nothing within 20,000 rounds.
   - The information per pull shrinks by about (1 − φ)/(1 + φ), so certified exploration takes 19–66 times longer.
   - At T = 20,000 the invalid iid rule still has lower total regret. The valid rule wins only at longer horizons, where linear regret dominates.
4. **B3: the (1 − ρ) slate gain is exact only for equal pairs.**
   - With unequal variances or mixed persistence, the gain shrinks: 0.28 and 0.38 instead of 0.10 at ρ = 0.9. The long-run covariance formula Ω predicts it exactly.
   - Under persistence, alternating (staggered) observations keep almost the whole gain. Under iid rewards they keep none of it.
5. **The Open Bandit Dataset supports the mean channel, not the fluctuation channel.**
   - Item click rates are learnable: the reliability of a 7-day click rate is 0.79–0.92.
   - Their daily wobble is larger than binomial noise, but it does not persist (lag-1 autocorrelation −0.14 to −0.22).
   - The semi-synthetic pooling run repeats the KuaiRec pattern on a second recommender:
     - graph-free empirical-Bayes Thompson sampling (TS) is best (regret 0.21–0.29 × KL-UCB);
     - oracle-certified pooling gains only 0–30%;
     - uncertified pooling fails by dilution on one graph: it never finds the best item.

## 3a. Variance inflation on Wikipedia (`results/inflation/`)

Here x is log(1 + views) per article. Fit on 2022–2023, observe on 2024–2025. Values are medians over 150 articles per panel. "Level" removes each article's own mean; "weekday" also removes the weekday profile estimated on the prefix.

| Panel, variant | Lag-1 ρ | Observed, 7-day | AR(1) prediction | AR(20) prediction | Observed, 28-day | AR(1) prediction | AR(20) prediction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| One domain, level | 0.58 | 3.6 | 2.9 | 2.9 | 12.7 | 3.5 | 8.2 |
| One domain, weekday | 0.67 | 5.0 | 3.4 | 4.5 | 17.1 | 4.6 | 13.2 |
| Six communities, level | 0.76 | 5.1 | 4.1 | 4.8 | 17.0 | 6.5 | 14.3 |
| Six communities, weekday | 0.79 | 5.3 | 4.4 | 5.0 | 17.8 | 7.4 | 15.3 |

- The ratio of observed to AR(20)-predicted inflation, at 7 and 28 days, is 1.04–1.10 on the six-community panel and 1.08–1.47 on the one-domain panel.
- The prediction is too low for 61–75% of articles.

**Caveat.** The panels were selected retrospectively. This is a diagnostic of dynamics, not policy evidence.

## 4. Certificates with estimated and misspecified dynamics (`results/robustness/`)

N = 20 arms, T = 5,000, 30 seeds per cell. The table gives the share of runs with any SP-UCB certificate violation under bursty exposure (batch 25), for independent and correlated shocks.

| Learner | φ = 0.5 | φ = 0.9 | φ = 0.97 |
| --- | --- | --- | --- |
| Innovation, known dynamics | 0% / 0% | 0% / 0% | 0% / 0% |
| Fitted, 365-round prefix | 0% / 3% | 0% / 0% | 0% / 0% |
| Fitted, 100-round prefix (median φ̂ = 0.46, 0.87, 0.94) | 0% / 7% | 0% / 3% | 17% / 10% |
| Fitted 100 + 2 SE | 0% / 3% | 0% / 3% | 7% / 3% |
| φ − 0.05 | 0% / 3% | 0% / 3% | 0% / 0% |
| Correlation ignored (correlated truth only) | 0% | 0% | 0% |
| t(3) shocks, known parameters | 7% / 17% | 10% / 10% | 7% / 3% |
| **iid certificate** | 10% / 7% | **87% / 67%** | **90% / 87%** |

When the truth is AR(7) with a weekly lag:
- **AR(1) fitted on 365 rounds:** 20% / 27%.
- **iid certificate:** 77% / 77%.

**Elimination at T = 20,000** (batch 25), which separates validity from power:

| Learner | Violation rate (φ = 0.9 / 0.97) | Best arm eliminated (φ = 0.9 / 0.97) | Eliminates anything? |
| --- | --- | --- | --- |
| Innovation, known or fit365 | 0–3% | 0% | No: regret equals round-robin |
| Fitted, 100-round prefix | 7–10% / 30–40% | 0–3% | Barely |
| Fitted 100 + 2 SE | 3% / 10–27% | 0% | Barely |
| AR(7) truth fitted as AR(1) | 63–73% | 10% | Yes |
| iid certificate | 87–100% | 27–47% / 57–77% | Yes |

**Takeaways**
- Validity survives estimation from a long prefix.
- With a short prefix, φ is biased low (shrinkage from demeaning), so coverage fails at high persistence. The +2 SE fix is only partial.
- The dangerous misspecification is a **missed lag**: weekly structure fitted as AR(1). It should be the first robustness item in the paper.
- The paper's claim should read "valid when the dynamics are estimated from a long enough prefix with the right lag structure". Report empirical coverage, not a theorem.

## 6. Theory instances (`results/theory_instances/`)

**B2: false elimination** (certified successive elimination, known dynamics, 100 seeds, T = 20,000).

| φ | Batch | iid: best eliminated | iid: regret per round after | B1″: best eliminated | Regret at 20k (iid / B1″) |
| --- | --- | --- | --- | --- | --- |
| 0 | any | 0% | — | 0% | 4,566 / 3,805 |
| 0.9 | 10 | 5% | 0.20 | 0% | 2,762 / 4,696 |
| 0.9 | 25 | 28% | 0.14 | 0% | 2,115 / 4,696 |
| 0.9 | 100 | 39% | 0.15 | 0% | 2,552 / 4,696 |
| 0.97 | 10 | 28% | 0.17 | 0% | 2,750 / 4,696 |
| 0.97 | 25 | 72% | 0.23 | 0% | 3,558 / 4,696 |
| 0.97 | 100 | 89% | 0.26 | 0% | 4,550 / 4,696 |

- With continuous exposure (batch 1), even the iid rule never drops the best arm. The failure needs **bursty exposure and persistence together**, as B2 says.
- The valid rule at φ ≥ 0.9 is still pure round-robin at 20,000 rounds (regret 4,696). The paper should state the trade-off honestly: valid certificates under persistence cost exploration time of order (1 + φ)/(1 − φ).

**B3: slate contrast.** Variance of a two-arm contrast relative to ρ = 0, for n = 365 observations of each arm.

| Pair | ρ = 0.3 | ρ = 0.6 | ρ = 0.9 | Staggered, ρ = 0.9 |
| --- | --- | --- | --- | --- |
| Equal, φ = 0.9 | 0.70 | 0.40 | 0.10 | 0.11 |
| Unequal sd (1 and 2) | 0.76 | 0.52 | 0.28 | 0.28 |
| φ = 0.9 with φ = 0.5 | 0.79 | 0.59 | 0.38 | 0.41 |
| Equal, iid | 0.70 | 0.41 | 0.11 | **1.00** |

- The long-run formula (Ω_ii + Ω_jj − 2Ω_ij)/(Ω_ii + Ω_jj) matches the exact values to 3 decimals at n = 365.
- At n = 7 the long-run variance overstates the exact one by about 3×.
- A Monte Carlo check (20,000 draws) agrees with the exact formula to within 0.3%.

## 8a. Open Bandit Dataset feasibility (`results/obd_feasibility/`)

Uniform-random logs, 24–30 November 2019, CC BY 4.0. Propensities are uniform (1/80, 1/34, 1/46).

| Campaign | Rows | Items | Clicks | CTR | Between-item sd / sampling se | Split-half r (days 1–3 vs 4–7) | Daily dispersion (null 95% quantile) | Lag-1 autocorrelation of daily residuals |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| All | 1,374,327 | 80 | 4,768 | 0.35% | 3.5 | 0.71 | 1.97 (1.29) | −0.22 |
| Men | 452,949 | 34 | 2,321 | 0.51% | 1.9 | 0.33 | 2.02 (1.42) | −0.20 |
| Women | 864,585 | 46 | 4,163 | 0.48% | 3.1 | 0.49 | 2.10 (1.36) | −0.14 |

- Position effects are under 10% relative.
- The top item differs between the two halves in all three campaigns.
- At 6-hour bins the median is 1–2 clicks per item, and residual autocorrelation is about 0.
- **Decision:** the mean channel goes ahead (8b, on the All and Women campaigns). The fluctuation or censored-feedback study is deferred, because the excess variation does not persist.

## 8b. Certified pooling on OBD click rates (`results/obd_pooling/`)

Setup:
- **Truth:** day 4–7 click rates.
- **Components:** built from days 1–3.
- **Horizon and seeds:** 2M impressions, in blocks of 100, 20 seeds.

Each cell is regret at T = 2M relative to KL-UCB at the same fixed confidence level, paired by seed; lower is better.

| Policy | All: attr | All: audience | All: attr shuffled | Women: attr | Women: audience | Women: attr shuffled |
| --- | --- | --- | --- | --- | --- | --- |
| SP-KLUCB, oracle certificate | 0.84 | 0.70 | 0.87 | 0.98 | 0.97 | 0.95 |
| SP-KLUCB, prefix certificate | 0.86 | 0.78 | 0.87 | 1.01 | 0.81 | 1.01 |
| SP-KLUCB, no certificate | 0.66 (best found 28%) | 0.60 (**best never found**) | 0.41 | 1.14 | 0.88 | 0.34 |
| TS pooled toward the component mean (uncertified) | 0.27 | 0.27 | 0.33 | 0.44 | 0.32 | 0.29 |

Graph-free baselines, each with a single ratio per campaign (All / Women):

| Baseline | All | Women |
| --- | --- | --- |
| KL-UCB, log t level | 0.68 | 0.75 |
| Beta TS | 0.35 | 0.39 |
| Empirical-Bayes TS (prior fitted on days 1–3) | **0.21** | **0.29** |

- **Prefix certificate coverage.** The prefix range covers the true within-component range in only 25–70% of components, because click rates drift between the two halves. Even so, its regret is close to the oracle's.
- **Real against shuffled components.** Real components beat shuffled ones only for the oracle certificate on the All campaign: 0.70–0.84 against 0.87. As on KuaiRec, the average gains come from **shrinkage, not from graph structure**.
- **Uncertified pooling.** On All with the audience components, no-certificate SP-KLUCB never finds the best item, and its regret grows linearly. That is the dilution failure, now on a second platform.

## Cross-check with the parallel runs in `today_2026_10_10/`

Another agent ran overlapping experiments on the same day, with independent code and designs; see [its README](../today_2026_10_10/README.md). Where the two overlap, they agree:

| Question | Here | today_2026_10_10 |
| --- | --- | --- |
| Wrong-order dynamics against innovation coverage | AR(7) truth fitted as AR(1): 20–73% of runs violate | AR(20) truth, wrong order or diagonal fit: 40/100 fail |
| Fitted dynamics from a 365-round prefix | 0–3% violate | 5/100 fail |
| iid elimination under bursty persistence | φ = 0.97: 72–89% drop the best arm | φ = 0.97 and 0.995: 30/100 and 47/100 |
| Valid elimination | Never drops the best arm, never eliminates at φ ≥ 0.9 | Same: 0/100, no elimination at its horizons |
| Slate (1 − ρ) | Exact only for equal pairs; Monte Carlo within 0.3% | Within 1.8% in 8 configurations |
| OBD temporal signal | No persistence at daily or 6-hour bins | 92% of hourly bins have no click; Gaussian filtering poorly supported |

Each covers ground the other does not:
- **Only here:** the Wikipedia variance-inflation diagnostic, and the OBD mean-channel pooling run.
- **Only there:** full-year Wikipedia policy baselines, the correlation factorial screen, and the OBD censored-learner pilot.

## What this changes in the plan

- **Gate B (16 October) can be answered now for experiment 4.** The abstract should say "valid when the dynamics are estimated with the right lag structure from a long enough prefix", and the paper should show the missed-weekly-lag failure.
- **Experiment 3b** should use AR(7) or AR(20) learners, since AR(1) under-covers on real data. It should also add a margin: the observed-to-predicted inflation of 1.05–1.5 suggests inflating the variance by about 1.5.
- **The B2 story needs the trade-off stated:** iid certificates fail, and valid ones are slow by a factor of about (1 + φ)/(1 − φ). A sharper certificate is the open method problem.
- **OBD gives the paper a second real recommender for Q2:** shrinkage dominates, certified pooling is safe but gains little, and uncertified pooling can fail. It is semi-synthetic, and must be labelled as such.
- **Still needed:** KuaiRec raw data (Zenodo record 18164998) for experiments 1, 2, 7 and the KuaiRec half of 3a.

## Reproduce

From the repository root, with `.venv` built from `experiments/requirements.txt`. OBD unzipped into `data/obd/` from `https://research.zozo.com/data_release/open_bandit_dataset.zip`; only `random/` is needed.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
.venv/bin/python -I experiments/oct10_runs/code/inflation.py                        # 1 min
.venv/bin/python -I experiments/oct10_runs/code/robustness.py --seeds 30 --jobs 5   # ~15 min
.venv/bin/python -I experiments/oct10_runs/code/robustness.py --policies se_st2 se_iid \
    --horizon 20000 --phis 0.9 0.97 --batches 25 --tag _elim20k --jobs 3            # ~30 min
.venv/bin/python -I experiments/oct10_runs/code/theory_instances.py b3              # seconds
.venv/bin/python -I experiments/oct10_runs/code/theory_instances.py b2 --seeds 100 --jobs 2   # ~1 h
.venv/bin/python -I experiments/oct10_runs/code/obd_feasibility.py                  # 2 min
.venv/bin/python -I experiments/oct10_runs/code/obd_pooling.py --seeds 20 --jobs 3  # ~1 h
.venv/bin/python -I experiments/oct10_runs/code/analyze.py
```
