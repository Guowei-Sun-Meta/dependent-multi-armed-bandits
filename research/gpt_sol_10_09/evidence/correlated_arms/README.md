# Correlated Arms: Theory Map for the WWW 2027 Long Paper

9 October 2026. The paper merges the graph-alignment work and the spatiotemporal work into one model of correlated arms. Graphs are the tool for encoding correlation. This note lists each result, where it was proved, and the new bridging results (B1–B3), with their proofs or proof plans.

Source labels:
- **[A]** [alignment_paper/manuscript.tex](../alignment_paper/manuscript.tex)
- **[S]** [spatiotemporal_bandits/manuscript.tex](../spatiotemporal_bandits/manuscript.tex)
- **[P]** [predictive_ar1](../predictive_ar1/README.md), [two_arm_ar1](../two_arm_ar1/README.md), [ar_p_bandits](../ar_p_bandits/README.md)
- **[N]** the repo note [graph_spectral_bandits.md](../graph_spectral_bandits.md)

## Model

N arms. At each round the learner pulls one arm, or a slate of k arms, and every arm keeps evolving:

```math
Y_t=\mu_{a_t}+z_{a_t,t}+\xi_t,\qquad z_t=\sum_{r=1}^{p}A_r z_{t-r}+\eta_t,\qquad \eta_t\sim N(0,Q_G),\qquad \xi_t\sim N(0,r)
```

- **Mean channel.** μ is fixed and unknown, in [0, 1]^N. A graph supplies either a component partition with certified diameters $`\varepsilon_c\ge\max_{i\in C_c}\mu_i-\min_{i\in C_c}\mu_i`$, or an energy certificate $`\mu^\top L\mu\le S^2`$. **[A] Lemma 1** converts energy into diameters through the resistance diameter.
- **Fluctuation channel.** Stable AR dynamics, known in the theory and estimated in the experiments. The innovation covariance Q_G is built from a graph.
- **Regrets.**
    - Mean regret: $`\mathcal R_T=\sum_t(\mu^\star-\mu_{a_t})`$.
    - Dynamic regret: against $`\max_i f_{i,t}`$.
- **iid case:** A_r = 0 and Q_G diagonal.

## Reused results

| Label | Statement (short) | Source | Role in the paper |
| --- | --- | --- | --- |
| A1 | SP-UCB regret: $`\sum_{c\in\mathcal O}A_c+\sum_{c\notin\mathcal O}\min\{A_c,H_c\}`$, with H_c finite only when ε_c < Γ_c | [A] Thm "Alignment-sensitive finite-time guarantee" | Mean channel, iid noise; template for B1 |
| A2 | Path versus clique: the same diameters but information costs differing by a factor growing with m; GDE-UCB attains the path rate | [A] main separation and GDE-UCB theorem | Graph geometry, not diameter, sets the value of correlation |
| A3 | Graph-error inflation: (1 − η)L ≼ L̂ ≼ (1 + η)L, so energy radius √(1 + η) S | [A] perturbation section | Certificates from estimated graphs |
| A4 | The cost of loosening a certificate is governed by the resistance radius ρ_L | [A] information sensitivity | Explains why loose (energy) certificates barely help on KuaiRec |
| N1 | A misaligned fixed smoother gives linear regret (explicit counterexample) | [N] §4 | Motivates certification |
| S1 | **Innovation regression.** Under adaptive restless sampling, $`R_t=u_t^\top\mu+\epsilon_t`$ with predictable u_t and $`\epsilon_t\mid\mathcal H_t\sim N(0,1)`$ | [S] Thm "Predictable innovation experiments" | Foundation of B1 |
| S2 | **All-time confidence.** $`\lvert v^\top(\widehat\mu_T-\mu)\rvert\le\beta_T\lVert v\rVert_{J_T^{-1}}`$ for all T and all contrasts v, with J_T = H + I_T | [S] Thm "All-time confidence at a fixed mean" | B1 validity |
| S3 | **Full-field information.** $`\mathcal I_n=\mathcal I_p+(n-p)D_cQ_G^{-1}D_c`$; long-run covariance $`D_c^{-1}Q_GD_c^{-1}`$ | [S] Prop "General full-field information" | B3 |
| S4 | KL of adaptive experiments: $`\tfrac12\mathbb E[(\mu-\nu)^\top\mathcal I_T(\mu-\nu)]`$ | [S] information-limits section | B3 lower bounds |
| S5 | **Innovation lower bound** on dynamic regret: $`T\{\mathcal G(\mu,K_0)-\mathcal G(\mu,K_0-Q_G)\}`$ | [S], [P] | Fluctuation channel |
| S6 | Contrast information: an observation reduces the variance of a future difference by $`(C_j-C_k)^2/d`$; common shocks cancel | [S] README §5 | Why correlated shocks help comparisons |
| P1 | Exact two-period score; joint predictive sampling; sparse-monitoring lower bound (two arms) | [P], [S] §6 | Fluctuation-channel policies |

