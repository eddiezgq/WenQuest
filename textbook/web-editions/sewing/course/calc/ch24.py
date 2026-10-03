"""第 24 章 机针与旋梭的制造 —— 课程包数值题计算（数据取自教材 24.1–24.8 节；选配用教材 figsrc/ch24_model.py 的同一模型）"""
import math
import sys
from pathlib import Path
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "figsrc"))
import ch24_model as M  # noqa: E402  教材模型（与虚拟实验 24-1 相同的随机数）

Phi = norm.cdf

# ---------- 24.1 机针消耗 ----------
print("年耗针", 300 * 0.5 * 300)

# ---------- 24.2 刚度与减面率 ----------
rel = lambda nm, ref=90: (nm / ref) ** 4
print("Nm110/90", round(rel(110), 2), " Nm70/90", round(rel(70), 2), " Nm110/70", round((110 / 70) ** 4, 1))
print("DB×1 Nm90 截面比", round((0.9 / 1.62) ** 2, 3), " 减面率", round(1 - (0.9 / 1.62) ** 2, 3))
print("习题1 Nm80/100", round(rel(80, 100), 2))

# ---------- 24.5 旋梭工作条件 ----------
Rh, Rr = 0.0135, 0.012
for n in (3000, 4000, 5000, 5500):
    nh = 2 * n
    vh = 2 * math.pi * Rh * nh / 60
    vr = 2 * math.pi * Rr * nh / 60
    print("n", n, "梭尖 m/s", round(vh, 1), "梭道 m/s", round(vr, 1), "km/h", round(vr * 3.6))
print("掠过 0.9 mm μs", round(0.9e-3 / (2 * math.pi * Rh * 10000 / 60) * 1e6))

# ---------- 24.4 Cp/Cpk 与控制图 ----------
USL, LSL = 0.380, 0.340


def cp_cpk(mu, s, usl=USL, lsl=LSL):
    return (usl - lsl) / (6 * s), min(usl - mu, mu - lsl) / (3 * s)


def ppm(mu, s, usl=USL, lsl=LSL):
    return ((1 - Phi((usl - mu) / s)) + Phi((lsl - mu) / s)) * 1e6


print("算例估计 Cp/Cpk", [round(x, 2) for x in cp_cpk(0.3622, 0.0039)], " 真值 Cpk", round(cp_cpk(0.362, 0.004)[1], 2),
      " ppm", round(ppm(0.362, 0.004), 1))
print("漂移 1σ: Cpk", round(cp_cpk(0.366, 0.004)[1], 2), " ppm", round(ppm(0.366, 0.004)), " 倍数", round(ppm(0.366, 0.004) / ppm(0.362, 0.004)))
A2, D4 = 0.577, 2.114
print("控制限", round(0.3622 - A2 * 0.0091, 4), round(0.3622 + A2 * 0.0091, 4), " UCL_R", round(D4 * 0.0091, 4))


def arl(delta, n):
    p = Phi(-3 + delta * math.sqrt(n)) + Phi(-3 - delta * math.sqrt(n))
    return 1 / p


print("ARL0", round(arl(0, 5)))
for dl in (0.5, 1.0, 1.5):
    print(" δ", dl, [round(arl(dl, n), 1) for n in (2, 3, 4, 5, 6, 8)])
print("习题3 n=7 δ0.5", round(arl(0.5, 7), 1))
print("习题2 Cp", round(0.020 / 0.012, 2), " Cpk", round(0.007 / 0.006, 2))

# ---------- 24.7 选配 ----------
sc = 5 * math.sqrt(2)
print("互换 σc", round(sc, 2), " 合格率", round((2 * Phi(10 / sc) - 1) * 100, 1), " 99% 需每件 σ ≤", round(10 / 2.576 / math.sqrt(2), 2))
cases = [("互换", dict(k=1)), ("互换 σ2.6", dict(k=1, sD=2.6, sd=2.6)), ("2组", dict(k=2)), ("3组", dict(k=3)), ("4组", dict(k=4)),
         ("3组 sm2", dict(k=3, sm=2.0)), ("3组 梭道+4", dict(k=3, muD=4.0)), ("3组 +4 +4", dict(k=3, muD=4.0, mud=4.0)),
         ("3组 6/4", dict(k=3, sD=6.0, sd=4.0))]
for name, kw in cases:
    r = M.simulate(**kw)
    print(f" {name:10s} pass {r['pass_rate'] * 100:.1f}% left {r['left_rate'] * 100:.1f}% cost {r['cost']:.1f}")
# 习题 4
s4 = 4 * math.sqrt(2)
print("习题4 σc", round(s4, 2), " 合格率", round((2 * Phi(10 / s4) - 1) * 100, 1))

# ---------- 24.8 瓶颈 ----------
for name, minutes, cap in (("热处理线", 6, 1), ("抛光线", 6, 1), ("梭道磨床", 14, 2), ("数控车床", 18, 3), ("选配站", 3, 1)):
    print(" 单班产能", name, round(480 * cap / minutes, 1))

# ---------- 课程题 ----------
print("Q Nm100/Nm80 刚度", round((100 / 80) ** 4, 2))
print("Q 梭尖线速度 4500 r/min", round(2 * math.pi * Rh * 9000 / 60, 1))
print("Q Cpk 0.358 σ0.005", round(cp_cpk(0.358, 0.005)[1], 2))
print("Q ARL δ1 n4", round(arl(1.0, 4), 1))
print("Q 互换 σ 3μm 合格率", round((2 * Phi(10 / (3 * math.sqrt(2))) - 1) * 100, 1))
print("E 控制限 X̿=0.3605 R̄=0.0080 n5:", round(0.3605 - A2 * 0.008, 4), round(0.3605 + A2 * 0.008, 4), " σ̂", round(0.008 / 2.326, 5))
print("E Cpk(估计) 0.3605, σ̂", round(min(USL - 0.3605, 0.3605 - LSL) / (3 * 0.008 / 2.326), 2))
print("E 3 组组宽 μm", 30 / 3, " 4 组", 30 / 4)
print("E ARL δ1.5 n3", round(arl(1.5, 3), 1))
print("E 互换 99.5% 需 σc", round(10 / norm.ppf(0.9975), 2), " 每件", round(10 / norm.ppf(0.9975) / math.sqrt(2), 2))
# 作业
print("A Nm 120/90 刚度", round(rel(120), 2), " Nm 65/90", round(rel(65), 2))
print("A 直度单侧 Cpk USL0.03 μ0.012 s0.004", round((0.03 - 0.012) / 0.012, 2), " μ0.015 s0.005", round((0.03 - 0.015) / 0.015, 2))
for n in (3, 4, 5, 6, 7, 8, 9, 10):
    print(" A ARL δ0.8 n", n, round(arl(0.8, n), 1))
print("A 每班单产能 梭道磨床增至 3 台", round(480 * 3 / 14, 1))
