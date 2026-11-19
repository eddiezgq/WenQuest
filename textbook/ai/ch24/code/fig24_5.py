"""图 24.5.1：抓取位姿的几何打分。

（a）工件轮廓、质心，以及几个候选抓取位姿：三条判据打分最高的几个（蓝），
    与“只看开口不看质心”挑出来的那个（红）；每个位姿标出打分与实际成功率；
（b）几何打分与实际成功率的关系——**有用，但不是一条直线**：打分只是近似。
"""
import math

import numpy as np

from _ch24 import (GRIPPER, cross2, grasp_line, grasp_score, grasp_truth, poly_centroid,
                   polygon)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_CAND, TOP = 400, 3

P = polygon("L")
c = poly_centroid(P)
g = np.random.default_rng(0)
cands = []
while len(cands) < N_CAND:
    ctr = np.array([g.uniform(P[:, 0].min(), P[:, 0].max()),
                    g.uniform(P[:, 1].min(), P[:, 1].max())])
    ang = g.uniform(0.0, math.pi)
    gl = grasp_line(P, ctr, ang)
    if gl is None:
        continue
    i = len(cands)
    cands.append({"gl": gl, "score": grasp_score(P, gl), "truth": grasp_truth(P, gl, seed=i)})

score = np.array([x["score"] for x in cands])
truth = np.array([x["truth"] for x in cands]) * 100
width = np.array([x["gl"]["width"] for x in cands])
fits = width <= GRIPPER["open_max_m"]
order = np.argsort(-score)
naive = np.where(fits, 1.0 - width / GRIPPER["open_max_m"], -1.0)
order_n = np.argsort(-naive)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.6))

# ---------------- (a) 工件与候选位姿
poly = np.vstack([P, P[:1]]) * 1000
a.plot(poly[:, 0], poly[:, 1], color=C["ink"], lw=2.0)
a.fill(poly[:, 0], poly[:, 1], color=C["ink"], alpha=0.07)
a.plot(c[0] * 1000, c[1] * 1000, "x", color=C["x"], ms=11, mew=2.4)
a.annotate(T("质心", "centre of mass"), xy=(c[0] * 1000, c[1] * 1000), xytext=(8, -14),
           textcoords="offset points", fontsize=9, color=C["x"])

marks = "①②③④⑤"
rows = []
for rank, i in enumerate(order[:TOP], 1):
    gl = cands[i]["gl"]
    p0, p1 = gl["p0"] * 1000, gl["p1"] * 1000
    a.plot([p0[0], p1[0]], [p0[1], p1[1]], "-o", color=C["z"], lw=2.0, ms=5)
    mid = (p0 + p1) / 2
    a.annotate(marks[rank - 1], xy=(mid[0], mid[1]), xytext=(0, 10 + 9 * (rank - 1)),
               textcoords="offset points", ha="center", fontsize=11, color=C["z"])
    rows.append(T(f"{marks[rank - 1]} 打分 {score[i]:.2f}　实际成功率 {truth[i]:.0f}%",
                  f"{marks[rank - 1]} score {score[i]:.2f}, actual {truth[i]:.0f}%"))

i_n = int(order_n[0])
gl = cands[i_n]["gl"]
p0, p1 = gl["p0"] * 1000, gl["p1"] * 1000
a.plot([p0[0], p1[0]], [p0[1], p1[1]], "s", color=C["x"], lw=2.0, ms=5, ls="--")
off_n = abs(cross2(np.array([math.cos(gl["angle"]), math.sin(gl["angle"])]), c - gl["p0"])) * 1000
a.annotate("■", xy=((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2), xytext=(-12, 0),
           textcoords="offset points", ha="center", fontsize=10, color=C["x"])
a.text(0.97, 0.30, "\n".join(rows), transform=a.transAxes, ha="right", va="top",
       fontsize=8.6, color=C["z"])
a.text(0.97, 0.10, T(f"■ 只看开口挑的：开口最小，离质心 {off_n:.0f} mm，\n　 实际成功率 {truth[i_n]:.0f}%",
                     f"■ picked by opening alone: {off_n:.0f} mm off the\n   centre, actual {truth[i_n]:.0f}%"),
       transform=a.transAxes, ha="right", va="top", fontsize=8.6, color=C["x"])
a.set_aspect("equal")
a.set_xlim(-18, 112)
a.set_ylim(-42, 76)
a.set_xlabel(T("x（mm）", "x (mm)"))
a.set_ylabel(T("y（mm）", "y (mm)"))
a.set_title(T("(a) 夹得下不等于夹得住：连线要穿过质心",
              "(a) fitting the jaws is not holding: the line must pass the centre"), fontsize=10)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 打分对实际成功率
b.scatter(score[fits], truth[fits], s=18, color=C["z"], alpha=0.45,
          label=T("夹得下的位姿", "poses the jaws fit around"))
b.scatter(score[~fits], truth[~fits], s=18, color=C["muted"], alpha=0.45,
          label=T("开口不够（打分 0）", "opening too small (score 0)"))
b.scatter(score[order[:TOP]], truth[order[:TOP]], s=90, facecolors="none",
          edgecolors=C["z"], lw=2.0, label=T(f"打分前 {TOP} 名", f"top {TOP} by score"))
b.scatter([score[i_n]], [truth[i_n]], s=90, marker="s", facecolors="none",
          edgecolors=C["x"], lw=2.0, label=T("只看开口挑的", "picked by opening alone"))
corr = float(np.corrcoef(score, truth)[0, 1])
top5 = float(np.mean(truth[order[:5]]))
rnd = float(np.mean(truth))
b.axhline(rnd, color=C["muted"], lw=1.4, ls=":")
b.annotate(T(f"随便挑：平均 {rnd:.0f}%", f"random pick: {rnd:.0f}% on average"),
           xy=(0.82, rnd), xytext=(0, 7), textcoords="offset points", ha="center",
           fontsize=8.5, color=C["muted"])
b.set_xlabel(T("几何打分（质心偏距 × 开口 × 摩擦锥）",
                "geometric score (centre offset × opening × friction cone)"))
b.set_ylabel(T("实际成功率（%，每个位姿扰动 24 次）",
                "actual success rate (%, 24 perturbed trials each)"))
b.set_title(T(f"(b) 打分与实际成功率的相关系数 {corr:.2f}——有用，但不是 1",
              f"(b) score vs actual success: correlation {corr:.2f} — useful, not perfect"),
            fontsize=10)
b.annotate(T(f"打分前 5 名实际成功率 {top5:.0f}%，随便挑只有 {rnd:.0f}%：\n"
             f"三条中学几何判据，一行学习都没有",
             f"top-5 by score succeed {top5:.0f}% vs {rnd:.0f}% at random:\n"
             f"three schoolbook criteria, no learning at all"),
           xy=(0.03, 0.70), xycoords="axes fraction", ha="left", va="top",
           fontsize=8.5, color=C["accent"])
b.set_ylim(-6, 112)
b.legend(fontsize=8, loc="upper left", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig24_5_1")
