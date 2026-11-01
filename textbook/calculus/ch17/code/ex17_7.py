"""17.7 节：经济与生物中的应用——买一台焊接机器人值不值：连续现金流的现值与动态回收期；消费者剩余；
指示剂稀释法测心输出量（采样浓度 + 辛普森公式）；管道层流（泊肃叶流动）的流量。"""
import math

from scipy import integrate, optimize

from _quad import simpson, trap
from bookout import out

# 机器人投资：价格 30 万元；每年节省人工 12 万元（连续流入），维护费第一年 1 万元、每年增加 0.5 万元；折现率 6%
C0, S, m0, dm, r, life = 30.0, 12.0, 1.0, 0.5, 0.06, 8.0
flow = lambda t: S - (m0 + dm * t)
PV = lambda T: integrate.quad(lambda t: flow(t) * math.exp(-r * t), 0, T)[0]
T_pay = optimize.brentq(lambda T: PV(T) - C0, 0.5, life)
T_simple = optimize.brentq(lambda T: integrate.quad(flow, 0, T)[0] - C0, 0.5, life)
out(C0=C0, S=S, m0=m0, dm=dm, r=r, life=life, PV_life=PV(life), NPV=PV(life) - C0, T_pay=T_pay, T_simple=T_simple,
    PV_nodisc=integrate.quad(flow, 0, life)[0])
# 分期付款：车价 15 万元，每年连续还 3.36 万元，5 年，求年利率
out(car_r=100 * optimize.brentq(lambda r: 3.36 * (1 - math.exp(-5 * r)) / r - 15, 0.001, 0.5))
# 消费者剩余：需求 p = 100 − 2q（元），市场价 40 元
qe = (100 - 40) / 2
out(CS=integrate.quad(lambda q: (100 - 2 * q) - 40, 0, qe)[0], qe=qe)
# 指示剂稀释：注入 5 mg，c(t) = 3.75 t² e^{−t/2}（mg/L），每 2 s 采样，0～24 s
A = 5.0
c = lambda t: 3.75 * t * t * math.exp(-t / 2)
ts = [2 * k for k in range(13)]
out(dye_tab="，".join(f"{c(t):.2f}" for t in ts))
I_s, I_t, I_ex = simpson(c, 0, 24, 12), trap(c, 0, 24, 12), integrate.quad(c, 0, math.inf)[0]
out(dye_Is=I_s, dye_It=I_t, dye_Iex=I_ex, CO_s=A / I_s * 60, CO_ex=A / I_ex * 60)
# 泊肃叶流动：管半径 R、中心流速 vmax，流量 πR²vmax/2；冷却管 R = 4 mm、vmax = 0.3 m/s
Rp, vmax = 0.004, 0.3
Q = integrate.quad(lambda rr: 2 * math.pi * rr * vmax * (1 - rr * rr / Rp ** 2), 0, Rp)[0]
out(Q_Lmin=Q * 1000 * 60, Q_ex=math.pi * Rp * Rp * vmax / 2 * 1000 * 60, v_mean=Q / (math.pi * Rp * Rp))
