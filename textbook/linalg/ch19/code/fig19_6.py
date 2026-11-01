"""图 19.6.1：霍特林 T² 图。(a) 温升与振动（标准化）：两张单变量图的控制区域是正方形，T² 的是椭圆；
灰点为第一阶段 200 件，蓝点为第二阶段第 1–30 件，红点为第 31–60 件（用错了润滑油）；
(b) 第二阶段 60 件的 T² 与控制限；(c) 温升、噪声、振动三张单变量图（±3 倍标准差）。
图 19.6.2：(a) 第 35 件与第 31–60 件平均的变量贡献；(b) 基于前 3 个主成分的 T²ₖ 与 SPE（Q 统计量）。"""
import math

import numpy as np
from scipy import stats

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from _num import fix_sign
from _qc import N_I, N_II, SHORT, SHORT_EN, START_II, X_I, X_II

p, alpha = 6, 0.0027
m = X_I.mean(axis=0)
S = np.cov(X_I.T)
s = np.sqrt(np.diag(S))
Si = np.linalg.inv(S)
ucl = p * (N_I + 1) * (N_I - 1) / (N_I * (N_I - p)) * stats.f.ppf(1 - alpha, p, N_I - p)
D = X_II - m
T2 = np.einsum("ij,jk,ik->i", D, Si, D)
Z1 = (X_I - m) / s
Z2 = D / s
idx = np.arange(1, N_II + 1)
bad = idx > START_II

fig = plt.figure(figsize=(13.0, 7.2))
gs = fig.add_gridspec(3, 2, width_ratios=[1, 1.5])
a1 = fig.add_subplot(gs[:, 0])
i, j = 3, 4
R = np.corrcoef(X_I.T)
r = R[i, j]
a1.scatter(Z1[:, i], Z1[:, j], s=7, color=MUTED, alpha=0.5, lw=0)
a1.scatter(Z2[~bad, i], Z2[~bad, j], s=16, color=BLUE)
a1.scatter(Z2[bad, i], Z2[bad, j], s=16, color=RED)
a1.add_patch(plt.Rectangle((-3, -3), 6, 6, fill=False, ec=INK, lw=1.2, ls="--"))
# 两个变量时的 99.73% 椭圆：zᵀR₂⁻¹z = χ²₂(0.9973)
R2 = R[np.ix_([i, j], [i, j])]
w2, V2 = np.linalg.eigh(R2)
c2 = stats.chi2.ppf(1 - alpha, 2)
t = np.linspace(0, 2 * np.pi, 300)
El = V2 @ np.vstack([np.sqrt(c2 * w2[0]) * np.cos(t), np.sqrt(c2 * w2[1]) * np.sin(t)])
a1.plot(El[0], El[1], color=GREEN, lw=2)
a1.text(-3.9, 3.15, T("单变量图：正方形 |z| ≤ 3", "univariate charts: square |z| ≤ 3"), fontsize=9, color=INK)
a1.text(0.6, -3.6, T(f"两个变量的 T² 椭圆（r = {r:.2f}）", f"two-variable T² ellipse (r = {r:.2f})"), fontsize=9, color=GREEN)
a1.set_aspect("equal")
a1.set_xlim(-4.2, 5.2)
a1.set_ylim(-4.0, 4.0)
a1.set_xlabel(T("温升（标准化）", "temperature rise (standardized)"))
a1.set_ylabel(T("振动（标准化）", "vibration (standardized)"))
a1.set_title(T("(a) 正方形与椭圆", "(a) Square versus ellipse"), fontsize=11)
for sp in ("top", "right"):
    a1.spines[sp].set_visible(False)

a2 = fig.add_subplot(gs[0, 1])
a2.plot(idx, T2, "-", color=MUTED, lw=0.8)
a2.plot(idx[T2 <= ucl], T2[T2 <= ucl], "o", color=BLUE, ms=4)
a2.plot(idx[T2 > ucl], T2[T2 > ucl], "o", color=RED, ms=5)
a2.axhline(ucl, color=RED, lw=1, ls="--")
a2.text(1, ucl + 3, f"UCL = {ucl:.1f}", color=RED, fontsize=9)
a2.axvline(START_II + 0.5, color=ACC, lw=1)
a2.text(START_II + 1, 55, T("第 31 件起用错了润滑油", "wrong oil from unit 31"), color=ACC, fontsize=9)
a2.set_ylabel("T²")
a2.set_xlim(0, N_II + 1)
a2.set_title(T(f"(b) T² 图：后 30 件报警 {int(np.sum(T2[bad] > ucl))} 件", f"(b) T² chart: {int(np.sum(T2[bad] > ucl))} alarms in the last 30"), fontsize=11)
names = T(SHORT, SHORT_EN)
a3 = fig.add_subplot(gs[1:, 1], sharex=a2)
for row, (jj, col) in enumerate(((3, RED), (2, GREEN), (4, BLUE))):
    off = 8 * (1 - row)
    a3.axhline(off, color=MUTED, lw=0.5)
    a3.axhline(off + 3, color=col, lw=0.6, ls=":")
    a3.axhline(off - 3, color=col, lw=0.6, ls=":")
    z = Z2[:, jj]
    a3.plot(idx, off + z, "-o", color=col, ms=3, lw=0.8)
    out_ = np.abs(z) > 3
    a3.plot(idx[out_], off + z[out_], "o", mfc="none", mec=INK, ms=8)
    a3.text(N_II + 1.5, off, names[jj], color=col, fontsize=10, va="center")
