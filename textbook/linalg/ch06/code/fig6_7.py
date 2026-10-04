"""图 6.7.1：过 4 个时刻的关节角插值多项式（范德蒙德方程组）。左：t = 0, 1, 2, 3 s，曲线平稳；
右：第 3 个时刻挪到 1.01 s，范德蒙德矩阵几乎奇异：这一时刻的读数取 20.5° 或 22°（只差 1.5°），两条插值曲线天差地别。"""
import numpy as np

from _fig import BLUE, INK, RED, T, figure, plt

fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.9))
tt = np.linspace(0, 3, 400)
t = np.array([0, 1, 2, 3.0])
cc = np.linalg.solve(np.vander(t, increasing=True), np.array([0, 20, 60, 90.0]))
axs[0].plot(tt, np.polyval(cc[::-1], tt), color=BLUE, lw=2)
axs[0].plot(t, [0, 20, 60, 90], "o", color=INK, ms=6)
axs[0].set_title(T("节点 0, 1, 2, 3 s", "nodes 0, 1, 2, 3 s"), fontsize=11)
t2 = np.array([0, 1, 1.01, 3.0])
for v, c in ((20.5, BLUE), (22.0, RED)):
    th = np.array([0, 20, v, 90.0])
    cc = np.linalg.solve(np.vander(t2, increasing=True), th)
    axs[1].plot(tt, np.polyval(cc[::-1], tt), color=c, lw=2, label=T(f"1.01 s 时读数 {v:g}°", f"reading {v:g}° at 1.01 s"))
axs[1].plot([0, 1, 3], [0, 20, 90], "o", color=INK, ms=6)
axs[1].legend(frameon=False, fontsize=9)
axs[1].set_title(T("节点 0, 1, 1.01, 3 s", "nodes 0, 1, 1.01, 3 s"), fontsize=11)
for ax in axs:
    ax.set_xlabel("t / s")
    ax.set_ylabel(T("关节角 / °", "joint angle / °"))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig6_7_1")
