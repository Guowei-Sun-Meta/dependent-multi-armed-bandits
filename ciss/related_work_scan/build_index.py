"""Write ../related_work_abstracts.md from records.json (made by harvest_abstracts.py).

The selection and the relevance notes are ours; the abstracts are verbatim from
OpenAlex (IEEE Xplore records) or arXiv. Run from the scratch directory that
holds records.json:  python3 <repo>/ciss/related_work_scan/build_index.py <repo>/ciss
"""
import json
import sys
from pathlib import Path

# (DOI, theme, core, note). Themes: A structure between arms / graph signals,
# B temporal dependence and filtering, C confidence and estimation under
# misspecification, D bandits and sequential decisions at CISS.
SELECTED = [
    ("10.1109/ciss56502.2023.10089744", "A", True,
     "The only CISS graph-bandit paper in the window, but the graph constrains movement (which arm can follow which), not the means. Its regret depends on the diameter $`D`$; our path--clique separation shows that for a mean restriction diameters miss the information geometry. Cite to separate the two meanings of 'graph bandit'."),
    ("10.1109/ciss59072.2024.10480177", "A", True,
     "MAP denoising of graph signals under a frequency-domain smoothness prior: the static, offline counterpart of the penalty $`H=\\alpha I+\\lambda L_\\mu`$ in Theorem 3. It assumes the smoothness prior is right; our certificate question (is the graph valid for this decision?) is absent."),
    ("10.1109/ciss56502.2023.10089638", "A", False,
     "Generative versus discriminative design of graph filters when the graph model is partly known. Parallels our two graph roles: fitting the model that generates the signal versus learning the estimator directly."),
    ("10.1109/ciss64860.2025.10944757", "A", False,
     "Graph-filter estimation averaged over several candidate topologies. A possible route to robustness against graph misspecification, which our certificate handles by widths instead."),
    ("10.1109/ciss56502.2023.10089777", "A", False,
     "Learns task correlations from gradients and rewires the communication graph to isolate harmful tasks: a data-driven check on pooling, the multitask analogue of rejecting a component."),
    ("10.1109/ciss59072.2024.10480214", "B", True,
     "Wiener--Kallianpur innovation representation as the canonical object for probabilistic forecasting. Our Theorem 2 uses the same idea in a parametric, partially observed form: the Kalman innovations of an adaptively sampled field form a predictable Gaussian regression for the means. Cite as the CISS lineage of innovation-based inference."),
    ("10.1109/ciss64860.2025.10944680", "B", False,
     "Scalar Kalman filter with 1-bit quantized measurements. Relevant to the binary (click) observations of KuaiRec and OBD, where our Gaussian innovation model is a working approximation."),
    ("10.1109/ciss56502.2023.10089747", "B", False,
     "Detection over temporally correlated (Jakes/Markov) channels with limited feedback: a communications instance of persistent noise that inflates the effective variance, the mechanism of Proposition 2."),
    ("10.1109/ciss59072.2024.10480203", "B", False,
     "Mean-square bounds for constant-gain LMS with linearly dependent design vectors; the step size must respect fourth moments of the design. Our design vectors $`u_t`$ are also dependent and adaptive, but we bound the self-normalized error rather than the mean-square error."),
    ("10.1109/ciss53076.2022.9751165", "B", False,
     "Spatio-temporal cellular traffic prediction with handover-based neighbour features: an applied example of shocks propagating along a graph, the shock role of the graph."),
    ("10.1109/ciss53076.2022.9751190", "B", False,
     "Dynamic functional connectivity: time-varying cross-region covariance. Background for heterogeneous node--time covariance (Proposition 1), not for decisions."),
    ("10.1109/ciss64860.2025.10944723", "C", True,
     "Expected versus observed Fisher information for MLE confidence regions. Our $`J_T`$ is an observed (path-wise) information whose ellipsoid is valid at all times by a martingale argument rather than asymptotically; the paper gives the asymptotic comparison CISS reviewers will know."),
    ("10.1109/ciss64860.2025.10944690", "C", True,
     "Misspecified Cramér--Rao bound when compound-Gaussian data are analysed as Gaussian. Our fitted-dynamics and heavy-tail stresses are exactly this misspecification; cite when stating that fitted-model coverage is not covered by Theorem 3."),
    ("10.1109/ciss64860.2025.10944720", "C", True,
     "Misspecified Barankin-type bound for the non-asymptotic threshold region. Complements the previous entry: our certificates operate at small samples, where asymptotic misspecification bounds are uninformative."),
    ("10.1109/ciss64860.2025.10944700", "C", False,
     "Learning estimation-performance bounds from a generative model of the data. A possible way to calibrate widths from logs, the open problem of the paper."),
    ("10.1109/ciss53076.2022.9751186", "C", False,
     "Spatial multiple testing with local false discovery rates in sensor networks: spatial inference with error control, but for fixed (non-adaptive) samples."),
    ("10.1109/ciss64860.2025.10944748", "C", False,
     "Optimal sequential hypothesis testing and stopping under adversarial falsification; the sequential-testing side of CISS, with iid observations."),
    ("10.1109/ciss56502.2023.10089653", "D", True,
     "Particle Thompson sampling: fit particles survive and unfit decay, measured in KL. Represents the Thompson-sampling line at CISS; our baselines are Beta and Gaussian TS."),
    ("10.1109/ciss56502.2023.10089647", "D", False,
     "Regenerative particles fix PTS's particle collapse. Companion to the previous entry."),
    ("10.1109/ciss53076.2022.9751154", "D", True,
     "Kernelized neural UCB for protein design: structure between arms through a learned kernel, uncertified. A non-recommender example of pooling across similar arms."),
    ("10.1109/ciss53076.2022.9751189", "D", False,
     "Reward-biased MLE for adaptive control: optimism through biased estimation, an alternative to the confidence-bound optimism we use."),
    ("10.1109/ciss56502.2023.10089655", "D", False,
     "Information-directed actor-critic (occupancy information ratio). Related to the information value of exploring persistent shocks discussed in our Section V."),
    ("10.1109/ciss56502.2023.10089651", "D", False,
     "Sequential probing of a discrete memoryless channel with PAC rates: adaptive sampling with non-asymptotic guarantees, from the information-theory side."),
    ("10.1109/ciss53076.2022.9751174", "D", False,
     "Recommendation as an MDP solved by deep RL with attention; models dynamic user preferences without confidence statements."),
    ("10.1109/ciss64860.2025.10944666", "D", False,
     "Consensus policy evaluation over a time-varying network, average-reward setting with Markovian samples; dependence over time and a graph across agents."),
    ("10.1109/ciss53076.2022.9751158", "D", False,
     "Doubly pessimistic offline RL under safety constraints; pessimism as a safety rail, as our certificates are for irrevocable decisions."),
]

