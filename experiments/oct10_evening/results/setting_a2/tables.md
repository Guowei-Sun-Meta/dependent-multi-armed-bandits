# Setting A v2 at 120 users x 3 subsets

## All policies: 360 instances

Setting A v2: 300 videos per instance, T = 20,000; 360 instances (users x video subsets).

| Policy | Graph | Parameter | Ratio to TS (mean / median / 90th pct.) | Share beating TS | Ratio to KL-UCB at fixed level (mean / 90th pct.) |
| --- | --- | --- | --- | ---: | --- |
| ts | - | - | 1.000 / 1.000 / 1.00 | 0.00 | 0.806 / 1.30 |
| klucb | - | logt | 1.057 / 1.163 / 1.33 | 0.47 | 0.748 / 1.00 |
| klucb | - | ell | 1.755 / 1.443 / 3.13 | 0.47 | 1.000 / 1.00 |
| shrink_ts | complete | 1.0 | 2.397 / 1.413 / 4.05 | 0.26 | 2.516 / 5.12 |
| shrink_ts | complete | 10.0 | 0.916 / 0.674 / 1.32 | 0.84 | 0.902 / 1.61 |
| spectral_ts | I-mf | 10.0 | 1.173 / 0.686 / 1.64 | 0.78 | 1.168 / 1.97 |
| sp_klucb | I-mf | oracle | 1.197 / 0.988 / 1.90 | 0.50 | 0.802 / 1.04 |
| sp_klucb | I-mf | energy | 1.688 / 1.434 / 2.99 | 0.47 | 0.977 / 1.04 |
| sp_klucb | I-mf | none | 0.801 / 0.679 / 1.25 | 0.83 | 0.622 / 1.08 |
| sp_klucb | I-mf | cal90 | 1.731 / 1.431 / 3.04 | 0.47 | 0.992 / 1.04 |
| sp_klucb | I-mf | cal50 | 1.241 / 1.088 / 2.01 | 0.48 | 0.825 / 1.04 |
| spectral_ts | I-coeng | 10.0 | 2.805 / 1.115 / 4.89 | 0.42 | 2.906 / 4.49 |
| sp_klucb | I-coeng | oracle | 1.141 / 0.932 / 1.76 | 0.53 | 0.781 / 1.04 |
| sp_klucb | I-coeng | energy | 1.708 / 1.420 / 3.02 | 0.47 | 0.987 / 1.04 |
| sp_klucb | I-coeng | none | 0.825 / 0.735 / 1.30 | 0.78 | 0.634 / 1.13 |
| sp_klucb | I-coeng | cal90 | 1.721 / 1.426 / 2.99 | 0.47 | 0.991 / 1.04 |
| sp_klucb | I-coeng | cal50 | 1.178 / 1.026 / 1.81 | 0.50 | 0.802 / 1.04 |
| spectral_ts | I-tag | 10.0 | 1.440 / 0.889 / 2.32 | 0.60 | 1.476 / 2.83 |
| sp_klucb | I-tag | oracle | 1.275 / 1.056 / 2.05 | 0.49 | 0.833 / 1.04 |
| sp_klucb | I-tag | energy | 1.708 / 1.438 / 3.00 | 0.47 | 0.986 / 1.04 |
| sp_klucb | I-tag | none | 1.181 / 0.760 / 2.41 | 0.63 | 0.893 / 1.74 |
| sp_klucb | I-tag | cal90 | 1.746 / 1.442 / 3.10 | 0.47 | 0.999 / 1.04 |
| sp_klucb | I-tag | cal50 | 1.342 / 1.223 / 2.18 | 0.48 | 0.863 / 1.04 |
| spectral_ts | I-mf~rewired | 10.0 | 1.156 / 0.685 / 1.69 | 0.81 | 1.164 / 1.92 |
| sp_klucb | I-mf~rewired | oracle | 1.278 / 1.049 / 2.10 | 0.49 | 0.832 / 1.04 |
| sp_klucb | I-mf~rewired | energy | 1.749 / 1.442 / 3.12 | 0.47 | 0.996 / 1.04 |
| sp_klucb | I-mf~rewired | none | 0.779 / 0.701 / 1.05 | 0.87 | 0.619 / 1.04 |
| sp_klucb | I-mf~rewired | cal90 | 1.752 / 1.443 / 3.12 | 0.47 | 0.997 / 1.04 |
| sp_klucb | I-mf~rewired | cal50 | 1.314 / 1.178 / 2.23 | 0.47 | 0.851 / 1.04 |

