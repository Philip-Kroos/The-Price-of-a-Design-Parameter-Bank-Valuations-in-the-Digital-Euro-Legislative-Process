# ===== Copy this whole block into ONE cell at https://colab.research.google.com and press Run =====
# Colab setup (run in a separate cell if needed): %pip -q install -U yfinance curl_cffi

import time, pandas as pd, yfinance as yf
from google.colab import files

T = ["DBK.DE","CBK.DE","BNP.PA","GLE.PA","ACA.PA","SAN.MC","BBVA.MC","CABK.MC","SAB.MC","BKT.MC","UNI.MC",
     "ISP.MI","UCG.MI","BAMI.MI","BPE.MI","MB.MI","INGA.AS","ABN.AS","KBC.BR","EBS.VI","RBI.VI","BG.VI",
     "BIRG.IR","A5G.IR","ETE.AT","EUROB.AT","ALPHA.AT","TPEIR.AT","BCP.LS","BOCH.CY",
     "MA","V","AXP","PYPL","NEXI.MI","WLN.PA","ADYEN.AS","WISE.L","FI","GPN",
     "AAPL","GOOGL","AMZN","META",
     "SWED-A.ST","SHB-A.ST","DANSKE.CO","DNB.OL","LLOY.L","NWG.L","UBSG.SW",
     "^STOXX","^SX7P","^GSPC"]

frames, log = [], []
for t in T:
    try:
        d = yf.download(t, start="2019-06-01", end="2022-01-10", auto_adjust=True, progress=False, threads=False)
        c = d["Close"]
        if hasattr(c, "columns"): c = c.iloc[:, 0]
        c = c.dropna()
        frames.append(pd.DataFrame({"date": c.index, "ticker": t, "close": c.values}))
        log.append((t, len(c))); print(t, len(c))
    except Exception as e:
        log.append((t, 0)); print(t, "FAILED", e)
    time.sleep(0.3)

pd.concat(frames).to_csv("prices_2019_2021.csv", index=False)
pd.DataFrame(log, columns=["ticker", "rows"]).to_csv("download_log_2019.csv", index=False)
files.download("prices_2019_2021.csv"); files.download("download_log_2019.csv")
# ===== Both files download automatically to your computer. Upload them here. =====
