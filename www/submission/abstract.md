# OpenReview Abstract (due 18 October 2026, AoE)

Paste into OpenReview (`Conference_Long_Papers`). Authors are frozen after this deadline, and placeholder abstracts are forbidden. The text matches the abstract in [main.tex](main.tex); change both together.

**Title:** When Can a Bandit Trust Correlation? Spatial and Temporal Dependence in Web Bandits

**Track:** Search, Recommendation, and Retrieval-Augmented AI (alternative: Graph Algorithms and Modeling for the Web)

**Keywords:** multi-armed bandits; spatiotemporal dependence; graph bandits; restless bandits; autoregressive rewards; confidence sequences

**Abstract** (290 words):

Web rewards are correlated in space and time. Items that are close in a co-engagement or hyperlink graph share long-run appeal and short-run shocks, and engagement persists for days. We develop a theory of bandits under this spatiotemporal dependence and test its predictions on three Web platforms. Each reward is a fixed long-run mean plus an autoregressive deviation whose innovations are correlated across arms. A graph can play two distinct roles: it can restrict the means through a Laplacian energy bound, or shape the shock covariance. We show that the node-time covariance factors into a spatial innovation covariance and per-arm temporal impulse responses, and is separable only when all arms share the same dynamics. An exact innovation regression turns any adaptive, restless history into a predictable linear experiment. Its information is bounded above and below by sample counts scaled by the extremes of the spectral density, which combines the shocks' spatial spectrum with the AR frequency response. This yields graph-regularized confidence sets valid at all times and sublinear mean regret. In graph Fourier modes, long-run information is c²/q_k per field, so graph-smooth shocks make rough contrasts cheap and smooth ones expensive. Certified graph pooling remains valid under this dependence. Confidence sets built for independent rewards are inflated by the autocorrelation under bursty exposure, and the best sampling schedule depends on how spatial correlation meets the lag structure. On real data, held-out Wikipedia attention shows the predicted inflation, a week of views carrying the information of 1.3–1.9 independent days, and iid certificates fail in 56–95% of runs on worlds calibrated to it. Certified pooling gains track the components it can reject (Spearman −0.87 on KuaiRec, −0.81 on the Open Bandit Dataset), and persistence-aware policies halve regret on a chronological KuaiRec panel.

## Where each number comes from

| Claim | Source |
| --- | --- |
| Node-time covariance, spectral sandwich, long-run information by graph mode, AR(2) schedules | Proofs in Appendix A of [main.tex](main.tex), adapted from [research/gpt_sol_10_09/appendices/spatiotemporal_bandits.tex](../../research/gpt_sol_10_09/appendices/spatiotemporal_bandits.tex) |
| Spearman −0.87 (KuaiRec), −0.81 (OBD) | [experiments/report §3](../../experiments/report/README.md#3-mean-channel-certified-pooling-a1-a4-n1) |
| Real graphs beat rewired only under certification (0.916) | [experiments/report §3](../../experiments/report/README.md#shrinkage-against-structure) |
| 1.3–1.9 independent days per week | [experiments/report §4](../../experiments/report/README.md#b2-iid-certificates-fail-and-real-data-is-in-the-failure-regime) |
| 56–95% iid violations; innovation 0–1% | [oct10_evening §3b](../../experiments/oct10_evening/README.md) |
| Persistence-aware policies halve regret; last value ties | [experiments/report §6](../../experiments/report/README.md#6-fluctuation-channel-dynamic-policies-s5-p1) |
