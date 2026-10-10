import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import copy
import time

base=source_module('released_wiki','research/gpt_sol_10_09/code/wikipedia_experiment.py')

def run_policy(y,weekdays,fit,engine,policy,param,seed,batch,prefix):
    rng=np.random.default_rng(SEED+seed);engine=copy.deepcopy(engine)
    de=y-fit['season'][weekdays]; hist=de[:prefix].copy()
    counts=np.full(y.shape[1],float(prefix));sums=hist.sum(0); ew=hist[-1].copy(); last=hist[-1].copy()
    var=np.maximum(hist.var(0),1e-6); records=[];n=y.shape[1]
    for t in range(prefix,len(y)):
        season=fit['season'][weekdays[t]]
        if policy=='static':score=hist[:prefix].mean(0)+season
        elif policy=='last':score=last+season
        elif policy=='seasonal':score=hist[t-7]+season
        elif policy=='ewma':score=ew+season
        elif policy.startswith(('iid_','discounted_','window_')):
            if policy.startswith('window_'):
                h=hist[-int(param):];c=np.isfinite(h).sum(0);s=np.nansum(h,axis=0)
            else:c=counts;s=sums
            mean=np.divide(s,c,out=hist[:prefix].mean(0).copy(),where=c>0)
            sd=np.sqrt(var/np.maximum(c,1))
            if policy.endswith('ts'):score=mean+sd*rng.standard_normal(n)+season
            else:score=mean+np.sqrt(2*np.log(t+2))*sd+season
        else:
            f,cov=engine.forecast();score=f+season
            if policy.endswith('ucb'):score+=param*np.sqrt(np.maximum(np.diag(cov-engine.q),0))
        chosen=np.argsort(-score,kind='stable')[:batch]
        # No current reward is accessed until the full slate is chosen.
        loss=float(np.sort(y[t])[-batch:].sum()-y[t,chosen].sum())/batch
        assert loss>=-1e-10
        if policy.startswith('discounted_'):counts*=param;sums*=param
        counts[chosen]+=1;sums[chosen]+=de[t,chosen]
        last[chosen]=de[t,chosen];ew[chosen]=(1-param)*ew[chosen]+param*de[t,chosen] if policy=='ewma' else ew[chosen]
        predicted=engine.forecast()[0] if policy.endswith(('greedy','ucb')) else hist[-7].copy() if policy=='seasonal' else np.full(n,np.nan)
        # Seasonal naive uses recursive seasonal forecasts for unobserved lags.
        if policy=='seasonal':recorded=predicted.copy()
        else:recorded=np.full(n,np.nan)
        recorded[chosen]=de[t,chosen]
        if policy.endswith(('greedy','ucb')):
            for i in chosen:engine.update(int(i),de[t,i])
            engine.propagate()
        hist=np.vstack((hist,recorded))
        records.append({'date_index':t,'policy':policy,'seed':seed,'batch':batch,'loss_per_slot':loss,'chosen':','.join(map(str,chosen))})
    return records

