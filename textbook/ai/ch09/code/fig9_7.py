"""9.7 节的示意图（数据同程序 9.7.1）。

图 9.7.1：（a）7B 模型在 A100 上解码，每生成一步的时间随批大小 b 的变化：读权重的时间（与 b 无关）与计算的时间（与 b 成正比），
取两者中较大的（不计读键值缓存）；批小时每个词元的成本主要是读权重，b 接近屋脊（约 150）以后才受算力限制。（b）键值缓存的分配：
按最大长度预先分配的连续缓存浪费的比例，与按 16 个词元一块分页分配的比例。
"""
import numpy as np

from _ch9 import A100, BIG, params
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N = params(BIG)
bs = np.logspace(0, 3, 200)
t_mem = 2 * N / A100["bw"] * 1e3 * np.ones_like(bs)
t_cmp = 2 * N * bs / A100["fp16t"] * 1e3
fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1.4, 1]})
a.plot(bs, np.maximum(t_mem, t_cmp), color=C["z"], lw=2, label=T("每一步的时间", "time per step"))
a.plot(bs, t_mem, color=C["muted"], ls="--", lw=1, label=T("读权重", "reading weights"))
a.plot(bs, t_cmp, color=C["x"], ls=":", lw=1, label=T("计算（峰值）", "compute (peak)"))
a.plot(bs, np.maximum(t_mem, t_cmp) / bs, color=C["y"], lw=2, label=T("每个词元的时间", "time per token"))
a.set_xscale("log")
a.set_yscale("log")
a.set_xlabel(T("同时解码的序列数 b", "concurrent sequences b"))
a.set_ylabel("ms")
a.legend(frameon=False, fontsize=8)
a.set_title(T("（a）7B 模型在 A100 上解码", "(a) Decoding a 7B model on an A100"), fontsize=10)
rng = np.random.default_rng(97)
lens = rng.integers(100, 2001, 10000)
w1 = 100 * (1 - lens.sum() / (len(lens) * 4096))
w2 = 100 * (1 - lens.sum() / (np.ceil(lens / 16) * 16).sum())
b.bar([0, 1], [w1, w2], color=[C["x"], C["z"]], alpha=0.7)
for i, v in enumerate([w1, w2]):
    b.text(i, v + 1.5, f"{v:.1f}%", ha="center", fontsize=9)
b.set_xticks([0, 1])
b.set_xticklabels([T("按最大长度连续分配", "contiguous, max length"), T("分页（每块 16 个词元）", "paged (16 tokens/block)")], fontsize=9)
b.set_ylabel(T("浪费的键值缓存（%）", "wasted KV cache (%)"))
b.set_ylim(0, 85)
b.set_title(T("（b）分页注意力", "(b) Paged attention"), fontsize=10)
fig.tight_layout()
figure(fig, "fig9_7_1")
plt.close(fig)
