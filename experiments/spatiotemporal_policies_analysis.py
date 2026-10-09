"""Paired uncertainty, oracle floor, tables, and figures for the AR(20) study."""
from __future__ import annotations
import argparse
import csv
import json
import math
import platform
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/"research"/"spatiotemporal_bandits"/"results"/"policies_ar20"
LABELS={
    "iid_ucb":"IID UCB", "iid_ts":"IID TS",
    "ar_state_ucb":"Independent AR UCB", "ar_state_ts":"Independent AR TS",
    "joint_mean_ucb":"Joint mean UCB", "joint_mean_ts":"Joint mean TS",
    "joint_mean_ucb_cert":"Certified mean UCB",
    "joint_state_ucb":"Joint full-state UCB", "joint_state_ts":"Joint full-state TS",
    "joint_predictive_ucb":"Joint predictive UCB", "joint_predictive_ts":"Joint predictive TS",
    "joint_lucb":"Contrast LUCB", "joint_tt_ts":"Top-two contrast TS",
    "round_robin":"Round robin", "known_mean_greedy":"Known-mean greedy",
    "mean_oracle":"Best-mean arm", "past_state_genie":"Full-past genie",
    "state_oracle":"Current-state oracle"}
CONFIG_LABELS={"persistent":"Persistent dense AR(20)","weak":"Weak dense AR(20)",
    "seasonal":"Lag-20 AR(20)","heterogeneous":"Heterogeneous AR(20)",
    "no_spatial":"Independent spatial innovations"}
METRICS=("oracle_regret_per_round","mean_pseudo_regret_per_round",
         "stationary_mean_reward_regret_per_round",
         "fixed_best_reward_regret_per_round","correct_selection","simple_regret",
         "mean_squared_error")
COLORS={"iid_ucb":"#7f7f7f","ar_state_ucb":"#e69f00",
    "joint_mean_ucb":"#0072b2","joint_mean_ts":"#56b4e9",
    "joint_state_ucb":"#882255",
    "joint_predictive_ucb":"#009e73","joint_predictive_ts":"#cc79a7",
    "joint_lucb":"#d55e00","joint_tt_ts":"#8b4513",
    "round_robin":"#aaaabb","past_state_genie":"#111111"}
CURVE_POLICIES=("iid_ucb","ar_state_ucb","joint_mean_ucb","joint_state_ucb","joint_predictive_ucb",
                "joint_predictive_ts","joint_lucb","joint_tt_ts")
PAIRS=(
    ("joint_state_ucb","iid_ucb"),
    ("joint_state_ucb","ar_state_ucb"),
    ("joint_state_ucb","joint_mean_ucb"),
    ("joint_predictive_ucb","iid_ucb"),
    ("joint_predictive_ucb","ar_state_ucb"),
    ("joint_predictive_ucb","joint_state_ucb"),
    ("joint_predictive_ts","joint_state_ts"),
    ("joint_predictive_ucb","joint_mean_ucb"),
    ("joint_mean_ucb","iid_ucb"),
    ("joint_mean_ts","iid_ts"),
    ("joint_lucb","round_robin"),
    ("joint_tt_ts","round_robin"),
    ("joint_lucb","joint_mean_ucb"),
    ("joint_tt_ts","joint_mean_ts"),
    ("joint_predictive_ucb","joint_predictive_ts"),
)


def interval(values):
    a=np.asarray(values,dtype=float)
    mean=float(a.mean());n=len(a)
    se=float(a.std(ddof=1)/math.sqrt(n)) if n>1 else float("nan")
    half=float(student_t.ppf(.975,n-1)*se) if n>1 else float("nan")
    return mean,se,mean-half,mean+half


def wilson(successes,n):
    z=1.959963984540054;p=successes/n
    denominator=1+z*z/n
    center=(p+z*z/(2*n))/denominator
    radius=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denominator
    return center-radius,center+radius


