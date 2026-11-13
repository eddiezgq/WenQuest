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
PRESS = os.environ.get("WQ_PRESS", "down")                  # G4.7 压脚：down 放下 / hand 手抬 / knee 膝抬
TRIM = os.environ.get("WQ_TRIM", "sew")                     # G4.8 剪线：sew 平时缝纫 / trim 剪线那一转（滚子在槽里）/ wipe 停在 80° 拨线
_OP = json.loads((T.OUT / "选配件.json").read_text()) if (T.OUT / "选配件.json").exists() else None
MK = T.Mech2(r=R, l=L, mr=S.SEW["mr"], lk=TK)
_CT = json.loads((T.OUT / "操纵件.json").read_text())["geo"]["tension"] if (T.OUT / "操纵件.json").exists() else None
TENSION_PATH = ([[_CT["x"] + 8.0, _CT["y_wall"] - 7.2, _CT["z"] + 14.0], [_CT["x"], _CT["y_wall"] - 7.2, _CT["z"] - 3.2],
                 [_CT["x"] - 19.0, _CT["y_wall"] - 3.5, _CT["z"] + 10.0]] if _CT else [])      # 进线 → 夹线盘之间 → 挑线簧钩
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


def rot_axis(axis, ang_deg, c):
    """绕过点 c、方向 axis 的轴转 ang_deg（4×4）"""
    a = np.asarray(axis, float) / np.linalg.norm(axis)
    t = ang_deg * DEG
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    Rm = np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K
    M = np.eye(4)
    M[:3, :3] = Rm
    M[:3, 3] = np.asarray(c, float) - Rm @ np.asarray(c, float)
    return M


def rigid3(a0, b0, a1, b1):
    """把线段 a0b0 送到 a1b1 的刚体变换（绕垂直于两者的轴转最小角）"""
    a0, b0, a1, b1 = (np.asarray(v, float) for v in (a0, b0, a1, b1))
    u, v = (b0 - a0) / np.linalg.norm(b0 - a0), (b1 - a1) / np.linalg.norm(b1 - a1)
    ax = np.cross(u, v)
    sn = np.linalg.norm(ax)
    M = np.eye(4)
    if sn > 1e-12:
        M = rot_axis(ax, math.degrees(math.atan2(sn, float(u @ v))), (0, 0, 0))
    M[:3, 3] += a1 - M[:3, :3] @ a0
    return M


def opt_motion(phi):
    """G4.8 选配件的变换（剪线那一转跟凸轮走；平时都不动；wipe 时拨线钩扫一下）"""
    if _OP is None:
        return {}
    g, kn = _OP["geo"], _OP["knife"]
    h = kn["cam_h"]
    s = 0.0
    if TRIM == "trim":
        p = phi % 360
        if 20.0 <= p < 75.0:
            u = (p - 20.0) / 55.0
            s = h * (1 - (u - math.sin(2 * math.pi * u) / (2 * math.pi)))
        elif p < 20.0 or p >= 340.0:
            s = h
        elif 280.0 <= p < 340.0:
            u = (p - 280.0) / 60.0
            s = h * (u - math.sin(2 * math.pi * u) / (2 * math.pi))
    k, rr = g["knife"], g["rock"]
    px, py = k["pivot"]
    dl = kn["beta_deg"] * s / h                             # 动刀往前转（逆时针）
    Kp = np.array([px - k["crank_r"] * math.cos(dl * DEG), py - k["crank_r"] * math.sin(dl * DEG), -50.0])
    K0 = np.array([px - k["crank_r"], py, -50.0])
    Sy, Sz, rc, cx = rr["y"], rr["z"], rr["crank_r"], rr["crank_x"]
    off = np.array([-6.0, -rc])                           # 摆轴曲柄上的球头销：朝 −y 伸出 6（cad/opt.py）

    def rpin(e):
        c, s_ = math.cos(e * DEG), math.sin(e * DEG)
        return np.array([cx, Sy + c * off[0] - s_ * off[1], Sz + s_ * off[0] + c * off[1]])
    R0 = rpin(0.0)
    L0 = float(np.linalg.norm(R0 - K0))
    lo, hi = -40.0, 40.0                                  # 摆轴转角 ε：拉杆长度不变（动刀往前时拉杆被拉向 −y，摆轴反转）
    for _ in range(60):
        e = (lo + hi) / 2
        if np.linalg.norm(rpin(e) - Kp) > L0:              # ε 增大时销往 +y、离动刀曲柄销更远
            hi = e
        else:
            lo = e
    e = (lo + hi) / 2
    R = rpin(e)
    rock = rot_x(e, Sy, Sz)
    lev = rock.copy()
    if TRIM == "trim":
        lev[0, 3] += g["solenoid_trim"]["stroke"]            # 剪线那一转：摆杆被电磁铁推进凸轮槽（按整转都在槽里查，偏严）
    M = dict(moving_knife=rot_axis((0, 0, 1), dl, (px, py, 0)), knife_shaft=rot_axis((0, 0, 1), dl, (px, py, 0)),
             trim_rock=rock, trim_lever=lev, trim_roller=lev, trim_link=rigid3(K0, R0, Kp, R),
             trim_cam=rot_x(phi, S.YL, S.ZL))
    if TRIM == "wipe":
        w = g["wiper"]
        M["wiper"] = rot_axis((0, 0, 1), w["sweep_deg"] * (phi % 360) / 358.0, (w["pivot"][0], w["pivot"][1], 0))
    return M


