import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import second_stage
p = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"])
ev = pd.read_csv("data/hand/event_coding_v1.csv", dtype=str); ev["date"] = pd.to_datetime(ev.date)

# 1. event-level mean CAR by group (pp)
p["grp"] = p.group.replace({"device": "gate", "bigtech": "gate"})
tab = p.pivot_table(index="event_date", columns="grp", values="car", aggfunc="mean") * 100
dirs = p.groupby(["event_date", "grp"]).direction.first().unstack()
out = tab.round(2).join(dirs.add_prefix("dir_"), how="left")
print("EVENT-LEVEL MEAN CAR (pp) AND CODED DIRECTION"); print(out.to_string())

# 2. F2 placebo: give control banks the bank direction
q = p.copy()
bank_dir = p[p.group == "bank"].groupby("event_date").direction.first()
q["placebo_dir"] = np.where(q.group == "control_bank", q.event_date.map(bank_dir), 0.0)
qq = q[q.group.isin(["control_bank"])].copy()
# compare control banks against payments+gate as reference is not meaningful; instead regress control CAR on bank direction with event FE vs euro banks
both = p[p.group.isin(["bank", "control_bank"])].copy()
both["dir_euro"] = np.where(both.group == "bank", both.direction, 0.0)
both["dir_ctrl"] = np.where(both.group == "control_bank", both.event_date.map(bank_dir), 0.0)
r2 = second_stage(both, ["dir_euro", "dir_ctrl"])
print("\nF2: euro banks vs control banks given the SAME bank direction")
for n, b, s, t in zip(r2["names"], r2["beta"], r2["se_jackknife"], r2["t"]):
    print(f"  {n:10s} beta {b*100:6.3f} pp  se {s*100:5.3f}  t {t:5.2f}")

# 3. F1: procedural events only -> any group CAR differs from controls?
proc_dates = set(ev[ev.procedural == "1"].date)
pp = p[p.event_date.isin(proc_dates)].copy()
print("\nF1: procedural events, mean CAR by group (pp)")
print((pp.groupby("grp").car.mean() * 100).round(3).to_string())

# 4. leave one event out, bank coefficient
res = []
for d in sorted(p.event_date.unique()):
    s = p[p.event_date != d].copy()
    for g, col in [("bank","dir_bank"),("payments","dir_payments"),("gate","dir_gate")]:
        s[col] = np.where(s.grp == g, s.direction, 0.0)
    r = second_stage(s, ["dir_bank", "dir_payments", "dir_gate"])
    res.append(dict(dropped=str(d.date()), bank=r["beta"][0]*100, payments=r["beta"][1]*100, gate=r["beta"][2]*100))
lo = pd.DataFrame(res)
print("\nLEAVE-ONE-EVENT-OUT ranges (pp)")
print(lo[["bank","payments","gate"]].agg(["min","max"]).round(3).to_string())
print("gate coefficient when dropping 2025-12-19:", round(float(lo[lo.dropped=="2025-12-19"].gate.iloc[0]),3))
lo.to_csv("output/leave_one_event_out.csv", index=False)
out.to_csv("output/event_level_cars.csv")
