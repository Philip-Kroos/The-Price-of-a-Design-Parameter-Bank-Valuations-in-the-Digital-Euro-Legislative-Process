"""Further checks of the preferred specification (draft report dated 31 October 2025), post-review.

 (1) Exposure available before the events: the deposit share of 31 December 2019, from the EBA
     transparency exercise published in 2020, instead of 31 March 2023 (published December 2023).
 (2) Currency-consistent first stage with strictly pre-event loadings: euro market model in
     excess returns (STOXX Europe 600 less the ECB deposit facility rate), loadings estimated for
     each event on trading days [-260, -11], excluding +-10 days around any event.
 (3) Event-level uncertainty: (a) leave-one-event-out jackknife standard error; (b) placebo dates:
     the 22 coded direction vectors are assigned in random order to 22 non-event trading days since
     January 2023, at least ten trading days from any event, 2,000 draws.
Each check is also reported for the pre-specified dating. Run after src/run_redate_draft.py.
"""
import sys; sys.path.insert(0, ".")
import json, numpy as np, pandas as pd
from src.eventstudy import abnormal_returns, second_stage, second_stage_beta
from src.firststage import R, EU, USL, GROUP
from src.run_inference_final import run, zmap, x_main, CTRL
from src.run_redate_draft import setup, first_stage, build, finish, rfe, SPX, Z23

Z19 = zmap("data/derived/bank_exposure_2019q4.csv", "dep_share_2019")
REG = ["x_bank"] + CTRL


def theta(q, Z=Z23):
    q = q.copy(); q["z"] = q.firm.map(Z); q["x_bank"] = np.where(q.grp == "bank", q.z * q.direction, 0.0)
    r = second_stage(q, REG)
    return dict(theta=float(r["beta"][0] * 100), se=float(r["se_jackknife"][0] * 100), t=float(r["t"][0]), n=int(r["n"]))


def per_event_excess(evd):
    """Per-event loadings on days [-260, -11], euro market model in excess returns (US firms: S&P 500)."""
    def one(Y, X):
        idx = Y.index; Xv = X.reindex(idx).to_numpy(float); near = np.zeros(len(idx), bool)
        for d in evd:
            pos = idx.searchsorted(d); near[max(0, pos - 10):pos + 11] = True
        out = []
        for d in evd:
            pos = idx.searchsorted(d)
            win = np.arange(max(0, pos - 260), max(0, pos - 10)); win = win[~near[win]]
            for c in Y.columns:
                y = Y[c].to_numpy(float); ok = win[np.isfinite(y[win]) & np.all(np.isfinite(Xv[win]), axis=1)]
                if len(ok) < 60 or not np.isfinite(y[pos]): continue
                A = np.column_stack([np.ones(len(ok)), Xv[ok]]); b, *_ = np.linalg.lstsq(A, y[ok], rcond=None)
                out.append(dict(event_date=d, firm=c, car=float(y[pos] - (b[0] + Xv[pos] @ b[1:]))))
        return pd.DataFrame(out)
    mx = (R["^STOXX"] - rfe).rename("mkt").to_frame()
    return pd.concat([one(R[EU].sub(rfe, axis=0), mx), one(R[USL], SPX)])


def event_jackknife(q):
    q = q.copy(); q["x_bank"] = np.where(q.grp == "bank", q.z * q.direction, 0.0)
    evs = sorted(q.event_date.unique())
    b = np.array([second_stage_beta(q[q.event_date != e], REG)[0] for e in evs]) * 100
    se = float(np.sqrt((len(evs) - 1) / len(evs) * ((b - b.mean()) ** 2).sum()))
    full = float(second_stage_beta(q, REG)[0] * 100)
    return dict(theta=full, se_event_jackknife=se, t=full / se, events=len(evs))


def placebo_dates(q, A, evd, seed, draws=2000):
    """Move the coded direction vectors (by group) to random non-event days; distribution of theta."""
    q = q.copy(); q["x_bank"] = np.where(q.grp == "bank", q.z * q.direction, 0.0)
    b0 = float(second_stage_beta(q, REG)[0] * 100)
    dirs = q.groupby(["event_date", "grp"]).direction.first().unstack().reindex(evd)
    idx = A.index[(A.index >= "2023-01-01") & (A.index <= A.dropna(how="all").index.max())]
    near = set()
    for d in evd:
        pos = A.index.searchsorted(d); near |= set(A.index[max(0, pos - 10):pos + 11])
    pool = np.array([d for d in idx if d not in near])
    firms = [f for f in A.columns if GROUP.get(f) is not None]
    grp = {f: ("gate" if GROUP[f] in ("device", "bigtech") else GROUP[f]) for f in firms}
    z = pd.Series({f: Z23.get(f, np.nan) for f in firms})
    rng = np.random.default_rng(seed); out = np.empty(draws)
    for k in range(draws):
        days = rng.choice(pool, size=len(evd), replace=False); order = rng.permutation(len(evd))
        rows = []
        for j, d in enumerate(days):
            dv = dirs.iloc[order[j]]
            for f, v in A.loc[d, firms].items():
                g = grp[f]
                if not np.isfinite(v) or g not in dv.index or not np.isfinite(dv[g]): continue
                rows.append((d, f, v, g, dv[g]))
        p = pd.DataFrame(rows, columns=["event_date", "firm", "car", "grp", "direction"])
        p = p[~((p.grp == "bank") & p.firm.map(z).isna())]
        p["x_bank"] = np.where(p.grp == "bank", p.firm.map(z) * p.direction, 0.0)
        for nm, g in [("d_bank", "bank"), ("d_pay", "payments"), ("d_gate", "gate")]:
            p[nm] = np.where(p.grp == g, p.direction, 0.0)
        out[k] = second_stage_beta(p, REG)[0] * 100
    return dict(theta=b0, placebo_sd=float(out.std()), p_placebo=float((1 + (np.abs(out) >= abs(b0)).sum()) / (draws + 1)),
                band95=[float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))], draws=draws)


