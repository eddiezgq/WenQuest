"""5.2 节：漏电。

算例 5.2.1  亚阈值区：NMOS 的亚阈值摆幅 S 与 DIBL（SKY130 仿真），按 I = I_T·10^((VGS − VT)/S) 由 100 nA·W/L 处的阈值外推
            VGS = 0 时的电流，与仿真的关断电流比较（NMOS、PMOS 分别看）。
算例 5.2.2  巡检机器人在仓库里放三个月，控制芯片不断电（待机）：约五万个参考反相器当量，27 °C 与 85 °C（夏天的车厢）时的待机电流
            和三个月的耗电，与 20 Ah 电池比较；两管叠层能把漏电降到多少。
图 5.2.1    参考反相器的漏电随温度的变化（仿真，对数纵轴）：输入为 1（PMOS 关），两个 PMOS 叠层；点线为模型的数值下限。
"""
import numpy as np

from bookout import T, figure, out, style
from mos import P, Wmin, L, r_ratio, leak_inv
import _draw as d

q = P["power_sim"]
p = P["problems"]["p52"]
r = r_ratio()

# ---------------------------------------------------------------- 算例 5.2.1
S27, S85, dibl, vt = q["S27"] / 1e3, q["S85"] / 1e3, q["dibl"], q["vt_cc"]
i_t = 100e-9 * Wmin / L
i_off_est = i_t * 10 ** (-vt / S27)
i_n, i_p = q["leak_in0"]["27"], q["leak_in1"]["27"]
out(S27=S27 * 1e3, S85=S85 * 1e3, ideal_S=60 * (273.15 + 27) / 300, dibl=dibl, vt_cc=vt, i_t_na=i_t * 1e9,
    i_off_est_fa=i_off_est * 1e15, p_over_est=i_p / i_off_est, i_n_pa=i_n * 1e12, i_p_pa=i_p * 1e12, n_ratio=i_n / i_off_est, p_over_n=i_p / i_n,
    floor_pa=1e-12 * 1.8 * 1e12, dibl_dvt_mv=dibl * 1.75, dibl_x=10 ** (dibl * 1.75 / 1e3 / S27), n_factor=S27 * 1e3 / (60 * 300.15 / 300))

# ---------------------------------------------------------------- 算例 5.2.2
hours = p["days"] * 24
for t in p["temps"]:
    i = p["n_equiv"] * leak_inv(t)
    out(**{f"i{t}_ua": i * 1e6, f"ah{t}": i * hours, f"pct{t}": i * hours / p["battery_Ah"] * 100, f"inv{t}_na": leak_inv(t) * 1e9})
out(n_equiv=p["n_equiv"], days=p["days"], battery=p["battery_Ah"], t_ratio=leak_inv(85) / leak_inv(27),
    t_ratio125=leak_inv(125) / leak_inv(27))
for t in ("27", "85", "125"):
    out(**{f"stack{t}": 1 / q["stack"][t]})
out(stack_i85_ua=p["n_equiv"] * leak_inv(85) * q["stack"]["85"] * 1e6)

# ---------------------------------------------------------------- 图 5.2.1
plt = style()
fig, ax = plt.subplots(figsize=(5.8, 3.4))
ts = [27, 85, 125]
ax.semilogy(ts, [q["leak_in1"][str(t)] for t in ts], "o-", color=d.PMOS, lw=1.8, label=T("输入为 1：PMOS 关", "input 1: PMOS off"))
ax.axhline(q["leak_in0"]["27"], color=d.NMOS, lw=1.0, ls=":")
ax.text(30, q["leak_in0"]["27"] * 1.4, T("模型的数值下限（gbmin × VDD）：NMOS 关断电流低于它", "model floor (gbmin × VDD): NMOS off current lies below it"), fontsize=8, color=d.NMOS)
ax.semilogy(ts, [q["leak_in1"][str(t)] * 2 * q["stack"][str(t)] for t in ts], "^--", color=d.MEAN, lw=1.4,
            label=T("两个 PMOS 叠层（同样宽度的两倍）", "two stacked PMOS (2× width each)"))
ax.set_xlabel(T("温度 / °C", "temperature / °C")); ax.set_ylabel(T("漏电 / A", "leakage / A"))
ax.set_xticks(ts)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
d.spines(ax)
figure(fig, "fig5_2_1")
