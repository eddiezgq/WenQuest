"""第 23 章 缝纫机的设计、制造与检测 —— 课程包数值题计算（数据取自教材 23.3、23.6 节与虚拟实验 23-1 的模型）"""
import math
import numpy as np
from scipy.stats import norm

# ---------- 23.3 梭尖间隙尺寸链（八个环，公差为示意值，与虚拟实验 23-1 相同）----------
# (名称, 公差 ±mm, 调整吸收, 换针时变)
CHAIN = [("针杆套孔位置", 0.03, 1, 0), ("针杆与针杆套的游隙", 0.008, 0, 0), ("针夹孔偏移", 0.02, 1, 0),
         ("机针凹口面尺寸", 0.02, 0, 1), ("机针安装偏转", 0.015, 0, 1), ("旋梭轴孔位置", 0.03, 1, 0),
         ("梭尖到安装基准", 0.02, 1, 0), ("旋梭轴径向游隙", 0.01, 0, 0)]
G0, GMIN, GMAX, ADJ = 0.07, 0.04, 0.10, 0.01
tol = np.array([c[1] for c in CHAIN])
wc = tol.sum()
sg = math.sqrt(((tol / 3) ** 2).sum())


def yield_normal(sigma, half=0.03):
    return 2 * norm.cdf(half / sigma) - 1


print("极值法 ±", round(wc, 3), " 统计法 σg", round(sg, 4), " 合格率(解析)", round(yield_normal(sg), 3),
      " 每1000台不合格", round((1 - yield_normal(sg)) * 1000))
# 均匀收紧到 99%
k = 0.03 / norm.ppf(0.995) / sg
print("99% 需 σg ≤", round(0.03 / norm.ppf(0.995), 4), " 收紧系数", round(k, 2))
# 装配调整：剩调整误差、针杆游隙、旋梭轴径向游隙、机针两环（调整时吸收）
rem = [ADJ] + [c[1] for c in CHAIN if not c[2] and not c[3]]
sa = math.sqrt(sum((t / 3) ** 2 for t in rem))
print("调整后 σ", round(sa, 4), " 合格率", round(yield_normal(sa), 5))
# 调整后换针：机针两环回来（新针 + 原针误差被调整吸收的部分 → 两倍方差）
needle = [c[1] for c in CHAIN if c[3]]
ss = math.sqrt(sa ** 2 + 2 * sum((t / 3) ** 2 for t in needle))
print("调整后换针 σ", round(ss, 4), " 合格率", round(yield_normal(ss), 4))

# 蒙特卡罗（与虚拟实验 23-1 相同的规则，numpy 随机数，结果与教材图 23-4 同量级）
rng = np.random.default_rng(7)
N = 4000
e = rng.standard_normal((N, 8)) * tol / 3
g_int = G0 + e.sum(1)
absorbed = np.array([c[2] for c in CHAIN], bool)
chg = np.array([c[3] for c in CHAIN], bool)
keep = ~absorbed & ~chg
g_adj = G0 + rng.standard_normal(N) * ADJ / 3 + e[:, keep].sum(1)
g_swap = g_adj + (rng.standard_normal((N, chg.sum())) * tol[chg] / 3 - e[:, chg]).sum(1)
for name, g in (("互换", g_int), ("调整", g_adj), ("调整后换针", g_swap)):
    print("MC", name, round(((g >= GMIN) & (g <= GMAX)).mean(), 4), " σ", round(g.std(), 4))

# 习题 1、2 复核
t4 = np.array([0.03, 0.02, 0.02, 0.01])
s4 = math.sqrt(((t4 / 3) ** 2).sum())
print("习题1 极值 ±", t4.sum(), " 统计 ±", round(3 * s4, 3), " 习题2 σ", round(s4, 4), "合格率", round(yield_normal(s4), 3))
s4a = math.sqrt((0.01 / 3) ** 2 + (0.01 / 3) ** 2)
print("     调整后 σ", round(s4a, 4), " 合格率", round(yield_normal(s4a), 6))

# ---------- 23.6 共振 ----------


def amp(r, z):
    return 1 / math.sqrt((1 - r * r) ** 2 + (2 * z * r) ** 2)


