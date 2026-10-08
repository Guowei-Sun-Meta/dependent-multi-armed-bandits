# Graph Alignment and Cumulative Regret

A full working manuscript extending the similarity selection idea to cumulative-regret bandits. The draft includes a model, algorithm, proved finite-time bounds, an explicit information lower bound, experiments, and references. Its novelty and proofs still need independent review.

- [Read the manuscript PDF](manuscript.pdf).
- [Edit the LaTeX source](manuscript.tex).
- [Inspect aggregate results](results/summary.csv) or [run-level results](results/runs.csv).
- [Inspect the experiment metadata](results/metadata.json), including actual graphs and the certificates supplied to the policies.
- [Run the experiment code](../../experiments/alignment_regret.py).

The central distinction is between preserving the reward ranking and giving the learner reliable bounds on reward differences. Ranking preservation alone does not guarantee lower regret. With a valid graph-energy certificate, however, observations can rule out a whole group of similar suboptimal arms.

For a component with gap \(\Gamma_c\) from the optimum and certified reward diameter \(\varepsilon_c<\Gamma_c\), the proposed policy has component regret bounded, with high probability, by

\[
(\Gamma_c+\varepsilon_c)
\left(1+\frac{8\sigma^2\log(2(K+M)T/\delta)}{(\Gamma_c-\varepsilon_c)^2}\right).
\]

Its bound also takes the minimum with an ordinary arm-wise UCB bound. Tightening a valid diameter certificate improves this guarantee. The guarantee does not imply that realized regret must decrease on every run when the certificate changes.

The paper derives a more precise information comparison for a homogeneous suboptimal clique of size \(m\), edge weight \(w\), gap \(\Gamma\), and supplied energy budget \(S^2\). Define

\[
q=\frac{S}{\Gamma\sqrt{w(m-1)}}.
\]

The clique's contribution to the structured Gaussian information lower bound is

\[
\frac{2\sigma^2m}{\Gamma\{1+(m-1)(1-q)_+^2\}}.
\]

Relative to the classical unstructured information constant, the reduction factor is therefore \(1+(m-1)(1-q)_+^2\). At exact similarity it is \(m\); when enough mismatch is allowed to make a single arm optimal independently of its neighbors, it returns to one. This is an exact solution of a lower-bound optimization for that specific graph family, **not** a claim that the proposed policy attains the constant for all positive \(S\).

With exact equality within every component, classical optimal algorithms on component representatives attain the matching asymptotic constant. The bounded-reward minimax rate becomes \(\Theta(\sqrt{MT})\) for \(2\le M\le T\), where \(M\) is the number of components.

The experiment used 25 arms, four true components, Gaussian noise with \(\sigma=0.15\), 20,000 rounds, and 40 independent runs. Mean final regret was 100.02 for ordinary UCB, 28.65 for a configured regularized spectral baseline, and 12.22 for pooling with exact certificates. Looser certificates and incorrectly grouped arms removed some or all of the benefit. These are controlled synthetic results with supplied certificates; graph learning was not evaluated.

The literature includes close competitors: [Spectral bandits (JMLR 2020)](https://www.jmlr.org/papers/v21/16-529.html), [clustered Thompson sampling (IJCAI 2021)](https://www.ijcai.org/proceedings/2021/305), and [Clus-UCB (2025 preprint)](https://arxiv.org/abs/2508.02909). The manuscript explicitly acknowledges their overlap. A publication claim would require a stronger novelty assessment, approximate-alignment optimality analysis, and broader comparisons.

Reproduce the actual experiment from the project root:

```sh
python3 experiments/alignment_regret.py --verify
python3 experiments/alignment_regret.py --runs 40 --horizon 20000
cd research/alignment_paper
tectonic --only-cached --keep-logs manuscript.tex
```

The Python experiment uses only the standard library. PGFPlots renders figures directly from its CSV output. If TeX resources are not cached on another machine, omit `--only-cached` to let Tectonic obtain its support files.
