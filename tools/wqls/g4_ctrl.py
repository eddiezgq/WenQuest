"""第 138 轮 G4.7：压脚与操纵件的尺寸和计算 → docs/设计/WQ-LS/G4/操纵件.json（cad/ctrl.py 按其中的 geo 画零件）

    python3 tools/wqls/g4_ctrl.py [零件目录]      零件目录给了，就用其中 parts.json 的质量（不给按估算）

内容：
  ① 压脚组：压脚杆 Ø8、压脚弹簧（调压螺钉调 20–80 N）、压脚跟随送布牙（5000 r/min 不跳）；
  ② 手抬压脚：机头后面扳手带偏心凸轮，抬 5.5 mm，过死点自锁；
  ③ 膝抬压脚：推杆顺着立柱上来 → 立柱里的角杠杆 C1 → 机臂里的水平推杆 → 机头里的角杠杆 C2 → 拉杆勾起抬压脚块，抬 13 mm；
  ④ 松线：抬压脚块抬起 1 mm 后顶起松线轴，经松线推杆、立轴拨杆推开夹线盘；
  ⑤ 针距旋钮、倒缝扳手 → 调节器：调节器板上一条臂，竖拉杆顺着立柱上来；拉杆上端的横臂带一个销，插在针距旋钮端面的
     环形槽里，槽的内、外壁就是倒缝、正缝的限位；倒缝扳手轴上的曲柄拨拉杆上的耳子；拉簧把调节器拉向正缝；
  ⑥ 夹线器、挑线簧。
坐标同整机（spec.py）：x 沿上轴向右，y 向后，z 向上，原点在针板面、针中心，mm。
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

G4 = ROOT / "docs" / "设计" / "WQ-LS" / "G4"
OUT = G4 / "操纵件.json"
FD = json.loads((G4 / "送布机构.json").read_text())
DYN = json.loads((G4 / "送布动力.json").read_text()) if (G4 / "送布动力.json").exists() else {}
N_RPM = 5000.0
W = N_RPM * 2 * math.pi / 60
DEG = math.pi / 180
G_STEEL = 79e3                    # 弹簧钢切变模量 MPa

# ------------------------------------------------------------------ 几何（φ = 0、压脚放下、3 mm 正缝时的位置）
GEO = dict(
    # ① 压脚组
    bar=dict(x=-16.0, y=6.0, d=8.0, bore=4.5, z=(14.0, 186.0)),       # 压脚杆（空心 Ø8 × Ø4.5）
    guide_low=dict(z=(38.0, 50.0), d_bush=12.0),                      # 下导套：机头底板上 G3 已有的凸台（Ø18）
    guide_up=dict(z=(170.0, 182.0), d_bush=12.0, r_boss=9.0),         # 上导套：和针杆上导套座连成一块
    collar=dict(z=(183.0, 186.0), r=8.0),                             # 弹簧座（压脚杆顶端）
    screw=dict(d=18.0, boss_z=(244.0, 256.0), r_boss=13.0),           # 调压螺钉 M18 × 1.5，空心，攻在机头顶上；弹簧（外径 15.8）在螺孔里导向
    foot=dict(sole=(-14.0, 10.0, -14.0, 12.0, 0.0, 3.0), hinge=(0.0, 4.5), shank=(-20.0, -12.0, 0.0, 12.0, 6.0, 22.0)),
    bracket=dict(z=(140.0, 148.0), body=(-24.0, -9.0, 0.0, 12.0),     # 抬压脚块（夹在压脚杆上）
                 cam_arm=(-44.0, -24.0, 14.0, 22.0), hook_arm=(-28.0, -20.0, 12.0, 46.0),
                 rel_tab=(-24.0, -9.0, -13.0, 0.01)),
    # ② 手抬：偏心凸轮在 y 14…22，轴沿 y 从凸轮到机头后壁外
    hand=dict(x=-40.0, z=None, e=8.0, rho=10.0, theta_rest=80.0, theta_up=-10.0, y=(14.0, 22.0), y_out=76.0, lever=45.0, gap=1.0),
    # ③ 膝抬：推杆（立柱里）→ C1 → 水平推杆（机臂里）→ C2（机头里）→ 拉杆 → 抬压脚块的钩臂
    knee=dict(y=42.0, rod_z=190.0, push=dict(x=384.0, z=(-75.0, None), d=8.0),
              C1=dict(x=368.0, z=168.0, up=22.0, side=16.0), C2=dict(x=-46.0, z=168.0, up=22.0, side=22.0),
              link_x=-24.0, arm_rod_d=6.0, gap=0.0),
    # ④ 松线：轴沿 y（x −30、z 176，y −36…−2），y −9…−5 的臂伸到抬压脚块的松线舌上面（间隙 1）；y −36 那头的臂朝下 4，
    #   接松线推杆（沿 x，y −34、z 172，到 x 63.5）；
    #   立轴拨杆（轴线沿 z，在 (74, −28)），下臂接推杆，上臂推夹线柱里的松线销（x 66、y −35、z 210）
    release=dict(shaft=(-30.0, 176.0, -36.0, -2.0), tip=(-14.0, 149.0), a_rod=4.5, rod=(-34.0, 172.0, 63.5), gap=1.0,
                 pivot=(74.0, -28.0, 168.0, 214.0), r_rod=(-8.0, -6.0), r_pin=(-8.0, -7.0)),
    # ⑤ 针距旋钮、倒缝扳手
    dial=dict(x=340.0, z=170.0, y_cam=(-50.0, -44.0), r0=20.0, rp=2.5, turn_deg=300.0),
    reg_arm=dict(len=20.0),                                           # 调节器板上的臂（朝前），臂端的销伸到 x 326
    pull_rod=dict(x=324.0, y=-20.0, d=6.0, lug=(330.0, -23.0, 128.0), top_z=150.0),
    reverse=dict(x=352.0, z=128.0, y_in=-26.0, handle=56.0, crank=22.0),   # 倒缝扳手转轴（G3 在 z 116，挪到 128 让开立柱横隔板 z 115…122）
    spring_rev=dict(top=(324.0, -24.0, 100.0), anchor=(324.0, -36.0, 62.0)),
    # ⑥ 夹线器（G3 的位置）
    tension=dict(x=66.0, z=210.0, y_wall=-46.0, post_d=5.0, disc_d=22.0),
)
GEO["hand"]["z"] = GEO["bracket"]["z"][0] - GEO["hand"]["gap"] - (GEO["hand"]["e"] * math.cos(GEO["hand"]["theta_rest"] * DEG) + GEO["hand"]["rho"])
GEO["knee"]["push"]["z"] = (-75.0, GEO["knee"]["C1"]["z"])


def presser(mass_kg=0.104):
    """① 压脚弹簧和压脚跟随。运动质量 = 压脚杆、压脚、抬压脚块、弹簧座 + 弹簧质量的 1/3（零件目录给了就用实体的质量）。
    送布牙把压脚（没有布时直接、有布时隔着布）顶起 ≤ 0.8 mm 再落回，压脚要靠弹簧跟着往下：弹簧力 ≥ 1.5 × m × 最大向下加速度。
    加速度和转速的平方成正比，所以给定压力下不跳的最高转速 n = 5000 × √(F / F_需要)。"""
    P = FD["poses"]["s5"]
    dz = np.array([p[1] for p in P["dog"]])                     # 牙顶高出针板（每 2°）
    n = len(dz)
    dphi = 2 * math.pi / n
    zf = np.maximum(dz, 0.0) / 1000                              # 压脚（没有布时）被牙顶起的高度 m
    a = (np.roll(zf, -1) - 2 * zf + np.roll(zf, 1)) / dphi ** 2 * W ** 2
    on = dz > 0
    a_down = float(-np.min(np.where(on, a, 0.0)))               # 牙在针板上面、压脚跟着往下时最大的向下加速度
    F_need = 1.5 * mass_kg * a_down
    # 弹簧：琴钢丝（SWP-B）d 1.8、中径 14、有效圈 16
    d, D, n_c = 1.8, 14.0, 16
    k = G_STEEL * d ** 4 / (8 * D ** 3 * n_c)
    C = D / d
    Kw = (4 * C - 1) / (4 * C - 4) + 0.615 / C
    tau = lambda F: Kw * 8 * F * D / (math.pi * d ** 3)          # noqa: E731
    Hs = (n_c + 2) * d                                           # 并紧高度
    F_lo, F_hi, lift = 20.0, 80.0, 13.0
    x_hi = F_hi / k + lift
    H0 = round(Hs + x_hi + 5.0, 0)                               # 自由高度：最大压缩后还剩 5 mm 不并紧
    sb = 2000.0                                                  # d 1.8 琴钢丝抗拉强度 MPa（SWP-B 下限）
    # 缝纫时：压脚压力 80 N 档，牙把压脚顶起 0.8 mm 再落回 → 脉动；按 Goodman（τ−1 取 0.30 σb、τb 取 0.6 σb）
    Fa, Fm = k * 0.8 / 2, F_hi + k * 0.8 / 2
    ta, tm = tau(Fa), tau(Fm)
    SF_fat = 1 / (ta / (0.30 * sb) + tm / (0.6 * sb))
    SF_static = 0.5 * sb / tau(F_hi + k * lift)                  # 抬到 13 mm：许用取 0.5 σb
    seat0 = GEO["collar"]["z"][1]
    F_set = 50.0                                                 # 出厂压力（G4.6 送布阻力按它算）
    n_max = {f"{int(F)}N": int(round(N_RPM * math.sqrt(F / F_need), -1)) for F in (20.0, 35.0, 50.0, 80.0)}
    return dict(mass_kg=mass_kg, a_down_max_ms2=round(a_down, 1), F_need_N=round(F_need, 1), F_set_N=F_set,
                SF_at_set=round(F_set / (mass_kg * a_down), 2), n_max_rpm=n_max,
                follow_ok=bool(F_set >= F_need),
                spring=dict(wire_mm=d, D_mm=D, n=n_c, k_Nmm=round(k, 3), H0_mm=H0, Hs_mm=round(Hs, 1),
                            L_at_20N=round(H0 - F_lo / k, 1), L_at_80N=round(H0 - F_hi / k, 1),
                            L_80N_lift13=round(H0 - x_hi, 1), screw_travel_mm=round((F_hi - F_lo) / k, 1),
                            screw_bottom_z_20N=round(seat0 + H0 - F_lo / k, 1), screw_bottom_z_80N=round(seat0 + H0 - F_hi / k, 1),
                            tau_max_MPa=round(tau(F_hi + k * lift), 0), SF_static=round(SF_static, 2), SF_fatigue=round(SF_fat, 2),
                            F_80_lift13_N=round(F_hi + k * lift, 1)),
                spring_ok=bool(SF_fat >= 1.5 and SF_static >= 1.2 and H0 - x_hi > Hs))


def hand(F_spring_at_lift):
    """② 偏心凸轮：转角 θ（0 = 偏心朝上），接触点高度 = 轴心 + e cos θ + ρ；从 80° 扳到 −10°（过死点 10° 自锁）"""
    h = GEO["hand"]
    th = np.linspace(h["theta_rest"], h["theta_up"], 91)
    zc = h["z"] + h["e"] * np.cos(th * DEG) + h["rho"]
    rise = zc - zc[0]
    lift = rise - h["gap"]                                       # 压脚抬起量（凸轮先走完 1 mm 间隙）
    # 扳手力：凸轮力矩 = 抬压脚块压在凸轮上的力 × e |sin θ|（接触点在凸轮顶上），手柄长 lever
    k = F_spring_at_lift["k"]
    F = np.where(lift > 0, F_spring_at_lift["F0"] + k * np.maximum(lift, 0), 0.0)
    T = F * h["e"] * np.abs(np.sin(th * DEG))
    lock = bool(h["theta_up"] < 0)                               # 过死点：力的作用线越过轴心，把扳手压向限位
    return dict(shaft_z=round(h["z"], 2), lift_mm=round(float(lift[-1]), 2), lift_top_dead_center_mm=round(float(h["e"] * (1 - math.cos(h["theta_rest"] * DEG)) - h["gap"]), 2),
                F_hand_max_N=round(float(np.max(T)) / h["lever"], 1), self_lock=lock,
                ok=bool(abs(float(lift[-1]) - 5.5) <= 0.3 and float(np.max(T)) / h["lever"] <= 30.0 and lock))


def knee(F_spring_at_lift):
    """③ 膝抬连杆：两个角杠杆（转轴都沿 y），抬压脚块抬 13 mm。C2：水平臂端（x −24）上下动、拉杆勾起抬压脚块；
    竖臂上端接机臂里的水平推杆。C1：竖臂上端接水平推杆，水平臂端被立柱里的推杆往上顶。转角按对称于水平位置取。"""
    kn = GEO["knee"]
    c2, c1 = kn["C2"], kn["C1"]
    L2s = kn["link_x"] - c2["x"]                                 # C2 水平臂 22
    lift = 13.0
    b2 = 2 * math.asin(lift / 2 / L2s)                           # C2 总转角（水平臂从 −b2/2 转到 +b2/2）
    s_rod = 2 * c2["up"] * math.sin(b2 / 2)                      # 水平推杆位移（竖臂端的水平位移，弦长）
    b1 = 2 * math.asin(s_rod / 2 / c1["up"])
    s_push = 2 * c1["side"] * math.sin(b1 / 2)
    # 力（静力，按最不利位置：臂偏离垂直的最大角 b/2）：抬压脚块的力 F = 弹簧（80 N 档）在抬起 13 mm 时
    F_lift = F_spring_at_lift["F0"] + F_spring_at_lift["k"] * lift
    F_rod = F_lift * L2s / c2["up"] / math.cos(b2 / 2) ** 2      # 两臂都斜 b2/2：力臂都乘 cos
    F_push = F_rod * c1["up"] / c1["side"] / math.cos(b1 / 2) ** 2
    # 传动角：推杆、拉杆和臂之间的夹角最小值（90° − 偏斜角）
    mu_min = 90 - math.degrees(max(b1, b2)) / 2
    # 台板下的膝控板（外购标准件）：杠杆比按 5 计（膝盖处行程约 5 × 推杆行程）——只用来估膝推力
    knee_ratio = 5.0
    E = 2.1e5
    Pcr_rod = math.pi ** 2 * E * (math.pi * kn["arm_rod_d"] ** 4 / 64) / (c1["x"] - c2["x"]) ** 2
    Pcr_push = math.pi ** 2 * E * (math.pi * kn["push"]["d"] ** 4 / 64) / (kn["push"]["z"][1] - kn["push"]["z"][0]) ** 2
    return dict(lift_mm=lift, C2_turn_deg=round(math.degrees(b2), 1), C1_turn_deg=round(math.degrees(b1), 1),
                arm_rod_travel_mm=round(s_rod, 2), push_rod_travel_mm=round(s_push, 2),
                F_lift_N=round(F_lift, 1), F_arm_rod_N=round(F_rod, 1), F_push_N=round(F_push, 1),
                knee_ratio_assumed=knee_ratio, F_knee_N=round(F_push / knee_ratio, 1), transmission_min_deg=round(mu_min, 1),
                SF_buckling_arm_rod=round(Pcr_rod / F_rod, 1), SF_buckling_push=round(Pcr_push / F_push, 1),
                ok=bool(F_push / knee_ratio <= 60 and mu_min >= 40 and Pcr_rod / F_rod >= 3 and Pcr_push / F_push >= 3))


def release_angle(lift):
    """④ 松线轴的转角：长臂端（tip，r 2.5 的圆头）搁在抬压脚块的松线舌上，舌比臂端低 gap。舌的右端在 x_end：臂端转过去、
    圆心越过 x_end 后就从舌上滑下来，靠在舌的侧面上不再转（空行程）——所以压脚抬多高，松线轴最多转 θ_max。"""
    r = GEO["release"]
    (rx, rz), (tx, tz) = r["shaft"][:2], r["tip"]
    vx, vz = tx - rx, tz - rz
    x_end = GEO["bracket"]["rel_tab"][1]
    th_max = 0.0
    while rx + vx * math.cos(th_max) - vz * math.sin(th_max) < x_end:
        th_max += 1e-4
    rise = lambda th: (vx * math.sin(th) + vz * math.cos(th)) - vz                                  # noqa: E731
    need = max(0.0, lift - r["gap"])
    if need >= rise(th_max):
        return th_max
    lo, hi = 0.0, th_max
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if rise(mid) < need else (lo, mid)
    return lo


def release(lift):
    """松线轴转 θ，短臂（a_rod）推松线推杆 a_rod θ；立轴拨杆按 |r_pin| / |r_rod| 变成松线销的位移 = 夹线盘张开量"""
    r = GEO["release"]
    k_lev = math.hypot(*r["r_pin"]) / math.hypot(*r["r_rod"])
    return round(r["a_rod"] * release_angle(lift) * k_lev, 3)


def dial():
    """⑤ 针距旋钮槽的内外壁、拉杆、倒缝扳手力。调节器角 α（正 = 正缝）→ 调节器臂端 z = −50 − L sin α，拉杆跟着上下。
    旋钮刻度 s（0…5）↔ 旋钮转角 θ = turn × s / 5。正缝：拉簧把拉杆往下拉，销被拉向槽外壁（离旋钮轴远）；倒缝：扳手把拉杆
    往上拨，销靠到槽内壁。内、外壁按正缝、倒缝各自的调节器角做，所以倒缝针距也对。"""
    dl, ra = GEO["dial"], GEO["reg_arm"]
    d = FD["dial"]
    fw = sorted([(s["s"], s["alpha_deg"]) for s in FD["settings"] if not s["reverse"]])
    rv = sorted([(s["s"], s["alpha_deg"]) for s in FD["settings"] if s["reverse"]])
    s_grid = np.linspace(0.0, 5.0, 51)
    a_f = np.interp(s_grid, [0.0] + [a for a, _ in fw], [d["alpha0_deg"]] + [b for _, b in fw])
    a_r = np.interp(s_grid, [0.0] + [a for a, _ in rv], [d["alpha0_deg"]] + [b for _, b in rv])
    dz_f = -ra["len"] * np.sin(a_f * DEG)                      # 拉杆位移（向上为正）：正缝向下
    dz_r = -ra["len"] * np.sin(a_r * DEG)
    r_out = dl["r0"] - dz_f + dl["rp"]                           # 销在旋钮轴正下方 r0 处（z = 150）：拉杆往下 → 半径变大
    r_in = dl["r0"] - dz_r - dl["rp"]
    th = dl["turn_deg"] * s_grid / 5
    # 刻度误差：凸轮按 g4_feed 的标定做，误差来自旋钮刻度线（每格 60°）的读数分辨率 ±1° → 针距 ±1/60 mm
    err = 1.0 / (dl["turn_deg"] / 5)
    # 倒缝扳手力：拉簧 F_s（正缝时拉住调节器，顶住调节器上的送布力矩 M_reg × 1.5）；倒缝时手扳 = (F_s + 拉簧伸长增加 + M_reg / L) × 曲柄 / 手柄
    M_reg = max(DYN[k]["strength"]["regulator"]["M_max_Nmm"] for k in ("s5", "r5")) if DYN and "regulator" in DYN.get("s5", {}).get("strength", {}) else 368.0
    F_dyn = M_reg / ra["len"]
    F_s = round(1.5 * F_dyn + 0.5, 0)
    k_s = 0.3
    travel = float(np.max(dz_r) - np.min(dz_f))
    rv_ = GEO["reverse"]
    F_hand = (F_s + k_s * travel + F_dyn) * rv_["crank"] / rv_["handle"]
    rev_turn = math.degrees(2 * math.asin(travel / 2 / rv_["crank"]))
    knob_T = 0.15 * (F_s + F_dyn) * dl["r0"]                   # 转旋钮：销和槽壁之间的摩擦力矩（μ 0.15）
    ratio = [round(float(abs(a_r[i]) / a_f[i]), 4) for i in range(10, 51, 10)]
    return dict(groove=dict(s=[round(float(x), 2) for x in s_grid], theta_deg=[round(float(x), 1) for x in th],
                            r_out=[round(float(x), 3) for x in r_out], r_in=[round(float(x), 3) for x in r_in]),
                rod_travel_fwd_mm=round(float(-np.min(dz_f)), 2), rod_travel_rev_mm=round(float(np.max(dz_r)), 2),
                scale_err_mm=round(err, 3), M_reg_Nmm=M_reg, F_spring_N=F_s, spring_rate_Nmm=k_s,
                F_reverse_hand_N=round(F_hand, 1), reverse_turn_deg=round(rev_turn, 1), knob_torque_Nmm=round(knob_T, 0),
                knob_force_N=round(knob_T / 19.0, 1), reverse_over_forward=ratio,
                groove_width_min_mm=round(float(np.min(r_out - r_in)), 2),
                ok=bool(err <= 0.2 and F_hand <= 20.0 and float(np.min(r_out - r_in)) >= 2 * dl["rp"] - 1e-6))


def tension():
    """⑥ 夹线器：线在两片夹线盘之间，张力增量 ΔT = 2 μ N（两面摩擦，μ 取 0.2）；设计软件的工作张力 Td 30…280 cN，默认 100。
    夹线簧：琴钢丝 d 0.7、中径 8、有效圈 6；调节螺母行程按 N 的范围；松线时再压缩松线量。挑线簧：行程按设计软件（10 mm）。"""
    mu = 0.2
    N = lambda T_cN: T_cN / 100 / (2 * mu)                        # noqa: E731
    d, D, n = 0.7, 8.0, 6
    k = G_STEEL * d ** 4 / (8 * D ** 3 * n)
    C = D / d
    Kw = (4 * C - 1) / (4 * C - 4) + 0.615 / C
    N_lo, N_hi = N(30), N(280) * 1.2                              # 上限留 20%
    rel = release(13.0)
    x_max = N_hi / k + rel
    Hs = (n + 2) * d
    tau = Kw * 8 * (N_hi + k * rel) * D / (math.pi * d ** 3)
    sb = 2300.0
    tk = json.loads((G4 / "挑线机构.json").read_text())["result"]
    return dict(mu=mu, N_range_N=[round(N_lo, 2), round(N_hi, 2)], spring=dict(wire_mm=d, D_mm=D, n=n, k_Nmm=round(k, 3),
                nut_travel_mm=round((N_hi - N_lo) / k, 1), H0_mm=round(Hs + x_max + 2, 1), tau_max_MPa=round(tau, 0),
                SF_static=round(0.5 * sb / tau, 2)),
                release_open_mm=dict(lift_3=release(3.0), lift_5_5=release(5.5), lift_13=rel),
                check_spring=dict(stroke_mm=10.0, takeup_pre_mm=round(tk["pre"], 2), arm_mm=15.0, turn_deg=round(math.degrees(10.0 / 15.0), 1),
                                  force_cN=(30, 50), ok=bool(tk["pre"] <= 10.0)),
                ok=bool(release(3.0) >= 0.5 and 0.5 * sb / tau >= 1.2))


def needle_window():
    """膝抬 13 mm 时压脚顶面（底板 3 厚，z 16）比针夹底高：针杆往下走到针夹底离压脚顶不到 1 mm 就会碰。算出针杆能转的范围
    （主轴转角 φ，0 = 上止点），控制器只在这个范围里停针时才允许膝抬、自动抬压脚（GC），手抬 5.5 mm 时整转都不碰。"""
    import spec as S
    r, l, ZU = S.SEW["r"], S.SEW["l"], S.ZU
    zb0 = r - l + ZU - S.MECH_X["nb_below"]                     # 上止点时针杆下端 z
    out = {}
    for lift in (5.5, 13.0):
        top = lift + GEO["foot"]["sole"][5]
        ok = []
        for phi in range(0, 360):
            q = phi * DEG
            zb = r * math.cos(q) - math.sqrt(l * l - (r * math.sin(q)) ** 2) + ZU - S.MECH_X["nb_below"]
            ok.append(zb - 1.5 - top >= 1.0)                     # 针夹底 = 针杆下端 − 1.5
        bad = [p for p in range(360) if not ok[p]]
        out[str(lift)] = dict(foot_top=top, clamp_bottom_bdc=round(zb0 - 2 * r - 1.5, 2),
                              blocked_phi=[min(bad), max(bad)] if bad else None)
    return out


def main():
    mass = 0.104
    if len(sys.argv) > 1:
        info = json.loads((Path(sys.argv[1]) / "parts.json").read_text())["parts"]
        ks = [k for k in ("presser_bar", "presser_foot", "lift_bracket", "presser_collar") if k in info]
        if len(ks) == 4:
            mass = round(sum(info[k]["mass_kg"] for k in ks) + 0.0158 / 3, 4)          # 弹簧 15.8 g（钢丝长 π × 14 × 18）的 1/3
    pr = presser(mass)
    sp = dict(F0=80.0, k=pr["spring"]["k_Nmm"])
    res = dict(geo=GEO, presser=pr, hand=hand(sp), knee=knee(sp), dial=dial(), tension=tension())
    res["release"] = dict(gap_mm=GEO["release"]["gap"], open_mm=res["tension"]["release_open_mm"],
                          theta_deg={str(L): round(math.degrees(release_angle(L)), 2) for L in (0.0, 3.0, 5.5, 13.0)})
    res["needle_window"] = needle_window()
    res["checks"] = {"压脚跟随（出厂 50 N、5000 r/min）": pr["follow_ok"], "压脚弹簧": pr["spring_ok"], "手抬": res["hand"]["ok"], "膝抬": res["knee"]["ok"],
                     "针距旋钮、倒缝": res["dial"]["ok"], "夹线器、松线": res["tension"]["ok"], "挑线簧": res["tension"]["check_spring"]["ok"]}
    res["all_ok"] = all(res["checks"].values())
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1))
    show = {k: v for k, v in res.items() if k not in ("geo", "dial")}
    show["dial"] = {k: v for k, v in res["dial"].items() if k != "groove"}
    print(json.dumps(show, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
