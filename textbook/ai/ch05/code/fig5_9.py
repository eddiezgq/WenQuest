"""5.9 节的示意图。

图 5.9.1：线程块 128×128 的 C 块由 256 个线程（16×16）分担，每个线程 8×8 个元素。（a）regtile：线程 (trow, tcol) 负责连续的
8 行 8 列——图中线程 (1, 2) 是第 8—15 行、第 16—23 列；（b）vec、dbuf：8 行分成 trow·4 + {0..3} 与 64 + trow·4 + {0..3} 两组，
8 列同理，线程 (1, 2) 负责四个 4×4 的小块。这样一个线程束读共享内存时，每四分之一个线程束（8 个线程）读连续的 32 个字，没有存储体冲突；
（c）每一步 k：从共享内存读 A 的 8 个数、B 的 8 个数，做 8×8 = 64 次乘加（外积）。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, axs = plt.subplots(1, 3, figsize=(13, 4.6), gridspec_kw={"width_ratios": [1, 1, 0.8]})
for ax, mode in zip(axs[:2], ("reg", "vec")):
    ax.add_patch(plt.Rectangle((0, 0), 128, 128, fc="#f2f4f6", ec=C["muted"]))
    for v in range(0, 129, 8):
        ax.plot([v, v], [0, 128], color="white", lw=0.6)
        ax.plot([0, 128], [v, v], color="white", lw=0.6)
    tr, tc = 1, 2
    if mode == "reg":
        ax.add_patch(plt.Rectangle((tc * 8, tr * 8), 8, 8, fc=C["accent"], alpha=0.9))
        ax.set_title(T("（a）regtile：连续的 8×8", "(a) regtile: one contiguous 8×8"), fontsize=10)
    else:
        for r0 in (tr * 4, 64 + tr * 4):
            for c0 in (tc * 4, 64 + tc * 4):
                ax.add_patch(plt.Rectangle((c0, r0), 4, 4, fc=C["accent"], alpha=0.9))
        ax.plot([64, 64], [0, 128], color=C["muted"], lw=1, ls="--")
        ax.plot([0, 128], [64, 64], color=C["muted"], lw=1, ls="--")
        ax.set_title(T("（b）vec：四个 4×4，相隔 64", "(b) vec: four 4×4 pieces, 64 apart"), fontsize=10)
    ax.set_xlim(-3, 131)
    ax.set_ylim(131, -3)
    ax.set_aspect("equal")
    ax.set_xticks([0, 64, 128])
    ax.set_yticks([0, 64, 128])
    ax.set_xlabel(T("列", "column"))
    ax.set_ylabel(T("行", "row"))
ax = axs[2]
for i in range(8):
    ax.add_patch(plt.Rectangle((0, 1.5 + i), 1, 1, fc=C["x"], alpha=0.6, ec="white"))
    ax.add_patch(plt.Rectangle((1.5 + i, 0), 1, 1, fc=C["z"], alpha=0.6, ec="white"))
    for j in range(8):
        ax.add_patch(plt.Rectangle((1.5 + j, 1.5 + i), 1, 1, fc=C["accent"], alpha=0.35, ec="white"))
ax.text(0.5, 10.3, T("A 的 8 个数", "8 of A"), ha="center", fontsize=9)
ax.text(5.5, -0.5, T("B 的 8 个数", "8 of B"), ha="center", fontsize=9)
ax.text(5.5, 10.3, T("64 个累加器（寄存器）", "64 accumulators (registers)"), ha="center", fontsize=9)
ax.set_xlim(-0.5, 10)
ax.set_ylim(11, -1.2)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title(T("（c）每步：读 16 个数，做 64 次乘加", "(c) Each step: 16 loads, 64 FMAs"), fontsize=10)
fig.tight_layout()
figure(fig, "fig5_9_1")
plt.close(fig)
