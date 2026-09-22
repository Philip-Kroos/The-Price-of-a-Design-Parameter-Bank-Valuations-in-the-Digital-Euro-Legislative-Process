import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import abnormal_returns, cars, second_stage
p = pd.read_csv("data/raw/prices_2019_2021.csv", parse_dates=["date"])
W = p.pivot_table(index="date", columns="ticker", values="close").sort_index()
R = np.log(W).diff()
F = pd.read_csv("data/derived/ff3_europe_daily.csv", parse_dates=["date"]).set_index("date")
raw = open("data/raw/Europe_3_Factors_Daily.csv", encoding="latin-1").read().splitlines()
st = next(i for i,l in enumerate(raw) if l.strip().startswith(",Mkt-RF")); rows=[]
for l in raw[st+1:]:
    q=[x.strip() for x in l.split(",")]
    if len(q)==5 and q[0].isdigit(): rows.append((pd.to_datetime(q[0]), *[float(v)/100 for v in q[1:]]))
FF = pd.DataFrame(rows, columns=["date","mkt_rf","smb","hml","rf"]).set_index("date")
ev = pd.read_csv("data/hand/events_early_2020_2021.csv", parse_dates=["date"])
firms = pd.read_csv("data/hand/firm_universe_v0.csv"); firms = firms[firms.ticker_guess.isin(R.columns)]
US = {"MA","V","AXP","PYPL","GPN","AAPL","GOOGL","AMZN","META"}
eu = [t for t in firms.ticker_guess if t not in US]; us = [t for t in firms.ticker_guess if t in US]
com = R.index.intersection(FF.index)
AR = pd.concat([abnormal_returns(R.loc[com, eu], FF.loc[com, ["mkt_rf","smb","hml"]], ev.date),
                abnormal_returns(R[us], R[["^GSPC"]].rename(columns={"^GSPC":"mkt"}), ev.date)], axis=1)
c = cars(AR, ev.date, window=(0,0))
g = dict(zip(firms.ticker_guess, firms.group)); c["group"] = c.firm.map(g)
c["grp"] = c.group.replace({"device":"gate","bigtech":"gate"})
colmap = {"bank":"dir_banks","payments":"dir_psp","gate":"dir_bigtech"}
e = ev.set_index("date")
c["direction"] = [0.0 if colmap.get(gr) is None else float(e.loc[d, colmap[gr]]) for gr, d in zip(c.grp, c.event_date)]
ex = pd.read_csv("data/derived/bank_exposure_2023q1.csv"); eb = ex[ex.group=="bank"]
Z = dict(zip(ex.ticker, (ex.dep_share-eb.dep_share.mean())/eb.dep_share.std())); c["z"] = c.firm.map(Z)
c.to_csv("output/car_panel_early.csv", index=False)
def build(q):
    q = q.copy(); q["x_bank"] = np.where(q.grp=="bank", q.z*q.direction, 0.0)
    for nm,gr in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]: q[nm] = np.where(q.grp==gr, q.direction, 0.0)
    return q
R_ = ["x_bank","d_bank","d_pay","d_gate"]
q = build(c); r = second_stage(q, R_)
# permutation of exposure among euro banks
banks = sorted(q[q.grp=="bank"].firm.unique()); zb = np.array([Z[b] for b in banks]); rng = np.random.default_rng(11); null=[]
for _ in range(999):
    mp = dict(zip(banks, rng.permutation(zb))); s = q.copy(); zz = s.firm.map(mp)
    s["x_bank"] = np.where(s.grp=="bank", zz*s.direction, 0.0); null.append(second_stage(s, R_)["beta"][0])
null=np.array(null); pp=(1+(np.abs(null)>=abs(r["beta"][0])).sum())/1000
out = dict(theta_early=float(r["beta"][0]), se=float(r["se_jackknife"][0]), t=float(r["t"][0]), p_perm=float(pp), n=int(r["n"]))
print("EARLY (2020-21) theta %.3f pp per SD, se %.3f, t %.2f, p_perm %.3f, n %d" % (r["beta"][0]*100, r["se_jackknife"][0]*100, r["t"][0], pp, r["n"]))
# event-level signed slopes
b = q[(q.grp=="bank") & (q.direction!=0)]
for d, gg in b.groupby("event_date"):
    X = np.column_stack([np.ones(len(gg)), gg.z]); cc,*_ = np.linalg.lstsq(X, gg.car, rcond=None)
    ee = gg.car - X@cc; se = np.sqrt((ee**2).sum()/(len(gg)-2)/((gg.z-gg.z.mean())**2).sum())
    print(d.date(), "dir", int(gg.direction.iloc[0]), "signed slope %.3f (se %.3f)" % (cc[1]*gg.direction.iloc[0]*100, se*100), "| mean bank CAR %.2f pp" % (gg.car.mean()*100))
json.dump(out, open("output/early_results.json","w"), indent=1)
