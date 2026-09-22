"""Timing robustness: shift events released after the close to the next trading day, and exclude
events with major same-day confounders. Both decided from documented release circumstances, before estimation."""
import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import abnormal_returns, second_stage
R = pd.read_csv("data/derived/returns_daily.csv", index_col=0, parse_dates=True)
F = pd.read_csv("data/derived/ff3_europe_daily.csv", parse_dates=["date"]).set_index("date")
firms = pd.read_csv("data/hand/firm_universe_v0.csv"); firms = firms[firms.ticker_guess.isin(R.columns)]
p0 = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"])
evd = sorted(p0.event_date.unique())
US = {"MA","V","AXP","PYPL","GPN","AAPL","GOOGL","AMZN","META"}
eu = [t for t in firms.ticker_guess if t not in US]; us = [t for t in firms.ticker_guess if t in US]
com = R.index.intersection(F.index)
AR = pd.concat([abnormal_returns(R.loc[com, eu], F.loc[com, ["mkt_rf","smb","hml"]], evd),
                abnormal_returns(R[us], R[["^GSPC"]].rename(columns={"^GSPC":"mkt"}), evd)], axis=1)
ex = pd.read_csv("data/derived/bank_exposure_2023q1.csv"); eb = ex[ex.group=="bank"]
Z = dict(zip(ex.ticker, (ex.dep_share-eb.dep_share.mean())/eb.dep_share.std()))
def spec(p):
    q = p.copy(); q["grp"] = q.group.replace({"device":"gate","bigtech":"gate"}); q["z"] = q.firm.map(Z)
    q["x_bank"] = np.where(q.grp=="bank", q.z*q.direction, 0.0)
    for nm,g in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]: q[nm] = np.where(q.grp==g, q.direction, 0.0)
    r = second_stage(q, ["x_bank","d_bank","d_pay","d_gate"]); return float(r["beta"][0]), float(r["t"][0]), int(q.event_date.nunique())
out = {}
out["baseline"] = spec(p0)
# (i) European Council 23.10.2025: conclusions adopted at the end of the summit -> next trading day
old, new = pd.Timestamp("2025-10-23"), AR.index[AR.index > pd.Timestamp("2025-10-23")][0]
p1 = p0.copy(); m = p1.event_date == old
p1.loc[m, "car"] = p1.loc[m, "firm"].map(AR.loc[new]); p1.loc[m, "event_date"] = new
out["shift_EUCO_to_next_day"] = spec(p1)
# (ii) exclude events with a documented major same-day confounder
conf = {pd.Timestamp("2025-10-23"): "19th Russia sanctions package adopted the same morning",
        pd.Timestamp("2025-12-19"): "European Council summit of 18-19 December on MFF, enlargement and Ukraine"}
p2 = p0[~p0.event_date.isin(conf)]
out["exclude_confounded"] = spec(p2)
json.dump({k: dict(theta=v[0], t=v[1], events=v[2]) for k, v in out.items()}, open("output/timing_robustness.json","w"), indent=1)
for k, v in out.items(): print(f"{k:28s} theta {v[0]*100:6.3f} pp  t {v[1]:5.2f}  events {v[2]}")
print("next trading day used for EUCO:", new.date())
