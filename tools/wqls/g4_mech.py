"""第 138 轮 G4.1：刺布、挑线机构一转的运动（每 2°），给三维动画和干涉检查用。

    python3 tools/wqls/g4_mech.py <零件目录>      → <零件目录>/frames.json

每个运动零件给一个 4×4 变换（相对 cad/mech.py 画零件时的 φ = 0 位置，整机坐标 mm，行主序）。
运动学全部来自设计软件：针杆—连杆按曲柄滑块精确式（sewcore Mech），挑线四连杆按 g4_takeup.Mech2（设计软件 link_pose 加装配分支）。
另给出面线的路线（过线点 A → 线眼 → 导线点 B → 针杆线钩 → 针眼）。
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE)]
import g4_takeup as T  # noqa: E402
import spec as S  # noqa: E402

DEG = math.pi / 180
R, L, ZU = S.SEW["r"], S.SEW["l"], S.ZU
TK = json.loads((T.OUT / "挑线机构.json").read_text())["lk"]
import os  # noqa: E402
FD = json.loads((T.OUT / "送布机构.json").read_text())
FP = FD["poses"][os.environ.get("WQ_FEED", "s3")]          # G4.6 送布组：哪一档（s3 动画，s5 / r5 干涉检查）
MK = T.Mech2(r=R, l=L, mr=S.SEW["mr"], lk=TK)
X = S.MECH_X


def w(p):
    """端视 (u, v) → 整机 (y, z)"""
    return np.array([-p[0], ZU + p[1]])


def rigid(a0, b0, a1, b1):
    """把 a0、b0 送到 a1、b1 的平面刚体变换（在 YZ 平面里，绕 X 轴转）"""
    a0, b0, a1, b1 = (np.asarray(v, float) for v in (a0, b0, a1, b1))
    t0, t1 = b0 - a0, b1 - a1
    al = math.atan2(t1[1], t1[0]) - math.atan2(t0[1], t0[0])
    c, s = math.cos(al), math.sin(al)
    Rm = np.array([[c, -s], [s, c]])
    t = a1 - Rm @ a0
    M = np.eye(4)
    M[1:3, 1:3] = Rm
    M[1:3, 3] = t
    return M


def trans(dy, dz):
    M = np.eye(4)
    M[1, 3], M[2, 3] = dy, dz
    return M


def rot_x(phi_deg, yc=0.0, zc=ZU):
    a = phi_deg * DEG
    c, s = math.cos(a), math.sin(a)
    Rm = np.array([[c, -s], [s, c]])
    M = np.eye(4)
    M[1:3, 1:3] = Rm
    M[1:3, 3] = np.array([yc, zc]) - Rm @ np.array([yc, zc])
    return M


def pose(phi):
    q = phi * DEG
    C = (R * math.sin(q), R * math.cos(q))
    Bv = C[1] - math.sqrt(L * L - C[0] ** 2)
    lp = MK.link_pose(phi % 360, MK.LK0)
    return C, Bv, lp


def frames(step=2):
    C0, B00, lp0 = pose(0.0)
    out = []
    for phi in range(0, 360, step):
        C, Bv, lp = pose(phi)
        tb = trans(0.0, Bv - B00)
        rod = rigid(w(C0), w((0.0, B00)), w(C), w((0.0, Bv)))
        lev = rigid(w(lp0["P"]), w(lp0["M"]), w(lp["P"]), w(lp["M"]))
        rck = rigid(w(lp0["Q"]), w(lp0["M"]), w(lp["Q"]), w(lp["M"]))
        dM = w(lp["M"]) - w(lp0["M"])
        rot = rot_x(phi)
        M = dict(shaft=rot, crank=rot, crank_pin=rot, needle_bar=tb, needle_clamp=tb, needle=tb, nb_link=tb, rod=rod,
                 lever=lev, rocker=rck, pin_M=trans(*dM),
                 rotor=rot, rotor_magnets=rot, encoder_disc=rot, handwheel=rot, handwheel_ring=rot,   # G4.3 电机转子、码盘、手轮随上轴转
                 pulley_upper=rot)
        # G4.5 旋梭组：下轴经同步带 1 : 1 同向转；旋梭轴经外啮合齿轮 1 : 2 反向转
        low = rot_x(phi, S.YL, S.ZL)
        hk = rot_x(-2 * phi, 0.0, S.ZH)
        M.update(pulley_lower=low, lower_shaft=low, gear_lower=low, gear_hook=hk, hook_shaft=hk, hook=hk)
        # G4.6 送布组（g4_feed.py 算的每 2° 位置）
        i = (phi // 2) % len(FP["E"])
        g = FD["geo"]
        f0 = {k: FP[k][0] for k in ("E", "P", "C", "T", "D", "EL", "dog")}
        fi = {k: FP[k][i] for k in ("E", "P", "C", "T", "D", "EL", "dog")}
        M.update(feed_ecc=rot, lift_ecc=low,
                 feed_rod=rigid(f0["E"], f0["P"], fi["E"], fi["P"]),
                 reg_slider=trans(fi["P"][0] - f0["P"][0], fi["P"][1] - f0["P"][1]),
                 feed_link=rigid(f0["P"], f0["C"], fi["P"], fi["C"]),
                 feed_rock=rot_x(math.degrees(FP["beta"][i] - FP["beta"][0]), *g["Fr"]),
                 feed_bar=rigid(f0["T"], f0["dog"], fi["T"], fi["dog"]),
                 lift_link=rigid(f0["EL"], f0["D"], fi["EL"], fi["D"]),
                 lift_rock=rot_x(math.degrees(FP["gam"][i] - FP["gam"][0]), *g["Lr"]))
        # 面线：A → 线眼 → B → 针杆线钩 → 针眼（x 取各自所在平面）
        tip = Bv + ZU - X["nb_below"] - X["tip_below"]
        Ey, Ez = w(lp["E"])
        Ay, Az = w(TK["A"])
        By, Bz = w(TK["B"])
        nb_bot = Bv + ZU - X["nb_below"]
        thread = [[40.0, Ay, Az], [X["lever"][0] + X["lever"][1] / 2, Ey, Ez], [0.0, By, Bz], [0.0, -6.0, nb_bot + 3.5],
                  [0.0, -0.3, tip + 2.8]]
        out.append(dict(phi=phi, M={k: [round(v, 5) for v in m.flatten()] for k, m in M.items()}, thread=thread,
                        tip_z=round(tip, 3), eye=[round(Ey, 3), round(Ez, 3)]))
    return out


def main():
    d = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/wqls_mech")
    fr = frames()
    (d / "frames.json").write_text(json.dumps(dict(step=2, frames=fr)))
    print(len(fr), "frames → ", d / "frames.json")


if __name__ == "__main__":
    main()
