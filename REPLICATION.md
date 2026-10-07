# Replication guide

## 1. Environment

Python 3.11 with the packages in `requirements.txt`.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. One command

From the repository root:

```bash
python run_all.py
```

The script first checks the SHA-256 hashes of the frozen inputs, then rebuilds the derived data, every
estimate and Figures 1–4, and finally runs the unit tests. It stops at the first failure. All random draws
use fixed seeds, so a rerun reproduces every number in the paper. A full run takes about one hour on one
core; most of it is the permutation and wild bootstrap inference with 9,999 draws.

All inputs are in the repository, including the ECB deposit facility rate. The price and EBA downloads
(`src/colab_download*.py`, `src/colab_eba*.py`) are not part of the run; they were executed in Google Colab
and their outputs are in `data/raw` (see `data/raw/README.md`).

## 3. Script map

| Exhibit | Script | Output |
|---|---|---|
| Derived data | `src/build_derived.py` (`--check` compares with the stored files) | `data/derived/*.csv` |
| Table 4 (power) | `src/power.py` | `output/power_secondstage.csv` |
| Table 5 (group-level estimates) | `src/run_main.py` | `output/main_results.json`, `car_panel_w00.csv`, `car_panel_w01.csv` |
| Table 5 placebo p, Figure 3B | `src/run_placebo_dates.py` | `output/placebo_dates_bank.csv` |
| Figure 3A, leave-one-event-out | `src/run_diagnostics.py` | `output/event_level_cars.csv`, `leave_one_event_out.csv` |
| Table 6 coefficients | `src/run_continuous.py w00 w01` | `output/continuous_results_w01.json` |
| Section 9.6 robustness | `src/run_robust_cont.py`, `src/run_round3.py` | `output/robust_continuous.json`, `round3.json` |
| Table 7 | `src/run_referee.py`, `src/run_timing.py`, `src/run_ts_final.py` | `output/referee_analyses.json`, `timing_robustness.json`, `ts_final.json` |
| Euro benchmarks | `src/run_currency.py`, `src/run_currency_inf.py`, `src/run_round10b.py` | `output/currency_results.json`, `currency_inference.json`, `round10_late.json` |
| Table 10 | `src/run_robust_table.py`, `src/run_alt_dates.py`, `src/run_f1.py` | `output/robustness_table.json`, `alt_dates.json`, `f1_procedural.json` |
| Romano–Wolf adjustment | `src/run_romanowolf.py` | `output/romano_wolf.json` |
| Design-only power | `src/run_round4.py` | `output/round4.json` |
| Section 9.7 and Figure 4 (2020–21) | `src/run_early.py`, `src/run_early_2019.py`, `src/run_round10.py` | `output/early_results*.json`, `round10_early.json` |
| **All permutation and wild bootstrap p-values** | `src/run_inference_final.py`, `src/run_ts_final.py` | `output/inference_final.json`, `ts_final.json` |
| Figure 1 | `src/make_fig_timeline.py` | see note below |
| Figures 2–4 | `src/make_figures.py` | `paper/figures/fig_lobby.png`, `fig_results_bank.png`, `fig_event_slopes_all.png` |

Shared code: `src/eventstudy.py` (abnormal returns, CARs, second stage with leave-one-firm-out jackknife),
`src/firststage.py` (first-stage models), `src/ecb_rate.py` (deposit facility rate).

**p-values.** Every permutation and wild cluster bootstrap p-value in the paper uses 9,999 draws and comes
from `output/inference_final.json` or `output/ts_final.json`. Some earlier scripts also print p-values with
499 or 999 draws as a by-product; those differ in the second decimal and are not the ones reported. The
placebo-date test uses 500 sets of dates and the Romano–Wolf adjustment 300 joint draws, as stated in the paper.

**Figure 1.** The paper uses the version in `paper/figures/fig_timeline.png`. `src/make_fig_timeline.py`
draws the same figure from the same data; the master script writes it to
`output/fig_timeline_regenerated.png` so that the paper's file is not replaced.

## 4. Tests

```bash
python -m pytest -q
```

The analysis package is named `src/` rather than `code/` because a package called `code` shadows Python's
standard-library module of that name, which breaks `pytest` and `pdb`.

## 5. Frozen plan and hashes

```bash
sha256sum data/hand/event_coding_v1.csv data/hand/firm_universe_v0.csv docs/pap_v1.md data/hand/events_early_2020_2021.csv
```

The expected values and freeze timestamps are in `docs/coding_freeze.sha256`; `run_all.py` checks them
before it runs anything. `docs/pap_v1.md` is the frozen plan (v1.13). The later addenda, with the date of
each decision, are in `docs/pap_history.md`. Every departure from the plan is listed in Table 11 of the
paper and in `docs/deviations.md`.

## 6. Paper

The compiled paper is `paper/main.pdf`, the one-page abstract `paper/abstract.pdf`. To rebuild with a
LaTeX distribution:

```bash
cd paper
pdflatex main.tex && pdflatex main.tex && pdflatex main.tex
pdflatex abstract.tex
```
