"""Post-referee analyses (21.09.2026), reported alongside the registered estimate, never replacing it.
A: drop events whose coding used ex-post information (E04, E06).
B: separate design-parameter events from implementation / issuance-probability events.
C: continuous placebo on non-euro banks (triple difference)."""
import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import second_stage
ex = pd.read_csv("data/derived/bank_exposure_2023q1.csv"); eu = ex[ex.group=="bank"]
mu, sd = eu.dep_share.mean(), eu.dep_share.std()
Z = dict(zip(ex.ticker, (ex.dep_share-mu)/sd))          # controls standardised on the euro-bank scale
p = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"])
p["grp"] = p.group.replace({"device":"gate","bigtech":"gate"}); p["z"] = p.firm.map(Z)
ev = pd.read_csv("data/hand/event_coding_v1.csv", dtype=str); ev["date"] = pd.to_datetime(ev.date)
IMPL = {"E01","E03","E11","E20","E23","E24"}          # advance the project without fixing a parameter
DESIGN = {"E12","E14","E17","E22","E26","E19"}         # fix or signal a parameter
date_type = {}
for r in ev.itertuples():
    t = "impl" if r.event_id in IMPL else ("design" if r.event_id in DESIGN else "other")
    date_type[r.date] = t if date_type.get(r.date) in (None, "other") else date_type[r.date]
p["etype"] = p.event_date.map(date_type)
bank_dir = p[p.grp=="bank"].groupby("event_date").direction.first()
def perm_p(q, cols, target, n=499, seed=5):
    base = second_stage(q, cols); b0 = base["beta"][cols.index(target)]
    banks = sorted(q[q.grp=="bank"].firm.unique()); zb = np.array([Z[b] for b in banks]); rng = np.random.default_rng(seed); null=[]
    for _ in range(n):
        mp = dict(zip(banks, rng.permutation(zb))); s = q.copy(); zz = s.firm.map(mp).fillna(s.z)
        for c in cols:
            if c.startswith("x_"):
                s[c] = np.where(s[c] != 0, zz * s["_dir_" + c], 0.0) if "_dir_" + c in s else s[c]
        null.append(second_stage(s, cols)["beta"][cols.index(target)])
    null = np.array(null); return base, float((1+(np.abs(null)>=abs(b0)).sum())/(1+len(null)))
def lvl(q):
    for nm,g in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]:
        q[nm] = np.where(q.grp==g, q.direction, 0.0)
    return q
out = {}
# A: drop E04/E06 dates
drop = set(ev[ev.event_id.isin(["E04","E06"])].date)
qa = lvl(p[~p.event_date.isin(drop)].copy()); qa["x_bank"] = np.where(qa.grp=="bank", qa.z*qa.direction, 0.0); qa["_dir_x_bank"]=np.where(qa.grp=="bank", qa.direction, 0.0)
ra, pa = perm_p(qa, ["x_bank","d_bank","d_pay","d_gate"], "x_bank")
out["A_no_lookahead"] = dict(theta=float(ra["beta"][0]), t=float(ra["t"][0]), p_perm=pa, events=int(qa.event_date.nunique()))
# B: design vs implementation
qb = lvl(p[~p.event_date.isin(drop)].copy())
for t in ["design","impl"]:
    m = (qb.grp=="bank") & (qb.etype==t)
    qb[f"x_{t}"] = np.where(m, qb.z*qb.direction, 0.0); qb[f"_dir_x_{t}"] = np.where(m, qb.direction, 0.0)
rb, pb = perm_p(qb, ["x_design","x_impl","d_bank","d_pay","d_gate"], "x_design")
out["B_design"] = dict(theta=float(rb["beta"][0]), t=float(rb["t"][0]), p_perm=pb,
                       n_design_bank_events=int(qb[(qb.grp=="bank")&(qb.etype=="design")&(qb.direction!=0)].event_date.nunique()))
out["B_impl"] = dict(theta=float(rb["beta"][1]), t=float(rb["t"][1]))
# C: triple difference with non-euro banks that have EBA exposure
qc = lvl(p[~p.event_date.isin(drop)].copy())
qc["bank_dir_all"] = qc.event_date.map(bank_dir).fillna(0.0)
qc["x_euro"] = np.where(qc.grp=="bank", qc.z*qc.direction, 0.0)
has = qc.grp.eq("control_bank") & qc.z.notna()
qc["x_ctrl"] = np.where(has, qc.z*qc.bank_dir_all, 0.0)
qc = qc[~(qc.grp.eq("control_bank") & qc.z.isna())]      # controls without exposure data drop out of this test
rc = second_stage(qc, ["x_euro","x_ctrl","d_bank","d_pay","d_gate"])
diff = rc["beta"][0]-rc["beta"][1]
out["C_triple"] = dict(theta_euro=float(rc["beta"][0]), theta_ctrl=float(rc["beta"][1]), t_ctrl=float(rc["t"][1]),
                       euro_minus_ctrl=float(diff), n_ctrl=int(qc[qc.grp=="control_bank"].firm.nunique()))
json.dump(out, open("output/referee_analyses.json","w"), indent=1)
for k,v in out.items(): print(k, {a:(round(b*100,3) if isinstance(b,float) and abs(b)<1 and a not in("p_perm",) and not a.startswith("t") else (round(b,3) if isinstance(b,float) else b)) for a,b in v.items()})
