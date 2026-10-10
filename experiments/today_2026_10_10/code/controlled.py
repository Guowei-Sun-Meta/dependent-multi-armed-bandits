import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import argparse
import time
from scipy.linalg import solve_discrete_lyapunov
from functools import lru_cache

base=source_module('released_wiki_controlled','research/gpt_sol_10_09/code/wikipedia_experiment.py')

class Model:
    def __init__(self,a,q,r=.01):
        self.a=np.asarray(a);self.n,self.p=self.a.shape;self.q=q;self.r=r
        n,p=self.n,self.p;self.f=np.zeros((n*p,n*p))
        self.f[:n]=np.hstack([np.diag(self.a[:,i]) for i in range(p)])
        if p>1:self.f[n:,:-n]=np.eye(n*(p-1))
        radius=max(abs(np.linalg.eigvals(self.f)));assert radius<1,(radius,a)
        noise=np.zeros_like(self.f);noise[:n,:n]=q
        self.gamma=solve_discrete_lyapunov(self.f,noise)
        self.gamma=(self.gamma+self.gamma.T)/2
        assert np.linalg.eigvalsh(self.gamma).min()>-1e-7

    def rows(self,x):
        shape=x.shape;rows=x.reshape(self.p,self.n,-1);out=np.empty_like(rows)
        out[0]=np.einsum('ip,pij->ij',self.a,rows)
        if self.p>1:out[1:]=rows[:-1]
        return out.reshape(shape)

class Regression:
    def __init__(self,model,alpha=.01):
        self.model=model;self.alpha=alpha;n=model.n;d=n*model.p
        self.g=np.zeros(d);self.D=np.zeros((d,n));self.P=model.gamma.copy()
        self.J=alpha*np.eye(n);self.score=np.zeros(n)
    def observe(self,a,y):
        n=self.model.n;v=np.eye(n)[a]+self.D[a];d=self.P[a,a]+self.model.r;res=y-self.g[a]
        self.J+=np.outer(v,v)/d;self.score+=v*res/d
        col=self.P[:,a].copy();self.g+=col*res/d;self.D-=np.outer(col,v)/d;self.P-=np.outer(col,col)/d
    def advance(self):
        self.g=self.model.rows(self.g[:,None]).ravel();self.D=self.model.rows(self.D)
        self.P=self.model.rows(self.model.rows(self.P).T).T
        self.P[:self.model.n,:self.model.n]+=self.model.q
    def bounds(self,delta=.05):
        n=self.model.n;inv=np.linalg.inv(self.J);m=inv@self.score
        beta=np.sqrt(max(0,np.linalg.slogdet(self.J)[1]-n*np.log(self.alpha))+2*np.log(1/delta))+np.sqrt(self.alpha*n)
        rad=beta*np.sqrt(np.maximum(np.diag(inv),0))
        assert np.isfinite(m).all() and np.isfinite(rad).all()
        return m,rad

def simulate(model,mu,T,rng,heavy=False):
    d=model.n*model.p;x=rng.multivariate_normal(np.zeros(d),model.gamma,check_valid='raise');L=np.linalg.cholesky(model.q)
    out=np.empty((T,model.n))
    for t in range(T):
        out[t]=mu+x[:model.n]+np.sqrt(model.r)*rng.normal(size=model.n)
        eps=rng.standard_t(3,size=model.n)/np.sqrt(3) if heavy else rng.normal(size=model.n)
        x=model.rows(x[:,None]).ravel();x[:model.n]+=L@eps
    assert np.isfinite(out).all()
    return out

def fit_model(prefix,order,independent=False,safety=1.):
    n=prefix.shape[1];z=prefix-prefix.mean(0)
    design=np.stack([z[order-i:len(z)-i] for i in range(1,order+1)],axis=-1);a=[];res=[]
    for i in range(n):
        X=design[:,i];target=z[order:,i];coef=np.linalg.solve(X.T@X+np.eye(order),X.T@target)
        f=np.zeros((order,order));f[0]=coef
        if order>1:f[1:,:-1]=np.eye(order-1)
        if max(abs(np.linalg.eigvals(f)))>=.99:coef*=.95/max(np.sum(abs(coef)),.95)
        a.append(coef);res.append(target-X@coef)
    q=np.cov(np.asarray(res));q=.8*q+.2*np.diag(np.diag(q))+1e-6*np.eye(n)
    if independent:q=np.diag(np.diag(q))
    return Model(np.asarray(a),q*safety)

