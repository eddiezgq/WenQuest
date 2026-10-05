"""8.5 节的示意图（数据同程序 8.5.1）。

图 8.5.1：（a）一批激活中各通道的最大绝对值：4 个离群通道比其余大约 50 倍（示意）；逐张量量化的比例由它们决定，
其余通道只用得上很少几个格点。（b）INT8 量化后矩阵乘积的相对误差：没有离群通道、有离群通道、LLM.int8()（离群通道走浮点）、
SmoothQuant（把激活的尺度按通道“搬”一部分到权重上）。
"""
import numpy as np

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
rng = np.random.default_rng(85)
ntok, dm, do = 512, 1024, 1024
X0 = rng.normal(0, 1, (ntok, dm))
W = rng.normal(0, 1, (dm, do)) / np.sqrt(dm)
out_ch = rng.choice(dm, 4, replace=False)
X = X0.copy()
X[:, out_ch] *= 50


def q8(x):
    s = np.abs(x).max() / 127
    return np.clip(np.round(x / s), -127, 127) * s


rel = lambda a, b: np.linalg.norm(a - b) / np.linalg.norm(b) * 100
big = np.abs(X).max(axis=0) > 6
s = np.abs(X).max(axis=0) ** 0.5 / np.abs(W).max(axis=1) ** 0.5
errs = [rel(q8(X0) @ q8(W), X0 @ W), rel(q8(X) @ q8(W), X @ W), rel(q8(X[:, ~big]) @ q8(W[~big]) + X[:, big] @ W[big], X @ W),
        rel(q8(X / s) @ q8(W * s[:, None]), X @ W)]
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 4.0), gridspec_kw={"width_ratios": [1.3, 1]})
a.bar(np.arange(dm), np.abs(X).max(axis=0), width=1.0, color=C["z"])
a.axhline(np.abs(X).max(), color=C["x"], ls="--", lw=1)
a.text(dm * 0.5, np.abs(X).max() * 0.92, T("逐张量量化的比例由离群通道决定", "the per-tensor scale is set by the outliers"), ha="center", fontsize=9, color=C["x"])
a.set_xlabel(T("通道", "channel"))
a.set_ylabel(T("最大绝对值", "max |x|"))
a.set_title(T("（a）激活各通道的最大绝对值（示意）", "(a) Per-channel max of the activations (illustrative)"), fontsize=10)
labels = [T("无离群", "no outliers"), T("有离群", "outliers"), "LLM.int8()", "SmoothQuant"]
b.bar(range(4), errs, color=[C["muted"], C["x"], C["y"], C["z"]], alpha=0.75)
for i, e in enumerate(errs):
    b.text(i, e * 1.03, f"{e:.1f}%", ha="center", fontsize=9)
b.set_ylim(0, max(errs) * 1.15)
b.set_xticks(range(4))
b.set_xticklabels(labels, fontsize=9)
b.set_ylabel(T("乘积的相对误差（%）", "relative error of the product (%)"))
b.set_title(T("（b）INT8 量化后矩阵乘积的误差", "(b) Error of the INT8 product"), fontsize=10)
fig.tight_layout()
figure(fig, "fig8_5_1")
plt.close(fig)
