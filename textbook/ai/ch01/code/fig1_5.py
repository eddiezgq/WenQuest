"""1.5 节的示意图。

图 1.5.1：AlexNet 各层的乘加次数与参数量：运算集中在卷积层，参数集中在全连接层。
图 1.5.2：CPU 与 GPU 的设计取向示意：少数复杂的大核与大缓存，对比成千上万个简单的运算单元与高带宽显存。
图 1.5.3：在 H100 上逐词生成（70 亿参数模型，FP16）时，每个词元的计算时间下限与读权重时间下限随批大小的变化。
"""
import numpy as np
from matplotlib.patches import FancyBboxPatch

from _ch1 import CPU, HW, alexnet_layers
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

# ---------------------------------------------------------------- 图 1.5.1
rows = alexnet_layers()
names = [r[0] for r in rows]
macs = np.array([r[1] for r in rows]) / 1e6
params = np.array([r[2] for r in rows]) / 1e6
fig, axs = plt.subplots(1, 2, figsize=(10.0, 3.8))
cols = [C["z"] if n.startswith("conv") else C["accent"] for n in names]
for ax, vals, lab, title in ((axs[0], macs, T("乘加次数（百万）", "multiply–adds (millions)"), T("（a）每张图的乘加次数", "(a) Multiply–adds per image")),
                             (axs[1], params, T("参数量（百万）", "parameters (millions)"), T("（b）参数量", "(b) Parameters"))):
    b = ax.bar(names, vals, color=cols, width=0.65)
    for bb, v in zip(b, vals):
        ax.text(bb.get_x() + bb.get_width() / 2, v + vals.max() * 0.015, (f"{v:.2f}" if v < 1 else f"{v:.1f}"), ha="center", fontsize=8, color=C["ink"])
    ax.set_ylabel(lab)
    ax.set_title(title, fontsize=11)
    ax.tick_params(axis="x", labelsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axs[0].text(0.98, 0.92, T("蓝：卷积层  金：全连接层", "blue: conv   gold: fully connected"), transform=axs[0].transAxes, ha="right",
            fontsize=8.6, color=C["muted"])
fig.tight_layout()
figure(fig, "fig1_5_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 1.5.2
fig, axs = plt.subplots(1, 2, figsize=(10.0, 4.0))
for ax in axs:
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")


def rbox(ax, x, y, w, h, fc, ec, text="", fs=9, lw=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.08", fc=fc, ec=ec, lw=lw))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=C["ink"])


ax = axs[0]
ax.set_title(T("CPU：少数大核，面向低延迟", "CPU: a few big cores, built for latency"), fontsize=11)
for i in range(2):
    for j in range(2):
        x0, y0 = 0.4 + 2.4 * j, 3.6 + 1.6 * i
        rbox(ax, x0, y0, 2.1, 1.35, "#eef3f8", C["z"], "", lw=1.2)
        rbox(ax, x0 + 0.1, y0 + 0.75, 0.9, 0.5, "#fdf3dc", C["ink"], T("控制", "control"), 7.5)
        rbox(ax, x0 + 1.1, y0 + 0.75, 0.9, 0.5, "#dbe7f3", C["ink"], T("运算", "ALU"), 7.5)
        rbox(ax, x0 + 0.1, y0 + 0.1, 1.9, 0.5, "#f1f6ef", C["ink"], T("一级、二级缓存", "L1/L2 cache"), 7.5)
rbox(ax, 5.3, 3.6, 4.2, 2.95, "#f1f6ef", C["y"], T("大容量末级缓存", "large last-level cache"), 9.5)
rbox(ax, 0.4, 1.6, 9.1, 1.4, "#f5f5f5", C["muted"], T(f"内存（DDR）：容量大，带宽约 {CPU['channels'] * CPU['mts'] * 8 / 1e9:.0f} GB/s（8 通道 DDR5-4800）",
                                                     f"Memory (DDR): large, ≈ {CPU['channels'] * CPU['mts'] * 8 / 1e9:.0f} GB/s (8-channel DDR5-4800)"), 9)
ax.text(5, 0.7, T("分支预测、乱序执行、大缓存：让单个线程尽快跑完", "branch prediction, out-of-order, big caches: finish one thread fast"),
        ha="center", fontsize=8.8, color=C["muted"])
ax = axs[1]
ax.set_title(T("GPU：成千上万个简单单元，面向高吞吐", "GPU: thousands of simple units, built for throughput"), fontsize=11)
for i in range(4):
    for j in range(6):
        x0, y0 = 0.3 + 1.58 * j, 3.55 + 0.78 * i
        rbox(ax, x0, y0, 1.45, 0.68, "#eef3f8", C["z"], "", lw=0.8)
        ax.add_patch(plt.Rectangle((x0 + 0.05, y0 + 0.47), 0.4, 0.15, fc="#fdf3dc", ec=C["ink"], lw=0.5))
        for kx in range(6):
            for ky in range(2):
                ax.add_patch(plt.Rectangle((x0 + 0.08 + 0.22 * kx, y0 + 0.08 + 0.18 * ky), 0.17, 0.13, fc="#9fc0e0", ec="none"))
rbox(ax, 0.3, 2.85, 9.35, 0.5, "#f1f6ef", C["y"], T("二级缓存（所有流多处理器共享）", "L2 cache (shared by all SMs)"), 8.5)
rbox(ax, 0.3, 1.6, 9.35, 1.05, "#fbe9e7", C["x"], T(f"高带宽显存（HBM）：H100 约 {HW['h100']['bw'] / 1e12:.2f} TB/s",
                                                   f"High-bandwidth memory (HBM): H100 ≈ {HW['h100']['bw'] / 1e12:.2f} TB/s"), 9)
ax.text(5, 0.7, T("每个方框是一个流多处理器（SM），里面有许多运算单元和张量核心", "each box is a streaming multiprocessor with many ALUs and tensor cores"),
        ha="center", fontsize=8.8, color=C["muted"])
fig.tight_layout()
figure(fig, "fig1_5_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 1.5.3
N = 7e9
P = HW["h100"]["P_fp16"]
bw = HW["h100"]["bw"]
B = np.logspace(0, 3.3, 200)
t_comp = 2 * N * B / P                 # 一批 B 条序列各生成一个词元的运算时间下限
t_mem = np.full_like(B, 2 * N / bw)    # 读一遍 FP16 权重的时间下限（忽略 KV 缓存）
fig, ax = plt.subplots(figsize=(7.0, 4.0))
ax.loglog(B, t_comp * 1e3, color=C["z"], lw=1.8, label=T("计算时间下限 $W/P$", "compute bound $W/P$"))
ax.loglog(B, t_mem * 1e3, color=C["x"], lw=1.8, label=T("读权重时间下限 $Q/\\beta$", "memory bound $Q/\\beta$"))
ax.loglog(B, np.maximum(t_comp, t_mem) * 1e3, color=C["ink"], lw=3, alpha=0.25, label=T("两者中较大的", "the larger of the two"))
Bs = P / bw
ax.axvline(Bs, color=C["muted"], ls=":", lw=1.2)
ax.text(Bs * 1.08, 0.02, T(f"$B \\approx {Bs:.0f}$", f"$B \\approx {Bs:.0f}$"), fontsize=10, color=C["muted"])
ax.text(1.3, 6.0, T("受显存带宽限制", "memory-bound"), fontsize=10, color=C["x"])
ax.text(1900, 12, T("受算力限制", "compute-bound"), fontsize=10, color=C["z"], ha="right")
ax.set_xlabel(T("批大小 $B$（同时生成的序列数）", "batch size $B$ (sequences generated together)"))
ax.set_ylabel(T("每步时间下限 / ms", "time per step (lower bound) / ms"))
ax.set_ylim(0.01, 100)
ax.legend(fontsize=8.6, frameon=False, loc="lower right")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig1_5_3")
plt.close(fig)
