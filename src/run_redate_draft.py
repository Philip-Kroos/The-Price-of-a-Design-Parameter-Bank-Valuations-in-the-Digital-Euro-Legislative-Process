"""Dating of the rapporteur's draft report and documented release times (post-review check).

The content of the draft report (E12; document PE778.136 dated 3 November 2025, presented in
committee on 5 November) was first reported by Bloomberg on 30 October 2025 at 21:12 UTC, after
the close of European markets, so the first trading day with the information is 31 October 2025.
The ECB release of 30 October 2025 (E11) was public by 11:05 GMT (MLex), during trading hours.
data/hand/event_timing_v2.csv records both; data/hand/event_timing.csv is the earlier record.

The script
 (1) moves E12 to 31 October 2025, re-estimates every first stage with the moved date in the
     exclusion band, and re-estimates the main specification (one-day and two-day window, and
     with per-event pre-event betas) and the design-only specification, with the inference of
     src/run_inference_final.py (9,999 draws);
 (2) re-estimates the release-time-aligned specification with the timing in event_timing_v2.csv
     for the three first stages, with the inference of src/run_ts_final.py.
Before (1) and (2) the same code is run with the original dating and must reproduce the stored
estimates. Run after src/run_main.py, src/run_robust_table.py, src/run_ts_final.py and
src/run_inference_final.py:   python src/run_redate_draft.py
"""
import sys; sys.path.insert(0, ".")
import json, numpy as np, pandas as pd
from src.eventstudy import abnormal_returns, cars, second_stage
from src.firststage import R, F, EU, USL, GROUP, AR, window_car
from src.ecb_rate import load_dfr_daily
from src.run_inference_final import run, zmap, x_main, CTRL
from src.run_ts_final import inference

OLD, NEW = pd.Timestamp("2025-11-03"), pd.Timestamp("2025-10-31")
CONFOUNDED = {pd.Timestamp("2025-10-23"), pd.Timestamp("2025-12-19")}
Z23 = zmap("data/derived/bank_exposure_2023q1.csv", "dep_share")
p0 = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"])
ev = pd.read_csv("data/hand/event_coding_v1.csv", dtype=str); ev["date"] = pd.to_datetime(ev.date)
rfe = load_dfr_daily().reindex(R.index).ffill()
SPX = R[["^GSPC"]].rename(columns={"^GSPC": "mkt"})


def setup(redate):
    mv = (lambda d: NEW if d == OLD else d) if redate else (lambda d: d)
    evd = sorted(mv(d) for d in p0.event_date.unique())
    dirmap = {(mv(d), f): v for (d, f), v in p0.groupby(["event_date", "firm"]).direction.first().items()}
    design = {mv(d) for d in ev[ev.event_id.isin(["E12", "E14", "E17", "E22", "E26", "E19"])].date}
    lookahead = set(ev[ev.event_id.isin(["E04", "E06"])].date)
    T = pd.read_csv("data/hand/event_timing_v2.csv" if redate else "data/hand/event_timing.csv", parse_dates=["date"])
    assert set(T.date) == set(evd)
    return evd, dirmap, design, lookahead, dict(zip(T.date, T.timing))


def first_stage(evd, version):
    if version == "eur_excess":
        mx = (R["^STOXX"] - rfe).rename("mkt").to_frame()
        return pd.concat([abnormal_returns(R[EU].sub(rfe, axis=0), mx, evd), abnormal_returns(R[USL], SPX, evd)], axis=1)
    return AR(evd, version)


