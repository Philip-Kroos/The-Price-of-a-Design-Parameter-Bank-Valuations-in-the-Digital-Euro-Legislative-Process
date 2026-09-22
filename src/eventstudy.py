"""Two-stage event study for the digital euro design-parameter paper.

Stage 1: abnormal returns from a three-factor model estimated on a clean window that excludes
event days, then cumulative abnormal returns over a chosen window.
Stage 2: CAR(i,e) on exposure interacted with the coded design direction of the event, with firm
and event fixed effects. Inference: cluster-robust, permutation of exposure across firms within
group, and a null-imposed wild cluster bootstrap.
"""
from __future__ import annotations
import numpy as np, pandas as pd


def abnormal_returns(ret: pd.DataFrame, factors: pd.DataFrame, event_dates, est_window=250, gap=10):
    """ret: index date, columns firms. factors: index date, columns factor returns (incl. mkt).
    Returns a long frame date x firm of abnormal returns, estimating betas on days at least `gap`
    trading days away from any event, using the most recent `est_window` clean days."""
    ev = pd.to_datetime(pd.Series(sorted(set(event_dates))))
    idx = ret.index
    near = np.zeros(len(idx), bool)
    for d in ev:
        pos = idx.searchsorted(d)
        near[max(0, pos - gap): min(len(idx), pos + gap + 1)] = True
    clean = ~near
    X = factors.reindex(idx).to_numpy(float)
    out = pd.DataFrame(index=idx, columns=ret.columns, dtype=float)
    for c in ret.columns:
        y = ret[c].to_numpy(float)
        ok = clean & np.isfinite(y) & np.all(np.isfinite(X), axis=1)
        if ok.sum() < 60:
            continue
        sel = np.where(ok)[0][-est_window:]
        A = np.column_stack([np.ones(len(sel)), X[sel]])
        b, *_ = np.linalg.lstsq(A, y[sel], rcond=None)
        pred = b[0] + X @ b[1:]
        out[c] = y - pred
    return out


def cars(ar: pd.DataFrame, event_dates, window=(0, 0)) -> pd.DataFrame:
    """Cumulative abnormal returns per firm and event over the trading-day window."""
    idx = ar.index
    rows = []
    for d in pd.to_datetime(pd.Series(sorted(set(event_dates)))):
        pos = idx.searchsorted(d)
        if pos >= len(idx):
            continue
        lo, hi = pos + window[0], pos + window[1]
        if lo < 0 or hi >= len(idx):
            continue
        s = ar.iloc[lo:hi + 1].sum(min_count=hi - lo + 1)   # require a return on every day of the window
        for firm, v in s.items():
            if np.isfinite(v):
                rows.append(dict(event_date=d, firm=firm, car=float(v)))
    return pd.DataFrame(rows)


def _fe_design(fi, ei, n_f, n_e, X=None):
    n = len(fi)
    Z = np.zeros((n, n_f + n_e - 1))
    Z[np.arange(n), fi] = 1
    m = ei > 0
    Z[np.arange(n)[m], n_f + ei[m] - 1] = 1
    return Z if X is None else np.hstack([Z, X])


def second_stage(panel: pd.DataFrame, regressors, cluster="firm"):
    """panel needs: car, firm, event_date and the columns in `regressors`.
    Returns coefficients with cluster-robust and leave-one-cluster-out jackknife standard errors."""
    d = panel.dropna(subset=["car"] + list(regressors)).reset_index(drop=True)
    firms = sorted(d.firm.unique()); evs = sorted(d.event_date.unique())
    fi = d.firm.map({f: i for i, f in enumerate(firms)}).to_numpy()
    ei = d.event_date.map({e: i for i, e in enumerate(evs)}).to_numpy()
    X = d[list(regressors)].to_numpy(float)
    A = np.hstack([X, _fe_design(fi, ei, len(firms), len(evs))])
    y = d.car.to_numpy(float)
    k = X.shape[1]
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    b = coef[:k]
    resid = y - A @ coef
    g = d[cluster].to_numpy()
    XtX_inv = np.linalg.pinv(A.T @ A)
    meat = np.zeros_like(XtX_inv)
    for gg in np.unique(g):
        m = g == gg
        s = A[m].T @ resid[m]
        meat += np.outer(s, s)
    V = XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(V))[:k]
    jk = []
    for gg in np.unique(g):
        m = g != gg
        c2, *_ = np.linalg.lstsq(A[m], y[m], rcond=None)
        jk.append(c2[:k])
    jk = np.array(jk); G = len(jk)
    se_jk = np.sqrt((G - 1) / G * ((jk - jk.mean(0)) ** 2).sum(0))
    return dict(names=list(regressors), beta=b, se_cluster=se, se_jackknife=se_jk,
                t=b / np.where(se_jk > 0, se_jk, np.nan), n=len(d), firms=len(firms), events=len(evs))



def second_stage_beta(panel: pd.DataFrame, regressors):
    """Fast OLS coefficients for the fixed-effects second stage.

    This is algebraically the same point estimator as ``second_stage`` but omits
    cluster/jackknife inference. It is used inside permutation loops where only
    the coefficient is needed.
    """
    d = panel.dropna(subset=["car"] + list(regressors)).reset_index(drop=True)
    firms = sorted(d.firm.unique()); evs = sorted(d.event_date.unique())
    fi = d.firm.map({f: i for i, f in enumerate(firms)}).to_numpy()
    ei = d.event_date.map({e: i for i, e in enumerate(evs)}).to_numpy()
    X = d[list(regressors)].to_numpy(float)
    A = np.hstack([X, _fe_design(fi, ei, len(firms), len(evs))])
    y = d.car.to_numpy(float)
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef[: X.shape[1]]

def permutation_p(panel: pd.DataFrame, regressors, exposure_col, group_col="group", n_perm=999, seed=0):
    """Permute the exposure values across firms within group, holding the event coding fixed."""
    rng = np.random.default_rng(seed)
    base = second_stage(panel, regressors)
    t0 = base["t"][0]
    expo = panel.groupby("firm")[[exposure_col, group_col]].first()
    null = []
    for _ in range(n_perm):
        mapping = {}
        for grp, sub in expo.groupby(group_col):
            vals = rng.permutation(sub[exposure_col].to_numpy())
            mapping.update(dict(zip(sub.index, vals)))
        p = panel.copy()
        p[exposure_col] = p.firm.map(mapping)
        for r in regressors:
            if r.endswith("_x_dir"):
                p[r] = p[exposure_col] * p["direction"]
        try:
            null.append(second_stage(p, regressors)["t"][0])
        except Exception:
            null.append(np.nan)
    null = np.array(null, float); null = null[np.isfinite(null)]
    return dict(t=float(t0), p_perm=float((1 + (np.abs(null) >= abs(t0)).sum()) / (1 + len(null))),
                draws=int(len(null)))
