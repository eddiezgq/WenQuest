"""5.10 节的示意图。

图 5.10.1：wmma_gemm 的分工。（a）线程块的 128×128 个输出分给 8 个线程束（4 行 × 2 列），每个线程束 32×64，由 2×4 个 16×16 的累加
片段组成；（b）一次 mma_sync：一个线程束合作完成 16×16 与 16×16 的乘加，4096 次乘加，相当于 128 条单精度乘加指令。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1, 1.2]})
cmap = plt.get_cmap("tab10")
for w in range(8):
    wm, wn = w // 2, w % 2
    for i in range(2):
        for j in range(4):
            a.add_patch(plt.Rectangle((wn * 64 + j * 16, wm * 32 + i * 16), 16, 16, fc=cmap(w), alpha=0.35 + 0.15 * ((i + j) % 2), ec="white"))
    a.text(wn * 64 + 32, wm * 32 + 16, T(f"线程束 {w}", f"warp {w}"), ha="center", va="center", fontsize=10)
a.set_xlim(-2, 130)
a.set_ylim(130, -2)
a.set_aspect("equal")
a.set_xticks([0, 64, 128])
a.set_yticks([0, 32, 64, 96, 128])
a.set_title(T("（a）8 个线程束，每个 32×64 = 2×4 个片段", "(a) 8 warps, each 32×64 = 2×4 fragments"), fontsize=10)
for i in range(4):
    for j in range(4):
        b.add_patch(plt.Rectangle((j, 5 + i), 1, 1, fc=C["x"], alpha=0.5, ec="white"))
        b.add_patch(plt.Rectangle((5 + j, i), 1, 1, fc=C["z"], alpha=0.5, ec="white"))
        b.add_patch(plt.Rectangle((5 + j, 5 + i), 1, 1, fc=C["accent"], alpha=0.5, ec="white"))
b.text(2, 9.7, T("A 片段 16×16（半精度）", "A fragment 16×16 (FP16)"), ha="center", fontsize=9)
b.text(7, -0.6, T("B 片段 16×16（半精度）", "B fragment 16×16 (FP16)"), ha="center", fontsize=9)
b.text(7, 9.7, T("累加片段 16×16（单精度）", "accumulator 16×16 (FP32)"), ha="center", fontsize=9)
b.text(10, 6.2, T("一次 mma_sync：\n4096 次乘加\n= 128 条单精度\n  乘加指令", "one mma_sync call:\n4096 FMAs\n= 128 FP32\n  FMA instructions"), fontsize=9, va="center")
b.set_xlim(-0.5, 13.5)
b.set_ylim(10.4, -1.4)
b.set_aspect("equal")
b.axis("off")
b.set_title(T("（b）D = A·B + C，整个线程束一起做", "(b) D = A·B + C, by the whole warp"), fontsize=10)
fig.tight_layout()
figure(fig, "fig5_10_1")
plt.close(fig)
