"""4.8 节的示意图。

图 4.8.1：（a）数据竞争：两个线程同时把计数器加 1，指令交错时有一次加法丢失（算例 4.8.1）；
（b）检测相机测试图的灰度直方图（数据同程序 4.8.1）：像素集中在少数几个灰度级上，用原子加法统计时争用严重。
"""
import numpy as np

from _ch4 import frame, gray
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1, 1.1]})
ax = axs[0]
steps = [("A", T("读 c → 5", "read c → 5"), 5), ("B", T("读 c → 5", "read c → 5"), 5), ("A", T("写 c ← 6", "write c ← 6"), 6),
         ("B", T("写 c ← 6", "write c ← 6"), 6)]
for i, (who, text, c) in enumerate(steps):
    x = 0 if who == "A" else 1
    ax.add_patch(plt.Rectangle((x * 2.2, 3 - i), 2.0, 0.8, color=C["z"] if who == "A" else C["accent"], alpha=0.75))
    ax.text(x * 2.2 + 1.0, 3.4 - i, text, ha="center", va="center", fontsize=9.5, color="white")
    ax.text(4.8, 3.4 - i, f"c = {c}", va="center", fontsize=9.5, color=C["ink"])
ax.text(1.0, 4.1, T("线程 A", "thread A"), ha="center", fontsize=10, color=C["ink"])
ax.text(3.2, 4.1, T("线程 B", "thread B"), ha="center", fontsize=10, color=C["ink"])
ax.text(2.6, -0.6, T("应为 7，结果为 6：一次加法丢失", "should be 7, is 6: one addition lost"), ha="center", fontsize=9.5, color=C["x"])
ax.set_xlim(-0.3, 5.8)
ax.set_ylim(-1, 4.6)
ax.axis("off")
ax.set_title(T("（a）“读—加一—写”的交错", "(a) Interleaved read–add–write"), fontsize=10.5)
ax = axs[1]
y = gray(frame()).ravel()
h = np.bincount(y, minlength=256)
ax.bar(np.arange(256), h / 1e3, width=1.0, color=C["z"])
ax.set_yscale("log")
ax.set_xlabel(T("灰度级", "grey level"))
ax.set_ylabel(T("像素数（千）", "pixels (thousands)"))
ax.set_xlim(0, 255)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title(T(f"（b）测试图的直方图：只用到 {int((h > 0).sum())} 个灰度级", f"(b) Histogram of the test frame: {int((h > 0).sum())} grey levels used"),
             fontsize=10.5)
figure(fig, "fig4_8_1")
plt.close(fig)
