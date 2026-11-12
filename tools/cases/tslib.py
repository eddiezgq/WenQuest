"""第 161e 轮：关节扭矩传感器 WQ-TS 的共用代码（案例 A、B、C）——轮辐式弹性体的几何、有限元、应变片与电桥。

弹性体：外圈（固定在关节输出法兰）+ 内毂（接减速器输出）+ 4 根轮辐；每根轮辐中段两面各铣一个凹槽，留一层薄“剪切腹板”，
应变片（剪切型双栅，±45° 两个栅）贴在正面凹槽底的腹板中心。有限元用数字工厂“仿真与分析”同一个求解器（cae/solve.py：
Gmsh 二阶四面体 + CalculiX）。示例设计，不是任何厂家的传感器。
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "factory" / "digital")]
os.environ.setdefault("WQ_MESH_THREADS", "1")       # 网格每次相同，数字可复现（教材程序同样设置）

# 17-4PH（ASTM A564 Type 630，H1025 时效）：屈服 ≥ 1000 MPa、抗拉 ≥ 1070 MPa（标准最低值）；E、ν 为手册常用值
MAT = dict(id="17-4PH-H1025", name="17-4PH 不锈钢（H1025）", E_mpa=197000.0, nu=0.272, density=7.80, yield_mpa=1000.0, ultimate_mpa=1070.0)
G_MPA = MAT["E_mpa"] / (2 * (1 + MAT["nu"]))
GF = 2.0              # 应变片灵敏系数（常见金属箔式应变片的量级，示例）
R_GRID = 350.0        # 每个栅 350 Ω（SG-350）；一个桥臂 = 相对两根轮辐上同方向的两个栅串联 → 700 Ω
R_ARM = 2 * R_GRID
V_EX = 5.0            # 供桥电压 V（信号调理板 SIG-TS 的 5 V 基准）
T_FS = 200.0          # 量程 N·m（清单：WQ-TS ±200 N·m）
T_OVL = 300.0         # 过载 150 %（不屈服、不损坏）

# 几何 mm：第一版（手算定）与定稿（有限元改）
GEOM_V1 = dict(R_o=45.0, R_ri=34.0, R_ho=22.0, R_b=10.0, H=14.0, B=14.0, PL=8.0, PW=8.0, TW=1.5)
GEOM = dict(GEOM_V1, PL=10.0, PW=10.0, TW=1.0)
GAUGE = 3.0           # 应变片敏感栅区域 3 × 3 mm：有限元结果在这块面积上取平均


def r_mid(g):
    return (g["R_ho"] + g["R_ri"]) / 2


def solid(g, holes=False):
    """build123d 实体（z 向为轴线，z = 0 为中面）。holes=True 带安装孔（三维图、图纸用；有限元不带——孔远离应变区）"""
    import build123d as bd
    H = g["H"]
    s = bd.Cylinder(g["R_o"], H) - bd.Cylinder(g["R_ri"], H)
    s += bd.Cylinder(g["R_ho"], H) - bd.Cylinder(g["R_b"], H)
    for k in range(4):
        s += bd.Rot(0, 0, 90 * k) * bd.Pos(r_mid(g), 0, 0) * bd.Box(g["R_ri"] - g["R_ho"] + 2, g["B"], H)
        for z in (1, -1):
            s -= bd.Rot(0, 0, 90 * k) * bd.Pos(r_mid(g), 0, z * (g["TW"] / 2 + (H - g["TW"]) / 4)) * bd.Box(g["PL"], g["PW"], (H - g["TW"]) / 2)
    if holes:
        for k in range(8):                                   # 外圈 8 × M5 通孔 Ø5.5，分布圆 R39.5
            s -= bd.Rot(0, 0, 22.5 + 45 * k) * bd.Pos(HOLE_R_RIM, 0, 0) * bd.Cylinder(2.75, H)
        for k in range(8):                                   # 内毂分布圆 R16：6 × M6 螺纹孔（画成 Ø5 底孔）+ 0°、180° 两个 Ø6 锥销孔
            s -= bd.Rot(0, 0, 45 * k) * bd.Pos(HOLE_R_HUB, 0, 0) * bd.Cylinder(3.0 if k % 4 == 0 else 2.5, H)
    return s


HOLE_R_RIM = 39.5
HOLE_R_HUB = 16.0


def handcalc(g, T=T_FS):
    """短梁（两端固定、导向）+ 工字截面剪应力公式：τ = V·Q / (I·t_w)，V = T / (4·R_mid)"""
    V = T * 1000 / (4 * r_mid(g))                             # N
    B, H, PW, TW = g["B"], g["H"], g["PW"], g["TW"]
    wall = (B - PW) / 2
    I = 2 * H * ((B / 2) ** 3 - (PW / 2) ** 3) / 3 + TW * PW ** 3 / 12      # 绕轴线方向（z）的惯性矩 mm⁴
    Q = H * wall * (PW / 2 + wall / 2) + TW * (PW / 2) * (PW / 4)          # 中性轴以外面积矩 mm³
    tau = V * Q / (I * TW)
    gam = tau / G_MPA
    L = g["R_ri"] - g["R_ho"]
    M = V * L / 2                                                         # 根部弯矩（反弯点在中点）
    sig = M * (B / 2) / I
    return dict(V_N=V, I_mm4=I, Q_mm3=Q, tau_mpa=tau, gamma=gam, mv_v=GF * gam / 2 * 1000, M_root_nmm=M, sig_root_mpa=sig)


def _strain(s):
    sx, sy, sz, txy, tyz, tzx = s
    E, nu = MAT["E_mpa"], MAT["nu"]
    return (sx - nu * (sy + sz)) / E, (sy - nu * (sx + sz)) / E, txy / G_MPA


def fea(g, load="torque", value=T_FS, h=2.0):
    """一次有限元：load = torque（N·m，绕 z）/ fx（N，径向力）/ mx（N·m，倾覆力矩）。外圈外圆面固定，载荷加在内孔面。
    → dict(stats, surf, gauges[4] = (ε_rr, ε_tt, γ_rt) 平均, mv_v（电桥输出 mV/V）, theta_rad（内孔平均转角）)"""
    cdir = os.environ.get("WQ_TS_FEA_CACHE")          # 调试用：有限元结果缓存（不设就每次都算）
    if cdir:
        import hashlib
        import pickle
        key = hashlib.md5(repr((sorted(g.items()), load, value, h)).encode()).hexdigest()
        cp = Path(cdir) / f"{key}.pkl"
        if cp.exists():
            return pickle.loads(cp.read_bytes())
        r = _fea(g, load, value, h)
        cp.parent.mkdir(parents=True, exist_ok=True)
        cp.write_bytes(pickle.dumps(r))
        return r
    return _fea(g, load, value, h)


def _fea(g, load, value, h):
    import build123d as bd
    import tempfile
    from cae import geometry as GE, solve as SV
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "f.step")
        bd.export_step(solid(g), p)
        step = open(p, "rb").read()
    faces, _, _ = GE.faces(step)
    cyl = [f for f in faces if f["kind"] == "cylinder"]
    outer = [f["id"] for f in cyl if abs(f["radius_mm"] - g["R_o"]) < 1e-6]
    bore = [f["id"] for f in cyl if abs(f["radius_mm"] - g["R_b"]) < 1e-6]
    if load == "torque":
        ld = {"type": "torque", "faces": bore, "value_nmm": value * 1000, "axis": {"origin": [0, 0, 0], "dir": [0, 0, 1]}}
    elif load == "fx":
        ld = {"type": "force", "faces": bore, "vector_n": [value, 0, 0]}
    elif load == "mx":
        ld = {"type": "moment", "faces": bore, "vector_nmm": [value * 1000, 0, 0]}
    else:
        raise KeyError(load)
    cap = {}
    orig = SV.read_frd

    def rf(path):
        dd, ss = orig(path)
        cap["d"], cap["s"] = dd, ss
        return dd, ss
    SV.read_frd = rf
    try:
        stats, surf, allr = SV.solve(step, {"material": MAT, "loads": [{"type": "fixed", "faces": outer}, ld], "mesh": {"size_mm": h}})
    finally:
        SV.read_frd = orig
    P, S, U = allr["nodes"], cap["s"], cap["d"]
    ids = np.array([n for n in S if n in P])
    X = np.array([P[n] for n in ids])
    gauges = []
    rm = r_mid(g)
    for k in range(4):
        a = math.radians(90 * k)
        c, s_ = math.cos(a), math.sin(a)
        r = X[:, 0] * c + X[:, 1] * s_
        t = -X[:, 0] * s_ + X[:, 1] * c
        sel = (np.abs(X[:, 2] - g["TW"] / 2) < 1e-3) & (np.abs(r - rm) <= GAUGE / 2) & (np.abs(t) <= GAUGE / 2)
        e = []
        for n in ids[sel]:
            ex, ey, gxy = _strain(S[int(n)])
            err = ex * c * c + ey * s_ * s_ + gxy * c * s_
            ett = ex * s_ * s_ + ey * c * c - gxy * c * s_
            grt = 2 * (ey - ex) * c * s_ + gxy * (c * c - s_ * s_)
            e.append((err, ett, grt))
        gauges.append(np.mean(np.array(e), axis=0) if e else np.full(3, np.nan))
    th = []
    for n, p in P.items():
        rr = math.hypot(p[0], p[1])
        if abs(rr - g["R_b"]) < 1e-3 and n in U:
            th.append((-p[1] * U[n][0] + p[0] * U[n][1]) / rr / rr)
    return dict(stats=stats, surf=surf, gauges=[tuple(float(x) for x in v) for v in gauges], mv_v=bridge_mv_v(gauges),
                theta_rad=float(np.mean(th)), n_gauge_nodes=int(sel.sum()))


def grid_strains(gauges):
    """每根轮辐的 +45°、−45° 两个栅的应变"""
    out = []
    for err, ett, grt in gauges:
        m = (err + ett) / 2
        out.append((m + grt / 2, m - grt / 2))
    return out


def bridge_mv_v(gauges):
    """全桥：臂 1 = 轮辐 0、2 的 +45° 栅串联；臂 2 = 轮辐 0、2 的 −45°；臂 3 = 轮辐 1、3 的 +45°；臂 4 = 轮辐 1、3 的 −45°。
    Vout/Vex = GF/4 ·(ε1 − ε2 + ε3 − ε4)（小应变线性近似），→ mV/V"""
    gs = grid_strains(gauges)
    a1 = (gs[0][0] + gs[2][0]) / 2
    a2 = (gs[0][1] + gs[2][1]) / 2
    a3 = (gs[1][0] + gs[3][0]) / 2
    a4 = (gs[1][1] + gs[3][1]) / 2
    return GF / 4 * (a1 - a2 + a3 - a4) * 1000
