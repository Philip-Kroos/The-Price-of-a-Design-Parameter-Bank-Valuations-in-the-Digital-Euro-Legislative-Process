# Raw data

| File | Content | Source |
|---|---|---|
| `prices_daily.csv` | daily adjusted closes, 2022–2026 | Yahoo Finance via `yfinance` (`src/colab_download.py`) |
| `prices_2019_2021.csv` | daily adjusted closes, 2019–2021 | Yahoo Finance via `yfinance` (`src/colab_download_early.py`) |
| `download_log*.csv` | which tickers downloaded, with row counts | written by the download scripts |
| `Europe_3_Factors_Daily.csv` | European Fama–French three factors, daily, in US dollars | Kenneth French Data Library |
| `eba_liabilities.csv`, `eba_codes.csv` | bank liabilities, 31 March 2023 | EBA EU-wide transparency exercise 2023 (`src/colab_eba.py`) |
| `eba2020_liabilities.csv`, `eba2020_codes.csv` | bank liabilities, 31 December 2019 | EBA EU-wide transparency exercise 2020 (`src/colab_eba2020.py`) |
| `ecb_deposit_facility_rate_daily.csv` | ECB key rates, daily; the scripts use series `FM.D.U2.EUR.4F.KR.DFR.LEV` | ECB Data Portal |

The price files are included for replication. Their redistribution is subject to Yahoo's terms of use; the
download scripts re-create them.
