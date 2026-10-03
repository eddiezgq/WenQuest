"""本章“部分习题答案”中的数值。"""
import json
import math
from pathlib import Path

import numpy as np

from bookout import out

# 习题 2.1.8：肩关节误差 0.01°，腕心误差不超过 0.15 mm，肘关节误差上限
e = json.loads((Path(__file__).resolve().parents[2] / "models" / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))
js = {j["name"]: j for j in e["robot"]["joints"]}
l1, l2 = js["elbow_joint"]["origin"]["xyz"][2], js["wrist_1_joint"]["origin"]["xyz"][2]
d1 = math.radians(0.01)
d2 = (0.15e-3 - (l1 + l2) * d1) / l2
out(e218=math.degrees(d2))

# 习题 2.1.9：∛10，从 [2, 3] 出发，区间长度 2^(−k) < 10^(−6)
k = math.ceil(math.log2(1e6))
out(e219_k=k, e219=10 ** (1 / 3))

# 习题 2.2.6：每 0.1 s 记录时线性插值的最大误差
T, D = 2.0, 90.0
th = lambda t: D * (10 * (t / T) ** 3 - 15 * (t / T) ** 4 + 6 * (t / T) ** 5)
tt = np.linspace(0, T, 40001)
err = lambda dt: float(np.abs(np.interp(tt, np.arange(0, T + 1e-9, dt), th(np.arange(0, T + 1e-9, dt))) - th(tt)).max())
out(e226_025=err(0.25), e226_01=err(0.1), e226_ratio=err(0.25) / err(0.1))

# 习题 2.3.8：膝关节第一项振幅最大可取多少，使曲线在 [−120°, −65°] 内
t1 = np.linspace(0, 0.5, 20001)
ok = lambda A: (lambda y: y.max() <= -65 and y.min() >= -120)(-90 + A * np.sin(4 * np.pi * t1) + 6 * np.sin(8 * np.pi * t1 + 0.6))
lo, hi = 20.0, 40.0
for _ in range(50):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if ok(m) else (lo, m)
out(e238=lo)

# 习题 2.4.4（1）、2.4.5、2.4.8
out(e244=math.log(2) / (math.log(3) - math.log(2)), e245_rad=math.pi, e245_1rad=math.degrees(1), e245_001=math.degrees(0.01),
    e248=5730 * math.log2(10))

# 习题 2.4.6：目标 (0.6, 0) 的“肘上”解（肘关节在连线上方，θ2 < 0 时上臂在下方……按 θ1 较大的一组）
px, py = 0.6, 0.0
c2 = (px * px + py * py - l1 * l1 - l2 * l2) / (2 * l1 * l2)
sols = []
for s in (+1, -1):
    t2 = s * math.acos(c2)
    t1_ = math.atan2(py, px) - math.atan2(l2 * math.sin(t2), l1 + l2 * math.cos(t2))
    sols.append((math.degrees(t1_), math.degrees(t2)))
up = max(sols)                              # 肩关节角较大（上臂朝上）的一组
out(e246_t1=up[0], e246_t2=up[1], e246_rmin=abs(l1 - l2), e246_rmax=l1 + l2)

# 习题 2.4.7：1.1^x 与 x^20（x > 1）的交点：比较 x ln 1.1 与 20 ln x
G = lambda x: x * math.log(1.1) - 20 * math.log(x)
xs = np.linspace(1.0001, 2000, 2000001)
gs = xs * math.log(1.1) - 20 * np.log(xs)
idx = np.nonzero(np.diff(np.sign(gs)))[0]
roots = []
for i in idx:
    a, b = xs[i], xs[i + 1]
    for _ in range(60):
        m = (a + b) / 2
        a, b = (m, b) if G(a) * G(m) > 0 else (a, m)
    roots.append((a + b) / 2)
out(e247_n=len(roots), e247_r1=roots[0], e247_r2=roots[1])

# 习题 2.6.5：垂度不超过 1 m 时 a 的下限（垂度随 a 增大而减小）
L = 10.0
sag = lambda a: a * (math.cosh(L / a) - 1)
lo, hi = 10.0, 200.0
for _ in range(80):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if sag(m) > 1 else (lo, m)
out(e265_a=hi, e265_extra=(2 * hi * math.sinh(L / hi) - 2 * L) * 1000)

# 习题 2.6.6：x = 1e−8 时按定义计算 sinh 的相对误差
x = 1e-8
out(e266_def=abs((math.exp(x) - math.exp(-x)) / 2 - math.sinh(x)) / math.sinh(x))

# 习题 2.7.3：最高速度 2 m/s 达不到，速度曲线为三角形
a, S = 0.5, 5.0
out(e273_tp=math.sqrt(S / a), e273_vp=math.sqrt(a * S), e273_T=2 * math.sqrt(S / a))

# 习题 2.8.4：弹簧
xx = np.array([1, 2, 3, 4, 5.0])
F = np.array([2.1, 3.9, 6.2, 7.8, 10.1])
k1, b1 = np.polyfit(xx, F, 1)
out(e284_k=k1, e284_b=b1, e284_k0=float((xx @ F) / (xx @ xx)))

# 习题 2.8.7：摆
l = np.array([0.2, 0.4, 0.6, 0.8, 1.0])
Tp = np.array([0.90, 1.27, 1.55, 1.79, 2.01])
kk, bb = np.polyfit(np.log10(l), np.log10(Tp), 1)
C = 10**bb                                   # T ≈ C l^k，k ≈ 1/2 时 C = 2π/√g
out(e287_k=kk, e287_g=(2 * math.pi / float(np.mean(Tp / np.sqrt(l)))) ** 2)

# 习题 2.8.8：月平均气温的正弦模型
m = np.arange(1, 13, dtype=float)
Tm = np.array([-4, -1, 6, 14, 20, 25, 27, 26, 21, 13, 5, -2], dtype=float)
A = np.column_stack([np.ones(12), np.sin(2 * np.pi * m / 12), np.cos(2 * np.pi * m / 12)])
c, *_ = np.linalg.lstsq(A, Tm, rcond=None)
amp = math.hypot(c[1], c[2])
peak = (math.atan2(c[1], c[2]) / (2 * math.pi) * 12) % 12
out(e288_mean=float(c[0]), e288_amp=amp, e288_peak=peak, e288_rms=float(np.sqrt(np.mean((Tm - A @ c) ** 2))))
