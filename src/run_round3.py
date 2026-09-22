import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import second_stage
ex = pd.read_csv("data/derived/bank_exposure_2023q1.csv"); eb = ex[ex.group=="bank"]
Z = dict(zip(ex.ticker, (ex.dep_share-eb.dep_share.mean())/eb.dep_share.std()))
fu = pd.read_csv("data/hand/firm_universe_v0.csv"); CTRY = dict(zip(fu.ticker_guess, fu.country))
p = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"])
p["grp"] = p.group.replace({"device":"gate","bigtech":"gate"}); p["z"] = p.firm.map(Z)
def build(q, zmap=None):
    q = q.copy(); z = q.firm.map(zmap) if zmap else q.z
    q["x_bank"] = np.where(q.grp=="bank", z*q.direction, 0.0)
    for nm,g in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]: q[nm] = np.where(q.grp==g, q.direction, 0.0)
    return q
R = ["x_bank","d_bank","d_pay","d_gate"]
base = second_stage(build(p), R); b0 = base["beta"][0]
banks = sorted(p[p.grp=="bank"].firm.unique()); rng = np.random.default_rng(21)
# 1. permutation blocked within country
blocks = {}
for b in banks: blocks.setdefault(CTRY[b], []).append(b)
null = []
for _ in range(499):
    mp = {}
    for c, members in blocks.items():
        vals = rng.permutation([Z[m] for m in members]); mp.update(dict(zip(members, vals)))
    null.append(second_stage(build(p, mp), R)["beta"][0])
null = np.array(null); p_block = (1+(np.abs(null)>=abs(b0)).sum())/(1+len(null))
# 2. exposure residualised on country: within-country variation only
eu = ex[ex.group=="bank"].copy(); eu["ctry"] = eu.ticker.map(CTRY)
eu["res"] = eu.dep_share - eu.groupby("ctry").dep_share.transform("mean")
Zr = dict(zip(eu.ticker, eu.res/eu.res.std()))
rr = second_stage(build(p, Zr), R)
# 3. Romano-Wolf step-down for the three group predictions, binary spec, placebo-date resampling
from src.eventstudy import abnormal_returns
out = dict(main=float(b0), p_block_country=float(p_block), n_blocks=len(blocks),
           within_country_theta=float(rr["beta"][0]), within_country_t=float(rr["t"][0]))
json.dump(out, open("output/round3.json","w"), indent=1)
print("main %.3f | blocked-by-country permutation p %.3f (%d countries)" % (b0*100, p_block, len(blocks)))
print("within-country exposure: theta %.3f pp per SD, t %.2f" % (rr["beta"][0]*100, rr["t"][0]))
