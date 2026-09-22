"""Valid placebo for the binary-exposure design: move the actual coded direction vector to random
non-event trading days and re-estimate. The event-FE-collinear F2 variant is NOT valid here and is dropped."""
import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd
from src.eventstudy import abnormal_returns, second_stage
R = pd.read_csv("data/derived/returns_daily.csv", index_col=0, parse_dates=True)
F = pd.read_csv("data/derived/ff3_europe_daily.csv", parse_dates=["date"]).set_index("date")
firms = pd.read_csv("data/hand/firm_universe_v0.csv"); firms = firms[firms.ticker_guess.isin(R.columns)]
panel = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"])
evdates = sorted(panel.event_date.unique())
US = {"MA","V","AXP","PYPL","GPN","AAPL","GOOGL","AMZN","META"}
eu = [t for t in firms.ticker_guess if t not in US]; us = [t for t in firms.ticker_guess if t in US]
common = R.index.intersection(F.index)
AR = pd.concat([abnormal_returns(R.loc[common, eu], F.loc[common, ["mkt_rf","smb","hml"]], evdates),
                abnormal_returns(R[us], R[["^GSPC"]].rename(columns={"^GSPC":"mkt"}), evdates)], axis=1)
g = dict(zip(firms.ticker_guess, firms.group))
dirmap = panel.groupby(["event_date","group"]).direction.first().unstack()   # event x group direction
real = second_stage(panel.assign(dir_bank=np.where(panel.group=="bank", panel.direction, 0.0)), ["dir_bank"])
b_real = real["beta"][0]
idx = AR.index[(AR.index >= "2023-01-01") & (AR.index <= F.index.max())]
excl = set()
for d in evdates:
    pos = AR.index.searchsorted(d)
    excl |= set(AR.index[max(0,pos-10):pos+11])
pool = [d for d in idx if d not in excl]
rng = np.random.default_rng(20260921)
draws = []
bank_dirs = dirmap["bank"].values
for _ in range(500):
    days = rng.choice(pool, size=len(evdates), replace=False)
    order = rng.permutation(len(evdates))
    rows = []
    for k, d in enumerate(days):
        dvec = bank_dirs[order[k]]
        s = AR.loc[d]
        for firm, v in s.items():
            if np.isfinite(v) and firm in g:
                rows.append(dict(event_date=d, firm=firm, car=v,
                                 dir_bank=dvec if g[firm]=="bank" else 0.0))
    pp = pd.DataFrame(rows)
    draws.append(second_stage(pp, ["dir_bank"])["beta"][0])
draws = np.array(draws)
p = (1 + (np.abs(draws) >= abs(b_real)).sum()) / (1 + len(draws))
print(f"bank coefficient (binary exposure, 1-day): {b_real*100:.3f} pp")
print(f"placebo-date distribution: sd {draws.std()*100:.3f} pp, 95% band [{np.percentile(draws,2.5)*100:.3f}, {np.percentile(draws,97.5)*100:.3f}]")
print(f"placebo-date p-value (two-sided, 500 draws): {p:.3f}")
pd.Series(draws).to_csv("output/placebo_dates_bank.csv", index=False)
