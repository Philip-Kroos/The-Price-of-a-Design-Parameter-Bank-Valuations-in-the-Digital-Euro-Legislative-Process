import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import second_stage
from src.ecb_rate import load_dfr_daily
out = {}
# euro risk-free: daily ECB deposit facility rate
dfr = load_dfr_daily()
# ---- (3) 2020 positive control with strictly pre-event betas -------------------------------------------
p = pd.read_csv("data/raw/prices_2019_2021.csv", parse_dates=["date"])
W = p.pivot_table(index="date", columns="ticker", values="close").sort_index(); R = np.log(W).diff()
raw = open("data/raw/Europe_3_Factors_Daily.csv", encoding="latin-1").read().splitlines()
st = next(i for i,l in enumerate(raw) if l.strip().startswith(",Mkt-RF")); rows=[]
for l in raw[st+1:]:
    q=[x.strip() for x in l.split(",")]
    if len(q)==5 and q[0].isdigit(): rows.append((pd.to_datetime(q[0]), *[float(v)/100 for v in q[1:]]))
FF = pd.DataFrame(rows, columns=["date","mkt_rf","smb","hml","rf"]).set_index("date")
ex = pd.read_csv("data/derived/bank_exposure_2019q4.csv"); eb = ex[ex.group=="bank"]
Z = dict(zip(ex.ticker, (ex.dep_share_2019-eb.dep_share_2019.mean())/eb.dep_share_2019.std()))
banks = [t for t in eb.ticker if t in R.columns]
evs = pd.read_csv("data/hand/events_early_2020_2021.csv", parse_dates=["date"])
def slope_pre_event(day, model):
    idx = R.index; pos = idx.searchsorted(day)
    near = np.zeros(len(idx), bool)
    for dd in evs.date:
        k = idx.searchsorted(dd); near[max(0,k-10):k+11] = True
    win = np.arange(max(0,pos-260), max(0,pos-10)); win = win[~near[win]]
    if model == "ff3":
        X = FF.reindex(idx)[["mkt_rf","smb","hml"]].to_numpy(float); y_adj = lambda y: y
    else:
        rfe = dfr.reindex(idx).ffill().to_numpy(float)
        X = (R["^STOXX"].to_numpy(float) - rfe)[:, None]; y_adj = lambda y: y - rfe
    cars, zs = [], []
    for b in banks:
        y = y_adj(R[b].to_numpy(float)); ok = win[np.isfinite(y[win]) & np.all(np.isfinite(X[win]), axis=1)]
        if len(ok) < 60 or not np.isfinite(y[pos]): continue
        A = np.column_stack([np.ones(len(ok)), X[ok]]); c,*_ = np.linalg.lstsq(A, y[ok], rcond=None)
        cars.append(y[pos] - (c[0] + X[pos] @ c[1:])); zs.append(Z[b])
    zs, cars = np.array(zs), np.array(cars)
    Xs = np.column_stack([np.ones(len(zs)), zs]); c,*_ = np.linalg.lstsq(Xs, cars, rcond=None)
    e = cars - Xs@c; se = np.sqrt((e**2).sum()/(len(zs)-2)/((zs-zs.mean())**2).sum())
    return float(c[1]*100), float(se*100), len(zs)
for lab, day, sign in [("report_2020_10_02", "2020-10-02", -1), ("cap_2021_02_10", "2021-02-10", 1)]:
    for m in ["ff3", "stoxx_excess"]:
        s, se, n = slope_pre_event(pd.Timestamp(day), m)
        out[f"{lab}_{m}"] = dict(signed=sign*s, se=se, n=n)
        print(f"{lab:20s} {m:13s} signed slope {sign*s:6.3f} (se {se:.3f}, n={n})")
json.dump(out, open("output/round10_early.json","w"), indent=1)
