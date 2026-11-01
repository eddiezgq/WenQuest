"""17.3 节：质心与形心——线密度变化的杆；第 15 章变截面连杆的质心；半圆形薄板与半圆弧的形心；帕普斯–古尔丁定理验证
（球、圆环体）；装满物料的 AGV 料斗（第 16 章的正四棱台）的质心高度与整车转弯时的侧翻极限。"""
import math

from scipy import integrate

from bookout import out

g = 9.81
# 变截面铝连杆（15.3 节）：L = 0.5 m，A(x) = A0(1 − x/(2L))
L = 0.5
lam = lambda x: 1 - x / (2 * L)
xc_link = integrate.quad(lambda x: x * lam(x), 0, L)[0] / integrate.quad(lam, 0, L)[0]
out(xc_link=xc_link, xc_link_ratio=xc_link / L)
# 半圆薄板 x² + y² ≤ r², y ≥ 0 的形心；半圆弧的形心
r = 1.0
A = math.pi * r * r / 2
yc_disk = integrate.quad(lambda y: y * 2 * math.sqrt(r * r - y * y), 0, r)[0] / A
yc_arc = integrate.quad(lambda t: r * math.sin(t) * r, 0, math.pi)[0] / (math.pi * r)
out(yc_disk=yc_disk, yc_disk_ex=4 * r / (3 * math.pi), yc_arc=yc_arc, yc_arc_ex=2 * r / math.pi)
# 帕普斯–古尔丁：半圆绕直径旋转得球
out(pap_ball=2 * math.pi * yc_disk * A, ball=4 / 3 * math.pi, pap_sph=2 * math.pi * yc_arc * math.pi * r, sph=4 * math.pi)
# AGV 料斗：上口 0.6 m、下口 0.2 m、高 0.5 m 的倒置正四棱台，装满物料（1600 kg/m³）；斗底离地 0.45 m
a, b, h, rho = 0.6, 0.2, 0.5, 1600.0
s = lambda z: b + (a - b) * z / h
V = integrate.quad(lambda z: s(z) ** 2, 0, h)[0]
zc = integrate.quad(lambda z: z * s(z) ** 2, 0, h)[0] / V
m_load = rho * V
m_car, h_car, z0, track = 90.0, 0.22, 0.45, 0.6
h_tot = (m_car * h_car + m_load * (z0 + zc)) / (m_car + m_load)
h_empty = h_car
out(hop_V=V, hop_zc=zc, hop_zc_ratio=zc / h, m_load=m_load, m_car=m_car, h_car=h_car, z0=z0, track=track, h_tot=h_tot,
    a_lat_full=g * track / 2 / h_tot, a_lat_empty=g * track / 2 / h_empty, v_full=math.sqrt(g * track / 2 / h_tot * 1.0))
