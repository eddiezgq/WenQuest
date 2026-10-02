"""算例 10.5.1–10.5.3：自然坐标，切向加速度与法向加速度，曲率。

算例 10.5.1：UR5e 的工具尖沿半径 R = 0.10 m 的水平圆去毛刺，从静止起以切向加速度 0.5 m/s² 加速到 0.25 m/s 后匀速。
  求加速段中点和加速结束时的切向、法向加速度与总加速度；用直角坐标数值求导核对，并用 κ = |v × a|/|v|³ 核对曲率。
算例 10.5.2：10.2 节的涂胶椭圆。曲率的最大、最小值；若要求匀速涂胶且法向加速度不超过 1.0 m/s²，允许的最高速率与一圈的时间。
  另求 10.2 节匀角速度参数化在 t = 0.5 s 时的切向、法向加速度，与算例 10.2.1 的 |a| 核对。
算例 10.5.3：同一时刻的速度、加速度在直角、柱面、球面（原点在椭圆中心正上方 0.3 m 的相机光心）、自然四种坐标的局部基上的分量；四组分量的长度相同。
"""
import math

import numpy as np

from _kin import cyl_basis, d1, d2, sph_basis, to_sph
from bookout import out

# ---------------------------------------------------------------- 算例 10.5.1
R, at0, vmax = 0.10, 0.5, 0.25
t_acc = vmax / at0
c = np.array([-0.50, -0.20, 0.25])          # 圆心在 UR5e 基座坐标系中的位置，m


def s_of(t):                                 # 弧长 s(t)：先匀加速，后匀速
    return 0.5 * at0 * t * t if t <= t_acc else 0.5 * at0 * t_acc ** 2 + vmax * (t - t_acc)


def pos(t):
    u = s_of(t) / R
    return c + R * np.array([math.cos(u), math.sin(u), 0.0])


def natural(t):
    sd = at0 * t if t <= t_acc else vmax
    sdd = at0 if t < t_acc else 0.0
    return sdd, sd * sd / R                  # 式 (10.5.6)：a_t = s̈，a_n = κ ṡ²


res = {}
for name, t in (("mid", 0.5 * t_acc), ("end", t_acc - 1e-9)):
    a_t, a_n = natural(t)
    tt = min(t, t_acc - 2e-3)               # 数值求导取在加速段内部
    a_num = d2(pos, tt, 1e-4)
    v_num = d1(pos, tt, 1e-5)
    et = v_num / np.linalg.norm(v_num)
    at_n, an_n = natural(tt)
    assert abs(a_num @ et - at_n) < 1e-5 and abs(np.linalg.norm(a_num - (a_num @ et) * et) - an_n) < 1e-5
    kappa = np.linalg.norm(np.cross(v_num, a_num)) / np.linalg.norm(v_num) ** 3
    assert abs(kappa - 1 / R) < 1e-3
    res[name] = (a_t, a_n, math.hypot(a_t, a_n), math.degrees(math.atan2(a_n, a_t)))
s_acc = s_of(t_acc)

# ---------------------------------------------------------------- 算例 10.5.2
a, b = 0.12, 0.08
kmax, kmin = a / b ** 2, b / a ** 2
u = np.linspace(0, 2 * math.pi, 200001)
xp, yp = -a * np.sin(u), b * np.cos(u)
xpp, ypp = -a * np.cos(u), -b * np.sin(u)
kap = np.abs(xp * ypp - yp * xpp) / (xp ** 2 + yp ** 2) ** 1.5      # 式 (10.5.9)
assert abs(kap.max() - kmax) < 1e-6 and abs(kap.min() - kmin) < 1e-6
an_lim = 1.0
v0 = math.sqrt(an_lim / kmax)
ds = np.sqrt(xp ** 2 + yp ** 2)
L = float(np.sum((ds[1:] + ds[:-1]) / 2 * np.diff(u)))              # 梯形公式求周长
hh = ((a - b) / (a + b)) ** 2
L_ram = math.pi * (a + b) * (1 + 3 * hh / (10 + math.sqrt(4 - 3 * hh)))  # 拉马努金近似
assert abs(L - L_ram) < 1e-9
T_cycle = L / v0
# 10.2 节的参数化在 t = 0.5 s
w, t1 = math.pi / 2, 0.5
v1 = np.array([-a * w * math.sin(w * t1), b * w * math.cos(w * t1), 0])
a1 = np.array([-a * w * w * math.cos(w * t1), -b * w * w * math.sin(w * t1), 0])
sp = np.linalg.norm(v1)
k1 = np.linalg.norm(np.cross(v1, a1)) / sp ** 3
at1 = v1 @ a1 / sp
an1 = k1 * sp * sp
assert abs(math.hypot(at1, an1) - np.linalg.norm(a1)) < 1e-12

# ---------------------------------------------------------------- 算例 10.5.3：四种分解
xc, yc, z0 = 0.40, 0.05, 0.10
P = np.array([xc + a * math.cos(w * t1), yc + b * math.sin(w * t1), z0])
cam = np.array([0.40, 0.05, 0.40])          # 相机光心：椭圆中心正上方 0.3 m
comp = {}
comp["cart"] = (v1.copy(), a1.copy())
phi = math.atan2(P[1], P[0])
B = np.array(cyl_basis(phi))
comp["cyl"] = (B @ v1, B @ a1)
r, th, ph = to_sph(P - cam)
B = np.array(sph_basis(th, ph))
comp["sph"] = (B @ v1, B @ a1)
et = v1 / sp
en = (a1 - (a1 @ et) * et)
en /= np.linalg.norm(en)
eb = np.cross(et, en)
B = np.array([et, en, eb])
comp["nat"] = (B @ v1, B @ a1)
for k, (vv, aa) in comp.items():
    assert abs(np.linalg.norm(vv) - sp) < 1e-12 and abs(np.linalg.norm(aa) - np.linalg.norm(a1)) < 1e-12
assert abs(comp["nat"][0][1]) < 1e-15 and abs(comp["nat"][1][2]) < 1e-15
assert abs(comp["nat"][1][0] - at1) < 1e-12 and abs(comp["nat"][1][1] - an1) < 1e-12

vals = {}
for k, (vv, aa) in comp.items():
    for i in range(3):
        vals[f"{k}_v{i}"] = 0.0 if abs(vv[i]) < 1e-12 else float(vv[i])     # 舍入误差记为 0
        vals[f"{k}_a{i}"] = 0.0 if abs(aa[i]) < 1e-12 else float(aa[i])

out(R=R, at0=at0, vmax=vmax, t_acc=t_acc, s_acc=s_acc, s_acc_deg=math.degrees(s_acc / R),
    mid_at=res["mid"][0], mid_an=res["mid"][1], mid_a=res["mid"][2], mid_ang=res["mid"][3],
    end_at=res["end"][0], end_an=res["end"][1], end_a=res["end"][2], end_ang=res["end"][3],
    kmax=kmax, kmin=kmin, rmin=1 / kmax, rmax=1 / kmin, v0=v0, L=L, T_cycle=T_cycle, an_lim=an_lim,
    k1=float(k1), at1=float(at1), an1=float(an1), a1=float(np.linalg.norm(a1)), sp1=float(sp),
    cyl_phi_deg=math.degrees(phi), sph_r=r, sph_th_deg=math.degrees(th), sph_ph_deg=math.degrees(ph), **vals)
