"""3.3 节的示意图。

图 3.3.1：（a）CPU 与 GPU 芯片面积分配的示意（不按比例）：CPU 把面积用在少数强大的核心、控制逻辑和大缓存上，
GPU 把面积用在大量简单的运算通道上；（b）利特尔定律：要用满带宽，路上（已发出、未返回）的数据 = 带宽 × 延迟，
CPU 与 H100 的比较（数据同程序 3.3.1）。
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
runpy.run_path(str(Path(__file__).with_name("ex3_3.py")))
bookout.out = saved

fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.4), gridspec_kw={"width_ratios": [1.35, 1]})
ax = axs[0]
ax.set_xlim(0, 10.6)
ax.set_ylim(0, 5.4)
ax.axis("off")
# CPU
ax.add_patch(plt.Rectangle((0.2, 0.4), 4.6, 4.3, fill=False, ec=C["ink"], lw=1.2))
for i in range(2):
    for j in range(2):
        x0, y0 = 0.4 + j * 2.2, 2.65 + i * 1.0
        ax.add_patch(plt.Rectangle((x0, y0), 0.9, 0.85, color=C["accent"], alpha=0.35))
        ax.add_patch(plt.Rectangle((x0 + 0.95, y0), 1.1, 0.85, color=C["z"], alpha=0.75))
for i in range(2):
    for j in range(2):
        ax.text(0.85 + j * 2.2, 3.07 + i * 1.0, T("控制", "ctrl"), ha="center", va="center", fontsize=8.2, color=C["ink"])
        ax.text(1.9 + j * 2.2, 3.07 + i * 1.0, T("运算", "ALU"), ha="center", va="center", fontsize=8.2, color="white")
ax.add_patch(plt.Rectangle((0.4, 1.25), 4.2, 1.25, color=C["y"], alpha=0.35))
ax.text(2.5, 1.85, T("大容量缓存", "large caches"), ha="center", va="center", fontsize=9.5, color=C["ink"])
ax.add_patch(plt.Rectangle((0.4, 0.55), 4.2, 0.55, color=C["muted"], alpha=0.35))
ax.text(2.5, 0.82, T("内存接口", "DRAM interface"), ha="center", va="center", fontsize=8.5, color=C["ink"])
ax.text(2.5, 4.95, T("CPU：面向延迟", "CPU: latency-oriented"), ha="center", fontsize=11, weight="bold", color=C["ink"])
# GPU
ax.add_patch(plt.Rectangle((5.6, 0.4), 4.8, 4.3, fill=False, ec=C["ink"], lw=1.2))
for r in range(8):
    y0 = 1.25 + r * 0.42
    ax.add_patch(plt.Rectangle((5.75, y0), 0.3, 0.34, color=C["accent"], alpha=0.35))
    ax.add_patch(plt.Rectangle((6.1, y0), 0.3, 0.34, color=C["y"], alpha=0.35))
    for c in range(12):
        ax.add_patch(plt.Rectangle((6.48 + c * 0.32, y0), 0.26, 0.34, color=C["z"], alpha=0.75))
ax.add_patch(plt.Rectangle((5.75, 0.55), 4.5, 0.55, color=C["muted"], alpha=0.35))
ax.text(8.0, 0.82, T("高带宽显存接口", "HBM interface"), ha="center", va="center", fontsize=8.5, color=C["ink"])
ax.text(8.0, 4.95, T("GPU：面向吞吐", "GPU: throughput-oriented"), ha="center", fontsize=11, weight="bold", color=C["ink"])
ax.text(5.3, 0.05, T("橙：控制　绿：缓存　蓝：运算单元（示意，不按比例）", "orange: control  green: cache  blue: ALUs (schematic, not to scale)"),
        ha="center", fontsize=8.5, color=C["muted"])
ax.set_title(T("（a）芯片面积花在哪里", "(a) Where the die area goes"), fontsize=11)

ax = axs[1]
names = [T("CPU\n（8 通道 DDR5）", "CPU\n(8-ch DDR5)"), "H100\n(HBM3)"]
vals = [v["cpu_inflight_kB"], v["gpu_inflight_MB"] * 1e3]
b = ax.bar([0, 1], vals, color=[C["accent"], C["z"]], width=0.55)
ax.set_yscale("log")
for i, (bb, val) in enumerate(zip(b, vals)):
    txt = T(f"{val:.0f} kB\n= {v['cpu_bw_G']:.0f} GB/s × {v['cpu_lat_ns']:.0f} ns", f"{val:.0f} kB\n= {v['cpu_bw_G']:.0f} GB/s × {v['cpu_lat_ns']:.0f} ns") if i == 0 \
        else T(f"{val / 1e3:.2f} MB\n= {v['h_bw_T']:.2f} TB/s × {v['tau_ns']:.0f} ns", f"{val / 1e3:.2f} MB\n= {v['h_bw_T']:.2f} TB/s × {v['tau_ns']:.0f} ns")
    ax.text(bb.get_x() + bb.get_width() / 2, val * 1.25, txt, ha="center", fontsize=9, color=C["ink"])
ax.set_xticks([0, 1])
ax.set_xticklabels(names)
ax.set_ylim(5, 2e4)
ax.set_ylabel(T("在途数据（kB）", "bytes in flight (kB)"))
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title(T("（b）要用满带宽，路上要有多少数据", "(b) Data in flight to saturate bandwidth"), fontsize=11)
fig.tight_layout()
figure(fig, "fig3_3_1")
plt.close(fig)
