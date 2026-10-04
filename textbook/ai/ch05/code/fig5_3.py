"""5.3 节的示意图。

图 5.3.1：8 个数的两种并行扫描。（a）希利斯—斯蒂尔：第 d 步每个位置加上左边相隔 d 的位置，3 步，17 次加法；
（b）布莱洛赫：上扫建出一棵和树（7 次加法），把最后一个位置置零，下扫把前缀分发下去（7 次加法与交换），6 步，得到排他前缀和。
"""
import numpy as np

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
x = [3, 1, 4, 1, 5, 9, 2, 6]
n = len(x)
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 5.2), gridspec_kw={"width_ratios": [1, 1.25]})


def row(ax, vals, y, hl=(), fc=None):
    for i, v in enumerate(vals):
        ax.add_patch(plt.Rectangle((i, y - 0.3), 0.86, 0.6, fc=fc or (C["z"] if i in hl else "#e6e9ec"), alpha=0.55 if i in hl else 1, ec="white"))
        ax.text(i + 0.43, y, str(v), ha="center", va="center", fontsize=10)


def arrow(ax, i, j, y0, y1, color):
    ax.annotate("", xy=(j + 0.43, y1 + 0.3), xytext=(i + 0.43, y0 - 0.3), arrowprops=dict(arrowstyle="-|>", color=color, lw=1))


# (a) Hillis–Steele
v = list(x)
row(a, v, 0)
d, y = 1, 0
while d < n:
    new = [v[i] + (v[i - d] if i >= d else 0) for i in range(n)]
    for i in range(d, n):
        arrow(a, i - d, i, y, y - 1, C["accent"])
        arrow(a, i, i, y, y - 1, C["muted"])
    y -= 1
    row(a, new, y, hl=range(d, n))
    a.text(n + 0.2, y, f"d = {d}", fontsize=9, va="center")
    v, d = new, 2 * d
a.set_xlim(-0.2, n + 1.2)
a.set_ylim(y - 0.6, 0.6)
a.axis("off")
a.set_title(T("（a）希利斯—斯蒂尔：3 步，17 次加法（包含式）", "(a) Hillis–Steele: 3 steps, 17 adds (inclusive)"), fontsize=10)

# (b) Blelloch
v = list(x)
row(b, v, 0)
y, d = 0, 1
while d < n:                                         # 上扫
    new = list(v)
    for k in range(0, n, 2 * d):
        new[k + 2 * d - 1] = v[k + 2 * d - 1] + v[k + d - 1]
        arrow(b, k + d - 1, k + 2 * d - 1, y, y - 1, C["accent"])
    y -= 1
    row(b, new, y, hl=[k + 2 * d - 1 for k in range(0, n, 2 * d)])
    b.text(n + 0.2, y, T(f"上扫 d = {d}", f"up-sweep d = {d}"), fontsize=9, va="center")
    v, d = new, 2 * d
v[n - 1] = 0
y -= 1
row(b, v, y, hl=[n - 1], fc=None)
b.text(n + 0.2, y, T("末位置零", "clear last"), fontsize=9, va="center")
d = n // 2
while d >= 1:                                        # 下扫
    new = list(v)
    for k in range(0, n, 2 * d):
        l, r = k + d - 1, k + 2 * d - 1
        new[l], new[r] = v[r], v[r] + v[l]
        arrow(b, r, l, y, y - 1, C["y"])
        arrow(b, l, r, y, y - 1, C["accent"])
    y -= 1
    row(b, new, y, hl=[k + d - 1 for k in range(0, n, 2 * d)] + [k + 2 * d - 1 for k in range(0, n, 2 * d)])
    b.text(n + 0.2, y, T(f"下扫 d = {d}", f"down-sweep d = {d}"), fontsize=9, va="center")
    v, d = new, d // 2
assert v == list(np.cumsum(x) - np.array(x))
b.set_xlim(-0.2, n + 2.2)
b.set_ylim(y - 0.6, 0.6)
b.axis("off")
b.set_title(T("（b）布莱洛赫：上扫 + 下扫，6 步，14 次加法（排他式）", "(b) Blelloch: up- and down-sweep, 6 steps, 14 adds (exclusive)"), fontsize=10)
fig.tight_layout()
figure(fig, "fig5_3_1")
plt.close(fig)