def vib(n, fn=190, z=0.03, m=1.0, K=1e8, F1=300, F2=120, N0=5000):
    k = K * (fn / 190) ** 2
    vs = []
    for order, F0 in ((1, F1), (2, F2)):
        f = order * n / 60
        r = f / fn
        F = F0 * m * (n / N0) ** 2
        X = F / k * amp(r, z)
        vs.append(2 * math.pi * f * X / math.sqrt(2) * 1000)
    return math.hypot(*vs)


VREF = vib(5000)


def noise(n, **kw):
    return 83.5 + 20 * math.log10(vib(n, **kw) / VREF)


for n in (5000, 5500):
    r = 2 * n / 60 / 190
    print("n", n, " f2", round(2 * n / 60, 1), " r", round(r, 3), " 放大", round(amp(r, 0.03), 2),
          " v mm/s", round(vib(n), 2), " 噪声", round(noise(n), 1))
fn2 = 190 * math.sqrt(1.3)
print("加筋 fn", round(fn2, 1), " r", round(2 * 5500 / 60 / fn2, 3), " v", round(vib(5500, fn=fn2), 2), " 噪声", round(noise(5500, fn=fn2), 1),
      " 共振转速", round(fn2 * 30))
for z in (0.06, 0.10):
    print("阻尼", z, " v", round(vib(5500, z=z), 2))
for m in (0.8, 0.6):
    print("减重", m, " v", round(vib(5500, m=m), 2))
# 扫描峰值
ns = np.arange(2000, 6001, 10)
vv = [vib(n) for n in ns]
print("扫描峰值转速", ns[int(np.argmax(vv))])
# 惯性力增加
print("转速 +10% 惯性力 ×", round(1.1 ** 2, 2), " 368 N →", round(368 * 1.21))
# 习题 3 复核
for fn in (200, 240):
    r = 2 * 5800 / 60 / fn
    print("习题3 fn", fn, " r", round(r, 3), " 放大", round(amp(r, 0.04), 2))

# ---------- 课程题 ----------
# 测验：三环 ±0.03, ±0.03, ±0.02 统计法
t3 = np.array([0.03, 0.03, 0.02])
print("Q 三环 极值", t3.sum(), " 统计 ±", round(3 * math.sqrt(((t3 / 3) ** 2).sum()), 4))
# 测验：放大倍数 r=0.9, ζ=0.05
print("Q 放大 r0.9 z0.05", round(amp(0.9, 0.05), 2))
# 测验：二阶激振频率 4800 r/min
print("Q f2@4800", 2 * 4800 / 60)
# 测验：噪声 振动 ×3
print("Q 噪声 振动×3:", round(20 * math.log10(3), 2))
# 考试：共振转速 fn 210 Hz 二阶
print("E 二阶共振转速 fn=210:", 210 * 30)
# 考试：σ 0.012 合格率
print("E σ0.012 合格率", round(yield_normal(0.012) * 100, 2))
# 考试：fn 180 Hz, ζ 0.03, 5200 r/min
r = 2 * 5200 / 60 / 180
print("E fn180 n5200 r", round(r, 3), " 放大", round(amp(r, 0.03), 2))
# 作业：五环尺寸链
t5 = np.array([0.025, 0.02, 0.015, 0.01, 0.01])
s5 = math.sqrt(((t5 / 3) ** 2).sum())
print("A 五环 极值", t5.sum(), " σ", round(s5, 4), " 合格率 ±0.03", round(yield_normal(s5), 4))
s5a = math.sqrt((0.01 / 3) ** 2 + (0.01 / 3) ** 2 + (0.01 / 3) ** 2)
print("A 调整后（剩调整误差 + 后两环）σ", round(s5a, 4), " 合格率", round(yield_normal(s5a), 6))
# 作业：fn 200 Hz, ζ 0.03, 最高 5800；加筋到 250 Hz
for fn in (200, 250):
    r = 2 * 5800 / 60 / fn
    print("A fn", fn, " r", round(r, 3), " 放大", round(amp(r, 0.03), 2), " 共振转速", fn * 30)
# 作业：B10 —— 韦布尔
beta_w, eta = 2.5, 8000
print("A B10 h", round(eta * (-math.log(0.9)) ** (1 / beta_w)))
