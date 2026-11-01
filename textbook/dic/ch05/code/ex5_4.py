"""5.4 节：时钟门控与电源门控。

算例 5.4.1  巡检机器人的视觉预处理模块（约三万个门、翻转率 0.1、每门 5 fF、100 MHz）只在拍照时工作。用 PMOS 休眠管（header）
            给它断电：(1) 工作时的峰值电流取平均电流的 3 倍（示意值），休眠管上的压降不超过 VDD 的 5 %，休眠管至少要多宽；
            (2) 85 °C 时断电前后的漏电；(3) 唤醒时要给虚拟电源轨和模块内部的电容重新充电（取全部门电容之和，示意值），
            唤醒能量多大，空闲多久以上断电才划算（盈亏平衡时间），27 °C 时又是多久。
图 5.4.1    (a) 电源门控的结构：休眠管、虚拟电源轨、隔离单元与保持寄存器；(b) 休眠管宽度与压降、关断漏电的关系。
"""
import numpy as np

from bookout import T, figure, out, style
from mos import P, VDD, fo4_scale, leak_inv, sleep_ron
import _draw as d

q = P["problems"]["p54"]
ps = P["power_sim"]
N, a, C, f = q["n_gates"], q["alpha"], q["c_gate_fF"] * 1e-15, q["f_MHz"] * 1e6
i_avg = a * N * C * VDD * f
i_pk = q["peak"] * i_avg
dv_max = q["drop_pct"] / 100 * VDD
r_max = dv_max / i_pk
w_need = sleep_ron(1.0) / r_max                       # Ron ∝ 1/W
wp_ref = P["kn"] / P["kp"] * P["Wmin"]


def header_leak(w, temp):
    """关断的休眠管漏电：按参考反相器输入为 1（PMOS 关）的仿真漏电折算到每微米。"""
    return ps["leak_in1"][str(temp)] / wp_ref * w


T85 = q["temp"]
blk85 = N * leak_inv(T85)
hdr85 = header_leak(w_need, T85)
c_rail = N * C
e_wake = c_rail * VDD ** 2
be85 = e_wake / ((blk85 - hdr85) * VDD)
blk27, hdr27 = N * leak_inv(27), header_leak(w_need, 27)
be27 = e_wake / ((blk27 - hdr27) * VDD)
slow_pct = (fo4_scale(VDD - dv_max) / fo4_scale(VDD) - 1) * 100
out(n_gates=N, f_MHz=q["f_MHz"], i_avg_ma=i_avg * 1e3, i_pk_ma=i_pk * 1e3, peak=q["peak"], drop_pct=q["drop_pct"], dv_mv=dv_max * 1e3,
    r_max=r_max, w_need=w_need, ron_1um=sleep_ron(1.0), blk85_ua=blk85 * 1e6, hdr85_ua=hdr85 * 1e6, cut85=blk85 / hdr85,
    c_rail_pf=c_rail * 1e12, e_wake_nj=e_wake * 1e9, be85_us=be85 * 1e6, be27_us=be27 * 1e6, blk27_ua=blk27 * 1e6,
    slow_pct=slow_pct, area_pct=w_need / (N * 2 * (P["Wmin"] + wp_ref)) * 100)
# 一个拍照周期：每 0.5 s 工作 20 ms（示意值），空闲 480 ms
t_on, t_cyc = 20e-3, 0.5
p_dyn = i_avg * VDD
e_no = (p_dyn * t_on + blk85 * VDD * t_cyc)
e_pg = (p_dyn * t_on + blk85 * VDD * t_on + hdr85 * VDD * (t_cyc - t_on) + e_wake)
out(t_on_ms=t_on * 1e3, t_cyc_ms=t_cyc * 1e3, p_avg_no_uw=e_no / t_cyc * 1e6, p_avg_pg_uw=e_pg / t_cyc * 1e6, pg_save_pct=(1 - e_pg / e_no) * 100,
    p_dyn_mw=p_dyn * 1e3)

