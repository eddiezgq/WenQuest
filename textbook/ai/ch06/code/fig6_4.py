"""6.4 节的示意图（数据同程序 6.4.2）。

图 6.4.1：4 块 GPU 的环形全归约。每块 GPU 的数组切成 4 块（a、b、c、d）。归约—散播 3 步：每步每块 GPU 把一块发给右邻，右邻加到自己的
同一块上，3 步后每块 GPU 有一块完整的和（深色）；全收集 3 步：把完整的块沿环传下去，最后每块 GPU 都有全部的和。
图 6.4.2：α–β 模型下 8 块 A100 的全归约耗时随消息大小的变化：朴素、环形、树形三种算法。
"""
import math

import numpy as np

from bookout import COLORS, T, figure, style
from gpus import NVLINK

plt = style()
C = COLORS
p = 4
cols = [C["x"], C["z"], C["y"], C["accent"]]
fig, axs = plt.subplots(1, 7, figsize=(13, 3.4))
have = [[{r} for c in range(p)] for r in range(p)]      # have[r][c]：第 r 块 GPU 的第 c 块里已经加了哪些 GPU 的数据
stages = [("开始", "start")]
snap = [[set(x) for x in row] for row in have]
snaps = [snap]
for s in range(p - 1):
    new = [[set(x) for x in row] for row in have]
    for r in range(p):
        c = (r - s) % p
        new[(r + 1) % p][c] |= have[r][c]
    have = new
    snaps.append([[set(x) for x in row] for row in have])
    stages.append((f"归约—散播 {s + 1}", f"reduce-scatter {s + 1}"))
for s in range(p - 1):
    new = [[set(x) for x in row] for row in have]
    for r in range(p):
        c = (r + 1 - s) % p
        new[(r + 1) % p][c] = set(have[r][c])
    have = new
    snaps.append([[set(x) for x in row] for row in have])
    stages.append((f"全收集 {s + 1}", f"all-gather {s + 1}"))
for ax, sn, (zh, en) in zip(axs, snaps, stages):
    for r in range(p):
        for c in range(p):
            full = len(sn[r][c]) == p
            ax.add_patch(plt.Rectangle((c, -r), 0.92, 0.85, fc=cols[c], alpha=0.95 if full else 0.15 + 0.15 * len(sn[r][c]), ec="white"))
            ax.text(c + 0.46, -r + 0.42, str(len(sn[r][c])), ha="center", va="center", fontsize=8)
    ax.set_xlim(-0.1, p)
    ax.set_ylim(-p + 0.7, 1.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(T(zh, en), fontsize=9)
axs[0].text(-0.2, 0.42, "GPU 0", ha="right", va="center", fontsize=8)
axs[0].text(-0.2, -2.58, f"GPU {p - 1}", ha="right", va="center", fontsize=8)
fig.suptitle(T("4 块 GPU 的环形全归约：格中数字是这一块里已经加进了几块 GPU 的数据，深色 = 完整的和",
               "Ring all-reduce on 4 GPUs: each cell shows how many GPUs' data it already contains; dark = complete sum"), fontsize=10)
fig.tight_layout()
figure(fig, "fig6_4_1")
plt.close(fig)

alpha, beta, P = 2e-6, NVLINK["a100"], 8
n = np.logspace(3, 10.5, 200)
fig, ax = plt.subplots(figsize=(8, 4.6))
for name, f, c in ((T("朴素", "naive"), lambda x: 2 * (P - 1) * (alpha + x / beta), C["muted"]),
                   (T("环形", "ring"), lambda x: 2 * (P - 1) * alpha + 2 * (P - 1) / P * x / beta, C["z"]),
                   (T("树形", "tree"), lambda x: 2 * math.log2(P) * alpha + 2 * x / beta, C["x"])):
    ax.plot(n, f(n) * 1e3, color=c, lw=2, label=name)
for x, lab in ((46.1e6, T("小型 Transformer 的梯度", "tiny Transformer grads")), (14e9, T("70 亿参数（半精度）", "7B params (FP16)"))):
    ax.axvline(x, color=C["muted"], ls=":", lw=1)
    ax.text(x * 1.15, 2e-3, lab, rotation=90, fontsize=8, color=C["muted"], va="bottom")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel(T("消息大小（字节）", "message size (bytes)"))
ax.set_ylabel(T("全归约耗时（ms）", "all-reduce time (ms)"))
ax.set_title(T(f"8 块 A100 的全归约（α = {alpha * 1e6:.0f} μs，β = {beta / 1e9:.0f} GB/s）", f"All-reduce on 8 A100s (α = {alpha * 1e6:.0f} μs, β = {beta / 1e9:.0f} GB/s)"), fontsize=10)
ax.legend(frameon=False, fontsize=9)
fig.tight_layout()
figure(fig, "fig6_4_2")
plt.close(fig)
