import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import second_stage, second_stage_beta
ex = pd.read_csv("data/derived/bank_exposure_2023q1.csv")
eu = ex[ex.group == "bank"]
Z = {}
for m in ["dep_share", "overnight_share"]:
    mu, sd = eu[m].mean(), eu[m].std()
    Z[m] = dict(zip(ex.ticker, (ex[m] - mu) / sd))
out = {}
for win in sys.argv[1:] or ["w01"]:
    p = pd.read_csv(f"output/car_panel_{win}.csv", parse_dates=["event_date"])
    p["grp"] = p.group.replace({"device": "gate", "bigtech": "gate"})
    for m in ["dep_share", "overnight_share"]:
        q = p.copy()
        q["z"] = q.firm.map(Z[m])
        # euro banks: continuous exposure x direction; other treated groups: group-level direction as in v1.12
        q["x_bank"] = np.where(q.grp == "bank", q.z * q.direction, 0.0)
        q["d_bank"] = np.where(q.grp == "bank", q.direction, 0.0)
        q["d_pay"] = np.where(q.grp == "payments", q.direction, 0.0)
        q["d_gate"] = np.where(q.grp == "gate", q.direction, 0.0)
        r = second_stage(q, ["x_bank", "d_bank", "d_pay", "d_gate"])
        # permutation of exposure across euro banks
        rng = np.random.default_rng(7); banks = sorted(q[q.grp == "bank"].firm.unique())
        zb = np.array([Z[m][b] for b in banks]); null = []
        for _ in range(499):
            mp = dict(zip(banks, rng.permutation(zb)))
            s = q.copy(); zz = s.firm.map(mp)
            s["x_bank"] = np.where(s.grp == "bank", zz * s.direction, 0.0)
            null.append(second_stage_beta(s, ["x_bank", "d_bank", "d_pay", "d_gate"])[0])
        null = np.array(null)
        p_perm = (1 + (np.abs(null) >= abs(r["beta"][0])).sum()) / 500
        key = f"{win}_{m}"
        out[key] = dict(theta=float(r["beta"][0]), se_jk=float(r["se_jackknife"][0]), t=float(r["t"][0]),
                        p_perm=float(p_perm), level_bank=float(r["beta"][1]), n=int(r["n"]))
        print(f"{key:22s} theta {r['beta'][0]*100:6.3f} pp per SD  se {r['se_jackknife'][0]*100:5.3f}  t {r['t'][0]:5.2f}  p_perm {p_perm:.3f} | level {r['beta'][1]*100:6.3f}")
    # robustness: drop Credit Agricole (consolidation mismatch)
    q = p[p.firm != "ACA.PA"].copy(); q["grp"] = q.group.replace({"device": "gate", "bigtech": "gate"})
    q["z"] = q.firm.map(Z["dep_share"])
    q["x_bank"] = np.where(q.grp == "bank", q.z * q.direction, 0.0)
    for nm, g in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]:
        q[nm] = np.where(q.grp == g, q.direction, 0.0)
    r = second_stage(q, ["x_bank", "d_bank", "d_pay", "d_gate"])
    out[f"{win}_dep_noACA"] = dict(theta=float(r["beta"][0]), t=float(r["t"][0]))
    print(f"{win}_dep_share_noACA    theta {r['beta'][0]*100:6.3f}  t {r['t'][0]:5.2f}")
json.dump(out, open(f"output/continuous_results_{win}.json", "w"), indent=1)
