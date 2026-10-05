"""6.4 注塑：冷却时间随壁厚的变化（平板一维导热的解）；协作机器人关节外罩（ABS，壁厚 2.5 mm）用注塑、数控加工、激光烧结三种做法的
单件成本随批量的变化与交点（算例 6.4.1、6.4.2，图 6.4.1）。

冷却时间：平板两面同时冷却，中心温度降到顶出温度的时间 t = s²/(π²α)·ln[(4/π)(Tm − Tw)/(Te − Tw)]，s 为壁厚。
ABS 的热扩散率、熔体温度、模具温度、顶出温度取常用的工艺值；模具费、机时费率、材料单价是本书设定的教学值（美元示意）。"""
import math

import numpy as np

import _ch6 as H
from bookout import T, figure, out, style

ALPHA = 0.12            # ABS 的热扩散率 mm²/s
TM, TW, TE = 230.0, 60.0, 90.0      # 熔体、模具、顶出温度 °C


def t_cool(s):
    return s * s / (math.pi ** 2 * ALPHA) * math.log(4 / math.pi * (TM - TW) / (TE - TW))


S0 = 2.5
tc0 = t_cool(S0)
tc_ratio = t_cool(2 * S0) / tc0
# 关节外罩：开口的盒子 100 × 80 × 40，壁厚 2.5（本书设定）
BOX = (100.0, 80.0, 40.0)
area = BOX[0] * BOX[1] + 2 * (BOX[0] + BOX[1]) * BOX[2]
vol = area * S0                                         # mm³
RHO_ABS = 1.05e-6
mass = vol * RHO_ABS
# 成本（本书设定）
MOLD = 8000.0           # 单腔注塑模具 美元
R_IM = 40.0             # 注塑机 美元/小时
P_ABS = 3.0             # ABS 粒料 美元/kg
T_AUX = 6.0             # 每模开合、注射、保压等冷却以外的时间 s
cycle = tc0 + T_AUX


def c_inject(q):
    return mass * 1.05 * P_ABS + cycle / 3600 * R_IM + MOLD / q          # 5% 料头、废品


# 数控加工：从 ABS 方料铣出薄壁盒子（编程一次性 150 min、每批装夹调整 30 min，每件 60 min；方料 4 美元/kg），费率取数字工厂 VMC-01
def c_cnc(q):
    blank = (BOX[0] + 4) * (BOX[1] + 4) * (BOX[2] + 2) * RHO_ABS
    return blank * 4.0 + 60 / 60 * H.R_VMC + (150 + 30) / 60 * H.R_VMC / q


def c_sls(q):
    p = H.P
    return mass / RHO_ABS * H.RHO_PA12 * p["pa12"] + vol / 1000 / p["print_rate"] * p["R_print"] + p["t_post"] / 60 * p["R_labour"] + p["print_job"] / 60 * p["R_labour"] / q


qs = np.unique(np.round(np.logspace(0, 4, 200)).astype(int))
ci, cc, cs = [c_inject(q) for q in qs], [c_cnc(q) for q in qs], [c_sls(q) for q in qs]
q_im_sls = H.breakeven(c_inject, c_sls)
q_im_cnc = H.breakeven(c_inject, c_cnc)

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 2.9))
ss = np.linspace(0.8, 5, 60)
a0.plot(ss, [t_cool(s) for s in ss], color=H.C_IM, lw=1.2)
a0.plot([S0, 2 * S0], [tc0, t_cool(2 * S0)], "o", color=H.INK, ms=3.5)
a0.text(S0 + 0.1, tc0, T(f"{S0} mm：{tc0:.1f} s", f"{S0} mm: {tc0:.1f} s"), fontsize=6.6, va="top")
a0.text(2 * S0 - 0.1, t_cool(2 * S0), T(f"{2 * S0:.0f} mm：{t_cool(2 * S0):.1f} s", f"{2 * S0:.0f} mm: {t_cool(2 * S0):.1f} s"), fontsize=6.6, ha="right")
a0.set_xlabel(T("壁厚 / mm", "Wall thickness / mm"), fontsize=7.5)
a0.set_ylabel(T("冷却时间 / s", "Cooling time / s"), fontsize=7.5)
a0.tick_params(labelsize=6.5)
a0.set_title(T("(a) ABS 注塑件的冷却时间", "(a) Cooling time of ABS moldings"), fontsize=7.8)
a1.loglog(qs, ci, color=H.C_IM, label=T("注塑（模具 8000 美元）", "injection (mold 8000 USD)"))
a1.loglog(qs, cc, color=H.C_MILL, label=T("数控加工", "CNC machining"))
a1.loglog(qs, cs, color=H.C_AM, label=T("激光烧结 PA12", "laser-sintered PA12"))
a1.axvline(q_im_sls, color=H.MUTED, lw=0.6, ls="--")
a1.text(q_im_sls * 1.1, max(ci) / 3, str(q_im_sls), fontsize=6.6, color=H.MUTED)
a1.set_xlabel(T("批量 / 件", "Batch size"), fontsize=7.5)
a1.set_ylabel(T("单件成本 / 美元", "Cost per part / USD"), fontsize=7.5)
a1.legend(fontsize=6.3, frameon=False)
a1.tick_params(labelsize=6.5)
a1.set_title(T("(b) 关节外罩：三种做法的单件成本", "(b) Joint cover: cost per part, three routes"), fontsize=7.8)
fig.tight_layout()
figure(fig, "fig6_4_1")

out(alpha=ALPHA, Tm=TM, Tw=TW, Te=TE, s0=S0, tc0=tc0, tc_ratio=tc_ratio, box_l=BOX[0], box_w=BOX[1], box_h=BOX[2], mass_g=mass * 1000,
    mold=MOLD, cycle=cycle, ci_1000=c_inject(1000), cs_1000=c_sls(1000), cc_1000=c_cnc(1000), ci_10=c_inject(10), cs_10=c_sls(10), cc_10=c_cnc(10),
    q_im_sls=q_im_sls, q_im_cnc=q_im_cnc, r_im=R_IM, p_abs=P_ABS,
    cnc_run=60, cnc_once=150, cnc_batch=30, p_abs_block=4.0)