## New results

### B1. Certified pooling under correlated, persistent rewards

**Policy (SP-UCB-ST).** Run the innovation regression S1 with $`J_t=H+\mathcal I_t`$ and $`\widehat\mu_t=J_t^{-1}q_t`$. With β_t from S2, define:

```math
U_i=\widehat\mu_i+\beta_t\lVert e_i\rVert_{J_t^{-1}},\qquad
U_c=\min\Big\{\max_{i\in C_c}U_i,\ \min_{w\in\Delta(C_c)}\big(w^\top\widehat\mu+\beta_t\lVert w\rVert_{J_t^{-1}}\big)+\varepsilon_c\Big\}
```

Choose $`c_t\in\arg\max_cU_c`$ and pull $`\arg\max_{i\in C_{c_t}}U_i`$. With iid noise and H → 0, S1 reduces to sample means, and SP-UCB-ST becomes A1's SP-UCB up to its confidence constant.

**Theorem B1.** Suppose the certificates are valid and the dynamics, Q_G and r are correctly specified.

1. *(Validity.)* With probability at least 1 − δ, at every round, U_i ≥ μ_i for every arm and U_c ≥ v_c = max over C_c of μ_i for every component.
2. *(Regret.)* Suppose each pull of an arm in C_c raises $`1/\min_{w\in\Delta(C_c)}\lVert w\rVert^2_{J_t^{-1}}`$ by at least ι_c, and each pull of arm i raises $`1/\lVert e_i\rVert^2_{J_t^{-1}}`$ by at least ι_i. Then on the same event:

```math
N_c(T)\le1+\frac{4\beta_T^2}{\iota_c(\Gamma_c-\varepsilon_c)^2}\ (\varepsilon_c<\Gamma_c),\qquad
n_i(T)\le1+\frac{4\beta_T^2}{\iota_i\Delta_i^2}
```

   and $`\mathcal R_T\le\sum_{c\in\mathcal O}A^{\iota}_c+\sum_{c\notin\mathcal O}\min\{A^{\iota}_c,H^{\iota}_c\}`$. Here A^ι and H^ι are A1's quantities with 8σ²ℓ replaced by 4β_T²/ι.

3. *(Corollary: independent AR(1) arms, 0 ≤ φ < 1.)* ι_i ≥ (1 − φ)²/(V + r) and ι_c ≥ |C_c|(1 − φ)²/(V + r), where V = Var(z). So persistence costs at most a factor (1 − φ)⁻² against iid noise of the same marginal variance. B3 shows the sharp asymptotic factor is (1 + φ)/(1 − φ).

