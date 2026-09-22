#!/usr/bin/env python3
"""Run the core replication pipeline from the repository root.

The final post-review euro excess-return checks are run automatically only when
`data/raw/ecb_dfr_daily.csv` is available; their frozen outputs are bundled.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(*args: str) -> None:
    cmd = [sys.executable, *args]
    print("\n$", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def verify_hashes() -> None:
    expected = {
        "data/hand/event_coding_v1.csv": "06cc052fc56419c581a70ebed9d5d7df9153ff01a7b084386c374b3a6a6659ad",
        "data/hand/firm_universe_v0.csv": "7d407a36d225d1db523f5b18fdd75d2fc03c512baf4dce6e8f7db1ba2d39d15c",
        "docs/pap_v1.md": "cb9d788baf5526ad2118c8db7283fdc0ebe87dfdfc6f6134c2f4ad1ec57bf93c",
        "data/hand/events_early_2020_2021.csv": "42323ed8ffa3e823847866a72557f805635f4ca856bbc239fd6bfb561ad9b820",
    }
    print("Verifying frozen inputs...")
    for rel, want in expected.items():
        p = ROOT / rel
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        status = "OK" if got == want else "FAIL"
        print(f"  {status:4s} {rel}")
        if got != want:
            raise SystemExit(f"Hash mismatch for {rel}: {got} != {want}")


def main() -> int:
    verify_hashes()
    (ROOT / "output").mkdir(exist_ok=True)

    steps = [
        ["src/run_main.py"],
        ["src/run_continuous.py", "w00", "w01"],
        ["src/run_placebo_dates.py"],
        ["src/run_romanowolf.py"],
        ["src/run_timing.py"],
        ["src/run_ts_inference.py"],
        ["src/run_early.py"],
        ["src/run_early_2019.py"],
        ["src/run_referee.py"],
        ["src/run_robust_cont.py"],
        ["src/run_robust_table.py"],
        ["src/run_currency.py"],
        ["src/run_currency_inf.py"],
    ]
    for step in steps:
        run(*step)

    if (ROOT / "data/raw/ecb_dfr_daily.csv").exists():
        run("src/run_round10.py")
        run("src/run_round10b.py")
    else:
        print("\n[optional] Skipping src/run_round10.py and src/run_round10b.py")
        print("           because data/raw/ecb_dfr_daily.csv is not present.")
        print("           Frozen outputs are bundled; see REPLICATION.md.")

    run("-m", "pytest", "-q")
    print("\nCore replication completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
