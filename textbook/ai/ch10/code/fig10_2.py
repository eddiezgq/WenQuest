"""10.2 节的示意图（数据同程序 10.2.1）。

图 10.2.1：（a）线程束内归约：32 道做 5 层洗牌，64 道要 6 层；把为 32 道写的循环（起点 16）照搬到 64 道上，
每个波前只算出低 32 道与高 32 道各自的和（灰色的一半被丢掉），结果约为正确值的一半（程序 10.6.2 验证了这一点）；
（b）一条 32 位访存指令一次请求的字节数：32 道正好一个 128 字节的缓存行，64 道是 256 字节。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, (a, b) = plt.subplots(1, 2, figsize=(12.4, 4.0), gridspec_kw={"width_ratios": [1.5, 1]})

# ---------- (a) 洗牌的层数
def draw_tree(ax, w, y0, label, dead_half=False):
    """w 道的波前：每层把活动的道画成方块，箭头表示 v += __shfl_down(v, off)。"""
    n_levels = {32: 5, 64: 6}[w]
    for lv in range(n_levels + 1):
        act = w >> lv                                     # 这一层结束后仍持有部分和的道数
        y = y0 - lv * 0.62
        for i in range(min(act, 8)):
            x = i * 0.5
            dead = dead_half and lv >= 6                  # 照搬 32 道的写法时，第 6 层（最后一层）根本没做
            ax.add_patch(plt.Rectangle((x, y), 0.4, 0.42, fc=C["muted"] if dead else C["z"],
                                       alpha=0.3 if dead else 0.6, ec="none"))
        if act > 8:
            ax.text(8 * 0.5 + 0.1, y + 0.2, "…", fontsize=9, color=C["muted"], va="center")
        ax.text(-0.25, y + 0.2, f"{act}", ha="right", va="center", fontsize=8, color=C["ink"])
    ax.text(-0.25, y0 + 0.75, label, ha="left", va="center", fontsize=9, color=C["ink"])


draw_tree(a, 32, 3.6, T("32 道（NVIDIA）：5 层", "32 lanes (NVIDIA): 5 steps"))
a.set_xlim(-1.4, 11.2)
a.set_ylim(-0.6, 4.6)
a.axis("off")
ax2 = a.inset_axes([0.5, 0.0, 0.5, 1.0])
draw_tree(ax2, 64, 3.6, T("64 道（AMD CDNA）：要 6 层", "64 lanes (AMD CDNA): 6 steps"), dead_half=True)
ax2.set_xlim(-1.4, 5.6)
ax2.set_ylim(-0.6, 4.6)
ax2.axis("off")
ax2.text(-1.3, -0.35, T("灰色：照搬 32 道的写法时漏掉的一层", "grey: the step a 32-lane port misses"),
         fontsize=7.5, color=C["muted"])
a.set_title(T("(a) 线程束内归约的层数", "(a) Steps of an in-warp reduction"), fontsize=10)

# ---------- (b) 一条访存指令请求多少字节
for i, (w, col) in enumerate(((32, C["z"]), (64, C["x"]))):
    nbytes = w * 4
    y = 1 - i
    b.add_patch(plt.Rectangle((0, y), nbytes / 256 * 4, 0.5, fc=col, alpha=0.6, ec="none"))
    b.text(nbytes / 256 * 4 + 0.1, y + 0.25, f"{nbytes} B", va="center", fontsize=9, color=col)
    b.text(-0.15, y + 0.25, T(f"{w} 道", f"{w} lanes"), ha="right", va="center", fontsize=9)
for x in (2, 4):                                          # 128 字节的缓存行边界
    b.plot([x, x], [-0.3, 1.8], ls=":", lw=0.9, color=C["muted"])
b.text(2, 1.9, T("128 字节（缓存行）", "128 B (cache line)"), ha="center", fontsize=8, color=C["muted"])
b.set_xlim(-1.6, 5.6)
b.set_ylim(-0.4, 2.2)
b.axis("off")
b.set_title(T("(b) 一条 32 位访存指令的请求", "(b) One 32-bit load per lane"), fontsize=10)

fig.tight_layout()
figure(fig, "fig10_2_1")
