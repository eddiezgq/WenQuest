"""7.4 节的示意图（配置同程序 7.4.1）。

图 7.4.1：CUTLASS 矩阵乘法的分块层次。（a）线程块负责 C 的 128×128 块，分给 4 个线程束，各 64×64；
（b）一个线程束的 64×64 再分成 4×8 个 16×8 的小块，每块是一条张量核心指令 mma.m16n8k16 的输出；
（c）一条指令的 16×8 个输出分在 32 个线程的寄存器里：第 t 个线程拿第 ⌊t/4⌋ 与 ⌊t/4⌋+8 行、第 2(t mod 4) 与 2(t mod 4)+1 列，共 4 个数
（PTX 文档规定的片段布局）。每一层都是一个“布局”：坐标到线程、到寄存器的映射。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, (a, b, c) = plt.subplots(1, 3, figsize=(13, 4.6), gridspec_kw={"width_ratios": [1, 1, 1.15]})
for i in range(2):
    for j in range(2):
        a.add_patch(plt.Rectangle((j * 64, i * 64), 64, 64, fc=C["z"] if (i, j) == (0, 0) else C["muted"], alpha=0.45 if (i, j) == (0, 0) else 0.15, ec=C["ink"], lw=1))
        a.text(j * 64 + 32, i * 64 + 32, T(f"线程束 {i * 2 + j}", f"warp {i * 2 + j}"), ha="center", va="center", fontsize=10)
a.set_xlim(-2, 130)
a.set_ylim(-2, 130)
a.invert_yaxis()
a.set_aspect("equal")
a.axis("off")
a.set_title(T("（a）线程块：128×128，4 个线程束", "(a) Block: 128×128, 4 warps"), fontsize=10)
for i in range(4):
    for j in range(8):
        hl = (i, j) == (0, 0)
        b.add_patch(plt.Rectangle((j * 8, i * 16), 8, 16, fc=C["y"] if hl else C["z"], alpha=0.6 if hl else 0.25, ec=C["ink"], lw=0.6))
b.text(32, 70, T("每格 16×8：一条 mma.m16n8k16；沿 k 每步 32 要 2 条", "each cell 16×8: one mma.m16n8k16; 2 per 32-wide k step"), ha="center", fontsize=8.5)
b.set_xlim(-1, 65)
b.set_ylim(-1, 74)
b.invert_yaxis()
b.set_aspect("equal")
b.axis("off")
b.set_title(T("（b）线程束：64×64 = 4×8 条指令的输出", "(b) Warp: 64×64 = outputs of 4×8 instructions"), fontsize=10)
cmap = plt.get_cmap("tab20")
for t in range(32):
    for r in (t // 4, t // 4 + 8):
        for col in (2 * (t % 4), 2 * (t % 4) + 1):
            c.add_patch(plt.Rectangle((col, r), 1, 1, fc=cmap(t % 20), alpha=0.55, ec="white", lw=0.8))
            c.text(col + 0.5, r + 0.5, str(t), ha="center", va="center", fontsize=6.5)
c.set_xlim(-0.2, 8.2)
c.set_ylim(-0.2, 16.2)
c.invert_yaxis()
c.set_aspect("equal")
c.axis("off")
c.set_title(T("（c）一条指令的 16×8 个输出在 32 个线程里", "(c) 16×8 outputs of one instruction across 32 threads"), fontsize=10)
fig.tight_layout()
figure(fig, "fig7_4_1")
plt.close(fig)
