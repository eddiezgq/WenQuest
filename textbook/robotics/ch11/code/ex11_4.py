"""11.4 节：工作空间。

(1) 平面 3R 臂（0.425、0.392、0.1 m）：可达工作空间与灵巧工作空间的解析结果（定理 11.4.1、11.4.2），
    用网格点 × 360 个朝向的数值检查核对；边界上 det J = L1 L2 sinθ2 = 0。
(2) UR5e（零件库模型尺寸）：法兰中心的可达工作空间与灵巧工作空间。
    关节 1 可整周转动，工作空间绕基座竖直轴对称，只需在 (ρ, z) 半平面上划网格（2 cm）；
    对每个格点取 K 个法兰法线方向（斐波那契球面网格），用解析逆运动学判断有没有解（_ch11.ur_reachable）。
    可达 = 至少一个方向有解；灵巧 = 所有方向都有解。体积按 V = Σ 2πρ Δρ Δz 计算。K = 100 与 K = 400 比较收敛性。
    另算“法兰朝下”（a = −z）时可到达的区域，以及几个解析的边界：内侧不可达圆柱的半径 d4 − d6、灵巧区内半径 d4 + d6。
    随机抽一批有解的格点，用逆解代回正运动学核对。
(3) SCARA（零件库模型）：水平面内可达区域的面积（关节 1、2 的限位），乘丝杠行程得体积；
    关节 4 可转 ±360°，所以对它自己的任务空间 R³ × S¹，灵巧工作空间等于可达工作空间。
"""
import math

import numpy as np

from _ch11 import (D4, D6, H1, L1u, L2u, SC_L1, SC_L2, SC_STROKE, frame_from_z, scara_limits, scara_reach_xy, sphere_dirs,
                   ur_fk_dh, ur_ik, ur_reachable)
from bookout import out

# ---------------------------------------------------------------- (1) 平面 3R 臂
L1, L2, L3 = 0.425, 0.392, 0.1
r_out = L1 + L2 + L3
r_in = max(0.0, abs(L1 - L2) - L3)
dex_out = L1 + L2 - L3
dex_gap = (L3 - abs(L1 - L2), L3 + abs(L1 - L2))           # 灵巧区中间被挖去的环：L3 − |L1 − L2| < r < L3 + |L1 − L2|
assert dex_gap[0] > 0


def reach2(r):
    return (r >= abs(L1 - L2) - 1e-12) & (r <= L1 + L2 + 1e-12)


rs = np.linspace(0.0005, 0.95, 1900)
phis = np.linspace(0, 2 * np.pi, 720, endpoint=False)
P = rs[:, None]                                            # 点取在 x 轴上（问题绕原点对称）
wx = P - L3 * np.cos(phis)[None, :]
wy = -L3 * np.sin(phis)[None, :]
ok = reach2(np.hypot(wx, wy))
num_reach = ok.any(1)
num_dex = ok.all(1)
ana_reach = rs <= r_out
ana_dex = (rs <= dex_out) & ((rs <= dex_gap[0]) | (rs >= dex_gap[1]))
mism_reach = int((num_reach != ana_reach).sum())
mism_dex = int((num_dex != ana_dex).sum())
assert mism_reach <= 2 and mism_dex <= 4                  # 只在边界上相差一个网格
A_reach = math.pi * r_out ** 2
A_dex = math.pi * (dex_gap[0] ** 2 + dex_out ** 2 - dex_gap[1] ** 2)
# 2R 臂的边界与 det J = 0：θ2 = 0（伸直）给出外圆，θ2 = π（折回）给出内圆
for t2, rr in ((0.0, L1 + L2), (math.pi, abs(L1 - L2))):
    assert abs(math.hypot(L1 + L2 * math.cos(t2), L2 * math.sin(t2)) - rr) < 1e-12
    assert abs(L1 * L2 * math.sin(t2)) < 1e-12

# ---------------------------------------------------------------- (2) UR5e
h = 0.02
rho = np.arange(h / 2, 1.06, h)
zz = np.arange(-0.88, 1.16, h) + h / 2
RR, ZZ = np.meshgrid(rho, zz, indexing="ij")
pts = np.stack([RR.ravel(), np.zeros(RR.size), ZZ.ravel()], 1)
w_cell = 2 * np.pi * pts[:, 0] * h * h


