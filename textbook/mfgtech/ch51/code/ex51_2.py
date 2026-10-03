"""51.2 节：SH-301 上的各种基准（图 51.2.1）——设计基准 A–B（两轴承位公共轴线）、工艺上用的两端中心孔、铣键槽时的定位基准与工序基准。"""
import _mfg as M
from bookout import T, figure, out, style

p = M.plan()
segs = p["part"]["segments"]
plt = style()
fig, ax = plt.subplots(figsize=(7.4, 2.9))
z = 0
for d, L, _ in segs:
    ax.add_patch(plt.Rectangle((z, -d / 2), L, d, fc="#e8edf1", ec=M.INK, lw=1.0))
    z += L
total = z
ax.plot([-8, total + 8], [0, 0], color=M.MUTED, lw=0.8, ls=(0, (8, 3, 2, 3)))
kw = p["part"]["keyway"]
x0 = sum(L for _, L, _ in segs[:kw["segment"]]) + kw["offset_mm"]
ax.add_patch(plt.Rectangle((x0, 20 - kw["t"]), kw["L"], kw["t"], fc="white", ec=M.INK, lw=1.0))
for x in (0, total):                                       # 中心孔
    s = 1 if x == 0 else -1
    ax.plot([x, x + s * 6, x], [-3, 0, 3], color=M.INK, lw=1)
zA = sum(L for _, L, _ in segs[:1]) + 6
zB = sum(L for _, L, _ in segs[:3]) + 12.5
for zz, lab in ((zA, "A"), (zB, "B")):
    ax.annotate("", xy=(zz, -17.5), xytext=(zz, -27), arrowprops=dict(arrowstyle="-|>", color=M.ACCENT, lw=1.2))
    ax.text(zz, -31, lab, ha="center", va="top", fontsize=10, color=M.ACCENT, weight="bold")
ax.text(zA - 8, -42, T("设计基准：两轴承位的公共轴线 A–B", "design datum: common axis A–B of the bearing seats"), ha="right", fontsize=8.5, color=M.ACCENT)
ax.annotate(T("工艺基准：两端中心孔\n（定位基准、测量基准）", "process datum: centre holes\n(locating and measuring datum)"),
            xy=(2, 1.5), xytext=(-6, 28), fontsize=8, color=M.WARM, arrowprops=dict(arrowstyle="-", color=M.WARM, lw=0.8))
ax.annotate(T("铣键槽的定位基准：齿轮位外圆（V 形块）", "locating datum for the keyway: gear-seat OD (V-block)"),
            xy=(x0 + kw["L"] + 6, -20.5), xytext=(x0 + 78, -30), fontsize=8, color=M.RED, arrowprops=dict(arrowstyle="-", color=M.RED, lw=0.8))
ax.annotate(T("工序基准：精车外圆下母线（工序尺寸 H 的起点）", "operation datum: bottom generatrix (origin of H)"),
            xy=(x0 + kw["L"] / 2, -20.2), xytext=(x0 - 10, -54), fontsize=8, color=M.RED, arrowprops=dict(arrowstyle="-", color=M.RED, lw=0.8))
ax.plot([x0, x0 + kw["L"]], [-20.15, -20.15], color=M.RED, lw=2.2)
ax.set_xlim(-70, total + 50); ax.set_ylim(-60, 36); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig51_2_1")
out(total=total, keyway_L=kw["L"])
