# ===== Copy this whole block into ONE Colab cell (https://colab.research.google.com) and press Run =====
import pandas as pd, io, requests
from google.colab import files

BASE = "https://www.eba.europa.eu/assets/TE2023/Full_database/837203/"
H = {"User-Agent": "Mozilla/5.0"}

# 1) liabilities data, filtered to what the paper needs (keeps the upload small)
r = requests.get(BASE + "tr_oth.csv", headers=H, timeout=120); r.raise_for_status()
df = pd.read_csv(io.StringIO(r.content.decode("utf-8-sig")), dtype=str)
keep = df[df["Item"].isin(["2321214", "2321215", "2321010"])]   # total liabilities, liabilities by sector/instrument, total assets
keep.to_csv("eba_liabilities.csv", index=False)
print("liabilities rows kept:", len(keep), "| banks:", keep["LEI_Code"].nunique())

# 2) the code lists needed to decode sector and instrument
m = requests.get(BASE + "TR_Metadata.xlsx", headers=H, timeout=120); m.raise_for_status()
xl = pd.ExcelFile(io.BytesIO(m.content))
print("metadata sheets:", xl.sheet_names)
out = []
for sh in xl.sheet_names:
    if any(k in sh.lower() for k in ["exposure", "financial_instr", "financial instr"]):
        t = xl.parse(sh, header=None).dropna(how="all")
        t.insert(0, "sheet", sh); out.append(t)
pd.concat(out).to_csv("eba_codes.csv", index=False)

files.download("eba_liabilities.csv"); files.download("eba_codes.csv")
# ===== Two files download automatically. Upload both here. =====
