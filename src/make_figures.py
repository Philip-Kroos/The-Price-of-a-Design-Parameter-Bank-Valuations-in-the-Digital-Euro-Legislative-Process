"""Figures 2 to 4 of the paper.

Figure 2  paper/figures/fig_lobby.png             negotiation record: meetings by quarter and category; meetings before each event
Figure 3  paper/figures/fig_results_bank.png      event-day gap euro minus non-euro banks; placebo-date distribution
Figure 4  paper/figures/fig_event_slopes_all.png  event-level exposure slopes, 2020 to 2026
Run from the repository root after src/run_main.py, src/run_placebo_dates.py and src/run_early.py:
    python src/make_figures.py [output_dir]
"""
import sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

OUT = sys.argv[1] if len(sys.argv) > 1 else "paper/figures"
import matplotlib.dates as mdates
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.titlesize": 9.5,
                     "axes.labelsize": 8, "legend.fontsize": 7, "axes.linewidth": 0.8,
                     "axes.spines.top": False, "axes.spines.right": False})
NAVY, RED, GREY = "#1c2430", "#9b3328", "#9aa3ad"

ev = pd.read_csv("data/hand/event_coding_v1.csv", parse_dates=["date"])
est = ev[ev.status.str.startswith("coded") & (ev.date <= "2026-07-31") & (ev.event_id != "E13")]

# ---------------------------------------------------------------- Figure 2
L = pd.read_csv("data/derived/lobby_categorised.csv", parse_dates=["date"])
CATS = [("bank", "Banks", "#1c2430"), ("bank_assoc", "Banking associations", "#5b6670"),
        ("payments", "Payment providers", "#2e5f9e"), ("bigtech", "Large technology", "#7fb0dd"),
        ("retail", "Retail", "#9b3328"), ("civil_society", "Civil society", "#c98a2e"),
        ("other", "Public bodies, other", "#d5d9de")]
L["q"] = L.date.dt.to_period("Q")
tab = L.pivot_table(index="q", columns="category", values="mep", aggfunc="count", fill_value=0).sort_index()
fig, (a, b) = plt.subplots(1, 2, figsize=(6.5, 3.3), gridspec_kw=dict(width_ratios=[1.1, 1.0], wspace=0.30))
fig.subplots_adjust(left=0.09, right=0.99, top=0.91, bottom=0.21)
x = np.arange(len(tab)); bottom = np.zeros(len(tab))
for key, lab, col in CATS:
    v = tab[key].to_numpy() if key in tab else np.zeros(len(tab))
    a.bar(x, v, bottom=bottom, color=col, width=0.78, label=lab); bottom += v
a.set_xticks(x); a.set_xticklabels([f"{p.year} Q{p.quarter}" for p in tab.index], rotation=50, ha="right", rotation_mode="anchor")
a.set_ylabel("Disclosed meetings"); a.set_title("A. Who met the negotiators", loc="left")
a.legend(frameon=False, loc="upper left", handlelength=1.4, fontsize=6.6, labelspacing=0.35)
a.set_ylim(0, 63)

cnt = lambda d: int(((L.date < d) & (L.date >= d - pd.Timedelta(days=30))).sum())
e2 = est.copy(); e2["m30"] = e2.date.map(cnt)
des, pro = e2[e2.procedural == 0], e2[e2.procedural == 1]
b.scatter(des.date, des.m30, s=22, color=NAVY, zorder=3, label="design content")
b.scatter(pro.date, pro.m30, s=36, color=RED, marker="x", linewidths=1.6, zorder=4, label="procedural")
NOTE = {"E19": ("Eurogroup", (-52, -1)), "E23": ("European\nCouncil", (8, 3)),
        "E20": ("Pilot call", (6, 5)), "E07": ("Resumption", (-70, 12))}
for eid, (txt, off) in NOTE.items():
    r = e2[e2.event_id == eid].iloc[0]
    b.annotate(txt, (r.date, r.m30), xytext=off, textcoords="offset points", fontsize=6.8, color="#333",
               arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7, shrinkA=0, shrinkB=3))