*Proof.*
1. **Validity.** S2 holds for all contrasts simultaneously, so it covers every e_i and every w in every simplex, at every round. For w in Δ(C_c), wᵀμ ≥ min over C_c of μ_i ≥ v_c − ε_c. Hence both terms of U_c bound v_c from above. The event does not depend on how w is chosen, so minimizing over w is free.
2. **Regret.** If c is selected at round t, then on the event μ* ≤ U_c ≤ wᵀμ + 2β_t‖w‖ + ε_c ≤ v_c + ε_c + 2β_t‖w‖ for the minimizing w. So $`\min_w\lVert w\rVert^2_{J_t^{-1}}\ge(\Gamma_c-\varepsilon_c)^2/(4\beta_t^2)`$. The information-growth condition says this minimum is at most 1/(ι_c (N_c − 1)) after N_c pulls. The arm bound is identical. Summation follows A1's proof, with the first-pull term unchanged.
3. **Corollary.** For independent arms, the observation information I_t is diagonal (S1 with block-diagonal dynamics). The coefficient of μ_i in a pull of arm i is $`1-\varphi^h s`$, where h ≥ 1 is the gap since the arm's last observation and s is the Kalman filter's estimate of z after seeing residuals all equal to 1. Each filter step is a convex combination of φ × (previous estimate) and the new residual, so 0 ≤ s ≤ 1, and the coefficient is at least 1 − φ. The predictive variance satisfies d ≤ V + r. Each pull therefore adds at least (1 − φ)²/(V + r) to $`(\mathcal I_t)_{ii}`$. For a component, take w proportional to the diagonal information; then $`w^\top J^{-1}w\le w^\top\mathrm{diag}(\mathcal I)^{-1}w=1/\sum_{i\in C_c}\mathcal I_{ii}`$. ∎

**Status.** Parts 1 and 2 are complete given S1, S2 and A1. Part 3 is complete for independent AR(1) arms.
- *Open:* a per-pull information bound with correlated shocks Q_G. The coefficient of μ_i then also involves other arms' means. Plan: state the component bound in terms of the realized information, which is always computable, and check it numerically.
- *Open:* the analogue for GDE-UCB (the A2 path rate) under persistence, using the same substitution of information for counts.

### B1′. A tight certificate for independent shocks

**Why B1 is too wide.** B1's confidence width carries the N-dimensional log-determinant, about $`\sqrt{N\log T}`$. With 20 arms and T = 20,000 that is about 12 standard errors, against about 5.5 for a per-arm bound. In the long-horizon elimination test (T = 20,000), B1 eliminated **no** arm in any run.

**Proposition B1′.** Assume Q_G is diagonal (shocks independent across arms) and the regularizer is H = αI. In S1, every observation's design vector u_t then has a single nonzero entry, so $`\mathcal I_t`$ is diagonal and each arm's score $`W_{i}=\sum_{t:a_t=i}u_t\epsilon_t`$ is a scalar martingale. Define for each arm i, and for each component c the pooled sums $`J_c=\alpha+\sum_{i\in C_c}\mathcal I_{ii}`$ and $`q_c=\sum_{i\in C_c}q_i`$:

```math
U_i=\frac{q_i}{J_{ii}}+\frac{\sqrt{2\log\big(\sqrt{J_{ii}/\alpha}\,/\delta'\big)}+\sqrt\alpha}{\sqrt{J_{ii}}},\qquad
U_c^{\rm pool}=\frac{q_c}{J_c}+\frac{\sqrt{2\log\big(\sqrt{J_c/\alpha}\,/\delta'\big)}+\sqrt\alpha}{\sqrt{J_c}}+\varepsilon_c,\qquad \delta'=\frac{\delta}{N+M}
```

With probability at least 1 − δ, at every round, U_i ≥ μ_i and $`U_c^{\rm pool}\ge v_c`$.

*Proof.*
1. **Arms.** Each arm's (q_i, J_ii) is the scalar case of S2, so the one-dimensional method of mixtures applies. The regularization bias is at most √α · |μ_i| ≤ √α.
2. **Components.** The pooled statistic estimates the information-weighted average of the pulled arms' means, which is at least v_c − ε_c. Its error is a scalar martingale with quadratic variation J_c − α.
3. **Union bound** over the N + M scalar processes. ∎

The scalar construction is valid for any adaptive, restless schedule. With correlated shocks the design vectors couple arms, and the per-contrast analogue is open.

**First check** (one seed, independent shocks):

| | iid SP-UCB | SP-UCB with B1′ |
| --- | --- | --- |
| φ = 0, one at a time | regret 274, valid | regret 221, valid |
| φ = 0.97, blocks of 25 | regret 1,424, violated in 99.8% of rounds | regret 763, never violated |

**Full sweep** (20 seeds, independent shocks, T = 5,000; `coverage_runs_scalar.csv`). Mean regret of SP-UCB with iid / B1 / B1′ certificates, and the share of runs where the iid certificate was violated:

