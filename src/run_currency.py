import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.firststage import AR, window_car, GROUP
from src.eventstudy import cars, second_stage
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
def panel(A, mode):
    if mode in ("w00","w01"):
        c = cars(A, evd, window=(0,0) if mode=="w00" else (0,1))
    else:
        rows=[]
        for d in evd:
            s = window_car(A, d, tim.get(d, "unknown"))
            for f, v in s.items():
                if np.isfinite(v): rows.append(dict(event_date=d, firm=f, car=float(v)))
        c = pd.DataFrame(rows)
    c["direction"] = [dirmap.get((d, f), np.nan) for d, f in zip(c.event_date, c.firm)]
    c = c.dropna(subset=["direction"]); c["grp"] = c.firm.map(GROUP).replace({"device":"gate","bigtech":"gate"})
    c["z"] = c.firm.map(Z); c["etype"] = c.event_date.map(typ); return c
def lv(q):
    for nm,g in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]: q[nm] = np.where(q.grp==g, q.direction, 0.0)
    return q
def main(q):
    q = lv(q.copy()); q["x_bank"] = np.where(q.grp=="bank", q.z*q.direction, 0.0)
    r = second_stage(q, ["x_bank","d_bank","d_pay","d_gate"]); return r["beta"][0]*100, r["se_jackknife"][0]*100, r["t"][0], r["n"]
def design(q):
    q = lv(q[~q.event_date.isin(drop)].copy())
    for t in ["design","impl"]:
        m = (q.grp=="bank") & (q.etype==t); q[f"x_{t}"] = np.where(m, q.z*q.direction, 0.0)
    r = second_stage(q, ["x_design","x_impl","d_bank","d_pay","d_gate"]); return r["beta"][0]*100, r["se_jackknife"][0]*100, r["t"][0]
out = {}
for ver in ["ff3usd","local3"]:
    A = AR(evd, ver)
    for mode in ["w00","w01","ts"]:
        q = panel(A, mode); m = main(q); dz = design(q)
        out[f"{ver}_{mode}"] = dict(theta=m[0], se=m[1], t=m[2], n=int(m[3]), design=dz[0], design_se=dz[1], design_t=dz[2])
        print(f"{ver:7s} {mode:4s} main {m[0]:6.3f} (se {m[1]:.3f}, t {m[2]:5.2f}, n {m[3]}) | design {dz[0]:6.3f} (t {dz[2]:5.2f})")
        q.to_csv(f"output/car_{ver}_{mode}.csv", index=False)
json.dump(out, open("output/currency_results.json","w"), indent=1)