b.set_ylim(-1, 26); b.set_ylabel("Meetings in the 30 days before")
b.set_title("B. Contestation before each event", loc="left")
b.legend(frameon=False, loc="upper left", fontsize=6.6, handletextpad=0.3, borderaxespad=0.2)
b.xaxis.set_major_locator(mdates.YearLocator()); b.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
b.set_xlim(pd.Timestamp("2023-05-01"), pd.Timestamp("2026-12-31"))
fig.savefig(f"{OUT}/fig_lobby.png", dpi=300, facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- Figure 3
g = pd.read_csv("output/event_level_cars.csv", parse_dates=["event_date"])
g = g[g.dir_bank != 0]
gap = g.bank - g.control_bank
pl = pd.read_csv("output/placebo_dates_bank.csv").iloc[:, 0].to_numpy() * 100
p = pd.read_csv("output/car_panel_w00.csv")
from src.eventstudy import second_stage  # noqa: E402
actual = second_stage(p.assign(dir_bank=np.where(p.group == "bank", p.direction, 0.0)), ["dir_bank"])["beta"][0] * 100
fig, (a, b) = plt.subplots(1, 2, figsize=(6.5, 2.8), gridspec_kw=dict(wspace=0.30))
fig.subplots_adjust(left=0.11, right=0.99, top=0.90, bottom=0.22)
xx = np.arange(len(g))
a.bar(xx, gap, color=[NAVY if d > 0 else RED for d in g.dir_bank], width=0.8)
a.axhline(0, color=GREY, lw=0.8)
a.set_xticks(xx); a.set_xticklabels(g.event_date.dt.strftime("%b %y"), rotation=50, ha="right", rotation_mode="anchor")
a.set_ylabel("Euro minus non-euro banks, pp"); a.set_title("A. Event-day gap", loc="left")
a.legend(handles=[Patch(color=NAVY, label="coded +1"), Patch(color=RED, label="coded −1")],
         frameon=False, loc="lower left")
b.hist(pl, bins=30, color="#ccd2d9", edgecolor="white", linewidth=0.6)
b.axvline(actual, color=NAVY, lw=1.6, label=f"actual: {actual:.2f} pp")
b.set_xlabel("Bank coefficient, pp"); b.set_title(f"B. Against {len(pl)} placebo dates", loc="left")
b.legend(frameon=False, loc="upper right"); b.set_xticks([-0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75])
fig.savefig(f"{OUT}/fig_results_bank.png", dpi=300, facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- Figure 4
def slopes(panel, zmap, design_ids, date_to_id):
    q = panel[(panel.grp == "bank") & (panel.direction != 0)].copy(); q["z"] = q.firm.map(zmap)
    rows = []
    for d, s in q.dropna(subset=["z"]).groupby("event_date"):
        X = np.column_stack([np.ones(len(s)), s.z]); c, *_ = np.linalg.lstsq(X, s.car, rcond=None)
        e = s.car - X @ c; se = np.sqrt((e ** 2).sum() / (len(s) - 2) / ((s.z - s.z.mean()) ** 2).sum())
        sign = s.direction.iloc[0]
        rows.append(dict(date=pd.Timestamp(d), b=c[1] * sign * 100, se=se * 100,
                         design=date_to_id.get(pd.Timestamp(d)) in design_ids))
    return pd.DataFrame(rows)

def zmap(path, col):
    x = pd.read_csv(path); eb = x[x.group == "bank"]
    return dict(zip(x.ticker, (x[col] - eb[col].mean()) / eb[col].std()))

early_ev = pd.read_csv("data/hand/events_early_2020_2021.csv", parse_dates=["date"])
pe = pd.read_csv("output/car_panel_early.csv", parse_dates=["event_date"])
s1 = slopes(pe, zmap("data/derived/bank_exposure_2019q4.csv", "dep_share_2019"),
            set(early_ev.loc[early_ev.type == "design", "event_id"]), dict(zip(early_ev.date, early_ev.event_id)))
p0 = pd.read_csv("output/car_panel_w00.csv", parse_dates=["event_date"]); p0["grp"] = p0.group
s2 = slopes(p0, zmap("data/derived/bank_exposure_2023q1.csv", "dep_share"),
            {"E12", "E14", "E17", "E22", "E26", "E19"}, dict(zip(est.date, est.event_id)))
S = pd.concat([s1, s2], ignore_index=True)
fig, ax = plt.subplots(figsize=(6.5, 2.9))
fig.subplots_adjust(left=0.10, right=0.99, top=0.95, bottom=0.22)
xx = np.arange(len(S))
for des, mk, col, lab in [(False, "o", NAVY, "implementation event"), (True, "s", RED, "design event")]:
    m = S.design == des
    ax.errorbar(xx[m], S.b[m], yerr=1.96 * S.se[m], fmt=mk, color=col, ecolor=GREY, elinewidth=1.0,
                capsize=2.5, ms=5, label=lab, zorder=3)
ax.axhline(0, color=GREY, lw=0.8)
ax.axvline(len(s1) - 0.5, color=GREY, lw=0.8, ls=":")
ax.text((len(s1) - 1) / 2, 2.0, "2020–21", ha="center", fontsize=7.5, color="#555")
ax.text(len(s1) + (len(s2) - 1) / 2, 2.0, "2023–26, legislative phase", ha="center", fontsize=7.5, color="#555")
ax.set_ylim(-2.2, 2.3); ax.set_yticks(np.arange(-2, 2.01, 0.5))
ax.set_xticks(xx); ax.set_xticklabels(S.date.dt.strftime("%b %y"), rotation=50, ha="right", rotation_mode="anchor")
ax.set_ylabel("Signed slope, pp per SD")
ax.legend(frameon=False, loc="lower right")
fig.savefig(f"{OUT}/fig_event_slopes_all.png", dpi=300, facecolor="white")
plt.close(fig)
print("figures written to", OUT)
print(S.round(2).to_string())
