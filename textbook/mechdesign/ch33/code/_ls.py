"""33.11 典型案例二：工业平缝机 WQ-LS 的上轴（主轴）LS-101。

数据来源：《缝纫机设计与制造》（问渠网页版，第 15 轮）第 3、8、13、14、23、27 章的示意数据——最高 5 000 r/min（第 23 章
讨论提速到 5 500 r/min），400 W 交流伺服电机直驱上轴，针杆曲柄半径 r = 15.5 mm、连杆长 l = 55 mm，往复质量约 0.12 kg，
平衡率 0.45，上轴轴颈 Ø12、轴承 6201（零件库 A-BRG-DG/6201）。LS-101 的轴段尺寸是本书按这些数据排的结构（示意）。

单位：长度 mm、力 N、力矩 N·mm、应力 MPa、质量 kg。z 沿轴线，从机头前端（针杆曲柄一端）算起。
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conventions"))
import mdstd  # noqa: E402

N_MAX = 5000.0                     # r/min
N_UP = 5500.0                      # 提速方案
R_CRANK, L_ROD = 15.5, 55.0        # mm
LAMBDA = R_CRANK / L_ROD
M_RECIP = 0.12                     # kg：针杆、针、针杆夹头与连杆的一部分（往复）
BALANCE = 0.45                     # 平衡率：曲柄平衡块抵消一阶往复惯性力的比例
P_MOTOR = 400.0                    # W（额定）
P_SEW = 150.0                      # W：正常缝纫时的平均功率（示意）
MAT = "45-QT"
BEARING = "6201"
FILLET = 0.5                       # 轴颈台阶 Ø12 → Ø16 的过渡圆角

# (直径, 长度, 名称)
SEGS = [(10, 22, "针杆曲柄座"), (12, 10, "前轴承位"), (16, 215, "轴身（挑线凸轮、送布偏心轮）"),
        (12, 10, "后轴承位"), (10, 40, "同步带轮、手轮、电机转子")]
# 集中质量（kg）与位置（z, mm）：曲柄连平衡块、挑线凸轮、送布偏心轮、同步带轮、手轮与电机转子（示意）
MASSES = [("针杆曲柄与平衡块", 11.0, 0.15), ("挑线凸轮", 45.0, 0.05), ("送布偏心轮", 150.0, 0.08),
          ("同步带轮", 262.0, 0.06), ("手轮与电机转子", 282.0, 0.45)]
BELT_N = 120.0                     # 同步带两边张力之和（铅垂向下，示意）


def layout(segs=SEGS):
    out, z = [], 0.0
    for d, L, n in segs:
        out.append((z, z + L, d, n))
        z += L
    return out, z


LAY, LEN = layout()
Z_CRANK = 11.0
Z_BRG = (LAY[1][0] + LAY[1][1]) / 2, (LAY[3][0] + LAY[3][1]) / 2
Z_STEP = LAY[1][1]                 # 前轴承位 Ø12 → 轴身 Ø16
Z_BELT = 262.0


def omega(n):
    return n * 2 * math.pi / 60


def crank_force(theta, n):
    """曲柄销对上轴的力（N），在固定坐标里：y 沿针杆（铅垂），x 水平。往复惯性力（一、二阶）+ 平衡块离心力。
    theta 为曲柄转角（针杆在上止点时为 0）。"""
    A = M_RECIP * R_CRANK / 1000 * omega(n) ** 2
    fy = A * ((1 - BALANCE) * np.cos(theta) + LAMBDA * np.cos(2 * theta))
    fx = -A * BALANCE * np.sin(theta)
    return fx, fy


def crank_torque(theta, n):
    """往复惯性力引起的转矩波动（N·mm），曲柄滑块的常用级数（到三阶）"""
    B = M_RECIP * (R_CRANK / 1000) ** 2 * omega(n) ** 2 * 1000
    return B * (LAMBDA / 4 * np.sin(theta) - 0.5 * np.sin(2 * theta) - 3 * LAMBDA / 4 * np.sin(3 * theta))


def moments(theta, n):
    """两个平面的弯矩分布：返回 (z, Mx(z), My(z))，单位 N·mm；轴承处简支，前端曲柄外伸，后端带轮力"""
    fx, fy = crank_force(theta, n)
    z = np.linspace(0, LEN, 601)
    za, zb = Z_BRG
    out = []
    for F_c, F_b in ((fx, 0.0), (fy, -BELT_N)):
        # 对 A 取矩求 B 支反力：外力在 Z_CRANK（F_c）、Z_BELT（F_b）
        RB = -(F_c * (Z_CRANK - za) + F_b * (Z_BELT - za)) / (zb - za)
        RA = -(F_c + F_b + RB)
        M = np.zeros_like(z)
        for P, zp in ((F_c, Z_CRANK), (RA, za), (RB, zb), (F_b, Z_BELT)):
            M += P * np.clip(z - zp, 0, None)
        out.append(M)
    return z, out[0], out[1]


# ---------------------------------------------------------------- 梁单元：临界转速
def diameter_at(z):
    for z0, z1, d, _ in LAY:
        if z0 - 1e-9 <= z <= z1 + 1e-9:
            return d
    return LAY[-1][2]


def critical_speeds(masses=MASSES, n_modes=2, E=206000.0, rho=7.85e-9, h=2.0):
    pts = {0.0, LEN, *Z_BRG, *(z for _, z, _ in masses)}
    for z0, z1, *_ in LAY:
        pts |= {z0, z1}
    pts = sorted(pts)
    z = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        k = max(1, int(math.ceil((b - a) / h)))
        z += list(np.linspace(a, b, k + 1)[1:])
    z = np.array(z)
    n = len(z)
    K, M = np.zeros((2 * n, 2 * n)), np.zeros((2 * n, 2 * n))
    for e in range(n - 1):
        L = z[e + 1] - z[e]
        d = diameter_at((z[e] + z[e + 1]) / 2)
        I, A = math.pi * d ** 4 / 64, math.pi * d ** 2 / 4
        k = E * I / L ** 3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                                        [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
        m = rho * A * L / 420 * np.array([[156, 22 * L, 54, -13 * L], [22 * L, 4 * L * L, 13 * L, -3 * L * L],
                                          [54, 13 * L, 156, -22 * L], [-13 * L, -3 * L * L, -22 * L, 4 * L * L]])
        idx = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        K[np.ix_(idx, idx)] += k
        M[np.ix_(idx, idx)] += m
    for _, zm, mk in masses:
        i = 2 * int(np.argmin(abs(z - zm)))
        M[i, i] += mk / 1000.0
    fixed = [2 * int(np.argmin(abs(z - zb))) for zb in Z_BRG]
    free = [i for i in range(2 * n) if i not in fixed]
    from scipy.linalg import eigh
    w2, V = eigh(K[np.ix_(free, free)], M[np.ix_(free, free)])
    w = np.sqrt(np.abs(w2[:n_modes]))
    modes = []
    for kk in range(n_modes):
        u = np.zeros(2 * n)
        u[free] = V[:, kk]
        y = u[0::2]
        modes.append(y / np.max(np.abs(y)))
    return w * 60 / (2 * math.pi), z, modes


def step_bytes(fillet=FILLET):
    """build123d 建 LS-101（不含键槽、偏心轮等装配件），与数字工厂“在线设计台”同一种建模方法"""
    import tempfile
    import build123d as bd
    z, s, steps = 0.0, None, []
    for d, L, _ in SEGS:
        c = bd.Pos(0, 0, z) * bd.Cylinder(d / 2, L, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        s = c if s is None else s + c
        z += L
        steps.append(z)
    s = s.clean()
    sel = []
    for zz in steps[:-1]:
        es = [e for e in s.edges() if e.geom_type == bd.GeomType.CIRCLE and abs(e.center().Z - zz) < 1e-6]
        if len(es) == 2:
            sel.append(min(es, key=lambda e: e.radius))
    if fillet and sel:
        s = s.fillet(fillet, sel)
    p = os.path.join(tempfile.mkdtemp(), "LS-101.step")
    bd.export_step(s, p)
    return open(p, "rb").read()
