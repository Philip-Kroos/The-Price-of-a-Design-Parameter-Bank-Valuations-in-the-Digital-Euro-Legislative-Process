"""Download the price data for the digital euro event study.

Run locally (not in the sandbox):
    pip install yfinance pandas
    python download_prices.py

Writes two files next to the script:
    prices_daily.csv   date, ticker, adj_close   (long format)
    download_log.csv   ticker, rows, first, last, status

Then upload prices_daily.csv and download_log.csv to the chat.
"""
import sys, time
import pandas as pd

TICKERS = {
    # --- euro area banks ---
    "DBK.DE": "Deutsche Bank", "CBK.DE": "Commerzbank",
    "BNP.PA": "BNP Paribas", "GLE.PA": "Societe Generale", "ACA.PA": "Credit Agricole",
    "SAN.MC": "Banco Santander", "BBVA.MC": "BBVA", "CABK.MC": "CaixaBank",
    "SAB.MC": "Banco Sabadell", "BKT.MC": "Bankinter", "UNI.MC": "Unicaja",
    "ISP.MI": "Intesa Sanpaolo", "UCG.MI": "UniCredit", "BAMI.MI": "Banco BPM",
    "BPE.MI": "BPER Banca", "MB.MI": "Mediobanca",
    "INGA.AS": "ING Groep", "ABN.AS": "ABN AMRO", "KBC.BR": "KBC Group",
    "EBS.VI": "Erste Group", "RBI.VI": "Raiffeisen Bank Intl", "BG.VI": "BAWAG",
    "BIRG.IR": "Bank of Ireland", "A5G.IR": "AIB Group",
    "ETE.AT": "National Bank of Greece", "EUROB.AT": "Eurobank",
    "ALPHA.AT": "Alpha Services", "TPEIR.AT": "Piraeus Financial",
    "BCP.LS": "Banco Comercial Portugues", "BOCH.CY": "Bank of Cyprus",
    # --- payment providers and card networks ---
    "MA": "Mastercard", "V": "Visa", "AXP": "American Express", "PYPL": "PayPal",
    "NEXI.MI": "Nexi", "WLN.PA": "Worldline", "ADYEN.AS": "Adyen",
    "WISE.L": "Wise", "FI": "Fiserv", "GPN": "Global Payments",
    # --- device gatekeepers and bigtech ---
    "AAPL": "Apple", "GOOGL": "Alphabet", "AMZN": "Amazon", "META": "Meta",
    # --- non-euro control banks ---
    "SWED-A.ST": "Swedbank", "SHB-A.ST": "Handelsbanken", "DANSKE.CO": "Danske Bank",
    "DNB.OL": "DNB Bank", "LLOY.L": "Lloyds", "NWG.L": "NatWest", "UBSG.SW": "UBS Group",
    # --- market and sector indices (for the factor model alternatives) ---
    "^STOXX": "STOXX Europe 600", "^SX7P": "STOXX Europe 600 Banks", "^GSPC": "S&P 500",
}

START, END = "2022-01-01", "2026-09-30"

def main():
    try:
        import yfinance as yf
    except ImportError:
        sys.exit("pip install yfinance pandas first")
    frames, log = [], []
    for t in TICKERS:
        try:
            df = yf.download(t, start=START, end=END, auto_adjust=True,
                             progress=False, threads=False)
            if df is None or df.empty:
                log.append(dict(ticker=t, rows=0, first="", last="", status="EMPTY"))
                continue
            close = df["Close"]
            if hasattr(close, "columns"):
                close = close.iloc[:, 0]
            out = close.rename("adj_close").to_frame()
            out["ticker"] = t
            out = out.reset_index().rename(columns={"Date": "date"})
            frames.append(out[["date", "ticker", "adj_close"]])
            log.append(dict(ticker=t, rows=len(out),
                            first=str(out.date.min())[:10], last=str(out.date.max())[:10],
                            status="ok"))
            print(f"{t:12s} {len(out):5d} rows")
        except Exception as exc:
            log.append(dict(ticker=t, rows=0, first="", last="", status=f"ERROR {exc}"))
            print(f"{t:12s} FAILED: {exc}")
        time.sleep(0.4)
    if frames:
        pd.concat(frames).to_csv("prices_daily.csv", index=False)
    pd.DataFrame(log).to_csv("download_log.csv", index=False)
    print("\nwritten: prices_daily.csv, download_log.csv")
    bad = [r for r in log if r["status"] != "ok"]
    if bad:
        print(f"{len(bad)} tickers failed or were empty; send download_log.csv so the symbols can be fixed")

if __name__ == "__main__":
    main()