| Exposure | φ | iid / B1 / B1′ regret | iid violated | B1, B1′ violated |
| --- | ---: | --- | ---: | ---: |
| One at a time | 0 | 353 / 753 / **295** | 0% | 0% |
| One at a time | 0.5 | 457 / 752 / **396** | 0% | 0% |
| One at a time | 0.9 | 533 / 759 / 564 | 0% | 0% |
| One at a time | 0.97 | 649 / 755 / 679 | 0% | 0% |
| Blocks of 25 | 0 | 380 / 766 / **338** | 0% | 0% |
| Blocks of 25 | 0.5 | 406 / 916 / 510 | 5% | 0% |
| Blocks of 25 | 0.9 | 629 / 1,023 / 818 | 75% | 0% |
| Blocks of 25 | 0.97 | 853 / 1,034 / **828** | 90% | 0% |

**Reading.**

- **B1′ is always valid.** It beats iid pooling when persistence is low or absent: 16% lower regret at φ = 0. It is within 6% of iid pooling at high persistence with one-at-a-time sampling. With bursty exposure it is 26–30% worse at φ = 0.5–0.9, where the iid certificate is invalid in up to 75% of runs, and 3% better at φ = 0.97.
- **B1′ removes most of B1's cost** (753 → 295 at φ = 0).
- **The single seed above (1,424 against 763) was not representative.** On average, invalid iid certificates cost little regret in this toy, because suboptimal components are the ones under-covered.
- **Elimination.** With valid certificates, B1 and B1′ alike, nothing is eliminated within 5,000 rounds at these gaps (0.1–0.4 against unit fluctuation variance). The only eliminations come from invalid iid certificates, and in bursty high-persistence runs they remove the best arm 65–75% of the time.

**What the paper can claim.** B1′ makes certified pooling valid under persistence at no material regret cost against uncertified iid pooling, and lower regret when persistence is low. Invalid iid certificates mainly threaten irrevocable decisions, not regret.

### B1″. Correlated shocks: iterated nuisance plug-in

With correlated shocks, each design vector u_t couples arms. Write G = J − αI for the realized information. For arm i:

```math
q_i-\sum_{j\ne i}G_{ij}m_j=G_{ii}\mu_i+\sum_{j\ne i}G_{ij}(\mu_j-m_j)+W_i
```

Here $`W_i=\sum_t u_{t,i}\epsilon_t`$ is a scalar martingale with quadratic variation G_ii.

**The interval map.** Take any intervals that contain the true means μ_j, with midpoints m_j and half-widths h_j. Then:

```math
\hat\mu_i\pm\rho_i,\qquad \hat\mu_i=\frac{q_i-\sum_{j\ne i}G_{ij}m_j}{J_{ii}},\qquad \rho_i=\frac{\sqrt{2J_{ii}\log(\sqrt{J_{ii}/\alpha}/\delta')}+\alpha+\sum_{j\ne i}\lvert G_{ij}\rvert h_j}{J_{ii}}
```

On the event that every scalar mixture bound holds, this map sends true-containing intervals to true-containing intervals. So iterating from [0, 1] is valid.

**Components.** Write μ_i = θ_c + d_i, with θ_c the component midrange and |d_i| ≤ ε_c/2. The same argument applies to θ with design Pᵀu_t, where P is the membership matrix. The deviation term $`\sum_i\lvert(P^\top G)_{ci}\rvert\,\varepsilon_{c(i)}/2`$ is deterministic given the data. This gives a valid pooled bound θ̂_c + ρ_c + ε_c/2 ≥ v_c. With independent shocks it reduces to SP-UCB's +ε_c structure.

*Implementation note.* Return the unclipped upper bounds. Clipping them at 1 creates ties that index-based argmax breaks toward a fixed arm. The sweep below also shuffles arm order.

**Sweep** (correlated shocks, shuffled arms, 20 seeds; `coverage_runs_plugin.csv`):
- B1″ is never violated.
- With one-at-a-time sampling it beats iid pooling up to φ = 0.9 (606 against 642 at φ = 0.9).
- With bursty exposure it is 9–21% worse at φ ≥ 0.5, where the iid certificate is invalid in 85–90% of runs.
- Successive elimination with iid certificates wrongly drops the best arm in 35–90% of bursty, high-persistence runs; with B1″, never.

