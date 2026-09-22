"""Ex-ante power for the second stage, using the ACTUAL event coding and the planned firm universe.
No price data is used: only the number of firms per group, the number of events with non-zero coded
direction per group, and assumptions on the standard deviation of abnormal returns and of exposure."""
from __future__ import annotations
import numpy as np, pandas as pd, sys
sys.path.insert(0, ".")
from src.eventstudy import second_stage

def simulate(theta, sd_car=0.015, n_perm=0, reps=400, seed=0, window_scale=1.0):
    rng = np.random.default_rng(seed)
    coding = pd.read_csv("data/hand/event_coding_v1.csv", dtype=str)
    firms = pd.read_csv("data/hand/firm_universe_v0.csv")
    gmap = {"bank": "dir_banks", "payments": "dir_psp", "device": "dir_bigtech", "bigtech": "dir_bigtech"}
    firms = firms[firms.group.isin(gmap)].reset_index(drop=True)
    ev = coding[coding.status.astype(str).str.startswith("coded")].copy()
    for c in ["dir_banks", "dir_psp", "dir_bigtech"]:
        ev[c] = pd.to_numeric(ev[c], errors="coerce").fillna(0.0)
    rows = []
    for f in firms.itertuples():
        col = gmap[f.group]
        for e in ev.itertuples():
            d = getattr(e, col)
            rows.append(dict(firm=f.name, group=f.group, event_date=e.date, direction=d))
    base = pd.DataFrame(rows)
    hits = []
    for r in range(reps):
        expo = {f: rng.uniform(0.2, 0.8) for f in firms.name}
        p = base.copy()
        p["exposure"] = p.firm.map(expo)
        p["expo_x_dir"] = p.exposure * p.direction
        p["car"] = theta * p.expo_x_dir + rng.normal(0, sd_car * np.sqrt(window_scale), len(p))
        res = second_stage(p, ["expo_x_dir"])
        t = res["t"][0]
        hits.append(abs(t) > 1.96)
    return dict(theta=theta, sd_car=sd_car, reps=reps, power=float(np.mean(hits)),
                firms=len(firms), events=int(len(ev)),
                nonzero_bank_events=int((ev.dir_banks != 0).sum()),
                nonzero_psp_events=int((ev.dir_psp != 0).sum()))

if __name__ == "__main__":
    out = []
    for th in [0.0, 0.005, 0.0075, 0.01, 0.015, 0.02]:
        r = simulate(th, reps=300, seed=int(th * 10000))
        out.append(r); print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
    pd.DataFrame(out).to_csv("output/power_secondstage.csv", index=False)
