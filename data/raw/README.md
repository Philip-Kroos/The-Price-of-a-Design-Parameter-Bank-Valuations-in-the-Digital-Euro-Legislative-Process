# Raw-data note

Most raw inputs required by the bundled replication are included in this directory.

One post-review robustness exercise uses the ECB deposit-facility-rate series:

- ECB Data Portal series key: `FM.D.U2.EUR.4F.KR.DFR.LEV`
- Unit: percent per annum
- Frequency: daily

The original working file was not included in the submitted archive. To rerun `src/run_round10.py` and `src/run_round10b.py` from raw inputs, download the official ECB series and save it as:

`data/raw/ecb_dfr_daily.csv`

The frozen JSON outputs produced by those checks are already included in `output/`.
