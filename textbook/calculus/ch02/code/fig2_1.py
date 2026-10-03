"""图 2.1.1：两节连杆的误差累积——肩关节、肘关节各转过小角 δ，腕心沿两段圆弧偏离。"""
import json
import math
from pathlib import Path

import numpy as np

from _fig import ACC, BLUE, INK, MUTED, RED, T, figure, plt

e = json.loads((Path(__file__).resolve().parents[2] / "models" / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))
js = {j["name"]: j for j in e["robot"]["joints"]}
l1, l2 = js["elbow_joint"]["origin"]["xyz"][2], js["wrist_1_joint"]["origin"]["xyz"][2]
t1, t2, d = math.radians(35), math.radians(-60), math.radians(9)       # 为看清楚，δ 画得很大


def pts(a, b):
    E = np.array([l1 * math.cos(a), l1 * math.sin(a)])
    W = E + l2 * np.array([math.cos(a + b), math.sin(a + b)])
    return E, W


fig, ax = plt.subplots(figsize=(7, 4.6))
E, P = pts(t1, t2)
E1, P1 = pts(t1 + d, t2)
_, P2 = pts(t1 + d, t2 + d)
for (Ee, Pp, c, ls, lw) in ((E, P, INK, "-", 3), (E1, P1, MUTED, "--", 1.5), (E1, P2, BLUE, "-", 2)):
    ax.plot([0, Ee[0], Pp[0]], [0, Ee[1], Pp[1]], color=c, ls=ls, lw=lw, marker="o", ms=5)
R = np.linalg.norm(P)
a0 = math.atan2(P[1], P[0])
th = np.linspace(a0, a0 + d, 50)
ax.plot(R * np.cos(th), R * np.sin(th), color=RED, lw=1.5)
b0 = math.atan2(P1[1] - E1[1], P1[0] - E1[0])
th = np.linspace(b0, b0 + d, 50)
ax.plot(E1[0] + l2 * np.cos(th), E1[1] + l2 * np.sin(th), color=ACC, lw=1.5)
ax.annotate("", xy=P2, xytext=P, arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.3))
ax.text(0.03, -0.03, T("肩", "shoulder"), ha="left", va="top")
ax.text(E[0] - 0.02, E[1] + 0.03, T("肘", "elbow"), ha="right")
ax.text(P[0] + 0.02, P[1] - 0.04, "$P$")
ax.text(P1[0] + 0.02, P1[1], "$P'$", color=MUTED)
ax.text(P2[0] - 0.06, P2[1] + 0.02, "$P''$", color=BLUE)
ax.text(0.30, 0.20, T("肩转 δ：弧长 ≤ (l₁+l₂)δ", "shoulder δ: arc ≤ (l₁+l₂)δ"), color=RED, fontsize=10, transform=ax.transAxes, ha="left")
ax.text(0.30, 0.12, T("肘转 δ：弧长 ≤ l₂δ", "elbow δ: arc ≤ l₂δ"), color=ACC, fontsize=10, transform=ax.transAxes, ha="left")
ax.text(0.30, 0.04, "$|PP''| \\leq |PP'| + |P'P''|$", fontsize=11, transform=ax.transAxes, ha="left")
ax.set_aspect("equal")
ax.axis("off")
ax.set_title(T("两个关节的误差在腕心处累加（δ 放大画出）", "Joint errors add up at the wrist (δ exaggerated)"), fontsize=11)
fig.tight_layout()
figure(fig, "fig2_1_1")
