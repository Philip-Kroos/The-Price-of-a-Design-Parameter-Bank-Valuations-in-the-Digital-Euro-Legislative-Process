"""Alternative dating of two events, as announced in Sections 2.3 and 2.6.

(a) Council position: Council working document date, 17 December 2025, instead of the press release, 19 December 2025.
(b) Rapporteur's draft report: presentation to the committee, 5 November 2025, instead of the document date, 3 November 2025.
Each variant moves one event date, re-estimates the first stage with the moved date in the exclusion band,
and re-estimates the main deposit-exposure specification in the one-day window.
Run from the repository root:  python src/run_alt_dates.py
"""
import sys; sys.path.insert(0, ".")
import json, numpy as np, pandas as pd
from src.eventstudy import abnormal_returns, cars, second_stage

R = pd.read_csv("data/derived/returns_daily.csv", index_col=0, parse_dates=True)
F = pd.read_csv("data/derived/ff3_europe_daily.csv", parse_dates=["date"]).set_index("date")
fu = pd.read_csv("data/hand/firm_universe_v0.csv"); fu = fu[fu.ticker_guess.isin(R.columns)]
grp = dict(zip(fu.ticker_guess, fu.group))
p0 = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"])
evd0 = sorted(p0.event_date.unique()); dir0 = p0.groupby(["event_date", "firm"]).direction.first()
ex = pd.read_csv("data/derived/bank_exposure_2023q1.csv"); eb = ex[ex.group == "bank"]
Z = dict(zip(ex.ticker, (ex.dep_share - eb.dep_share.mean()) / eb.dep_share.std()))
US = {"MA", "V", "AXP", "PYPL", "GPN", "AAPL", "GOOGL", "AMZN", "META"}
eu = [t for t in fu.ticker_guess if t not in US]; us = [t for t in fu.ticker_guess if t in US]
com = R.index.intersection(F.index)


def estimate(move):
    old, new = (pd.Timestamp(d) for d in move) if move else (None, None)
    evd = sorted([new if d == old else d for d in evd0])
    dirmap = {((new if d == old else d), f): v for (d, f), v in dir0.items()}
    a = abnormal_returns(R.loc[com, eu], F.loc[com, ["mkt_rf", "smb", "hml"]], evd)
    b = abnormal_returns(R[us], R[["^GSPC"]].rename(columns={"^GSPC": "mkt"}), evd)
    c = cars(pd.concat([a, b], axis=1), evd, window=(0, 0))
    c["direction"] = [dirmap.get((d, f), np.nan) for d, f in zip(c.event_date, c.firm)]
    c = c.dropna(subset=["direction"])
    c["grp"] = c.firm.map(grp).replace({"device": "gate", "bigtech": "gate"}); c["z"] = c.firm.map(Z)
    c["x_bank"] = np.where(c.grp == "bank", c.z * c.direction, 0.0)
    for nm, g in [("d_bank", "bank"), ("d_pay", "payments"), ("d_gate", "gate")]:
        c[nm] = np.where(c.grp == g, c.direction, 0.0)
    r = second_stage(c, ["x_bank", "d_bank", "d_pay", "d_gate"])
    return dict(theta=float(r["beta"][0] * 100), t=float(r["t"][0]), n=int(r["n"]), events=int(r["events"]))


out = {"baseline": estimate(None),
       "council_17dec2025": estimate(("2025-12-19", "2025-12-17")),
       "draft_report_5nov2025": estimate(("2025-11-03", "2025-11-05"))}
for k, v in out.items():
    print(f"{k:24s} theta {v['theta']:.3f}  t {v['t']:.2f}  n {v['n']}  events {v['events']}")
json.dump(out, open("output/alt_dates.json", "w"), indent=1)
