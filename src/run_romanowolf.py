import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import abnormal_returns, second_stage
R = pd.read_csv("data/derived/returns_daily.csv", index_col=0, parse_dates=True)
F = pd.read_csv("data/derived/ff3_europe_daily.csv", parse_dates=["date"]).set_index("date")
firms = pd.read_csv("data/hand/firm_universe_v0.csv"); firms = firms[firms.ticker_guess.isin(R.columns)]
panel = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"])
evd = sorted(panel.event_date.unique())
US = {"MA","V","AXP","PYPL","GPN","AAPL","GOOGL","AMZN","META"}
eu = [t for t in firms.ticker_guess if t not in US]; us = [t for t in firms.ticker_guess if t in US]
com = R.index.intersection(F.index)
AR = pd.concat([abnormal_returns(R.loc[com, eu], F.loc[com, ["mkt_rf","smb","hml"]], evd),
                abnormal_returns(R[us], R[["^GSPC"]].rename(columns={"^GSPC":"mkt"}), evd)], axis=1)
g = dict(zip(firms.ticker_guess, firms.group)); G = {k: {"device":"gate","bigtech":"gate"}.get(v, v) for k, v in g.items()}
dirs = panel.assign(grp=panel.group.replace({"device":"gate","bigtech":"gate"})).groupby(["event_date","grp"]).direction.first().unstack().fillna(0)
cols = ["bank","payments","gate"]
def fit(rows):
    pp = pd.DataFrame(rows)
    for c in cols: pp[f"d_{c}"] = np.where(pp.grp==c, pp.dv, 0.0)
    return second_stage(pp, [f"d_{c}" for c in cols])["beta"]
real_rows = [dict(event_date=r.event_date, firm=r.firm, car=r.car, grp=G[r.firm], dv=float(dirs.loc[r.event_date].get(G[r.firm], 0.0)))
             for r in panel.itertuples() if r.firm in G]
b_real = np.array(fit(real_rows))
excl = set()
for d in evd:
    pos = AR.index.searchsorted(d); excl |= set(AR.index[max(0,pos-10):pos+11])
pool = [d for d in AR.index[(AR.index>="2023-01-01") & (AR.index<=F.index.max())] if d not in excl]
rng = np.random.default_rng(99); draws = []
for _ in range(300):
    days = rng.choice(pool, size=len(evd), replace=False); order = rng.permutation(len(evd)); rows=[]
    for k, d in enumerate(days):
        dv = dirs.iloc[order[k]]
        for firm, v in AR.loc[d].items():
            if np.isfinite(v) and firm in G:
                rows.append(dict(event_date=d, firm=firm, car=v, grp=G[firm], dv=float(dv.get(G[firm], 0.0))))
    draws.append(fit(rows))
D = np.array(draws); sd = D.std(0); t_real = b_real/sd; T = D/sd
# Romano-Wolf step-down on |t|
order = np.argsort(-np.abs(t_real)); p_adj = np.zeros(3); prev = 0
for i, k in enumerate(order):
    remaining = order[i:]
    mx = np.abs(T[:, remaining]).max(1)
    pk = (1 + (mx >= abs(t_real[k])).sum()) / (1 + len(mx))
    prev = max(prev, pk); p_adj[k] = prev
raw = [(1+(np.abs(T[:,k])>=abs(t_real[k])).sum())/(1+len(T)) for k in range(3)]
out = {c: dict(beta=float(b_real[k]), p_raw=float(raw[k]), p_romano_wolf=float(p_adj[k])) for k, c in enumerate(cols)}
json.dump(out, open("output/romano_wolf.json","w"), indent=1)
for c, v in out.items(): print(f"{c:9s} beta {v['beta']*100:6.3f} pp  p_raw {v['p_raw']:.3f}  p_RW {v['p_romano_wolf']:.3f}")