# ---------------------------------------------------------------- 图 5.4.1
plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.6), gridspec_kw={"width_ratios": [1.1, 1]})
# (a) 结构
d_ = 0.0
a1.plot([0.2, 4.6], [3.2, 3.2], color=d.INK, lw=1.5); a1.text(0.1, 3.2, "VDD", ha="right", va="center", fontsize=9)
a1.plot([1.2, 1.2], [3.2, 2.85], color=d.INK, lw=1.3)
a1.add_patch(__import__("matplotlib").patches.Rectangle((0.95, 2.35), 0.5, 0.5, fill=False, ec=d.PMOS, lw=1.4))
a1.text(1.2, 2.6, "P", ha="center", va="center", color=d.PMOS, fontsize=9)
a1.text(0.85, 2.6, T("休眠管", "sleep\ntransistor"), ha="right", va="center", fontsize=8.5, color=d.PMOS)
a1.plot([1.2, 1.2], [2.35, 2.0], color=d.INK, lw=1.3)
a1.plot([0.6, 3.6], [2.0, 2.0], color=d.LOAD, lw=1.5, ls="--"); a1.text(3.65, 2.0, T("虚拟电源轨", "virtual VDD"), va="center", fontsize=8.5, color=d.LOAD)
a1.add_patch(__import__("matplotlib").patches.Rectangle((0.6, 0.6), 2.2, 1.2, fill=False, ec=d.NMOS, lw=1.4))
a1.text(1.7, 1.35, T("视觉预处理模块", "vision block"), ha="center", fontsize=9, color=d.NMOS)
a1.add_patch(__import__("matplotlib").patches.Rectangle((0.7, 0.72), 1.05, 0.38, fill=False, ec=d.MEAN, lw=1.2))
a1.text(1.22, 0.91, T("保持寄存器", "retention"), ha="center", va="center", fontsize=7.5, color=d.MEAN)
a1.plot([0.3, 0.3, 0.7], [3.2, 0.91, 0.91], color=d.MEAN, lw=1.0, ls="-.")
a1.text(0.25, 1.6, T("常开电源", "always-on"), ha="right", fontsize=7.5, color=d.MEAN)
for x in (1.4, 2.0):
    a1.plot([x, x], [2.0, 1.8], color=d.INK, lw=1.0)
a1.plot([2.8, 3.3], [1.2, 1.2], color=d.INK, lw=1.2)
a1.add_patch(__import__("matplotlib").patches.Rectangle((3.3, 1.0), 0.55, 0.4, fill=False, ec=d.MEAN, lw=1.2))
a1.text(3.575, 1.2, T("隔离", "iso"), ha="center", va="center", fontsize=8, color=d.MEAN)
a1.plot([3.85, 4.4], [1.2, 1.2], color=d.INK, lw=1.2); a1.text(4.45, 1.2, T("其余电路", "rest of chip"), va="center", fontsize=8.5)
a1.text(1.2, 3.35, T("睡眠信号", "sleep"), ha="center", fontsize=8, color=d.MUTED)
a1.set_xlim(-0.6, 5.6); a1.set_ylim(0.4, 3.6); a1.axis("off")
a1.set_title(T("(a) 电源门控的结构", "(a) power-gating structure"), fontsize=10)
# (b) 宽度
ws = np.logspace(np.log10(50), np.log10(5000), 80)
a2.loglog(ws, [i_pk * sleep_ron(w) / VDD * 100 for w in ws], color=d.PMOS, lw=1.8, label=T("峰值时的压降 / VDD（%）", "drop at peak / VDD (%)"))
a2.loglog(ws, [header_leak(w, T85) / blk85 * 100 for w in ws], color=d.NMOS, lw=1.8, label=T(f"关断漏电 / 模块漏电（%，{T85} °C）", f"off leakage / block leakage (%, {T85} °C)"))
a2.axhline(q["drop_pct"], color=d.LOAD, lw=0.9, ls=":")
a2.axvline(w_need, color=d.MEAN, lw=0.9, ls="--")
a2.text(w_need * 1.1, 60, T(f"{w_need:.0f} μm", f"{w_need:.0f} μm"), fontsize=8.5, color=d.MEAN)
a2.set_xlabel(T("休眠管宽度 / μm", "sleep-transistor width / μm")); a2.set_ylabel("%")
a2.legend(fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2))
a2.set_title(T("(b) 宽度的取舍", "(b) choosing the width"), fontsize=10)
d.spines(a2)
figure(fig, "fig5_4_1")
