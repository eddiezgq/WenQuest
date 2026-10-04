"""4.5 节的示意图。

图 4.5.1：CUDA 程序看到的存储空间：每个线程的寄存器与本地内存，每个线程块的共享内存，所有线程共用的全局内存、
常量内存（只读、有缓存），以及它们所在的硬件位置（片上 / 显存）。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6.4)
ax.axis("off")


def box(x, y, w, h, text, col, alpha=0.2, fs=9):
    ax.add_patch(plt.Rectangle((x, y), w, h, color=col, alpha=alpha, lw=0))
    ax.add_patch(plt.Rectangle((x, y), w, h, fill=False, ec=col, lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=C["ink"])


ax.add_patch(plt.Rectangle((0.2, 2.75), 9.6, 3.45, fill=False, ec=C["muted"], lw=1, ls="--"))
ax.text(0.35, 6.0, T("芯片上（每个 SM）", "on chip (each SM)"), fontsize=10, color=C["muted"])
for b, x0 in enumerate((0.5, 5.2)):
    ax.add_patch(plt.Rectangle((x0, 2.95), 4.3, 2.85, fill=False, ec=C["ink"], lw=1))
    ax.text(x0 + 0.1, 5.55, T(f"线程块 {b}", f"block {b}"), fontsize=9.5, color=C["ink"])
    box(x0 + 0.2, 4.4, 3.9, 0.7, T("共享内存 __shared__（块内共享，几十个周期）", "shared memory __shared__ (per block, tens of cycles)"), C["y"], fs=8.5)
    for t in range(2):
        tx = x0 + 0.2 + t * 2.0
        box(tx, 3.15, 1.9, 1.0, T(f"线程 {t}\n寄存器（最快）", f"thread {t}\nregisters (fastest)"), C["z"], fs=8.5)
box(0.5, 0.25, 4.3, 1.1, T("全局内存（所有线程、主机都可读写；\n几百个周期；经 L2 缓存）", "global memory (all threads and the host;\nhundreds of cycles; via L2)"), C["x"], fs=8.5)
box(5.2, 0.95, 2.1, 1.0, T("常量内存\n（64 KB，只读）", "constant memory\n(64 KB, read-only)"), C["accent"], fs=8.5)
box(7.5, 0.95, 2.1, 1.0, T("本地内存\n（寄存器溢出）", "local memory\n(register spills)"), C["muted"], fs=8.5)
ax.text(0.35, 2.3, T("显存（片外 DRAM）", "device memory (off-chip DRAM)"), fontsize=10, color=C["muted"])
ax.add_patch(plt.Rectangle((0.2, 0.1), 9.6, 2.4, fill=False, ec=C["muted"], lw=1, ls="--"))
for x in (1.6, 3.6):
    ax.annotate("", xy=(x, 1.35), xytext=(x, 3.15), arrowprops=dict(arrowstyle="<|-|>", color=C["muted"], lw=1))
figure(fig, "fig4_5_1")
plt.close(fig)
