"""算例 13.5.1–13.5.3：相邻关节轴接近平行时 DH 参数的突变，哈亚蒂参数，以及一台 UR 机器人的实际标定数据。

几何：轴 i 为 {i−1} 的 z 轴（过原点、竖直）；轴 i+1 名义上与它平行，相距 a = 0.425 m（UR5e 关节 2、3 之间，即大臂长），
经过点 (a, 0, 0)。把轴 i+1 偏转一个小角 ε：方向 (sin ε cos φ, −sin ε sin φ, cos ε)，φ = 0 时偏转在两轴所在的平面内，
φ = 90° 时垂直于该平面。
13.5.1 按 DH 的规则（公垂线，13.1.2 节）求 a_i、α_i、d_i；ε 从 0.001° 到 1°。
13.5.2 按哈亚蒂的参数化 Rot(z, θ) Trans(x, a) Rot(x, α) Rot(y, β) 求 a、α、β；再看旋量轴怎样变化。三种参数化都用
       “由参数重建直线，与原直线比较”的办法核对。
13.5.3 UR ROS 2 驱动文档中给出的一台 UR 机器人的出厂标定 DH 参数：d₂、d₃ 达到数百米，而 d₂ tan α₂ 与 d₂ + d₃ + d₄
       分别接近 UR10e 的名义 a₂ 和 d₄。
"""
import math

import numpy as np

from _dh import common_normal, screw_revolute
from bookout import out

A = 0.425


def tilted(eps, phi=0.0):
    u = np.array([math.sin(eps) * math.cos(phi), -math.sin(eps) * math.sin(phi), math.cos(eps)])
    return np.array([A, 0, 0.0]), u


def dh_of(eps, phi=0.0):
    """DH：两条直线的公垂线。平行时按规则取过原点的一条（d = 0）。返回 (a, α, d)。"""
    p, u = tilted(eps, phi)
    kind, f1, f2, dist, n = common_normal((0, 0, 0), (0, 0, 1), p, u)
    if kind == "parallel":
        return dist, 0.0, 0.0
    alpha = math.atan2(float(np.cross([0, 0, 1.0], u) @ n), float(u[2]))
    # 由参数重建：轴 i+1 应过 f1 + a n，方向为绕 n 把 z 转 α
    rebuilt = f1 + dist * n
    assert np.linalg.norm(np.cross(rebuilt - p, u)) < 1e-6 * max(1.0, abs(f1[2]))
    return dist, alpha, float(f1[2])


def hayati_of(eps, phi=0.0):
    """哈亚蒂：取轴 i+1 与 {i−1} 的 xy 平面（z = 0）的交点，Rot(z, θ) Trans(x, a) 到达交点，再 Rot(x, α) Rot(y, β) 对准方向。"""
    p, u = tilted(eps, phi)
    t = -p[2] / u[2]
    P = p + t * u
    a = math.hypot(P[0], P[1])
    th = math.atan2(P[1], P[0])
    c, s = math.cos(-th), math.sin(-th)
    ul = np.array([c * u[0] - s * u[1], s * u[0] + c * u[1], u[2]])         # 方向在 Rot(z, θ) 之后的坐标系中
    beta = math.asin(ul[0])
    alpha = math.atan2(-ul[1], ul[2])
    # 核对：Rot(x, α) Rot(y, β) e_z = (sin β, −sin α cos β, cos α cos β)
    assert np.allclose([math.sin(beta), -math.sin(alpha) * math.cos(beta), math.cos(alpha) * math.cos(beta)], ul, atol=1e-12)
    return a, alpha, beta


S0 = screw_revolute((0, 0, 1.0), (A, 0, 0))


def sci(x):
    """1.75e-05 → 1.75 × 10^{-5}（LaTeX）。"""
    m, e = f"{x:.2e}".split("e")
    return f"{m}\\times 10^{{{int(e)}}}"


