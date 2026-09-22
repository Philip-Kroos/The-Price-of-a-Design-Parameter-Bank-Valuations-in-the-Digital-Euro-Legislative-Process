import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import abnormal_returns, cars, second_stage
R = pd.read_csv("data/derived/returns_daily.csv", index_col=0, parse_dates=True)
F = pd.read_csv("data/derived/ff3_europe_daily.csv", parse_dates=["date"]).set_index("date")
fu = pd.read_csv("data/hand/firm_universe_v0.csv"); fu = fu[fu.ticker_guess.isin(R.columns)]
p0 = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"])
evd = sorted(p0.event_date.unique()); dirmap = p0.groupby(["event_date","firm"]).direction.first()
grp = dict(zip(fu.ticker_guess, fu.group))
ex = pd.read_csv("data/derived/bank_exposure_2023q1.csv"); eb = ex[ex.group=="bank"]
Z = dict(zip(ex.ticker, (ex.dep_share-eb.dep_share.mean())/eb.dep_share.std()))
US = {"MA","V","AXP","PYPL","GPN","AAPL","GOOGL","AMZN","META"}
eu = [t for t in fu.ticker_guess if t not in US]; us = [t for t in fu.ticker_guess if t in US]
com = R.index.intersection(F.index)
def ar(est=250, extra_excl=(), market_model=False):
    excl = list(evd) + list(extra_excl)
    fac = R.loc[com, ["^STOXX"]].rename(columns={"^STOXX":"mkt"}) if market_model else F.loc[com, ["mkt_rf","smb","hml"]]
    a = abnormal_returns(R.loc[com, eu], fac, excl, est_window=est)
    b = abnormal_returns(R[us], R[["^GSPC"]].rename(columns={"^GSPC":"mkt"}), excl, est_window=est)
    return pd.concat([a, b], axis=1)
def theta(AR, window=(0,0), subset=None):
    c = cars(AR, evd, window=window)
    c["direction"] = [dirmap.get((d, f), np.nan) for d, f in zip(c.event_date, c.firm)]
    c = c.dropna(subset=["direction"])
    c["grp"] = c.firm.map(grp).replace({"device":"gate","bigtech":"gate"}); c["z"] = c.firm.map(Z)
    if subset is not None:
        c = c[~((c.grp=="bank") & (c.direction!=0) & ~c.direction.isin(subset))]
    c["x_bank"] = np.where(c.grp=="bank", c.z*c.direction, 0.0)
    for nm,g in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]: c[nm] = np.where(c.grp==g, c.direction, 0.0)
    r = second_stage(c, ["x_bank","d_bank","d_pay","d_gate"]); return float(r["beta"][0]*100), float(r["t"][0])
base = ar()
march = pd.bdate_range("2023-03-09", "2023-03-24")
rows = {
 "Baseline (one day, 250-day window, three factors)": theta(base),
 "Three-day window": theta(base, (0,2)),
 "Estimation window 120 days": theta(ar(est=120)),
 "Estimation window 500 days": theta(ar(est=500)),
 "Excluding March 2023 banking turmoil from estimation": theta(ar(extra_excl=march)),
 "Market model (STOXX Europe 600)": theta(ar(market_model=True)),
 "F3: limiting events only (direction +1)": theta(base, subset=[1.0]),
 "F3: expanding events only (direction -1)": theta(base, subset=[-1.0]),
}
json.dump({k: dict(theta=v[0], t=v[1]) for k, v in rows.items()}, open("output/robustness_table.json","w"), indent=1)
for k, v in rows.items(): print(f"{k:56s} {v[0]:6.3f}  t {v[1]:5.2f}")

# conventional per-event pre-event estimation window: betas from trading days [-260, -11] before each event,
# excluding +-10 days around any other event
def per_event_car(R_, fac):
    idx = R_.index; X = fac.reindex(idx).to_numpy(float); near = np.zeros(len(idx), bool)
    for d in evd:
        pos = idx.searchsorted(d); near[max(0,pos-10):pos+11] = True
    out = []
    for d in evd:
        pos = idx.searchsorted(d)
        if pos >= len(idx): continue
        win = np.arange(max(0, pos-260), max(0, pos-10)); win = win[~near[win]]
        for c in R_.columns:
            y = R_[c].to_numpy(float); ok = win[np.isfinite(y[win]) & np.all(np.isfinite(X[win]), axis=1)]
            if len(ok) < 60 or not np.isfinite(y[pos]): continue
            A = np.column_stack([np.ones(len(ok)), X[ok]]); b,*_ = np.linalg.lstsq(A, y[ok], rcond=None)
            out.append(dict(event_date=d, firm=c, car=float(y[pos] - (b[0] + X[pos] @ b[1:]))))
    return pd.DataFrame(out)
pe = pd.concat([per_event_car(R.loc[com, eu], F.loc[com, ["mkt_rf","smb","hml"]]),
                per_event_car(R[us], R[["^GSPC"]].rename(columns={"^GSPC":"mkt"}))])
pe["direction"] = [dirmap.get((d, f), np.nan) for d, f in zip(pe.event_date, pe.firm)]
pe = pe.dropna(subset=["direction"]); pe["grp"] = pe.firm.map(grp).replace({"device":"gate","bigtech":"gate"}); pe["z"] = pe.firm.map(Z)
pe["x_bank"] = np.where(pe.grp=="bank", pe.z*pe.direction, 0.0)
for nm,g in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]: pe[nm] = np.where(pe.grp==g, pe.direction, 0.0)
r = second_stage(pe, ["x_bank","d_bank","d_pay","d_gate"])
rows["Pre-event estimation window per event [-260,-11]"] = (float(r["beta"][0]*100), float(r["t"][0]))
json.dump({k: dict(theta=v[0], t=v[1]) for k, v in rows.items()}, open("output/robustness_table.json","w"), indent=1)
print("Pre-event window per event:", round(r["beta"][0]*100,3), "t", round(r["t"][0],2), "| n events", pe.event_date.nunique())
