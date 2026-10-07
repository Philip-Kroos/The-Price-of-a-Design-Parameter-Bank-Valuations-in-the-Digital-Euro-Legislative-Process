"""ECB deposit facility rate as a daily decimal risk-free rate.

Used by src/run_round10.py and src/run_round10b.py for the euro excess-return market model.
Input: data/raw/ecb_deposit_facility_rate_daily.csv, an ECB Data Portal export that contains
the series FM.D.U2.EUR.4F.KR.DFR.LEV (deposit facility rate, percent per annum, one row per
calendar day). The rate is carried forward over gaps and converted to a daily decimal rate by
dividing by 100 and 252.
"""
from pathlib import Path
import pandas as pd

DEFAULT_DFR = Path("data/raw/ecb_deposit_facility_rate_daily.csv")
SERIES = "FM.D.U2.EUR.4F.KR.DFR.LEV"


def load_dfr_daily(path: str | Path = DEFAULT_DFR) -> pd.Series:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Download ECB series {SERIES} from the ECB Data Portal.")
    df = pd.read_csv(path)
    date_col = next((c for c in df.columns if c.upper() in ("DATE", "TIME_PERIOD")), None)
    if date_col is None:
        raise ValueError("ECB file needs a DATE or TIME_PERIOD column")
    value_col = next((c for c in df.columns if SERIES in c), None)
    if value_col is None and "OBS_VALUE" in df.columns:
        value_col = "OBS_VALUE"   # single-series export
    if value_col is None:
        raise ValueError(f"No column for {SERIES} in {path}")
    s = pd.to_numeric(df[value_col], errors="coerce")
    s.index = pd.to_datetime(df[date_col])
    return s.sort_index().ffill().rename("dfr") / 100 / 252
