import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import subprocess

def block_pairs(daily,refs,metric='loss_per_slot',timecol='test_day'):
    rows=[];rng=np.random.default_rng(SEED)
    for keys,g in daily.groupby(['panel','batch']):
        tab=g.groupby([timecol,'policy'])[metric].mean().unstack('policy')
        for ref in refs:
            for pol in tab:
                if pol==ref:continue
                x=(tab[pol]-tab[ref]).to_numpy();n=len(x)
                for length in [7,14,28]:
                    idx=rng.integers(0,n-length+1,size=(1000,int(np.ceil(n/length))))[:,:,None]+np.arange(length)
                    samples=x[idx.reshape(1000,-1)[:,:n]].mean(1);lo,hi=np.quantile(samples,[.025,.975])
                    rows.append(dict(panel=keys[0],batch=keys[1],policy=pol,reference=ref,block_days=length,difference=float(x.mean()),ci_low=lo,ci_high=hi))
    return pd.DataFrame(rows)

def validate():
    wiki=source_module('today_wiki_checks','experiments/today_2026_10_10/code/wikipedia.py')
    wiki.verify_feedback()
    required={'wikipedia':108,'obd':142,'certificates':480,'certificates_confirmation':400,'false_elimination':600,'factorial':2520}
    checks={}
    for folder,expected in required.items():
        d=pd.read_csv(OUT/folder/'runs.csv');assert len(d)==expected,(folder,len(d),expected)
        cols=d.select_dtypes(include='number').columns.difference(['failure_time'])
        # Deterministic-policy spread is undefined in summary tables, not raw runs.
        assert np.isfinite(d[cols].to_numpy()).all(),folder
        checks[folder]={'runs':len(d),'numeric_raw_results_finite':True}
    w=pd.read_csv(OUT/'wikipedia/daily.csv');assert len(w)==108*365
    assert w.groupby(['panel','batch','policy','seed']).size().eq(365).all()
    assert w.loss_per_slot.min()>=-1e-10
    for _,r in w.iterrows():assert len(set(map(int,r.chosen.split(','))))==r.batch
    o=pd.read_csv(OUT/'obd/decisions.csv');assert len(o)==142*72
    assert o.groupby(['policy','seed']).size().eq(72).all()
    assert o.matching_clicks.le(o.matching_impressions).all()
    assert o.matching_impressions.le(o.eligible_impressions).all()
    assert np.allclose(o.ips_numerator,o.matching_clicks*34)
    slate=pd.read_csv(OUT/'slate/summary.csv');assert (abs(slate.empirical_over_exact-1)<.04).all()
    checks.update({'wikipedia_daily_records':len(w),'obd_hourly_decisions':len(o),'slate_finite_variance_error_under_4_percent':True,'budget_and_slate_checks':'pass','obd_uniform_position_propensity_identity':'pass'})
    save_json(OUT/'validation.json',checks)
    return checks

