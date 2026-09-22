"""Helpers for optional ECB deposit-facility-rate robustness checks."""
from pathlib import Path
import pandas as pd

DEFAULT_DFR = Path("data/raw/ecb_dfr_daily.csv")


def load_dfr_daily(path: str | Path = DEFAULT_DFR) -> pd.Series:
    """Load the ECB deposit-facility-rate export as a daily decimal rate.

    Expected series: FM.D.U2.EUR.4F.KR.DFR.LEV (percent per annum).
    The function accepts common ECB Data Portal CSV layouts with DATE or
    TIME_PERIOD and OBS_VALUE columns. Values are converted to a daily decimal
    rate by dividing the annual percent rate by 100 and 252.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Download ECB series FM.D.U2.EUR.4F.KR.DFR.LEV "
            "and save it there. See data/raw/README.md."
        )
    df = pd.read_csv(path)
    cols = {c.upper(): c for c in df.columns}
    date_col = cols.get("DATE") or cols.get("TIME_PERIOD")
    value_col = cols.get("OBS_VALUE")
    if date_col is None:
        raise ValueError("ECB DFR file needs a DATE or TIME_PERIOD column")
    if value_col is None:
        candidates = []
        for c in df.columns:
            if c == date_col:
                continue
            x = pd.to_numeric(df[c], errors="coerce")
            if x.notna().sum() > 0:
                candidates.append((x.notna().sum(), c))
        if not candidates:
            raise ValueError("Could not identify the rate column in ECB DFR file")
        value_col = max(candidates)[1]
    s = pd.Series(
        pd.to_numeric(df[value_col], errors="coerce").to_numpy(),
        index=pd.to_datetime(df[date_col]),
        name="dfr",
    ).dropna().sort_index()
    return s / 100.0 / 252.0
