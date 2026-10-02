"""图 39.6.1–39.6.2：数字工厂 SH-301 轴承位直径的检测数据（与算例 39.6.2、39.6.3 相同）。

图 39.6.1：判定与保护带示意。
图 39.6.2：(a) 连续 100 件的直径与公差带；(b) 均值控制图；(c) 极差控制图；(d) 每 14 件修整砂轮后的 100 件。
"""
import numpy as np

import ex39_6 as ex
from bookout import COLORS as C, T, figure, style

plt = style()
lo, hi, U = ex.SPEC_LO, ex.SPEC_HI, ex.U

# ---------------------------------------------------------------- 图 39.6.1 保护带
fig, ax = plt.subplots(figsize=(8.6, 2.5))
ax.axvspan(lo + U, hi - U, color=C["y"], alpha=0.15, lw=0)
for v in (lo, hi):
    ax.axvline(v, color=C["ink"], lw=1.4)
for v in (lo + U, hi - U):
    ax.axvline(v, color=C["y"], lw=1.2, ls="--")
ax.text((lo + hi) / 2 - 0.002, 0.86, T("接收区（判合格）", "Acceptance zone (accept)"), ha="center", fontsize=9.5, color=C["y"])
ax.text(lo - 0.0002, 0.97, T("下极限 L", "Lower limit L"), ha="right", fontsize=8.5)
ax.text(hi + 0.0002, 0.97, T("上极限 H", "Upper limit H"), ha="left", fontsize=8.5)
for x, txt in ((lo + U / 2, T("保护带\nU", "Guard band\nU")), (hi - U / 2, T("保护带\nU", "Guard band\nU"))):
    ax.text(x, 0.68, txt, ha="center", fontsize=8.5, color=C["x"], bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
cases = [(35.0100, T("明显合格", "Clearly conforming"), -1), (35.0163, T("在公差内，但真值可能超差：\n判不合格", "In tolerance, but true value\nmay be out: rejected"), 1), (35.0200, T("超差", "Out of tolerance"), -1)]
for x, txt, side in cases:
    y = 0.25
    ax.errorbar(x, y, xerr=U, fmt="o", color=C["z"], capsize=4, ms=5)
    ax.text(x, y + 0.13 * side, txt, ha="center", va="top" if side < 0 else "bottom", fontsize=8.5, bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
ax.set_xlim(lo - 0.004, hi + 0.004)
ax.set_ylim(-0.1, 1.05)
ax.set_xticks([lo, ex.NOMINAL, hi])
ax.set_xticklabels([f"{v:.3f}" for v in (lo, ex.NOMINAL, hi)], fontsize=9)
ax.set_yticks([])
ax.set_xlabel(T("直径 / mm（点：测得值；短线：± U）", "Diameter / mm (dot: measured value; bar: ± U)"))
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
figure(fig, "fig39_6_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 39.6.2 控制图
x, x2 = np.array(ex.x), np.array(ex.x2)
xbar, R, xbar2 = np.array(ex.xbar), np.array(ex.R) * 1000, np.array(ex.xbar2)
g = np.arange(1, xbar.size + 1)
sig = [s for s, _ in ex.sig]
fig, axs = plt.subplots(2, 2, figsize=(10.5, 6.2))
(a, b), (c, d) = axs


def parts(ax, y, title):
    n = np.arange(1, y.size + 1)
    bad = (y < lo) | (y > hi)
    ax.axhspan(lo, hi, color=C["y"], alpha=0.10, lw=0)
    for v in (lo, hi):
        ax.axhline(v, color=C["ink"], lw=1)
    ax.axhline(ex.NOMINAL, color=C["muted"], lw=0.7, ls=":")
    ax.plot(n, y, ".-", color=C["z"], lw=0.6, ms=4)
    ax.plot(n[bad], y[bad], "o", mfc="none", color=C["x"], ms=9, mew=1.5)
    ax.set_ylim(lo - 0.003, hi + 0.003)
    ax.set_xlabel(T("零件序号", "Part number"))
    ax.set_ylabel(T("直径 / mm", "Diameter / mm"))
    ax.set_title(title, fontsize=10.5)


parts(a, x, T(f"(a) 原工艺：连续 100 件，{ex.n_out} 件超差（红圈）", f"(a) Original process: 100 consecutive parts, {ex.n_out} out of tolerance (red circles)"))
parts(d, x2, T(f"(d) 每 14 件修整砂轮：{ex.n_out2} 件超差", f"(d) Wheel dressed every 14 parts: {ex.n_out2} out of tolerance"))
b.plot(g, xbar, "o-", color=C["z"], ms=4, lw=1)
b.plot(np.array(sig), xbar[np.array(sig) - 1], "o", mfc="none", color=C["x"], ms=10, mew=1.5)
for v, ls in ((ex.xbb, "-"), (ex.ucl, "--"), (ex.lcl, "--")):
    b.axhline(v, color=C["ink"], lw=0.9, ls=ls)
b.text(g[-1] + 0.4, ex.ucl, "UCL", va="bottom", fontsize=8.5)
b.text(g[-1] + 0.4, ex.lcl, "LCL", va="bottom", fontsize=8.5)
b.set_xlabel(T("组号（每组 5 件）", "Subgroup (5 parts each)"))
b.set_ylabel(T("组均值 / mm", "Subgroup mean / mm"))
b.set_title(T("(b) 均值控制图（事后分析；红圈：判异）", "(b) $\\bar{x}$ chart (retrospective; red circles: signals)"), fontsize=10.5)
c.plot(g, R, "o-", color=C["z"], ms=4, lw=1)
c.axhline(ex.Rbar * 1000, color=C["ink"], lw=0.9)
c.axhline(ex.r_ucl * 1000, color=C["ink"], lw=0.9, ls="--")
c.text(g[-1] + 0.4, ex.r_ucl * 1000, "UCL", va="bottom", fontsize=8.5)
c.set_xlabel(T("组号（每组 5 件）", "Subgroup (5 parts each)"))
c.set_ylabel(T("组极差 / μm", "Subgroup range / μm"))
c.set_title(T("(c) 极差控制图", "(c) R chart"), fontsize=10.5)
for ax in axs.ravel():
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig39_6_2")
plt.close(fig)
