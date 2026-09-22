# ===== Copy into ONE Colab cell (https://colab.research.google.com) and press Run =====
# Historic deposit exposure for the 2020-21 events: EBA Spring 2020 transparency exercise,
# reference dates 30 Sep 2019 and 31 Dec 2019. Exact file addresses taken from the EBA 2020 page.
import pandas as pd, io, requests
from google.colab import files
H = {"User-Agent": "Mozilla/5.0"}
OTH = ("https://eba.europa.eu/sites/default/files/document_library/Risk%20Analysis%20and%20Data/"
       "EU%20Wide%20Transparency%20Exercise/2020/Full%20database/885655/tr_oth.csv")
META = ("https://www.eba.europa.eu/sites/default/files/document_library/Risk%20Analysis%20and%20Data/"
        "EU%20Wide%20Transparency%20Exercise/2020/Full%20database/TR_Metadata.xlsx")

r = requests.get(OTH, headers=H, timeout=180); r.raise_for_status()
df = pd.read_csv(io.StringIO(r.content.decode("utf-8-sig", errors="replace")), dtype=str)
print("columns:", list(df.columns)); print("rows:", len(df))
lab = [c for c in df.columns if c.lower() == "label"]
if lab:
    keep = df[df[lab[0]].str.contains("liabilit|deposit", case=False, na=False)]
else:   # fall back to the item codes used from 2021 on
    keep = df[df["Item"].isin(["2021214", "2021215", "2321214", "2321215"])] if "Item" in df.columns else df
keep.to_csv("eba2020_liabilities.csv", index=False)
print("rows kept:", len(keep))

m = requests.get(META, headers=H, timeout=180)
if m.ok:
    xl = pd.ExcelFile(io.BytesIO(m.content)); out = []
    for sh in xl.sheet_names:
        t = xl.parse(sh, header=None).dropna(how="all"); t.insert(0, "sheet", sh); out.append(t)
    pd.concat(out).to_csv("eba2020_codes.csv", index=False)
    files.download("eba2020_codes.csv")
files.download("eba2020_liabilities.csv")
# ===== Upload both files here. =====
