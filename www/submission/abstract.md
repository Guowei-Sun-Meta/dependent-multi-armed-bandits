# OpenReview Abstract (due 18 October 2026, AoE)

Paste into OpenReview (`Conference_Long_Papers`). Authors are frozen after this deadline, and placeholder abstracts are forbidden. The text matches the abstract in [main.tex](main.tex); change both together.

**Title:** When Can a Bandit Trust Correlation? Certified Pooling under Persistent Web Rewards

**Track:** Search, Recommendation, and Retrieval-Augmented AI (alternative: Graph Algorithms and Modeling for the Web)

**Keywords:** multi-armed bandits; correlated arms; graph bandits; restless bandits; confidence sequences; recommendation

**Abstract** (248 words):

Web platforms hold many graphs, such as co-engagement, embeddings and hyperlinks, that seem to say which items share appeal. Their rewards are also restless: engagement persists for days and moves together across items. Bandits that pool information along such graphs, or that build confidence sets as if rewards were independent, can fail. We ask when a learner can trust correlation. We model each reward as a long-run mean, restricted by a graph certificate, plus a persistent autoregressive deviation whose shocks are correlated along a graph. For the mean channel, certified pooling gains in proportion to the components its certificate can reject. Across certificates, regret falls with the rejectable share (Spearman −0.87 on KuaiRec, −0.81 on the Open Bandit Dataset). Uncertified pooling fails on a minority of instances, and real graphs beat rewired ones only under certification. To bridge the two channels, we prove two results. Certified pooling stays valid under persistent, correlated, restless sampling when its confidence sets come from an exact innovation regression. Confidence sets built for independent rewards fail under bursty exposure, by an inflation factor we derive. Real Wikipedia attention is in this failure regime: a week of consecutive views carries the information of 1.3–1.9 independent days. On worlds calibrated to it, iid certificates are violated in 56–95% of runs, while innovation certificates hold but are still too wide to act on. On a chronologically valid KuaiRec panel, persistence-aware policies halve regret against Thompson sampling, but the last observed value captures most of the gain.

## Where each number comes from

| Claim | Source |
| --- | --- |
| Spearman −0.87 (KuaiRec), −0.81 (OBD) | [experiments/report §3](../../experiments/report/README.md#3-mean-channel-certified-pooling-a1-a4-n1) |
| Real graphs beat rewired only under certification (0.916) | [experiments/report §3](../../experiments/report/README.md#shrinkage-against-structure) |
| 1.3–1.9 independent days per week | [experiments/report §4](../../experiments/report/README.md#b2-iid-certificates-fail-and-real-data-is-in-the-failure-regime) |
| 56–95% iid violations; innovation 0–1% | [oct10_evening §3b](../../experiments/oct10_evening/README.md) |
| Persistence-aware policies halve regret; last value ties | [experiments/report §6](../../experiments/report/README.md#6-fluctuation-channel-dynamic-policies-s5-p1) |
