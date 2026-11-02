"""算例 56.3.1、56.3.2：SH-101 的毛坯——棒料与模锻件的材料利用率、每件毛坯与粗车的成本，以及换用锻件的临界年产量。
棒料单价取工厂数据（factory/data.py：RM-20CR-D60 每千克的价格），粗车工时与费率取工厂数据（数控车床 CNC-L01）；
锻件的余量（单边 2 mm、端面 2.5 mm）、锻造加工费、锻模费和锻件粗车工时是示意值（教学设定），书中注明。画图 56.3.2、56.3.3。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

P = M.part101()
RT = M.route()
F = M.F
rho = 7.85e-6                                    # kg/mm³
segs = [(float(d), float(L), n) for d, L, n in P["part"]["segments"]]


def vol(ss):
    return sum(math.pi / 4 * d * d * L for d, L, _ in ss)


# 零件：齿轮段按分度圆与齿顶圆之间约一半的齿槽估算（齿槽约占齿顶圆与齿根圆之间环形面积的一半）
g = P["part"]["gear"]
part_v = sum(math.pi / 4 * d * d * L for d, L, n in segs if n != "齿轮")
gL = next(L for d, L, n in segs if n == "齿轮")
part_v += gL * (math.pi / 4 * g["df_mm"] ** 2 + 0.5 * math.pi / 4 * (g["da_mm"] ** 2 - g["df_mm"] ** 2))
m_part = part_v * rho
blank = M.route101()["blank"]
m_bar = math.pi / 4 * 60 ** 2 * blank["length_mm"] * rho
util_bar = m_part / m_bar
price = F.ITEMS["RM-20CR-D60"][3]                 # 元/kg
# 模锻件（示意）：三段——左段（轴伸、密封轴颈、左轴承位）Ø29、齿轮段 Ø57、右段 Ø30，单边余量 2 mm，两端各 2.5 mm；飞边与烧损 12%
forg = [(29.0, 36 + 20 + 17 + 2.5, "左段"), (57.0, 8 + 30 + 8, "齿轮段"), (30.0, 17 + 2.5, "右段")]
m_forg = vol(forg) * rho
m_forg_in = m_forg * 1.12
util_forg = m_part / m_forg_in
rate, _ = RT.rate_per_hour("数控车床 CNC-L01")
t_rough_bar, t_rough_forg = 14.0, 7.0             # 粗车工时（min）：棒料取工艺路线工序 20，锻件余量小、约一半（示意）
forge_fee, die = 4.0, 36000.0                     # 锻造加工费（元/件）、一副锻模（元，按一年摊销），示意
c_bar = m_bar * price + t_rough_bar / 60 * rate
c_forg_var = m_forg_in * price + forge_fee + t_rough_forg / 60 * rate
N_crit = die / (c_bar - c_forg_var)
N = P["annual_volume"]

plt = style()
# ---- 图 56.3.2：毛坯图（模锻件，示意）与棒料的轮廓，零件轮廓在里面
fig, ax = plt.subplots(figsize=(7.0, 2.5))
x = 0
for d, L, n in segs:
    ax.add_patch(plt.Rectangle((x, -d / 2), L, d, fc="#f6ead9", ec=M.INK, lw=0.8))
    x += L
x = -2.5
xs = []
for d, L, n in forg:
    ax.add_patch(plt.Rectangle((x, -d / 2), L, d, fc="none", ec=M.RED, lw=1.3, ls="--"))
    xs.append((x, L, d))
    x += L
ax.add_patch(plt.Rectangle((-3, -30), blank["length_mm"], 60, fc="none", ec=M.ACCENT, lw=1.0, ls=":"))
ax.text(136 + 13, 22, T(f"棒料 Ø60 × {blank['length_mm']}\n{m_bar:.2f} kg", f"bar Ø60 × {blank['length_mm']}\n{m_bar:.2f} kg"), fontsize=7, color=M.ACCENT)
ax.text(136 + 13, -2, T(f"模锻件（示意）\n{m_forg:.2f} kg", f"die forging (illustr.)\n{m_forg:.2f} kg"), fontsize=7, color=M.RED)
ax.text(136 + 13, -24, T(f"零件 {m_part:.2f} kg", f"part {m_part:.2f} kg"), fontsize=7, color=M.INK)
ax.annotate(T("单边余量 2", "2 per side"), (58, 14.5), (52, 38), fontsize=7, color=M.RED, arrowprops={"arrowstyle": "-", "lw": 0.5, "color": M.RED})
ax.plot([-8, 145], [0, 0], color=M.INK, lw=0.5, ls=(0, (8, 2, 1, 2)))
ax.set_xlim(-10, 182); ax.set_ylim(-34, 42); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig56_3_2")

# ---- 图 56.3.3：每件毛坯与粗车的成本随年产量
fig, ax = plt.subplots(figsize=(5.8, 2.9))
ns = np.linspace(1000, 20000, 200)
ax.plot(ns, np.full_like(ns, c_bar), color=M.ACCENT, lw=1.4, label=T("棒料：材料 + 粗车", "bar: material + rough turning"))
ax.plot(ns, c_forg_var + die / ns, color=M.RED, lw=1.4, label=T("模锻件：材料 + 锻造 + 锻模摊销 + 粗车", "forging: material + forging + die + rough turning"))
ax.axvline(N_crit, color=M.MUTED, ls="--", lw=0.8)
ax.text(N_crit * 1.03, c_bar * 1.25, T(f"临界年产量 ≈ {N_crit:.0f}", f"break-even ≈ {N_crit:.0f}/yr"), fontsize=7.5, color=M.MUTED)
ax.plot(N, c_bar, "o", color=M.INK, ms=4)
ax.text(N * 0.97, c_bar * 0.86, T(f"WQR-105 年产 {N}", f"WQR-105: {N}/yr"), fontsize=7, ha="right")
ax.set_ylim(0, c_bar * 2.2)
ax.set_xlabel(T("年产量 / 件", "annual volume")); ax.set_ylabel(T("每件成本 / 元", "cost per part / CNY"))
ax.grid(lw=0.3, alpha=0.5); ax.legend(fontsize=7, loc="upper right")
figure(fig, "fig56_3_3")

out(m_part=m_part, m_bar=m_bar, util_bar_pct=util_bar * 100, price=price, m_forg=m_forg, m_forg_in=m_forg_in, util_forg_pct=util_forg * 100,
    rate=rate, t_rough_bar=t_rough_bar, t_rough_forg=t_rough_forg, forge_fee=forge_fee, die=die, c_bar=c_bar, c_forg_var=c_forg_var,
    N_crit=N_crit, N=N, c_forg_N=c_forg_var + die / N, bar_len=blank["length_mm"])