def main():
    checks=validate();figs=HERE/'figures';figs.mkdir(exist_ok=True)
    w=pd.read_csv(OUT/'wikipedia/summary.csv');daily=pd.read_csv(OUT/'wikipedia/daily.csv')
    pairs=block_pairs(daily,['iid_ts','discounted_ts','ar_greedy','ewma']);pairs.to_csv(OUT/'wikipedia/paired.csv',index=False)
    coverage=pd.read_csv(OUT/'certificates_confirmation/summary.csv');elim=pd.read_csv(OUT/'false_elimination/summary.csv')
    ob=pd.read_csv(OUT/'obd/summary.csv');audit=pd.read_csv(OUT/'obd/observation_precision.csv')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':160})
    fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    chosen=['static','iid_ts','discounted_ts','ewma','ar_greedy','st_ucb']
    for ax,panel in zip(axs,['astronomy','football']):
        sub=w[(w.panel==panel)&(w.batch==5)].set_index('policy').loc[chosen]
        ax.barh(chosen,sub.loss_per_slot,color=['#9ca3af']*4+['#38a3a5','#3157a4']);ax.invert_yaxis();ax.set_title(panel.title()+', five readings/day');ax.set_xlabel('Observed-oracle log-view loss per slot')
    fig.savefig(figs/'wikipedia_baselines.png');plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    labels={'fitted':'Fitted','fitted_inflated':'Fitted, inflated','known':'Known model','wrong_order_or_diagonal':'Wrong order + diagonal'}
    axs[0].bar([labels[x] for x in coverage['mode']],coverage.failure_rate,color='#3157a4');axs[0].errorbar(np.arange(len(coverage)),coverage.failure_rate,yerr=[coverage.failure_rate-coverage.ci_low,coverage.ci_high-coverage.failure_rate],fmt='none',color='black',capsize=3);axs[0].tick_params(axis='x',rotation=25);axs[0].set_title('AR(20): 100 fresh worlds');axs[0].set_ylabel('Anytime certificate failure fraction')
    for method,color,shift in [('iid','#d16a43',-.12),('innovation','#3157a4',.12)]:
        d=elim[elim.method==method];x=np.arange(3)+shift;axs[1].bar(x,d.failure_rate,width=.24,label=method,color=color);axs[1].errorbar(x,d.failure_rate,yerr=[d.failure_rate-d.ci_low,d.ci_high-d.failure_rate],fmt='none',color='black',capsize=3)
    axs[1].set_xticks(range(3),['0','0.97','0.995']);axs[1].set_xlabel('AR(1) persistence');axs[1].set_title('Wrong elimination: 100 worlds/cell');axs[1].legend()
    fig.savefig(figs/'certificate_failures.png');plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    p=pd.read_csv(OUT/'factorial/paired.csv');p=p[(p.policy=='st_ucb')&(p.reference=='ar_ucb')&(p.level_spread==.25)]
    matrix=p.pivot(index='phi',columns='rho',values='difference');im=axs[0].imshow(matrix,vmin=-.09,vmax=.09,cmap='RdBu_r');axs[0].set_xticks(range(3),matrix.columns);axs[0].set_yticks(range(3),matrix.index);axs[0].set_xlabel('Innovation graph strength');axs[0].set_ylabel('Persistence');axs[0].set_title('Joint minus temporal-only loss\n20-world exploratory screen');fig.colorbar(im,ax=axs[0],shrink=.8)
    a=audit[(audit.campaign=='men')&(audit.position==1)];axs[1].bar(a.bin_hours.astype(str),a.zero_click_fraction,color='#3157a4');axs[1].set_ylim(0,1);axs[1].set_xlabel('Bin duration (hours)');axs[1].set_ylabel('Training item bins with zero clicks');axs[1].set_title('OBD rare-event precision gate')
    fig.savefig(figs/'correlation_and_obd.png');plt.close(fig)
    # Conditional date-block sensitivity for logged values, not deployment or population intervals.
    od=pd.read_csv(OUT/'obd/decisions.csv');od['hour']=pd.to_datetime(od.hour,utc=True);tab=od.groupby(['hour','policy'])[['ips_numerator','eligible_impressions']].mean();sens=[];rng=np.random.default_rng(SEED)
    for policy,g in tab.groupby(level='policy'):
        num=g.ips_numerator.to_numpy();den=g.eligible_impressions.to_numpy();n=len(num)
        for length in [6,12,24]:
            idx=rng.integers(0,n-length+1,size=(1000,int(np.ceil(n/length))))[:,:,None]+np.arange(length);idx=idx.reshape(1000,-1)[:,:n]
            values=num[idx].sum(1)/den[idx].sum(1);lo,hi=np.quantile(values,[.025,.975]);sens.append({'policy':policy,'block_hours':length,'ips_ctr':num.sum()/den.sum(),'low':lo,'high':hi,'scope':'descriptive within-field date-block sensitivity; no replay of adaptive histories'})
    pd.DataFrame(sens).to_csv(OUT/'obd/block_sensitivity.csv',index=False)
    manifest={'git_head_at_analysis':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'date':'2026-10-10','source_hashes':{},'new_files':{}}
    for source in ['research/gpt_sol_10_09/code/wikipedia_experiment.py','research/gpt_sol_10_09/results/wikipedia/astronomy_ar7_model.npz','research/gpt_sol_10_09/results/wikipedia/football_ar7_model.npz']:
        manifest['source_hashes'][source]=sha(ROOT/source)
    for path in HERE.rglob('*'):
        if path.is_file() and '.mplconfig' not in path.parts and '__pycache__' not in path.parts and path!=OUT/'manifest.json':manifest['new_files'][str(path.relative_to(HERE))]=sha(path)
    save_json(OUT/'manifest.json',manifest)
    def table(df):return df.to_markdown(index=False,floatfmt='.4f')
    key=w[(w.batch==5)&w.policy.isin(chosen)].pivot(index='policy',columns='panel',values='loss_per_slot').reset_index()
    reports=['# Same-day experiment results — 10 October 2026','',
    'Completed: 108 full-year Wikipedia policy runs; 480 general-AR coverage screen runs; 400 fresh AR(20) confirmation runs; 600 false-elimination runs; 2,520 correlation-screen runs; 142 OBD censored-learner trajectories. The slate-variance check uses 20,000 independent worlds per cell. These are new executions, not a repackaging of old results.',
    '', '## Findings', '',
    '**Real-data gains depend on panel and budget.** At one reading/day, static ranking and iid TS remain strongest or match the best rule on these two mature panels. At five readings/day, joint UCB is 25.1% below iid TS in astronomy, but EWMA is only about 2.6% above joint UCB. In football, temporal-only greedy is about 40.9% below iid TS and outperforms joint UCB. Thus a universal graph advantage or a universal need for filtering is not supported.', '',
    table(key), '',
    'Loss is observed-oracle log1p-view loss per selected item, averaged over the full 365-day 2025 field. All policies receive 8,784 full-history readings in 2024, with no full-field test refresh. Development parameters are frozen before test. Five TS seeds are conditional randomization, not independent Web histories. Paired block sensitivities are saved for block lengths 7, 14 and 28 days. Astronomy joint UCB versus EWMA is inconclusive when the interval crosses zero; this does not establish equivalence. Historical graphs are reused from the released study; the newly acquired series and archived source matrices have hashes.', '',
    '**Wrong-order dynamics break nominal innovation coverage.** The independent 100-world AR(20) follow-up is below: known-model failure is 1/100, versus 40/100 under the wrong model. Fitted-model failure is 5/100 and inflated-model failure is 3/100; these counts do not establish a learned-model coverage guarantee or a reliable inflation remedy. Fitted-model rows use a 365-day independent prefix; inflated rows multiply fitted innovation covariance by 1.5. The wrong model is AR(1) with diagonal innovations. Exact-model confidence is very wide (maximum arm interval widths can exceed the entire [0,1] mean range), so safety alone does not demonstrate useful decisions.', '',
    table(coverage[['mode','worlds','failures','failure_rate','ci_low','ci_high','mean_final_max_width']]), '',
    'This follow-up was selected after the four-profile screen and uses fresh seeds (offset 10,000). Pointwise nominal 95% diagnostics are recorded separately from the all-time confidence sets. The four-profile screen includes AR(1), AR(7), dense AR(20), and heterogeneous AR orders; it does not complete the heavy-tail or online-refitting agenda.', '',
    '**Bursty exposure causes irreversible wrong decisions with iid confidence.** At persistence 0.97 and 0.995, iid elimination drops the best arm in 30/100 and 47/100 worlds; innovation elimination drops it in 0/100. The 95% upper failure bound for 0/100 is 3.7%, not zero. The innovation rule does not eliminate at these horizons and has mean regret 400; iid mean regret is about 323 and 390 respectively. This is a safety/usefulness tradeoff, not evidence that the valid rule has lower average regret. Arm ordering is randomized. Horizon curves illustrate lasting loss after failure; they do not prove an asymptotic theorem.', '',
    '**Spatial correlation helps in a controlled persistent setting, with limits.** In the AR(1) screen at persistence 0.9 and graph strength 0.8, joint UCB improves on matched temporal-only UCB by 0.039 latent-oracle loss per round in the smaller-gap regime (95% paired interval: -0.070 to -0.008 for joint minus temporal-only). In the larger-gap regime the difference is -0.028 (interval: -0.062 to +0.005), which is inconclusive. Corrupting only the learner graph weakens this advantage. This is a 16-arm exploratory mechanism screen with fixed constants, not the planned general-AR factorial or a tuned comparison against all published algorithms. The final run matches the true sensor variance in the filter and scores the latent field, excluding sensor noise from the oracle.', '',
    '**The slate-contrast calculation checks out.** Across 8 configurations, simulated contrast variance is within 1.8% of the exact finite-sample prediction. Equal marginal variance and matched simultaneous AR(1) observations show the expected (1-rho) gain. Dense-Gaussian checks cover general-AR staggered and simultaneous conditional observations; arbitrary schedules must use their conditional covariance.', '',
    '**OBD is feasible for a narrow logged-feedback pilot, but hourly Gaussian filtering is poorly supported.** All three full uniform-random campaign logs were audited (2,691,861 rows). In the men’s campaign at position 1, 91.7% of training hourly item bins have no click; 60.8% of six-hour bins have no click; daily bins have only three clicks at the median. Null or noisy temporal diagnostics are retained. The executed test compares stationary/forgetting and graph/shrinkage heuristics, not a validated general-AR click filter.', '',
    table(ob), '',
    'OBD training is November 24–26 UTC, development November 27, and test November 28–30. The pilot uses 34 supported items at position 1. Every policy chooses before each hour, sees only matching randomized feedback and advances through empty bins. Most trajectories obtain only roughly 10–16 test clicks: the apparent CTR ordering is underpowered. Seed SD is conditional algorithmic variation; the date-block file is descriptive sensitivity, not a confidence guarantee for deployment. Graph transfer uses a fixed 100 pseudo-impressions and is explicitly uncertified. Real, relabelled and graph-free shrinkage controls are retained. The target is the censored learner receiving these sparse observations, not a deployed learner with full selected feedback. Position-specific IPS identity and hidden-label invariance passed.', '',
    '## What remains', '',
    '- KuaiRec chronology and reruns: raw data are absent from this checkout. No corrected KuaiRec claim is made.',
    '- AR2-p, dense general-AR correlation confirmation, heavy-tail/blocked-innovation stress tests, and practical non-oracle certificates remain outstanding.',
    '- No Retailrocket acquisition or low-rank/Web-scale claim; no latent PCS or oracle regret claim from OBD logs.',
    '- Next priority: useful learned-dynamics uncertainty and stronger rare-click estimation, then broader independently predefined panels. Keep the new evidence’s panel-dependent conclusions in the abstract.', '',
    '## Files and reproduction', '',
    '- `design.md`: protocol and explicit scope.',
    '- `results/wikipedia/`: 39,420 daily decisions, tuning records, model matrices, inflation diagnostics and paired differences.',
    '- `results/certificates*`, `false_elimination`, `factorial`, `slate`: raw runs, summaries, checks and measured runtimes.',
    '- `results/obd/`: hourly aggregates, chronology/support manifest, precision diagnostics, 10,224 decisions, IPS summaries and checks.',
    '- `results/validation.json` and `results/manifest.json`: integrity checks and source hashes.',
    '- `figures/`: standalone PNG figures.', '',
    'Run from the repository root after data acquisition:', '',
    '```sh',
    'export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1',
    'export MPLCONFIGDIR=experiments/today_2026_10_10/.mplconfig',
    '.venv/bin/python -I experiments/today_2026_10_10/code/wikipedia.py',
    '.venv/bin/python -I experiments/today_2026_10_10/code/obd.py',
    '.venv/bin/python -I experiments/today_2026_10_10/code/controlled.py coverage',
    '.venv/bin/python -I experiments/today_2026_10_10/code/controlled.py coverage --profiles ar20 --worlds 100 --seed-offset 10000',
    '.venv/bin/python -I experiments/today_2026_10_10/code/controlled.py elimination',
    '.venv/bin/python -I experiments/today_2026_10_10/code/controlled.py factorial',
    '.venv/bin/python -I experiments/today_2026_10_10/code/controlled.py slate',
    '.venv/bin/python -I experiments/today_2026_10_10/code/analyze.py',
    '```', '',
    'Source data: [OBD release](https://research.zozo.com/data.html), Saito et al. [dataset paper](https://arxiv.org/abs/2008.07146), and Wikimedia per-article pageviews. The OBD archive is CC BY 4.0; released acknowledgement is retained in `results/obd/source_readme.txt`.', '',
    'The local NumPy/Apple BLAS emitted floating-point status warnings on some matrix products. Explicit finiteness assertions and dense-equivalence checks pass; no nonfinite raw numeric result is accepted. Scientific conclusions remain bounded by the study designs and replication sizes above.']
    (HERE/'README.md').write_text('\n'.join(reports)+'\n')
    # Manifest is last so it includes the generated report.
    manifest['new_files']['README.md']=sha(HERE/'README.md');save_json(OUT/'manifest.json',manifest)
    print('validated',checks,flush=True)

if __name__=='__main__':main()
