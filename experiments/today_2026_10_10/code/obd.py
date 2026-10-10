import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *
import time
import zipfile

def ingest():
    start=time.perf_counter(); archive=ROOT/'data/obd/open_bandit_dataset.zip'
    dest=OUT/'obd'; dest.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((dest/'manifest.json').read_text()) if (dest/'manifest.json').exists() else {'archive_sha256':sha(archive),'source':'https://research.zozo.com/data_release/open_bandit_dataset.zip','license':'CC BY 4.0','campaigns':{}}
    with zipfile.ZipFile(archive) as z:
        (dest/'source_readme.txt').write_bytes(z.read('open_bandit_dataset/README'))
        for campaign in ['men','women','all']:
            member=f'open_bandit_dataset/random/{campaign}/{campaign}.csv'
            if (dest/f'{campaign}_hourly.csv').exists(): continue
            accum=[]; cohort=[]; count=0; invalid=0; minp=1.;maxp=0.;mind=None;maxd=None; ids=set(); positions=set()
            with z.open(member) as f:
                for chunk in pd.read_csv(f,usecols=['timestamp','item_id','position','click','propensity_score','user_feature_0'],chunksize=100000):
                    dates=pd.to_datetime(chunk.timestamp,utc=True,format='mixed')
                    chunk['hour']=dates.dt.floor('h'); chunk['day']=dates.dt.floor('D')
                    invalid+=int((~chunk.click.isin([0,1]) | (chunk.propensity_score<=0) | (chunk.propensity_score>1)).sum())
                    count+=len(chunk); ids.update(chunk.item_id.unique());positions.update(chunk.position.unique())
                    minp=min(minp,float(chunk.propensity_score.min()));maxp=max(maxp,float(chunk.propensity_score.max()))
                    mind=dates.min() if mind is None else min(mind,dates.min());maxd=dates.max() if maxd is None else max(maxd,dates.max())
                    chunk['ips_click']=chunk.click/chunk.propensity_score
                    accum.append(chunk.groupby(['hour','item_id','position']).agg(impressions=('click','size'),clicks=('click','sum'),ips_clicks=('ips_click','sum')).reset_index())
                    # Predetermined training dates, no current/test response data in graph.
                    tr=chunk[chunk.day<pd.Timestamp('2019-11-27',tz='UTC')]
                    cohort.append(tr.groupby(['item_id','position','user_feature_0']).agg(impressions=('click','size'),clicks=('click','sum')).reset_index())
            frame=pd.concat(accum).groupby(['hour','item_id','position'],as_index=False)[['impressions','clicks','ips_clicks']].sum()
            frame.to_csv(dest/f'{campaign}_hourly.csv',index=False)
            pd.concat(cohort).groupby(['item_id','position','user_feature_0'],as_index=False)[['impressions','clicks']].sum().to_csv(dest/f'{campaign}_training_cohorts.csv',index=False)
            manifest['campaigns'][campaign]={'rows':count,'items':sorted(map(int,ids)),'positions':sorted(map(int,positions)),'min_timestamp':str(mind),'max_timestamp':str(maxd),'min_propensity':minp,'max_propensity':maxp,'invalid_rows':invalid,'member_bytes':z.getinfo(member).file_size}
            print('ingested',campaign,count,'rows',flush=True)
    manifest['seconds']=time.perf_counter()-start
    save_json(dest/'manifest.json',manifest)

def matrices(frame,pos=1):
    frame=frame[frame.position==pos].copy(); frame.hour=pd.to_datetime(frame.hour,utc=True)
    dates=pd.date_range(frame.hour.min(),frame.hour.max(),freq='h'); ids=sorted(frame.item_id.unique())
    arrays=[frame.pivot(index='hour',columns='item_id',values=k).reindex(index=dates,columns=ids).fillna(0).to_numpy(float) for k in ['impressions','clicks','ips_clicks']]
    return dates,ids,arrays

def choose(policy,n,s,rng,step,graph=None):
    if policy=='random':return int(rng.integers(len(n)))
    if policy=='static':return int(np.argmax((s+.5)/(n+1)))
    if policy.endswith('ts'):
        if policy in ['graph_ts','rewired_ts','shrink_ts']:
            rates=(s+.5)/(n+1);prior=np.sum(graph*rates[None,:],axis=1)
            assert np.isfinite(prior).all() and ((prior>=0)&(prior<=1)).all()
            # Fixed 100 pseudo-impression transfer; empirical heuristic, not certificate.
            return int(np.argmax(rng.beta(s+.5+100*prior,n-s+.5+100*(1-prior))))
        return int(np.argmax(rng.beta(s+.5,n-s+.5)))
    return int(np.argmax((s+.5)/(n+1)+np.sqrt(2*np.log(step+2)/np.maximum(n,1))))