def main():
    start=time.perf_counter();dest=OUT/'wikipedia';dest.mkdir(parents=True,exist_ok=True)
    requests=json.loads((HERE/'data/wikipedia/requests.json').read_text()); acquired=[]; allrows=[]; tuning=[];metadata={}
    original=json.loads((ROOT/'research/gpt_sol_10_09/results/wikipedia/metadata.json').read_text())
    policies={'static':[0],'last':[0],'seasonal':[0],'ewma':[.05,.2,.5],'iid_ucb':[0],'iid_ts':[0],'discounted_ucb':[.95,.98,.995],'discounted_ts':[.95,.98,.995],'window_ucb':[14,30,90],'window_ts':[14,30,90],'ar_greedy':[0],'ar_ucb':[.5,1,2],'st_greedy':[0],'st_ucb':[.5,1,2],'factor_greedy':[0]}
    checks=base.verify()
    for panel in ['astronomy','football']:
        entries=[e for e in requests if e['panel']==panel and (ROOT/e['path']).exists()]
        # Only complete 24-arm panels enter the primary historical replication.
        if len(entries)!=24:
            metadata[panel]={'status':'not_run_incomplete_acquisition','available':len(entries),'required':24};continue
        vals=[];date_arrays=[]
        for e in entries:
            x=json.loads((ROOT/e['path']).read_text())['items'];date_arrays.append([a['timestamp'][:8] for a in x]);vals.append([a['views'] for a in x]);acquired.append({**e,'sha256':sha(ROOT/e['path'])})
        assert all(x==date_arrays[0] for x in date_arrays)
        dates=pd.to_datetime(date_arrays[0],format='%Y%m%d');assert len(dates)==731
        raw=np.asarray(vals,float).T;y=np.log1p(raw);weekdays=dates.dayofweek.to_numpy()
        modelpath=ROOT/f'research/gpt_sol_10_09/results/wikipedia/{panel}_ar7_model.npz';archive=np.load(modelpath)
        w=archive['graph'];wr=archive['rewired_graph']; specs,ll=base.select_covariances(y[:366],weekdays[:366],w,wr,7)
        # Covariance hyperparameters themselves use a development score. No test values.
        devfit=base.fit_ar(y[:274],weekdays[:274],7);fit=base.fit_ar(y[:366],weekdays[:366],7)
        dev_engines={k:base.burnin(y[:274],weekdays[:274],devfit,base.covariance(devfit,w,k,**specs[k])) for k in ['ar','st','factor']}
        engines={k:base.burnin(y[:366],weekdays[:366],fit,base.covariance(fit,w,k,**specs[k])) for k in ['ar','st','factor']}
        metadata[panel]={'status':'complete','titles':[e['title'] for e in entries],'graph_source_sha256':sha(modelpath),'graph_cutoff':'before 2024, as reconstructed by released study','initial_readings':366*24,'ar_coefficients':fit['a'].tolist(),'covariance_specs':specs,'covariance_development_scores':ll,'spectral_radius':fit['radius']}
        np.savez_compressed(dest/f'{panel}_models.npz',a=fit['a'],season=fit['season'],graph=w,**{f'Q_{k}':v.q for k,v in engines.items()})
        for batch in [1,5]:
            for policy,grid in policies.items():
                kind=policy.split('_')[0] if policy.split('_')[0] in engines else 'ar'
                scores=[]
                for param in grid:
                    losses=[]
                    # Tune stochastic rules on three separate fixed development seeds.
                    for seed in (range(3) if policy.endswith('ts') else [0]):
                        r=run_policy(y[:366],weekdays[:366],devfit,dev_engines[kind],policy,param,1000+seed,batch,274)
                        losses.append(np.mean([x['loss_per_slot'] for x in r]))
                    score=float(np.mean(losses));scores.append((score,param));tuning.append({'panel':panel,'batch':batch,'policy':policy,'parameter':param,'dev_loss':score})
                chosen=min(scores)[1]
                for seed in (range(5) if policy.endswith('ts') else [0]):
                    rows=run_policy(y,weekdays,fit,engines[kind],policy,chosen,seed,batch,366)
                    for r in rows:r.update(panel=panel,date=str(dates[r['date_index']].date()),test_day=r['date_index']-366,parameter=chosen)
                    allrows.extend(rows)
                print('wiki',panel,batch,policy,'parameter',chosen,flush=True)
        # Policy-free block-mean variance diagnostic uses fitted stationary residual covariance.
        from scipy.linalg import solve_discrete_lyapunov
        a=fit['a'];f=np.zeros((7,7));f[0]=a;f[1:,:-1]=np.eye(6);unit=np.zeros((7,7));unit[0,0]=1
        g=solve_discrete_lyapunov(f,unit);aut=[(np.linalg.matrix_power(f,h)@g)[0,0]/g[0,0] for h in range(14)]
        z=y-fit['season'][weekdays]-fit['mu'];infl=[]
        for b in [1,3,7,14]:
            # Nonoverlapping block estimates are descriptive on this observed drifting field.
            test=z[366:];blocks=test[:len(test)//b*b].reshape(-1,b,24).mean(1)
            ratio=blocks.var(0,ddof=1)/(test.var(0,ddof=1)/b)
            pred=1+2*sum((1-h/b)*aut[h] for h in range(1,b))
            for i in range(24):infl.append({'panel':panel,'item':i,'block_days':b,'predicted_inflation':pred,'observed_inflation':ratio[i]})
        pd.DataFrame(infl).to_csv(dest/f'{panel}_inflation.csv',index=False)
    if not allrows:raise RuntimeError('No complete historical panel available')
    daily=pd.DataFrame(allrows);daily.to_csv(dest/'daily.csv',index=False)
    runs=daily.groupby(['panel','batch','policy','seed']).loss_per_slot.mean().reset_index();runs.to_csv(dest/'runs.csv',index=False)
    runs.groupby(['panel','batch','policy']).loss_per_slot.mean().reset_index().to_csv(dest/'summary.csv',index=False)
    daily['window']=np.minimum(daily.test_day//90,4)
    daily.groupby(['panel','batch','policy','window']).loss_per_slot.mean().reset_index().to_csv(dest/'windows.csv',index=False)
    pd.DataFrame(tuning).to_csv(dest/'development.csv',index=False)
    # Moving block bootstrap of seed-averaged paired daily losses; conditional on one panel.
    paired=[];rng=np.random.default_rng(SEED)
    for (panel,batch),grp in daily.groupby(['panel','batch']):
        tab=grp.groupby(['test_day','policy']).loss_per_slot.mean().unstack('policy')
        for reference in ['iid_ts','discounted_ts','ar_greedy']:
            for policy in tab:
                if policy==reference:continue
                x=(tab[policy]-tab[reference]).to_numpy();n=len(x)
                for length in [7,14,28]:
                    samples=[]
                    for _ in range(1000):
                        starts=rng.integers(0,n-length+1,size=int(np.ceil(n/length)));idx=(starts[:,None]+np.arange(length)).ravel()[:n];samples.append(x[idx].mean())
                    lo,hi=np.quantile(samples,[.025,.975]);paired.append({'panel':panel,'batch':batch,'policy':policy,'reference':reference,'block_days':length,'difference':float(x.mean()),'ci_low':lo,'ci_high':hi,'scope':'conditional date-block sensitivity; one fixed panel'})
    pd.DataFrame(paired).to_csv(dest/'paired.csv',index=False)
    metadata['seconds']=time.perf_counter()-start;metadata['runs']=len(runs);metadata['daily_records']=len(daily)
    save_json(dest/'metadata.json',metadata);save_json(dest/'acquisition.json',acquired)
    checks.update({'batch_selected_before_feedback':'pass_by_interface','nonnegative_oracle_loss':'pass','future_data_in_fit':'absent_by_prefix_slicing','full_field_refresh_during_test':'none','tuning':'2024 development only; 3 stochastic development seeds','scope':'conditional historical-panel evidence'})
    save_json(dest/'checks.json',checks)

if __name__=='__main__':main()
