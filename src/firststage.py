"""First stage in two versions. 'ff3usd': pre-specified, European FF3 factors (USD-based) on local-currency returns.
'local3': currency-consistent, market factor replaced by the local-currency STOXX Europe 600 return; SMB and HML are
long-short USD portfolios whose currency component largely cancels. US-listed firms: market model on the S&P 500 in both."""
import numpy as np, pandas as pd
from src.eventstudy import abnormal_returns
R = pd.read_csv("data/derived/returns_daily.csv", index_col=0, parse_dates=True)
F = pd.read_csv("data/derived/ff3_europe_daily.csv", parse_dates=["date"]).set_index("date")
fu = pd.read_csv("data/hand/firm_universe_v0.csv"); fu = fu[fu.ticker_guess.isin(R.columns)]
US = {"MA","V","AXP","PYPL","GPN","AAPL","GOOGL","AMZN","META"}
EU = [t for t in fu.ticker_guess if t not in US]; USL = [t for t in fu.ticker_guess if t in US]
GROUP = dict(zip(fu.ticker_guess, fu.group))
def AR(evd, version="ff3usd", est=250):
    com = R.index.intersection(F.index)
    if version == "ff3usd":
        fac = F.loc[com, ["mkt_rf","smb","hml"]]
    else:
        fac = pd.concat([R.loc[com, "^STOXX"].rename("mkt_local"), F.loc[com, ["smb","hml"]]], axis=1)
    a = abnormal_returns(R.loc[com, EU], fac, evd, est_window=est)
    b = abnormal_returns(R[USL], R[["^GSPC"]].rename(columns={"^GSPC":"mkt"}), evd, est_window=est)
    return pd.concat([a, b], axis=1)
def window_car(A, d, timing):
    pos = A.index.searchsorted(d)
    if timing == "before_close": w = A.iloc[pos:pos+1]
    elif timing == "after_close": w = A.iloc[pos+1:pos+2]
    else: w = A.iloc[pos:pos+2]
    return w.sum(min_count=len(w))
