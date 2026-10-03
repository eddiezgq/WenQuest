"""3.8 节的示意图。

图 3.8.1：H100（FP16 张量核心 989.4 TFLOP/s，3.35 TB/s）的屋顶线，与小型 Transformer 各层、一个 3×3 卷积层、
大模型逐词生成时的线性层的位置（数据同程序 3.8.1）。
图 3.8.2：几种 GPU 的屋顶线（FP16 张量核心）。
"""
import runpy
from pathlib import Path

import numpy as np

import bookout
from bookout import COLORS, T, figure, style
from gpus import GPUS

plt = style()
C = COLORS
saved = bookout.out
v = {}
bookout.out = lambda **kw: v.update(kw)
runpy.run_path(str(Path(__file__).with_name("ex3_8.py")))
bookout.out = saved

I = np.logspace(-1.3, 3.5, 400)
P, bw = v["P_T"], v["bw_T"]
fig, ax = plt.subplots(figsize=(9.4, 5.2))
ax.loglog(I, np.minimum(P, bw * I), color=C["ink"], lw=2)
ax.axvline(v["ridge"], color=C["muted"], lw=0.8, ls=":")
ax.text(v["ridge"] * 1.08, 1.4, T(f"平衡点\n{v['ridge']:.0f} FLOP/B", f"ridge\n{v['ridge']:.0f} FLOP/B"), fontsize=8.8, color=C["muted"])
ax.text(0.07, bw * 0.07 * 1.9, T("受带宽限制：P = βI", "bandwidth-bound: P = βI"), rotation=33, fontsize=9, color=C["ink"])
ax.text(2000, P * 1.25, T("受算力限制", "compute-bound"), fontsize=9, color=C["ink"], ha="center")
names = {"QKV": "QKV", "proj": T("输出投影", "out proj"), "FF1": "FF1", "FF2": "FF2", "logits": T("输出层", "logits"),
         "QKT": "QKᵀ", "softmax": "softmax", "LN": T("层归一化", "LayerNorm"), "GELU": "GELU", "add": T("残差加法", "residual"),
         "conv3x3": T("3×3 卷积", "3×3 conv"), "decode": T("逐词生成\n（B = 1）", "decoding\n(B = 1)")}
pos = {"QKV": (40, 2000), "proj": (25, 330), "FF1": (900, 420), "FF2": (900, 260), "logits": (900, 160),
       "QKT": (60, 60), "softmax": (0.35, 15), "LN": (6, 3), "GELU": (6, 12), "add": (0.3, 0.25),
       "conv3x3": (60, 1100), "decode": (0.25, 3.5)}
for k, name in names.items():
    x, y = v[f"I_{k}"], v[f"T_{k}"]
    col = C["z"] if k in ("QKV", "proj", "FF1", "FF2", "logits", "QKT") else (C["y"] if k == "conv3x3" else (C["x"] if k == "decode" else C["accent"]))
    ax.plot(x, y, "o", color=col, ms=6, zorder=3)
    ax.annotate(name, xy=(x, y), xytext=pos[k], fontsize=8.4, color=col, va="center",
                arrowprops=dict(arrowstyle="-", color=col, lw=0.6, shrinkA=1, shrinkB=3))
ax.set_xlabel(T("计算强度 I（FLOP/B）", "arithmetic intensity I (FLOP/B)"))
ax.set_ylabel(T("可达到的算力（TFLOP/s）", "attainable performance (TFLOP/s)"))
ax.set_ylim(0.1, 4000)
ax.set_xlim(0.05, 3000)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig3_8_1")
plt.close(fig)

fig, ax = plt.subplots(figsize=(8.4, 4.6))
for key, col in (("v100", C["muted"]), ("a100", C["y"]), ("rtx4090", C["accent"]), ("h100", C["z"]), ("b200", C["x"])):
    g = GPUS[key]
    Pg, bg = g["fp16t"] / 1e12, g["bw"] / 1e12
    ax.loglog(I, np.minimum(Pg, bg * I), color=col, lw=1.8, label=T(f"{g['name']}（{Pg:g} TFLOP/s，{bg:g} TB/s）", f"{g['name']} ({Pg:g} TFLOP/s, {bg:g} TB/s)"))
    ax.plot(Pg / bg, Pg, "o", color=col, ms=4)
ax.set_xlabel(T("计算强度 I（FLOP/B）", "arithmetic intensity I (FLOP/B)"))
ax.set_ylabel(T("可达到的算力（TFLOP/s）", "attainable performance (TFLOP/s)"))
ax.set_ylim(1, 5000)
ax.set_xlim(0.5, 3000)
ax.legend(fontsize=8.4, frameon=False, loc="lower right")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig3_8_2")
plt.close(fig)
