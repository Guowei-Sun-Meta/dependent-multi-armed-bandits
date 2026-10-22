# Related Work: Indexed Abstracts from CISS, 2022–2025

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
2. **Graph signal processing is the CISS language for our mean restriction.** Smoothness priors, graph filters and topology-averaged estimators (C02–C04) are the offline analogues of the Laplacian penalty $`H=\alpha I+\lambda L_\mu`$; framing Theorem 3 as graph-regularized estimation with an all-time guarantee will read naturally to this audience.
3. **Innovation representations and Kalman filtering are native here.** C06 builds forecasting on the Wiener–Kallianpur innovation sequence; C07–C08 study filtering and correlated fading. Theorem 2 (the innovation regression) should be presented as an innovations argument, the language CISS readers already use.
4. **Misspecification bounds are an active CISS thread.** Misspecified Cramér–Rao and Barankin bounds (C13, C14) and expected-versus-observed Fisher information (C12) are the right reference points for the draft's honest limitation: coverage with fitted dynamics is measured, not proved.
5. **Bandit papers at CISS are algorithmic and iid.** Particle Thompson sampling (C18, C19), neural UCB (C20) and reward-biased MLE (C21) assume independent rewards; none treats persistent or correlated feedback, which is the draft's opening.

## Index

| ID | Year | Title | Theme | Core |
| --- | ---: | --- | :---: | :---: |
| [C01](#c01) | 2023 | Multi-armed Bandit Learning on a Graph | A | yes |
| [C02](#c02) | 2024 | Bayesian Spectral Graph Denoising with Smoothness Prior | A | yes |
| [C03](#c03) | 2023 | Generative Versus Discriminative Data-Driven Graph Filtering of Random Graph Signals | A |  |
| [C04](#c04) | 2025 | Bayesian Graph Signal Estimation in Nonlinear GSP Models with Multiple Topologies | A |  |
| [C05](#c05) | 2023 | Personalized Decentralized Multi-Task Learning Over Dynamic Communication Graphs | A |  |
| [C06](#c06) | 2024 | Generative Probabilistic Time Series Forecasting and Applications in Grid Operations | B | yes |
| [C07](#c07) | 2025 | One-Dimensional Kalman Filter with Measurement Noise Replaced by Quantization | B |  |
| [C08](#c08) | 2023 | Distributed Detection in EH-Powered Mobile WSNs: Adaptive Transmission over Temporally Correlated MIMO Channels with Limited Feedback | B |  |
| [C09](#c09) | 2024 | Error bounds of constant gain least-mean-squares algorithms | B |  |
| [C10](#c10) | 2022 | Multivariate Spatio-temporal Cellular Traffic Prediction with Handover Based Clustering | B |  |
| [C11](#c11) | 2022 | Data-driven spatio-temporal dynamic brain connectivity analysis using fALFF: Application to sensorimotor task data | B |  |
| [C12](#c12) | 2025 | Comparative Confidence Regions using Expected and Observed Fisher Information | C | yes |
| [C13](#c13) | 2025 | On the Misspecified Cramér-Rao Bound and Elliptically Symmetric Distributions | C | yes |
| [C14](#c14) | 2025 | Misspecified Barankin Type Bound | C | yes |
| [C15](#c15) | 2025 | Opportunities and challenges in learning to bound | C |  |
| [C16](#c16) | 2022 | Estimating Test Statistic Distributions for Multiple Hypothesis Testing in Sensor Networks | C |  |
| [C17](#c17) | 2025 | A Hypothesis Testing-based Cyber Deception Framework under Sequential Reconnaissance | C |  |
| [C18](#c18) | 2023 | Particle Thompson Sampling with Static Particles | D | yes |
| [C19](#c19) | 2023 | Improving Particle Thompson Sampling through Regenerative Particles | D |  |
| [C20](#c20) | 2022 | Neural Bandits for Protein Sequence Optimization | D | yes |
| [C21](#c21) | 2022 | The RBMLE method for Reinforcement Learning | D |  |
| [C22](#c22) | 2023 | Information-Directed Policy Search in Sparse-Reward Settings via the Occupancy Information Ratio | D |  |
| [C23](#c23) | 2023 | Near-optimal Sampling to Optimize Communication Over Discrete Memoryless Channels | D |  |
| [C24](#c24) | 2022 | Sequential Recommendation Using Deep Reinforcement Learning and Multi-Head Attention | D |  |
| [C25](#c25) | 2025 | Distributed Policy Evaluation with Local Updates over Time-Varying Communication Network | D |  |
| [C26](#c26) | 2022 | Doubly Pessimistic Algorithms for Strictly Safe Off-Policy Optimization | D |  |

## Entries

### C01

**Multi-armed Bandit Learning on a Graph**  
Tianpeng Zhang, Kasper Johansson, Na Li. CISS 2023 (57th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss56502.2023.10089744)  
Theme A: Graph structure and graph signals. **Core**

> The multi-armed bandit(MAB) problem is a simple yet powerful framework that has been extensively studied in the context of decision-making under uncertainty. In many real-world applications, such as robotic applications, selecting an arm corresponds to a physical action that constrains the choices of the next available arms (actions). Motivated by this, we study an extension of MAB called the graph bandit, where an agent travels over a graph to maximize the reward collected from different nodes. The graph defines the agent's freedom in selecting the next available nodes at each step. We assume the graph structure is fully available, but the reward distributions are unknown. Built upon an offline graph-based planning algorithm and the principle of optimism, we design a learning algorithm, G-UCB, that balances long-term exploration-exploitation using the principle of optimism. We show that our proposed algorithm achieves\${O}(\sqrt{\vert S\vert T\log(T)}+D\vert S\vert \log T)\$learning regret, where\$\vert S\vert\$is the number of nodes and\$D\$is the diameter of the graph, which matches the theoretical lower bound\$\Omega(\sqrt{\vert S\vert T})\$up to logarithmic factors. To our knowledge, this result is among the first tight regret bounds in non-episodic, un-discounted learning problems with known deterministic transitions. Numerical experiments confirm that our algorithm outperforms several benchmarks.

**Relevance.** The only CISS graph-bandit paper in the window, but the graph constrains movement (which arm can follow which), not the means. Its regret depends on the diameter $`D`$; our path--clique separation shows that for a mean restriction diameters miss the information geometry. Cite to separate the two meanings of 'graph bandit'.

### C02

**Bayesian Spectral Graph Denoising with Smoothness Prior**  
Sam Leone, Xingzhi Sun, Michael Perlmutter, Smita Krishnaswamy. CISS 2024 (58th, Princeton). [IEEE Xplore](https://doi.org/10.1109/ciss59072.2024.10480177)  
Theme A: Graph structure and graph signals. **Core**

> Here we consider the problem of denoising features associated to complex data, modeled as signals on a graph, via a smoothness prior. This is motivated in part by settings such as single-cell RNA where the data is very high-dimensional, but its structure can be captured via an affinity graph. This allows us to utilize ideas from graph signal processing. In particular, we present algorithms for the cases where the signal is perturbed by Gaussian noise, dropout, and uniformly distributed noise. The signals are assumed to follow a prior distribution defined in the frequency domain which favors signals which are smooth across the edges of the graph. By pairing this prior distribution with our three models of noise generation, we propose Maximum A Posteriori (M.A.P.) estimates of the true signal in the presence of noisy data and provide algorithms for computing the M.A.P. Finally, we demonstrate the algorithms’ ability to effectively restore signals from white noise on image data and from severe dropout in single-cell RNA sequence data.

**Relevance.** MAP denoising of graph signals under a frequency-domain smoothness prior: the static, offline counterpart of the penalty $`H=\alpha I+\lambda L_\mu`$ in Theorem 3. It assumes the smoothness prior is right; our certificate question (is the graph valid for this decision?) is absent.

### C03

**Generative Versus Discriminative Data-Driven Graph Filtering of Random Graph Signals**  
Lital Dabush, Nir Shlezinger, Tirza Routtenberg. CISS 2023 (57th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss56502.2023.10089638)  
Theme A: Graph structure and graph signals

> In this paper we consider the problem of recovering random graph signals by using graph signal processing (GSP) tools. We focus on partially-known linear settings, where one has access to data in order to cope with the missing domain knowledge in designing a graph filter for signal recovery. In this work, we formulate two main approaches for leveraging both the available domain knowledge and data for such graph filter design: 1) the GSP-generative approach, where data is used to fit the underlying linear model that determines the graph filter; and 2) the GSP-discriminative approach, where data is used to directly learn the graph filter for graph signal recovery, bypassing the need to estimate the underlying model. Then, we compare qualitatively and quantitatively these two approaches of graph filter design. Our results provide an understanding with regard to which approach is preferable in which regime. In particular, it is shown that GSP-discriminative learning reliably copes with mismatches in the available domain knowledge, since it bypasses the need to fit the underlying model. On the other hand, the model awareness of the GSP-generative approach results in its achieving a lower mean-squared error (MSE) when data is scarce. In the asymptotic region where the number of training data points approaches infinity, both approaches achieve the oracle minimum MSE estimator under the considered setting.

**Relevance.** Generative versus discriminative design of graph filters when the graph model is partly known. Parallels our two graph roles: fitting the model that generates the signal versus learning the estimator directly.

### C04

**Bayesian Graph Signal Estimation in Nonlinear GSP Models with Multiple Topologies**  
Eyal Zeltzer, Tirza Routtenberg. CISS 2025 (59th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss64860.2025.10944757)  
Theme A: Graph structure and graph signals

> Dynamic systems with evolving graph topologies arise in applications such as power grids and sensor networks. Conventional graph signal estimation methods often assume fixed topologies, limiting their applicability in dynamic environments. In this paper, we address the problem of Bayesian graph signal estimation in nonlinear models with varying networks by leveraging graph filters from graph signal processing (GSP) theory. We use the criterion of averaged mean-squared error (AMSE) across topologies, and develop the GSP-minimum linear AMSE (GSP-MLAMSE) estimator, which minimizes the AMSE among graph-filter-based estimators. We demonstrate that the GSP-MLAMSE estimator extends the GSP linear minimum mean-squared-error (GSP-LMMSE) estimator [1] to the case of multiple topologies. In addition, we prove that it achieves the minimum linear AMSE estimator for orthogonal graph frequencies. We also develop its parametric version via the Chebyshev graph filter, which ensures numerical stability and scalability while maintaining robustness to topology variations. Simulations of power system state estimation demonstrate significant improvements in the AMSE and robustness across varying signal-to-noise ratios (SNRs) compared to existing methods.

**Relevance.** Graph-filter estimation averaged over several candidate topologies. A possible route to robustness against graph misspecification, which our certificate handles by widths instead.

### C05

**Personalized Decentralized Multi-Task Learning Over Dynamic Communication Graphs**  
Matin Mortaheb, Sennur Ulukus. CISS 2023 (57th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss56502.2023.10089777)  
Theme A: Graph structure and graph signals

> Decentralized and federated learning algorithms face data heterogeneity as one of the biggest challenges, especially when users want to learn a specific task. Even when personalized headers are used concatenated to a shared network (PF-MTL), aggregating all the networks with a decentralized algorithm can result in performance degradation as a result of heterogeneity in the data. Our algorithm uses exchanged gradients to calculate the correlations among tasks automatically, and dynamically adjusts the communication graph to connect mutually beneficial tasks and isolate those that may negatively impact each other. This algorithm improves the learning performance and leads to faster convergence compared to the case where all clients are connected to each other regardless of their correlations. We conduct experiments on a synthetic Gaussian dataset and a large-scale celebrity attributes (CelebA) dataset. The experiment with the synthetic data illustrates that our proposed method is capable of detecting tasks that are positively and negatively correlated. Moreover, the results of the experiments with CelebA demonstrate that the proposed method may produce significantly faster training results than fully-connected networks.

**Relevance.** Learns task correlations from gradients and rewires the communication graph to isolate harmful tasks: a data-driven check on pooling, the multitask analogue of rejecting a component.

### C06

**Generative Probabilistic Time Series Forecasting and Applications in Grid Operations**  
Xinyi Wang, Lang Tong, Qing Zhao. CISS 2024 (58th, Princeton). [IEEE Xplore](https://doi.org/10.1109/ciss59072.2024.10480214) · [arXiv PDF](https://arxiv.org/pdf/2402.13870v1)  
Theme B: Temporal dependence, innovations and filtering. **Core**

> Generative probabilistic forecasting produces future time series samples according to the conditional probability distribution given past time series observations. Such techniques are essential in risk-based decision-making and planning under uncertainty with broad applications in grid operations, including electricity price forecasting, risk-based economic dispatch, and stochastic optimizations. Inspired by Wiener and Kallianpur's innovation representation, we propose a weak innovation autoencoder architecture and a learning algorithm to extract independent and identically distributed innovation sequences from nonparametric stationary time series. We show that the weak innovation sequence is Bayesian sufficient, which makes the proposed weak innovation autoencoder a canonical architecture for generative probabilistic forecasting. The proposed technique is applied to forecasting highly volatile real-time electricity prices, demonstrating superior performance across multiple forecasting measures over leading probabilistic and point forecasting techniques.

**Relevance.** Wiener--Kallianpur innovation representation as the canonical object for probabilistic forecasting. Our Theorem 2 uses the same idea in a parametric, partially observed form: the Kalman innovations of an adaptively sampled field form a predictable Gaussian regression for the means. Cite as the CISS lineage of innovation-based inference.

### C07

**One-Dimensional Kalman Filter with Measurement Noise Replaced by Quantization**  
Pedro Aquino de Alcantara, Flavio Bezerra Costa, Daniel R. Fuhrmann. CISS 2025 (59th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss64860.2025.10944680)  
Theme B: Temporal dependence, innovations and filtering

> Several communication systems applications rely on state estimators for dynamic monitoring and control. Kalman Filters have been widely used for state estimation of stochastic processes. Low communication bandwidth adds more complexity to state estimator models, as state quantization should be considered. This paper studies a one-dimensional Kalman Filter with a 1-bit quantization process replacing noisy measurements. 2-bin and 3-bin 1-bit quantizers are considered. State distributions are calculated using discrete convolutions on a fine grid, and with Gaussian approximations. For the 3-bin 1-bit quantizer, two variations of the Gaussian approximation are developed. MATLAB simulations for the five resulting methods indicate that discrete convolutions are not worth the high computational cost, and that the 3-bin 1-bit quantizer eliminates the granular noise of the conventional 2-bin 1-bit quantizer.

**Relevance.** Scalar Kalman filter with 1-bit quantized measurements. Relevant to the binary (click) observations of KuaiRec and OBD, where our Gaussian innovation model is a working approximation.

### C08

**Distributed Detection in EH-Powered Mobile WSNs: Adaptive Transmission over Temporally Correlated MIMO Channels with Limited Feedback**  
Ghazaleh Ardeshiri, Azadeh Vosoughi. CISS 2023 (57th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss56502.2023.10089747)  
Theme B: Temporal dependence, innovations and filtering

> We address distributed detection problem in a mobile wireless sensor network, where each deployed sensor stores randomly arriving energy units in a finite-size battery. Sensors transmit their symbols simultaneously to a mobile fusion center (FC) with\$M > 1\$antennas, over temporally correlated fading channels. To characterize the time variation of the fading channel, we adopt a Markovian model and assume that the fading channel time-correlation is defined by the Jakes-Clark's correlation function. We consider limited feedback of channel gain, defined as the Frobenius norm of MIMO channel matrix, at a fixed feedback frequency from the FC to sensors. Modeling the randomly arriving energy units during a time slot as a Poisson process, and the quantized channel gain and the battery dynamics as homogeneous finite-state Markov chains, we propose an adaptive transmission scheme such that the\$J\$-divergence based detection metric is maximized at the FC, subject to an average per-sensor transmit power constraint. The proposed scheme is parameterized in terms of the scale factors (our optimization variables) corresponding to the channel gain quantization intervals. This scheme allows each sensor to adapt its transmit power in each time slot, based on its current battery state and the latest available channel gain feedback.

**Relevance.** Detection over temporally correlated (Jakes/Markov) channels with limited feedback: a communications instance of persistent noise that inflates the effective variance, the mechanism of Proposition 2.

### C09

**Error bounds of constant gain least-mean-squares algorithms**  
Chang Liu, Antwan D. Clark. CISS 2024 (58th, Princeton). [IEEE Xplore](https://doi.org/10.1109/ciss59072.2024.10480203)  
Theme B: Temporal dependence, innovations and filtering

> Constant gain least-mean-squares (LMS) algorithms have a wide range of applications in trajectory tracking problems, but the formal convergence of LMS in mean square is not yet fully established. This work provides an upper bound on the constant gain that guarantees a bounded mean-squared error of LMS for a general design vector. These results highlight the role of the fourth-order moment of the design vector. Numerical examples demonstrate the applicability of this upper bound in setting a constant gain in LMS, while existing criteria may fail. We also provide the associated error bound, which can be applied to design vectors with linearly dependent elements.

**Relevance.** Mean-square bounds for constant-gain LMS with linearly dependent design vectors; the step size must respect fourth moments of the design. Our design vectors $`u_t`$ are also dependent and adaptive, but we bound the self-normalized error rather than the mean-square error.

### C10

**Multivariate Spatio-temporal Cellular Traffic Prediction with Handover Based Clustering**  
Evren Tuna, Alkan Soysal. CISS 2022 (56th, Princeton). [IEEE Xplore](https://doi.org/10.1109/ciss53076.2022.9751165)  
Theme B: Temporal dependence, innovations and filtering

> We consider an RNN-based traffic volume prediction, which is a critical problem for network slice management and resource allocation in slicing-enabled next generation cellular networks. We propose to use a novel cost function that takes SLA violations into account. Our approach is multivariate and spatio-temporal in three aspects. First, we consider the effects of several other RAN features in a cell besides the traffic volume. Second, we introduce feature vectors based on peak hours of the day and days of the week. Third, we introduce feature vectors based on incoming handover statistics from the neighboring cells. Our results show about 60% improvement over MAE-based univariate LSTM models and about 20% improvement over SLA-based univariate models.

**Relevance.** Spatio-temporal cellular traffic prediction with handover-based neighbour features: an applied example of shocks propagating along a graph, the shock role of the graph.

### C11

**Data-driven spatio-temporal dynamic brain connectivity analysis using fALFF: Application to sensorimotor task data**  
Khondoker Murad Hossain, Suchita Bhinge, Qunfang Long, Vince D. Calhoun, Tulay Adali. CISS 2022 (56th, Princeton). [IEEE Xplore](https://doi.org/10.1109/ciss53076.2022.9751190)  
Theme B: Temporal dependence, innovations and filtering

> Dynamic functional connectivity (dFC) analysis enables us to capture the time-varying interactions between brain regions and can lead to powerful biomarkers. Most dFC studies are focused on the study of temporal dynamics and require significant post-processing to summarize the results of the dynamics analysis. In this paper, we introduce an effective framework that makes use of independent vector analysis (IVA) with fractional amplitude of low frequency fluctuation (fALFF) features extracted from task functional magnetic resonance imaging (fMRI) data. Our approach, which is based on IVA with fALLF features as input, (IVA-fALLF) produces an effective summary of the dynamics also greatly facilitating the study of both spatial and temporal dynamics in a more concise manner. IVA-fALLF captures the spatial and temporal dynamics of sensorimotor task data and identifies a component with significant difference in dynamic behavior between healthy controls (HC) and patients with schizophrenia (SZ). Finally, our post analysis using behavioral scores finds significant correlation between brain imaging data and the associated behavioral scores, increasing confidence on our results. Our results are consistent with the previous data-driven dFC analysis as we find similar brain networks showing abnormal behavior in patients with SZ. Moreover, our analysis identifies component behavior in task and rest windows separately and provides additional confirmation of results through correlation with behavioral scores.

**Relevance.** Dynamic functional connectivity: time-varying cross-region covariance. Background for heterogeneous node--time covariance (Proposition 1), not for decisions.

### C12

**Comparative Confidence Regions using Expected and Observed Fisher Information**  
Geng Zhang, James C. Spall. CISS 2025 (59th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss64860.2025.10944723)  
Theme C: Confidence and estimation under misspecification. **Core**

> Maximum likelihood estimation (MLE) is a fundamental method for statistical prediction, with confidence regions playing a critical role in assessing the accuracy of these estimates. Established theory shows that the standardized MLE is asymptotically normally distributed, with its covariance matrix approximated by either the inverse of the observed Fisher information matrix (FIM) or the inverse of the expected FIM. This paper demonstrates that the expected FIM provides a more accurate approximation for the MLE confidence region under typical conditions. Specifically, in asymptotic settings, the eigenvalues and eigenvectors of the expected FIM evaluated at the MLE exhibit lower mean squared error relative to the true covariance matrix compared to those derived from the observed FIM. These conclusions are supported by theoretical analysis and numerical experiments across multiple scenarios.

**Relevance.** Expected versus observed Fisher information for MLE confidence regions. Our $`J_T`$ is an observed (path-wise) information whose ellipsoid is valid at all times by a martingale argument rather than asymptotically; the paper gives the asymptotic comparison CISS reviewers will know.

### C13

**On the Misspecified Cramér-Rao Bound and Elliptically Symmetric Distributions**  
Christ D. Richmond. CISS 2025 (59th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss64860.2025.10944690)  
Theme C: Confidence and estimation under misspecification. **Core**

> Parameter estimation is among the many goals of engineering systems and scientific applications, and parameter bounds have provided significant insights into achievable system performance. These bounds are based on an assumed distribution for the data that may differ from the true data distribution, i.e. often the impacts of model misspecification are inevitable. Thus, researchers have derived Slepian-Bangs-type formulas for elliptically symmetric distributions under model misspecification to explore these effects. The present work continues this exploration by establishing a simple version of the Slepian formula applicable to circular complex compound Gaussian distributed data (a special class of non-Gaussian distributions, also sometimes called Gaussian mixtures), when the data distribution assumed for algorithm development is complex Gaussian.

**Relevance.** Misspecified Cramér--Rao bound when compound-Gaussian data are analysed as Gaussian. Our fitted-dynamics and heavy-tail stresses are exactly this misspecification; cite when stating that fitted-model coverage is not covered by Theorem 3.

### C14

**Misspecified Barankin Type Bound**  
Nadav E. Rosenthal, Joseph Tabrikian. CISS 2025 (59th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss64860.2025.10944720)  
Theme C: Confidence and estimation under misspecification. **Core**

> In statistical signal processing and estimation theory, discrepancies between the true data-generating model and the assumed model can lead to large estimation errors. The misspecified Cramér-Rao bound (MCRB) quantifies the impact of model mismatch on the mean-squared error (MSE), but it is derived for the asymptotic region, where the estimation errors are small. Consequently, it cannot be used to investigate estimation performance in the non-asymptotic region, where estimation errors are large. For instance, the MCRB is not effective in predicting the threshold phenomenon, which is crucial in many signal processing applications. The Barankin bound offers a tighter bound in the non-asymptotic region, and several works have demonstrated its applicability in predicting the threshold phenomenon. However, it is derived for perfectly specified models, where the true data-generating model matches the assumed model. In this work, a misspecified Barankin-type bound that accounts for model mismatch, enabling investigation of the impact of misspecification on the threshold phenomenon, is derived. The Barankin bound and the MCRB emerge as special cases of this lower bound. To illustrate its utility and investigate threshold signal-to-noise ratio phenomenon, we apply the proposed bound to the problem of direction-of-arrival estimation using a sensor array under model misspecification. The modeling errors induce large errors and distort the ambiguity function, a behavior effectively captured by the proposed bound.

**Relevance.** Misspecified Barankin-type bound for the non-asymptotic threshold region. Complements the previous entry: our certificates operate at small samples, where asymptotic misspecification bounds are uninformative.

### C15

**Opportunities and challenges in learning to bound**  
Hai Victor Habi, Hagit Messer, Yoram Bresler. CISS 2025 (59th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss64860.2025.10944700)  
Theme C: Confidence and estimation under misspecification

> Parameter estimation performance bounds serve as valuable tools in statistical signal processing, yet deriving them traditionally requires full knowledge of the data distribution. Recently, a framework has been proposed that combines a generative model with estimation performance bounds, thus eliminating the need for full knowledge of the data distribution by learning it from data. We refer to this approach as learning-to-bound (L2B). In this paper, we offer a comprehensive review of recent developments and emphasize their advantages. We then dive into open challenges and future directions within the L2B framework. Lastly, we explore a different perspective – the application of estimation performance bounds to deep learning.

**Relevance.** Learning estimation-performance bounds from a generative model of the data. A possible way to calibrate widths from logs, the open problem of the paper.

### C16

**Estimating Test Statistic Distributions for Multiple Hypothesis Testing in Sensor Networks**  
Martin Golz, Abdelhak M. Zoubir, Visa Koivunen. CISS 2022 (56th, Princeton). [IEEE Xplore](https://doi.org/10.1109/ciss53076.2022.9751186)  
Theme C: Confidence and estimation under misspecification

> We recently proposed a novel approach to perform spatial inference using large-scale sensor networks and multiple hypothesis testing [1]. It identifies the regions in which a spatial phenomenon of interest exhibits different behavior from its nominal statistical model. To reduce the intra-sensor-network communication overhead, the raw data is pre-processed at the sensors locally and a summary statistic is send to the cloud or fusion center where the actual spatial inference using multiple hypothesis testing and false discovery control takes place. Local false discovery rates (lfdrs) are estimated to express local believes in the state of the spatial signal. In this work, we extend our approach by proposing two novel lfdr estimators stemming from the Expectation-Maximization method. The estimation bias is considered to explain the differences in performance among the compared lfdr estimators.

**Relevance.** Spatial multiple testing with local false discovery rates in sensor networks: spatial inference with error control, but for fixed (non-adaptive) samples.

### C17

**A Hypothesis Testing-based Cyber Deception Framework under Sequential Reconnaissance**  
Abhinav Kumar, Swastik Brahma, Charles A. Kamhoua. CISS 2025 (59th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss64860.2025.10944748)  
Theme C: Confidence and estimation under misspecification

> In this paper, we present a novel sequential hypothesis testing framework to model an attacker’s process of gathering and processing information sequentially during the reconnaissance phase. The attacker’s optimal sequential decision rule, that enables it to promptly terminate its sequential reconnaissance process when its gathered information yields a desired decision-making quality, has been characterized. Further, employing the developed framework, we characterize optimal strategies that a defender can employ to feed the attacker with falsified information such that the expected time taken by the attacker for its malicious decision-making is maximally prolonged. Criterion that such falsification strategies must satisfy to blind the attacker and make it take indefinitely long to decide has been presented. Numerical results have been presented to provide important insights into the developed strategies.

**Relevance.** Optimal sequential hypothesis testing and stopping under adversarial falsification; the sequential-testing side of CISS, with iid observations.

### C18

**Particle Thompson Sampling with Static Particles**  
Zeyu Zhou, Bruce Hajek. CISS 2023 (57th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss56502.2023.10089653)  
Theme D: Bandits and sequential decisions. **Core**

> Particle Thompson sampling (PTS) is a simple and flexible approximation of Thompson sampling for solving stochastic bandit problems. PTS circumvents the intractability of maintaining a continuous posterior distribution in Thompson sampling by replacing the continuous distribution with a discrete distribution supported at a set of weighted static particles. We analyze the dynamics of particles' weights in PTS for general stochastic bandits without assuming that the set of particles contains the unknown system parameter. It is shown that fit particles survive and unfit particles decay, with the fitness measured in KL-divergence. For Bernoulli bandit problems, all but a few fit particles decay.

**Relevance.** Particle Thompson sampling: fit particles survive and unfit decay, measured in KL. Represents the Thompson-sampling line at CISS; our baselines are Beta and Gaussian TS.

### C19

**Improving Particle Thompson Sampling through Regenerative Particles**  
Zeyu Zhou, Bruce Hajek. CISS 2023 (57th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss56502.2023.10089647)  
Theme D: Bandits and sequential decisions

> This paper proposes regenerative particle Thompson sampling (RPTS) as an improvement of particle Thompson sampling (PTS) for solving general stochastic bandit problems. PTS approximates Thompson sampling by replacing the continuous posterior distribution with a discrete distribution supported at a set of weighted static particles. PTS is flexible but may suffer from poor performance due to the tendency of the probability mass to concentrate on a small number of particles. RPTS exploits the particle weight dynamics of PTS and uses non-static particles: it deletes a particle if its probability mass gets sufficiently small and regenerates new particles in the vicinity of the surviving particles. Empirical evidence shows uniform improvement across a set of representative bandit problems without increasing the number of particles.

**Relevance.** Regenerative particles fix PTS's particle collapse. Companion to the previous entry.

### C20

**Neural Bandits for Protein Sequence Optimization**  
Chenyu Wang, Joseph Kim, Le Cong, Mengdi Wang. CISS 2022 (56th, Princeton). [IEEE Xplore](https://doi.org/10.1109/ciss53076.2022.9751154)  
Theme D: Bandits and sequential decisions. **Core**

> Protein design involves searching over a large combinatorial sequence space. Evaluating the fitness of new protein sequences often requires wet-lab experiments that are costly and time consuming. In this paper we propose a neural bandits algorithm that utilizes a modified upper-confidence bound algorithm for accelerating the search for optimal designs. The algorithm makes adaptive queries as guided by the kernelized neural bandits. The algorithm is tested on two public protein fitness datasets, the GB1 and WW domain. For both datasets, our algorithm consistently identifies top-fitness protein sequences. Notably, this approach finds a diverse and rich class of high fitness proteins using substantially fewer design queries compared to a range of alternative methods.

**Relevance.** Kernelized neural UCB for protein design: structure between arms through a learned kernel, uncertified. A non-recommender example of pooling across similar arms.

### C21

**The RBMLE method for Reinforcement Learning**  
Akshay Mete, Rahul Singh, P. R. Kumar. CISS 2022 (56th, Princeton). [IEEE Xplore](https://doi.org/10.1109/ciss53076.2022.9751189)  
Theme D: Bandits and sequential decisions

> The Reward Biased Maximum Likelihood Estimate (RBMLE) method was proposed about four decades ago for the adaptive control of unknown Markov Decision Processes, and later studied for more general Controlled Markovian Systems and Linear Quadratic Gaussian systems. It showed that if one could bias the Maximum Likelihood Estimate in favor of parameters with larger rewards then one could obtain long-term average optimality. It provided a reason for preferring parameters with larger rewards based on the fact that generally one can only identify the behavior of a system under closed-loop, and therefore any limiting parameter estimate has to necessarily have lower reward than the true parameter. It thereby provided a reason for what his now called “optimism in the face of uncertainty”. It similarly preceded the definition of “regret”, and it is only in the last three years that it has been analyzed for its regret performance, both analytically, and in comparative simulation testing. This paper provides an account of the RBMLE method for reinforcement learning.

**Relevance.** Reward-biased MLE for adaptive control: optimism through biased estimation, an alternative to the confidence-bound optimism we use.

### C22

**Information-Directed Policy Search in Sparse-Reward Settings via the Occupancy Information Ratio**  
Wesley A. Suttle, Alec Koppel, Ji Liu. CISS 2023 (57th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss56502.2023.10089655)  
Theme D: Bandits and sequential decisions

> This paper examines a new measure of the exploration/exploitation trade-off in reinforcement learning (RL) called the occupancy information ratio (OIR). To this end, the paper derives the Information-Directed Actor-Critic (IDAC) algorithm for solving the OIR problem, provides an overview of the rich theory underlying IDAC and related OIR policy gradient methods, and experimentally investigates the advantages of such methods. The central contribution of this paper is to provide empirical evidence that, due to the form of the OIR objective, IDAC enjoys superior performance over vanilla RL methods in sparse-reward environments.

**Relevance.** Information-directed actor-critic (occupancy information ratio). Related to the information value of exploring persistent shocks discussed in our Section V.

### C23

**Near-optimal Sampling to Optimize Communication Over Discrete Memoryless Channels**  
Michael A. Tope, Joel M. Morris. CISS 2023 (57th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss56502.2023.10089651)  
Theme D: Bandits and sequential decisions

> This paper develops a strategy to minimize the number of channel probes required to recover the components of the channel law and maximize the reliable communication rate across a discrete memoryless channel (DMC). Based on the aggregate set of observed input-output pairs over time, the algorithm sequentially probes subsets of channel input values. We leverage a non-asymptotic probably approximately correct (PAC) bounds to establish the rate of convergence towards channel capacity as\$O(\sqrt{\log(\log(N))\log(N)/N)}s\$, where\$N\$is the number of channel probes. For a discrete channel with\$\vert \mathcal{X}\vert\$input values and\$\vert \mathcal{Y}\vert\$output values, the sampling strategy may reduce the sample complexity by a factor of nearly\$\min(\vert \mathcal{X}\vert /\vert \mathcal{Y}\vert, 1)\$relative to previous methods.

**Relevance.** Sequential probing of a discrete memoryless channel with PAC rates: adaptive sampling with non-asymptotic guarantees, from the information-theory side.

### C24

**Sequential Recommendation Using Deep Reinforcement Learning and Multi-Head Attention**  
Raneem Sultan, Mervat Abu-Elkheir. CISS 2022 (56th, Princeton). [IEEE Xplore](https://doi.org/10.1109/ciss53076.2022.9751174)  
Theme D: Bandits and sequential decisions

> Recommender Systems have become a crucial part of many of our online interactions. From shopping for clothes, planning a trip, or deciding what to watch, recommender systems are aiming to help users navigate the overwhelming amount of options available online. The problem with most of the existing recommender systems is that they treat the recommendation process as a static one and make recommendations according to a fixed greedy strategy. This is a problem because user preferences are dynamic. In this paper, we aim to address this problem by modeling the recommendation problem as a Markov Decision Process (MDP) and solving it using deep reinforcement learning. Furthermore, we use multi-head attention to improve the recommendations. We conduct extensive experiments using the MovieLens real-world dataset and achieve an improvement of 6% over the state-of-the-art approach results in terms of precision@20.

**Relevance.** Recommendation as an MDP solved by deep RL with attention; models dynamic user preferences without confidence statements.

### C25

**Distributed Policy Evaluation with Local Updates over Time-Varying Communication Network**  
Matthew Crespo, Chinwendu Enyioha. CISS 2025 (59th, Johns Hopkins). [IEEE Xplore](https://doi.org/10.1109/ciss64860.2025.10944666)  
Theme D: Bandits and sequential decisions

> This paper studies a consensus-based policy evaluation algorithm in a cooperative team of heterogeneous learners. To improve each agent’s approximation of their value function, they each update their weight parameters, then perform consensus updates with neighboring agents over a dynamic communication network. We present the analysis of an efficient fully distributed algorithm for cooperatively evaluating and optimizing their value functions over a time-varying communication network in the average-reward setting. Our main result shows that, using this algorithm, the agents can approximate the true value function, with the approximation error dependent on the number of communication rounds and number of time steps it takes for the communication network to be connected. To validate the theoretical results, we present accompanying numerical experiments that show the theoretical error bounds are not only tight, but get tighter as the time steps required to guarantee network connectivity reduces.

**Relevance.** Consensus policy evaluation over a time-varying network, average-reward setting with Markovian samples; dependence over time and a graph across agents.

### C26

**Doubly Pessimistic Algorithms for Strictly Safe Off-Policy Optimization**  
Sanae Amani, Lin F. Yang. CISS 2022 (56th, Princeton). [IEEE Xplore](https://doi.org/10.1109/ciss53076.2022.9751158)  
Theme D: Bandits and sequential decisions

> We study offline reinforcement learning (RL) in the presence of safety requirements: from a dataset collected a priori and without direct access to the true environment, learn an optimal policy that is guaranteed to respect the safety constraints. We address this problem by modeling the safety requirement as an unknown cost function of states and actions, whose expected value with respect to the policy must fall below a certain threshold. We then present an algorithm in the context of finite-horizon Markov decision processes (MDPs), termed Safe-DPVI that performs in a doubly pessimistic manner when 1) it constructs a conservative set of safe policies; and 2) when it selects a good policy from that conservative set. Without assuming the sufficient coverage of the dataset or any structure for the underlying MDPs, we establish a data-dependent upper bound on the suboptimality gap of the safe policy Safe-DPVI returns. We then specialize our results to linear MDPs with appropriate assumptions on dataset being well-explored. Both data-dependent and specialized bounds nearly match that of state-of-the-art unsafe offline RL algorithms, with an additional multiplicative factor\$\frac{\Sigma_{h=1}^{H}\alpha_{h}}{H}\$, where αhcharacterizes the safety constraint at time-step\$h\$. We further present numerical simulations that corroborate our theoretical findings. A full version referred to as technical report of this paper is accessible at: https://offline-rl-neurips.github.io/2021/pdf/21.pdf

**Relevance.** Doubly pessimistic offline RL under safety constraints; pessimism as a safety rail, as our certificates are for irrevocable decisions.