OUT = {}
for label, redate, seed in [("preferred", True, 401), ("prespecified", False, 501)]:
    evd, dirmap, design, lookahead, tim = setup(redate)
    A = first_stage(evd, "ff3usd")
    q = build(A, evd, dirmap, tim, "w00")
    o = {}
    o["exposure_2019"] = theta(q, Z19)
    o["exposure_2019"]["p_perm"] = run(q, Z19, x_main, "x_bank", seed)["p_perm"]
    o["excess_per_event"] = theta(finish(per_event_excess(evd), dirmap))
    o["event_jackknife"] = event_jackknife(q)
    o["placebo_dates"] = placebo_dates(q, A, evd, seed + 1)
    OUT[label] = o
    print(label)
    for k, v in o.items():
        print(f"  {k:18s}", {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()})
json.dump(OUT, open("output/robust_redate.json", "w"), indent=1)

# (4) Day-level noise behind the 2020 positive control: the report-day slope against the slopes of all
#     non-event trading days from July 2019 to December 2021, same first stage and 2019 exposure.
p = pd.read_csv("data/raw/prices_2019_2021.csv", parse_dates=["date"])
W = p.pivot_table(index="date", columns="ticker", values="close").sort_index(); RE = np.log(W).diff()
raw = open("data/raw/Europe_3_Factors_Daily.csv", encoding="latin-1").read().splitlines()
st = next(i for i, l in enumerate(raw) if l.strip().startswith(",Mkt-RF")); rows = []
for l in raw[st + 1:]:
    x = [v.strip() for v in l.split(",")]
    if len(x) == 5 and x[0].isdigit(): rows.append((pd.to_datetime(x[0]), *[float(v) / 100 for v in x[1:]]))
FF = pd.DataFrame(rows, columns=["date", "mkt_rf", "smb", "hml", "rf"]).set_index("date")
ev0 = pd.read_csv("data/hand/events_early_2020_2021.csv", parse_dates=["date"])
banks = [b for b in EU if GROUP.get(b) == "bank" and b in RE.columns and np.isfinite(Z19.get(b, np.nan))]
com = RE.index.intersection(FF.index)
AE = abnormal_returns(RE.loc[com, banks], FF.loc[com, ["mkt_rf", "smb", "hml"]], ev0.date)
zb = pd.Series({b: Z19[b] for b in banks})
def day_slope(d):
    r = AE.loc[d, banks].astype(float); ok = r.notna()
    return float(np.polyfit(zb[ok], r[ok], 1)[0] * 100) if ok.sum() >= 15 else np.nan
near = set()
for d in ev0.date:
    pos = AE.index.searchsorted(d); near |= set(AE.index[max(0, pos - 10):pos + 11])
days = [d for d in AE.index if pd.Timestamp("2019-07-01") <= d <= pd.Timestamp("2021-12-31") and d not in near]
S = np.array([day_slope(d) for d in days]); S = S[np.isfinite(S)]
rep = day_slope(pd.Timestamp("2020-10-02"))
OUT["report_day_vs_daily_slopes"] = dict(report_day_slope=rep, daily_sd=float(S.std()), n_days=int(len(S)),
                                         p_two_sided=float((1 + (np.abs(S) >= abs(rep)).sum()) / (len(S) + 1)),
                                         band95=[float(np.percentile(S, 2.5)), float(np.percentile(S, 97.5))])
# the same for the legislative period: slopes of single non-event days, 2023 to 2026, 2023 exposure
evd, dirmap, *_ = setup(True); A = first_stage(evd, "ff3usd")
b23 = [b for b in A.columns if GROUP.get(b) == "bank" and np.isfinite(Z23.get(b, np.nan))]
z23 = pd.Series({b: Z23[b] for b in b23}); near = set()
for d in evd:
    pos = A.index.searchsorted(d); near |= set(A.index[max(0, pos - 10):pos + 11])
S2 = []
for d in A.index[(A.index >= "2023-01-01")]:
    if d in near: continue
    r = A.loc[d, b23].astype(float); ok = r.notna()
    if ok.sum() >= 15: S2.append(np.polyfit(z23[ok], r[ok], 1)[0] * 100)
OUT["daily_slopes_2023_2026"] = dict(daily_sd=float(np.std(S2)), n_days=len(S2))
print("report day vs daily slopes", OUT["report_day_vs_daily_slopes"], "| 2023-26 daily sd", round(float(np.std(S2)), 3))
json.dump(OUT, open("output/robust_redate.json", "w"), indent=1)
