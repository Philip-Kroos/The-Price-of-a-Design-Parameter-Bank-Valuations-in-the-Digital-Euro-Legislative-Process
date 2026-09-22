import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import abnormal_returns, second_stage
ex = pd.read_csv("data/derived/bank_exposure_2023q1.csv"); eb = ex[ex.group=="bank"]
Z = dict(zip(ex.ticker, (ex.dep_share-eb.dep_share.mean())/eb.dep_share.std()))
p = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"])
R2 = pd.read_csv("data/derived/returns_daily.csv", index_col=0, parse_dates=True)
F = pd.read_csv("data/derived/ff3_europe_daily.csv", parse_dates=["date"]).set_index("date")
fu = pd.read_csv("data/hand/firm_universe_v0.csv"); fu = fu[fu.ticker_guess.isin(R2.columns)]
US = {"MA","V","AXP","PYPL","GPN","AAPL","GOOGL","AMZN","META"}
eu = [t for t in fu.ticker_guess if t not in US]; us = [t for t in fu.ticker_guess if t in US]
evd = sorted(p.event_date.unique()); com = R2.index.intersection(F.index)
AR = pd.concat([abnormal_returns(R2.loc[com, eu], F.loc[com, ["mkt_rf","smb","hml"]], evd),
                abnormal_returns(R2[us], R2[["^GSPC"]].rename(columns={"^GSPC":"mkt"}), evd)], axis=1)
T = pd.read_csv("data/hand/event_timing.csv", parse_dates=["date"]); tim = dict(zip(T.date, T.timing))
rows = []
for d in evd:
    pos = AR.index.searchsorted(d); t = tim.get(d, "unknown")
    win = AR.iloc[pos:pos+1] if t=="before_close" else (AR.iloc[pos+1:pos+2] if t=="after_close" else AR.iloc[pos:pos+2])
    s = win.sum(min_count=1)
    for rr in p[p.event_date==d].itertuples():
        v = s.get(rr.firm, np.nan)
        if np.isfinite(v): rows.append(dict(event_date=d, firm=rr.firm, car=v, group=rr.group, direction=rr.direction))
q = pd.DataFrame(rows); q["grp"] = q.group.replace({"device":"gate","bigtech":"gate"}); q["z"] = q.firm.map(Z)
def build(q, zz=None):
    q = q.copy(); z = q.z if zz is None else zz
    q["x_bank"] = np.where(q.grp=="bank", z*q.direction, 0.0)
    for nm,g in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]: q[nm] = np.where(q.grp==g, q.direction, 0.0)
    return q
R = ["x_bank","d_bank","d_pay","d_gate"]
qb = build(q); r = second_stage(qb, R); b0, se0 = r["beta"][0], r["se_jackknife"][0]
banks = sorted(q[q.grp=="bank"].firm.unique()); zb = np.array([Z[b] for b in banks]); rng = np.random.default_rng(31); null=[]
for _ in range(999):
    mp = dict(zip(banks, rng.permutation(zb))); null.append(second_stage(build(q, q.firm.map(mp)), R)["beta"][0])
null = np.array(null); p_perm = (1+(np.abs(null)>=abs(b0)).sum())/1000
# wild cluster bootstrap, null imposed, clusters = firms
d = qb.dropna(subset=["car"]+R).reset_index(drop=True)
firms = sorted(d.firm.unique()); fi = d.firm.map({f:i for i,f in enumerate(firms)}).to_numpy()
evs = sorted(d.event_date.unique()); ei = d.event_date.map({e:i for i,e in enumerate(evs)}).to_numpy()
def design(cols):
    n=len(d); Zm=np.zeros((n,len(firms)+len(evs)-1)); Zm[np.arange(n),fi]=1
    m=ei>0; Zm[np.arange(n)[m], len(firms)+ei[m]-1]=1; return np.hstack([d[cols].to_numpy(float), Zm])
Xf, Xr, y = design(R), design(R[1:]), d.car.to_numpy(float)
cr,*_ = np.linalg.lstsq(Xr, y, rcond=None); fit0 = Xr@cr; u0 = y-fit0
cf,*_ = np.linalg.lstsq(Xf, y, rcond=None); bs=[]
for _ in range(999):
    w = rng.choice([-1.0,1.0], size=len(firms))[fi]; cb,*_ = np.linalg.lstsq(Xf, fit0+w*u0, rcond=None); bs.append(cb[0])
bs=np.array(bs); p_wild=(1+(np.abs(bs)>=abs(cf[0])).sum())/1000
out = dict(theta=float(b0), se=float(se0), ci=[float(b0-1.96*se0), float(b0+1.96*se0)], p_perm=float(p_perm), p_wild=float(p_wild))
json.dump(out, open("output/ts_inference.json","w"), indent=1)
print("timestamp-aligned: theta %.3f pp, se %.3f, 95%% CI [%.2f, %.2f], p_perm %.3f, p_wild %.3f" % (b0*100, se0*100, (b0-1.96*se0)*100, (b0+1.96*se0)*100, p_perm, p_wild))
