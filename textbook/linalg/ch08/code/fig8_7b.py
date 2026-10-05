"""图 8.7.2：Franka Panda 在零空间中运动（自运动）：末端位置与姿态不变，肘部沿一条曲线移动。
画出五个位形的连杆折线（侧视与俯视）。"""
import numpy as np
import scipy.linalg as sla

from _arm import panda
from _fig import BLUE, INK, MUTED, RED, T, figure, plt

arm = panda()
q = np.array([0.0, -np.pi / 4, 0, -3 * np.pi / 4, 0, np.pi / 2, np.pi / 4])
# 从 ready 姿态沿零空间两侧各走 0.5 rad
def walk(q, sgn, steps):
    out = [q.copy()]
    for _ in range(steps):
        nn = sla.null_space(arm.jacobian(q))[:, 0]
        if nn[0] * sgn < 0:
            nn = -nn
        q = q + 0.0025 * nn
        out.append(q.copy())
    return out
path = walk(q, -1, 200)[::-1] + walk(q, 1, 200)[1:]
pick = [path[i] for i in np.linspace(0, len(path) - 1, 5).astype(int)]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.4))
cols = plt.cm.viridis(np.linspace(0.1, 0.9, len(pick)))
for qq, c in zip(pick, cols):
    axes, Tt = arm.frames(qq)
    pts = np.array([np.zeros(3)] + [o for _, o in axes] + [arm.tool(qq)])
    a1.plot(pts[:, 0], pts[:, 2], "-o", color=c, ms=3, lw=2)
    a2.plot(pts[:, 0], pts[:, 1], "-o", color=c, ms=3, lw=2)
    a1.plot(axes[3][1][0], axes[3][1][2], "s", color=RED, ms=7)
    a2.plot(axes[3][1][0], axes[3][1][1], "s", color=RED, ms=7)
tool = arm.tool(q)
for a, (i, j), name in ((a1, (0, 2), T("侧视（x–z）", "side view (x–z)")), (a2, (0, 1), T("俯视（x–y）", "top view (x–y)"))):
    a.plot(tool[i], tool[j], "*", color=BLUE, ms=14)
    a.set_aspect("equal")
    a.set_title(name, fontsize=11)
    a.set_xlabel(["x", "y", "z"][i] + " / m")
    a.set_ylabel(["x", "y", "z"][j] + " / m")
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig8_7_2")
