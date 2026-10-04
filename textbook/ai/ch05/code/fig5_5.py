"""5.5 节的示意图。

图 5.5.1：im2col。（a）4×4 的单通道输入、3×3 的卷积核、不补零，得到 2×2 个输出，每个输出用到一个 3×3 的窗口（四种颜色）；
（b）把每个窗口的 9 个数排成一列，得到 9×4 的矩阵；卷积核排成 1×9 的一行，卷积就成了一次矩阵乘法 (1×9)×(9×4)。
输入中每个数在矩阵里出现的次数等于覆盖它的窗口数，中间的 4 个数各出现 4 次。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
cols = [C["x"], C["z"], C["y"], C["accent"]]
fig, (a, b) = plt.subplots(1, 2, figsize=(11.5, 4.6), gridspec_kw={"width_ratios": [1, 1.5]})
vals = [[4 * r + c + 1 for c in range(4)] for r in range(4)]
for r in range(4):
    for c in range(4):
        a.add_patch(plt.Rectangle((c, r), 1, 1, fc="#f2f4f6", ec=C["muted"], lw=0.8))
        a.text(c + 0.5, r + 0.5, str(vals[r][c]), ha="center", va="center", fontsize=12)
for k, (r0, c0) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):
    off = 0.06 * (k + 1)
    a.add_patch(plt.Rectangle((c0 + off, r0 + off), 3 - 2 * off, 3 - 2 * off, fill=False, ec=cols[k], lw=2))
a.set_xlim(-0.2, 4.2)
a.set_ylim(4.2, -0.2)
a.set_aspect("equal")
a.axis("off")
a.set_title(T("（a）4×4 输入上的四个 3×3 窗口", "(a) Four 3×3 windows on a 4×4 input"), fontsize=10)
for k, (r0, c0) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):
    for i in range(9):
        v = vals[r0 + i // 3][c0 + i % 3]
        b.add_patch(plt.Rectangle((k + 3, i), 1, 1, fc=cols[k], alpha=0.25, ec="white"))
        b.text(k + 3.5, i + 0.5, str(v), ha="center", va="center", fontsize=10)
for i in range(9):
    b.add_patch(plt.Rectangle((0.5, i), 1, 1, fc="#d9dee3", ec="white"))
    b.text(1.0, i + 0.5, f"w{i // 3}{i % 3}", ha="center", va="center", fontsize=9)
b.text(2.25, 4.5, "×", ha="center", va="center", fontsize=18)
b.text(1.0, 9.8, T("卷积核", "kernel"), ha="center", va="center", fontsize=9)
b.text(5.0, 9.8, T("im2col 矩阵：每列一个窗口", "im2col matrix: one window per column"), ha="center", va="center", fontsize=9)
b.set_xlim(0, 7.5)
b.set_ylim(10.4, -0.4)
b.set_aspect("equal")
b.axis("off")
b.set_title(T("（b）展开成矩阵：卷积 = (1×9)·(9×4)", "(b) Unrolled: convolution = (1×9)·(9×4)"), fontsize=10)
fig.tight_layout()
figure(fig, "fig5_5_1")
plt.close(fig)
