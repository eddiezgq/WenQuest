"""4.3 节的示意图。

图 4.3.1：处理一帧图像的时间线（PCIe 4.0 ×16 理论带宽、A10 显存带宽估计，数据同程序 4.3.1）：
上：传入图像 → 核函数 → 取回掩码，依次进行；下：用锁页内存与多个流，让下一帧的传输与这一帧的计算重叠（第 6 章）。
"""
import runpy
from pathlib import Path

import bookout
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
saved = bookout.out
v = {}
bookout.out = lambda **kw: v.update(kw)
runpy.run_path(str(Path(__file__).with_name("ex4_3.py")))
bookout.out = saved

h2d = v["frame_MB"] / v["pcie4"]                # ms（MB / GB/s = ms）
d2h = v["mask_MB"] / v["pcie4"]
k = v["tk_a10_us"] / 1e3
fig, ax = plt.subplots(figsize=(10, 3.4))
y1, y2 = 2.6, 0.6
t = 0
for i in range(3):
    for dur, col, lab in ((h2d, C["x"], T("传入", "H2D")), (k, C["z"], T("核", "kernel")), (d2h, C["accent"], T("取回", "D2H"))):
        ax.add_patch(plt.Rectangle((t, y1), dur, 0.7, color=col, alpha=0.8))
        if dur > 0.15:
            ax.text(t + dur / 2, y1 + 0.35, lab, ha="center", va="center", fontsize=8.5, color="white")
        t += dur
ax.text(-0.05, y1 + 0.35, T("依次进行", "one after another"), ha="right", va="center", fontsize=9.5, color=C["ink"])
t = 0
for i in range(3):          # 传入与取回在两个方向上同时进行，核函数插在中间
    ax.add_patch(plt.Rectangle((i * h2d, y2 + 0.45), h2d, 0.4, color=C["x"], alpha=0.8))
    ax.add_patch(plt.Rectangle(((i + 1) * h2d, y2), k, 0.4, color=C["z"], alpha=0.8))
    ax.add_patch(plt.Rectangle(((i + 1) * h2d + k, y2 - 0.45), d2h, 0.4, color=C["accent"], alpha=0.8))
ax.text(-0.05, y2, T("重叠（多个流）", "overlapped (streams)"), ha="right", va="center", fontsize=9.5, color=C["ink"])
ax.set_xlim(-1.4, 3 * (h2d + k + d2h) + 0.1)
ax.set_ylim(-0.2, 3.6)
ax.set_yticks([])
ax.set_xticks([0, 1, 2, 3])
ax.set_xlabel(T("时间（ms）", "time (ms)"))
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.set_title(T(f"每帧：传入 {h2d:.2f} ms，核函数 {k * 1e3:.0f} µs，取回 {d2h:.2f} ms（PCIe 4.0 ×16 理论值，A10）",
               f"Per frame: H2D {h2d:.2f} ms, kernel {k * 1e3:.0f} µs, D2H {d2h:.2f} ms (PCIe 4.0 ×16 theoretical, A10)"), fontsize=10.5)
figure(fig, "fig4_3_1")
plt.close(fig)
