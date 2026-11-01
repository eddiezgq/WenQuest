"""第 8 章共用：材料常数、截面、拉梅公式、赫兹接触、曲梁、莫尔圆。

- 材料：数字工厂材料库（经 mdstd.material；E、ν 用 MPa）；
- 关节力矩传感器：协作机器人肩关节空心轴 RJ-201（第 33 章：Ø50/Ø30、40Cr 调质；谐波减速器 CSF-25-100 的转矩取零件库）；
- WQR-105：输出轴 SH-301 B 版（第 33 章 _shaft.py）、齿轮与键的尺寸；第二级齿宽取数字工厂参数配置器的布置（40 mm）。
长度 mm，力 N，应力 MPa。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (ROOT / "factory", ROOT / "factory" / "digital", HERE.parents[1] / "conventions", HERE.parents[1] / "ch33" / "code"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import mdstd                            # noqa: E402
from bookout import COLORS, T           # noqa: E402

INK, MUTED, ACC = COLORS["ink"], COLORS["muted"], COLORS["accent"]


def mat(mid):
    m = mdstd.material(mid)
    E, nu = float(m["E"]), float(m["mu"])
    return {"id": mid, "name": m["name"], "E": E, "nu": nu, "G": E / (2 * (1 + nu)), "sy": m["sigma_s"], "sb": m["sigma_b"]}


# 线膨胀系数 1/K（典型值，本书取值；材料库里没有）
ALPHA = {"steel": 11.5e-6, "al": 23.0e-6}


# ---------------------------------------------------------------- 截面
def Wp_hollow(D, d):
    return math.pi * (D ** 4 - d ** 4) / (16 * D)


def J_hollow(D, d):
    return math.pi * (D ** 4 - d ** 4) / 32


# ---------------------------------------------------------------- 平面应力与莫尔圆
def principal2(sx, sy, txy):
    c, r = (sx + sy) / 2, math.hypot((sx - sy) / 2, txy)
    th = 0.5 * math.degrees(math.atan2(2 * txy, sx - sy))          # σ1 的方向（从 x 轴量起，逆时针）
    return c + r, c - r, th, r


def rosette_rect(e0, e45, e90):
    """直角应变花（0°、45°、90°）→ 主应变与 σ1 方向"""
    ex, ey, gxy = e0, e90, 2 * e45 - e0 - e90
    c, r = (ex + ey) / 2, math.hypot((ex - ey) / 2, gxy / 2)
    return c + r, c - r, 0.5 * math.degrees(math.atan2(gxy, ex - ey))


def strain_to_stress(e1, e2, E, nu):
    k = E / (1 - nu * nu)
    return k * (e1 + nu * e2), k * (e2 + nu * e1)


# ---------------------------------------------------------------- 厚壁圆筒（拉梅）
def lame(p_i, p_o, a, b, r):
    """内半径 a、外半径 b，内压 p_i、外压 p_o，半径 r 处的径向、周向应力（拉为正）"""
    A = (p_i * a * a - p_o * b * b) / (b * b - a * a)
    B = (p_i - p_o) * a * a * b * b / (b * b - a * a)
    return A - B / r ** 2, A + B / r ** 2


def fit_pressure(delta, d, D_hub, Eh, nuh, Es, nus, d_bore=0.0):
    """过盈 δ（直径上，mm）→ 接触压力 p（MPa）。轴可为空心（内径 d_bore）"""
    Ch = (D_hub ** 2 + d ** 2) / (D_hub ** 2 - d ** 2) + nuh
    Cs = (d ** 2 + d_bore ** 2) / (d ** 2 - d_bore ** 2) - nus
    return delta / (d * (Ch / Eh + Cs / Es))


# ---------------------------------------------------------------- 赫兹接触
def E_star(E1, nu1, E2, nu2):
    return 1 / ((1 - nu1 ** 2) / E1 + (1 - nu2 ** 2) / E2)


def hertz_line(Fp, R, Es):
    """线接触：单位长度载荷 F′（N/mm）、当量曲率半径 R（mm）、当量模量 E*。返回半宽 a、最大压力 p0"""
    a = math.sqrt(4 * Fp * R / (math.pi * Es))
    return a, 2 * Fp / (math.pi * a)


def line_subsurface(z_over_a):
    """线接触对称轴上的应力 / p0（McEwen）：σx、σz 和主切应力 τ1 = (σx − σz)/2 的绝对值"""
    s = math.sqrt(1 + z_over_a ** 2)
    sx = -((1 + 2 * z_over_a ** 2) / s - 2 * z_over_a)
    sz = -1 / s
    return sx, sz, abs(sx - sz) / 2


def hertz_point(F, Rx, Ry, Es):
    """椭圆接触（Hamrock–Brewe 近似）：主曲率半径 Rx ≤ Ry。返回半轴 a（Ry 向，较长）、b、最大压力 p0。
    Hamrock–Brewe 的式子用 E′ = 2E*（E* 按式 (8.9.1)）"""
    Ep = 2 * Es
    k = 1.0339 * (Ry / Rx) ** 0.636
    eps = 1.0003 + 0.5968 * Rx / Ry
    R = 1 / (1 / Rx + 1 / Ry)
    a = (6 * k * k * eps * F * R / (math.pi * Ep)) ** (1 / 3)
    b = (6 * eps * F * R / (math.pi * k * Ep)) ** (1 / 3)
    return a, b, 1.5 * F / (math.pi * a * b)


# ---------------------------------------------------------------- 曲梁（矩形截面）
def curved_rect(ri, ro, b, M, N=0.0):
    """温克勒–巴赫：返回 (r_n, e, σ_inner, σ_outer)；M 使曲率增大（内侧受拉）为正，N 拉为正"""
    h, A = ro - ri, b * (ro - ri)
    rc = (ri + ro) / 2
    rn = h / math.log(ro / ri)
    e = rc - rn
    s = lambda r: M * (rn - r) / (A * e * r) + N / A
    return rn, e, s(ri), s(ro)


def curved_exact_pure(ri, ro, b, M):
    """矩形截面曲杆纯弯曲的弹性力学精确解（铁木辛柯《弹性理论》）：返回内、外侧的周向应力"""
    a, c = ri, ro
    Nn = (c * c - a * a) ** 2 - 4 * a * a * c * c * math.log(c / a) ** 2
    Mb = M / b
    def st(r):        # 符号与 curved_rect 一致：M 使内侧受拉为正
        return -4 * Mb / Nn * (-(a * a * c * c) / r ** 2 * math.log(c / a) + c * c * math.log(r / c) - a * a * math.log(r / a) + c * c - a * a)
    return st(a), st(c)
