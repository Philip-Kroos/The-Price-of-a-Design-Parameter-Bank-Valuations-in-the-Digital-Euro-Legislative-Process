# The Price of a Design Parameter

**Bank Valuations in the Digital Euro Legislative Process**  
Philip Kroos · September 2026

Replication and companion repository for the paper **“The Price of a Design Parameter: Bank Valuations in the Digital Euro Legislative Process.”**

The paper studies whether financial markets priced the concrete design choices of the digital euro during the European legislative process. It combines a hand-coded event study, pre-proposal bank deposit exposure, a public record of 309 disclosed meetings with interest representatives, and several falsification and robustness exercises.

## Main findings

- In the pre-specified bank-exposure specification, a euro-area bank one standard deviation more deposit-funded gains about **0.05 percentage points** more on an event that limits the digital euro (`permutation p = 0.47`).
- Conservative release-time alignment raises the estimate to roughly **0.15–0.17 percentage points**, providing some evidence of a small effect but not a robust large effect across inference procedures.
- Events that **set or signal a design parameter** show no detectable valuation effect; the design-only estimate is approximately zero.
- Using predetermined exposure and strictly pre-event factor loadings, the same design detects a substantially larger response on the day of the **October 2020 Eurosystem report**, showing that the event-study design can detect effects of the magnitude documented in the earlier literature.
- The published legislative transparency record contains **309 disclosed meetings**, showing that the same parameters were intensely contested even though the valuation response was modest.

The current paper PDF is available at [`paper/main.pdf`](paper/main.pdf).

## Repository structure

```text
.
├── README.md
├── REPLICATION.md
├── requirements.txt
├── run_all.py
├── CITATION.cff
├── data/
│   ├── hand/       hand-collected event, firm, timing and lobbying data
│   ├── raw/        downloaded source data used by the analysis
│   └── derived/    cleaned exposure, return and lobbying datasets
├── docs/
│   ├── pap_v1.md               exact frozen PAP snapshot (v1.13)
│   ├── pap_history.md          subsequent chronological project log
│   ├── coding_freeze.sha256    frozen hashes and timestamps
│   ├── deviations.md           departures from the pre-specified plan
│   ├── second_coder_instructions.md
│   └── second_coder_sheet.csv
├── output/         stored estimation outputs used in the paper
├── paper/          paper source, PDF, tables and figures
├── src/            analysis and data-construction code
└── tests/          unit tests for the event-study functions
```

## Quick reproduction

Create a Python environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the core replication pipeline:

```bash
python run_all.py
```

Run the unit tests:

```bash
python -m pytest -q
```

`run_all.py` uses the data already bundled in the repository and reproduces the core event-study, continuous-exposure, timing, placebo, early-event and robustness outputs. See [`REPLICATION.md`](REPLICATION.md) for the exact script map and the one post-review robustness exercise that additionally requires an official ECB deposit-facility-rate download.

## Pre-specification and transparency

This project was **pre-specified, not externally pre-registered**. The event coding and firm universe were frozen before any return was computed; the bank-exposure definition was frozen before the first estimate using it; and the early-event coding and historical exposure were frozen before the corresponding estimates.

The exact frozen PAP snapshot is [`docs/pap_v1.md`](docs/pap_v1.md). Its SHA-256 hash matches the value recorded in [`docs/coding_freeze.sha256`](docs/coding_freeze.sha256). Later additions to the project log are preserved separately in [`docs/pap_history.md`](docs/pap_history.md), so the frozen snapshot is not overwritten by subsequent amendments.

All departures from the plan are documented in the paper and in [`docs/deviations.md`](docs/deviations.md).

## Data

The repository contains the data needed for the bundled replication runs, including:

- European Parliament / Council / ECB event coding and timing;
- the published negotiation record used to construct the 309-meeting dataset;
- EBA bank-exposure inputs and derived exposure measures;
- European Fama–French factors used in the pre-specified first stage;
- daily price and return panels used in the event study;
- the 2019 exposure measure and 2020–2021 event extension.

The paper also reports a fully euro-denominated excess-return robustness check using the ECB deposit-facility rate. The frozen outputs from that check are included. To rerun those specific post-review scripts from raw inputs, place an ECB Data Portal export for series `FM.D.U2.EUR.4F.KR.DFR.LEV` at `data/raw/ecb_dfr_daily.csv`; see `REPLICATION.md`.

## Key output files

- `output/main_results.json` — group-level event-study estimates
- `output/continuous_results_w01.json` — continuous bank-exposure estimates
- `output/timing_robustness.json` — release-time and same-day-news checks
- `output/referee_analyses.json` — design-vs-implementation and non-euro placebo analyses
- `output/robustness_table.json` — robustness specifications
- `output/round10_early.json` — early-event positive-control checks
- `output/round10_late.json` — euro-denominated and provider-coding sensitivity checks

## Citation

If you use this repository, please cite the paper. Machine-readable citation metadata are provided in [`CITATION.cff`](CITATION.cff).

## Notes

- The repository contains public/research data and code only; no proprietary market data are included beyond the archived public price series used in the analysis.
- Download helper scripts are retained for provenance but are not required for the bundled replication run.
- No software license has been added automatically. Add the license you want before inviting third-party reuse of the code.
