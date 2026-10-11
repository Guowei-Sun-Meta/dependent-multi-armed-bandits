# KuaiRec daily slot, chronological protocol: tables

Regret per slot per day (logit complete-play rate), mean over 15 panel-window units (5 seeds averaged within each unit). Lower is better.

|   k | policy         |   regret |   ÷ ts_iid |   ÷ static |
|----:|:---------------|---------:|-----------:|-----------:|
|   1 | st_greedy      |   0.2209 |      0.47  |      0.464 |
|   1 | ewma           |   0.2283 |      0.485 |      0.48  |
|   1 | last_value     |   0.2309 |      0.491 |      0.486 |
|   1 | ar_greedy      |   0.2334 |      0.496 |      0.491 |
|   1 | st_ucb_rewired |   0.2351 |      0.5   |      0.494 |
|   1 | st_ucb_nograph |   0.2362 |      0.502 |      0.497 |
|   1 | st_ucb         |   0.2383 |      0.507 |      0.501 |
|   1 | ar_ucb         |   0.2399 |      0.51  |      0.504 |
|   1 | swucb          |   0.2884 |      0.613 |      0.606 |
|   1 | dts            |   0.3613 |      0.768 |      0.76  |
|   1 | ts_iid         |   0.4703 |      1     |      0.989 |
|   1 | seasonal       |   0.4713 |      1.002 |      0.991 |
|   1 | static         |   0.4756 |      1.011 |      1     |
|   5 | last_value     |   0.1411 |      0.43  |      0.405 |
|   5 | st_greedy      |   0.1444 |      0.44  |      0.414 |
|   5 | ar_greedy      |   0.1495 |      0.456 |      0.429 |
|   5 | st_ucb         |   0.1504 |      0.459 |      0.432 |
|   5 | st_ucb_rewired |   0.1525 |      0.465 |      0.438 |
|   5 | st_ucb_nograph |   0.1559 |      0.475 |      0.447 |
|   5 | ar_ucb         |   0.1696 |      0.517 |      0.487 |
|   5 | ewma           |   0.2391 |      0.729 |      0.686 |
|   5 | swucb          |   0.2421 |      0.738 |      0.695 |
|   5 | dts            |   0.2941 |      0.897 |      0.844 |
|   5 | ts_iid         |   0.328  |      1     |      0.941 |
|   5 | seasonal       |   0.3301 |      1.006 |      0.947 |
|   5 | static         |   0.3484 |      1.062 |      1     |

## Paired contrasts

