"""5.1 节的示意图。

图 5.1.1：3×3 模板计算的分块。（a）一个线程块负责 T×T 个输出（图中 T = 8），要把 (T+2)×(T+2) 个输入读进共享内存，
外面一圈是晕圈；（b）每个输出平均要从显存读几个输入：不靠缓存的朴素版 9 个，分块后 (T+2)²/T² 个，T 越大越接近 1。
"""
import numpy as np

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [1, 1.25]})
t = 8
for i in range(t + 2):
    for j in range(t + 2):
        inner = 1 <= i <= t and 1 <= j <= t
        a.add_patch(plt.Rectangle((j, i), 1, 1, fc=C["z"] if inner else C["accent"], alpha=0.35 if inner else 0.45, ec="white", lw=1))
a.add_patch(plt.Rectangle((1, 1), t, t, fill=False, ec=C["z"], lw=2))
for (i, j) in [(4, 4)]:                     # 一个输出要用到的 3×3 邻域
    a.add_patch(plt.Rectangle((j - 1, i - 1), 3, 3, fill=False, ec=C["x"], lw=2))
    a.add_patch(plt.Rectangle((j, i), 1, 1, fc=C["x"], alpha=0.8))
a.set_xlim(-0.3, t + 2.3)
a.set_ylim(t + 2.3, -0.3)
a.set_aspect("equal")
a.axis("off")
a.set_title(T(f"（a）T = {t}：蓝色是输出，黄色是晕圈", f"(a) T = {t}: outputs (blue), halo (yellow)"), fontsize=10)
ts = np.arange(4, 65)
b.plot(ts, (ts + 2) ** 2 / ts ** 2, color=C["z"], lw=2, label=T("分块：(T+2)²/T²", "tiled: (T+2)²/T²"))
b.axhline(9, color=C["x"], lw=1.5, ls="--", label=T("不靠缓存的朴素版：9", "naive without caches: 9"))
b.axhline(1, color=C["muted"], lw=1, ls=":", label=T("每个输入只读一次：1", "each input read once: 1"))
for tt in (8, 16, 32):
    v = (tt + 2) ** 2 / tt ** 2
    b.plot([tt], [v], "o", color=C["z"])
    b.annotate(f"{v:.2f}", (tt, v), textcoords="offset points", xytext=(4, 6), fontsize=9)
b.set_yscale("log")
b.set_yticks([1, 2, 4, 9])
b.set_yticklabels(["1", "2", "4", "9"])
b.set_xlabel(T("线程块负责的输出块边长 T", "output tile size T"))
b.set_ylabel(T("每个输出从显存读的输入个数", "inputs read from memory per output"))
b.set_title(T("（b）分块的晕圈开销", "(b) Halo overhead of tiling"), fontsize=10)
b.legend(fontsize=9, frameon=False)
fig.tight_layout()
figure(fig, "fig5_1_1")
plt.close(fig)
