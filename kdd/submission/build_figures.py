#!/usr/bin/env python3
"""Rebuild manuscript vector figures from the included result snapshot."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                     'axes.labelsize': 8, 'legend.fontsize': 7,
                     'xtick.labelsize': 7, 'ytick.labelsize': 7,
                     'pdf.fonttype': 42, 'ps.fonttype': 42,
                     'axes.spines.top': False, 'axes.spines.right': False})
(HERE / 'figures').mkdir(exist_ok=True)
with (HERE / 'data/real_dynamics_certificates.csv').open() as f:
    rows = [r for r in csv.DictReader(f) if r['noise']=='gauss' and r['policy']=='sp']
fig, axes = plt.subplots(2,1, figsize=(3.35,3.35), layout='constrained')
colors = {'iid':'#b74a40', 'known':'#226384', 'fitted':'#608942'}
labels = {'iid':'IID', 'known':'Known model', 'fitted':'Fitted model'}
for k in (5,10):
    for j,m in enumerate(('iid','known','fitted')):
        row = next(r for r in rows if int(r['budget'])==k and r['learner']==m)
        x = (0 if k==5 else 1) + (j-1)*0.22
        y = float(row['failure_rate'])*100
        err = [[y-float(row['ci_low'])*100],[float(row['ci_high'])*100-y]]
        axes[0].errorbar(x,y,yerr=err,color=colors[m],fmt='o',ms=4,capsize=2,
                         label=labels[m] if k==5 else None)
        axes[1].bar(x,float(row['mean_regret']),width=0.19,color=colors[m])
axes[0].set(ylabel='Runs with violations (%)',ylim=(-3,106))
axes[0].legend(loc='upper left', frameon=False)
axes[1].set(ylabel='Cumulative mean regret',ylim=(0,560))
for ax in axes:
    ax.set_xticks([0,1],['Slate size 5','Slate size 10'])
    ax.grid(axis='y',alpha=.18); ax.set_axisbelow(True)
fig.savefig(HERE/'figures/coverage_cost.pdf',metadata={'Title':'Confidence validity and regret cost'})
plt.close(fig)

with (HERE/'data/kuairec_chronological_contrasts.csv').open() as f:
    rows = [r for r in csv.DictReader(f) if int(r['budget'])==5 and r['policy']=='st_ucb']
refs = [('ts_iid','IID TS'),('ar_ucb','Temporal UCB'),('st_ucb_rewired','Rewired graph'),
        ('st_ucb_nograph','Common factor'),('last_value','Last value')]
fig, ax = plt.subplots(figsize=(3.35,2.05),layout='constrained')
for i,(key,label) in enumerate(refs):
    row = next(r for r in rows if r['reference']==key)
    y = float(row['relative_difference'])*100
    lo,hi = float(row['ci_low'])*100,float(row['ci_high'])*100
    ax.errorbar(y,i,xerr=[[y-lo],[hi-y]],fmt='o',color='#226384',capsize=2,ms=4)
ax.axvline(0,color='#666666',lw=.8,ls='--')
ax.set_yticks(range(len(refs)),[v for _,v in refs]); ax.invert_yaxis()
ax.set(xlabel='Joint UCB relative loss difference (%)',xlim=(-74,68))
ax.set_xticks([-60,-30,0,30,60]); ax.grid(axis='x',alpha=.18)
fig.savefig(HERE/'figures/policy_controls.pdf',metadata={'Title':'Chronological KuaiRec paired policy controls'})
plt.close(fig)
print('Built two vector figures from included CSV snapshots.')