def per_event_ar(evd):
    """Conventional per-event betas on trading days [-260, -11], excluding +-10 days around any event (as in run_robust_table)."""
    com = R.index.intersection(F.index)
    def one(R_, fac):
        idx = R_.index; X = fac.reindex(idx).to_numpy(float); near = np.zeros(len(idx), bool)
        for d in evd:
            pos = idx.searchsorted(d); near[max(0, pos - 10):pos + 11] = True
        out = []
        for d in evd:
            pos = idx.searchsorted(d)
            if pos >= len(idx): continue
            win = np.arange(max(0, pos - 260), max(0, pos - 10)); win = win[~near[win]]
            for c in R_.columns:
                y = R_[c].to_numpy(float); ok = win[np.isfinite(y[win]) & np.all(np.isfinite(X[win]), axis=1)]
                if len(ok) < 60 or not np.isfinite(y[pos]): continue
                A = np.column_stack([np.ones(len(ok)), X[ok]]); b, *_ = np.linalg.lstsq(A, y[ok], rcond=None)
                out.append(dict(event_date=d, firm=c, car=float(y[pos] - (b[0] + X[pos] @ b[1:]))))
        return pd.DataFrame(out)
    return pd.concat([one(R.loc[com, EU], F.loc[com, ["mkt_rf", "smb", "hml"]]), one(R[USL], SPX)])


def finish(c, dirmap):
    c["direction"] = [dirmap.get((d, f), np.nan) for d, f in zip(c.event_date, c.firm)]
    c = c.dropna(subset=["direction", "car"]).copy()
    c["grp"] = c.firm.map(GROUP).replace({"device": "gate", "bigtech": "gate"}); c["z"] = c.firm.map(Z23)
    for nm, g in [("d_bank", "bank"), ("d_pay", "payments"), ("d_gate", "gate")]:
        c[nm] = np.where(c.grp == g, c.direction, 0.0)
    return c.reset_index(drop=True)


def build(A, evd, dirmap, tim, mode):
    if mode == "aligned":
        rows = []
        for d in evd:
            for f, v in window_car(A, d, tim[d]).items():
                if np.isfinite(v): rows.append(dict(event_date=d, firm=f, car=float(v)))
        return finish(pd.DataFrame(rows), dirmap)
    return finish(cars(A, evd, window=(0, 0) if mode == "w00" else (0, 1)), dirmap)


def point(q):
    q = q.copy(); q["x_bank"] = np.where(q.grp == "bank", q.z * q.direction, 0.0)
    r = second_stage(q, ["x_bank"] + CTRL)
    return dict(theta=float(r["beta"][0] * 100), se=float(r["se_jackknife"][0] * 100), t=float(r["t"][0]))


def design_spec(q, design, lookahead):
    q = q[~q.event_date.isin(lookahead)].reset_index(drop=True)
    def xfun(qq, z):
        bank = qq.grp == "bank"; des = qq.event_date.isin(design)
        return {"x_design": np.where(bank & des, z * qq.direction, 0.0),
                "x_impl": np.where(bank & ~des, z * qq.direction, 0.0)}
    return q, xfun


def bank_slope(A, d):
    banks = [f for f in A.columns if GROUP.get(f) == "bank" and np.isfinite(Z23.get(f, np.nan))]
    r = A.loc[d, banks].astype(float); z = pd.Series({b: Z23[b] for b in banks}); ok = r.notna()
    return float(np.polyfit(z[ok], r[ok], 1)[0] * 100)


