import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import second_stage
ex = pd.read_csv("data/derived/bank_exposure_2019q4.csv"); eb = ex[ex.group=="bank"]
Z = dict(zip(ex.ticker, (ex.dep_share_2019-eb.dep_share_2019.mean())/eb.dep_share_2019.std()))
q = pd.read_csv("output/car_panel_early.csv", parse_dates=["event_date"]); q["z"] = q.firm.map(Z)
def build(q, zz=None):
    q = q.copy(); z = q.z if zz is None else zz
    q["x_bank"] = np.where(q.grp=="bank", z*q.direction, 0.0)
    for nm,g in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]: q[nm] = np.where(q.grp==g, q.direction, 0.0)
    return q
R = ["x_bank","d_bank","d_pay","d_gate"]
r = second_stage(build(q), R)
banks = sorted(q[q.grp=="bank"].firm.unique()); zb = np.array([Z[b] for b in banks]); rng = np.random.default_rng(12); null=[]
for _ in range(999):
    mp = dict(zip(banks, rng.permutation(zb))); null.append(second_stage(build(q, q.firm.map(mp)), R)["beta"][0])
null=np.array(null); pp=(1+(np.abs(null)>=abs(r["beta"][0])).sum())/1000
print("EARLY with Dec-2019 exposure: theta %.3f pp per SD, se %.3f, t %.2f, p_perm %.3f" % (r["beta"][0]*100, r["se_jackknife"][0]*100, r["t"][0], pp))
b = q[(q.grp=="bank") & (q.direction!=0)]
rows = {}
for d, g in b.groupby("event_date"):
    X = np.column_stack([np.ones(len(g)), g.z]); c,*_ = np.linalg.lstsq(X, g.car, rcond=None)
    e = g.car - X@c; se = np.sqrt((e**2).sum()/(len(g)-2)/((g.z-g.z.mean())**2).sum())
    rows[str(d.date())] = dict(signed=float(c[1]*g.direction.iloc[0]*100), se=float(se*100))
    print(d.date(), "signed slope %.3f (se %.3f)" % (c[1]*g.direction.iloc[0]*100, se*100))
json.dump(dict(theta=float(r["beta"][0]), t=float(r["t"][0]), p_perm=float(pp), events=rows), open("output/early_results_2019exposure.json","w"), indent=1)
