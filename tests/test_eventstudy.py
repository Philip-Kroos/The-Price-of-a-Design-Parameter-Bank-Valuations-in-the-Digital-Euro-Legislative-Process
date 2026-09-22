import sys, pathlib
import numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.eventstudy import abnormal_returns, cars, second_stage, permutation_p

def make(beta_true=0.0, seed=0, n_firms=30, n_days=800, n_events=8):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2023-01-02", periods=n_days)
    mkt = rng.normal(0, 0.01, n_days)
    factors = pd.DataFrame({"mkt": mkt, "smb": rng.normal(0, .004, n_days), "hml": rng.normal(0, .004, n_days)}, index=dates)
    firms = [f"F{i:02d}" for i in range(n_firms)]
    expo = pd.Series(rng.uniform(0.2, 0.8, n_firms), index=firms)
    ev_idx = np.linspace(300, n_days - 20, n_events).astype(int)
    ev_dates = dates[ev_idx]
    direction = rng.choice([-1, 1], n_events)
    R = pd.DataFrame(index=dates, columns=firms, dtype=float)
    for j, f in enumerate(firms):
        beta = 0.8 + 0.4 * rng.random()
        R[f] = beta * mkt + rng.normal(0, 0.012, n_days)
    for e, (d, s) in enumerate(zip(ev_dates, direction)):
        R.loc[d] += beta_true * s * expo.values
    return R, factors, ev_dates, expo, dict(zip(ev_dates, direction))

def build_panel(R, factors, ev_dates, expo, dirmap):
    ar = abnormal_returns(R, factors, ev_dates)
    p = cars(ar, ev_dates)
    p["exposure"] = p.firm.map(expo)
    p["direction"] = p.event_date.map(dirmap)
    p["expo_x_dir"] = p.exposure * p.direction
    p["group"] = "bank"
    return p

def test_recovers_planted_effect():
    R, F, E, X, D = make(beta_true=0.05, seed=1)
    p = build_panel(R, F, E, X, D)
    res = second_stage(p, ["expo_x_dir"])
    assert abs(res["beta"][0] - 0.05) < 0.02 and res["t"][0] > 3

def test_no_effect_is_not_rejected():
    R, F, E, X, D = make(beta_true=0.0, seed=2)
    p = build_panel(R, F, E, X, D)
    res = permutation_p(p, ["expo_x_dir"], "exposure", n_perm=199, seed=3)
    assert res["p_perm"] > 0.05

def test_cars_window_shapes():
    R, F, E, X, D = make(seed=4)
    ar = abnormal_returns(R, F, E)
    assert len(cars(ar, E, window=(0,1))) == len(cars(ar, E, window=(0,0)))
