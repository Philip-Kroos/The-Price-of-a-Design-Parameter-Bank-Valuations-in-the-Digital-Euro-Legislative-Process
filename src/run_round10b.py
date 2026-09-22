import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import abnormal_returns, cars, second_stage
from src.firststage import R, F, EU, USL, GROUP, AR, window_car
from src.ecb_rate import load_dfr_daily
dfr = load_dfr_daily()
p0 = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"])
evd = sorted(p0.event_date.unique()); dirmap = p0.groupby(["event_date","firm"]).direction.first()
ex = pd.read_csv("data/derived/bank_exposure_2023q1.csv"); eb = ex[ex.group=="bank"]
Z = dict(zip(ex.ticker, (ex.dep_share-eb.dep_share.mean())/eb.dep_share.std()))
ev = pd.read_csv("data/hand/event_coding_v1.csv", dtype=str); ev["date"] = pd.to_datetime(ev.date)
IMPL = {"E01","E03","E11","E20","E23","E24"}; DESIGN = {"E12","E14","E17","E22","E26","E19"}
typ = {}
for r in ev.itertuples():
    t = "impl" if r.event_id in IMPL else ("design" if r.event_id in DESIGN else "other")
    typ[r.date] = t if typ.get(r.date) in (None, "other") else typ[r.date]
drop = set(ev[ev.event_id.isin(["E04","E06"])].date)
T = pd.read_csv("data/hand/event_timing.csv", parse_dates=["date"]); tim = dict(zip(T.date, T.timing))
# STOXX market model in excess returns (euro risk-free = ECB deposit facility rate); US firms: S&P 500 in USD as before
rfe = dfr.reindex(R.index).ffill()
Rx = R[EU].sub(rfe, axis=0); mx = (R["^STOXX"] - rfe).rename("mkt")
A = pd.concat([abnormal_returns(Rx, mx.to_frame(), evd), abnormal_returns(R[USL], R[["^GSPC"]].rename(columns={"^GSPC":"mkt"}), evd)], axis=1)
def build(c):
    c["direction"] = [dirmap.get((dd, f), np.nan) for dd, f in zip(c.event_date, c.firm)]
    c = c.dropna(subset=["direction"]).copy(); c["grp"] = c.firm.map(GROUP).replace({"device":"gate","bigtech":"gate"})
    c["z"] = c.firm.map(Z); c["etype"] = c.event_date.map(typ)
    for nm,g in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]: c[nm] = np.where(c.grp==g, c.direction, 0.0)
    return c
def main(c):
    c = c.copy(); c["x_bank"] = np.where(c.grp=="bank", c.z*c.direction, 0.0)
    r = second_stage(c, ["x_bank","d_bank","d_pay","d_gate"]); return round(r["beta"][0]*100,3), round(r["t"][0],2)
def design(c):
    c = c[~c.event_date.isin(drop)].copy()
    for t in ["design","impl"]:
        m = (c.grp=="bank") & (c.etype==t); c[f"x_{t}"] = np.where(m, c.z*c.direction, 0.0)
    r = second_stage(c, ["x_design","x_impl","d_bank","d_pay","d_gate"]); return round(r["beta"][0]*100,3), round(r["t"][0],2)
out = {}
c1 = build(cars(A, evd, window=(0,0)))
rows=[]
for dd in evd:
    s = window_car(A, dd, tim.get(dd, "unknown"))
    for f, v in s.items():
        if np.isfinite(v): rows.append(dict(event_date=dd, firm=f, car=float(v)))
cts = build(pd.DataFrame(rows))
out["stoxx_excess"] = dict(one_day=main(c1), aligned=main(cts), design=design(c1))
print("STOXX excess-return market model:", out["stoxx_excess"])
# (1) provider sensitivity: binary spec with the Council provider direction set to 0
q = build(cars(AR(evd, "ff3usd"), evd, window=(0,0)))
q["dir_bank"], q["dir_payments"], q["dir_gate"] = q.d_bank, q.d_pay, q.d_gate
base = second_stage(q, ["dir_bank","dir_payments","dir_gate"])
council = pd.Timestamp("2025-12-19"); q2 = q.copy(); q2.loc[(q2.event_date==council) & (q2.grp=="payments"), "dir_payments"] = 0.0
sens = second_stage(q2, ["dir_bank","dir_payments","dir_gate"])
out["provider_base"] = dict(beta=round(base["beta"][1]*100,3), t=round(base["t"][1],2))
out["provider_council0"] = dict(beta=round(sens["beta"][1]*100,3), t=round(sens["t"][1],2))
print("providers: base", out["provider_base"], "| Council provider direction = 0:", out["provider_council0"])
json.dump(out, open("output/round10_late.json","w"), indent=1)

# permutation and wild bootstrap for the aligned STOXX excess-return specification
c = cts.copy(); banks = sorted(c[c.grp=="bank"].firm.unique()); zb = np.array([Z[b] for b in banks])
def fitz(zz):
    s = c.copy(); s["x_bank"] = np.where(s.grp=="bank", zz*s.direction, 0.0)
    return second_stage(s, ["x_bank","d_bank","d_pay","d_gate"])
r0 = fitz(c.z); b0 = r0["beta"][0]; rng = np.random.default_rng(77)
null = [fitz(c.firm.map(dict(zip(banks, rng.permutation(zb)))))["beta"][0] for _ in range(499)]
pp = (1+(np.abs(np.array(null))>=abs(b0)).sum())/500
dd = c.copy(); dd["x_bank"] = np.where(dd.grp=="bank", dd.z*dd.direction, 0.0); dd = dd.dropna(subset=["car"]).reset_index(drop=True)
fs = sorted(dd.firm.unique()); fi = dd.firm.map({f:i for i,f in enumerate(fs)}).to_numpy()
es = sorted(dd.event_date.unique()); ei = dd.event_date.map({e:i for i,e in enumerate(es)}).to_numpy()
def X(cols):
    n=len(dd); M=np.zeros((n,len(fs)+len(es)-1)); M[np.arange(n),fi]=1; m=ei>0; M[np.arange(n)[m],len(fs)+ei[m]-1]=1
    return np.hstack([dd[cols].to_numpy(float), M])
Xf, Xr, y = X(["x_bank","d_bank","d_pay","d_gate"]), X(["d_bank","d_pay","d_gate"]), dd.car.to_numpy(float)
cr,*_ = np.linalg.lstsq(Xr,y,rcond=None); f0=Xr@cr; u0=y-f0; cf,*_=np.linalg.lstsq(Xf,y,rcond=None); bs=[]
for _ in range(999):
    w = rng.choice([-1.0,1.0], size=len(fs))[fi]; cb,*_ = np.linalg.lstsq(Xf, f0+w*u0, rcond=None); bs.append(cb[0])
pw = (1+(np.abs(np.array(bs))>=abs(cf[0])).sum())/1000
se = r0["se_jackknife"][0]
out["stoxx_excess_aligned_inference"] = dict(theta=float(b0*100), se=float(se*100), ci=[float((b0-1.96*se)*100), float((b0+1.96*se)*100)], p_perm=float(pp), p_wild=float(pw))
print("aligned STOXX excess: theta %.3f se %.3f CI [%.2f,%.2f] p_perm %.3f p_wild %.3f" % (b0*100, se*100, (b0-1.96*se)*100, (b0+1.96*se)*100, pp, pw))
json.dump(out, open("output/round10_late.json","w"), indent=1)
