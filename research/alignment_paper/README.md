# Graph Alignment and Cumulative Regret

The revised paper is **Graph Alignment and Cumulative Regret: Resistance Geometry and Spectral Pooling**. It develops graph-specific information calculations, a finite-time policy, certified graph-error bounds, and reproducible experiments. The proofs and publication novelty still require independent review.

- [Read the manuscript PDF](manuscript.pdf).
- [Edit the main LaTeX source](manuscript.tex).
- [Inspect the information and geometry proofs](geometry_information.tex).
- [Inspect the algorithm and regret proofs](geometry_policy.tex).
- [Read the novelty assessment and revision update](novelty_audit.md).
- [Inspect the main experiment results](results/geometry/summary.csv) and [metadata](results/geometry/metadata.json).
- [Inspect the supplementary certificate experiments](results/summary.csv).

The main improvement is a result that component widths cannot express. A path with edge weights `(m-1)/2` and a clique with edge weights `1/m` both have resistance diameter two. Give both the same homogeneous rewards and the same positive energy radius equal to their gap from the best singleton. The clique permits every arm to become optimal independently; an average of the path's endpoints constrains every interior reward.

The paper establishes an information separation growing with `m`, and a concrete policy that realizes the path's improved dependence on arm count. This compares two graph-energy model classes and does not establish superiority over all spectral algorithms.

For a fixed observation design `p`, the useful graph quantity is

```math
\kappa_L(p)=\max_i\sqrt{(e_i-p)^\top L^\dagger(e_i-p)},\qquad
\rho_L=\min_{p\ge0,\,\mathbf1^\top p=1}\kappa_L(p).
```

The radius is the smallest enclosing ball in the resistance embedding. Its computation is equivalent to the established maximum graph variance problem, credited to prior work. We connect it to the first-order increase in information cost when a valid energy certificate is loosened:

```math
\frac{C_{L,S}}{2\sigma^2/\Gamma}
=1+2(S/\Gamma)\rho_L+O((S/\Gamma)^2D),
```

where `D` is resistance diameter and the component's true means are homogeneous. A general information design and a finite-strength spectral resolvent oracle describe the underlying lower-bound program. The expansion is not the achieved regret coefficient of the proposed policy.

The new algorithm, GDE-UCB, samples a fixed resistance design in doubling stages, eliminates components using valid bounds, and falls back to ordinary arm UCB. Its regret bound charges exploration and integer rounding. On the normalized path at `S=Γ`, a sufficient horizon permits rejection using only the two endpoints, with

```math
R_T\le1024\sigma^2\ell/\Gamma+4\Gamma+\delta T,
\quad \ell=\log(2(K+M)T/\delta).
```

The corresponding clique class has an information lower-bound coefficient `2σ²m/Γ`. These statements separate arm-count dependence; the constants do not match, and the algorithm is not proved information-optimal.

If an estimated Laplacian satisfies `(1-η)L ≼ L_hat ≼ (1+η)L` on the constant-free subspace, with `η<1`, inflating a valid reference energy radius to `sqrt(1+η) S` yields a valid estimated-graph certificate. Its bias radius is at most `S ρ_L sqrt((1+η)/(1-η))`. The paper also sandwiches the information constants. This requires a certified graph comparison, not a graph learned for free.

The main experiment uses component sizes 16, 64, and 256, an optimal singleton of mean 0.8, homogeneous suboptimal mean 0.6, fixed supplied `S=0.2`, Gaussian noise `σ=0.05`, horizon 20,000, and 40 independent replications. Comparators are ordinary UCB, diameter pooling, and an explicitly specified Gaussian width-profile analogue motivated by Clus-UCB. Small-instance overhead and poor clique performance are reported alongside the path benefit. A hidden-peak stress test demonstrates linear loss under an invalid zero-energy certificate. Graph learning is not evaluated.

The original SP-UCB analysis and experiments remain as supplementary material. Closest prior work includes spectral and clustered bandits, structured information lower bounds, GRUB's pure-exploration geometry, maximum graph variance, and misspecified kernel and linear bandits. The contribution boundary is narrower than a first study of graph correctness.

Reproduce from the project root:

```sh
python3 experiments/simulations/theory/graph_alignment/resistance_geometry.py --verify
python3 experiments/simulations/theory/graph_alignment/resistance_geometry.py --runs 40 --horizon 20000
python3 experiments/simulations/theory/graph_alignment/render_geometry_results.py
python3 experiments/simulations/theory/graph_alignment/alignment_regret.py --verify
python3 experiments/simulations/theory/graph_alignment/alignment_regret.py --runs 40 --horizon 20000
cd research/alignment_paper
tectonic --only-cached --keep-logs manuscript.tex
```

Both experiment scripts use only Python's standard library. Tables and experimental prose are rendered directly from saved CSVs. PGFPlots renders the analytical and empirical figures. If TeX resources are not cached elsewhere, omit `--only-cached` to obtain support files.

The [spatial and temporal extension](../spatiotemporal_bandits/README.md) connects deterministic graph certificates for fixed means with heterogeneous AR(p_i) dynamics and spatially correlated innovations. Its standalone paper derives joint lag-state likelihoods, adaptive mean confidence, comparison and prediction information, and an exact AR(2) schedule comparison. A fixed external Laplacian certificate transfers the mean-energy allowance while the innovation likelihood remains correct; arbitrary data-dependent graph learning and noise-model misspecification remain unresolved.
