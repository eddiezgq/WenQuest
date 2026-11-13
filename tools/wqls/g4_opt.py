"""第 138 轮 G4.8：选配 T（自动剪线）和 E（电子针距）的尺寸和计算 → docs/设计/WQ-LS/G4/选配件.json（cad/opt.py 按其中的 geo 画零件）

    python3 tools/wqls/g4_opt.py <零件目录>      零件目录里要有 frames.json（一转运动，cad/mech.py 生成）

内容：
  ① 时刻：由一转运动取针尖、挑线杆线眼、送布牙的位置，定剪线凸轮的各段和停针窗口；
  ② 针板下面的空间：动刀平面夹在送布牙排和旋梭之间；
  ③ 剪线机构：下轴上的端面槽凸轮 → 摆杆（滚子）→ 沿 x 的剪线摆轴 → 下端曲柄、球头拉杆 → 动刀轴 → 动刀；
     剪线电磁铁把摆杆沿摆轴推进凸轮槽；动刀回程时和针板底下的定刀相遇，把线剪断；
  ④ 力、压力角、接触应力、电磁铁；剪线转速上限；线头长度（估算）；
  ⑤ 松线电磁铁（拉 G4.7 的立轴拨杆）、拨线器；
  ⑥ 电子针距：步进电机经同步带转调节器轴；力矩、换向时间、分辨率。
坐标同整机（spec.py）：x 沿上轴向右，y 向后，z 向上，原点在针板面、针中心，mm。φ 为主轴转角（针杆上止点为 0）。
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE)]
import spec as S  # noqa: E402

G4 = ROOT / "docs" / "设计" / "WQ-LS" / "G4"
OUT = G4 / "选配件.json"
FD = json.loads((G4 / "送布机构.json").read_text())
DYN = json.loads((G4 / "送布动力.json").read_text())
CTRL = json.loads((G4 / "操纵件.json").read_text())
HOOK = json.loads((G4 / "旋梭组计算.json").read_text())
DEG = math.pi / 180
ALPHA_STOP = HOOK["loads"]["alpha_stop_rad_s2"]          # 主轴停车减速度 rad/s²（G4.5）
LOW = (27.8, -35.4)                                       # 下轴中心 (y, z)
FABRIC_MAX = 3.0                                          # 停针时要让开的布厚（四层轻牛仔压紧后）mm

GEO = dict(
    # ② 针板下面：动刀刀片平面（厚 1.0）；定刀装在针板底面
    knife_plane=(-5.9, -4.9),
    plate_bottom=-2.5,
    # ③ 动刀：轴竖直，在针的左后方；刀尖在最前时越过针 3 mm，最后时退到 x −15
    knife=dict(pivot=(-10.0, 40.0), tip_fwd=(3.0, 1.0), tip_rest_x=-13.0, arm_z=(-9.0, -7.0), hub_r=6.0,
               shaft_d=8.0, shaft_z=(-52.0, -7.0), crank_z=-50.0, crank_r=8.0, edge_back=6.0),
    fixed=dict(x_edge=-12.0, y=(-5.0, 4.0), z=(-4.9, -2.5), x_back=-20.5, screw_x=-16.0),
    base=dict(z=(-14.0, -10.0), bushing=(-30.0, -14.0)),        # 动刀轴座（钢板，螺在机座顶板下面两个凸台上）
    rock=dict(y=60.0, z=-30.0, x=(-25.0, 150.0), d=10.0, crank_r=20.0, crank_x=-18.0, boss_x=(-12.0, 138.0)),
    cam=dict(x=(140.0, 150.0), rho0=14.0, groove_w=8.4, roller_d=8.0, groove_depth=4.0, lever_x=(126.0, 134.0)),
    link=dict(d=6.0, ball_d=8.0),
    solenoid_trim=dict(x=(108.0, 124.0), stroke=5.0, d=22.0),     # 推摆杆沿摆轴进槽（沿 +x）
    # ⑤ 松线电磁铁：拉立轴拨杆上加的第三条臂（朝 +y 10）往 −x；拨线器：机头左前下方的竖轴
    sol_release=dict(arm=(0.0, 10.0), x=(47.0, 64.0), d=16.0, stroke=3.0),
    # 拨线器：竖轴 (−30, −10) 从机头底板的轴座伸下来；钢丝 Ø1.2 在 z 4.6，长 31；收回时朝 −100°（在压脚前面外侧），扫到 +15° 时钩尖过针前
    wiper=dict(pivot=(-30.0, -10.0), wire_d=1.2, wire_z=4.6, r=31.0, rest_deg=-100.0, sweep_deg=115.0,
               sol=dict(x=(-26.0, -12.0), z=61.5, d=16.0, stroke=10.0)),
    # ⑥ 电子针距：步进电机在机座里，轴沿 x，经同步带转调节器轴（G4.6 调节器轴 x 297…310、y 0、z −50）
    estep=dict(motor_axis=(-24.0, -35.0), x_face=270.0, pulley_x=(286.0, 296.0)),
)


# ------------------------------------------------------------------ ① 时刻
def timing(frames):
    phi = np.array([f["phi"] for f in frames], float)
    tip = np.array([f["tip_z"] for f in frames], float)
    eye = np.array([f["eye"][1] for f in frames], float)
    dog = []
    for f in frames:
        M = np.array(f["M"]["feed_bar"]).reshape(4, 4)
        dog.append((M @ np.array([0, 0, 0.7278, 1]))[2])          # 牙顶（φ = 0 时 z 0.728）
    dog = np.array(dog)

    def cross(a, level, down=True):
        out = []
        for i in range(len(a)):
            j = (i + 1) % len(a)
            if (a[i] > level >= a[j]) if down else (a[i] < level <= a[j]):
                out.append(float(phi[i] + (phi[(i + 1) % len(a)] - phi[i]) % 360 * (a[i] - level) / (a[i] - a[j])))
        return out
    t = dict(
        hook_catch=206.1,                                    # G1 钩线角
        needle_below_plate=cross(tip, 0.0)[0], needle_above_plate=cross(tip, 0.0, down=False)[0],
        needle_reaches_fabric=cross(tip, FABRIC_MAX)[0],
        takeup_top=float(phi[int(np.argmax(eye))]),
        takeup_plateau=[float(min(phi[eye >= eye.max() - 0.4])), float(max(phi[eye >= eye.max() - 0.4]))],
        dog_below=cross(dog, 0.0)[0], dog_above=cross(dog, 0.0, down=False)[0],
    )
    t["idle_deg"] = (t["dog_above"] - t["dog_below"]) % 360
    # 线环：梭尖钩住后带着线环绕过梭壳（旋梭转 2 倍）；梭尖转过约 175° 时线环绕过梭壳最下面，再转到约 250° 时线环张得最大、
    # 两条腿分得最开（教材第 14 章同一组参数：206°–293° 绕梭壳，约 300°–330° 进刀）
    t["loop_round_bobbin"] = [t["hook_catch"], t["hook_catch"] + 175.0 / 2]
    t["knife_entry_window"] = [300.0, 330.0]
    return t, dict(phi=phi, tip=tip, eye=eye, dog=dog)


# ------------------------------------------------------------------ ③ 剪线凸轮（主轴 1 : 1，凸轮角 = φ）
SEG = dict(rise=(280.0, 340.0), hold=(340.0, 380.0), ret=(380.0, 435.0))   # 380 = 20°、435 = 75°（下一转）


def cyc(u):
    """摆线运动规律：位移、速度、加速度（无量纲，u 0…1）"""
    s = u - math.sin(2 * math.pi * u) / (2 * math.pi)
    v = 1 - math.cos(2 * math.pi * u)
    a = 2 * math.pi * math.sin(2 * math.pi * u)
    return s, v, a


def cam_lift(phi, h):
    """凸轮的从动件位移 s(φ)（0 = 动刀在最后，h = 最前）、ds/dφ（每弧度）"""
    p = phi % 360
    if p < SEG["rise"][0] - 360 + 360 and p < 75.0 and p >= 20.0:     # 回程 20…75
        b = (SEG["ret"][1] - SEG["ret"][0]) * DEG
        s, v, _ = cyc((p - 20.0) / 55.0)
        return h * (1 - s), -h * v / b
    if p < 20.0:
        return h, 0.0
    if SEG["rise"][0] <= p < SEG["rise"][1]:
        b = (SEG["rise"][1] - SEG["rise"][0]) * DEG
        s, v, _ = cyc((p - SEG["rise"][0]) / (SEG["rise"][1] - SEG["rise"][0]))
        return h * s, h * v / b
    if p >= SEG["rise"][1]:
        return h, 0.0
    return 0.0, 0.0


def knife():
    k = GEO["knife"]
    px, py = k["pivot"]
    fx, fy = k["tip_fwd"]
    R = math.hypot(fx - px, fy - py)
    a_f = math.atan2(fy - py, fx - px)
    # 刀尖退到 x = tip_rest_x：px + R cos a = x
    a_r = -math.acos((k["tip_rest_x"] - px) / R)
    if a_r > a_f:
        a_r = -a_r
    beta = a_f - a_r                                       # 动刀摆角（逆时针为往前）
    rr = GEO["rock"]
    gamma = beta * k["crank_r"] / rr["crank_r"]            # 剪线摆轴转角（两个曲柄销都沿 y 动，拉杆沿 y）
    # 凸轮：滚子在以下轴中心 C、摆轴中心 S 为直径的圆上（CR ⊥ SR），这样摆杆一摆滚子就沿凸轮半径方向走
    C = np.array(LOW)
    Sx = np.array((rr["y"], rr["z"]))
    d = float(np.linalg.norm(Sx - C))
    rho0 = GEO["cam"]["rho0"]
    L = math.sqrt(d * d - rho0 * rho0)
    h = L * gamma
    return dict(R_tip=R, a_fwd_deg=a_f / DEG, a_rest_deg=a_r / DEG, beta_deg=beta / DEG, gamma_deg=gamma / DEG,
                lever_L=L, cam_h=h, CS=d)


def cut_angle(kn):
    """动刀回程时刀刃（刀尖后面 edge_back 处的内刃）越过定刀刃 x 的转角"""
    k, fx = GEO["knife"], GEO["fixed"]["x_edge"]
    px, py = k["pivot"]
    R_e = kn["R_tip"] - k["edge_back"]
    for i in range(0, 551):
        p = 20.0 + i * 0.1
        s, _ = cam_lift(p, kn["cam_h"])
        a = kn["a_rest_deg"] + kn["beta_deg"] * s / kn["cam_h"]
        x = px + R_e * math.cos(a * DEG)
        if x <= fx:
            return round(p, 1)
    return None


def forces(kn, n_trim):
    k, rr, cm = GEO["knife"], GEO["rock"], GEO["cam"]
    F_cut = 15.0                                           # 剪两根线（面线 + 底线，#40–#20 涤纶）按 15 N 计
    T_knife = F_cut * (kn["R_tip"] - k["edge_back"])        # N·mm
    F_link = T_knife / k["crank_r"]
    T_rock = F_link * rr["crank_r"]
    F_roll_t = T_rock / kn["lever_L"]                      # 滚子上沿凸轮半径方向的力
    # 压力角（滚子沿半径方向走，凸轮转角 θ = φ）：tan α = (ds/dθ) / ρ
    worst = 0.0
    for p in np.arange(0, 360, 0.5):
        s, ds = cam_lift(p, kn["cam_h"])
        rho = cm["rho0"] + s
        worst = max(worst, math.degrees(math.atan(abs(ds) / rho)))
    F_roll = F_roll_t / math.cos(worst * DEG)
    # 滚子（Ø8 × 宽 6，GCr15）对凸轮槽（20CrMnTi 渗碳淬火）：线接触赫兹应力，凸轮槽壁按平面算（偏保守）
    E = 206e3
    b_w = 6.0
    r1 = cm["roller_d"] / 2
    sig_H = math.sqrt(F_roll * E / (2 * math.pi * (1 - 0.3 ** 2) * b_w * r1))
    # 剪线那一转多出的主轴力矩：凸轮推力 × 力臂（ρ 方向的速度比）
    T_main = 0.0
    for p in np.arange(0, 360, 0.5):
        s, ds = cam_lift(p, kn["cam_h"])
        T_main = max(T_main, F_roll_t * abs(ds))
    return dict(F_cut_N=F_cut, T_knife_Nmm=round(T_knife, 1), F_link_N=round(F_link, 1), T_rock_Nmm=round(T_rock, 1),
                F_roller_N=round(F_roll, 1), pressure_angle_max_deg=round(worst, 1), sigma_H_MPa=round(sig_H, 0),
                sigma_H_allow_MPa=1500, T_main_extra_Nmm=round(T_main, 0),
                ok=worst <= 35.0 and sig_H <= 1500)


def solenoids():
    st = GEO["solenoid_trim"]
    # 剪线电磁铁：推摆杆沿摆轴 5 mm 进槽；回位弹簧 6 N（到位时 9 N）、摆杆在轴上的摩擦（停在静止段，没有横向力，按 2 N）
    need_trim = 9.0 + 2.0
    trim = dict(stroke_mm=st["stroke"], need_N=need_trim, pick="24 V 推拉式电磁铁 Ø22（示例：行程 5 mm 时 22 N，通电 20%）",
                F_at_stroke_N=22.0, SF=round(22.0 / need_trim, 2), t_pull_in_ms=(5, 15))
    # 松线电磁铁：夹线簧最大 8.4 N + 张开 0.5 mm 的弹簧增量；立轴拨杆销臂 / 推杆臂 = 1.06；电磁铁臂 10、推杆臂 |r_rod| 10
    ten = CTRL["tension"]
    F_pin = ten["N_range_N"][1] + ten["spring"]["k_Nmm"] * 0.5
    r_pin = math.hypot(*CTRL["geo"]["release"]["r_pin"])
    r_sol = math.hypot(*GEO["sol_release"]["arm"])
    need_rel = F_pin * r_pin / r_sol
    rel = dict(need_N=round(need_rel, 1), pick="24 V 拉式电磁铁 Ø16（示例：行程 3 mm 时 15 N）", F_at_stroke_N=15.0,
               SF=round(15.0 / need_rel, 2), opening_mm=round(GEO["sol_release"]["stroke"] * r_pin / r_sol - 0.5, 2),
               note="行程 3 mm：先走完松线销 0.5 mm 的空程，再推开夹线盘")
    w = GEO["wiper"]
    wip = dict(pick="24 V 拉式电磁铁 Ø16（示例：行程 10 mm 时 8 N）", sweep_deg=w["sweep_deg"], r_mm=w["r"],
               t_sweep_ms=60, note="电磁铁经机头里的小曲柄（半径 5）转拨线轴 115°（曲柄过死点前后各 57.5°，行程 2 × 5 sin 57.5° = 8.4）；拨线钩是 Ø1.2 弹簧钢丝",
               needle_tip_min_mm=round(w["wire_z"] + w["wire_d"] / 2 + 1.0, 1))
    return dict(trim=trim, release=rel, wiper=wip, ok=trim["SF"] >= 1.5 and rel["SF"] >= 1.5)


def trim_speed(t, kn):
    """剪线转速上限：① 动刀回到最后（75°）以后、针尖碰布（留 5°）以前停住；② 电磁铁合上：凸轮入口段（静止段）要装得下延迟变化"""
    stop_lo = SEG["ret"][1] - 360
    # 停针上限：针尖碰布面前留 5°；拨线钩要从停住的针尖下面扫过（针尖离钢丝顶 ≥ 1.0）
    fr = t["_fr"]
    tip_min = GEO["wiper"]["wire_z"] + GEO["wiper"]["wire_d"] / 2 + 1.0
    ph = [p for p, z in zip(fr["phi"], fr["tip"]) if 60 <= p <= 120 and z >= tip_min]
    stop_wiper = max(ph)
    stop_hi = min(t["needle_reaches_fabric"] - 5.0, stop_wiper)
    W = (stop_hi - stop_lo) * DEG
    n_stop = math.sqrt(2 * ALPHA_STOP * W) * 60 / (2 * math.pi)
    gate = (100.0, SEG["rise"][0] - 5.0)                 # 滚子可以进槽的入口段（退出斜面之后、进刀之前留 5°）
    gate_w = gate[1] - gate[0]
    dt = (15 - 5) / 1000.0
    n_gate = (gate_w - 10.0) / (6 * dt) if gate_w > 10 else 0.0
    n_ok = 300.0
    return dict(stop_window=[stop_lo, round(stop_hi, 1)], stop_hi_fabric=round(t["needle_reaches_fabric"] - 5.0, 1), stop_hi_wiper=stop_wiper,
                n_stop_max=round(n_stop), gate=list(gate),
                gate_deg=gate_w, n_gate_max=round(n_gate), n_trim_max=round(min(n_stop, n_gate)),
                n_trim_default=n_ok, ok=min(n_stop, n_gate) >= n_ok)


def thread_tail(t, kn, fr):
    """针眼外留的面线（估算）：剪断时针眼高度 + 针板 + 到动刀平面 + 针孔到定刀刃的水平距离；
    松线时挑线杆从线团那边抽线，夹在动刀钩里的线环不缩，线环绕梭壳的半圈（梭壳半径 11.2）也留在线头上"""
    pc = cut_angle(kn)
    i = int(round((pc % 360) / 2)) % len(fr["phi"])
    eye_h = fr["tip"][i] + 2.8
    plane = -sum(GEO["knife_plane"]) / 2
    horiz = abs(GEO["fixed"]["x_edge"])
    loop = math.pi * 11.2
    L = eye_h + plane + horiz + loop
    return dict(cut_deg=pc, eye_above_plate=round(eye_h, 1), tail_est_mm=round(L, 1), tail_min_mm=35.0,
                bobbin_tail_est_mm=round(plane - GEO["plate_bottom"] + 1.5, 1), ok=bool(L >= 35.0),
                note="估算；首件试缝量实际线头，偏短就把定刀刃往左挪")


# ------------------------------------------------------------------ ⑥ 电子针距
MOTORS = [   # 示例：常见规格的典型样本值（24 V 驱动），选型以实际样本复核
    dict(name="42 步进 48 mm（闭环，带磁编码器）", T_hold=0.55, J=68e-7, n_c=300.0, I=1.7),
    dict(name="42 步进 60 mm（闭环，带磁编码器）", T_hold=0.73, J=102e-7, n_c=250.0, I=2.0),
    dict(name="57 步进 56 mm（闭环）", T_hold=1.2, J=300e-7, n_c=200.0, I=3.0),
]


def torque_at(m, n):
    """可用力矩（简化：转速 n_c 以下为保持力矩的 80%，以上按恒功率下降）N·m"""
    T = 0.8 * m["T_hold"]
    return T if n <= m["n_c"] else T * m["n_c"] / n


def efeed(t, stitch=5.0):
    """换向：从 +stitch 换到 −stitch，要在送布牙沉在针板下面的空闲角里（两头各留 10°）转完"""
    a_per_mm = FD["dial"]["alpha_per_mm_deg"]
    M_reg = max(DYN[k]["strength"]["regulator"]["M_max_Nmm"] for k in DYN) / 1000.0      # N·m
    swing = 2 * stitch * a_per_mm * DEG                   # 调节器转角
    J_reg = 3.0e-6                                        # 调节器、滑块、大带轮绕调节器轴（估算）kg·m²
    margin = 10.0
    win = t["idle_deg"] - 2 * margin
    rows = []
    for m in MOTORS:
        for i in (1, 2, 3):
            hold = torque_at(m, 0) * i
            if hold < 2 * M_reg:
                rows.append(dict(motor=m["name"], ratio=i, hold_Nm=round(hold, 3), ok_hold=False))
                continue
            th = swing * i                                 # 电机要转的角度
            Jt = m["J"] + J_reg / i ** 2
            # 找最高主轴转速 N：换向时间 t = win / (6 N)；三角形速度曲线 α = 4θ/t²、最高转速 ω = 2θ/t；要 J α ≤ T(ω)
            lo, hi = 100.0, 6000.0
            for _ in range(60):
                N = (lo + hi) / 2
                tt = win / (6 * N)
                a = 4 * th / tt ** 2
                w = 2 * th / tt
                if Jt * a <= torque_at(m, w * 60 / (2 * math.pi)):
                    lo = N
                else:
                    hi = N
            steps = 200 * 16
            res = (a_per_mm * DEG) ** -1 * (2 * math.pi / (steps * i))      # 每一微步对应的针距 mm
            rows.append(dict(motor=m["name"], ratio=i, hold_Nm=round(hold, 3), ok_hold=True, n_reverse_max=round(lo),
                             t_switch_ms=round(win / (6 * lo) * 1000, 1), res_mm=round(res, 4)))
    return dict(M_reg_Nm=M_reg, stitch_mm=stitch, swing_deg=round(swing / DEG, 1), idle_deg=round(t["idle_deg"], 1),
                margin_deg=margin, window_deg=round(win, 1), table=rows)


PICK = dict(motor="42 步进 48 mm（闭环，带磁编码器）", ratio=2)     # 用 GC 现有的 24 V、TMC2226 驱动带得动的最小电机


def efeed_all(t):
    full, bt = efeed(t, 5.0), efeed(t, 3.0)
    f = next(r for r in full["table"] if r["motor"] == PICK["motor"] and r["ratio"] == PICK["ratio"])
    b = next(r for r in bt["table"] if r["motor"] == PICK["motor"] and r["ratio"] == PICK["ratio"])
    return dict(full=full, backtack_3mm=bt, pick=PICK | dict(hold_Nm=f["hold_Nm"], n_full_max=f["n_reverse_max"],
                n_3mm_max=b["n_reverse_max"], res_mm=f["res_mm"], SF_hold=round(f["hold_Nm"] / full["M_reg_Nm"], 2)),
                targets=dict(n_full=1600, n_3mm=2200, res_mm=0.05, SF_hold=2.0),
                ok=f["n_reverse_max"] >= 1600 and b["n_reverse_max"] >= 2200 and f["res_mm"] <= 0.05 and f["hold_Nm"] >= 2 * full["M_reg_Nm"])


def main():
    D = Path(sys.argv[1])
    frames = json.loads((D / "frames.json").read_text())["frames"]
    t, fr = timing(frames)
    kn = knife()
    t["_fr"] = {k: [float(x) for x in v] for k, v in fr.items()}
    tt = {k: (round(v, 1) if isinstance(v, float) else v) for k, v in t.items() if not k.startswith("_")}
    res = dict(geo=GEO, timing=tt, cam_segments=SEG,
               knife=kn | {"cut_deg": cut_angle(kn)}, forces=forces(kn, 300.0), solenoids=solenoids(),
               trim_speed=trim_speed(t, kn), thread_tail=thread_tail(t, kn, fr), efeed=efeed_all(t))
    res["all_ok"] = all(res[k]["ok"] for k in ("forces", "solenoids", "trim_speed", "efeed"))
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))
    show = {k: res[k] for k in ("timing", "knife", "forces", "solenoids", "trim_speed", "thread_tail")}
    show["efeed"] = res["efeed"]["pick"] | {"ok": res["efeed"]["ok"]}
    print(json.dumps(show, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
