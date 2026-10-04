"""4.6 节的示意图（GPU 执行模拟器部分 ③，数据同程序 4.6.1）。

图 4.6.1：一个线程束 32 个线程各读一个 4 字节元素时，显存要搬运的 32 字节扇区（蓝）：连续、错位 4 字节、跨步 2、
结构体数组（每个结构体 24 字节、只读一个字段）。
"""
from bookout import COLORS, T, figure, style
from gpusim import addresses, coalesce

plt = style()
C = COLORS
cases = [(T("连续", "contiguous"), dict(kind="contiguous")), (T("错位 4 字节", "offset 4 B"), dict(kind="offset", offset=4)),
         (T("跨步 2", "stride 2"), dict(kind="stride", k=2)), (T("结构体数组（24 字节）", "array of 24-byte structs"), dict(kind="aos", struct=24))]
fig, axs = plt.subplots(len(cases), 1, figsize=(10.6, 6.2))
span = 768
for ax, (name, kw) in zip(axs, cases):
    a = addresses(**kw)
    r = coalesce(a)
    used = set(r["sector_list"])
    for s in range(span // 32):
        ax.add_patch(plt.Rectangle((s * 32, 0), 31, 1, color=C["z"] if s in used else "#e8ebed", lw=0))
    for x in range(0, span + 1, 128):
        ax.plot([x, x], [-0.2, 1.2], color=C["ink"], lw=1.2)
    for i, ad in enumerate(a):
        if ad < span:
            ax.plot([ad + 2], [1.45], "v", color=C["accent"], ms=4)
    ax.set_xlim(-2, span + 2)
    ax.set_ylim(-0.3, 1.8)
    ax.axis("off")
    ax.text(-8, 0.5, name, ha="right", va="center", fontsize=9.5, color=C["ink"])
    ax.text(span + 8, 0.5, T(f"{r['sectors']} 个扇区\n有效 {100 * r['eff']:.0f}%", f"{r['sectors']} sectors\n{100 * r['eff']:.0f}% useful"),
            va="center", fontsize=9, color=C["ink"])
axs[-1].text(0, -0.9, T("地址 0～768 字节；竖线为 128 字节缓存行边界，方格为 32 字节扇区；▼ 为线程读的位置",
                         "addresses 0–768 bytes; bars at 128-byte lines, boxes are 32-byte sectors; ▼ where threads read"),
             fontsize=8.8, color=C["muted"])
fig.subplots_adjust(left=0.2, right=0.86, hspace=0.35)
figure(fig, "fig4_6_1")
plt.close(fig)
