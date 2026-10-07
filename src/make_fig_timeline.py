"""Figure 1: the digital euro file, coded design content and contestation.

Panel A: coded design direction of each estimation-sample event with a non-zero direction
for at least one group, in chronological order. Panel B: meetings disclosed on procedure
file 2023/0212(COD) in the 30 calendar days before each event.
Run from the repository root:  python src/make_fig_timeline.py [output.png]
"""
import sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

OUT = sys.argv[1] if len(sys.argv) > 1 else "paper/figures/fig_timeline.png"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.linewidth": 0.8})

NAMES = {"E01": "Commission proposal", "E03": "ECB opinion", "E26": "Rapporteur paper",
         "E23": "European Council", "E11": "ECB next phase", "E12": "Draft report",
         "E22": "Council position", "E20": "ECB pilot call", "E14": "Committee vote",
         "E17": "Plenary mandate", "E24": "Pilot selection"}
ROWS = [("dir_banks", "Banks", "#1c2733"), ("dir_psp", "Payment providers", "#2e5f9e"),
        ("dir_bigtech", "Device gatekeepers", "#a33a2a")]
GRID, BAR = "#e9ecef", "#b0b7c1"

ev = pd.read_csv("data/hand/event_coding_v1.csv", parse_dates=["date"])
ev = ev[ev.event_id.isin(NAMES)].sort_values("date").reset_index(drop=True)
lob = pd.read_csv("data/hand/lobby_meetings_v1.csv", parse_dates=["date"])
pre = [int(((lob.date < d) & (lob.date >= d - pd.Timedelta(days=30))).sum()) for d in ev.date]
x = np.arange(len(ev))

fig, (a, b) = plt.subplots(2, 1, figsize=(6.5, 4.6), gridspec_kw=dict(height_ratios=[1.0, 0.82], hspace=0.30))
fig.subplots_adjust(left=0.20, right=0.98, top=0.93, bottom=0.25)

# Panel A
for k, (col, lab, c) in enumerate(ROWS):
    y = len(ROWS) - 1 - k
    a.axhline(y, color=GRID, lw=1.0, zorder=1)
    for i, r in ev.iterrows():
        v = r[col]
        if pd.notna(v) and v != 0:
            a.scatter(x[i], y, marker="^" if v > 0 else "v", s=34, color=c, zorder=3)
for xi in x:
    a.axvline(xi, color=GRID, lw=0.8, zorder=0)
a.set_xlim(-0.6, len(ev) - 0.4); a.set_ylim(-0.6, len(ROWS) - 0.4)
a.set_yticks(range(len(ROWS))); a.set_yticklabels([r[1] for r in ROWS][::-1], fontsize=7)
a.set_xticks([]); a.tick_params(axis="y", length=0)
for s in a.spines.values():
    s.set_visible(False)
a.set_title("A. Coded design direction by group", loc="left", fontsize=8.5)
a.legend(handles=[Line2D([], [], marker="^", ls="", ms=7, color="#55595e", label="favourable (+1)"),
                  Line2D([], [], marker="v", ls="", ms=7, color="#55595e", label="unfavourable (−1)")],
         loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=2, frameon=False, fontsize=6.8,
         handletextpad=0.6, columnspacing=2.0, borderaxespad=0.1)

# Panel B
b.bar(x, pre, width=0.55, color=BAR, zorder=2)
for xi, v in zip(x, pre):
    b.text(xi, v + 0.4, str(v), ha="center", va="bottom", fontsize=6.2, color="#444")
b.set_xlim(-0.6, len(ev) - 0.4); b.set_ylim(0, 26)
b.set_xticks(x)
b.set_xticklabels([f"{NAMES[e]}\n{d:%d %b %Y}" for e, d in zip(ev.event_id, ev.date)],
                  rotation=45, ha="right", rotation_mode="anchor", fontsize=6.2, linespacing=1.0)
b.tick_params(axis="y", labelsize=7)
b.set_ylabel("Meetings in the\n30 days before", fontsize=7, linespacing=1.0)
for s in ("top", "right"):
    b.spines[s].set_visible(False)
b.set_title("B. Disclosed meetings with interest representatives before each event", loc="left", fontsize=8.5)

fig.savefig(OUT, dpi=300, facecolor="white")
print("saved", OUT, "| 30-day counts:", pre)