def write_csv(path,rows):
    if not rows:
        return
    with path.open("w",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)


def summarize(rows):
    groups={}
    for row in rows:
        key=(row["config"],row["policy"],row["horizon"])
        groups.setdefault(key,[]).append(row)
    summary=[];lookup={}
    for (config,policy,horizon),group in sorted(groups.items()):
        group=sorted(group,key=lambda r:r["seed"])
        out={"config":config,"policy":policy,"horizon":horizon,"runs":len(group)}
        for metric in METRICS:
            values=[r[metric] for r in group]
            mean,se,low,high=interval(values)
            if metric=="correct_selection":
                low,high=wilson(sum(values),len(values))
            for suffix,value in (("",mean),("_se",se),("_ci_low",low),("_ci_high",high)):
                out[metric+suffix]=value
        out["checkpoint_confidence_audit_fraction"]=(float(np.mean([
            r["certified_policy_confidence_audit"] for r in group]))
            if policy=="joint_mean_ucb_cert" else None)
        summary.append(out);lookup[(config,policy,horizon)]=out
    return summary,lookup


def paired(rows):
    index={(r["config"],r["policy"],r["horizon"],r["seed"]):r for r in rows}
    configs=sorted({r["config"] for r in rows});horizons=sorted({r["horizon"] for r in rows})
    output=[]
    for config in configs:
        for horizon in horizons:
            for candidate,baseline in PAIRS:
                seeds=sorted({r["seed"] for r in rows if r["config"]==config
                    and r["policy"]==candidate and r["horizon"]==horizon})
                seeds=[s for s in seeds if (config,baseline,horizon,s) in index]
                if not seeds:
                    continue
                for metric in METRICS:
                    sign=1 if metric=="correct_selection" else -1
                    values=[sign*(index[config,candidate,horizon,s][metric]
                                  -index[config,baseline,horizon,s][metric]) for s in seeds]
                    mean,se,low,high=interval(values)
                    output.append({"config":config,"horizon":horizon,"candidate":candidate,
                        "baseline":baseline,"metric":metric,"paired_runs":len(seeds),
                        "improvement":mean,"se":se,"ci_low":low,"ci_high":high})
    return output


def oracle_floor(metadata,samples=200000):
    rng=np.random.default_rng(97110);output=[]
    for model in metadata["models"]:
        mu=np.array(model["fixed_means"]);q=np.array(model["innovation_covariance"])
        k0=np.array(model["stationary_current_covariance"])
        pred=(k0-q+(k0-q).T)/2
        eig,vec=np.linalg.eigh(pred)
        assert eig.min()>-1e-8
        factor=vec*np.sqrt(np.maximum(eig,0))[None,:]
        lq=np.linalg.cholesky(q)
        differences=[];oracle=[];genie=[]
        for start in range(0,samples,4000):
            size=min(4000,samples-start)
            past=rng.standard_normal((size,len(mu)))@factor.T
            innovation=rng.standard_normal((size,len(mu)))@lq.T
            a=(mu+past+innovation).max(axis=1);b=(mu+past).max(axis=1)
            differences.append(a-b);oracle.append(a);genie.append(b)
        mean,se,low,high=interval(np.concatenate(differences))
        output.append({"config":model["config"],"samples":samples,
            "oracle_floor":mean,"se":se,"ci_low":low,"ci_high":high,
            "expected_oracle_reward":float(np.concatenate(oracle).mean()),
            "expected_full_past_genie_reward":float(np.concatenate(genie).mean()),
            "best_mean":float(mu.max())})
    return output


