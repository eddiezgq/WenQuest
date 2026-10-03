"""51.3 节：六点定位（图 51.3.1）——长方体工件底面 3 点、侧面 2 点、端面 1 点；并用自由度分析程序数出各定位面限制的自由度。"""
import numpy as np

import _mfg as M
from bookout import T, figure, out, style

TL = M.tol()
plt = style()
fig, ax = plt.subplots(figsize=(6.2, 3.8))


def P(x, y, z):                     # 斜二测投影
    return np.array([x + 0.45 * y, z + 0.32 * y])


a, b, c = 6.0, 3.6, 2.2
V = {k: P(*k) for k in [(x, y, z) for x in (0, a) for y in (0, b) for z in (0, c)]}
edges = [((0, 0, 0), (a, 0, 0)), ((0, 0, 0), (0, b, 0)), ((0, 0, 0), (0, 0, c)), ((a, 0, 0), (a, b, 0)), ((a, 0, 0), (a, 0, c)),
         ((0, b, 0), (a, b, 0)), ((0, b, 0), (0, b, c)), ((0, 0, c), (a, 0, c)), ((0, 0, c), (0, b, c)), ((a, b, 0), (a, b, c)),
         ((a, 0, c), (a, b, c)), ((0, b, c), (a, b, c))]
for e0, e1 in edges:
    ax.plot(*zip(V[e0], V[e1]), color=M.INK, lw=1.1, ls="--" if (e0 == (0, b, 0) and e1 in ((a, b, 0), (0, b, c))) or (e0, e1) == ((0, 0, 0), (0, b, 0)) else "-")
faces = {"bottom": [(0, 0, 0), (a, 0, 0), (a, b, 0), (0, b, 0)], "side": [(0, b, 0), (a, b, 0), (a, b, c), (0, b, c)],
         "end": [(0, 0, 0), (0, b, 0), (0, b, c), (0, 0, c)]}
fcol = {"bottom": "#3a7dc9", "side": "#d98c3a", "end": "#b5443b"}
for k, f in faces.items():
    ax.add_patch(plt.Polygon([P(*q) for q in f], closed=True, fc=fcol[k], alpha=0.10, ec="none"))
pts = {"bottom": [(1.0, 0.8, 0), (5.0, 0.8, 0), (3.0, 2.9, 0)], "side": [(1.2, b, 0.9), (4.8, b, 0.9)], "end": [(0, 1.8, 1.1)]}
cols = {"bottom": M.ACCENT, "side": M.WARM, "end": M.RED}
for k, ps in pts.items():
    for q in ps:
        x, y = P(*q)
        ax.plot(x, y, "o", ms=7, color=cols[k], zorder=5)
lab = {"bottom": T("底面 3 点：z、绕 x、绕 y", "bottom 3 points: z, about x, about y"),
       "side": T("侧面 2 点：y、绕 z", "side 2 points: y, about z"), "end": T("端面 1 点：x", "end 1 point: x")}
for i, k in enumerate(("bottom", "side", "end")):
    ax.plot([], [], "o", color=cols[k], label=lab[k])
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=3, fontsize=8.5, frameon=False)
o = P(-1.0, -0.3, 0)
for vec, name in (((1.2, 0, 0), "x"), ((0, 1.6, 0), "y"), ((0, 0, 1.2), "z")):
    e = P(-1.0 + vec[0], -0.3 + vec[1], vec[2])
    ax.annotate("", xy=(e[0], e[1]), xytext=(o[0], o[1]), arrowprops=dict(arrowstyle="-|>", color=M.MUTED, lw=1.0))
    ax.text(e[0] + 0.08, e[1] + 0.05, name, fontsize=9, color=M.MUTED)
ax.set_xlim(-1.6, a + 0.45 * b + 0.4); ax.set_ylim(-0.7, c + 0.32 * b + 0.3)
ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig51_3_1")
r = TL.dof_analysis([("底面", {"z", "rx", "ry"}), ("侧面", {"y", "rz"}), ("端面", {"x"})], set(TL.DOF))
out(verdict=r["verdict"], n=r["n"])
