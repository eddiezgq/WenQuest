"""M1.3 节的示意图。

图 M1.3.1：同一批零件、同一个"最近邻"问题，在原始数据与标准化数据上，各项对距离的贡献完全不同：
左边几乎全是圆度（因为它按微米记，数值的波动最大），右边五项各占一份。
"""
import numpy as np

from _chM1 import FEATURES, FEATURES_EN, parts, standardize
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
X = parts()
Z, _, _ = standardize(X)
raw = ((X - X[0]) ** 2).sum(0)
std = ((Z - Z[0]) ** 2).sum(0)
raw, std = raw / raw.sum() * 100, std / std.sum() * 100
names = [T(a, b) for a, b in zip(FEATURES, FEATURES_EN)]

fig, (a, b) = plt.subplots(1, 2, figsize=(11.0, 3.8))
for ax, val, ttl in ((a, raw, T("(a) 原始数据", "(a) raw data")), (b, std, T("(b) 按列标准化后", "(b) standardized"))):
    ax.barh(names, val, color=[C["x"] if v == max(val) else C["z"] for v in val], height=0.6)
    for i, v_ in enumerate(val):
        ax.text(v_ + 1.5, i, f"{v_:.1f}%", va="center", fontsize=9, color=C["ink"])
    ax.set_xlim(0, 112)
    ax.set_xlabel(T("对距离平方的贡献（%）", "share of squared distance (%)"))
    ax.set_title(ttl, fontsize=10)
    ax.grid(axis="x", alpha=0.25, lw=0.5)
    ax.invert_yaxis()
fig.tight_layout()
figure(fig, "figM1_3_1")