|   k | contrast                                   | a         | b              | relative diff (a/b − 1)   | 95% interval     | units a wins   | verdict      |
|----:|:-------------------------------------------|:----------|:---------------|:--------------------------|:-----------------|:---------------|:-------------|
|   1 | joint filter (graph) vs iid TS             | st_ucb    | ts_iid         | -49.3%                    | -85.5% to -13.5% | 80%            | a better     |
|   1 | temporal-only filter vs iid TS             | ar_ucb    | ts_iid         | -49.0%                    | -84.6% to -12.8% | 73%            | a better     |
|   1 | graph vs temporal-only (same UCB)          | st_ucb    | ar_ucb         | -0.7%                     | -6.1% to +3.7%   | 53%            | inconclusive |
|   1 | real vs rewired prefix graph               | st_ucb    | st_ucb_rewired | +1.4%                     | -17.3% to +9.1%  | 33%            | inconclusive |
|   1 | graph vs common factor only                | st_ucb    | st_ucb_nograph | +0.9%                     | -5.1% to +6.1%   | 40%            | inconclusive |
|   1 | joint filter vs EWMA (forgetting)          | st_ucb    | ewma           | +4.4%                     | -10.2% to +42.4% | 40%            | inconclusive |
|   1 | joint filter vs discounted TS (forgetting) | st_ucb    | dts            | -34.0%                    | -72.5% to -13.5% | 87%            | a better     |
|   1 | temporal-only filter vs EWMA               | ar_ucb    | ewma           | +5.1%                     | -8.5% to +43.3%  | 40%            | inconclusive |
|   1 | joint filter (UCB) vs last value           | st_ucb    | last_value     | +3.2%                     | -12.6% to +42.9% | 27%            | inconclusive |
|   1 | joint filter (greedy) vs last value        | st_greedy | last_value     | -4.4%                     | -25.5% to +18.0% | 47%            | inconclusive |
|   1 | joint filter (greedy) vs EWMA              | st_greedy | ewma           | -3.3%                     | -23.7% to +19.1% | 33%            | inconclusive |
|   1 | EWMA vs iid TS                             | ewma      | ts_iid         | -51.5%                    | -89.3% to -11.7% | 67%            | a better     |
|   1 | discounted TS vs iid TS                    | dts       | ts_iid         | -23.2%                    | -54.1% to +10.0% | 47%            | inconclusive |
|   5 | joint filter (graph) vs iid TS             | st_ucb    | ts_iid         | -54.1%                    | -66.8% to -43.2% | 100%           | a better     |
|   5 | temporal-only filter vs iid TS             | ar_ucb    | ts_iid         | -48.3%                    | -60.8% to -37.1% | 100%           | a better     |
|   5 | graph vs temporal-only (same UCB)          | st_ucb    | ar_ucb         | -11.3%                    | -20.1% to -5.4%  | 87%            | a better     |
|   5 | real vs rewired prefix graph               | st_ucb    | st_ucb_rewired | -1.4%                     | -6.5% to +3.3%   | 67%            | inconclusive |
|   5 | graph vs common factor only                | st_ucb    | st_ucb_nograph | -3.5%                     | -7.0% to +1.1%   | 67%            | inconclusive |
|   5 | joint filter vs EWMA (forgetting)          | st_ucb    | ewma           | -37.1%                    | -51.8% to -17.4% | 87%            | a better     |
|   5 | joint filter vs discounted TS (forgetting) | st_ucb    | dts            | -48.9%                    | -63.0% to -39.5% | 93%            | a better     |
|   5 | temporal-only filter vs EWMA               | ar_ucb    | ewma           | -29.1%                    | -42.2% to -5.6%  | 80%            | a better     |
|   5 | joint filter (UCB) vs last value           | st_ucb    | last_value     | +6.6%                     | -9.5% to +61.1%  | 33%            | inconclusive |
|   5 | joint filter (greedy) vs last value        | st_greedy | last_value     | +2.4%                     | -11.6% to +44.5% | 40%            | inconclusive |
|   5 | joint filter (greedy) vs EWMA              | st_greedy | ewma           | -39.6%                    | -56.1% to -24.0% | 87%            | a better     |
|   5 | EWMA vs iid TS                             | ewma      | ts_iid         | -27.1%                    | -52.1% to -13.2% | 93%            | a better     |
|   5 | discounted TS vs iid TS                    | dts       | ts_iid         | -10.3%                    | -24.2% to -2.5%  | 73%            | a better     |

## By window (mean over panels)

|   k |   window |   ts_iid |   static |   ewma |    dts |   ar_ucb |   st_ucb |   st_ucb_rewired |
|----:|---------:|---------:|---------:|-------:|-------:|---------:|---------:|-----------------:|
|   1 |       30 |   0.5781 |   0.5306 | 0.4988 | 0.6254 |   0.4991 |   0.4952 |           0.4715 |
|   1 |       41 |   0.464  |   0.5085 | 0.0519 | 0.2672 |   0.0726 |   0.0705 |           0.0837 |
|   1 |       52 |   0.3689 |   0.3879 | 0.1343 | 0.1912 |   0.1481 |   0.1494 |           0.1503 |
|   5 |       30 |   0.4785 |   0.4832 | 0.4114 | 0.4612 |   0.2877 |   0.2629 |           0.2623 |
|   5 |       41 |   0.2876 |   0.3188 | 0.2032 | 0.2524 |   0.1252 |   0.1024 |           0.1077 |
|   5 |       52 |   0.2179 |   0.2433 | 0.1026 | 0.1687 |   0.0959 |   0.0859 |           0.0876 |

