Setting B: 300 users x 100 videos, T = 100,000 arrivals (333 per user, 3.3 per user-video pair); 8 instances.

Ratios are per instance, then averaged; min and max over instances in brackets.

| Policy | Graph | Parameter | Mean regret | Ratio to per-user TS [min, max] | Ratio to per-user KL-UCB |
| --- | --- | --- | ---: | --- | ---: |
| graph_ts | complete | 1.0 | 37,507 | 1.096 [1.074, 1.103] | 1.120 |
| graph_ts | complete | 10.0 | 24,699 | 0.726 [0.626, 0.802] | 0.742 |
| graph_ts | U-coeng | 1.0 | 38,573 | 1.128 [1.104, 1.140] | 1.152 |
| graph_ts | U-coeng | 10.0 | 25,798 | 0.759 [0.650, 0.834] | 0.775 |
| graph_ts | U-mf | 1.0 | 37,977 | 1.110 [1.089, 1.125] | 1.134 |
| graph_ts | U-mf | 10.0 | 25,201 | 0.741 [0.645, 0.799] | 0.757 |
| graph_ts | U-coauthor | 1.0 | 38,276 | 1.119 [1.097, 1.130] | 1.143 |
| graph_ts | U-coauthor | 10.0 | 25,361 | 0.746 [0.634, 0.837] | 0.762 |
| graph_ts | U-geo | 1.0 | 38,059 | 1.112 [1.085, 1.126] | 1.136 |
| graph_ts | U-geo | 10.0 | 30,466 | 0.893 [0.836, 0.950] | 0.912 |
| graph_ts | U-coeng~rewired | 1.0 | 38,186 | 1.116 [1.094, 1.129] | 1.140 |
| graph_ts | U-coeng~rewired | 10.0 | 25,310 | 0.745 [0.629, 0.839] | 0.761 |
| ts_ind | - | - | 34,220 | 1.000 [1.000, 1.000] | 1.021 |
| ts_one | - | - | 31,442 | 0.929 [0.645, 1.135] | 0.949 |
| klucb_ind | - | - | 33,510 | 0.979 [0.967, 0.985] | 1.000 |
| sp_klucb_user | U-coeng | oracle | 32,119 | 0.938 [0.926, 0.947] | 0.958 |
| sp_klucb_user | U-coeng | cal90 | 33,509 | 0.979 [0.967, 0.985] | 1.000 |
| sp_klucb_user | U-coeng | cal50 | 33,079 | 0.967 [0.958, 0.972] | 0.987 |
| sp_klucb_user | U-coeng | none | 47,526 | 1.390 [1.318, 1.419] | 1.420 |
| sp_klucb_user | U-mf | oracle | 32,093 | 0.938 [0.925, 0.949] | 0.958 |
| sp_klucb_user | U-mf | cal90 | 33,507 | 0.979 [0.967, 0.985] | 1.000 |
| sp_klucb_user | U-mf | cal50 | 33,071 | 0.967 [0.959, 0.977] | 0.987 |
| sp_klucb_user | U-mf | none | 47,494 | 1.389 [1.319, 1.418] | 1.419 |
| sp_klucb_user | U-coauthor | oracle | 31,981 | 0.934 [0.926, 0.945] | 0.954 |
| sp_klucb_user | U-coauthor | cal90 | 33,498 | 0.979 [0.967, 0.985] | 1.000 |
| sp_klucb_user | U-coauthor | cal50 | 33,052 | 0.966 [0.960, 0.976] | 0.987 |
| sp_klucb_user | U-coauthor | none | 47,486 | 1.389 [1.318, 1.418] | 1.419 |
| sp_klucb_user | U-geo | oracle | 32,231 | 0.942 [0.933, 0.955] | 0.962 |
| sp_klucb_user | U-geo | cal90 | 33,510 | 0.979 [0.967, 0.985] | 1.000 |
| sp_klucb_user | U-geo | cal50 | 33,091 | 0.967 [0.957, 0.973] | 0.988 |
| sp_klucb_user | U-geo | none | 46,967 | 1.374 [1.291, 1.411] | 1.404 |
| sp_klucb_user | U-coeng~rewired | oracle | 32,526 | 0.950 [0.938, 0.961] | 0.970 |
| sp_klucb_user | U-coeng~rewired | cal90 | 33,510 | 0.979 [0.967, 0.985] | 1.000 |
| sp_klucb_user | U-coeng~rewired | cal50 | 33,352 | 0.975 [0.964, 0.980] | 0.995 |
| sp_klucb_user | U-coeng~rewired | none | 47,546 | 1.391 [1.320, 1.419] | 1.420 |