### B2. iid certificates fail under persistence

**Proposition B2.** Take one arm sampled on n consecutive rounds, with stationary AR(1) persistence φ ∈ (0, 1), r = 0 and Var(z) = V. The sample mean has

```math
\mathrm{Var}(\bar Y_n)=\frac Vn\Big[\frac{1+\varphi}{1-\varphi}-\frac{2\varphi(1-\varphi^n)}{n(1-\varphi)^2}\Big]
```

The iid radius $`b(n)=\sqrt{2V\ell/n}`$ therefore has miscoverage probability

```math
\Pr\big(\lvert\bar Y_n-\mu\rvert>b(n)\big)\ \longrightarrow\ 2\Phi\Big(-\sqrt{2\ell\,\tfrac{1-\varphi}{1+\varphi}}\Big)\qquad(n\to\infty)
```

That limit tends to 1 as φ → 1 at a fixed confidence level ℓ, and it shrinks only like $`T^{-(1-\varphi)/(1+\varphi)}`$ when ℓ grows like log T. The union bound behind A1 assumes miscoverage of at most δ/(2(K + M)T) for each check, so iid certificates are invalid once φ > 0.

*Proof.* The variance is the standard AR(1) sum of autocovariances V φ^|s−u|, and $`\bar Y_n-\mu`$ is Gaussian. ∎

**Consequence (empirical, planned).** In the toy, SP-UCB with iid radii pooled over persistent rewards rejects the optimal component in a positive share of runs, giving linear mean regret, while SP-UCB-ST does not. A formal linear-regret instance is a two-component construction; a proof plan is to be added.

### B3. Long-run constants and the slate contrast gain

**Proposition B3.**
1. *(Long-run substitution.)* Suppose arms are observed in long consecutive runs, or as full fields, with common AR coefficients. By S3, the per-observation mean information converges to the inverse long-run covariance $`c^2Q_G^{-1}`$, where c = 1 − Σ_r a_r. A1, A2 and the information-design lower bound of [A], with the Gaussian KL from S4, then hold with σ² replaced by $`\sigma^2_{\rm LR}=q/c^2`$. For AR(1) that is V(1 + φ)/(1 − φ).
2. *(Slates: correlated shocks help contrasts.)* Suppose the learner observes a slate S_t of k arms in one round, as in the KuaiRec daily design. Each slate's whitened information is $`c^2 M_S Q_G^{-1} M_S^\top`$, restricted to the slate. For two arms in the same slate with innovation correlation ρ, the variance of their long-run contrast is $`2q(1-\rho)/c^2`$ per round. Positive graph correlation of shocks therefore makes comparisons, and so component rejections, cheaper by the factor (1 − ρ).

*Status.* Part 1 combines S3 and S4 with A's lower-bound program. For single-arm pulls at gaps, the exact information is schedule-dependent (S3 and [P]), and the long-run substitution is the consecutive-run limit. Part 2 is a direct Gaussian calculation; it needs writing up with the exact finite-slate formula.

## Empirical status (9 October 2026)

**Coverage test v1** (`experiments/st_toy/coverage.py`; 20 arms, 4 components, T = 5,000, 30 seeds, φ ∈ {0, 0.5, 0.9, 0.97}, independent or correlated shocks; results in `research/st_toy/results/coverage_runs.csv`):

| | iid-certified SP-UCB | SP-UCB-ST (B1) |
| --- | --- | --- |
| Runs with any certificate violation | 0 / 240 | 0 / 240 |
| Mean regret, independent shocks, φ = 0 → 0.97 | 352 → 660 | 742 → 765 |
| Mean regret, correlated shocks, φ = 0 → 0.97 | 370 → 756 | 739 → 789 |

**Reading.**

1. **B1 is valid, but its log-determinant confidence width is conservative.** At high persistence its regret approaches the iid policy's; at low persistence it is about 2× worse. The paper needs a tighter practical β, or comparisons at matched nominal coverage.
2. **B2's failure did not appear under one-at-a-time UCB sampling.** UCB interleaves arms, so repeat pulls are about 20 rounds apart. The correlation between them is φ²⁰ ≈ 0.54 at φ = 0.97, which inflates variance about 1.8×, not the 8× of consecutive pulls. With a conservative union-bound level, the iid certificate still covers. B2's mechanism therefore needs **bursty exposure**: commit blocks, daily slates, batched updates. Its practical form uses variances estimated from the arm's own autocorrelated samples.

