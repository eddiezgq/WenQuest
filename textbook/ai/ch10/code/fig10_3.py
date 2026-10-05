"""10.3 节的示意图（结构同 CANN 官方文档，数据同程序 10.3.1）。

图 10.3.1：（a）达芬奇架构 AI Core 的结构与一次矩阵乘法的数据流：显存 → L1 → L0A/L0B → 立方单元 → L0C（单精度累加）
→ 统一缓冲区 → 显存；向量单元在统一缓冲区上做逐元素运算，标量单元管循环、分支并调度各单元的流水线。
（b）CopyIn → Compute → CopyOut 三段流水：n 个数据块流完要 n + 2 段，而不是 3n 段（算例 10.3.2）。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, (a, b) = plt.subplots(1, 2, figsize=(12.6, 4.3), gridspec_kw={"width_ratios": [1.15, 1]})


def box(ax, x, y, w, h, text, col, alpha=0.55, fs=8.5):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=col, alpha=alpha, ec=col, lw=0.8))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=C["ink"])


def arrow(ax, x0, y0, x1, y1, text="", fs=7.5):
    ax.annotate("", (x1, y1), (x0, y0), arrowprops=dict(arrowstyle="-|>", lw=0.9, color=C["muted"]))
    if text:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.08, text, ha="center", fontsize=fs, color=C["muted"])


# ---------- (a) AI Core 的结构
box(a, 0.1, 3.3, 2.0, 0.55, T("显存（Global Memory）", "Global Memory"), C["muted"], 0.3)
box(a, 0.1, 2.4, 2.0, 0.5, T("L1 缓冲", "L1 buffer"), C["z"], 0.35)
box(a, 0.1, 1.5, 0.92, 0.5, "L0A", C["z"])
box(a, 1.18, 1.5, 0.92, 0.5, "L0B", C["z"])
box(a, 0.1, 0.6, 2.0, 0.55, T("立方单元 16×16×16", "Cube unit 16×16×16"), C["x"])
box(a, 0.1, -0.3, 2.0, 0.5, T("L0C（FP32 累加）", "L0C (FP32 accum.)"), C["z"], 0.35)
box(a, 2.6, 1.5, 1.9, 0.5, T("统一缓冲区 UB", "Unified Buffer"), C["z"], 0.35)
box(a, 2.6, 0.6, 1.9, 0.55, T("向量单元", "Vector unit"), C["y"])
box(a, 2.6, 2.4, 1.9, 0.5, T("标量单元（调度）", "Scalar unit (control)"), C["accent"], 0.4)
arrow(a, 1.1, 3.3, 1.1, 2.9)
arrow(a, 1.1, 2.4, 1.1, 2.0)
arrow(a, 1.1, 1.5, 1.1, 1.15)
arrow(a, 1.1, 0.6, 1.1, 0.2)
arrow(a, 2.1, 0.0, 2.6, 0.85)
arrow(a, 3.55, 1.15, 3.55, 1.5)
arrow(a, 3.55, 2.0, 3.55, 2.4)
arrow(a, 4.5, 1.75, 5.0, 1.75)
a.text(5.05, 1.75, T("→ 显存", "→ memory"), fontsize=8, va="center", color=C["muted"])
a.set_xlim(-0.2, 6.2)
a.set_ylim(-0.6, 4.1)
a.axis("off")
a.set_title(T("(a) AI Core 的结构与数据流", "(a) Inside one AI Core"), fontsize=10)

# ---------- (b) 三段流水
N, cols = 6, [C["z"], C["x"], C["y"]]
names = [T("搬入", "CopyIn"), T("计算", "Compute"), T("搬出", "CopyOut")]
for i in range(N):
    for s in range(3):
        b.add_patch(plt.Rectangle((i + s, N - 1 - i), 0.92, 0.8, fc=cols[s], alpha=0.6, ec="none"))
        if i == 0:
            b.text(s + 0.46, N - 0.6 + 0.9, names[s], ha="center", fontsize=8, color=cols[s])
    b.text(-0.2, N - 1 - i + 0.4, T(f"第 {i + 1} 块", f"tile {i + 1}"), ha="right", va="center", fontsize=8)
b.plot([0, N + 2], [-0.45, -0.45], lw=0.8, color=C["muted"])
b.text((N + 2) / 2, -1.0, T(f"总共 {N} + 2 = {N + 2} 段（各段串行要 {3 * N} 段）",
                           f"{N} + 2 = {N + 2} stages in all ({3 * N} if serial)"), ha="center", fontsize=8.5, color=C["ink"])
b.set_xlim(-1.6, N + 2.4)
b.set_ylim(-1.4, N + 0.9)
b.axis("off")
b.set_title(T("(b) 三段流水：不同数据块重叠进行", "(b) Three-stage pipeline over tiles"), fontsize=10)

fig.tight_layout()
figure(fig, "fig10_3_1")
