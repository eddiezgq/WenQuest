"""图 4.7.1：乘法次数——普通算法 n³ 与完全递归的施特拉森算法 7^log₂n = n^2.81（双对数坐标）；右：存储层次的容量与访问时间（数量级）。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

k = np.arange(1, 15)
n = 2.0 ** k
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.0))
a1.loglog(n, n ** 3, "o-", color=BLUE, ms=4, label=T("普通算法 n³", "standard n³"))
a1.loglog(n, 7.0 ** k, "s-", color=RED, ms=4, label=T("施特拉森 n^2.81", "Strassen n^2.81"))
a1.set_xlabel("n")
a1.set_ylabel(T("乘法次数", "multiplications"))
a1.legend(frameon=False)
levels = [(T("寄存器", "registers"), 1e3, 0.3), (T("一级缓存", "L1 cache"), 5e4, 1), (T("二级缓存", "L2 cache"), 1e6, 4),
          (T("三级缓存", "L3 cache"), 3e7, 15), (T("内存", "main memory"), 3e10, 80), (T("固态硬盘", "SSD"), 1e12, 1e5)]
y = np.arange(len(levels))
a2.barh(y, [np.log10(c) for _, c, _ in levels], color=GREEN, alpha=0.6)
for i, (name, c, t) in enumerate(levels):
    a2.text(0.1, i, f"{name}", va="center", fontsize=10)
    a2.text(np.log10(c) + 0.2, i, T(f"约 {t:g} ns", f"≈ {t:g} ns"), va="center", fontsize=9, color=MUTED)
a2.set_yticks([])
a2.invert_yaxis()
a2.set_xlabel(T("容量（字节，以 10 为底的对数）", "capacity (bytes, log10)"))
a2.set_xlim(0, 16)
a2.set_title(T("越大越慢：存储层次", "bigger is slower: the memory hierarchy"), fontsize=11)
for ax in (a1, a2):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig4_7_1")
