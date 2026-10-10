# Paper Analyses and Figures

Scripts that read the saved results of several experiments and produce the long papers' figures and cross-experiment analyses. They run no new experiments.

| Script | Reads | Writes |
| --- | --- | --- |
| [paper_figures.py](paper_figures.py) | KuaiRec, benchmark, certificate and one-domain Wikipedia results | [research/claude_opus_10_09/figures](../../research/claude_opus_10_09/figures) (`fig1`–`fig6`) |
| [deepdive.py](deepdive.py) | All four experiment families, plus the KuaiRec and Wikipedia panels | [research/claude_opus_10_09_v2/analysis](../../research/claude_opus_10_09_v2/analysis): one CSV and one markdown table per theory-to-data analysis |
| [paper_figures_v2.py](paper_figures_v2.py) | The `deepdive.py` analyses and the simulation results | [research/claude_opus_10_09_v2/figures](../../research/claude_opus_10_09_v2/figures) (`f1`–`f6`) |

From the repository root:

```sh
.venv/bin/python -I experiments/paper/paper_figures.py
OPENBLAS_NUM_THREADS=2 .venv/bin/python -I experiments/paper/deepdive.py     # about 15 s; needs data/kuairec_cache
.venv/bin/python -I experiments/paper/paper_figures_v2.py
```

`deepdive.py` imports the KuaiRec code (`data.py`, `graphs.py`, `daily.py`) from [../kuairec/code](../kuairec/code). `paper_figures_v2.py` reuses the colours and styles of `paper_figures.py`.