def make_plots(output,metadata,lookup,floors):
    plt.rcParams.update({"font.size":11,"axes.spines.top":False,
                         "axes.spines.right":False,"figure.dpi":150})
    configs=[m["config"] for m in metadata["models"]]
    horizons=sorted({key[2] for key in lookup})
    for metric,filename,ylabel in (
        ("oracle_regret_per_round","oracle_regret","Oracle regret / decision"),
        ("mean_pseudo_regret_per_round","mean_regret","Mean pseudo-regret / decision"),
        ("stationary_mean_reward_regret_per_round","stationary_reward_regret","Stationary reward regret / decision"),
        ("correct_selection","pcs","Probability of correct selection")):
        fig,axes=plt.subplots(2,3,figsize=(12,7.5),sharex=True)
        for ax,config in zip(axes.ravel(),configs):
            for policy in CURVE_POLICIES:
                series=[lookup.get((config,policy,h)) for h in horizons]
                series=[r for r in series if r is not None]
                if not series:
                    continue
                xx=[r["horizon"] for r in series]
                yy=[r[metric] for r in series]
                ax.plot(xx,yy,marker="o",markersize=3,color=COLORS[policy],
                        label=LABELS[policy],linewidth=1.8)
                ax.fill_between(xx,[r[metric+"_ci_low"] for r in series],
                                [r[metric+"_ci_high"] for r in series],
                                color=COLORS[policy],alpha=.07,linewidth=0)
            if metric=="oracle_regret_per_round":
                floor=next(r["oracle_floor"] for r in floors if r["config"]==config)
                ax.axhline(floor,color="black",linestyle="--",label="Innovation floor",linewidth=1.3)
            if metric=="stationary_mean_reward_regret_per_round":
                ax.axhline(0,color="black",linestyle="--",label="Stationary mean benchmark",linewidth=1.3)
            ax.set_title(CONFIG_LABELS[config],fontsize=11)
            ax.set_xlabel("Calendar samples");ax.set_ylabel(ylabel)
            ax.tick_params(axis="x",labelbottom=True)
            ax.grid(alpha=.18)
            if metric=="correct_selection":
                ax.set_ylim(0,1)
        axes.ravel()[-1].axis("off")
        handles,labels=axes.ravel()[0].get_legend_handles_labels()
        axes.ravel()[-1].legend(handles,labels,loc="center left",frameon=False,fontsize=10)
        title=("Fixed-truth PCS; 32 paired noise worlds; shading = Wilson 95% intervals" if metric=="correct_selection"
               else "Paired noise worlds; shading = pointwise 95% mean intervals")
        title=title.replace("32",str(metadata["runs"]))
        fig.suptitle(title,fontsize=13);fig.tight_layout(rect=(0,0,1,.96))
        fig.savefig(output/(filename+".pdf"),bbox_inches="tight")
        fig.savefig(output/(filename+".png"),bbox_inches="tight",dpi=180)
        plt.close(fig)
    # The reward targets can conflict; show both axes at the terminal budget.
    fig,axes=plt.subplots(2,3,figsize=(12,7.5))
    final=metadata["horizon"]
    for ax,config in zip(axes.ravel(),configs):
        for policy in CURVE_POLICIES:
            r=lookup.get((config,policy,final))
            if not r:
                continue
            x=r["mean_pseudo_regret_per_round"];y=r["oracle_regret_per_round"]
            ax.errorbar(x,y,xerr=1.96*r["mean_pseudo_regret_per_round_se"],
                yerr=1.96*r["oracle_regret_per_round_se"],fmt="o",color=COLORS[policy],
                capsize=2,markersize=6,label=LABELS[policy])
        ax.set_title(CONFIG_LABELS[config],fontsize=11)
        ax.set_xlabel("Mean pseudo-regret / decision");ax.set_ylabel("Oracle regret / decision")
        ax.grid(alpha=.18)
    axes.ravel()[-1].axis("off")
    handles,labels=axes.ravel()[0].get_legend_handles_labels()
    axes.ravel()[-1].legend(handles,labels,loc="center left",frameon=False,fontsize=10)
    fig.suptitle(f"Objective tradeoffs at T={final}; bars = 1.96 standard errors",fontsize=13)
    fig.tight_layout(rect=(0,0,1,.96))
    fig.savefig(output/"tradeoffs.pdf",bbox_inches="tight")
    fig.savefig(output/"tradeoffs.png",bbox_inches="tight",dpi=180);plt.close(fig)


