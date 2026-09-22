"""Main estimation: group-level specification (binary exposure), pre-specified in PAP v1.11."""
import sys; sys.path.insert(0, ".")
import json, numpy as np, pandas as pd
from src.eventstudy import abnormal_returns, cars, second_stage

R = pd.read_csv("data/derived/returns_daily.csv", index_col=0, parse_dates=True)
F = pd.read_csv("data/derived/ff3_europe_daily.csv", parse_dates=["date"]).set_index("date")
firms = pd.read_csv("data/hand/firm_universe_v0.csv")
firms = firms[firms.ticker_guess.isin(R.columns)].copy()
ev = pd.read_csv("data/hand/event_coding_v1.csv", dtype=str)
ev["date"] = pd.to_datetime(ev.date)
ev = ev[ev.status.str.startswith("coded") & (ev.date <= F.index.max())].copy()
for c in ["dir_banks", "dir_psp", "dir_bigtech"]:
    ev[c] = pd.to_numeric(ev[c], errors="coerce").fillna(0.0)
# pre-specified collision rule: same-date events are one event with combined coding (sum, clipped to [-1,1])
agg = ev.groupby("date").agg(dir_banks=("dir_banks","sum"), dir_psp=("dir_psp","sum"),
                             dir_bigtech=("dir_bigtech","sum"),
                             procedural=("procedural", lambda x: "1" if (x.astype(str)=="1").all() else "0")).reset_index()
for c in ["dir_banks","dir_psp","dir_bigtech"]:
    agg[c] = agg[c].clip(-1, 1)
ev = agg
ev_dates = ev.date.tolist()

US = {"MA","V","AXP","PYPL","GPN","AAPL","GOOGL","AMZN","META"}
eu_t = [t for t in firms.ticker_guess if t not in US]
us_t = [t for t in firms.ticker_guess if t in US]
# European firms: FF3 Europe (registered); US firms: market model on S&P 500 (logged deviation)
common = R.index.intersection(F.index)
ar_eu = abnormal_returns(R.loc[common, eu_t], F.loc[common, ["mkt_rf","smb","hml"]], ev_dates)
spx = R[["^GSPC"]].rename(columns={"^GSPC": "mkt"})
ar_us = abnormal_returns(R[us_t], spx, ev_dates)
AR = pd.concat([ar_eu, ar_us], axis=1)

def panel(window):
    c = cars(AR, ev_dates, window=window)
    g = dict(zip(firms.ticker_guess, firms.group))
    c["group"] = c.firm.map(g)
    colmap = {"bank": "dir_banks", "payments": "dir_psp", "device": "dir_bigtech", "bigtech": "dir_bigtech"}
    d = ev.set_index("date")
    def direction(row):
        col = colmap.get(row.group)
        return 0.0 if col is None else float(d.loc[row.event_date, col])
    c["direction"] = c.apply(direction, axis=1)
    c["proc"] = c.event_date.map(dict(zip(ev.date, ev.procedural.astype(str) == "1")))
    for gname, col in [("bank","dir_banks"),("payments","dir_psp"),("gate","dir_bigtech")]:
        members = {"bank":["bank"], "payments":["payments"], "gate":["device","bigtech"]}[gname]
        c[f"dir_{gname}"] = np.where(c.group.isin(members), c.direction, 0.0)
    return c

out = {}
for name, win in [("w00", (0, 0)), ("w01", (0, 1))]:
    p = panel(win)
    p.to_csv(f"output/car_panel_{name}.csv", index=False)
    pooled = second_stage(p, ["direction"])
    groups = second_stage(p, ["dir_bank", "dir_payments", "dir_gate"])
    out[name] = dict(n=pooled["n"], firms=pooled["firms"], events=pooled["events"],
        pooled=dict(beta=float(pooled["beta"][0]), se_cl=float(pooled["se_cluster"][0]),
                    se_jk=float(pooled["se_jackknife"][0]), t=float(pooled["t"][0])),
        groups={nm: dict(beta=float(b), se_jk=float(s), t=float(t)) for nm, b, s, t in
                zip(groups["names"], groups["beta"], groups["se_jackknife"], groups["t"])})
json.dump(out, open("output/main_results.json", "w"), indent=1)
for k, v in out.items():
    print(f"\n=== window {k}: n={v['n']} firms={v['firms']} events={v['events']}")
    pp = v["pooled"]; print(f"pooled   beta {pp['beta']*100:6.3f} pp  se_jk {pp['se_jk']*100:5.3f}  t {pp['t']:5.2f}")
    for nm, g in v["groups"].items():
        print(f"{nm:12s} beta {g['beta']*100:6.3f} pp  se_jk {g['se_jk']*100:5.3f}  t {g['t']:5.2f}")