def logged_run(policy,seed,N,S,IPS,dates,graph,discount=.98):
    n=N[:72].sum(0);s=S[:72].sum(0); rows=[];rng=np.random.default_rng(SEED+seed)
    prefix_n=n.copy();prefix_s=s.copy()
    # First 3 days initialize; development day unused by adaptive test learners.
    # The test starts with training counts for every policy; physical advance through day 4 is recorded.
    if policy=='discounted_ts':n*=discount**24;s*=discount**24
    if policy=='window_ts':n=np.zeros_like(n);s=np.zeros_like(s)
    for t in range(96,len(N)):
        a=choose(policy,prefix_n if policy=='static' else n,prefix_s if policy=='static' else s,rng,t,graph)
        total=N[t].sum(); match=N[t,a]; clicks=S[t,a]
        rows.append({'campaign':'men','position':1,'policy':policy,'seed':seed,'hour':str(dates[t]),'item_index':a,'eligible_impressions':total,'matching_impressions':match,'matching_clicks':clicks,'ips_numerator':IPS[t,a]})
        if policy=='discounted_ts':n*=discount;s*=discount
        if policy=='window_ts':
            # Only allowed selected-feedback histories enter the window.
            if len(rows)>24:
                old=rows[-25]; n[old['item_index']]-=old['matching_impressions'];s[old['item_index']]-=old['matching_clicks']
        if policy!='static':n[a]+=match;s[a]+=clicks
    return rows