def display_interval(row,metric,digits=3):
    return (f"{row[metric]:.{digits}f} "
            f"[{row[metric+'_ci_low']:.{digits}f}, {row[metric+'_ci_high']:.{digits}f}]")


def write_findings(output,metadata,lookup,pairs,floors,complete):
    horizon=metadata["horizon"];configs=[m["config"] for m in metadata["models"]]
    learning=[p for p in metadata["requested_policies"] if p in metadata["learning_policies"]]
    lines=["# Fixed-mean spatial AR(20): UCB, Thompson-style sampling, and PCS", "",
        f"The study contains **{metadata['arms']} arms**, order **{metadata['ar_order']}** per arm, "
        f"**{metadata['runs']} independent paired noise worlds per configuration**, and "
        f"**{horizon} decisions** per world. There are {len(configs)} configurations and "
        f"{len(learning)} learning policies plus {len(metadata['benchmarks'])} information benchmarks. "
        f"Result completeness: **{'complete' if complete else 'partial'}**.","",
        "The mean vector is deterministic and identical across noise worlds and configurations. "
        "Only deviations, sensor noise, and policy randomization change. Each learning rule receives "
        "only its selected reading after its action. All arms evolve every calendar round. Policies "
        "share latent paths and potential sensor noises within each replicate.","",
        "See [policy derivations](../../policies.md), [summary with intervals](summary.csv), "
        "[paired comparisons](paired.csv), [raw runs](runs.jsonl), [metadata](metadata.json), "
        "and [numerical checks](checks.json).", "",
        "## Objectives and uncertainty", "",
        "Oracle regret compares actual latent reward with the maximum current field. Mean "
        "pseudo-regret sums permanent mean gaps. Stationary mean reward regret subtracts actual "
        "reward from T times the best permanent mean and can be negative. Actual reward regret "
        "against always choosing the "
        "best-mean arm is reported separately and can be negative. PCS measures terminal selection "
        "of that fixed best mean. Known-mean benchmarks have artificial PCS one and are excluded "
        "from learning-policy selection comparisons.","",
        "Continuous-metric intervals use Student t across independent worlds. PCS intervals use "
        "Wilson's binomial formula. Paired differences use the same world for both policies and "
        "approximate Student t intervals, including PCS differences. These "
        "are pointwise 95% intervals, without simultaneous adjustment over policies or configurations. "
        "An observed winner is not proof of a universally best policy or a significant difference.","",
        "The budget includes one initial observation of every arm. Subsequent square-age forced "
        "probes have a vanishing fraction asymptotically; at this budget they still matter. UCB "
        "scale 0.7, Thompson scale 1, and H=0.1 I+0.5 L are fixed across all configurations. "
        "No per-configuration parameter optimization is performed.","",
        "## Terminal performance", "",
        "All continuous regret entries below are **per decision**. Brackets are 95% intervals. "
        "The full CSV includes every policy and checkpoint.", ""]
    selected=("iid_ucb","ar_state_ucb","joint_mean_ucb","joint_mean_ts",
              "joint_state_ucb","joint_predictive_ucb","joint_predictive_ts","joint_lucb","joint_tt_ts",
              "round_robin","known_mean_greedy","mean_oracle","past_state_genie")
    for config in configs:
        lines+= [f"### {CONFIG_LABELS[config]}","",
                 "| Policy | Oracle regret | Mean pseudo-regret | PCS | Simple regret |",
                 "|---|---:|---:|---:|---:|"]
        for policy in selected:
            r=lookup.get((config,policy,horizon))
            if not r:
                continue
            pcs=display_interval(r,"correct_selection",2) if policy in learning else "knows truth"
            lines.append(f"| {LABELS[policy]} | {display_interval(r,'oracle_regret_per_round')} "
                f"| {display_interval(r,'mean_pseudo_regret_per_round')} | {pcs} "
                f"| {r['simple_regret']:.3f} |")
        lines.append("")
        available=[lookup[config,p,horizon] for p in learning if (config,p,horizon) in lookup]
        if available:
            best_o=min(available,key=lambda r:r["oracle_regret_per_round"])
            best_m=min(available,key=lambda r:r["mean_pseudo_regret_per_round"])
            best_p=max(available,key=lambda r:r["correct_selection"])
            lines.append(f"Observed learning-policy leaders: oracle regret—{LABELS[best_o['policy']]}; "
                f"mean pseudo-regret—{LABELS[best_m['policy']]}; PCS—{LABELS[best_p['policy']]}. "
                "Ties and overlapping uncertainty should be assessed in the CSV, not interpreted as rankings.")
            lines.append("")
    lines += ["## Actual reward against the stationary mean", "",
        "Joint full-state UCB illustrates why permanent mean gaps and actual reward regret "
        "must be reported separately. Negative stationary reward regret means accumulated "
        "reward exceeds T times the best permanent mean. The fixed-arm path comparator has "
        "the same expectation, with additional finite-path noise from that arm.","",
        "| Configuration | Stationary reward regret / T [95% CI] | Mean pseudo-regret / T | Fixed-arm reward regret / T [95% CI] |",
        "|---|---:|---:|---:|"]
    for config in configs:
        r=lookup.get((config,"joint_state_ucb",horizon))
        if r:
            lines.append(f"| {config} | {display_interval(r,'stationary_mean_reward_regret_per_round')} "
                f"| {r['mean_pseudo_regret_per_round']:.3f} "
                f"| {display_interval(r,'fixed_best_reward_regret_per_round')} |")
    lines += ["", "## Paired comparisons", "",
        "Positive improvement means lower regret/loss, or higher PCS. These comparisons "
        "are paired across noise worlds; a negative number favors the baseline.","",
        "| Configuration | Comparison | Metric | Improvement [95% CI] |",
        "|---|---|---|---:|"]
    reported={
        ("joint_state_ucb","iid_ucb","oracle_regret_per_round"),
        ("joint_predictive_ucb","iid_ucb","oracle_regret_per_round"),
        ("joint_predictive_ucb","ar_state_ucb","oracle_regret_per_round"),
        ("joint_predictive_ts","joint_state_ts","oracle_regret_per_round"),
        ("joint_mean_ucb","iid_ucb","mean_pseudo_regret_per_round"),
        ("joint_lucb","round_robin","correct_selection"),
        ("joint_tt_ts","round_robin","correct_selection")}
    for r in pairs:
        if r["horizon"]!=horizon or (r["candidate"],r["baseline"],r["metric"]) not in reported:
            continue
        metric={"oracle_regret_per_round":"Oracle regret", "mean_pseudo_regret_per_round":
                "Mean regret", "correct_selection":"PCS"}[r["metric"]]
        lines.append(f"| {r['config']} | {LABELS[r['candidate']]} vs {LABELS[r['baseline']]} "
            f"| {metric} | {r['improvement']:.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}] |")
    lines += ["", "## Irreducible oracle-regret coefficient", "",
        "The full-past genie knows all arms' lag states and fixed means, but chooses before the fresh "
        "innovation. Its expected per-round regret is the proven lower bound "
        "G(mu,K0)-G(mu,K0-Q). We estimate it with 200,000 independent paired Gaussian samples "
        "per configuration. This calculation is independent of the policy experiment and its "
        "serial trajectory noise.","",
        "| Configuration | Innovation floor [MC 95% CI] | Sampled full-past genie | Best-mean arm |",
        "|---|---:|---:|---:|"]
    for floor in floors:
        config=floor["config"]
        genie=lookup.get((config,"past_state_genie",horizon))
        best=lookup.get((config,"mean_oracle",horizon))
        lines.append(f"| {config} | {floor['oracle_floor']:.3f} "
            f"[{floor['ci_low']:.3f}, {floor['ci_high']:.3f}] | "
            f"{display_interval(genie,'oracle_regret_per_round') if genie else 'absent'} | "
            f"{display_interval(best,'oracle_regret_per_round') if best else 'absent'} |")
    lines += ["", "Linear oracle regret and sublinear mean pseudo-regret are compatible: they use "
        "different comparators. A decreasing oracle-regret ratio over this finite budget does not "
        "establish convergence to a particular coefficient. The known-mean greedy filter is an "
        "implementable information benchmark, not a solved optimal causal policy.","",
        "## What is established and what remains open", "",
        "- Exact correlated-AR likelihood calculations are independently checked against dense "
        "Gaussian conditioning; mixed-filter covariance orientation, independent AR blocks, "
        "contrast information gains, and fixed physical means are verified.",
        "- The certified mean-UCB policy has a conservative high-probability sublinear mean-regret "
        "bound under supplied graph/norm bounds and known correct dynamics. Practical UCB and "
        "Thompson-style rules do not inherit that guarantee.",
        "- Gaussian uncertainty draws use inverse penalized information. They are not a physical "
        "mean population and are not automatically calibrated frequentist posterior draws.",
        "- PCS rules are one-step contrast-information designs. The top-two rule is inspired by "
        "top-two Thompson sampling but differs from the published algorithm; its optimality "
        "theorems are not imported.",
        "- Forecast policies removing Q ignore only independent fresh innovations, retaining "
        "uncertainty about all past lag states and permanent means. They remain myopic and can "
        "undervalue observations with delayed future relevance.",
        "- This is one fixed mean surface with five noise/dynamics configurations. It does not "
        "establish robustness to arbitrary graph misspecification, unknown AR coefficients, "
        "unknown innovation covariance, other gap profiles, or non-Gaussian traffic counts.","",
        "![Oracle regret](oracle_regret.png)","",
        "![Mean pseudo-regret](mean_regret.png)","",
        "![Stationary mean reward regret](stationary_reward_regret.png)","",
        "![Fixed-truth PCS](pcs.png)","",
        "![Objective tradeoffs](tradeoffs.png)",""]
    cert=[lookup[config,"joint_mean_ucb_cert",horizon] for config in configs
          if (config,"joint_mean_ucb_cert",horizon) in lookup]
    if cert:
        position=lines.index("## What is established and what remains open")
        audit="Certified mean-UCB checkpoint confidence audits: "+", ".join(
            f"{r['config']} {r['checkpoint_confidence_audit_fraction']:.3f}" for r in cert)+(
            ". These are checks at recorded checkpoints, not a continuous empirical coverage "
            "audit and not a terminal selection certificate.")
        lines[position:position]=[audit,""]
    (output/"findings.md").write_text("\n".join(lines))


