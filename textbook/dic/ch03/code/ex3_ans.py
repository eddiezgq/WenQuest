"""第 3 章部分习题答案中的数值（03-99.md“部分习题答案与提示”引用）。与正文程序用同一个模型。"""
import math

from bookout import out
from _skew import skew_ch4
from mos import fo4_tp, P, VDD, Wmin, cin, ff_tcq_le, ff_timing, gamma_self, hold_slack, inc_delay, le_g, mtbf, r_ratio, setup_slack, sync_tr, tau

g = gamma_self()
tu = tau()
ff = ff_timing()

# 3.1.3：占空比 10 %
st = ff_tcq_le()
loop = (st[2] + st[3] + (1 + g)) * tu
out(a313_laps=int(1e-9 // loop))
# 3.1.5：两级本地时钟反相器加大到 2 倍
old = (g + 3) + (g + 2)
new = (g + 4 / 2) + (g + 2 / 2)
out(a315_tau=old - new, a315_ps=(old - new) * tu * 1e12)

# 3.2.2：12 位、100 MHz
f = 100e6
out(a322_pwm_khz=f / 2 ** 12 / 1e3, a322_slack_ns=setup_slack(1 / f, inc_delay(12) * tu) * 1e9)
# 3.2.3：超前进位 40τ
Tm = ff["tcq"] + 40 * tu + ff["tsu"]
out(a323_fmax_mhz=1e-6 / Tm, a323_need_mhz=2 ** 16 * 20e3 / 1e6)
# 3.2.5：th = +40 ps
pair = 2 * (1 + g) * tu
skew = skew_ch4() + P["problems"]["p32"]["gate_fo4"] * fo4_tp(r_ratio())      # 与算例 3.2.2 相同：第 4 章的偏斜 + 门控单元
s0 = ff["tcq"] - 40e-12 - skew
n = 0
while s0 + n * pair < 0:
    n += 1
out(a325_slack_ps=s0 * 1e12, a325_n=n)

# 3.3.1、3.3.2
out(a331_tau=math.log(1000), a332_ps=ff["tau_m"] * math.log(2) * 1e12)
# 3.3.3：1 GHz
q = P["problems"]["p33"]
fd = q["rpm"] / 60 * q["lines"] * 2
fc = 1e9
need = q["robots"] * q["years"] * 365 * 24 * 3600
tr_need = ff["tau_m"] * math.log(need * ff["T0"] * fc * fd)
tr2, tr3 = sync_tr(2, fc, 0.0), sync_tr(3, fc, 0.0)
out(a333_need_ps=tr_need * 1e12, a333_tr2_ps=tr2 * 1e12, a333_tr3_ps=tr3 * 1e12,
    a333_m2_yr=mtbf(tr2, fc, fd) / (365 * 24 * 3600), a333_m3_log=math.log10(mtbf(tr3, fc, fd) / (365 * 24 * 3600)))

# 3.4.1：时钟树电容是触发器时钟电容的 1.5 倍，门控单元放在叶子上
q4 = P["problems"]["p34"]
C0 = cin(Wmin, r_ratio() * Wmin)
c_ff = (1 + (3 + g) + (2 + g)) * C0
c_icg = (1 + (1 + g) + 1 + le_g("nand", 2)) * C0
n_icg = q4["n_ff"] // q4["group"]
total = 2.5 * q4["n_ff"] * c_ff
after = 1.5 * q4["n_ff"] * c_ff + n_icg * c_icg + (1 - q4["idle"]) * q4["n_ff"] * c_ff
out(a341_pct=(1 - after / total) * 100)
