#!/bin/bash
# Three-hour experiment queue (9 October 2026). Run from the repo root.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
PY=".venv/bin/python -I"
LOG=data/logs
echo "$(date '+%H:%M:%S') START setting_b_main"
$PY experiments/kuairec/setting_b.py --instances 8 --users 300 --arms 100 --horizon 100000 --jobs 7 > $LOG/setting_b_main.log 2>&1 && echo "$(date '+%H:%M:%S') DONE setting_b_main" || echo "$(date '+%H:%M:%S') FAIL setting_b_main"
echo "$(date '+%H:%M:%S') START setting_a2"
$PY experiments/kuairec/setting_a2.py --users 60 --subsets 3 --horizon 20000 --jobs 7 > $LOG/setting_a2.log 2>&1 && echo "$(date '+%H:%M:%S') DONE setting_a2" || echo "$(date '+%H:%M:%S') FAIL setting_a2"
echo "$(date '+%H:%M:%S') START setting_b_large"
$PY experiments/kuairec/setting_b.py --instances 4 --users 600 --arms 100 --horizon 300000 --jobs 7 --tag _large > $LOG/setting_b_large.log 2>&1 && echo "$(date '+%H:%M:%S') DONE setting_b_large" || echo "$(date '+%H:%M:%S') FAIL setting_b_large"
echo "$(date '+%H:%M:%S') START alignment_r2"
$PY experiments/kuairec/alignment.py --model R2 --k 10 > $LOG/alignment_r2.log 2>&1 && $PY experiments/kuairec/render_alignment.py --model R2 --k 10 >> $LOG/alignment_r2.log 2>&1 && echo "$(date '+%H:%M:%S') DONE alignment_r2" || echo "$(date '+%H:%M:%S') FAIL alignment_r2"
echo "$(date '+%H:%M:%S') QUEUE_FINISHED"
