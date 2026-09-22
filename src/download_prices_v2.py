"""Price download with three fallbacks. Run locally, not in the sandbox.

    pip install -U yfinance curl_cffi pandas_datareader pandas requests
    python download_prices_v2.py

For each symbol it tries, in order:
    1) yfinance          (Yahoo; needs a CURRENT version, old ones return Access Denied)
    2) pandas_datareader (Stooq reader; different headers, often works when requests does not)
    3) requests          (Stooq CSV endpoint with browser-like headers)

Writes prices_daily.csv (date, ticker, close, source) and download_log.csv.
Upload BOTH files. The log tells me which symbols to fix.
"""
import io, time, sys
import pandas as pd

# name: (yahoo symbol, stooq symbol)
SYMBOLS = {
 "Deutsche Bank":("DBK.DE","dbk.de"), "Commerzbank":("CBK.DE","cbk.de"),
 "BNP Paribas":("BNP.PA","bnp.fr"), "Societe Generale":("GLE.PA","gle.fr"), "Credit Agricole":("ACA.PA","aca.fr"),
 "Santander":("SAN.MC","san.es"), "BBVA":("BBVA.MC","bbva.es"), "CaixaBank":("CABK.MC","cabk.es"),
 "Sabadell":("SAB.MC","sab.es"), "Bankinter":("BKT.MC","bkt.es"), "Unicaja":("UNI.MC","uni.es"),
 "Intesa":("ISP.MI","isp.it"), "UniCredit":("UCG.MI","ucg.it"), "Banco BPM":("BAMI.MI","bami.it"),
 "BPER":("BPE.MI","bpe.it"), "Mediobanca":("MB.MI","mb.it"),
 "ING":("INGA.AS","inga.nl"), "ABN AMRO":("ABN.AS","abn.nl"), "KBC":("KBC.BR","kbc.be"),
 "Erste":("EBS.VI","ebs.at"), "Raiffeisen":("RBI.VI","rbi.at"), "BAWAG":("BG.VI","bg.at"),
 "Bank of Ireland":("BIRG.IR","birg.ie"), "AIB":("A5G.IR","a5g.ie"),
 "NBG":("ETE.AT","ete.gr"), "Eurobank":("EUROB.AT","eurob.gr"), "Alpha":("ALPHA.AT","alpha.gr"),
 "Piraeus":("TPEIR.AT","tpeir.gr"), "BCP":("BCP.LS","bcp.pt"), "Bank of Cyprus":("BOCH.CY",""),
 "Mastercard":("MA","ma.us"), "Visa":("V","v.us"), "AmEx":("AXP","axp.us"), "PayPal":("PYPL","pypl.us"),
 "Nexi":("NEXI.MI","nexi.it"), "Worldline":("WLN.PA","wln.fr"), "Adyen":("ADYEN.AS","adyen.nl"),
 "Wise":("WISE.L","wise.uk"), "Fiserv":("FI","fi.us"), "Global Payments":("GPN","gpn.us"),
 "Apple":("AAPL","aapl.us"), "Alphabet":("GOOGL","googl.us"), "Amazon":("AMZN","amzn.us"), "Meta":("META","meta.us"),
 "Swedbank":("SWED-A.ST","swed-a.se"), "Handelsbanken":("SHB-A.ST","shb-a.se"),
 "Danske":("DANSKE.CO","danske.dk"), "DNB":("DNB.OL","dnb.no"),
 "Lloyds":("LLOY.L","lloy.uk"), "NatWest":("NWG.L","nwg.uk"), "UBS":("UBSG.SW","ubsg.ch"),
 "STOXX600":("^STOXX","^stoxx"), "SP500":("^GSPC","^spx"),
}
START, END = "2022-01-01", "2026-09-30"

def via_yfinance(sym):
    import yfinance as yf
    df = yf.download(sym, start=START, end=END, auto_adjust=True, progress=False, threads=False)
    if df is None or df.empty: return None
    c = df["Close"]
    if hasattr(c, "columns"): c = c.iloc[:, 0]
    out = c.rename("close").to_frame().reset_index().rename(columns={"Date": "date"})
    return out

def via_datareader(sym):
    from pandas_datareader import data as web
    df = web.DataReader(sym.upper(), "stooq", START, END)
    if df is None or df.empty: return None
    return df["Close"].rename("close").to_frame().reset_index().rename(columns={"Date": "date"}).sort_values("date")

def via_requests(sym):
    import requests
    url = f"https://stooq.com/q/d/l/?s={sym}&d1={START.replace('-','')}&d2={END.replace('-','')}&i=d"
    h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "text/csv,*/*",
         "Referer": f"https://stooq.com/q/d/?s={sym}"}
    r = requests.get(url, headers=h, timeout=30)
    if not r.text.strip().lower().startswith("date"): return None
    df = pd.read_csv(io.StringIO(r.text))
    return df.rename(columns={"Date": "date", "Close": "close"})[["date", "close"]]

def main():
    frames, log = [], []
    for name, (ysym, ssym) in SYMBOLS.items():
        got, src, err = None, "", ""
        for label, fn, arg in (("yfinance", via_yfinance, ysym),
                               ("datareader", via_datareader, ssym or ysym),
                               ("requests", via_requests, ssym)):
            if not arg: continue
            try:
                got = fn(arg)
                if got is not None and len(got):
                    src = label; break
            except Exception as exc:
                err = f"{label}: {exc}"[:90]
        if got is None:
            log.append(dict(name=name, yahoo=ysym, stooq=ssym, rows=0, source="", note=err or "no data"))
            print(f"{name:20s} FAILED  {err}")
        else:
            got["ticker"] = ysym
            got["source"] = src
            frames.append(got[["date", "ticker", "close", "source"]])
            log.append(dict(name=name, yahoo=ysym, stooq=ssym, rows=len(got), source=src, note=""))
            print(f"{name:20s} {len(got):5d} rows via {src}")
        time.sleep(0.5)
    if frames:
        pd.concat(frames).to_csv("prices_daily.csv", index=False)
    pd.DataFrame(log).to_csv("download_log.csv", index=False)
    ok = sum(1 for r in log if r["rows"])
    print(f"\n{ok} of {len(SYMBOLS)} symbols downloaded. Files: prices_daily.csv, download_log.csv")

if __name__ == "__main__":
    main()
