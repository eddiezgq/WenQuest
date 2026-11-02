"""6.2 节：并行前缀加法器。

算例 6.2.1  16 位 Kogge–Stone、Brent–Kung 与 Sklansky 三种前缀树：级数、前缀运算单元（“黑点”）的个数、最大扇出、
            所有连线的水平跨度之和（布线量），与 SKY130 综合的延时、面积对照（Sklansky 未综合）。
图 6.2.1    三种 16 位前缀树：竖线是信号，黑点是前缀运算 (G, P)∘(G′, P′) = (G + P·G′, P·P′)。
"""
from bookout import T, figure, out, style
from mos import P as PAR
import _draw as d

N = 16


def ks(n):
    ops, d_ = [], 1
    while d_ < n:
        ops.append([(i, i - d_) for i in range(d_, n)])
        d_ *= 2
    return ops


def sklansky(n):
    ops, d_ = [], 1
    while d_ < n:
        ops.append([(i, (i // (2 * d_)) * 2 * d_ + d_ - 1) for i in range(n) if (i // d_) % 2 == 1])
        d_ *= 2
    return ops


def bk(n):
    ops, d_ = [], 1
    while d_ < n:
        ops.append([(i, i - d_) for i in range(2 * d_ - 1, n, 2 * d_)])
        d_ *= 2
    d_ //= 2
    while d_ >= 1:
        lv = [(i, i - d_) for i in range(3 * d_ - 1, n, 2 * d_)]
        if lv:
            ops.append(lv)
        d_ //= 2
    return ops


def stats(ops):
    nops = sum(len(l) for l in ops)
    fan = max(max([sum(1 for (_, j) in l if j == k) for k in range(N)] + [0]) for l in ops) + 1   # 自己的延续 + 被引用的次数
    span = sum(i - j for l in ops for i, j in l)          # 所有前缀运算的连线跨度之和（以位间距为单位）
    return len(ops), nops, fan, span


res = {}
for name, f in (("ks", ks), ("bk", bk), ("sk", sklansky)):
    lv, nops, fan, span = stats(f(N))
    res[name] = f(N)
    out(**{f"{name}_lv": lv, f"{name}_ops": nops, f"{name}_fan": fan, f"{name}_span": span})
S = PAR["arith_syn"]
out(ks_d=S["add_ks_16"]["delay"], bk_d=S["add_bk_16"]["delay"], ks_a=S["add_ks_16"]["area"], bk_a=S["add_bk_16"]["area"],
    rca_d=S["add_rca_16"]["delay"], d_ratio=S["add_bk_16"]["delay"] / S["add_ks_16"]["delay"], a_ratio=S["add_ks_16"]["area"] / S["add_bk_16"]["area"],
    ks32_d=S["add_ks_32"]["delay"], bk32_d=S["add_bk_32"]["delay"], ks32_a=S["add_ks_32"]["area"], bk32_a=S["add_bk_32"]["area"])

# ---------------------------------------------------------------- 图 6.2.1
plt = style()
fig, axs = plt.subplots(1, 3, figsize=(10.2, 3.8))
for ax, (name, title) in zip(axs, (("ks", "Kogge–Stone"), ("bk", "Brent–Kung"), ("sk", "Sklansky"))):
    ops = res[name]
    L = len(ops)
    for i in range(N):
        x = N - 1 - i
        ax.plot([x, x], [0, -(L + 1)], color=d.MUTED, lw=0.6)
        ax.text(x, 0.5, str(i), ha="center", fontsize=6.5, color=d.MUTED)
    for k, lv in enumerate(ops):
        y = -(k + 1)
        for i, j in lv:
            ax.plot([N - 1 - j, N - 1 - i], [y + 0.6, y], color=d.NMOS, lw=0.8)
            ax.plot(N - 1 - i, y, "o", color=d.INK, ms=4)
    ax.set_title(f"{title}：{L} " + T("级", "levels"), fontsize=10)
    ax.set_xlim(-1, N); ax.set_ylim(-(L + 1.5), 1.2)
    ax.axis("off")
figure(fig, "fig6_2_1")