def frames(step=2):
    C0, B00, lp0 = pose(0.0)
    out = []
    for phi_ in range(0, 360, step):
        phi = 80 if TRIM == "wipe" else phi_                # wipe：针停在 80°，拨线钩随帧号扫过
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
                 lift_rock=rot_x(math.degrees(FP["gam"][i] - FP["gam"][0]), *g["Lr"]),
                 oil_ecc=low,                                                           # 油泵偏心（偏心 0.4，φ = 0 朝下）
                 oil_plunger=trans(0.0, 0.4 * (1 - math.cos(phi * DEG))))              # 柱塞跟着偏心最下点上下
        # G4.7 压脚组：压脚放下时（没有布）被送布牙顶起 max(0, 牙顶高出针板)；抬起时送布牙够不着，不动
        pz = max(0.0, fi["dog"][1]) if PRESS == "down" else 0.0
        M.update({k: trans(0.0, pz) for k in ("presser_bar", "presser_collar", "presser_foot", "lift_bracket")})
        mo = opt_motion(phi)
        if TRIM == "wipe" and "wiper" in mo:
            mo["wiper"] = rot_axis((0, 0, 1), _OP["geo"]["wiper"]["sweep_deg"] * phi_ / 358.0,
                                                                             (_OP["geo"]["wiper"]["pivot"][0], _OP["geo"]["wiper"]["pivot"][1], 0))
        M.update(mo)
        # 面线：A → 线眼 → B → 针杆线钩 → 针眼（x 取各自所在平面）
        tip = Bv + ZU - X["nb_below"] - X["tip_below"]
        Ey, Ez = w(lp["E"])
        Ay, Az = w(TK["A"])
        By, Bz = w(TK["B"])
        nb_bot = Bv + ZU - X["nb_below"]
        # G4.7：从夹线器开始——两片夹线盘之间（绕夹线柱下面）→ 挑线簧的钩 → 过线点 A
        # 过线点 B 之后：机头前面下沿的过线环（z 44，cad/ctrl.py 的 thread_guide）→ 针夹上的线钩 → 顺着机针前面的长槽到针眼
        thread = TENSION_PATH + [[40.0, Ay, Az], [X["lever"][0] + X["lever"][1] / 2, Ey, Ez], [0.0, By, Bz], [0.0, -51.0, 44.0],
                                 [0.0, -6.0, nb_bot + 0.3], [0.0, -0.75, nb_bot - 3.0], [0.0, -0.3, tip + 2.8]]
        own = (["tension", "tension", "check_spring"] if TENSION_PATH else []) + ["A", "lever", "B", "thread_guide", "needle_clamp", "needle", "needle"]
        out.append(dict(phi=phi_, M={k: [round(v, 5) for v in m.flatten()] for k, m in M.items()}, thread=thread, thread_own=own,
                        tip_z=round(tip, 3), eye=[round(Ey, 3), round(Ez, 3)]))
    return out


def main():
    d = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/wqls_mech")
    fr = frames()
    (d / "frames.json").write_text(json.dumps(dict(step=2, frames=fr)))
    print(len(fr), "frames → ", d / "frames.json")


if __name__ == "__main__":
    main()
