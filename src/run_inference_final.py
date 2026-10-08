"""Definitive permutation and wild-bootstrap p-values, 9,999 draws each.

Every permutation p-value reported in the paper for the deposit-exposure specifications is
computed here with one common standard: exposure is reassigned across euro area banks (or
within country blocks), all exposure-dependent regressors are rebuilt, and the coefficient is
re-estimated with the same group-level controls and firm and event fixed effects. The wild
cluster bootstrap imposes the null for the tested coefficient and draws Rademacher weights by
firm. Point estimates are identical to src/eventstudy.second_stage (asserted below).
Run after src/run_main.py and src/run_early.py:  python src/run_inference_final.py
"""
import sys; sys.path.insert(0, ".")
import json, numpy as np, pandas as pd
from src.eventstudy import second_stage

B = 9999
CTRL = ["d_bank", "d_pay", "d_gate"]
fu = pd.read_csv("data/hand/firm_universe_v0.csv"); CTRY = dict(zip(fu.ticker_guess, fu.country))
ev = pd.read_csv("data/hand/event_coding_v1.csv", dtype=str); ev["date"] = pd.to_datetime(ev.date)
DESIGN = set(ev[ev.event_id.isin(["E12", "E14", "E17", "E22", "E26", "E19"])].date)
LOOKAHEAD = set(ev[ev.event_id.isin(["E04", "E06"])].date)


def zmap(path, col):
    ex = pd.read_csv(path); eb = ex[ex.group == "bank"]
    return dict(zip(ex.ticker, (ex[col] - eb[col].mean()) / eb[col].std()))


def panel(path):
    q = pd.read_csv(path, parse_dates=["event_date"])
    if "grp" not in q: q["grp"] = q.group
    q["grp"] = q.grp.replace({"device": "gate", "bigtech": "gate"})
    if "proc" not in q: q["proc"] = False
    for nm, g in [("d_bank", "bank"), ("d_pay", "payments"), ("d_gate", "gate")]:
        q[nm] = np.where(q.grp == g, q.direction, 0.0)
    return q.dropna(subset=["car"]).reset_index(drop=True)


def x_main(q, z):
    return {"x_bank": np.where(q.grp == "bank", z * q.direction, 0.0)}


def x_design(q, z):
    bank = q.grp == "bank"; des = q.event_date.isin(DESIGN)
    return {"x_design": np.where(bank & des, z * q.direction, 0.0),
            "x_impl": np.where(bank & ~des, z * q.direction, 0.0)}


def x_f1(q, z):
    return {"x_bank": np.where(q.grp == "bank", z * q.direction, 0.0),
            "x_proc": np.where((q.grp == "bank") & (q.proc == True), z, 0.0)}


def run(q, Z, xfun, test, seed, blocks=False, wild=False):
    # banks without an exposure value drop out, exactly as in second_stage
    q = q[~((q.grp == "bank") & q.firm.map(Z).isna())].reset_index(drop=True)
    z0 = q.firm.map(Z).to_numpy(float)
    X0 = xfun(q, np.nan_to_num(z0)); names = list(X0)
    chk = q.copy()
    for k, v in X0.items(): chk[k] = v
    ref = second_stage(chk, names + CTRL)
    firms = sorted(q.firm.unique()); fi = q.firm.map({f: i for i, f in enumerate(firms)}).to_numpy()
    evs = sorted(q.event_date.unique()); ei = q.event_date.map({e: i for i, e in enumerate(evs)}).to_numpy()
    n = len(q); M = np.zeros((n, len(firms) + len(evs) - 1)); M[np.arange(n), fi] = 1
    m = ei > 0; M[np.arange(n)[m], len(firms) + ei[m] - 1] = 1
    W = np.hstack([q[CTRL].to_numpy(float), M])
    U, sv, _ = np.linalg.svd(W, full_matrices=False); Qw = U[:, sv > sv.max() * 1e-10]   # orthonormal basis, rank-safe
    res = lambda v: v - Qw @ (Qw.T @ v)
    y = q.car.to_numpy(float); ry = res(y); j = names.index(test)

    def coef(Xd, yy):
        Rx = np.column_stack([res(Xd[k]) for k in names])
        return np.linalg.solve(Rx.T @ Rx, Rx.T @ yy)

    b0 = coef(X0, ry)
    assert abs(b0[j] - ref["beta"][names.index(test)]) < 1e-10
    banks = sorted(q.loc[q.grp == "bank", "firm"].unique()); rng = np.random.default_rng(seed)
    groups = {}
    for b in banks: groups.setdefault(CTRY[b] if blocks else "all", []).append(b)
    null = np.empty(B)
    for k in range(B):
        mp = dict(Z)
        for members in groups.values():
            mp.update(dict(zip(members, rng.permutation([Z[b] for b in members]))))
        null[k] = coef(xfun(q, np.nan_to_num(q.firm.map(mp).to_numpy(float))), ry)[j]
    out = dict(theta=float(b0[j] * 100), se=float(ref["se_jackknife"][names.index(test)] * 100),
               t=float(ref["t"][names.index(test)]), n=int(n), events=int(len(evs)),
               p_perm=float((1 + (np.abs(null) >= abs(b0[j])).sum()) / (B + 1)), draws=B)
    if wild:
        others = [res(X0[k]) for k in names if k != test]
        if others:
            Rr = np.column_stack(others); g, *_ = np.linalg.lstsq(Rr, ry, rcond=None); u0 = ry - Rr @ g
        else:
            u0 = ry
        f0 = y - u0
        bs = np.empty(B)
        for k in range(B):
            w = rng.choice([-1.0, 1.0], size=len(firms))[fi]
            bs[k] = coef(X0, res(f0 + w * u0))[j]
        out["p_wild"] = float((1 + (np.abs(bs) >= abs(b0[j])).sum()) / (B + 1))
    return out


if __name__ == "__main__":
    Z23 = zmap("data/derived/bank_exposure_2023q1.csv", "dep_share")
    ZON = zmap("data/derived/bank_exposure_2023q1.csv", "overnight_share")
    Z19 = zmap("data/derived/bank_exposure_2019q4.csv", "dep_share_2019")
    w00, w01 = panel("output/car_panel_w00.csv"), panel("output/car_panel_w01.csv")
    nla = w00[~w00.event_date.isin(LOOKAHEAD)].reset_index(drop=True)
    early = panel("output/car_panel_early.csv")

    R = {}
    R["main_one_day"] = run(w00, Z23, x_main, "x_bank", 1, wild=True)
    R["overnight_one_day"] = run(w00, ZON, x_main, "x_bank", 2)
    R["main_two_day"] = run(w01, Z23, x_main, "x_bank", 3)
    R["overnight_two_day"] = run(w01, ZON, x_main, "x_bank", 4)
    R["country_blocked_one_day"] = run(w00, Z23, x_main, "x_bank", 5, blocks=True)
    R["no_lookahead"] = run(nla, Z23, x_main, "x_bank", 6)
    R["design_only"] = run(nla, Z23, x_design, "x_design", 7)
    R["f1_procedural"] = run(w00, Z23, x_f1, "x_proc", 8)
    R["early_2019_exposure"] = run(early, Z19, x_main, "x_bank", 9)
    for k, v in R.items():
        print(f"{k:24s} theta {v['theta']:7.3f}  se {v['se']:6.3f}  t {v['t']:6.2f}  p_perm {v['p_perm']:.3f}"
              + (f"  p_wild {v['p_wild']:.3f}" if "p_wild" in v else "") + f"  n {v['n']}  events {v['events']}")
    json.dump(R, open("output/inference_final.json", "w"), indent=1)
