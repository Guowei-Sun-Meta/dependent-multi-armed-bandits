| candidate               | baseline                      |   relative_difference |   ci_low |   ci_high |   users | scope                                                     |
|:------------------------|:------------------------------|----------------------:|---------:|----------:|--------:|:----------------------------------------------------------|
| spectral_ts/I-mf/10.0   | spectral_ts/I-mf~rewired/10.0 |               0.00286 | -0.04128 |   0.04638 |     120 | user-cluster bootstrap, conditional on common tuning data |
| sp_klucb/I-mf/oracle    | sp_klucb/I-mf~rewired/oracle  |              -0.08448 | -0.09459 |  -0.07383 |     120 | user-cluster bootstrap, conditional on common tuning data |
| sp_klucb/I-mf/none      | sp_klucb/I-mf~rewired/none    |               0.02796 | -0.03387 |   0.09739 |     120 | user-cluster bootstrap, conditional on common tuning data |
| shrink_ts/complete/10.0 | spectral_ts/I-mf/10.0         |              -0.13387 | -0.22097 |  -0.04498 |     120 | user-cluster bootstrap, conditional on common tuning data |
