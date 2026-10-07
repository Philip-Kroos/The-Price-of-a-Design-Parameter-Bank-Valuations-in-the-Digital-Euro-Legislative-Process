"""F1 (pre-specified falsification): no exposure slope on procedural dates.

Adds Exposure_i x 1{procedural date} for euro area banks to the main continuous
specification (one-day window) and tests it by permuting exposure across euro area banks.
Run from the repository root after src/run_main.py:  python src/run_f1.py
"""
import sys; sys.path.insert(0, ".")
import json, numpy as np, pandas as pd
from src.eventstudy import second_stage

ex = pd.read_csv("data/derived/bank_exposure_2023q1.csv")
eu = ex[ex.group == "bank"]
Z = dict(zip(ex.ticker, (ex.dep_share - eu.dep_share.mean()) / eu.dep_share.std()))
p = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"])
p["grp"] = p.group.replace({"device": "gate", "bigtech": "gate"})
X = ["x_bank", "x_proc", "d_bank", "d_pay", "d_gate"]

def build(q, z):
    q = q.copy(); q["z"] = q.firm.map(z)
    q["x_bank"] = np.where(q.grp == "bank", q.z * q.direction, 0.0)
    q["x_proc"] = np.where((q.grp == "bank") & (q.proc == True), q.z, 0.0)
    for nm, g in [("d_bank", "bank"), ("d_pay", "payments"), ("d_gate", "gate")]:
        q[nm] = np.where(q.grp == g, q.direction, 0.0)
    return q

r = second_stage(build(p, Z), X)
banks = sorted(p[p.grp == "bank"].firm.unique()); zb = np.array([Z[b] for b in banks])
rng = np.random.default_rng(11); null = []
for _ in range(999):
    null.append(second_stage(build(p, dict(zip(banks, rng.permutation(zb)))), X)["beta"][1])
p_perm = (1 + (np.abs(np.array(null)) >= abs(r["beta"][1])).sum()) / 1000
out = dict(procedural_dates=sorted(p.loc[p.proc == True, "event_date"].dt.strftime("%Y-%m-%d").unique()),
           f1_slope=float(r["beta"][1]), f1_se_jk=float(r["se_jackknife"][1]), f1_t=float(r["t"][1]),
           f1_p_perm=float(p_perm), theta_main=float(r["beta"][0]), n=int(r["n"]))
json.dump(out, open("output/f1_procedural.json", "w"), indent=1)
print(json.dumps(out, indent=1))
