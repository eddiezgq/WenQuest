"""图 22.4.1：(a) 屋顶线模型（假设峰值 1 TFLOP/s、内存带宽 100 GB/s）：可达速度 = min(峰值, 带宽 × 运算强度)，
一级（向量加）、二级（矩阵乘向量）BLAS 被带宽卡住，三级（矩阵乘法）可达峰值；(b) 64 阶矩阵乘法在一个 512 个数的 LRU 缓存上的
缓存未命中次数：三重循环与块大小 4、8、16 的分块算法（虚线为必须的最少次数：每个数读一次）。数值与程序 22.4.1 的模拟结果相同。"""
import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

peak, bw = 1000.0, 100.0 / 8
ai = np.logspace(-1, 3, 200)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.4))
a1.loglog(ai, np.minimum(peak, bw * ai), color=INK, lw=2)
for name, x, col in ((T("向量加（一级）", "axpy (level 1)"), 2 / 3, RED), (T("矩阵乘向量（二级）", "gemv (level 2)"), 2.0, GREEN),
                     (T("矩阵乘法 n = 1000（三级）", "gemm n = 1000 (level 3)"), 500.0, BLUE)):
    y = min(peak, bw * x)
    a1.plot([x], [y], "o", color=col, ms=8)
    a1.annotate(f"{name}\n{y:.4g} GFLOP/s", (x, y), xytext=(6, -26 if x < 100 else -34), textcoords="offset points", color=col, fontsize=9)
a1.axvline(peak / bw, color=MUTED, ls="--", lw=1)
a1.text(peak / bw * 1.1, 3, T("拐点 80 次/数", "ridge: 80 flops/word"), color=MUTED, fontsize=9)
a1.set_xlabel(T("运算强度（每读写一个数的运算次数）", "arithmetic intensity (flops per word moved)"))
a1.set_ylabel(T("可达速度 / (GFLOP/s)", "attainable speed / (GFLOP/s)"))
a1.set_ylim(1, 3000)
a1.set_title(T("(a) 屋顶线模型", "(a) Roofline model"), fontsize=10)
labels = [T("三重循环", "triple loop"), "b = 4", "b = 8", "b = 16"]
vals = [295424, 25088, 8704, 6144]
a2.bar(range(4), vals, color=[RED, GREEN, GREEN, GREEN])
a2.set_yscale("log")
a2.axhline(1536, color=MUTED, ls="--", lw=1)
a2.text(-0.4, 1700, T("下限 1536", "minimum 1536"), color=MUTED, fontsize=9, ha="left")
for i, v in enumerate(vals):
    a2.text(i, v * 1.15, str(v), ha="center", fontsize=9)
a2.set_xticks(range(4))
a2.set_xticklabels(labels)
a2.set_ylabel(T("缓存未命中次数", "cache misses"))
a2.set_ylim(1000, 1e6)
a2.set_title(T("(b) 64 阶矩阵乘法，缓存 512 个数", "(b) Order-64 matrix product, 512-word cache"), fontsize=10)
for a in (a1, a2):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig22_4_1")
