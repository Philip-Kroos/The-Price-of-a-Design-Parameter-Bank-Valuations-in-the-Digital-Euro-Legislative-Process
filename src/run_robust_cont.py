import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import second_stage
ex = pd.read_csv("data/derived/bank_exposure_2023q1.csv"); eu = ex[ex.group=="bank"]
Z = dict(zip(ex.ticker, (ex.dep_share - eu.dep_share.mean())/eu.dep_share.std()))
p = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"])
p["grp"] = p.group.replace({"device":"gate","bigtech":"gate"})
p["z"] = p.firm.map(Z)
def build(q):
    q = q.copy()
    q["x_bank"] = np.where(q.grp=="bank", q.z*q.direction, 0.0)
    for nm,g in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]:
        q[nm] = np.where(q.grp==g, q.direction, 0.0)
    return q
R = ["x_bank","d_bank","d_pay","d_gate"]
base = second_stage(build(p), R); th = base["beta"][0]
out = {"main": float(th)}
# 1. leave one event out
lo = []
for d in sorted(p.event_date.unique()):
    lo.append(second_stage(build(p[p.event_date!=d]), R)["beta"][0])
out["loo_min"], out["loo_max"] = float(min(lo)), float(max(lo))
print("LOO theta range: %.3f to %.3f pp" % (min(lo)*100, max(lo)*100))
# 2. wild cluster bootstrap (null imposed, Rademacher by firm)
q = build(p).dropna(subset=["car"]+R)
firms = sorted(q.firm.unique()); fi = q.firm.map({f:i for i,f in enumerate(firms)}).to_numpy()
evs = sorted(q.event_date.unique()); ei = q.event_date.map({e:i for i,e in enumerate(evs)}).to_numpy()
def design(cols):
    n=len(q); Zm=np.zeros((n,len(firms)+len(evs)-1)); Zm[np.arange(n),fi]=1
    m=ei>0; Zm[np.arange(n)[m], len(firms)+ei[m]-1]=1
    return np.hstack([q[cols].to_numpy(float), Zm])
Xf = design(R); Xr = design(R[1:]); y = q.car.to_numpy(float)
cr,*_ = np.linalg.lstsq(Xr, y, rcond=None); fit0 = Xr@cr; u0 = y-fit0
cf,*_ = np.linalg.lstsq(Xf, y, rcond=None); t0 = cf[0]
rng = np.random.default_rng(3); bs=[]
for _ in range(999):
    w = rng.choice([-1.0,1.0], size=len(firms))[fi]
    yb = fit0 + w*u0
    cb,*_ = np.linalg.lstsq(Xf, yb, rcond=None); bs.append(cb[0])
bs=np.array(bs); pw=(1+(np.abs(bs)>=abs(t0)).sum())/1000
out["p_wild"]=float(pw); print("wild cluster bootstrap p (coefficient): %.3f" % pw)
# 3. surprise split: high-surprise events only (pre-coded dimension)
ev = pd.read_csv("data/hand/event_coding_v1.csv", dtype=str); ev["date"]=pd.to_datetime(ev.date)
hi = set(ev[ev.surprise=="high"].date)
qh = p[p.event_date.isin(hi)]
rh = second_stage(build(qh), R)
out["high_surprise_theta"]=float(rh["beta"][0]); out["high_surprise_t"]=float(rh["t"][0]); out["high_events"]=int(qh.event_date.nunique())
print("high-surprise events only (%d events): theta %.3f pp, t %.2f" % (qh.event_date.nunique(), rh["beta"][0]*100, rh["t"][0]))
# 4. Romano-Wolf style joint check across the three group predictions (binary spec), permutation of event directions
json.dump(out, open("output/robust_continuous.json","w"), indent=1)
