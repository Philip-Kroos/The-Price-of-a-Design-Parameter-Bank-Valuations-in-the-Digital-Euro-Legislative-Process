#!/usr/bin/env python3
"""Master script: checks the frozen inputs, rebuilds the derived data, every estimate and
Figures 1-4, then runs the unit tests.

Run from the repository root:  python run_all.py
Requires Python 3.11+ and the packages in requirements.txt. The price and EBA downloads
(src/colab_download*.py, src/colab_eba*.py) are not part of this run; their outputs are in
data/raw. All random draws use fixed seeds. A full run takes about one hour on one core.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FROZEN = {  # docs/coding_freeze.sha256
    "data/hand/event_coding_v1.csv": "06cc052fc56419c581a70ebed9d5d7df9153ff01a7b084386c374b3a6a6659ad",
    "data/hand/firm_universe_v0.csv": "7d407a36d225d1db523f5b18fdd75d2fc03c512baf4dce6e8f7db1ba2d39d15c",
    "docs/pap_v1.md": "cb9d788baf5526ad2118c8db7283fdc0ebe87dfdfc6f6134c2f4ad1ec57bf93c",
    "data/hand/events_early_2020_2021.csv": "42323ed8ffa3e823847866a72557f805635f4ca856bbc239fd6bfb561ad9b820",
}

STEPS = [
    ["src/build_derived.py"],                      # data/derived from data/raw and data/hand
    ["src/run_main.py"],                           # CAR panels, Table 5
    ["src/run_placebo_dates.py"],                  # Table 5 placebo p, Figure 3B
    ["src/run_diagnostics.py"],                    # event-level CARs (Figure 3A), leave-one-event-out
    ["src/run_continuous.py", "w00", "w01"],       # Table 6 coefficients
    ["src/run_robust_cont.py"],                    # Section 9.6 robustness
    ["src/run_round3.py"],                         # country-residualised exposure
    ["src/run_referee.py"],                        # Table 7: no look-ahead, design vs implementation, non-euro placebo
    ["src/run_timing.py"],                         # Table 7: timing checks
    ["src/run_currency.py"],                       # euro benchmarks, release-time-aligned CAR panels
    ["src/run_currency_inf.py"],                   # two-day binary check under the corrected window rule
    ["src/run_round10b.py"],                       # euro excess-return market model, provider recoding
    ["src/run_ts_final.py"],                       # release-time-aligned inference, 9,999 draws
    ["src/run_robust_table.py"],                   # Table 10
    ["src/run_alt_dates.py"],                      # Table 10: alternative event dates
    ["src/run_f1.py"],                             # Table 10: F1
    ["src/run_romanowolf.py"],                     # Romano-Wolf adjustment
    ["src/power.py"],                              # Table 4
    ["src/run_round4.py"],                         # power of the design-only test
    ["src/run_early.py"],                          # 2020-21 events
    ["src/run_early_2019.py"],                     # 2020-21 events with December 2019 exposure
    ["src/run_round10.py"],                        # positive control with pre-event betas
    ["src/run_inference_final.py"],                # all permutation and wild-bootstrap p-values, 9,999 draws
    ["src/run_redate_draft.py"],                   # draft report dated by first press report; documented release times
    ["src/make_fig_timeline.py", "output/fig_timeline_regenerated.png"],   # Figure 1 (see REPLICATION.md)
    ["src/make_figures.py"],                       # Figures 2-4
]


def verify_hashes() -> None:
    print("Verifying frozen inputs ...")
    for rel, want in FROZEN.items():
        got = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        print(f"  {'OK' if got == want else 'FAIL':4s} {rel}")
        if got != want:
            raise SystemExit(f"Hash mismatch for {rel}: {got} != {want}")


def main() -> int:
    verify_hashes()
    (ROOT / "output").mkdir(exist_ok=True)
    env = dict(os.environ, PYTHONPATH=str(ROOT))
    t0 = time.time()
    for step in STEPS:
        t = time.time()
        print(f"\n=== {' '.join(step)}", flush=True)
        r = subprocess.run([sys.executable, "-W", "ignore", *step], cwd=ROOT, env=env)
        if r.returncode != 0:
            raise SystemExit(f"failed: {' '.join(step)}")
        print(f"--- {time.time() - t:.0f} s", flush=True)
    print("\n=== unit tests", flush=True)
    subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, check=True)
    print(f"\nall steps done in {(time.time() - t0) / 60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
