"""第 5 章部分习题答案中的数值（05-99.md“部分习题答案与提示”引用）。与正文程序用同一个模型。"""
import math

from bookout import out
from mos import P, VDD, energy_per_op, fo4_scale, fo4_tp, leak_inv, r_ratio, sleep_ron

ps = P["power_sim"]
f4 = fo4_tp(r_ratio())

# 5.2.1：阈值降低 100 mV，漏电变为几倍
out(a521=10 ** (0.1 / (ps["S27"] / 1e3)))
# 5.2.2：VDD 从 1.8 V 降到 1.2 V，只按 DIBL 估计的漏电倍数与仿真
out(a522_dibl=1 / 10 ** (ps["dibl"] / 1e3 * 0.6 / (ps["S27"] / 1e3)), a522_sim=leak_inv(27, 1.2) / leak_inv(27, 1.8))
# 5.2.3：125 °C 放 90 天
q = P["problems"]["p52"]
i125 = q["n_equiv"] * leak_inv(125)
out(a523_ua=i125 * 1e6, a523_ah=i125 * q["days"] * 24, a523_pct=i125 * q["days"] * 24 / q["battery_Ah"] * 100)
# 5.3.1：0.9 V 时每次运算的动态能量与速度
out(a531_e_pct=(0.9 / VDD) ** 2 * 100, a531_slow=fo4_scale(0.9))
# 5.3.3：控制环提高到 20 kHz（每个周期 50 μs，仍要 2000 个周期）
q3 = P["problems"]["p53"]
need = q3["cycles"] / (1 / (2 * q3["loop_kHz"] * 1e3))
v = VDD
while v > 0.4 and 1 / (q3["depth_fo4"] * f4 * fo4_scale(v - 0.01)) >= need:
    v -= 0.01
out(a533_f_mhz=need / 1e6, a533_v=round(v, 2))
# 5.4.1：125 °C 时的盈亏平衡时间；5.4.3：压降限 2 % 时的宽度
q4 = P["problems"]["p54"]
N, C = q4["n_gates"], q4["c_gate_fF"] * 1e-15
wp_ref = P["kn"] / P["kp"] * P["Wmin"]
i_pk = q4["peak"] * q4["alpha"] * N * C * VDD * q4["f_MHz"] * 1e6
w5 = sleep_ron(1.0) / (q4["drop_pct"] / 100 * VDD / i_pk)
w2 = sleep_ron(1.0) / (0.02 * VDD / i_pk)
blk = N * leak_inv(125)
hdr = ps["leak_in1"]["125"] / wp_ref * w5
out(a541_us=N * C * VDD ** 2 / ((blk - hdr) * VDD) * 1e6, a543_w=w2, a543_x=w2 / w5)
# 5.5.2：电机转速减半时编码器计数器的翻转率
q5 = P["problems"]["p55"]
out(a552_pct=q5["rpm"] / 2 / 60 * q5["lines"] * 4 / (q5["f_MHz"] * 1e6) * 100)
