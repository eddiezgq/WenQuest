"""8.3 节的示意图（数据同程序 8.3.1）。

图 8.3.1：（a）GELU 输出的分布（输入为标准正态）与 3 位量化的格点：对称量化的格点关于 0 对称，负半轴几乎没有数据，
一半的格点浪费了；非对称量化用一个零点把格点平移到 [min, max]，同样的位数格点更密（示意用 3 位，看得清楚；程序中是 8 位）。
（b）权重矩阵（各输出通道的尺度不同）按 INT8、INT4 量化的相对误差：逐张量与逐通道。
"""
import numpy as np

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 4.2))
z = np.random.default_rng(1).standard_normal(200000)
g = 0.5 * z * (1 + np.tanh(np.sqrt(2 / np.pi) * (z + 0.044715 * z ** 3)))
a.hist(g, bins=200, color=C["muted"], alpha=0.5, density=True)
bits = 3
qmax = 2 ** (bits - 1) - 1
s = np.abs(g).max() / qmax
for k in range(-qmax, qmax + 1):
    a.axvline(k * s, ymin=0.55, ymax=0.95, color=C["z"], lw=2)
lo, hi = g.min(), g.max()
s2 = (hi - lo) / (2 ** bits - 1)
for k in range(2 ** bits):
    a.axvline(lo + k * s2, ymin=0.05, ymax=0.45, color=C["x"], lw=2)
a.text(0.98, 0.9, T("对称：格点关于 0 对称", "symmetric grid"), transform=a.transAxes, ha="right", color=C["z"], fontsize=9, bbox=dict(fc="white", ec="none", alpha=0.85))
a.text(0.98, 0.35, T("非对称：格点铺满 [min, max]", "asymmetric grid over [min, max]"), transform=a.transAxes, ha="right", color=C["x"], fontsize=9, bbox=dict(fc="white", ec="none", alpha=0.85))
a.set_yticks([])
a.set_xlabel(T("GELU 的输出", "GELU output"))
a.set_title(T("（a）对称与非对称量化的格点（3 位，示意）", "(a) Symmetric and asymmetric grids (3 bits, illustrative)"), fontsize=10)

din, dout = 384, 1536
rng = np.random.default_rng(83)                             # 与程序 8.3.1 相同的权重矩阵
ch_scale = np.exp(rng.normal(0, 0.6, dout))
W = rng.normal(0, 0.02, (din, dout)) * ch_scale


def err(bits, axis):
    q = 2 ** (bits - 1) - 1
    sc = np.abs(W).max(axis=axis, keepdims=axis is not None) / q
    return np.linalg.norm(np.clip(np.round(W / sc), -q, q) * sc - W) / np.linalg.norm(W) * 100


x = np.arange(2)
b.bar(x - 0.18, [err(8, None), err(4, None)], 0.36, color=C["muted"], label=T("逐张量", "per tensor"))
b.bar(x + 0.18, [err(8, 0), err(4, 0)], 0.36, color=C["z"], label=T("逐通道", "per channel"))
b.set_xticks(x)
b.set_xticklabels(["INT8", "INT4"])
b.set_yscale("log")
b.set_ylabel(T("相对误差（%）", "relative error (%)"))
b.legend(frameon=False, fontsize=9)
b.set_title(T("（b）权重量化的误差：逐张量与逐通道", "(b) Weight quantization error: per tensor vs per channel"), fontsize=10)
fig.tight_layout()
figure(fig, "fig8_3_1")
plt.close(fig)