THEMES = {
    "A": "Graph structure and graph signals",
    "B": "Temporal dependence, innovations and filtering",
    "C": "Confidence and estimation under misspecification",
    "D": "Bandits and sequential decisions",
}
HEADER = """# Related Work: Indexed Abstracts from CISS, 2022–2025

22 October 2026. Compiled for the CISS 2027 practice submission ([ciss/README.md](README.md)). The scan covers every paper of the Conference on Information Sciences and Systems published in IEEE Xplore for the 2022–2025 meetings and keeps the papers that bear on the draft's three questions: structure between arms, dependence over time, and confidence under adaptive sampling.

## How the scan was done

- **Harvest.** Crossref lists 315 records in the four CISS volumes (52 for 2022, 107 for 2023, 61 for 2024, 95 for 2025, including front matter); OpenAlex lists the same counts. Abstracts were attached from OpenAlex by DOI (304 of 315). An arXiv search of comment fields naming CISS found 22 preprints of these papers and no further CISS 2022–2026 paper.
- **CISS 2026 is missing.** The 60th CISS (Princeton, March 2026) has no proceedings in Crossref, OpenAlex or arXiv comments as of today, and the conference sites (ciss.jhu.edu, ee-ciss.princeton.edu) refuse automated access. Add it by hand once IEEE Xplore lists it.
- **Coverage caveat.** Only papers submitted to the proceedings reach IEEE Xplore. Many CISS talks, especially in Princeton's invited sessions, have no paper, so the bandit and reinforcement-learning presence at CISS is larger than this index shows.
- **Screening.** Titles and abstracts were matched against a keyword list (bandit, regret, Thompson, confidence, sequential, Markov, Kalman, graph, Laplacian, correlated, non-stationary, recommendation and others), giving 192 hits, which were screened by hand to the 26 papers below. Full texts were not read: IEEE Xplore blocks automated downloads, and only one kept paper has an arXiv version.
- **Abstracts are verbatim** from OpenAlex (IEEE metadata) or arXiv; **relevance notes are ours**, keyed to the results of the CISS draft ([submission/main.tex](submission/main.tex)): Theorem 1 (alignment-sensitive regret), Theorems 2–4 (innovation design, all-time confidence, valid pooling), Propositions 1–2 (node–time covariance, inflation). Papers marked **core** are cited in the draft.
- Scripts to repeat the scan are in [related_work_scan/](related_work_scan/README.md).

## What the scan shows

1. **CISS has almost no work on pooling across arms.** The one graph-bandit paper (C01) uses the graph to constrain movement, not to relate means. The draft's certified-pooling question is new to this venue, so the introduction must define the mean role of a graph before using it.
2. **Graph signal processing is the CISS language for our mean restriction.** Smoothness priors, graph filters and topology-averaged estimators (C02–C04) are the offline analogues of the Laplacian penalty $`H=\\alpha I+\\lambda L_\\mu`$; framing Theorem 3 as graph-regularized estimation with an all-time guarantee will read naturally to this audience.
3. **Innovation representations and Kalman filtering are native here.** C06 builds forecasting on the Wiener–Kallianpur innovation sequence; C07–C08 study filtering and correlated fading. Theorem 2 (the innovation regression) should be presented as an innovations argument, the language CISS readers already use.
4. **Misspecification bounds are an active CISS thread.** Misspecified Cramér–Rao and Barankin bounds (C13, C14) and expected-versus-observed Fisher information (C12) are the right reference points for the draft's honest limitation: coverage with fitted dynamics is measured, not proved.
5. **Bandit papers at CISS are algorithmic and iid.** Particle Thompson sampling (C18, C19), neural UCB (C20) and reward-biased MLE (C21) assume independent rewards; none treats persistent or correlated feedback, which is the draft's opening.
"""