eps_deg = [0.001, 0.01, 0.1, 1.0]
rows, d_in, d_out, dS = [], [], [], []
for e in eps_deg:
    eps = math.radians(e)
    a1, al1, d1 = dh_of(eps, 0.0)
    a2, al2, d2 = dh_of(eps, math.pi / 2)
    ha, hal, hb = hayati_of(eps, 0.0)
    p, u = tilted(eps, 0.0)
    ds = float(np.linalg.norm(screw_revolute(u, p) - S0))
    d_in.append(d1)
    d_out.append(d2)
    dS.append(ds)
    z = lambda x, n: "0" if abs(x) < 0.5 * 10 ** (-n) else f"{x:.{n}f}"   # noqa: E731
    rows.append(f"| ${e:g}^\\circ$ | {z(a1, 3)} | ${z(d1, 1)}$ | {z(a2, 3)} | ${z(d2, 1)}$ | {z(ha, 3)} | ${math.degrees(hb):g}^\\circ$ | ${sci(ds)}$ |")
rows = "\n".join(rows)

# 平行时（ε = 0）
a0, al0, dd0 = dh_of(0.0)
assert abs(a0 - A) < 1e-12 and dd0 == 0.0
# 小角度时 d ≈ −a / ε（面内偏转），对比精确值 −a cot ε
e01 = math.radians(0.01)
d01 = dh_of(e01)[2]
assert abs(d01 - (-A / math.tan(e01))) < 1e-6 * abs(d01)
# 正负 ε：d 由 −∞ 跳到 +∞
d_neg = dh_of(-e01)[2]
assert d_neg > 0 > d01
# 哈亚蒂参数连续：β = ε，a 不变
for e in eps_deg:
    ha, hal, hb = hayati_of(math.radians(e))
    assert abs(hb - math.radians(e)) < 1e-12 and abs(ha - A) < 1e-12
# 灵敏度：ε = 0.01° 时，ε 改变 0.001°，d 改变多少
de = math.radians(0.001)
dd_sens = dh_of(e01 + de)[2] - d01

# ---------------------------------------------------------------- 13.5.3 实际标定数据（UR ROS 2 驱动文档 ur_calibration “Calibration correction algorithm”）
cal_d = [0.180539811714259, 439.140974079901, -446.027059806332, 7.0603368964236, 0.119811341150314, 0.115670917257426]
cal_a = [2.12234865571206e-05, 0.0193171326277006, -0.569251663611088, -4.61409023720934e-05, -6.39280053471802e-05, 0.0]
cal_alpha = [1.57014608044242, 0.0013941666682559, 0.00693818880325995, 1.56998468543761, -1.57038520649543, 0.0]
ur10e = {"d1": 0.1807, "a2": -0.6127, "a3": -0.57155, "d4": 0.17415, "d5": 0.11985, "d6": 0.11655}   # UR 公布的 UR10e 名义值
ur16e_a2 = -0.4784                                    # UR 公布的 UR16e 大臂（d₁、d₄、d₅、d₆ 与 UR10e 相同）
arm = cal_d[1] * math.tan(cal_alpha[1])
# 型号推断（文档未注明型号）：三个偏距与 UR10e 名义值差不到 1 mm，大臂长度与 UR10e 吻合而与 UR16e 相去甚远
for k, v in (("d1", cal_d[0]), ("d5", cal_d[4]), ("d6", cal_d[5])):
    assert abs(v - ur10e[k]) < 1e-3
assert abs(arm - abs(ur10e["a2"])) < 1e-3 and abs(arm - abs(ur16e_a2)) > 0.1
dsum = cal_d[1] + cal_d[2] + cal_d[3]

out(A=A, rows=rows, d01=d01, d_neg=d_neg, dd_sens=dd_sens, beta01=math.degrees(hayati_of(e01)[2]),
    cal_d2=cal_d[1], cal_d3=cal_d[2], cal_d4=cal_d[3], cal_al2=cal_alpha[1], cal_al2_deg=math.degrees(cal_alpha[1]),
    cal_d1=cal_d[0], cal_d5=cal_d[4], cal_d6=cal_d[5], cal_a3=cal_a[2],
    arm=arm, dsum=dsum, n_a2=ur10e["a2"], n_d4=ur10e["d4"], n_d1=ur10e["d1"], n_d5=ur10e["d5"], n_d6=ur10e["d6"], n_a3=ur10e["a3"], ur16e_a2=abs(ur16e_a2),
    eps_deg=eps_deg, d_in=d_in, d_out=d_out, dS=dS)
