"""33.10 典型案例一：协作机器人肩关节（J2）的输出空心轴 RJ-201。

数据来源：
- 机械臂：零件库 B-ARM-UR5E（MuJoCo Menagerie 模型，数字工厂“运动与动力分析”用的同一个模型），末端负载 4 kg；
- 一个搬运节拍：A → B 1.0 s，停 0.5 s，B → A 1.0 s，停 0.5 s，共 3 s（姿态见 POSE_A、POSE_B）；
- 减速器：零件库 D-RDC-HD-CSF（谐波减速器 CSF-2A 杯型）；轴承：零件库 A-BRG-DG（深沟球轴承）；
- 关节输出轴 RJ-201 的结构与尺寸是本书的设计方案（与任何一家机器人厂的实物无关）。

单位：长度 mm、力 N、力矩 N·mm（输出时换成 N·m）、应力 MPa。z 沿关节轴线，从减速器一侧的法兰端面算起。
"""
from __future__ import annotations

import csv
import math
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "factory" / "digital"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conventions"))
import mdstd  # noqa: E402

LIB = ROOT / "library" / "catalog"
ROBOT = "B-ARM-UR5E"
PAYLOAD_KG = 4.0
REACH_MM = 850.0                    # UR5e 工作半径（零件库 vendors/universal_robots.yaml）
POSE_A = {"shoulder_pan_joint": 0.0, "shoulder_lift_joint": -0.35, "elbow_joint": 0.6, "wrist_1_joint": -1.82,
          "wrist_2_joint": -1.5708, "wrist_3_joint": 0.0}
POSE_B = {"shoulder_pan_joint": 1.5708, "shoulder_lift_joint": -0.95, "elbow_joint": 1.3, "wrist_1_joint": -1.92,
          "wrist_2_joint": -1.5708, "wrist_3_joint": 0.0}
MOVE_S, DWELL_S = 1.0, 0.5
CYCLE_S = 2 * (MOVE_S + DWELL_S)
LIFE_H = 20000.0                    # 设计寿命：两班 × 5 年
DEFLECT_BUDGET_MM = 0.20            # 系统设计分配给“关节输出轴扭转”的末端弹性偏移（峰值力矩下）
HAND_MARGIN = 1.2                   # 手算选型时给台阶、法兰处的局部变形留的余量（33.10.4 用有限元核对）

# ---- RJ-201 的结构（外径, 长度, 名称）；内孔贯通
# 第 1 版（两端法兰都与轴一体、两轴承间是轴肩）装不起来（第 3.5.4 节）；现在的结构：减速器法兰与轴一体，两个轴承装在连续的
# 轴承位上、中间一个隔套，外端是渐开线花键，大臂法兰 RJ-202 是单独零件、靠花键传转矩，最外端圆螺母把 RJ-202 毂、
# 外侧轴承内圈、隔套、内侧轴承内圈一起压紧在减速器法兰端面上。两个轴承都从大臂一端装入。
BORE = 30.0                         # 本书方案的内孔
SPLINE_M = 1.5                      # 渐开线花键（GB/T 3478.1，30° 平齿根）的模数
SPACER_L = 24.0                     # 两轴承之间的隔套长
SPLINE_L = 20.0                     # 花键长（= RJ-202 毂长）
THREADS = [30, 33, 36, 39, 42, 45, 48]   # 圆螺母 GB/T 812 的细牙螺纹（螺距 1.5）


def spline(seat):
    """花键：外径要比轴承内径小（轴承从这一端装入）。返回 齿数、分度圆、大径、小径（mm）"""
    z = int((seat - 3) / SPLINE_M) - 1
    return {"z": z, "d": SPLINE_M * z, "D_ee": SPLINE_M * (z + 1), "D_ie": SPLINE_M * (z - 1.5)}


def thread(seat):
    """锁紧螺母的螺纹：比花键小径小的最大一档"""
    return max(t for t in THREADS if t < spline(seat)["D_ie"] - 0.5)


def segments(seat):
    """扭转与质量的计算模型（外径, 长度, 名称）：转矩从减速器法兰进、在花键段传给 RJ-202。轴承位直径 seat 决定其余尺寸；
    花键段按小径的圆柱计（齿不全参与扭转，偏于安全）。隔套、RJ-202、螺母不传扭转（与轴压紧在一起，但转矩只走轴）。"""
    return [(seat + 20, 10, "减速器法兰"), (seat, 16, "轴承位（内侧）"), (seat, SPACER_L, "隔套段"),
            (seat, 16, "轴承位（外侧）"), (spline(seat)["D_ie"], SPLINE_L, "花键段（RJ-202）")]


def shaft_segments(seat):
    """轴本身（数字工厂案例件 RJ-201 的模型）：计算模型 + 外端的螺纹段（花键按小径、螺纹按大径，都简化成圆柱）"""
    return segments(seat) + [(thread(seat), 10, "螺纹段 M{}×1.5".format(thread(seat)))]


def arm_offset(seat):
    """外侧轴承中心到大臂连接面（RJ-202 法兰外侧端面 = 花键段外端）的距离：大臂的力对外侧轴承的力臂"""
    sg = segments(seat)
    z_brg = sg[0][1] + sg[1][1] + sg[2][1] + sg[3][1] / 2
    return sum(L for _, L, _ in sg) - z_brg


SEAT = 50.0                         # 本书方案：轴承位 Ø50，6010 一对（零件库 A-BRG-DG 的 60 系列最大到 6010）
BEARING = "6010"
CANDIDATES = [(45, 25, "6009"), (45, 30, "6009"), (50, 30, "6010"), (50, 34, "6010"), (50, 38, "6010")]   # (轴承位, 内孔, 轴承)


