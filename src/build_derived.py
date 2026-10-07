"""Build data/derived from data/raw and data/hand.

Outputs
  data/derived/returns_daily.csv          daily log returns, 2022-01-03 to 2026-09-21, one column per ticker
  data/derived/ff3_europe_daily.csv       European three factors and risk-free rate, decimals, 2021-06-01 to 2026-07-31
  data/derived/bank_exposure_2023q1.csv   deposit exposure on 31 March 2023 (EBA transparency exercise 2023)
  data/derived/bank_exposure_2019q4.csv   deposit exposure on 31 December 2019 (EBA transparency exercise 2020)
  data/derived/lobby_categorised.csv      negotiation record with the hand-assigned category of each organisation
  data/derived/lobby_intensity_by_event.csv  meetings in the 7, 30 and 60 days before each event, by category

Run from the repository root:  python src/build_derived.py [--check]
With --check the script compares each output with the file already on disk and reports the largest difference.
"""
import sys
import numpy as np, pandas as pd

CHECK = "--check" in sys.argv
OUT = {}

# --- returns: log changes of adjusted closes, as downloaded
P = pd.read_csv("data/raw/prices_daily.csv", parse_dates=["date"])
W = P.pivot_table(index="date", columns="ticker", values="close").sort_index()
R = np.log(W).diff()
R.index.name = "date"
OUT["returns_daily"] = R

# --- European three factors from the Kenneth French Data Library (percent -> decimal)
raw = open("data/raw/Europe_3_Factors_Daily.csv").read().splitlines()
start = next(i for i, l in enumerate(raw) if l.replace(" ", "").lower().startswith(",mkt-rf"))
rows = []
for line in raw[start + 1:]:
    p = [x.strip() for x in line.split(",")]
    if len(p) < 5 or not p[0].isdigit():
        break
    rows.append(p)
F = pd.DataFrame(rows, columns=["date", "mkt_rf", "smb", "hml", "rf"])
F["date"] = pd.to_datetime(F.date, format="%Y%m%d")
for c in ["mkt_rf", "smb", "hml", "rf"]:
    F[c] = F[c].astype(float) / 100
F = F[(F.date >= "2021-06-01") & (F.date <= "2026-07-31")].reset_index(drop=True)
OUT["ff3_europe_daily"] = F

# --- bank exposure from the EBA transparency exercises
# total liabilities: item xx21214; deposits by sector: item xx21215 with Exposure 301 (non-financial
# corporations) and 401 (households); Financial_instruments 30 = deposits, 31 = of which overnight.
lei = pd.read_csv("data/hand/lei_map.csv")


def exposure(path, period, total_item, sector_item):
    E = pd.read_csv(path)
    E = E[E.Period == period]
    out = []
    for r in lei.itertuples():
        e = E[E.LEI_Code == r.lei]
        tot = e.loc[e.Item == total_item, "Amount"].sum()
        sec = e[(e.Item == sector_item) & e.Exposure.isin([301, 401])]
        dep = sec.loc[sec.Financial_instruments == 30, "Amount"].sum()
        on = sec.loc[sec.Financial_instruments == 31, "Amount"].sum()
        out.append(dict(ticker=r.ticker, lei=r.lei, eba_name=r.eba_name, group=r.group,
                        total_liab=tot, dep_hh_nfc=dep, overnight_hh_nfc=on))
    x = pd.DataFrame(out)
    x["dep_share"] = x.dep_hh_nfc / x.total_liab
    x["overnight_share"] = x.overnight_hh_nfc / x.total_liab
    return x


x23 = exposure("data/raw/eba_liabilities.csv", 202303, 2321214, 2321215)
OUT["bank_exposure_2023q1"] = x23
x19 = exposure("data/raw/eba2020_liabilities.csv", 201912, 2021214, 2021215)
x19 = x19.rename(columns={"dep_share": "dep_share_2019", "overnight_share": "overnight_share_2019"})
x19 = x19[["ticker", "lei", "eba_name", "group", "dep_share_2019", "overnight_share_2019"]].merge(
    x23[["ticker", "dep_share"]], on="ticker", how="left")
OUT["bank_exposure_2019q4"] = x19

# --- negotiation record
L = pd.read_csv("data/hand/lobby_meetings_v1.csv")
cat = pd.read_csv("data/hand/lobby_categories.csv")
L = L.merge(cat, on="organisation", how="left")
assert L.category.notna().all(), "organisation without category"
OUT["lobby_categorised"] = L

L["date"] = pd.to_datetime(L.date)
ev = pd.read_csv("data/hand/event_coding_v1.csv", parse_dates=["date"])
SIDE = {"bank_side": ["bank", "bank_assoc"], "payments": ["payments"], "retail_civil": ["retail", "civil_society"]}
rows = []
for r in ev.sort_values("date").itertuples():
    pre = lambda k: (L.date < r.date) & (L.date >= r.date - pd.Timedelta(days=k))
    d = dict(event_id=r.event_id, date=r.date.date(), meetings_7d=int(pre(7).sum()),
             meetings_30d=int(pre(30).sum()), meetings_60d=int(pre(60).sum()))
    for k, cats in SIDE.items():
        d[k] = int((pre(30) & L.category.isin(cats)).sum())
    rows.append(d)
OUT["lobby_intensity_by_event"] = pd.DataFrame(rows)

# --- write or check
for name, df in OUT.items():
    path = f"data/derived/{name}.csv"
    if CHECK:
        old = pd.read_csv(path)
        new = df.reset_index() if name == "returns_daily" else df.copy()
        new.columns = [str(c) for c in new.columns]
        common = [c for c in old.columns if c in new.columns]
        if name == "lobby_intensity_by_event":
            new = new.set_index("event_id").loc[old.event_id].reset_index()
        a, b = old[common], new[common].reset_index(drop=True)
        num = [c for c in common if pd.api.types.is_numeric_dtype(a[c])]
        diff = (a[num] - b[num].astype(float)).abs().max().max() if num else 0.0
        same_text = all((a[c].astype(str) == b[c].astype(str)).all() for c in common if c not in num and c != "date")
        print(f"{name:28s} rows {len(a)}/{len(b)}  max numeric diff {diff:.2e}  text identical {same_text}")
    else:
        df.to_csv(path, index=(name == "returns_daily"))
        print("wrote", path, df.shape)
