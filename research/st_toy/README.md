# Spatiotemporal Bandits: Algorithm Catalog and a Toy Benchmark

9 October 2026. In web applications iid rewards are rare. Video engagement, ad response and traffic all persist over days and move together across similar items. This note does two things:

1. It collects the algorithms already developed in this repo's theory notes that model that dependence, and maps each to an application role.
2. It tests them on a toy with 100 arms on a grid, AR(20) fluctuations and spatially correlated innovations, against standard bandits.

## 1. Algorithms available from the theory notes

| # | Algorithm | Source | What it assumes | Decision target | Role in applications |
| --- | --- | --- | --- | --- | --- |
| 1 | **Joint Kalman filter** on long-run means plus AR lag states, with graph-correlated innovations | [spatiotemporal_bandits §4](../spatiotemporal_bandits/README.md), [ar_p_bandits](../ar_p_bandits/README.md) | Known AR coefficients, innovation covariance and noise; Gaussian mean prior | Inference engine | One observation updates every arm and every lag. All model-based policies below run on it |
| 2 | **Spatiotemporal greedy** | Same | As 1 | Current reward | Baseline: exploits the forecast with no exploration |
| 3 | **Joint posterior (Thompson) sampling** of current rewards | spatiotemporal_bandits §6 | As 1 | Current reward | Simple, scalable default for restless feeds |
| 4 | **Exact two-period score** (rolling knowledge gradient): current mean plus E max of next-round means | spatiotemporal_bandits §6; ar_p_bandits | As 1 | Current plus next reward | Values an observation by how much it sharpens **next-round decisions**, not by its variance. Common-mode fluctuations cancel |
| 5 | **TV-GP-UCB on the node-time kernel** | spatiotemporal_bandits §9B | Correct Gaussian prior | Current reward | Comes with a generic regret bound; that bound can be linear |
| 6 | **Joint Predictive Sampling** (samples only the information that persists) | [predictive_ar1](../predictive_ar1/README.md); ar_p_bandits; spatiotemporal_bandits §6 | **Known long-run means** | Current reward | Mature catalogs where means are known and only fluctuations matter. Not exact with unknown means, so it is not in the toy |
| 7 | **PCS knowledge gradient / contrast information sampling** | spatiotemporal_bandits §7; [graph_ar1_mean](../../experiments/graph_ar1_mean.py) | As 1 | Final selection | A/B tests and launch decisions under autocorrelated traffic, for example choosing which creative to promote after a test window |
| 8 | **Graph-AR GLS mean estimator** with an energy constraint | spatiotemporal_bandits (standalone paper) | Known dynamics; trusted energy radius | Long-run means | Certified estimates of persistent item quality from autocorrelated logs |
| 9 | **Certified graph pooling** (SP-UCB, GDE-UCB) | [alignment_paper](../alignment_paper/README.md) | Valid component certificates | Mean regret | Already tested on KuaiRec ([report](../kuairec_graphs/README.md)). Safe pooling over item or user graphs |
| 10 | **Refresh-probe policy** with a constructive upper bound | predictive_ar1 | Known dynamics | Current reward | Simple deployable rule with a guarantee: probe each arm once per block, then exploit forecasts |
| 11 | **Innovation lower bound** G(μ, Γ) − G(μ, Γ − Q) per round | predictive_ar1; spatiotemporal_bandits §9A | — | Benchmark | Regret no causal policy can beat. It shows how close a policy is to the achievable limit |

Gaps the toy exposes, which become research targets:

- **Unknown dynamics.** All policies here know the AR coefficients and covariance. Real data requires learning them; Trella et al. (RLC 2025) and Ziomek et al. (AISTATS 2025) are the closest work.
- **Unknown-mean Predictive Sampling.** Algorithm 6 needs a target that screens the permanent mean as well as the future states.
- **Scale.** The state dimension is N(p + 1), which is 2,100 here, at O(N²p²) memory. Catalogs need low-rank or graph-spectral state approximations (spatiotemporal_bandits §10).

## 2. Toy benchmark

The world is restless: every arm evolves every round, and the learner sees only the pulled arm.

```math
f_{i,t}=\mu_i+z_{i,t},\qquad z_t=\sum_{r=1}^{20}a_r z_{t-r}+\varepsilon_t,\qquad \varepsilon_t\sim N(0,qC),\qquad Y_t=f_{a_t,t}+\xi_t
```

- 100 arms on a 10 × 10 grid. C is the unit-diagonal graph resolvent (I + 5L)⁻¹, so neighbouring arms' fluctuations are strongly correlated.
- AR(20) coefficients are proportional to exp(−r/6) and sum to 0.97 (strong persistence). q is chosen so that Var(z) = 1. Long-run means μ ~ N(0, 0.25 C) are smooth on the grid, and observation noise has standard deviation 0.3.
- Two other configurations: **weak_persistence** (coefficients sum to 0.6) and **no_spatial** (C = I).
- Horizon T = 2,000 (20 rounds per arm), 8 seeds. The world trajectory and noise are shared across policies (paired).
- **Dynamic regret** is measured against the oracle that knows every arm's current reward. **Mean regret** is measured against the best long-run mean.

| Family | Policies | What it models |
| --- | --- | --- |
| iid | UCB1, Gaussian TS, sliding-window UCB (window 500) | Nothing |
| spatial only | SpectralUCB / SpectralTS (graph prior on means, iid noise) | Smooth means |
| temporal only | AR-TS, AR two-step (exact AR(20) filter per arm; spatial correlation ignored) | Persistence |
| spatiotemporal | ST greedy, ST TS, ST UCB, ST two-step (joint filter, algorithms 1–5) | Both |

The filter is verified against dense Gaussian conditioning over the full node-time covariance. The expectation in the two-period score uses a 256-point normal-quantile grid, verified against the exact upper-envelope formula.

## 3. Results

*Running; this section is filled in when the runs finish.*

## Reproduce

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/st_toy/toy.py --verify
OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/st_toy/toy.py --seeds 8 --horizon 2000 --jobs 3
.venv/bin/python -I experiments/st_toy/analyze.py
```
