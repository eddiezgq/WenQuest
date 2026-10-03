"""图 2.7.1：8 个采样值组成的振动信号就是 R⁸ 中的一个向量。
图 2.7.2：八份检测记录与三种故障特征方向的余弦相似度（左），以及各记录标准化后的长度（右）。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from ex2_7_data import FAULTS, FAULTS_EN, RECORDS, cos, z

t = np.arange(8) * 1e-3
x = np.round(2.0 * np.sin(2 * math.pi * 125 * t) + 0.5 * np.sin(2 * math.pi * 250 * t), 2)
tt = np.linspace(0, 8e-3, 400)
fig, ax = plt.subplots(figsize=(8.0, 3.2))
ax.plot(tt * 1e3, 2.0 * np.sin(2 * math.pi * 125 * tt) + 0.5 * np.sin(2 * math.pi * 250 * tt), color=MUTED, lw=1)
ax.vlines(t * 1e3, 0, x, color=BLUE, lw=2)
ax.plot(t * 1e3, x, "o", color=BLUE)
for k in range(8):
    ax.text(t[k] * 1e3, x[k] + (0.25 if x[k] >= 0 else -0.45), f"$x_{k + 1}$", ha="center", fontsize=11)
ax.axhline(0, color=INK, lw=0.6)
ax.set_xlabel(T("时间 / ms", "time / ms"))
ax.set_ylabel(T("加速度 / (m/s²)", "acceleration / (m/s²)"))
ax.set_ylim(-2.8, 2.8)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig2_7_1")

names = list(FAULTS)
S = np.array([[cos(z(r), FAULTS[f]) for f in names] for r in RECORDS])
nr = np.linalg.norm(np.array([z(r) for r in RECORDS]), axis=1)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.4), gridspec_kw={"width_ratios": [1.3, 1]})
im = a1.imshow(S, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
for i in range(S.shape[0]):
    for j in range(S.shape[1]):
        a1.text(j, i, f"{S[i, j]:.2f}", ha="center", va="center", fontsize=10, color="white" if abs(S[i, j]) > 0.6 else INK)
a1.set_xticks(range(3), [T(f, FAULTS_EN[f]) for f in names])
a1.set_yticks(range(8), [T(f"记录 {i + 1}", f"record {i + 1}") for i in range(8)])
a1.set_title(T("余弦相似度", "cosine similarity"), fontsize=11)
fig.colorbar(im, ax=a1, fraction=0.05)
a2.barh(range(8), nr, color=[RED if v > 2.5 else MUTED for v in nr])
a2.axvline(2.5, color=INK, ls="--", lw=0.9)
a2.text(2.6, 7.4, T("2.5：报警线", "2.5: alarm line"), fontsize=9)
a2.set_yticks(range(8), [T(f"记录 {i + 1}", f"record {i + 1}") for i in range(8)])
a2.invert_yaxis()
a2.set_xlabel(T("标准化后的长度 ‖z‖", "standardized length ‖z‖"))
a2.set_title(T("偏离程度", "how far off"), fontsize=11)
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig2_7_2")
