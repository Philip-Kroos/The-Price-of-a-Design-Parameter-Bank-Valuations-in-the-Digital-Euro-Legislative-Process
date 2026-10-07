"""Power of the second stage, Table 4.

Uses no price data: the planned firm universe (44 firms in the bank, provider and gatekeeper groups),
the 22 pre-specified estimation dates with their coded directions (same-day events merged as in
src/run_main.py), exposure drawn uniformly on [0.2, 0.8], and normal abnormal returns with a given
standard deviation. Each replication estimates CAR = firm FE + event FE + theta * exposure x direction
and rejects when |t| > 1.96, with t from leave-one-firm-out jackknife standard errors as in the paper.
The fixed-effect projections are precomputed once, which makes the jackknife exact and fast.
Run from the repository root:  python src/power.py
"""
import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd
from src.eventstudy import second_stage

REPS = 2000
THETAS = [0.0, 0.005, 0.0075, 0.01, 0.0125, 0.0175]
SIGMAS = [0.015, 0.016, 0.025]

coding = pd.read_csv("data/hand/event_coding_v1.csv", dtype=str)
coding["date"] = pd.to_datetime(coding.date)
ev = coding[coding.status.str.startswith("coded") & (coding.date <= "2026-07-31")].copy()
for c in ["dir_banks", "dir_psp", "dir_bigtech"]:
    ev[c] = pd.to_numeric(ev[c], errors="coerce").fillna(0.0)
ev = ev.groupby("date")[["dir_banks", "dir_psp", "dir_bigtech"]].sum().clip(-1, 1).reset_index()
firms = pd.read_csv("data/hand/firm_universe_v0.csv")
gmap = {"bank": "dir_banks", "payments": "dir_psp", "device": "dir_bigtech", "bigtech": "dir_bigtech"}
firms = firms[firms.group.isin(gmap)].reset_index(drop=True)

rows = [dict(firm=i, event=j, direction=float(e[gmap[f.group]]))
        for i, f in firms.iterrows() for j, (_, e) in enumerate(ev.iterrows())]
P = pd.DataFrame(rows)
nF, nE, n = len(firms), len(ev), len(P)
fi, ei, d = P.firm.to_numpy(), P.event.to_numpy(), P.direction.to_numpy()


def basis(mask):
    """Orthonormal basis of the firm and event dummies on the rows in mask."""
    f = fi[mask]; e = ei[mask]; m = mask.sum()
    fs = np.unique(f); M = np.zeros((m, len(fs) + nE - 1))
    M[np.arange(m), np.searchsorted(fs, f)] = 1
    k = e > 0; M[np.arange(m)[k], len(fs) + e[k] - 1] = 1
    U, s, _ = np.linalg.svd(M, full_matrices=False)
    return U[:, s > s.max() * 1e-10]


full = np.ones(n, bool)
Q = basis(full)
LOO = [(fi != g, basis(fi != g)) for g in range(nF)]


def t_stat(x, y):
    rx = x - Q @ (Q.T @ x); ry = y - Q @ (Q.T @ y); b = rx @ ry / (rx @ rx)
    jk = []
    for m, Qm in LOO:
        xm, ym = x[m], y[m]
        rxm = xm - Qm @ (Qm.T @ xm); rym = ym - Qm @ (Qm.T @ ym); jk.append(rxm @ rym / (rxm @ rxm))
    jk = np.array(jk); se = np.sqrt((nF - 1) / nF * ((jk - jk.mean()) ** 2).sum())
    return b / se


# check against the estimator used in the paper on one draw
rng = np.random.default_rng(0)
expo = rng.uniform(0.2, 0.8, nF); x = expo[fi] * d; y = 0.01 * x + rng.normal(0, 0.015, n)
chk = second_stage(P.assign(car=y, x=x, event_date=P.event), ["x"])
assert abs(chk["t"][0] - t_stat(x, y)) < 1e-8

out = []
for sd in SIGMAS:
    for th in THETAS:
        rng = np.random.default_rng(int(sd * 1e4) * 100 + int(th * 1e4))
        hits = 0
        for _ in range(REPS):
            expo = rng.uniform(0.2, 0.8, nF); x = expo[fi] * d
            y = th * x + rng.normal(0, sd, n)
            hits += abs(t_stat(x, y)) > 1.96
        out.append(dict(theta_pp=th * 100, sd_car=sd, reps=REPS, power=hits / REPS, firms=nF, events=nE,
                        bank_events=int((ev.dir_banks != 0).sum()), provider_events=int((ev.dir_psp != 0).sum())))
        print(out[-1], flush=True)
pd.DataFrame(out).to_csv("output/power_secondstage.csv", index=False)