def verify():
    rng=np.random.default_rng(SEED);a=np.tile([.4,-.1,.2],(3,1));q=np.array([[.3,.1,.04],[.1,.4,.06],[.04,.06,.2]])
    model=Model(a,q);reg=Regression(model);actions=[0,2,1,0,1,2];times=[0,0,1,3,3,4];y=rng.normal(size=6)
    for j,(action,tm) in enumerate(zip(actions,times)):
        previous=times[j-1] if j else 0
        for _ in range(tm-previous):reg.advance()
        reg.observe(action,y[j])
    cov=np.empty((6,6));X=np.eye(3)[actions]
    for i in range(6):
        for j in range(6):
            if times[i]>=times[j]:val=(np.linalg.matrix_power(model.f,times[i]-times[j])@model.gamma)[actions[i],actions[j]]
            else:val=(np.linalg.matrix_power(model.f,times[j]-times[i])@model.gamma)[actions[j],actions[i]]
            cov[i,j]=val+model.r*(i==j)
    expected=X.T@np.linalg.solve(cov,X);score=X.T@np.linalg.solve(cov,y)
    assert np.allclose(reg.J-reg.alpha*np.eye(3),expected,atol=1e-9)
    assert np.allclose(reg.score,score,atol=1e-9)
    assert not np.allclose(np.linalg.inv(q)[:2,:2],np.linalg.inv(q[:2,:2]))
    return {'dense_conditional_innovation_information':'pass','dense_conditional_score':'pass','simultaneous_partial_slate_marginal_precision':'pass','whitening_includes_sensor_noise':True}

def profile(name,n=6):
    if name=='ar1':a=np.tile([.9],(n,1))
    elif name=='ar7':
        a=np.zeros((n,7));a[:,[0,1,6]]=[.4,.1,.3]
    elif name=='ar20':
        x=np.exp(-np.arange(20)/6);a=np.tile(.92*x/x.sum(),(n,1))
    elif name=='heterogeneous':a=np.array([[.6,-.2,0],[.35,.1,.2],[0,.75,0],[.1,.4,-.1],[.7,-.3,0],[.2,0,.45]])
    else:raise ValueError(name)
    # Each arm is normalized to stationary variance 1 before spatial mixing.
    scales=[]
    for coef in a:
        f=np.zeros((len(coef),len(coef)));f[0]=coef
        if len(coef)>1:f[1:,:-1]=np.eye(len(coef)-1)
        unit=np.zeros_like(f);unit[0,0]=1;g=solve_discrete_lyapunov(f,unit);scales.append(1/np.sqrt(g[0,0]))
    C=.6*np.eye(n)+.4*np.ones((n,n));q=np.asarray(scales)[:,None]*C*np.asarray(scales)[None,:]
    return Model(a,q)

