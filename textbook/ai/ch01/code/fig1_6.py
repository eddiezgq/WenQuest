"""1.6 节的示意图。

图 1.6.1：CUDA 的编程模型：主机启动核函数，网格由线程块组成，线程块由线程组成；每个线程按自己的编号处理一个元素。
图 1.6.2：三代 GPU 的单精度峰值、FP16 张量核心峰值与显存带宽（对数坐标），以及它们的比值 P/β。
"""
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from _ch1 import HW, gtx580_peak
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

# ---------------------------------------------------------------- 图 1.6.1
fig, ax = plt.subplots(figsize=(10.0, 4.8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 5.2)
ax.axis("off")
ax.add_patch(FancyBboxPatch((0.2, 1.6), 1.9, 2.4, boxstyle="round,pad=0.02,rounding_size=0.1", fc="#f5f5f5", ec=C["muted"], lw=1.2))
ax.text(1.15, 3.6, T("主机（CPU）", "Host (CPU)"), ha="center", fontsize=11, weight="bold", color=C["ink"])
ax.text(1.15, 2.8, "add<<<g, b>>>\n(a, b, c, n);", ha="center", va="center", fontsize=9.5, family="monospace", color=C["ink"])
ax.text(1.15, 1.95, T("启动核函数", "launch kernel"), ha="center", fontsize=9, color=C["muted"])
ax.add_patch(FancyArrowPatch((2.15, 2.8), (2.75, 2.8), arrowstyle="-|>", mutation_scale=16, lw=1.6, color=C["ink"]))
ax.add_patch(FancyBboxPatch((2.8, 0.55), 7.0, 4.25, boxstyle="round,pad=0.02,rounding_size=0.1", fc="#eef3f8", ec=C["z"], lw=1.4))
ax.text(3.0, 4.45, T("设备（GPU）上的网格：g 个线程块", "Grid on the device (GPU): g thread blocks"), fontsize=11, weight="bold", color=C["z"])
for k in range(4):
    x0 = 3.05 + 1.68 * k
    ax.add_patch(FancyBboxPatch((x0, 1.25), 1.5, 2.85, boxstyle="round,pad=0.02,rounding_size=0.06", fc="white", ec=C["ink"], lw=1.0))
    lab = T(f"线程块 {k}", f"block {k}") if k < 3 else T("……", "...")
    ax.text(x0 + 0.75, 3.85, lab, ha="center", fontsize=9.5, color=C["ink"])
    if k < 3:
        for j in range(8):
            yy = 3.45 - 0.27 * j
            ax.add_patch(plt.Rectangle((x0 + 0.12, yy - 0.1), 1.26, 0.2, fc="#fdf3dc" if j < 7 else "#ffffff", ec=C["accent"], lw=0.6))
            txt = f"t{j}" if j < 6 else ("…" if j == 6 else f"t{255}")
            ax.text(x0 + 0.25, yy, txt, va="center", fontsize=7.4, color=C["ink"])
            if j < 6:
                ax.text(x0 + 1.3, yy, f"i={k * 256 + j}", va="center", ha="right", fontsize=7.0, color=C["muted"])
            elif j == 7:
                ax.text(x0 + 1.3, yy, f"i={k * 256 + 255}", va="center", ha="right", fontsize=7.0, color=C["muted"])
ax.text(6.3, 0.85, T("每块 b = 256 个线程；线程 t 在块 k 中处理第 i = k·b + t 个元素",
                     "b = 256 threads per block; thread t of block k handles element i = k·b + t"), ha="center", fontsize=9.2,
        color=C["ink"])
figure(fig, "fig1_6_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 1.6.2
names = ["GTX 580\n(2010)", "A100\n(2020)", "H100\n(2022)"]
p32 = np.array([gtx580_peak(), HW["a100"]["P_fp32"], HW["h100"]["P_fp32"]]) / 1e12
p16 = np.array([np.nan, HW["a100"]["P_fp16"], HW["h100"]["P_fp16"]]) / 1e12
bw = np.array([HW["gtx580"]["bw"], HW["a100"]["bw"], HW["h100"]["bw"]]) / 1e12
fig, axs = plt.subplots(1, 2, figsize=(10.0, 3.9), gridspec_kw={"width_ratios": [1.4, 1]})
ax = axs[0]
x = np.arange(3)
w = 0.26
b1 = ax.bar(x - w, p32, w, color=C["z"], label=T("单精度峰值（TFLOP/s）", "FP32 peak (TFLOP/s)"))
b2 = ax.bar(x, np.nan_to_num(p16), w, color=C["accent"], label=T("FP16 张量核心稠密峰值（TFLOP/s）", "FP16 tensor-core dense peak (TFLOP/s)"))
b3 = ax.bar(x + w, bw, w, color=C["x"], label=T("显存带宽（TB/s）", "memory bandwidth (TB/s)"))
ax.set_yscale("log")
ax.set_ylim(0.1, 3000)
for bars, vals in ((b1, p32), (b2, p16), (b3, bw)):
    for bb, v in zip(bars, vals):
        if not np.isnan(v) and v > 0:
            ax.text(bb.get_x() + bb.get_width() / 2, v * 1.15, f"{v:.3g}", ha="center", fontsize=7.8, color=C["ink"])
ax.text(x[0], 5.0, T("（无张量核心）", "(no tensor cores)"), ha="center", fontsize=7.8, color=C["muted"])
ax.set_xticks(x)
ax.set_xticklabels(names, fontsize=9)
ax.legend(fontsize=8, frameon=False, loc="upper left")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title(T("（a）算力与带宽", "(a) Compute and bandwidth"), fontsize=11)
ax = axs[1]
bal32 = p32 / bw
bal16 = p16 / bw
ax.plot(x, bal32, "o-", color=C["z"], label=T("单精度 P/β", "FP32 P/β"))
ax.plot(x[1:], bal16[1:], "s-", color=C["accent"], label=T("FP16 张量核心 P/β", "FP16 tensor P/β"))
for xi, v in zip(x, bal32):
    ax.text(xi, v * 1.18, f"{v:.0f}", ha="center", fontsize=8.6, color=C["z"])
for xi, v in zip(x[1:], bal16[1:]):
    ax.text(xi, v * 1.18, f"{v:.0f}", ha="center", fontsize=8.6, color=C["accent"])
ax.set_yscale("log")
ax.set_ylim(3, 1000)
ax.set_xticks(x)
ax.set_xticklabels(names, fontsize=9)
ax.set_ylabel("FLOP/B")
ax.legend(fontsize=8, frameon=False, loc="upper left")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title(T("（b）每读一个字节要做多少次运算才不浪费算力", "(b) Operations per byte needed to keep the units busy"), fontsize=10)
fig.tight_layout()
figure(fig, "fig1_6_2")
plt.close(fig)