def lib_specs(pid):
    with (LIB.glob(f"*/{pid}") .__next__() / "specs.csv").open(encoding="utf-8") as f:
        return {r["size"]: r for r in csv.DictReader(f)}


def harmonic(size):
    """零件库 D-RDC-HD-CSF 的一行：额定、启停允许峰值、平均负载允许、瞬时允许最大转矩（N·m），输入最高转速"""
    r = lib_specs("D-RDC-HD-CSF")[size]
    return {"size": size, "rated": float(r["T_rated_Nm"]), "repeat": float(r["T_repeat_Nm"]), "avg": float(r["T_avg_Nm"]),
            "momentary": float(r["T_momentary_Nm"]), "n_max": float(r["n_max_grease_rpm"]), "ratio": float(r["ratio"]),
            "OD": float(r["OD_mm"]), "mass": float(r["mass_kg"]), "src": r["src_url"], "n_avg": float(r["n_avg_grease_rpm"])}


HD_L10_H, HD_N_RATED = 7000.0, 2000.0     # CSF 系列：额定转矩下、输入 2 000 r/min 的额定寿命 L10（样本 csf-csg-catalog，寿命一节）


def bearing(code):
    r = lib_specs("A-BRG-DG")[code]
    return {"d": float(r["d_mm"]), "D": float(r["D_mm"]), "B": float(r["B_mm"])}


# ---------------------------------------------------------------- 载荷：数字工厂“运动与动力分析”的同一个模型
def cycle():
    """一个节拍的 J2 驱动力矩 T(t)（N·m）、传给大臂的力 F(t)（N）、J2 角速度 W(t)（rad/s）、时间 t（s）。
    调用数字工厂的 cae.mbd（“运动与动力分析”的同一个求解器和模型）。"""
    os.environ.setdefault("WQ_MENAGERIE", "/opt/menagerie")
    from cae import mbd, mbd_models as MM
    spec_path = MM.robot_path(ROBOT)
    pay = [{"body": "wrist_3_link", "mass": PAYLOAD_KG, "pos": [0, 0.1, 0]}]

    def leg(P, Q):
        dr = [{"joint": j, "kind": "move", "to": Q[j], "t0": 0.0, "t1": MOVE_S} for j in P if abs(Q[j] - P[j]) > 1e-9]
        dr += [{"joint": j, "kind": "hold"} for j in P if abs(Q[j] - P[j]) <= 1e-9]
        _, ch, _ = mbd.simulate(mbd.load_spec(path=spec_path), {"duration_s": MOVE_S + DWELL_S, "initial": P,
                                                                 "payloads": pay, "drives": dr, "sample_hz": 200})
        return ch
    a, b = leg(POSE_A, POSE_B), leg(POSE_B, POSE_A)
    T = np.concatenate([a["drive.shoulder_lift_joint"], b["drive.shoulder_lift_joint"]])
    W = np.concatenate([a["qd.shoulder_lift_joint"], b["qd.shoulder_lift_joint"]])
    F = np.concatenate([a["rf.upper_arm_link.abs"], b["rf.upper_arm_link.abs"]])
    t = np.concatenate([a["t"], b["t"] + a["t"][-1] + (a["t"][1] - a["t"][0])])
    return t, T, F, W


# ---------------------------------------------------------------- 截面与刚度
def J_hollow(D, d=BORE):
    return math.pi * (D ** 4 - d ** 4) / 32


def W_hollow(D, d=BORE):
    return math.pi * (D ** 4 - d ** 4) / (32 * D)


def twist(T_nmm, segs, G, d=BORE):
    """减速器法兰到花键段（转矩传给 RJ-202 处）之间的扭转角（rad）：各段串联；两端各算一半长度"""
    return sum(T_nmm * L / (G * J_hollow(D, d)) for D, L, *_ in segs[1:-1]) + \
        sum(T_nmm * (L / 2) / (G * J_hollow(D, d)) for D, L, *_ in (segs[0], segs[-1]))


def mass(segs, rho_g_cm3, d=BORE):
    return sum(math.pi / 4 * (D ** 2 - d ** 2) * L for D, L, *_ in segs) * rho_g_cm3 * 1e-6      # kg


def step_bytes(segs, d=BORE, fillet=1.0):
    """build123d：沿 z 叠圆柱、打通孔、台阶内角倒圆。与数字工厂“在线设计台”同一种建模方法。"""
    import tempfile
    import build123d as bd
    z, s, steps = 0.0, None, []
    for k, (D, L, *_) in enumerate(segs):
        c = bd.Pos(0, 0, z) * bd.Cylinder(D / 2, L, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        s = c if s is None else s + c
        z += L
        if k + 1 < len(segs) and abs(segs[k + 1][0] - D) / 2 > 1.5 * fillet:    # 台阶高度够才倒圆（花键与螺纹之间的小台阶不倒）
            steps.append(z)
    s = s.clean()
    if fillet:
        sel = []
        for zz in steps:
            es = [e for e in s.edges() if e.geom_type == bd.GeomType.CIRCLE and abs(e.center().Z - zz) < 1e-6]
            if len(es) == 2:
                sel.append(min(es, key=lambda e: e.radius))
        s = s.fillet(fillet, sel)
    s = s - bd.Pos(0, 0, -1) * bd.Cylinder(d / 2, z + 2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    p = os.path.join(tempfile.mkdtemp(), "RJ-201.step")
    bd.export_step(s, p)
    return open(p, "rb").read()