def write_tex(output,metadata,lookup,floors,pairs):
    lines=[r"\begin{tabular}{llrrr}",r"\toprule",
           r"Dynamics & Policy & Oracle/$T$ & Mean/$T$ & PCS\\",r"\midrule"]
    selected=("iid_ucb","ar_state_ucb","joint_mean_ucb","joint_predictive_ucb",
              "joint_state_ucb","joint_predictive_ts","joint_lucb","joint_tt_ts")
    names={"persistent":"Persistent","weak":"Weak","seasonal":"Lag 20",
           "heterogeneous":"Heterogeneous","no_spatial":"Independent shocks"}
    for model in metadata["models"]:
        c=model["config"]
        for i,p in enumerate(selected):
            r=lookup.get((c,p,metadata["horizon"]))
            if not r:
                continue
            lines.append(f"{names[c] if i==0 else ''} & {LABELS[p]} & "
                f"{r['oracle_regret_per_round']:.3f} & {r['mean_pseudo_regret_per_round']:.3f} "
                f"& {r['correct_selection']:.3f}\\\\")
        lines.append(r"\midrule")
    lines[-1]=r"\bottomrule";lines.append(r"\end{tabular}")
    (output/"table.tex").write_text("\n".join(lines)+"\n")
    floor_text=", ".join(f"{names[r['config']]} ${r['oracle_floor']:.3f}$" for r in floors)
    (output/"floor_text.tex").write_text(floor_text+".\n")
    interpretation=[];h=metadata["horizon"]
    if ("weak","joint_predictive_ucb",h) in lookup:
        r=lookup["weak","joint_predictive_ucb",h]
        interpretation.append("For weak dependence, joint predictive UCB has PCS "
            f"${r['correct_selection']:.3f}$, with Wilson interval "
            f"$[{r['correct_selection_ci_low']:.3f},{r['correct_selection_ci_high']:.3f}]$. "
            "The full-variance state UCB has smaller mean and oracle regret in this experiment. "
            "Selection accuracy and accumulated reward thus favor different decisions.")
    if ("seasonal","joint_lucb",h) in lookup and ("seasonal","round_robin",h) in lookup:
        a=lookup["seasonal","joint_lucb",h];b=lookup["seasonal","round_robin",h]
        pair=next(r for r in pairs if r['config']=='seasonal' and r['horizon']==h
            and r['candidate']=='joint_lucb' and r['baseline']=='round_robin'
            and r['metric']=='correct_selection')
        interpretation.append("For lag-20 dependence, contrast LUCB gives PCS "
            f"${a['correct_selection']:.3f}$ versus ${b['correct_selection']:.3f}$ for round robin. "
            f"The paired improvement is ${pair['improvement']:.3f}$ with approximate interval "
            f"$[{pair['ci_low']:.3f},{pair['ci_high']:.3f}]$. "
            "Joint mean UCB has smaller mean pseudo-regret, while full-state UCB has smaller "
            "oracle regret. The PCS-focused rule pays for comparison information rather than "
            "only extracting immediate reward.")
    if ("persistent","joint_state_ucb",h) in lookup and ("persistent","iid_ucb",h) in lookup:
        a=lookup["persistent","joint_state_ucb",h];b=lookup["persistent","iid_ucb",h]
        interpretation.append("For persistent dynamics, joint full-state UCB gives oracle regret "
            f"${a['oracle_regret_per_round']:.3f}$ per round versus "
            f"${b['oracle_regret_per_round']:.3f}$ for iid UCB. "
            "PCS remains poor, and joint mean UCB does not uniformly improve over iid UCB. "
            "Persistence helps state prediction while making permanent means harder to estimate. "
            "For a fully observed single arm, the long-run mean-noise scale is "
            r"$q_i/(1-\sum_k a_{i,k})^2$; it is about 156 for the persistent profile. "
            "This full-observation scale illustrates the difficulty, without replacing the "
            "actual schedule-dependent likelihood.")
        interpretation.append("For the same persistent state-UCB policy, mean pseudo-regret "
            f"is ${a['mean_pseudo_regret_per_round']:.3f}$ per round, while actual reward regret "
            "against the stationary mean is "
            f"${a['stationary_mean_reward_regret_per_round']:.3f}$ with interval "
            f"$[{a['stationary_mean_reward_regret_per_round_ci_low']:.3f},"
            f"{a['stationary_mean_reward_regret_per_round_ci_high']:.3f}]$. "
            "The policy earns more than the best permanent mean by using predictable fluctuations, "
            "despite often choosing inferior permanent locations.")
    improvements=[r['improvement'] for r in pairs if r['horizon']==h
        and r['candidate']=='joint_predictive_ts' and r['baseline']=='joint_state_ts'
        and r['metric']=='oracle_regret_per_round']
    if improvements:
        interpretation.append("Removing fresh-innovation variance from Thompson draws improves "
            f"oracle regret by {min(improvements):.3f}--{max(improvements):.3f} per round "
            "across these configurations. It does not uniformly improve the UCB rule. "
            "For homogeneous filters, adding a common positive variance inside a square root "
            "compresses differences between optimism bonuses; finite-budget performance also "
            "depends on exploration scale. These experiments compare fixed practical scales, "
            "not optimally tuned policy families.")
    (output/"interpretation.tex").write_text("\n\n".join(interpretation)+"\n")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,default=DEFAULT)
    parser.add_argument("--allow-partial",action="store_true")
    args=parser.parse_args();output=args.input
    metadata=json.loads((output/"metadata.json").read_text())
    rows=[json.loads(s) for s in (output/"runs.jsonl").read_text().splitlines() if s.strip()]
    best_means={m["config"]:max(m["fixed_means"]) for m in metadata["models"]}
    for row in rows:
        row.setdefault("stationary_mean_reward_regret",row["horizon"]*best_means[row["config"]]-row["cumulative_reward"])
        row.setdefault("stationary_mean_reward_regret_per_round",best_means[row["config"]]-row["cumulative_reward"]/row["horizon"])
    assert len({(r["config"],r["policy"],r["horizon"],r["seed"]) for r in rows})==len(rows)
    # Benchmarks plus latent counterfactual path give an independent bookkeeping identity.
    by_world={}
    for r in rows:
        by_world.setdefault((r["config"],r["seed"],r["horizon"]),{})[r["policy"]]=r
        assert r["oracle_regret"]>=-1e-8 and r["mean_pseudo_regret"]>=-1e-8
        assert abs(r["oracle_regret_per_round"]*r["horizon"]-r["oracle_regret"])<1e-6
    for group in by_world.values():
        if "mean_oracle" not in group:
            continue
        for r in group.values():
            assert abs(r["oracle_regret"]-group["mean_oracle"]["oracle_regret"]
                       -r["fixed_best_reward_regret"])<1e-6
    final=[r for r in rows if r["horizon"]==metadata["horizon"]]
    expected=len(metadata["models"])*len(metadata["requested_policies"])*metadata["runs"]
    expected_keys={(m["config"],p,metadata["horizon"],s) for m in metadata["models"]
                   for p in metadata["requested_policies"] for s in range(metadata["runs"])}
    actual_keys={(r["config"],r["policy"],r["horizon"],r["seed"]) for r in final}
    complete=actual_keys==expected_keys
    if not complete and not args.allow_partial:
        raise ValueError(f"Incomplete experiment: {len(final)} / {expected} terminal rows")
    summary,lookup=summarize(rows);pairs=paired(rows)
    write_csv(output/"checkpoints.csv",sorted(rows,key=lambda r:(r["config"],r["seed"],r["policy"],r["horizon"])))
    write_csv(output/"summary.csv",summary);write_csv(output/"paired.csv",pairs)
    floors=oracle_floor(metadata);write_csv(output/"oracle_floor.csv",floors)
    write_findings(output,metadata,lookup,pairs,floors,complete)
    write_tex(output,metadata,lookup,floors,pairs);make_plots(output,metadata,lookup,floors)
    (output/"analysis_checks.json").write_text(json.dumps({"complete":complete,
        "terminal_rows":len(final),"expected_terminal_rows":expected,
        "bookkeeping_identity_verified":True,"nonnegative_regret_metrics_verified":True,
        "no_duplicate_rows":True,"floor_mc_samples_per_configuration":200000,
        "python":platform.python_version(),"numpy":np.__version__,"matplotlib":matplotlib.__version__},indent=2)+"\n")
    print(f"Analyzed {len(rows)} checkpoint rows; complete={complete}. Outputs in {output}")


if __name__=="__main__":
    main()
