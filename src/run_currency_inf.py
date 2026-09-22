import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd, json
from src.eventstudy import second_stage
ex = pd.read_csv("data/derived/bank_exposure_2023q1.csv"); eb = ex[ex.group=="bank"]
Z = dict(zip(ex.ticker, (ex.dep_share-eb.dep_share.mean())/eb.dep_share.std()))
def lv(q):
    for nm,g in [("d_bank","bank"),("d_pay","payments"),("d_gate","gate")]: q[nm] = np.where(q.grp==g, q.direction, 0.0)
    return q
out = {}
# binary group spec, two-day window, pre-specified first stage (fixed window rule)
q = lv(pd.read_csv("output/car_ff3usd_w01.csv", parse_dates=["event_date"]))
q["dir_bank"], q["dir_payments"], q["dir_gate"] = q.d_bank, q.d_pay, q.d_gate
r = second_stage(q, ["dir_bank","dir_payments","dir_gate"])
out["binary_w01"] = dict(names=r["names"], beta=[float(b*100) for b in r["beta"]], t=[float(t) for t in r["t"]], n=int(r["n"]))
print("binary two-day:", [round(b*100,3) for b in r["beta"]], [round(t,2) for t in r["t"]], "n", r["n"])
for ver in ["ff3usd","local3"]:
    q = lv(pd.read_csv(f"output/car_{ver}_ts.csv", parse_dates=["event_date"]))
    def fit(qq, zz=None):
        qq = qq.copy(); z = qq.z if zz is None else zz
        qq["x_bank"] = np.where(qq.grp=="bank", z*qq.direction, 0.0)
        return second_stage(qq, ["x_bank","d_bank","d_pay","d_gate"])
    r = fit(q); b0 = r["beta"][0]
    banks = sorted(q[q.grp=="bank"].firm.unique()); zb = np.array([Z[b] for b in banks]); rng = np.random.default_rng(41); null=[]
    for _ in range(499):
        mp = dict(zip(banks, rng.permutation(zb))); null.append(fit(q, q.firm.map(mp))["beta"][0])
    pp = (1+(np.abs(np.array(null))>=abs(b0)).sum())/500
    d = q.copy(); d["x_bank"] = np.where(d.grp=="bank", d.z*d.direction, 0.0); d = d.dropna(subset=["car"]).reset_index(drop=True)
    firms = sorted(d.firm.unique()); fi = d.firm.map({f:i for i,f in enumerate(firms)}).to_numpy()
    evs = sorted(d.event_date.unique()); ei = d.event_date.map({e:i for i,e in enumerate(evs)}).to_numpy()
    def X(cols):
        n=len(d); M=np.zeros((n,len(firms)+len(evs)-1)); M[np.arange(n),fi]=1; m=ei>0; M[np.arange(n)[m],len(firms)+ei[m]-1]=1
        return np.hstack([d[cols].to_numpy(float), M])
    Xf, Xr, y = X(["x_bank","d_bank","d_pay","d_gate"]), X(["d_bank","d_pay","d_gate"]), d.car.to_numpy(float)
    cr,*_ = np.linalg.lstsq(Xr,y,rcond=None); f0 = Xr@cr; u0 = y-f0; cf,*_ = np.linalg.lstsq(Xf,y,rcond=None); bs=[]
    for _ in range(999):
        w = rng.choice([-1.0,1.0], size=len(firms))[fi]; cb,*_ = np.linalg.lstsq(Xf, f0+w*u0, rcond=None); bs.append(cb[0])
    pw = (1+(np.abs(np.array(bs))>=abs(cf[0])).sum())/1000
    se = r["se_jackknife"][0]
    out[f"ts_{ver}"] = dict(theta=float(b0*100), se=float(se*100), ci=[float((b0-1.96*se)*100), float((b0+1.96*se)*100)], p_perm=float(pp), p_wild=float(pw))
    print(f"TS {ver}: theta {b0*100:.3f}, se {se*100:.3f}, CI [{(b0-1.96*se)*100:.2f}, {(b0+1.96*se)*100:.2f}], p_perm {pp:.3f}, p_wild {pw:.3f}")
json.dump(out, open("output/currency_inference.json","w"), indent=1)