a3.axvline(START_II + 0.5, color=ACC, lw=1)
a3.set_yticks([])
a3.set_xlabel(T("第二阶段的产品序号", "unit number (phase II)"))
nind = int(np.sum((np.abs(Z2[bad]) > 3).any(axis=1)))
a3.set_title(T(f"(c) 单变量图（±3σ，圈出的是超限点）：后 30 件中只有 {nind} 件有项目超限", f"(c) Univariate charts (±3σ; circled: out of limits): only {nind} of the last 30 flagged"), fontsize=11)
for a in (a2, a3):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig19_6_1")

# 图 19.6.2
u = 34
cu = D[u] * (Si @ D[u])
cb = (D[bad] * (D[bad] @ Si)).mean(axis=0)
w, V = np.linalg.eigh(Z1.T @ Z1 / (N_I - 1))
w, V = w[::-1], fix_sign(V[:, ::-1])
k = 3
Tk = Z2 @ V[:, :k]
T2k = np.sum(Tk ** 2 / w[:k], axis=1)
spe = np.sum((Z2 - Tk @ V[:, :k].T) ** 2, axis=1)
ucl_k = k * (N_I + 1) * (N_I - 1) / (N_I * (N_I - k)) * stats.f.ppf(1 - alpha, k, N_I - k)
th1, th2, th3 = (np.sum(w[k:] ** q) for q in (1, 2, 3))
h0 = 1 - 2 * th1 * th3 / (3 * th2 ** 2)
za = stats.norm.ppf(1 - alpha)
spe_lim = th1 * (za * math.sqrt(2 * th2 * h0 ** 2) / th1 + 1 + th2 * h0 * (h0 - 1) / th1 ** 2) ** (1 / h0)
fig, (b1, b2) = plt.subplots(1, 2, figsize=(12.0, 4.2), gridspec_kw={"width_ratios": [1, 1.5]})
x = np.arange(6)
b1.bar(x - 0.2, cu, width=0.38, color=RED, label=T(f"第 {u + 1} 件（T² = {T2[u]:.1f}）", f"unit {u + 1} (T² = {T2[u]:.1f})"))
b1.bar(x + 0.2, cb, width=0.38, color=ACC, label=T("第 31–60 件的平均", "mean over units 31–60"))
b1.axhline(0, color=INK, lw=0.6)
b1.set_xticks(x)
b1.set_xticklabels(names)
b1.set_ylabel(T("贡献 cⱼ = dⱼ(S⁻¹d)ⱼ", "contribution cⱼ = dⱼ(S⁻¹d)ⱼ"))
b1.legend(frameon=False, fontsize=9)
b1.set_title(T("(a) 变量贡献：温升偏高、振动却不高", "(a) Contributions: hot but not vibrating"), fontsize=11)
b2.plot(idx, T2k / ucl_k, "-o", color=BLUE, ms=3.5, lw=0.8, label=T(f"T²ₖ / 控制限（k = {k}）", f"T²ₖ / limit (k = {k})"))
b2.plot(idx, spe / spe_lim, "-s", color=RED, ms=3.5, lw=0.8, label=T("SPE / 控制限", "SPE / limit"))
b2.axhline(1, color=INK, lw=0.8, ls="--")
b2.axvline(START_II + 0.5, color=ACC, lw=1)
b2.set_xlabel(T("第二阶段的产品序号", "unit number (phase II)"))
b2.set_ylabel(T("统计量 / 控制限", "statistic / limit"))
b2.legend(frameon=False, fontsize=9, loc="upper left")
b2.set_title(T(f"(b) 故障落在残差子空间：SPE 报警 {int(np.sum(spe[bad] > spe_lim))} 件，T²ₖ 一件也没有",
               f"(b) Fault in the residual subspace: SPE flags {int(np.sum(spe[bad] > spe_lim))}, T²ₖ none"), fontsize=11)
for a in (b1, b2):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig19_6_2")
