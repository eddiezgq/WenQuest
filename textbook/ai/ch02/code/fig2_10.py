"""2.10 节的示意图。

图 2.10.1：小型 Transformer 一次前向计算（B = 32，T = 256，半精度）中，六类运算各占浮点运算量、数据搬运量
和按 H100 估计的耗时下限的百分比。
"""
import runpy
from pathlib import Path

import numpy as np

import bookout
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

# 复用程序 2.10.1 的统计（运行它，但不让它把数交给正文）
saved = bookout.out
vals = {}
bookout.out = lambda **kw: vals.update(kw)
runpy.run_path(str(Path(__file__).with_name("ex2_10.py")))
bookout.out = saved

keys = ["linear", "attn", "softmax", "norm", "gelu", "add"]
names = [T("线性层", "linear"), T("注意力矩阵乘", "attention matmuls"), "softmax", T("层归一化", "LayerNorm"), "GELU",
         T("残差加法", "residual add")]
W = np.array([vals[f"{k}_Wp"] for k in keys])
Q = np.array([vals[f"{k}_Qp"] for k in keys])
Tm = np.array([vals[f"{k}_tp"] for k in keys])
fig, ax = plt.subplots(figsize=(9.6, 4.0))
x = np.arange(len(keys))
w = 0.27
for off, arr, col, lab in ((-w, W, C["z"], T("浮点运算量", "FLOPs")), (0, Q, C["x"], T("数据搬运量", "bytes moved")),
                           (w, Tm, C["accent"], T("耗时下限（H100）", "time lower bound (H100)"))):
    b = ax.bar(x + off, arr, w, color=col, label=lab)
    for bb, v in zip(b, arr):
        ax.text(bb.get_x() + bb.get_width() / 2, v + 1.2, f"{v:.1f}" if v >= 1 else f"{v:.2f}", ha="center", fontsize=7.6,
                color=C["ink"], rotation=90 if v < 1 else 0)
ax.set_xticks(x)
ax.set_xticklabels(names, fontsize=9.5)
ax.set_ylabel(T("占全部的百分比（%）", "share of the total (%)"))
ax.set_ylim(0, 100)
ax.legend(fontsize=9, frameon=False, loc="upper right")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig2_10_1")
plt.close(fig)