## Tuned on the development window (days 20–30)

|          |   value |
|:---------|--------:|
| ewma|1   |    1    |
| dts|1    |    0.9  |
| swucb|1  |   14    |
| ar_ucb|1 |    0.5  |
| st_ucb|1 |    0.5  |
| ewma|5   |    7    |
| dts|5    |    0.97 |
| swucb|5  |   14    |
| ar_ucb|5 |    1    |
| st_ucb|5 |    0.5  |

Unavailable picks (chosen video with no plays that day), all test runs: 201 of 21450+ slot-days.

## Units

| unit        | kind   |   origin |   fit_days | test_days   |   cutoff_date |   videos |   eligible_at_origin |   graph_rows_before_cutoff |   unavailable_test_cells |   graph_edges |
|:------------|:-------|---------:|-----------:|:------------|--------------:|---------:|---------------------:|---------------------------:|-------------------------:|--------------:|
| dev_F19_p0  | dev    |       30 |         19 | 20-30       |      20200724 |       50 |                  255 |                    1583621 |                        0 |           405 |
| dev_F19_p1  | dev    |       30 |         19 | 20-30       |      20200724 |       50 |                  255 |                    1583621 |                        0 |           413 |
| dev_F19_p2  | dev    |       30 |         19 | 20-30       |      20200724 |       50 |                  255 |                    1583621 |                        0 |           417 |
| dev_F19_p3  | dev    |       30 |         19 | 20-30       |      20200724 |       50 |                  255 |                    1583621 |                        0 |           426 |
| dev_F19_p4  | dev    |       30 |         19 | 20-30       |      20200724 |       50 |                  255 |                    1583621 |                        0 |           436 |
| test_F30_p0 | test   |       30 |         30 | 31-41       |      20200804 |       50 |                  255 |                    3289224 |                        0 |           410 |
| test_F30_p1 | test   |       30 |         30 | 31-41       |      20200804 |       50 |                  255 |                    3289224 |                        0 |           412 |
| test_F30_p2 | test   |       30 |         30 | 31-41       |      20200804 |       50 |                  255 |                    3289224 |                        0 |           422 |
| test_F30_p3 | test   |       30 |         30 | 31-41       |      20200804 |       50 |                  255 |                    3289224 |                        0 |           427 |
| test_F30_p4 | test   |       30 |         30 | 31-41       |      20200804 |       50 |                  255 |                    3289224 |                        2 |           433 |
| test_F41_p0 | test   |       41 |         41 | 42-52       |      20200815 |       49 |                  247 |                    7713783 |                        0 |           410 |
| test_F41_p1 | test   |       41 |         41 | 42-52       |      20200815 |       49 |                  247 |                    7713783 |                        0 |           400 |
| test_F41_p2 | test   |       41 |         41 | 42-52       |      20200815 |       49 |                  247 |                    7713783 |                        0 |           422 |
| test_F41_p3 | test   |       41 |         41 | 42-52       |      20200815 |       49 |                  247 |                    7713783 |                        0 |           414 |
| test_F41_p4 | test   |       41 |         41 | 42-52       |      20200815 |       49 |                  247 |                    7713783 |                        0 |           416 |
| test_F52_p0 | test   |       52 |         52 | 53-63       |      20200826 |       49 |                  245 |                    7713783 |                        0 |           418 |
| test_F52_p1 | test   |       52 |         52 | 53-63       |      20200826 |       49 |                  245 |                    7713783 |                        7 |           412 |
| test_F52_p2 | test   |       52 |         52 | 53-63       |      20200826 |       49 |                  245 |                    7713783 |                        0 |           406 |
| test_F52_p3 | test   |       52 |         52 | 53-63       |      20200826 |       49 |                  245 |                    7713783 |                        8 |           407 |
| test_F52_p4 | test   |       52 |         52 | 53-63       |      20200826 |       49 |                  245 |                    7713783 |                        0 |           397 |
