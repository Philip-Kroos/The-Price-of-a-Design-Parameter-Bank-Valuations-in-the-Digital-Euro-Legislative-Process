"""Fallback price download via stooq (no API key, no yfinance, plain CSV URLs).

Run locally:
    pip install pandas requests
    python download_prices_stooq.py

Writes prices_daily.csv and download_log.csv in the working directory.
Stooq uses its own symbol suffixes, so a few symbols may need fixing; the log says which.
"""
import io, time
import pandas as pd, requests

SYMBOLS = {
    # euro area banks
    "dbk.de":"Deutsche Bank","cbk.de":"Commerzbank",
    "bnp.fr":"BNP Paribas","gle.fr":"Societe Generale","aca.fr":"Credit Agricole",
    "san.es":"Banco Santander","bbva.es":"BBVA","cabk.es":"CaixaBank","sab.es":"Sabadell",
    "bkt.es":"Bankinter","uni.es":"Unicaja",
    "isp.it":"Intesa Sanpaolo","ucg.it":"UniCredit","bami.it":"Banco BPM","bpe.it":"BPER","mb.it":"Mediobanca",
    "inga.nl":"ING","abn.nl":"ABN AMRO","kbc.be":"KBC",
    "ebs.at":"Erste Group","rbi.at":"Raiffeisen","bg.at":"BAWAG",
    "birg.ie":"Bank of Ireland","a5g.ie":"AIB",
    "ete.gr":"National Bank of Greece","eurob.gr":"Eurobank","alpha.gr":"Alpha","tpeir.gr":"Piraeus",
    "bcp.pt":"BCP",
    # payments, devices, bigtech
    "ma.us":"Mastercard","v.us":"Visa","axp.us":"American Express","pypl.us":"PayPal",
    "nexi.it":"Nexi","wln.fr":"Worldline","adyen.nl":"Adyen","fi.us":"Fiserv","gpn.us":"Global Payments",
    "aapl.us":"Apple","googl.us":"Alphabet","amzn.us":"Amazon","meta.us":"Meta",
    # non-euro controls
    "swed-a.se":"Swedbank","shb-a.se":"Handelsbanken","danske.dk":"Danske","dnb.no":"DNB",
    "lloy.uk":"Lloyds","nwg.uk":"NatWest","ubsg.ch":"UBS",
    # indices
    "^stoxx":"STOXX Europe 600","^spx":"S&P 500",
}
D1, D2 = "20220101", "20260930"

def main():
    frames, log = [], []
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    for sym in SYMBOLS:
        url = f"https://stooq.com/q/d/l/?s={sym}&d1={D1}&d2={D2}&i=d"
        try:
            r = s.get(url, timeout=30)
            txt = r.text.strip()
            if not txt.lower().startswith("date"):
                log.append(dict(symbol=sym, rows=0, status="NO DATA: " + txt[:60])); print(f"{sym:12s} no data")
                time.sleep(0.6); continue
            df = pd.read_csv(io.StringIO(txt))
            df["ticker"] = sym
            df = df.rename(columns={"Date": "date", "Close": "adj_close"})
            frames.append(df[["date", "ticker", "adj_close"]])
            log.append(dict(symbol=sym, rows=len(df), status="ok"))
            print(f"{sym:12s} {len(df):5d} rows")
        except Exception as exc:
            log.append(dict(symbol=sym, rows=0, status=f"ERROR {exc}")); print(f"{sym:12s} FAILED {exc}")
        time.sleep(0.6)
    if frames:
        pd.concat(frames).to_csv("prices_daily.csv", index=False)
    pd.DataFrame(log).to_csv("download_log.csv", index=False)
    print("\nwritten: prices_daily.csv, download_log.csv")

if __name__ == "__main__":
    main()