def coverage(worlds=30,T=800):
    dest=OUT/'certificates';dest.mkdir(parents=True,exist_ok=True);rows=[];start=time.perf_counter()
    for name in ['ar1','ar7','ar20','heterogeneous']:
        truth=profile(name);mu=np.linspace(.15,.75,truth.n)
        for seed in range(worlds):
            rng=np.random.default_rng(SEED+seed);prefix=simulate(truth,mu,365,rng);Y=simulate(truth,mu,T,rng)
            models={'known':truth,'fitted':fit_model(prefix,truth.p),'fitted_inflated':fit_model(prefix,truth.p,safety=1.5),'wrong_order_or_diagonal':fit_model(prefix,1,True)}
            for mode,model in models.items():
                reg=Regression(model);bad=False;count=0
                for t in range(T):
                    arm=(t//25)%truth.n;reg.observe(arm,Y[t,arm]);m,rad=reg.bounds()
                    violation=bool(np.any(np.abs(m-mu)>rad));bad|=violation;count+=violation;reg.advance()
                nominal=1.95996398454*np.sqrt(np.maximum(np.diag(np.linalg.inv(reg.J)),0))
                rows.append({'profile':name,'world':seed,'mode':mode,'horizon':T,'prefix_days':365,'bursty_block':25,'any_violation':int(bad),'violated_rounds':count,'final_max_width':float((2*rad).max()),'final_fraction_arms_outside_pointwise95':float(np.mean(np.abs(m-mu)>nominal)),'final_pointwise95_max_width':float((2*nominal).max())})
        print('coverage',name,'complete',flush=True)
    frame=pd.DataFrame(rows);frame.to_csv(dest/'runs.csv',index=False);summ=[]
    for keys,g in frame.groupby(['profile','mode']):
        k=int(g.any_violation.sum());lo,hi=wilson(k,len(g));summ.append({'profile':keys[0],'mode':keys[1],'worlds':len(g),'failures':k,'failure_rate':k/len(g),'ci_low':lo,'ci_high':hi,'mean_final_max_width':g.final_max_width.mean(),'mean_fraction_arms_outside_pointwise95':g.final_fraction_arms_outside_pointwise95.mean(),'mean_pointwise95_max_width':g.final_pointwise95_max_width.mean()})
    pd.DataFrame(summ).to_csv(dest/'summary.csv',index=False);save_json(dest/'metadata.json',{'seconds':time.perf_counter()-start,'scope':'small-world screening; anytime joint ellipsoid, fixed bursty schedule; fitted inflation is heuristic','r_obs':.01,'delta':.05,'true_means':mu.tolist(),'heavy_tails':'not_run_in_this_screen'})

def elimination(worlds=100,T=4000):
    dest=OUT/'false_elimination';dest.mkdir(parents=True,exist_ok=True);rows=[];traces=[];start=time.perf_counter()
    for phi in [.0,.97,.995]:
        model=Model(np.full((2,1),phi),(1-phi**2)*np.eye(2),r=0.)
        for seed in range(worlds):
            rng=np.random.default_rng(SEED+seed);mu=np.array([.55,.35])[rng.permutation(2)];Y=simulate(model,mu,T,rng)
            for method in ['iid','innovation']:
                counts=np.zeros(2);sums=np.zeros(2);alive=np.ones(2,bool);reg=Regression(model);wrong=False;failure_time=None;loss=0.;checkpoint={}
                for t in range(T):
                    choices=np.flatnonzero(alive);a=choices[(t//1000)%len(choices)]
                    counts[a]+=1;sums[a]+=Y[t,a]
                    if method=='iid':m=sums/np.maximum(counts,1);rad=np.sqrt(2*np.log(4*T/.05)/np.maximum(counts,1))
                    else:
                        reg.observe(a,Y[t,a]);m,rad=reg.bounds();reg.advance()
                    if counts.min()>0:
                        lower=m-rad;upper=m+rad;eliminate=alive & (upper<lower[alive].max());alive[eliminate]=False
                        assert alive.any()
                        if not alive[np.argmax(mu)] and not wrong:wrong=True;failure_time=t
                    loss+=mu.max()-mu[a]
                    if t+1 in [1000,2000,4000]:checkpoint[t+1]=loss
                rows.append({'phi':phi,'world':seed,'method':method,'wrong_elimination':int(wrong),'failure_time':failure_time,'mean_regret':loss,'best_arm':int(mu.argmax())})
                for h,v in checkpoint.items():traces.append({'phi':phi,'world':seed,'method':method,'horizon':h,'mean_regret':v})
        print('elimination',phi,'complete',flush=True)
    frame=pd.DataFrame(rows);frame.to_csv(dest/'runs.csv',index=False);pd.DataFrame(traces).to_csv(dest/'curves.csv',index=False)
    summary=[]
    for (phi,method),g in frame.groupby(['phi','method']):
        k=int(g.wrong_elimination.sum());lo,hi=wilson(k,len(g));summary.append({'phi':phi,'method':method,'worlds':len(g),'wrong_eliminations':k,'failure_rate':k/len(g),'ci_low':lo,'ci_high':hi,'mean_regret':g.mean_regret.mean()})
    pd.DataFrame(summary).to_csv(dest/'summary.csv',index=False);save_json(dest/'metadata.json',{'seconds':time.perf_counter()-start,'exposure_block':1000,'true_mean_gap':.2,'randomized_arm_order':True,'regret_comparison':'fixed batch exploration persists even after the best arm survives; loss mechanism illustration, not an optimal policy','claim':'finite-horizon evidence, not a proof of linear regret'})

def slate(worlds=20000,length=100):
    dest=OUT/'slate';dest.mkdir(parents=True,exist_ok=True);rows=[];rng=np.random.default_rng(SEED)
    for phi in [0.,.8]:
        for rho in [0.,.3,.6,.9]:
            q=(1-phi**2)*np.array([[1.,rho],[rho,1.]])
            z=rng.multivariate_normal(np.zeros(2),q/(1-phi**2),size=worlds);sumz=np.zeros_like(z)
            L=np.linalg.cholesky(q)
            for _ in range(length):sumz+=z;z=phi*z+rng.normal(size=(worlds,2))@L.T
            assert np.isfinite(sumz).all()
            empirical=float(np.var((sumz[:,0]-sumz[:,1])/length,ddof=1))
            infl=1+2*sum((1-h/length)*phi**h for h in range(1,length));exact=2*(1-rho)*infl/length
            rows.append({'phi':phi,'rho':rho,'worlds':worlds,'simultaneous_readings_per_world':2*length,'empirical_contrast_variance':empirical,'exact_finite_variance':exact,'long_run_variance':2*(1-rho)*(1+phi)/(1-phi)/length,'empirical_over_exact':empirical/exact})
    pd.DataFrame(rows).to_csv(dest/'summary.csv',index=False)

def factorial(worlds=20,T=500,n=16):
    dest=OUT/'factorial';dest.mkdir(parents=True,exist_ok=True);rows=[];start=time.perf_counter()
    W=np.zeros((n,n))
    for i in range(n):W[i,(i+1)%n]=W[(i+1)%n,i]=1
    L=np.diag(W.sum(0))-W;K=np.linalg.inv(np.eye(n)+3*L);C=K/np.sqrt(np.diag(K))[:,None]/np.sqrt(np.diag(K))[None,:]
    perm=np.random.default_rng(SEED).permutation(n);corrupt=C[np.ix_(perm,perm)]
    policies=['iid_ts','discounted_ts','ar_greedy','ar_ucb','st_greedy','st_ucb','corrupt_ucb']
    for phi in [0.,.5,.9]:
        for rho in [0.,.4,.8]:
            cov=(1-rho)*np.eye(n)+rho*C;q=(1-phi**2)*cov;model=Model(np.full((n,1),phi),q)
            for gap in [.25,1.]:
                mu=np.linspace(0,gap,n)
                for seed in range(worlds):
                    rng=np.random.default_rng(SEED+seed);Y=simulate(model,mu,T+120,rng)
                    for policy in policies:
                        kind=policy.split('_')[0];learnerQ=q if kind=='st' else (1-phi**2)*((1-rho)*np.eye(n)+rho*corrupt) if kind=='corrupt' else np.diag(np.diag(q))
                        engine=base.Filter(np.array([phi]),learnerQ);engine.m[:n]=mu.mean()
                        for t in range(120):
                            for a in range(n):engine.update(a,Y[t,a])
                            engine.propagate()
                        counts=np.full(n,120.);sums=Y[:120].sum(0);var=Y[:120].var(0);prng=np.random.default_rng(SEED+seed);loss=0.;mloss=0.
                        for t in range(120,len(Y)):
                            if kind in ['iid','discounted']:score=sums/counts+np.sqrt(var/counts)*prng.normal(size=n)
                            else:
                                f,c=engine.forecast();score=f+(np.sqrt(np.maximum(np.diag(c-engine.q),0)) if policy.endswith('ucb') else 0)
                            a=int(np.argmax(score));loss+=Y[t].max()-Y[t,a];mloss+=mu.max()-mu[a]
                            if kind=='discounted':counts*=.98;sums*=.98
                            counts[a]+=1;sums[a]+=Y[t,a]
                            if kind not in ['iid','discounted']:engine.update(a,Y[t,a]);engine.propagate()
                        rows.append({'phi':phi,'rho':rho,'level_spread':gap,'world':seed,'policy':policy,'oracle_loss_per_round':loss/T,'mean_pseudo_regret_per_round':mloss/T,'horizon':T,'prefix_readings':120*n})
            print('factorial',phi,rho,'complete',flush=True)
    frame=pd.DataFrame(rows);frame.to_csv(dest/'runs.csv',index=False)
    frame.groupby(['phi','rho','level_spread','policy'])[['oracle_loss_per_round','mean_pseudo_regret_per_round']].mean().reset_index().to_csv(dest/'summary.csv',index=False)
    pairs=[]
    for keys,g in frame.groupby(['phi','rho','level_spread']):
        tab=g.pivot(index='world',columns='policy',values='oracle_loss_per_round')
        for policy,ref in [('st_ucb','ar_ucb'),('st_greedy','ar_greedy'),('st_ucb','corrupt_ucb'),('st_ucb','discounted_ts')]:
            m,lo,hi=interval(tab[policy]-tab[ref]);pairs.append({'phi':keys[0],'rho':keys[1],'level_spread':keys[2],'policy':policy,'reference':ref,'difference':m,'ci_low':lo,'ci_high':hi,'worlds':worlds})
    pd.DataFrame(pairs).to_csv(dest/'paired.csv',index=False);save_json(dest/'metadata.json',{'seconds':time.perf_counter()-start,'arms':n,'truth_fixed_across_policies':True,'stationary_marginal_variance':1.,'scope':'AR(1) mechanism screen; general-AR extension outstanding','ucb_multiplier':1.,'discount':.98,'tuning':'fixed pilot constants, no per-cell optimization','corruption':'fixed degree-preserving node relabeling of cycle graph; record actual changed edges','changed_edge_fraction':float(np.sum((W>0)!=(W[np.ix_(perm,perm)]>0))/2/W.sum())})

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('study',choices=['coverage','elimination','slate','factorial','verify']);ap.add_argument('--worlds',type=int);ap.add_argument('--horizon',type=int);args=ap.parse_args()
    checks=verify();save_json(OUT/'controlled_checks.json',checks)
    if args.study=='verify':print(checks)
    elif args.study=='coverage':coverage(args.worlds or 30,args.horizon or 800)
    elif args.study=='elimination':elimination(args.worlds or 100,args.horizon or 4000)
    elif args.study=='slate':slate()
    elif args.study=='factorial':factorial(args.worlds or 20,args.horizon or 500)
