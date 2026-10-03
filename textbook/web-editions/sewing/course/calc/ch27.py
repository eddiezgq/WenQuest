"""第 27 讲（数字工厂）数值题答案。质量闭环、负荷、分期回收直接调用教材模型 figsrc/ch27_model.py 核对。
运行：python3 course/calc/ch27.py"""
import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "figsrc"))
import ch27_model as M

phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
def pout(m, sig=0.006, lsl=0.040, usl=0.100):
    return 1 - phi((usl - m) / sig) + phi((lsl - m) / sig)

print("== 车间问题（梭尖间隙漂移）")
print("X̄ 控制限 ±mm", round(3 * 0.006 / math.sqrt(5), 5), "2σ", round(2 * 0.006 / math.sqrt(5), 5), "1σ", round(0.006 / math.sqrt(5), 5))
for h in (3, 4, 5, 6):
    print("漂移", h, "h 后超差概率 %", round(pout(0.070 + 0.004 * h) * 100, 2))
for name, rules in (("R1", ("R1",)), ("R1-R4", M.RULES)):
    o = M.outcome(M.Q, rules)
    print(name, o["n_alarm"], round(o["t_alarm"], 2), "受影响", o["affected"], o["first"], o["last"], "返工", o["rework"], "发货", o["shipped"], "剩", o["lot_left"])
o = M.outcome(M.Q, by="tol")
print("只按超差", o["n_alarm"], round(o["t_alarm"], 2), o["affected"], o["rework"], o["shipped"])
print("台/h", 22.5, "第 46 台起 =", round(2 * 22.5) + 1)

print("== 负荷")
for r in M.loads():
    print(r)
print("HMC 每台 16 min，5×2 班×480×0.60 =", 5 * 2 * 480 * 0.6, "min → 能力", 5 * 2 * 480 * 0.6 / 16, "台；OEE 68% 负荷 %", round(180 * 16 / (4800 * 0.68) * 100, 1))
print("== 分期")
sv = [sum(s.values()) for s in M.savings()]
print("年节省", [round(x, 1) for x in sv]); cum, pay = M.cashflow(M.PH, sv)
print("回收月", pay, "5 年", round(cum[-1], 1), "最低", round(min(cum), 1))
print("只第一期", M.cashflow(M.PH[:1], sv[:1])[1], round(M.cashflow(M.PH[:1], sv[:1])[0][-1], 1))
b = dict(M.BASE, oee1=0.64); sv64 = [sum(s.values()) for s in M.savings(b)]
print("OEE 64%：回收月", M.cashflow(M.PH, sv64, b)[1])
print("== Weibull")
print("平均寿命 h", round(5000 * math.gamma(1 + 1 / 2.2)))
R = lambda t, b=2.2, e=5000: math.exp(-(t / e) ** b)

print("== 测验")
print("q UCL（σ=8um,n=4）mm", round(0.070 + 3 * 0.008 / 2, 4))
print("q HMC 200 台 负荷 %", round(200 * 16 / (5 * 960 * 0.6) * 100, 1), "；≤90% 需 OEE %", round(200 * 16 / (5 * 960 * 0.9) * 100, 1))
print("q 变型 2^4×3 − 8 =", 2 ** 4 * 3 - 8)
print("q Weibull a=3000 Δ=250 P %", round((1 - R(3250) / R(3000)) * 100, 2))
print("q 漂移 3 h 超差 %", round(pout(0.082) * 100, 3))
print("q 库存周转 4→6 年节省 万元", (6000 / 4 - 6000 / 6) * 0.2)
print("== 考试")
print("e OEE for 85% load at 200/day %", round(200 * 16 / (4800 * 0.85) * 100, 1))
print("e 新固件故障率 /千h", round(30 / 135, 3), "旧版本 0.62 → 预期次数", round(0.62 * 135, 1))
print("e 按平均寿命季度需求", round(4000 * 800 * 0.25 / 4430, 1))
print("e n=3 控制限 ±mm", round(3 * 0.006 / math.sqrt(3), 5))
print("e OEE 60→70% 节省 万元", round(800 * (1 - 60 / 70), 1))
print("== 作业")
print("hw 220 台/天 HMC 负荷 %", round(220 * 16 / (5 * 960 * 0.6) * 100, 1), "OEE 68% 时", round(220 * 16 / (5 * 960 * 0.68) * 100, 1), "需 OEE ≤90%:", round(220 * 16 / (4800 * 0.9) * 100, 1), "或增 1 台 OEE 0.68:", round(220 * 16 / (6 * 960 * 0.68) * 100, 1))
print("hw 6 台 0.60:", round(220 * 16 / (6 * 960 * 0.6) * 100, 1))
print("hw 控制限 σ=5um n=5: ±", round(3 * 0.005 / math.sqrt(5), 5))
for h in (2, 4, 6):
    print("hw 漂移 5um/h σ=5um h=", h, "P %", round(pout(0.070 + 0.005 * h, sig=0.005) * 100, 2))
print("hw Weibull a=1000 vs 4000，Δ=225:", round((1 - R(1225) / R(1000)) * 100, 2), round((1 - R(4225) / R(4000)) * 100, 2))