VOLUME = {2022: "CISS 2022 (56th, Princeton)", 2023: "CISS 2023 (57th, Johns Hopkins)",
          2024: "CISS 2024 (58th, Princeton)", 2025: "CISS 2025 (59th, Johns Hopkins)"}


def main(outdir):
    recs = {r["doi"]: r for r in json.load(open("records.json")) if r.get("doi")}
    rows, entries = [], []
    for k, (doi, theme, core, note) in enumerate(SELECTED, 1):
        r = recs[doi]
        pid = f"C{k:02d}"
        rows.append(f"| [{pid}](#{pid.lower()}) | {r['year']} | {r['title']} | {theme} | {'yes' if core else ''} |")
        links = [f"[IEEE Xplore](https://doi.org/{doi})"]
        if r.get("arxiv_id"):
            links.append(f"[arXiv PDF](https://arxiv.org/pdf/{r['arxiv_id']})")
        entries.append("\n".join([
            f"### {pid}",
            "",
            f"**{r['title']}**  ",
            f"{', '.join(r['authors'])}. {VOLUME[r['year']]}. {' · '.join(links)}  ",
            f"Theme {theme}: {THEMES[theme]}{'. **Core**' if core else ''}",
            "",
            "> " + (r.get("abstract") or "(no abstract available)").replace("$", "\\$"),
            "",
            f"**Relevance.** {note}",
            "",
        ]))
    body = HEADER +"\n## Index\n\n| ID | Year | Title | Theme | Core |\n| --- | ---: | --- | :---: | :---: |\n"
    body += "\n".join(rows) + "\n\n## Entries\n\n" + "\n".join(entries)
    Path(outdir, "related_work_abstracts.md").write_text(body)
    print("wrote", len(SELECTED), "entries")


if __name__ == "__main__":
    main(sys.argv[1])
