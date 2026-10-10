Setting A, 60 users x 6 graphs: SP-UCB regret / UCB1 regret against the share of suboptimal components whose certified width is below their gap (the condition for H_c < infinity).

| certificate   | rejectable share   |   instances |   median ratio to UCB1 |   q25 |   q75 |   spearman (all) |     p |
|:--------------|:-------------------|------------:|-----------------------:|------:|------:|-----------------:|------:|
| oracle        | <=40%              |          54 |                  0.844 | 0.781 | 0.912 |           -0.484 | 0.000 |
| oracle        | 40-60%             |          67 |                  0.727 | 0.629 | 0.788 |           -0.484 | 0.000 |
| oracle        | 60-80%             |         119 |                  0.522 | 0.410 | 0.608 |           -0.484 | 0.000 |
| oracle        | >80%               |         120 |                  0.399 | 0.300 | 0.830 |           -0.484 | 0.000 |
| energy        | <=40%              |         268 |                  0.980 | 0.948 | 0.995 |           -0.717 | 0.000 |
| energy        | 40-60%             |          43 |                  0.890 | 0.831 | 0.931 |           -0.717 | 0.000 |
| energy        | 60-80%             |          26 |                  0.959 | 0.799 | 0.971 |           -0.717 | 0.000 |
| energy        | >80%               |          23 |                  0.954 | 0.944 | 0.970 |           -0.717 | 0.000 |
