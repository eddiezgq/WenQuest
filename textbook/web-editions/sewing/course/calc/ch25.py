"""第 25 讲（机壳与凸轮的制造）数值题答案。运行：python3 course/calc/ch25.py"""
import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "figsrc"))
import ch25_model as M   # 教材的模型，用来核对 25.8 节的数字

w = lambda n: 2 * math.pi * n / 60
print("== 车间问题（24 阶 2 μm 振纹，6000 r/min）")
a_nom = 4.89 * 0.006 * w(6000) ** 2 / math.radians(150) ** 2
print("名义峰值加速度 m/s2", round(a_nom))                         # 1690
lim = 0.1 * a_nom
print("判据 10% m/s2", round(lim))                                 # 169
a24 = 2e-6 * (24 * w(6000)) ** 2
print("单个 24 阶 2um 分量 m/s2", round(a24, 1), "占名义", round(a24 / a_nom * 100, 1), "%")
print("只按此分量的允许转速", round(6000 * math.sqrt(lim / a24)))
for a0 in (469, 366):
    print("全部误差 a0 =", a0, "-> 允许转速", round(6000 * math.sqrt(lim / a0)))
c = M.CAMS['looper']
e = M.error_curve(c, 'mtrap', k=24, ek=2.0)
for name, ee in (("磨后", e), ("补偿一轮", M.compensate(e))):
    r = M.evaluate(c, 'mtrap', ee, 6000)
    print("模型", name, round(r['size'], 1), round(r['pv'], 1), round(r['aemax']), "n_allow", round(M.n_allow(c, 'mtrap', ee)))
e = M.error_curve(c, 'mtrap')
for name, ee in (("默认磨后", e), ("默认补偿一轮", M.compensate(e))):
    r = M.evaluate(c, 'mtrap', ee, 6000)
    print("模型", name, round(r['size'], 1), round(r['pv'], 1), round(r['aemax']))
print("惯性力 60 g × 469", round(0.06 * 469, 1), "N；频率", 24 * 100, "Hz")

print("== 表 25-7 每 μm 的加速度误差")
for k in (1, 2, 3, 6, 12, 24, 36):
    print(k, round(1e-6 * (k * w(6000)) ** 2, 2))

print("== 测验")
# Q 热膨胀：Ø25，温升 40 K
print("q 过盈减少 um", round(25 * (23 - 11.5) * 1e-6 * 40 * 1000, 2))           # 11.5
# Q 工序尺寸链：H0 = 40 ± 0.04，A1 = 120 ± 0.025
print("q A2", 120 - 40, "极值 ±", round(0.04 - 0.025, 4), "统计 ±um", round(math.sqrt(0.04**2 - 0.025**2) * 1000, 1))
# Q 12 阶 1.5 μm，5000 r/min
print("q 12阶 1.5um 5000rpm m/s2", round(1.5e-6 * (12 * w(5000)) ** 2, 1))
# Q 误差复映：16 μm，ε=0.25，2 次
print("q 复映 um", 16 * 0.25 ** 2)
# Q 调头镗：δc=3 μm、Δθ=6″、L=180 mm
dth = math.radians(6 / 3600)
print("q 调头镗 um", round(2 * 3 + 180e3 * dth, 2))
# Q 时效：σ = 30 MPa 全部释放
def drift(sig, t=2, h=70, B=60, wall=7, L=250, E=120e3):
    I = (h * B**3 - (h - 2 * wall) * (B - 2 * wall) ** 3) / 12
    F = sig * t * h; Mo = F * (B / 2 - t / 2)
    return Mo / (E * I) * L**2 / 2 * 1000, I
print("I mm4", round(drift(40)[1]), "40MPa 全释放 um", round(drift(40)[0], 1), "一半", round(drift(40)[0] / 2, 1))
print("q 30MPa 全释放 um", round(drift(30)[0], 1), "释放一半", round(drift(30)[0] / 2, 1))
print("== 考试")
print("e 砂轮小 0.05mm、α=12°：尺寸 um", 50, "形状 um", round(50 * (1 / math.cos(math.radians(12)) - 1), 2))
print("e 18 阶 1.2um 5500rpm a=", round(1.2e-6 * (18 * w(5500)) ** 2, 1), "限 120 -> n=", round(5500 * math.sqrt(120 / (1.2e-6 * (18 * w(5500)) ** 2))))
print("e 极值法 H0=25±0.02, A1 ±0.012 -> ±", round(0.02 - 0.012, 3), " 统计 ±", round(math.sqrt(0.02**2 - 0.012**2), 4))
print("e 峰值加速度 摆线 h=4mm β=120° 5000rpm", round(2 * math.pi * 0.004 * w(5000) ** 2 / math.radians(120) ** 2))
print("== 作业")
print("hw 铝机壳 Ø30 温升 35K 过盈减少 um", round(30 * (23 - 11.5) * 1e-6 * 35 * 1000, 2))
print("hw 尺寸链 H0=28±0.03, A1=100±0.018: A2=72, 极值 ±", round(0.03 - 0.018, 3), "统计 ±", round(math.sqrt(0.03**2 - 0.018**2), 4))
print("hw 8阶 2.5um 6000rpm", round(2.5e-6 * (8 * w(6000)) ** 2, 1))
# 作业第 3 题：一只弯针凸轮的谐波（μm），6000 r/min
H = {2: 4.0, 3: 2.0, 8: 2.5, 24: 0.8}
parts = {k: v * 1e-6 * (k * w(6000)) ** 2 for k, v in H.items()}
print("hw 各阶 m/s2", {k: round(v, 1) for k, v in parts.items()}, "上界和", round(sum(parts.values()), 1))
print("hw 按上界和的允许转速", round(6000 * math.sqrt(169 / sum(parts.values()))))
