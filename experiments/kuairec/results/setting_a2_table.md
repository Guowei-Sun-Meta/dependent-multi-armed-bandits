Setting A v2: 300 videos per instance, T = 20,000; 60 instances (users x video subsets).

| Policy | Graph | Parameter | Ratio to TS (mean / median / 90th pct.) | Share beating TS | Ratio to KL-UCB at fixed level (mean / 90th pct.) |
| --- | --- | --- | --- | ---: | --- |
| ts | - | - | 1.000 / 1.000 / 1.00 | 0.00 | 0.760 / 1.30 |
| klucb | - | logt | 1.080 / 1.242 / 1.33 | 0.42 | 0.717 / 1.00 |
| klucb | - | ell | 1.875 / 1.757 / 3.12 | 0.42 | 1.000 / 1.00 |
| shrink_ts | complete | 1.0 | 2.189 / 1.154 / 3.90 | 0.25 | 2.229 / 4.97 |
| shrink_ts | complete | 10.0 | 1.060 / 0.634 / 1.43 | 0.77 | 1.068 / 1.74 |
| spectral_ts | I-mf | 10.0 | 1.322 / 0.659 / 1.74 | 0.80 | 1.421 / 2.20 |
| sp_klucb | I-mf | oracle | 1.238 / 1.122 / 1.95 | 0.45 | 0.784 / 1.05 |
| sp_klucb | I-mf | energy | 1.803 / 1.729 / 2.91 | 0.42 | 0.983 / 1.05 |
| sp_klucb | I-mf | none | 0.824 / 0.740 / 1.19 | 0.83 | 0.668 / 1.32 |
| sp_klucb | I-mf | cal90 | 1.848 / 1.737 / 3.01 | 0.42 | 0.998 / 1.05 |
| sp_klucb | I-mf | cal50 | 1.279 / 1.187 / 2.03 | 0.43 | 0.805 / 1.05 |
| spectral_ts | I-coeng | 10.0 | 3.187 / 0.981 / 4.02 | 0.55 | 3.549 / 2.88 |
| sp_klucb | I-coeng | oracle | 1.162 / 1.092 / 1.75 | 0.45 | 0.753 / 1.04 |
| sp_klucb | I-coeng | energy | 1.826 / 1.725 / 2.94 | 0.42 | 0.992 / 1.04 |
| sp_klucb | I-coeng | none | 0.800 / 0.735 / 1.17 | 0.78 | 0.624 / 1.33 |
| sp_klucb | I-coeng | cal90 | 1.834 / 1.742 / 2.94 | 0.42 | 0.995 / 1.04 |
| sp_klucb | I-coeng | cal50 | 1.204 / 1.170 / 1.82 | 0.42 | 0.776 / 1.04 |
| spectral_ts | I-tag | 10.0 | 1.394 / 0.840 / 2.21 | 0.67 | 1.390 / 2.46 |
| sp_klucb | I-tag | oracle | 1.324 / 1.209 / 2.26 | 0.45 | 0.812 / 1.03 |
| sp_klucb | I-tag | energy | 1.816 / 1.739 / 2.93 | 0.42 | 0.984 / 1.03 |
| sp_klucb | I-tag | none | 1.219 / 0.798 / 3.03 | 0.60 | 0.803 / 1.34 |
| sp_klucb | I-tag | cal90 | 1.866 / 1.752 / 3.10 | 0.42 | 1.001 / 1.03 |
| sp_klucb | I-tag | cal50 | 1.394 / 1.402 / 2.20 | 0.42 | 0.842 / 1.03 |
| spectral_ts | I-mf~rewired | 10.0 | 1.425 / 0.605 / 4.04 | 0.80 | 1.565 / 4.66 |
| sp_klucb | I-mf~rewired | oracle | 1.326 / 1.312 / 2.11 | 0.42 | 0.813 / 1.04 |
| sp_klucb | I-mf~rewired | energy | 1.877 / 1.757 / 3.12 | 0.42 | 1.004 / 1.04 |
| sp_klucb | I-mf~rewired | none | 0.749 / 0.697 / 1.04 | 0.87 | 0.558 / 0.97 |
| sp_klucb | I-mf~rewired | cal90 | 1.878 / 1.757 / 3.12 | 0.42 | 1.005 / 1.04 |
| sp_klucb | I-mf~rewired | cal50 | 1.365 / 1.322 / 2.28 | 0.42 | 0.834 / 1.04 |

Certificates (means over instances and graphs):

| Certificate | Share of components valid | Share of suboptimal components rejectable | Mean width |
| --- | ---: | ---: | ---: |
| oracle | 1.00 | 0.63 | 0.358 |
| energy | 1.00 | 0.18 | 0.796 |
| none | 0.00 | 0.98 | 0.000 |
| cal90 | 0.93 | 0.19 | 0.709 |
| cal50 | 0.52 | 0.65 | 0.303 |