**Coverage test v2** adds commit blocks b ∈ {1, 25} (20 seeds; results in `research/st_toy/results/coverage_runs_v2.csv`):

| Exposure | φ | Runs with a violation, iid SP-UCB | Rounds violated, iid SP-UCB | Runs with a violation, SP-UCB-ST (B1) | Mean regret, iid / B1 (independent shocks) |
| --- | ---: | ---: | ---: | ---: | --- |
| one at a time (b = 1) | 0.97 | 0% | 0% | 0% | 649 / 755 |
| blocks of 25 | 0.5 | 5% | 5% | 0% | 406 / 916 |
| blocks of 25 | 0.9 | 70–75% | 58–59% | 0% | 629 / 1,023 |
| blocks of 25 | 0.97 | 90–100% | 86–88% | 0% | 853 / 1,034 |

1. **B2 is confirmed as a coverage failure under bursty exposure.** It matches the mechanism: consecutive pulls inflate variance by (1 + φ)/(1 − φ). One-at-a-time sampling stays covered.
2. **B1 is always valid**: 0 violations in 1,600 runs.
3. **Invalid certificates did not raise mean regret in this toy.** The iid policy's violations mostly under-cover suboptimal arms, and B1's confidence width is wide. A regret argument for certification therefore rests on cases where the *optimal* component is under-covered: KuaiRec Setting A's heavy tails, and the misalignment counterexample.
4. *(The empirical-variance, log t variant violates even at φ = 0, because variance estimates from 2–3 samples are tiny. That is a small-sample artifact, not persistence, and is excluded from the B2 claim.)*

**Certified successive elimination** (an irrevocable decision; 20 seeds, T = 5,000; `coverage_runs_elim.csv`):

| Exposure | φ | Best arm eliminated, iid certificate | Best arm eliminated, B1 | Mean regret, iid / B1 |
| --- | ---: | ---: | ---: | --- |
| One at a time | 0 to 0.97 | 0% | 0% | 1,088–1,170 / 1,170 |
| Blocks of 25 | 0.9 | 40% (correlated), 65% (independent) | 0% | 984–1,060 / 1,170 |
| Blocks of 25 | 0.97 | 65% (correlated), 75% (independent) | 0% | 1,072–1,097 / 1,170 |

- **Decision correctness:** under bursty persistent exposure, iid certificates make the wrong irrevocable decision in 40–75% of runs, against a nominal 5%. B1 never does.
- **Cost:** B1 eliminated nothing within 5,000 rounds; its regret equals round-robin's (1,170). Valid but slow, so it needs longer horizons and reported stopping times.
- **Regret consequence of the wrong eliminations is small here,** because near-best arms (0.50 against 0.55) survive. A larger best-arm gap would make it linear.

**Implications for the paper.**
- Present certification as guaranteeing **correct decisions**: certified rejection, stopping and recommendation, where a false certificate means a wrong irrevocable action. The fixed-confidence corollary in [S] is the natural statement.
- Present regret as the cost of that guarantee, not as the headline benefit.
- Tighten B1's width before final runs, for example with per-contrast martingale bounds over the finite set of arm and component contrasts.
- Add an instance where the optimal component's certificate is the one that fails, to show the regret consequence.

## Experiments that test the theory

| Claim | Test | Where |
| --- | --- | --- |
| B1 validity and regret | Coverage of U_c and mean regret for SP-UCB-ST against iid SP-UCB, across φ ∈ {0, 0.5, 0.9, 0.97} | Toy (to build in `experiments/st_toy/`) |
| B2 failure | The same runs: miscoverage rate of iid certificates against φ, with the B2 formula overlaid | Toy |
| B3 slate gain | Compare k-slot designs with high-ρ and low-ρ graph correlation | KuaiRec daily |
| S5 innovation lower bound | Gap closed by fluctuation-channel policies | Toy (running), KuaiRec daily |
| A1, A4 on real graphs | Certified against uncertified pooling; energy-to-gap ratio about 5 | KuaiRec Setting A (done) |
