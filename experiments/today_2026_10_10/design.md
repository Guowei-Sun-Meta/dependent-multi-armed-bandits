# Results-today protocol, 10 October 2026

This bounded implementation consolidates the two plans for same-day results. It preserves released results. Raw runs, dated acquisition, model settings, checks and measured resources belong here. Raw OBD ZIP is cached under git-ignored `data/obd`; only aggregates are retained here.

Primary order: existing historical-graph Wikipedia panels with stronger baselines; small general-AR coverage/robustness study; targeted false-elimination and slate-contrast instances; small controlled correlation experiment; actual OBD support audit and a calendar-time censored-feedback comparison. KuaiRec chronology requires raw files absent from this checkout and is explicitly outstanding.

## Wikipedia

Reuse the frozen astronomy and football article lists and archived pre-2024 graph matrices. Retrieve 2024–2025 human pageviews. Fit January–September 2024; develop October–December; refit on all 2024; evaluate continuously through 2025 without full-field refresh. Each method gets the same 366-day full-history initialization. Report four disjoint 90-day summaries plus the remaining five days separately; they share a field and are not independent histories. Use log1p views, batch budgets 1 and 5, and exact selected feedback. Hyperparameters are selected on development data, never 2025.

Compare static, last value, seasonal naive with predicted unobserved lags, EWMA, iid/discounted/window UCB and TS, AR-only greedy/UCB, historical-graph greedy/UCB and common-factor greedy. Five policy seeds quantify conditional randomization only. Date-block bootstrap comparisons are descriptive within each panel, not population inference. If API acquisition is incomplete, retain an explicitly acquisition-limited panel rather than silently impute values or select by outcomes. Archive source graph hashes; historical revisions were reconstructed in the released study and are not reacquired in this run.

## Controlled studies

Fix true means across paired innovation worlds; hold marginal fluctuation variance fixed. Screen small AR(1), selected-lag AR(7), dense AR(20), and heterogeneous-order cases with known, independently fitted and wrong dynamics. Gaussian theory checks use independent innovations over time. Heavy-tail results and conservative fitted-model scaling are empirical stress tests. Report anytime coverage and false elimination with Wilson intervals; zero failures is not proof. Verify innovation regression against dense Gaussian conditioning, including simultaneous slate observations with marginal covariance. The targeted false-elimination experiment uses randomized arm order, bursty sampling, and several horizons. The correlation study corrupts learner covariance with fixed true paths; it does not change the world across policies.

## OBD

Audit actual full random-policy campaign logs, item IDs, positions, propensities, UTC timestamps, seven-day coverage, counts and rare-event precision. Primary pilot: men's campaign, position 1; first three UTC dates train, fourth develop, last three test. Keep physical time and hourly bins, including empty feedback. Build graphs from training visitor-cohort response profiles; inspect precision before attempting general-AR Gaussian filtering. If click observations are too sparse, retain the declared stationary/forgetting censored-feedback comparison and frozen-policy IPS scope; do not claim a validated temporal likelihood or dynamically optimal policy.

Choose an item before a bin. Reveal matching item clicks/impressions only after selection. IPS uses the released position-specific probability without subset renormalization. Evaluate the learner receiving censored feedback, not a deployed learner with every selected click observed. Match test support, initialization and logging censoring across policies. No latent oracle regret or true PCS is estimated from logs. Report seed variation separately from block sensitivity. Test hidden-label invariance, propensity recovery on known-counterfactual data and empty-bin time advancement.

## Scope

This is a pilot evidence package, not completion of the full pre-submission agenda. Published comparator AR2-p, larger confirmations, a new Bernoulli filter, Retailrocket and Web-scale approximations are deferred. Negative results are retained. Any execution changes and resource limits are recorded in the final report.