if __name__ == "__main__":
    # ---- the original dating reproduces the stored estimates (same code path, point estimates) ----
    evd, dirmap, design, lookahead, tim = setup(False)
    stored = json.load(open("output/inference_final.json")); stored_ts = json.load(open("output/ts_final.json"))
    stored_rob = json.load(open("output/robustness_table.json"))
    A0 = first_stage(evd, "ff3usd")
    assert abs(point(build(A0, evd, dirmap, tim, "w00"))["theta"] - stored["main_one_day"]["theta"]) < 1e-9
    assert abs(point(build(A0, evd, dirmap, tim, "w01"))["theta"] - stored["main_two_day"]["theta"]) < 1e-9
    assert abs(point(finish(per_event_ar(evd), dirmap))["theta"] - stored_rob["Pre-event estimation window per event [-260,-11]"]["theta"]) < 1e-9
    for name, version in [("ff3usd", "ff3usd"), ("eur_mkt_ff", "local3"), ("eur_excess", "eur_excess")]:
        assert abs(point(build(first_stage(evd, version), evd, dirmap, tim, "aligned"))["theta"] - stored_ts[name]["theta"]) < 1e-9, name
    print("original dating reproduces the stored estimates")

    # ---- corrected dating ----
    evd, dirmap, design, lookahead, tim = setup(True)
    A = first_stage(evd, "ff3usd")
    q1 = build(A, evd, dirmap, tim, "w00")
    OUT = {"one_day": run(q1, Z23, x_main, "x_bank", 201, wild=True)}
    qd, xd = design_spec(q1, design, lookahead)
    OUT["one_day_design_only"] = run(qd, Z23, xd, "x_design", 202)
    OUT["two_day"] = run(build(A, evd, dirmap, tim, "w01"), Z23, x_main, "x_bank", 203)
    OUT["per_event_window"] = point(finish(per_event_ar(evd), dirmap))
    for v in ["local3", "eur_excess"]:
        OUT[f"one_day_{v}"] = point(build(first_stage(evd, v), evd, dirmap, tim, "w00"))
    OUT["slope_31oct2025"] = bank_slope(A, NEW)
    OUT["slope_3nov2025"] = bank_slope(A, OLD)
    OUT["aligned"] = {}
    for k, (name, version) in enumerate([("ff3usd", "ff3usd"), ("eur_mkt_ff", "local3"), ("eur_excess", "eur_excess")]):
        q = build(first_stage(evd, version), evd, dirmap, tim, "aligned")
        o = inference(q, 301 + k)
        qc = q[~q.event_date.isin(CONFOUNDED)]
        o["excl_confounded"] = {kk: point(qc)[kk] for kk in ("theta", "t")}
        qd, xd = design_spec(q, design, lookahead)
        o["design_only"] = run(qd, Z23, xd, "x_design", 311 + k)
        OUT["aligned"][name] = o
    # decomposition: documented timing of the ECB release alone, draft report at its document date
    evd0, dir0, _, _, tim0 = setup(False); tim0 = dict(tim0); tim0[pd.Timestamp("2025-10-30")] = "before_close"
    OUT["aligned_ecb_timing_only"] = {kk: point(build(first_stage(evd0, "ff3usd"), evd0, dir0, tim0, "aligned"))[kk] for kk in ("theta", "t")}
    q1.to_csv("output/car_panel_w00_redated.csv", index=False)
    OUT["notes"] = "E12 dated 2025-10-31; release-time-aligned windows from data/hand/event_timing_v2.csv"

    f = lambda d: f"{d['theta']:.3f} (se {d['se']:.3f}, t {d['t']:.2f}" + (f", p_perm {d['p_perm']:.3f}" if "p_perm" in d else "") + (f", p_wild {d['p_wild']:.3f}" if "p_wild" in d else "") + ")"
    print("one day             ", f(OUT["one_day"]))
    print("one day, design only", f(OUT["one_day_design_only"]))
    print("two days            ", f(OUT["two_day"]))
    print("per-event betas     ", f(OUT["per_event_window"]))
    print("one day, euro market + FF", f(OUT["one_day_local3"]), "| euro excess", f(OUT["one_day_eur_excess"]))
    print("aligned, ECB timing only", OUT["aligned_ecb_timing_only"])
    print(f"bank slope 31 Oct {OUT['slope_31oct2025']:.3f}, 3 Nov {OUT['slope_3nov2025']:.3f}")
    for name, a in OUT["aligned"].items():
        print(f"aligned {name:10s}", f(a), f"ci {a['ci'][0]:.2f} to {a['ci'][1]:.2f} | excl. confounded {a['excl_confounded']['theta']:.3f} "
              f"(t {a['excl_confounded']['t']:.2f}) | design only", f(a["design_only"]))
    json.dump(OUT, open("output/redate_draft.json", "w"), indent=1)
