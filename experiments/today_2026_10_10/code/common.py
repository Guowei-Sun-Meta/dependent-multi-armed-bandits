from pathlib import Path
import hashlib
import importlib.util
import json
import numpy as np
import pandas as pd
from scipy.stats import t

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
OUT = HERE / 'results'
SEED = 20261010

def source_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=lambda x: x.item() if isinstance(x, np.generic) else str(x))+'\n')

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def interval(x):
    x=np.asarray(x, float); n=len(x); m=float(x.mean())
    d=float(t.ppf(.975,n-1)*x.std(ddof=1)/np.sqrt(n)) if n>1 else float('nan')
    return m, m-d, m+d

def wilson(k,n):
    z=1.95996398454; p=k/n; den=1+z*z/n
    mid=(p+z*z/(2*n))/den
    half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return mid-half,mid+half
