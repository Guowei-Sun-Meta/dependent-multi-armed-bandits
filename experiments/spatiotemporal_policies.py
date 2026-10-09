"""Exact UCB/Thompson-style policies for fixed-mean spatial AR(p) bandits.

Run with the workspace scientific environment:
 OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/spatiotemporal_policies.py --verify
 OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/spatiotemporal_policies.py --runs 32 --horizon 1000 --jobs 4

Physical means are deterministic and identical across all noise replicates.
Gaussian mean draws are algorithmic uncertainty draws, never environment draws.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import lru_cache
import json
import math
from pathlib import Path
import time
import zlib

import numpy as np
from scipy.linalg import solve_discrete_lyapunov

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT/"research"/"spatiotemporal_bandits"/"results"/"policies_ar20"
ALPHA, LAMBDA, UCB_SCALE, TS_SCALE = 0.1, 0.5, 0.7, 1.0
OBS_VARIANCE, NORM_BOUND, ENERGY_BOUND = 0.09, 6.0, 3.0
SEED = 20261009
CONFIGS = ("persistent", "weak", "seasonal", "heterogeneous", "no_spatial")
LEARNING = ("iid_ucb", "iid_ts", "ar_state_ucb", "ar_state_ts",
            "joint_mean_ucb", "joint_mean_ts", "joint_mean_ucb_cert",
            "joint_state_ucb", "joint_state_ts", "joint_predictive_ucb", "joint_predictive_ts",
            "joint_lucb", "joint_tt_ts",
            "round_robin")
BENCHMARKS = ("known_mean_greedy", "mean_oracle", "past_state_genie", "state_oracle")


def grid_laplacian(side):
    n = side*side
    w = np.zeros((n,n))
    for r in range(side):
        for c in range(side):
            i=r*side+c
            if r+1<side:
                w[i,i+side]=w[i+side,i]=1
            if c+1<side:
                w[i,i+1]=w[i+1,i]=1
    return np.diag(w.sum(axis=1))-w


def fixed_means(side):
    yy,xx=np.meshgrid(np.linspace(0,1,side),np.linspace(0,1,side),indexing="ij")
    mu=(np.exp(-((xx-.73)**2+(yy-.28)**2)/.075)
        +.55*np.exp(-((xx-.22)**2+(yy-.76)**2)/.055)+.06*xx).ravel()
    mu=(mu-mu.min())/(mu.max()-mu.min())
    best=int(np.argmax(mu))
    second=np.partition(mu,-2)[-2]
    mu[best]+=max(0.0,.20-(mu[best]-second))
    return mu


def dense_coefficients(p, total, tau=6.0, alternating=False):
    w=np.exp(-np.arange(1,p+1)/tau)
    if alternating:
        w*=(-1.0)**np.arange(1,p+1)
    return total*w/np.abs(w).sum()


def companion(a):
    p=len(a)
    f=np.zeros((p,p)); f[0]=a
    f[1:,:-1]=np.eye(p-1)
    return f


class Model:
    """Finite AR profile bank; all arms may have different known filters."""
    def __init__(self, config, side=10, p=20, horizon=2000):
        self.config,self.n,self.p,self.horizon=config,side*side,p,horizon
        self.l=grid_laplacian(side); self.mu=fixed_means(side)
        assert np.linalg.norm(self.mu)<=NORM_BOUND
        assert self.mu@self.l@self.mu<=ENERGY_BOUND**2
        c=np.linalg.inv(np.eye(self.n)+3*self.l)
        c/=np.sqrt(np.diag(c))[:,None]*np.sqrt(np.diag(c))[None,:]
        if config=="no_spatial":
            c=np.eye(self.n)
        self.spatial=c
        if config=="seasonal":
            a=np.zeros(p);a[-1]=.85
            profiles=[a]
        elif config=="weak":
            profiles=[dense_coefficients(p,.35)]
        elif config=="heterogeneous":
            profiles=[dense_coefficients(p,.95),
                      dense_coefficients(p,.65,3),
                      dense_coefficients(p,.80,6,alternating=True)]
        else:
            profiles=[dense_coefficients(p,.95)]
        self.groups=np.arange(self.n)%len(profiles)
        self.profiles=np.array(profiles)
        self.coefficients=self.profiles[self.groups]
        fs=[companion(a) for a in profiles]
        for f in fs:
            assert np.max(np.abs(np.linalg.eigvals(f)))<1
        unit=np.zeros((p,p));unit[0,0]=1
        innovation_scales=np.array([1/solve_discrete_lyapunov(f,unit)[0,0] for f in fs])
        self.profile_q=innovation_scales
        qarm=innovation_scales[self.groups]
        self.q=c*np.sqrt(qarm[:,None]*qarm[None,:])
        self.lq=np.linalg.cholesky(self.q)
        count=len(profiles)
        self.cross=np.empty((count,count,p,p))
        self.temporal=np.empty((count,count,horizon+1))
        for g in range(count):
            for h in range(count):
                # Row-vectorization of Gamma_gh = F_g Gamma_gh F_h' + E q E'.
                rhs=(unit*np.sqrt(innovation_scales[g]*innovation_scales[h])).ravel()
                gamma=np.linalg.solve(np.eye(p*p)-np.kron(fs[g],fs[h]),rhs).reshape(p,p)
                self.cross[g,h]=gamma
                current=gamma.copy()
                for lag in range(horizon+1):
                    self.temporal[g,h,lag]=current[0,0]
                    current=fs[g]@current
        self.k0=self.spatial*self.temporal[self.groups[:,None],self.groups[None,:],0]
        self.h=ALPHA*np.eye(self.n)+LAMBDA*self.l
        self.v0=np.linalg.inv(self.h)
        self.initial_factor=None
        if count>1:
            blocks=self.cross[self.groups[:,None],self.groups[None,:]]*c[:,:,None,None]
            gamma=blocks.transpose(2,0,3,1).reshape(p*self.n,p*self.n)
            self.initial_factor=np.linalg.cholesky((gamma+gamma.T)/2)
        else:
            self.lag_factor=np.linalg.cholesky(self.cross[0,0])
            self.spatial_factor=np.linalg.cholesky(c)

    def kernel(self, t, actions):
        if len(actions)==0:
            return np.empty((self.n,0))
        times=np.arange(len(actions))
        return (self.spatial[:,actions]*self.temporal[
            self.groups[:,None],self.groups[np.asarray(actions)][None,:],(t-times)[None,:]])

    def initial_lags(self,rng):
        if self.initial_factor is not None:
            return (self.initial_factor@rng.standard_normal(self.p*self.n)).reshape(self.p,self.n)
        return self.lag_factor@rng.standard_normal((self.p,self.n))@self.spatial_factor.T

    def world(self, seed):
        rng=np.random.default_rng(seed)
        lags=self.initial_lags(rng)  # Complete state just before the first decision.
        field=np.empty((self.horizon,self.n))
        past_prediction=np.empty_like(field)
        for t in range(self.horizon):
            prediction=np.sum(self.coefficients.T*lags,axis=0)
            current=prediction+self.lq@rng.standard_normal(self.n)
            past_prediction[t]=self.mu+prediction
            field[t]=self.mu+current
            lags[1:]=lags[:-1].copy();lags[0]=current
        noise=rng.normal(0,np.sqrt(OBS_VARIANCE),field.shape)
        return field,noise,past_prediction

    def metadata(self):
        return {"config":self.config,"arms":self.n,"orders":[self.p]*self.n,
                "fixed_means":self.mu.tolist(),"best_mean_arm":int(np.argmax(self.mu)),
                "best_mean_gap":float(np.sort(self.mu)[-1]-np.sort(self.mu)[-2]),
                "mean_norm":float(np.linalg.norm(self.mu)),
                "mean_graph_energy":float(self.mu@self.l@self.mu),
                "profiles":self.profiles.tolist(),"profile_assignment":self.groups.tolist(),
                "innovation_scales":self.profile_q.tolist(),
                "innovation_covariance":self.q.tolist(),
                "stationary_current_covariance":self.k0.tolist()}


@lru_cache(maxsize=1)
def get_model(config,side,p,horizon):
    return Model(config,side,p,horizon)


class Likelihood:
    """Exact selected-observation covariance whitening, without state truncation."""
    def __init__(self, model, known_mean=False):
        self.model,self.n,self.capacity=model,model.n,model.horizon
        self.t=0;self.actions=np.empty(self.capacity,dtype=int)
        self.y=np.empty(self.capacity)
        self.a=np.zeros((self.capacity,self.capacity))
        self.m=np.zeros(self.n);self.v=model.v0.copy()
        self.logdet_ratio=0.0;self.known_mean=known_mean
        self.cached=None

    def mean(self):
        return self.model.mu if self.known_mean else self.m

    def forecast(self, full_cov=False, design=False):
        k=self.model.kernel(self.t,self.actions[:self.t])
        weights=k@self.a[:self.t,:self.t]
        mu=self.mean()
        forecast=mu+weights@(self.y[:self.t]-mu[self.actions[:self.t]])
        noise_diag=np.diag(self.model.k0)-np.sum(weights*k,axis=1)
        w=np.eye(self.n)
        if not self.known_mean and self.t:
            for i in range(self.n):
                w[i]-=np.bincount(self.actions[:self.t],weights=weights[i],minlength=self.n)
        b=self.v@w.T
        epistemic_diag=np.sum(w*b.T,axis=1)
        total_diag=noise_diag if self.known_mean else noise_diag+epistemic_diag
        covariance=None
        if full_cov:
            covariance=self.model.k0-weights@k.T
            if not self.known_mean:
                covariance+=w@b
            covariance=(covariance+covariance.T)/2
        self.cached=(weights,noise_diag,w)
        return forecast,total_diag,covariance,b

    def beta(self,delta=.05):
        return math.sqrt(max(0,self.logdet_ratio)+2*math.log(1/delta))+math.sqrt(
            ALPHA*NORM_BOUND**2+LAMBDA*ENERGY_BOUND**2)

    def update(self, arm, observation):
        t=self.t
        if self.cached is None:
            k=self.model.kernel(t,self.actions[:t])[arm]
            ak=self.a[:t,:t]@k
            d=self.model.k0[arm,arm]+OBS_VARIANCE-ak@k
            vector=np.eye(1,self.n,arm).ravel()-np.bincount(
                self.actions[:t],weights=ak,minlength=self.n)
        else:
            weights,noise_diag,w=self.cached
            ak=weights[arm];d=noise_diag[arm]+OBS_VARIANCE;vector=w[arm]
        assert d>0 and np.isfinite(d),("bad conditional variance",t,d)
        residual=observation-ak@self.y[:t]
        if not self.known_mean:
            column=self.v@vector
            denominator=d+vector@column
            self.m+=column*(residual-vector@self.m)/denominator
            self.v-=np.outer(column,column)/denominator
            self.logdet_ratio+=math.log1p((vector@column)/d)
        self.a[:t,:t]+=np.outer(ak,ak)/d
        self.a[t,:t]=-ak/d;self.a[:t,t]=-ak/d;self.a[t,t]=1/d
        self.actions[t]=arm;self.y[t]=observation
        self.t+=1;self.cached=None


class IndependentAR:
    """Exact temporal likelihood for each arm; spatial covariance is omitted."""
    def __init__(self,model):
        self.model,self.n,self.p=model,model.n,model.p
        self.m=np.zeros((self.n,self.p+1))
        self.cov=np.zeros((self.n,self.p+1,self.p+1))
        self.cov[:,0,0]=1/ALPHA
        for i,g in enumerate(model.groups):
            self.cov[i,1:,1:]=model.cross[g,g]
        self.transition=np.zeros((self.n,self.p+1,self.p+1))
        self.transition[:,0,0]=1
        self.transition[:,1,1:]=model.coefficients
        self.transition[:,2:,1:-1]=np.eye(self.p-1)

    def mean(self):
        return self.m[:,0]

    def forecast(self):
        forecast=self.m[:,0]+self.m[:,1]
        variance=self.cov[:,0,0]+self.cov[:,1,1]+2*self.cov[:,0,1]
        return forecast,variance

    def update(self,arm,y):
        column=self.cov[arm,:,0]+self.cov[arm,:,1]
        variance=column[0]+column[1]+OBS_VARIANCE
        self.m[arm]+=column*(y-self.m[arm,0]-self.m[arm,1])/variance
        self.cov[arm]-=np.outer(column,column)/variance
        self.m=np.einsum("nij,nj->ni",self.transition,self.m)
        self.cov=self.transition@self.cov@np.transpose(self.transition,(0,2,1))
        self.cov[:,1,1]+=np.diag(self.model.q)


class IID:
    def __init__(self,model):
        self.n=model.n;self.count=np.zeros(self.n);self.sum=np.zeros(self.n)
        self.variance=np.diag(model.k0)+OBS_VARIANCE
    def mean(self):
        return self.sum/self.variance/(ALPHA+self.count/self.variance)
    def sd(self):
        return 1/np.sqrt(ALPHA+self.count/self.variance)
    def update(self,arm,y):
        self.count[arm]+=1;self.sum[arm]+=y


def stable_factor(matrix):
    symmetric=(matrix+matrix.T)/2
    return np.linalg.cholesky(symmetric+1e-10*np.eye(len(matrix)))


def forced_action(t,n):
    if t<n:
        return t
    age=t-n+1
    root=math.isqrt(age)
    return (root-1)%n if root*root==age else None


def choose(policy,engine,t,rng):
    n=engine.n
    if policy=="round_robin":
        return t%n
    forced=forced_action(t,n) if policy in LEARNING else None
    if forced is not None:
        return forced
    scale=UCB_SCALE*math.sqrt(2*math.log(t+2))
    if policy.startswith("iid_"):
        return int(np.argmax(engine.mean()+(
            scale*engine.sd() if policy.endswith("ucb")
            else TS_SCALE*engine.sd()*rng.standard_normal(n))))
    if policy.startswith("ar_state_"):
        mean,variance=engine.forecast()
        return int(np.argmax(mean+(
            scale*np.sqrt(np.maximum(variance,0)) if policy.endswith("ucb")
            else TS_SCALE*np.sqrt(np.maximum(variance,0))*rng.standard_normal(n))))
    if policy=="joint_mean_ucb_cert":
        return int(np.argmax(engine.m+engine.beta()*np.sqrt(np.maximum(np.diag(engine.v),0))))
    if policy=="joint_mean_ucb":
        return int(np.argmax(engine.m+scale*np.sqrt(np.maximum(np.diag(engine.v),0))))
    if policy=="joint_mean_ts":
        return int(np.argmax(engine.m+TS_SCALE*stable_factor(engine.v)@rng.standard_normal(n)))
    if policy in ("joint_state_ucb","joint_state_ts","joint_predictive_ucb",
                  "joint_predictive_ts","known_mean_greedy"):
        m,diag,cov,_=engine.forecast(full_cov=policy.endswith("ts"))
        if policy=="known_mean_greedy":
            return int(np.argmax(m))
        if policy.startswith("joint_predictive_"):
            diag=diag-np.diag(engine.model.q)
            if cov is not None:
                cov=cov-engine.model.q
        if policy.endswith("ucb"):
            return int(np.argmax(m+scale*np.sqrt(np.maximum(diag,0))))
        return int(np.argmax(m+TS_SCALE*stable_factor(cov)@rng.standard_normal(n)))
    if policy in ("joint_lucb","joint_tt_ts"):
        v=engine.v
        if policy=="joint_tt_ts":
            lower=stable_factor(v)
            leader=int(np.argmax(engine.m+TS_SCALE*lower@rng.standard_normal(n)))
            challenger=leader
            for _ in range(64):
                challenger=int(np.argmax(engine.m+TS_SCALE*lower@rng.standard_normal(n)))
                if challenger!=leader:
                    break
        else:
            leader=int(np.argmax(engine.m));challenger=leader
        if challenger==leader:
            contrast_var=v[leader,leader]+np.diag(v)-2*v[leader]
            scores=engine.m-engine.m[leader]+scale*np.sqrt(np.maximum(contrast_var,0))
            scores[leader]=-np.inf;challenger=int(np.argmax(scores))
        _,variance,_,b=engine.forecast(design=True)
        gain=(b[leader]-b[challenger])**2/(variance+OBS_VARIANCE)
        return int(np.argmax(gain))
    raise ValueError(policy)


def checkpoint_row(config,seed,policy,t,engine,model,oracle_reg,mean_reg,static_reg,total_reward,
                   audit=None):
    recommendation=int(np.argmax(engine.mean()))
    return {"config":config,"seed":seed,"policy":policy,"horizon":t,
        "oracle_regret":float(oracle_reg),"oracle_regret_per_round":float(oracle_reg/t),
        "mean_pseudo_regret":float(mean_reg),"mean_pseudo_regret_per_round":float(mean_reg/t),
        "stationary_mean_reward_regret":float(t*model.mu.max()-total_reward),
        "stationary_mean_reward_regret_per_round":float(model.mu.max()-total_reward/t),
        "fixed_best_reward_regret":float(static_reg),"fixed_best_reward_regret_per_round":float(static_reg/t),
        "cumulative_reward":float(total_reward),"recommendation":recommendation,
        "correct_selection":int(recommendation==np.argmax(model.mu)),
        "simple_regret":float(model.mu.max()-model.mu[recommendation]),
        "mean_squared_error":float(np.mean((engine.mean()-model.mu)**2)),
        "certified_policy_confidence_audit":int(audit) if audit is not None else None}


def run_replicate(task):
    config,seed,side,p,horizon,policies=task
    start=time.perf_counter();model=get_model(config,side,p,horizon)
    field,noise,past=model.world(SEED+seed+zlib.crc32(config.encode()))
    oracle=field.max(axis=1);best=int(np.argmax(model.mu))
    checkpoints=sorted({x for x in (100,250,500,1000,1500,2000,5000,horizon) if x<=horizon})
    rows=[]
    for policy in policies:
        if policy in ("mean_oracle","past_state_genie","state_oracle"):
            actions=(np.full(horizon,best) if policy=="mean_oracle"
                     else np.argmax(past if policy=="past_state_genie" else field,axis=1))
            reward=field[np.arange(horizon),actions]
            orreg=np.cumsum(oracle-reward)
            mureg=np.cumsum(model.mu[best]-model.mu[actions])
            static=np.cumsum(field[:,best]-reward)
            for t in checkpoints:
                rows.append({"config":config,"seed":seed,"policy":policy,"horizon":t,
                    "oracle_regret":float(orreg[t-1]),"oracle_regret_per_round":float(orreg[t-1]/t),
                    "mean_pseudo_regret":float(mureg[t-1]),"mean_pseudo_regret_per_round":float(mureg[t-1]/t),
                    "fixed_best_reward_regret":float(static[t-1]),
                    "fixed_best_reward_regret_per_round":float(static[t-1]/t),
                    "cumulative_reward":float(reward[:t].sum()),"recommendation":best,
                    "stationary_mean_reward_regret":float(t*model.mu.max()-reward[:t].sum()),
                    "stationary_mean_reward_regret_per_round":float(model.mu.max()-reward[:t].mean()),
                    "correct_selection":1,"simple_regret":0.0,"mean_squared_error":0.0,
                    "certified_policy_confidence_audit":None})
            continue
        if policy.startswith("iid_"):
            engine=IID(model)
        elif policy.startswith("ar_state_"):
            engine=IndependentAR(model)
        else:
            engine=Likelihood(model,known_mean=policy=="known_mean_greedy")
        rng=np.random.default_rng(SEED+seed*1009+zlib.crc32(policy.encode()))
        regret_o=regret_m=regret_static=reward_total=0.0
        audit=True if policy=="joint_mean_ucb_cert" else None
        for time_index in range(horizon):
            arm=choose(policy,engine,time_index,rng)
            reward=field[time_index,arm]
            engine.update(arm,reward+noise[time_index,arm])
            regret_o+=oracle[time_index]-reward
            regret_m+=model.mu[best]-model.mu[arm]
            regret_static+=field[time_index,best]-reward
            reward_total+=reward
            t=time_index+1
            if policy=="joint_mean_ucb_cert" and t in checkpoints:
                error=engine.m-model.mu
                value=error@np.linalg.solve(engine.v,error)
                audit=audit and value<=engine.beta()**2+1e-7
            if t in checkpoints:
                rows.append(checkpoint_row(config,seed,policy,t,engine,model,regret_o,regret_m,
                                           regret_static,reward_total,audit))
    print(f"{config} seed {seed}: {len(policies)} policies, {time.perf_counter()-start:.1f}s",flush=True)
    return rows


def verify():
    assertions=0
    for config in ("persistent","seasonal","heterogeneous"):
        model=Model(config,side=2,p=4,horizon=18)
        engine=Likelihood(model)
        rng=np.random.default_rng(934)
        actions=[];ys=[]
        for t in range(model.horizon):
            m,diag,cov,b=engine.forecast(full_cov=True)
            if t:
                xi=np.empty((t,t))
                for i in range(t):
                    for j in range(t):
                        if i>=j:
                            value=model.spatial[actions[i],actions[j]]*model.temporal[
                                model.groups[actions[i]],model.groups[actions[j]],i-j]
                        else:
                            value=model.spatial[actions[j],actions[i]]*model.temporal[
                                model.groups[actions[j]],model.groups[actions[i]],j-i]
                        xi[i,j]=value+OBS_VARIANCE*(i==j)
                design=np.eye(model.n)[actions]
                info=design.T@np.linalg.solve(xi,design)
                v=np.linalg.inv(model.h+info)
                estimate=v@design.T@np.linalg.solve(xi,ys)
                assert np.allclose(engine.v,v,atol=2e-9)
                assert np.allclose(engine.m,estimate,atol=2e-9)
                assert np.allclose(engine.a[:t,:t],np.linalg.inv(xi),atol=2e-9)
                k=model.kernel(t,np.array(actions))
                weights=np.linalg.solve(xi,k.T).T
                w=np.eye(model.n)-weights@design
                noise=model.k0-weights@k.T
                assert np.allclose(m,estimate+weights@(np.array(ys)-design@estimate),atol=2e-9)
                assert np.allclose(cov,noise+w@v@w.T,atol=2e-9)
                assert np.allclose(b,v@w.T,atol=2e-9)
                assert abs(engine.logdet_ratio-(np.linalg.slogdet(model.h+info)[1]
                                                -np.linalg.slogdet(model.h)[1]))<2e-8
                assertions+=7
                beta=engine.beta()
                assert beta>0
                assertions+=1
            assert np.linalg.eigvalsh(cov).min()>-1e-8
            assertions+=1
            assert np.linalg.eigvalsh(cov-model.q).min()>-1e-8
            assertions+=1
            action=int(np.argmax(engine.m+.1*rng.standard_normal(model.n)))
            actions.append(action);ys.append(float(rng.normal()))
            old_v=engine.v.copy()
            d=diag[action]+OBS_VARIANCE
            old_c=old_v[0,0]+old_v[1,1]-2*old_v[0,1]
            gain=(b[0,action]-b[1,action])**2/d
            engine.update(action,ys[-1])
            new_c=engine.v[0,0]+engine.v[1,1]-2*engine.v[0,1]
            assert abs(old_c-new_c-gain)<2e-8
            assertions+=1
    # Independent AR blocks agree with the same dense kernel using Q diagonal.
    model=Model("no_spatial",side=2,p=4,horizon=15)
    model.h=ALPHA*np.eye(model.n);model.v0=np.eye(model.n)/ALPHA
    block=IndependentAR(model);kernel=Likelihood(model)
    rng=np.random.default_rng(25)
    for t in range(15):
        prediction,variance=block.forecast()
        mk,dk,_,_=kernel.forecast()
        assert np.allclose(prediction,mk,atol=1e-8)
        assert np.allclose(variance,dk,atol=1e-8)
        assert np.allclose(block.mean(),kernel.m,atol=1e-8)
        assertions+=3
        a=int(rng.integers(model.n));y=float(rng.normal())
        block.update(a,y);kernel.update(a,y)
    # Direct state Gaussian conditioning independently checks lag-kernel orientation.
    model=Model("heterogeneous",side=2,p=4,horizon=8)
    n,p=model.n,model.p
    blocks=model.cross[model.groups[:,None],model.groups[None,:]]*model.spatial[:,:,None,None]
    gamma=blocks.transpose(2,0,3,1).reshape(p*n,p*n)
    f=np.zeros_like(gamma)
    f[:n]=np.concatenate([np.diag(model.coefficients[:,k]) for k in range(p)],axis=1)
    f[n:,:-n]=np.eye(n*(p-1))
    w=np.zeros_like(gamma);w[:n,:n]=model.q
    assert np.allclose(gamma,f@gamma@f.T+w,atol=1e-9)
    assertions+=1
    for h in range(8):
        actual=(np.linalg.matrix_power(f,h)@gamma)[:n,:n]
        exact=model.spatial*model.temporal[model.groups[:,None],model.groups[None,:],h]
        assert np.allclose(actual,exact,atol=1e-8)
        assertions+=1
    # Means remain fixed when the environment seed changes.
    mu=model.mu.copy();one=model.world(1);two=model.world(2)
    assert np.array_equal(mu,model.mu) and not np.array_equal(one[0],two[0])
    assert np.max(one[0].max(axis=1)-one[0][:,0])>=0
    assertions+=2
    # Counterfactual stationary regret can be negative while mean pseudo-regret cannot.
    mu=np.array([1.0,0.0]);field=np.array([[0.0,2.0],[0.0,2.0]])
    assert np.sum(field[:,0]-field[:,1])<0
    assert np.sum(mu.max()-mu[[1,1]])>0
    assertions+=2
    for policy in LEARNING:
        model=Model("persistent",side=2,p=4,horizon=8)
        engine=IID(model) if policy.startswith("iid_") else IndependentAR(model) if policy.startswith("ar_state_") else Likelihood(model)
        action=choose(policy,engine,0,np.random.default_rng(5))
        assert action==0
        assertions+=1
    return {"assertions":assertions,"dense_likelihood_verified":True,
            "mixed_AR_kernel_orientation_verified":True,"means_are_fixed":True,
            "independent_AR_filter_verified":True,"contrast_gain_verified":True,
            "predictable_working_covariance_is_psd":True,
            "counterfactual_and_mean_regret_distinguished":True}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--verify",action="store_true")
    parser.add_argument("--runs",type=int,default=32)
    parser.add_argument("--horizon",type=int,default=1000)
    parser.add_argument("--jobs",type=int,default=4)
    parser.add_argument("--side",type=int,default=10)
    parser.add_argument("--order",type=int,default=20)
    parser.add_argument("--configs",nargs="+",choices=CONFIGS,default=list(CONFIGS))
    parser.add_argument("--policies",nargs="+",choices=LEARNING+BENCHMARKS,default=list(LEARNING+BENCHMARKS))
    parser.add_argument("--output",type=Path,default=OUTPUT)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    checks=verify()
    (args.output/"checks.json").write_text(json.dumps(checks,indent=2)+"\n")
    if args.verify:
        print(json.dumps(checks,indent=2));return
    if min(args.runs,args.horizon,args.jobs,args.side,args.order)<1:
        parser.error("positive run, horizon, worker and dimension values required")
    if args.side<2:
        parser.error("grid side must be at least 2 for a multiple-arm problem")
    metadata={"runs":args.runs,"horizon":args.horizon,"jobs":args.jobs,
        "base_seed":SEED,"grid_side":args.side,
        "environment_seed_rule":"base_seed + replicate + crc32(configuration)",
        "policy_seed_rule":"base_seed + 1009*replicate + crc32(policy)",
        "arms":args.side**2,"ar_order":args.order,"means_are_fixed":True,
        "learning_policies":LEARNING,"benchmarks":BENCHMARKS,"requested_policies":args.policies,
        "regularizer_alpha":ALPHA,"graph_penalty":LAMBDA,"ucb_scale":UCB_SCALE,"ts_scale":TS_SCALE,
        "measurement_variance":OBS_VARIANCE,"supplied_norm_bound":NORM_BOUND,
        "supplied_energy_radius":ENERGY_BOUND,"forced_probes":"initial N observations, then square calendar ages",
        "inference":"exact selected-history AR covariance; no lag/state truncation",
        "Gaussian_draws":"algorithmic uncertainty draws; the physical mean vector is fixed",
        "predictive_policies":"remove known fresh innovation covariance from current-field uncertainty",
        "PCS":"largest estimated stationary mean; fixed-truth repeated-noise accuracy",
        "certified_policy_audit":"at reported checkpoints; no fixed-budget certificate claimed",
        "models":[Model(c,args.side,args.order,args.horizon).metadata() for c in args.configs]}
    (args.output/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    tasks=[(c,s,args.side,args.order,args.horizon,tuple(args.policies))
           for c in args.configs for s in range(args.runs)]
    # Incremental results survive interruptions; each job is one paired world.
    with (args.output/"runs.jsonl").open("w") as handle:
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            futures=[pool.submit(run_replicate,task) for task in tasks]
            for future in as_completed(futures):
                for row in future.result():
                    handle.write(json.dumps(row)+"\n")
                handle.flush()
    print(f"Saved {len(tasks)} paired worlds to {args.output}",flush=True)


if __name__=="__main__":
    main()