def scan(K):
    cnt = np.zeros(len(pts), int)
    for d in sphere_dirs(K):
        cnt += ur_reachable(pts, np.repeat(d[None], len(pts), 0))
    return cnt


cnt = scan(100)
reach, dex = cnt > 0, cnt == 100
V_reach, V_dex = w_cell[reach].sum(), w_cell[dex].sum()
cnt4 = scan(400)
V_reach4, V_dex4 = w_cell[cnt4 > 0].sum(), w_cell[cnt4 == 400].sum()
assert abs(V_reach4 - V_reach) / V_reach < 0.01 and abs(V_dex4 - V_dex) / V_dex < 0.03
down = ur_reachable(pts, np.repeat(np.array([[0, 0, -1.0]]), len(pts), 0))
V_down = w_cell[down].sum()
# 与第 1 章“半径 0.85 m 的球”的估计比较
V_ball = 4 / 3 * math.pi * 0.85 ** 3
# 解析的边界：法兰中心离基座轴线至少 d4 − d6；灵巧时至少 d4 + d6
rho_min_reach = pts[reach, 0].min() - h / 2
rho_min_dex = pts[dex, 0].min() - h / 2
assert abs(rho_min_reach - (D4 - D6)) < h and abs(rho_min_dex - (D4 + D6)) < h
dist = np.hypot(pts[:, 0], pts[:, 2] - H1)                # 到肩部中心（关节 2 轴与基座轴线的交点高度）
d_reach_max, d_dex_max = dist[reach].max() + h / 2, dist[dex].max() + h / 2
# 抽查：有解的格点上，逆解代回正运动学
rng = np.random.default_rng(5)
idx = rng.choice(np.where(reach)[0], 300, replace=False)
dirs = sphere_dirs(100)
nchk = 0
for i in idx:
    for d in dirs[rng.choice(100, 5, replace=False)]:
        Tg = np.eye(4)
        Tg[:3, :3] = frame_from_z(d)[0]
        Tg[:3, 3] = pts[i]
        for q in ur_ik(Tg):
            assert np.allclose(ur_fk_dh(q), Tg, atol=1e-8)
            nchk += 1
assert nchk > 1000

# ---------------------------------------------------------------- (3) SCARA
lim = scara_limits()
hs = 0.0025
g = np.arange(-0.65, 0.65, hs) + hs / 2
X, Y = np.meshgrid(g, g)
okxy = scara_reach_xy(X, Y, lim["J1"], lim["J2"])
A_sc = okxy.sum() * hs * hs
V_sc = A_sc * SC_STROKE
r_sc = np.hypot(X, Y)[okxy]
r_sc_min = math.sqrt(SC_L1 ** 2 + SC_L2 ** 2 + 2 * SC_L1 * SC_L2 * math.cos(lim["J2"][1]))
assert abs(r_sc.min() - r_sc_min) < 2 * hs
A_ring = math.pi * ((SC_L1 + SC_L2) ** 2 - r_sc_min ** 2)
assert A_sc < A_ring

out(r_out=r_out, dex_out=dex_out, gap0=dex_gap[0], gap1=dex_gap[1], A_reach=A_reach, A_dex=A_dex, dex_ratio=100 * A_dex / A_reach,
    mism_reach=mism_reach, mism_dex=mism_dex,
    V_reach=V_reach, V_dex=V_dex, V_reach4=V_reach4, V_dex4=V_dex4, V_down=V_down, V_ball=V_ball,
    dex_pct=100 * V_dex / V_reach, down_pct=100 * V_down / V_reach,
    rho_in=D4 - D6, rho_dex=D4 + D6, d_reach_max=d_reach_max, d_dex_max=d_dex_max, nchk=nchk, ncell=len(pts),
    A_sc=A_sc, V_sc=V_sc, r_sc_min=r_sc_min, A_ring=A_ring, sc_t1=math.degrees(lim["J1"][1]), sc_t2=math.degrees(lim["J2"][1]),
    rho_max_reach=pts[reach, 0].max() + h / 2, L12=L1u + L2u, ratio_ur_sc=V_reach / V_sc, d_dex_max_mm=0)
