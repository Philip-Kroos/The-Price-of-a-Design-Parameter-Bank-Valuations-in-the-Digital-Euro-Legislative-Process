# Replication guide

## 1. Environment

Recommended: Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. One-command core replication

From the repository root:

```bash
python run_all.py
```

This runs the bundled-data analyses in dependency order and then the unit tests. The full run can take several minutes because the permutation and bootstrap procedures are intentionally repeated many times.

## 3. Main script map

| Script | Purpose | Main outputs |
|---|---|---|
| `src/run_main.py` | Pre-specified group-level event study | `output/main_results.json`, `output/car_panel_w00.csv`, `output/car_panel_w01.csv` |
| `src/run_continuous.py` | Continuous bank deposit exposure | `output/continuous_results_*.json` |
| `src/run_placebo_dates.py` | Placebo-date falsification | `output/placebo_dates_bank.csv` |
| `src/run_romanowolf.py` | Multiple-testing adjustment | `output/romano_wolf.json` |
| `src/run_timing.py` | Release-time and same-day-news checks | `output/timing_robustness.json` |
| `src/run_ts_inference.py` | Inference for timestamp-aligned estimates | `output/ts_inference.json` |
| `src/run_early.py`, `src/run_early_2019.py` | 2020–21 extension and predetermined exposure | `output/early_results*.json` |
| `src/run_referee.py` | Design-vs-implementation and non-euro placebo analyses | `output/referee_analyses.json` |
| `src/run_robust_cont.py`, `src/run_robust_table.py` | Continuous-exposure robustness checks | `output/robust_continuous.json`, `output/robustness_table.json` |
| `src/run_currency.py`, `src/run_currency_inf.py` | Currency-benchmark sensitivity using bundled inputs | `output/currency_results.json`, `output/currency_inference.json` |
| `src/run_round10.py`, `src/run_round10b.py` | Strict pre-event positive control and fully euro-denominated excess-return checks | `output/round10_early.json`, `output/round10_late.json` |

## 4. ECB deposit-facility-rate input for the final post-review checks

The last two scripts use the official ECB deposit-facility-rate series as the euro risk-free rate:

`FM.D.U2.EUR.4F.KR.DFR.LEV`

The original working export was not included in the source ZIP. The frozen outputs of those checks are included in `output/`, but rerunning the scripts from raw inputs requires downloading the official ECB Data Portal CSV and saving it as:

```text
data/raw/ecb_dfr_daily.csv
```

The loader accepts common ECB exports with `DATE` or `TIME_PERIOD` and `OBS_VALUE` columns.

## 5. Tests

```bash
python -m pytest -q
```

The analysis package is named `src/` rather than `code/` to avoid shadowing Python's standard-library `code` module, which otherwise prevents `pytest`/`pdb` from importing correctly.

## 6. Frozen plan and hashes

Verify the frozen files manually with:

```bash
sha256sum data/hand/event_coding_v1.csv
sha256sum data/hand/firm_universe_v0.csv
sha256sum docs/pap_v1.md
sha256sum data/hand/events_early_2020_2021.csv
```

The expected values and freeze timestamps are recorded in `docs/coding_freeze.sha256`. The file `docs/pap_v1.md` is the exact frozen v1.13 snapshot. Later amendments are preserved separately in `docs/pap_history.md`.

## 7. Paper

The compiled paper is `paper/main.pdf`. LaTeX source and figure/table inputs are in `paper/`.

To rebuild, if a LaTeX distribution is installed:

```bash
cd paper
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```
