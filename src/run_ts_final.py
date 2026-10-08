"""Release-time-aligned specification: definitive inference with 9,999 draws.

For each first stage (pre-specified FF3 in USD, euro market factor with FF size and value,
euro market model in excess returns) this reports the deposit-exposure coefficient, its
leave-one-firm-out jackknife standard error, an exposure permutation p-value and a
null-imposed wild cluster bootstrap p-value (Rademacher weights on firms), plus the
variants that exclude the two confounded days and that keep design-parameter events only.
Run after src/run_currency.py and src/run_round10b.py, which write the aligned CAR panels.
"""
import sys; sys.path.insert(0, ".")
import json, numpy as np, pandas as pd
from src.eventstudy import second_stage

B = 9999
ex = pd.read_csv("data/derived/bank_exposure_2023q1.csv"); eb = ex[ex.group == "bank"]
Z = dict(zip(ex.ticker, (ex.dep_share - eb.dep_share.mean()) / eb.dep_share.std()))
ev = pd.read_csv("data/hand/event_coding_v1.csv", dtype=str); ev["date"] = pd.to_datetime(ev.date)
DESIGN = set(ev[ev.event_id.isin(["E12", "E14", "E17", "E22", "E26", "E19"])].date)
LOOKAHEAD = set(ev[ev.event_id.isin(["E04", "E06"])].date)
CONFOUNDED = {pd.Timestamp("2025-10-23"), pd.Timestamp("2025-12-19")}
CTRL = ["d_bank", "d_pay", "d_gate"]


def prep(path):
    q = pd.read_csv(path, parse_dates=["event_date"])
    q["grp"] = q.get("grp", q.get("group")).replace({"device": "gate", "bigtech": "gate"})
    q["z"] = q.firm.map(Z)
    for nm, g in [("d_bank", "bank"), ("d_pay", "payments"), ("d_gate", "gate")]:
        q[nm] = np.where(q.grp == g, q.direction, 0.0)
    return q.dropna(subset=["car", "direction"]).reset_index(drop=True)


def design_only(q):
    q = q[~q.event_date.isin(LOOKAHEAD)].copy()
    q["x_design"] = np.where((q.grp == "bank") & q.event_date.isin(DESIGN), q.z * q.direction, 0.0)
    q["x_impl"] = np.where((q.grp == "bank") & ~q.event_date.isin(DESIGN), q.z * q.direction, 0.0)
    r = second_stage(q, ["x_design", "x_impl"] + CTRL)
    return dict(theta=float(r["beta"][0] * 100), se=float(r["se_jackknife"][0] * 100), t=float(r["t"][0]))


def inference(q, seed):
    q = q.copy(); q["x_bank"] = np.where(q.grp == "bank", q.z * q.direction, 0.0)
    r = second_stage(q, ["x_bank"] + CTRL)
    firms = sorted(q.firm.unique()); fi = q.firm.map({f: i for i, f in enumerate(firms)}).to_numpy()
    evs = sorted(q.event_date.unique()); ei = q.event_date.map({e: i for i, e in enumerate(evs)}).to_numpy()
    n = len(q); M = np.zeros((n, len(firms) + len(evs) - 1)); M[np.arange(n), fi] = 1
    m = ei > 0; M[np.arange(n)[m], len(firms) + ei[m] - 1] = 1
    W = np.hstack([q[CTRL].to_numpy(float), M])
    U, sv, _ = np.linalg.svd(W, full_matrices=False); Qw = U[:, sv > sv.max() * 1e-10]   # orthonormal basis, rank-safe
    res = lambda v: v - Qw @ (Qw.T @ v)
    y = q.car.to_numpy(float); ry = res(y)
    isbank = (q.grp == "bank").to_numpy(); dirn = q.direction.to_numpy(float)
    rx = res(q.x_bank.to_numpy(float)); b0 = rx @ ry / (rx @ rx)
    rng = np.random.default_rng(seed)
    banks = sorted(q.loc[isbank, "firm"].unique()); zb = np.array([Z[b] for b in banks])
    bpos = q.firm.map({b: i for i, b in enumerate(banks)}).to_numpy()
    perm = np.empty(B)
    for k in range(B):
        zp = rng.permutation(zb); x = np.where(isbank, zp[np.where(isbank, bpos, 0).astype(int)] * dirn, 0.0)
        rxp = res(x); perm[k] = rxp @ ry / (rxp @ rxp)
    f0 = y - ry; u0 = ry                       # restricted fit without the exposure term
    wild = np.empty(B)
    for k in range(B):
        w = rng.choice([-1.0, 1.0], size=len(firms))[fi]
        wild[k] = rx @ (f0 + w * u0) / (rx @ rx)
    pp = (1 + (np.abs(perm) >= abs(b0)).sum()) / (B + 1)
    pw = (1 + (np.abs(wild) >= abs(b0)).sum()) / (B + 1)
    se = r["se_jackknife"][0]
    assert abs(b0 - r["beta"][0]) < 1e-10
    return dict(theta=float(b0 * 100), se=float(se * 100), t=float(r["t"][0]),
                ci=[float((b0 - 1.96 * se) * 100), float((b0 + 1.96 * se) * 100)],
                p_perm=float(pp), p_wild=float(pw), n=int(len(q)), draws=B)


if __name__ == "__main__":
    out = {}
    for name, path, seed in [("ff3usd", "output/car_ff3usd_ts.csv", 101),
                             ("eur_mkt_ff", "output/car_local3_ts.csv", 102),
                             ("eur_excess", "output/car_stoxxexcess_ts.csv", 103)]:
        q = prep(path)
        o = inference(q, seed)
        qc = q[~q.event_date.isin(CONFOUNDED)].copy(); qc["x_bank"] = np.where(qc.grp == "bank", qc.z * qc.direction, 0.0)
        rc = second_stage(qc, ["x_bank"] + CTRL)
        o["excl_confounded"] = dict(theta=float(rc["beta"][0] * 100), t=float(rc["t"][0]))
        o["design_only"] = design_only(q)
        out[name] = o
        print(name, json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in o.items() if not isinstance(v, dict)}),
              "| excl. confounded", round(o["excl_confounded"]["theta"], 3), round(o["excl_confounded"]["t"], 2),
              "| design only", round(o["design_only"]["theta"], 3), round(o["design_only"]["se"], 3), round(o["design_only"]["t"], 2))
    json.dump(out, open("output/ts_final.json", "w"), indent=1)