Certificates (means over instances and graphs):

| Certificate | Share of components valid | Share of suboptimal components rejectable | Mean width |
| --- | ---: | ---: | ---: |
| oracle | 1.00 | 0.61 | 0.381 |
| energy | 1.00 | 0.18 | 0.802 |
| none | 0.00 | 0.95 | 0.000 |
| cal90 | 0.90 | 0.19 | 0.706 |
| cal50 | 0.48 | 0.63 | 0.302 |

## All policies: first 30 users x 2 subsets (committed v2 size)

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

## Per-user calibrated certificates: 360 instances

Setting A v2: 300 videos per instance, T = 20,000; 360 instances (users x video subsets).

| Policy | Graph | Parameter | Ratio to TS (mean / median / 90th pct.) | Share beating TS | Ratio to KL-UCB at fixed level (mean / 90th pct.) |
| --- | --- | --- | --- | ---: | --- |
| ts | - | - | 1.000 / 1.000 / 1.00 | 0.00 | 0.806 / 1.30 |
| klucb | - | logt | 1.057 / 1.163 / 1.33 | 0.47 | 0.748 / 1.00 |
| klucb | - | ell | 1.755 / 1.443 / 3.13 | 0.47 | 1.000 / 1.00 |
| sp_klucb | I-mf | user90 | 1.663 / 1.408 / 2.98 | 0.47 | 0.969 / 1.04 |
| sp_klucb | I-mf | user75 | 1.457 / 1.197 / 2.57 | 0.48 | 0.898 / 1.04 |
| sp_klucb | I-coeng | user90 | 1.625 / 1.369 / 2.92 | 0.47 | 0.957 / 1.04 |
| sp_klucb | I-coeng | user75 | 1.398 / 1.136 / 2.46 | 0.48 | 0.877 / 1.04 |

Certificates (means over instances and graphs):

| Certificate | Share of components valid | Share of suboptimal components rejectable | Mean width |
| --- | ---: | ---: | ---: |
| oracle | 1.00 | 0.63 | 0.369 |
| energy | 1.00 | 0.19 | 0.782 |
| none | 0.00 | 0.95 | 0.000 |
| cal90 | 0.90 | 0.21 | 0.699 |
| cal50 | 0.48 | 0.66 | 0.289 |
| user90 | 0.89 | nan | 0.630 |
| user75 | 0.74 | nan | 0.423 |

## Per-user calibrated certificates: first 30 users x 2 subsets (committed v2 size)

Setting A v2: 300 videos per instance, T = 20,000; 60 instances (users x video subsets).

| Policy | Graph | Parameter | Ratio to TS (mean / median / 90th pct.) | Share beating TS | Ratio to KL-UCB at fixed level (mean / 90th pct.) |
| --- | --- | --- | --- | ---: | --- |
| ts | - | - | 1.000 / 1.000 / 1.00 | 0.00 | 0.760 / 1.30 |
| klucb | - | logt | 1.080 / 1.242 / 1.33 | 0.42 | 0.717 / 1.00 |
| klucb | - | ell | 1.875 / 1.757 / 3.12 | 0.42 | 1.000 / 1.00 |
| sp_klucb | I-mf | user90 | 1.746 / 1.677 / 2.84 | 0.42 | 0.964 / 1.05 |
| sp_klucb | I-mf | user75 | 1.493 / 1.281 / 2.65 | 0.42 | 0.879 / 1.05 |
| sp_klucb | I-coeng | user90 | 1.702 / 1.630 / 2.87 | 0.42 | 0.950 / 1.04 |
| sp_klucb | I-coeng | user75 | 1.429 / 1.281 / 2.47 | 0.42 | 0.855 / 1.04 |

Certificates (means over instances and graphs):

| Certificate | Share of components valid | Share of suboptimal components rejectable | Mean width |
| --- | ---: | ---: | ---: |
| oracle | 1.00 | 0.67 | 0.345 |
| energy | 1.00 | 0.20 | 0.772 |
| none | 0.00 | 0.98 | 0.000 |
| cal90 | 0.93 | 0.22 | 0.701 |
| cal50 | 0.52 | 0.68 | 0.290 |
| user90 | 0.90 | nan | 0.575 |
| user75 | 0.73 | nan | 0.381 |
