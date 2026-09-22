"""Round 4: (a) design-only power/MDE on the actual structure; (b) timestamp-robust specification."""
import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import abnormal_returns, second_stage
ex = pd.read_csv("data/derived/bank_exposure_2023q1.csv"); eb = ex[ex.group=="bank"]
Z = dict(zip(ex.ticker, (ex.dep_share-eb.dep_share.mean())/eb.dep_share.std()))
p = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"])
p["grp"] = p.group.replace({"device":"gate","bigtech":"gate"}); p["z"] = p.firm.map(Z)
ev = pd.read_csv("data/hand/event_coding_v1.csv", dtype=str); ev["date"] = pd.to_datetime(ev.date)
IMPL = {"E01","E03","E11","E20","E23","E24"}; DESIGN = {"E12","E14","E17","E22","E26","E19"}
typ = {}
for r in ev.itertuples():
    t = "impl" if r.event_id in IMPL else ("design" if r.event_id in DESIGN else "other")
    typ[r.date] = t if typ.get(r.date) in (None, "other") else typ[r.date]
drop = set(ev[ev.event_id.isin(["E04","E06"])].date)
q0 = p[~p.event_date.isin(drop)].copy(); q0["etype"] = q0.event_date.map(typ)
def build(q):
    q = q.copy()
    for t in ["design","impl"]:
        m = (q.grp=="bank") & (q.etype==t); q[f"x_{t}"] = np.where(m, q.z*q.direction, 0.0)
    for nm,g in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]: q[nm] = np.where(q.grp==g, q.direction, 0.0)
    return q
R = ["x_design","x_impl","d_bank","d_pay","d_gate"]
# (a) power: replace CAR by theta * x_design + noise drawn from the empirical residual sd
qb = build(q0); base = second_stage(qb, R)
sd = float(qb.car.std()); rng = np.random.default_rng(4); res = {}
for th in [0.0, 0.002, 0.003, 0.004, 0.005, 0.006, 0.008]:
    hits = []
    for _ in range(300):
        s = qb.copy(); s["car"] = th*s.x_design + rng.normal(0, sd, len(s))
        r = second_stage(s, R); hits.append(abs(r["t"][0]) > 1.96)
    res[th] = float(np.mean(hits))
print("design-only power (sd of CAR %.4f):" % sd, {f"{k*100:.1f}pp": round(v, 2) for k, v in res.items()})
# (b) timestamp-robust: before close -> day 0, after close -> day +1, unknown -> days 0 and +1
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
    win = AR.iloc[pos:pos+1] if t == "before_close" else (AR.iloc[pos+1:pos+2] if t == "after_close" else AR.iloc[pos:pos+2])
    s = win.sum(min_count=1)
    sub = p[p.event_date==d]
    for rr in sub.itertuples():
        v = s.get(rr.firm, np.nan)
        if np.isfinite(v): rows.append(dict(event_date=d, firm=rr.firm, car=v, group=rr.group, direction=rr.direction))
pt = pd.DataFrame(rows); pt["grp"] = pt.group.replace({"device":"gate","bigtech":"gate"}); pt["z"] = pt.firm.map(Z)
pt["x_bank"] = np.where(pt.grp=="bank", pt.z*pt.direction, 0.0)
for nm,g in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]: pt[nm] = np.where(pt.grp==g, pt.direction, 0.0)
rt = second_stage(pt, ["x_bank","d_bank","d_pay","d_gate"])
print("timestamp-robust main spec: theta %.3f pp, t %.2f, events %d" % (rt["beta"][0]*100, rt["t"][0], pt.event_date.nunique()))
print("timing counts:", T.timing.value_counts().to_dict())
json.dump(dict(power_design=res, sd_car=sd, ts_theta=float(rt["beta"][0]), ts_t=float(rt["t"][0])), open("output/round4.json","w"), indent=1)