def run():
    dest=OUT/'obd'; audit=[];support=[];diagnostics=[]
    for campaign in ['men','women','all']:
        frame=pd.read_csv(dest/f'{campaign}_hourly.csv')
        for pos in sorted(frame.position.unique()):
            dates,ids,(N,S,IPS)=matrices(frame,pos)
            # Prefix-only Pearson residual correlations are noisy diagnostics, not evidence of AR dynamics.
            rates=(S[:72].sum(0)+.5)/(N[:72].sum(0)+1)
            resid=np.divide(S[:72]-N[:72]*rates,np.sqrt(np.maximum(N[:72]*rates*(1-rates),1e-9)),out=np.zeros_like(S[:72]),where=N[:72]>0)
            lag=[]
            for i in range(len(ids)):
                valid=(N[:71,i]>0)&(N[1:72,i]>0)
                if valid.sum()>10 and resid[:-1,i][valid].std()>0 and resid[1:,i][valid].std()>0:lag.append(np.corrcoef(resid[:-1,i][valid],resid[1:,i][valid])[0,1])
            se2=rates*(1-rates)/np.maximum(N[:72].sum(0),1)
            diagnostics.append({'campaign':campaign,'position':pos,'median_hourly_lag1_pearson_residual_correlation':float(np.median(lag)),'training_rate_spread_sd':float(rates.std()),'median_training_rate_sampling_se':float(np.median(np.sqrt(se2))),'method_of_moments_between_item_variance':float(max(0,rates.var()-se2.mean())),'scope':'prefix only; sparse Pearson correlations cannot validate an AR model'})
            for width in [1,6,24]:
                n=N[:72].reshape(-1,width,len(ids)).sum(1);s=S[:72].reshape(-1,width,len(ids)).sum(1)
                audit.append({'campaign':campaign,'position':pos,'bin_hours':width,'items':len(ids),'training_item_bins':n.size,'zero_click_fraction':float(np.mean(s==0)),'zero_impression_fraction':float(np.mean(n==0)),'median_clicks':float(np.median(s)),'median_impressions':float(np.median(n)),'fraction_at_least_5_clicks':float(np.mean(s>=5))})
            for i,item in enumerate(ids):
                support.append({'campaign':campaign,'position':pos,'item_id':item,'train_impressions':N[:72,i].sum(),'train_clicks':S[:72,i].sum(),'test_impressions':N[96:,i].sum(),'test_clicks':S[96:,i].sum()})
    pd.DataFrame(audit).to_csv(dest/'observation_precision.csv',index=False);pd.DataFrame(support).to_csv(dest/'item_support.csv',index=False);pd.DataFrame(diagnostics).to_csv(dest/'diagnostics.csv',index=False)
    dates,ids,(N,S,IPS)=matrices(pd.read_csv(dest/'men_hourly.csv'))
    assert len(dates)==168 and len(ids)==34
    c=pd.read_csv(dest/'men_training_cohorts.csv');c=c[c.position==1]
    cn=c.pivot(index='item_id',columns='user_feature_0',values='impressions').reindex(ids).fillna(0).to_numpy()
    cs=c.pivot(index='item_id',columns='user_feature_0',values='clicks').reindex(ids).fillna(0).to_numpy()
    profiles=(cs+.5)/(cn+100);dist=((profiles[:,None]-profiles[None,:])**2).sum(-1)
    graph=np.zeros_like(dist)
    for i in range(len(ids)):graph[i,np.argsort(dist[i])[1:6]]=1
    graph=np.maximum(graph,graph.T);graph/=np.maximum(graph.sum(1,keepdims=True),1)
    np.savez_compressed(dest/'training_graph.npz',graph=graph,item_ids=ids,profiles=profiles)
    records=[]
    permutation=np.random.default_rng(SEED).permutation(len(ids));rewired=graph[np.ix_(permutation,permutation)]
    for policy in ['static','random','ts','discounted_ts','window_ts','ucb','graph_ts','rewired_ts','shrink_ts']:
        used_graph=rewired if policy=='rewired_ts' else np.full_like(graph,1/len(ids)) if policy=='shrink_ts' else graph
        for seed in ([0] if policy in ['static','ucb'] else range(20)):
            records.extend(logged_run(policy,seed,N,S,IPS,dates,used_graph))
    daily=pd.DataFrame(records);daily.to_csv(dest/'decisions.csv',index=False)
    runs=daily.groupby(['policy','seed']).agg(ips_numerator=('ips_numerator','sum'),eligible_impressions=('eligible_impressions','sum'),matching_impressions=('matching_impressions','sum'),matching_clicks=('matching_clicks','sum')).reset_index()
    runs['ips_ctr']=runs.ips_numerator/runs.eligible_impressions;runs['match_fraction']=runs.matching_impressions/runs.eligible_impressions
    runs.to_csv(dest/'runs.csv',index=False)
    # With uniform propensities weights are constant; ESS among matching records equals their count.
    summary=runs.groupby('policy').agg(mean_ips_ctr=('ips_ctr','mean'),seed_sd=('ips_ctr','std'),mean_matches=('matching_impressions','mean'),mean_clicks=('matching_clicks','mean')).reset_index()
    summary.to_csv(dest/'summary.csv',index=False)
    # Hidden current/nonmatching labels never enter choose; explicitly perturb them and replay.
    r0=logged_run('ts',0,N,S,IPS,dates,graph); hiddenS=S.copy(); hiddenIPS=IPS.copy()
    for t,row in zip(range(96,len(N)),r0):
        mask=np.arange(len(ids))!=row['item_index'];hiddenS[t,mask]=N[t,mask];hiddenIPS[t,mask]=12345
    r1=logged_run('ts',0,N,hiddenS,hiddenIPS,dates,graph)
    assert [r['item_index'] for r in r0]==[r['item_index'] for r in r1]
    rng=np.random.default_rng(SEED);a=rng.integers(4,size=200000);y=rng.binomial(1,np.array([.1,.2,.3,.4])[a]);estimate=np.mean((a==2)*y*4)
    assert abs(estimate-.3)<.01
    N0=N.copy();S0=S.copy();I0=IPS.copy();N0[100]=0;S0[100]=0;I0[100]=0
    empty=logged_run('discounted_ts',0,N0,S0,I0,dates,graph)
    assert len(empty)==72 and empty[4]['eligible_impressions']==0
    save_json(dest/'checks.json',{'hidden_nonmatching_labels':'pass','known_counterfactual_ips':'pass','ips_simulation_estimate':estimate,'empty_bin_time_advance':'pass','utc_hours':168,'all_items_positive_training_exposure':bool((N[:72].sum(0)>0).all()),'gaussian_temporal_filter':'deferred_pending_precision: primary results are stationary/forgetting censored learners','seed_intervals':'conditional randomization only; no population confidence claim','training_hours':72,'development_hours':24,'test_hours':72,'training_impressions':int(N[:72].sum()),'item_ids':ids})
    print(summary.to_string(index=False),flush=True)

if __name__=='__main__':
    ingest();run()
