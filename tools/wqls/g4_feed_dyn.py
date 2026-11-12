"""第 138 轮 G4.6：送布组的动力学——惯性力矩、送布连杆力、各铰链力的量级，给 G2（上轴、电机）复算用。

    python3 tools/wqls/g4_feed_dyn.py <零件目录（g4_parts.py 的输出，读 parts.json）>   → docs/设计/WQ-LS/G4/送布动力.json

做法：各运动件的质心位置、转角由 g4_mech.py 的变换（g4_feed.py 综合出的尺寸）给出，主轴匀速 ω，对 φ 中心差分求速度、加速度；
  驱动力矩（能量法）T = Σ (m a·v + I_c ε θ̇) / ω，送布链（偏心以下）加在上轴，抬牙链加在下轴（经同步带 1 : 1 也回到上轴）；
  送布阻力：牙在针板上面时，压脚压力 P 下布的摩擦 μP 阻碍送布、牙往上顶压脚 → 功率 μP|ẏ| + P·ż（同 dyn.py）；
  送布连杆是二力杆（两端铰接），上轴送布偏心受的力 F = T_送布链 / h，h 是上轴中心到连杆线的距离（|h| 小于偏心量的 0.3 倍时不算）。
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE)]

FEED_PARTS = ["feed_rod", "reg_slider", "feed_link", "feed_rock", "feed_bar"]
LIFT_PARTS = ["lift_link", "lift_rock"]


def run(mdir: Path, setting="s5", n_rpm=5000.0, P_foot=50.0, mu=0.25):
    os.environ["WQ_FEED"] = setting
    import importlib
    import g4_mech
    importlib.reload(g4_mech)
    info = json.loads((mdir / "parts.json").read_text())["parts"]
    FR = g4_mech.frames()
    FD = json.loads((ROOT / "docs" / "设计" / "WQ-LS" / "G4" / "送布机构.json").read_text())
    FP = FD["poses"][setting]
    N = len(FR)
    w = n_rpm * 2 * math.pi / 60
    dphi = 2 * math.pi / N
    T_parts, F_in, KIN = {}, np.zeros((N, 2)), {}
    for k in FEED_PARTS + LIFT_PARTS:
        p = info[k]
        m = p["mass_kg"]
        I_c = p.get("Ixx_kgmm2", 0.0) * 1e-6                 # kg·m²
        c0 = np.array([1.0, *p["com"]])[[1, 2, 3]]
        com, ang = [], []
        for f in FR:
            M = np.array(f["M"][k]).reshape(4, 4)
            c = M[:3, :3] @ np.array(p["com"]) + M[:3, 3]
            com.append(c[1:3] / 1000)
            ang.append(math.atan2(M[2, 1], M[1, 1]))
        com, ang = np.array(com), np.unwrap(np.array(ang))
        v = (np.roll(com, -1, 0) - np.roll(com, 1, 0)) / (2 * dphi) * w
        a = (np.roll(com, -1, 0) - 2 * com + np.roll(com, 1, 0)) / dphi ** 2 * w ** 2
        om = (np.roll(ang, -1) - np.roll(ang, 1)) / (2 * dphi) * w
        al = (np.roll(ang, -1) - 2 * ang + np.roll(ang, 1)) / dphi ** 2 * w ** 2
        T_parts[k] = (m * np.sum(a * v, axis=1) + I_c * al * om) / w
        KIN[k] = dict(m=m, I_c=I_c, com=com, a=a, v=v, al=al)
        F_in += m * a                                           # 各件的惯性力之和（机壳受到的是 −Σ m a）
        del c0
    T_feed_inertia = sum(T_parts[k] for k in FEED_PARTS)
    T_lift_inertia = sum(T_parts[k] for k in LIFT_PARTS)
    # 送布阻力（牙在针板上面时）
    dog = np.array(FP["dog"]) / 1000
    vd = (np.roll(dog, -1, 0) - np.roll(dog, 1, 0)) / (2 * dphi) * w
    above = dog[:, 1] > 0
    T_resist = np.where(above, mu * P_foot * np.abs(vd[:, 0]) + P_foot * vd[:, 1], 0.0) / w
    # 送布阻力分到两条链：前后（y）那部分走送布链，上下（z）那部分走抬牙链
    T_res_feed = np.where(above, mu * P_foot * np.abs(vd[:, 0]), 0.0) / w
    T_res_lift = np.where(above, P_foot * vd[:, 1], 0.0) / w
    T_up = T_feed_inertia + T_res_feed                       # 上轴送布偏心上的力矩
    T_low = T_lift_inertia + T_res_lift                      # 下轴抬牙偏心上的力矩
    # 送布连杆力（二力杆）
    O1 = np.array(FD["geo"]["O1"])
    E, P = np.array(FP["E"]), np.array(FP["P"])
    u = (P - E) / np.linalg.norm(P - E, axis=1)[:, None]
    h = ((O1 - E)[:, 0] * u[:, 1] - (O1 - E)[:, 1] * u[:, 0]) / 1000          # m
    ok = np.abs(h) > 0.3 * FD["params"]["eF"] / 1000
    F_rod = np.where(ok, T_up / np.where(ok, h, 1.0), np.nan)
    phi = np.arange(N) * 360.0 / N
    ST = strength(FD, FP, KIN, dog, vd, above, w, dphi, P_foot, mu, F_rod)
    res = dict(strength=ST, setting=setting, n_rpm=n_rpm, phi=phi.tolist(),
               T_up_Nm=np.round(T_up, 5).tolist(), T_low_Nm=np.round(T_low, 5).tolist(),
               F_rod_N=[None if not math.isfinite(x) else round(float(x), 2) for x in F_rod],
               rod_dir=np.round(u, 5).tolist(),
               T_inertia_Nm=np.round(T_feed_inertia + T_lift_inertia, 5).tolist(), T_resist_Nm=np.round(T_resist, 5).tolist(),
               F_fe_vertical_N=[None if not math.isfinite(x) else round(float(x), 2) for x in F_rod * u[:, 1]],
               F_inertia_N=np.round(F_in, 3).tolist(),
               summary=dict(T_up_max=round(float(np.max(np.abs(T_up))), 4), T_low_max=round(float(np.max(np.abs(T_low))), 4),
                            T_total_max=round(float(np.max(np.abs(T_up + T_low))), 4), T_total_mean=round(float(np.mean(T_up + T_low)), 5),
                            P_mean_W=round(float(np.mean(T_up + T_low)) * w, 2),
                            F_rod_max=round(float(np.nanmax(np.abs(F_rod))), 1),
                            T_parts_max={k: round(float(np.max(np.abs(v))), 4) for k, v in T_parts.items()},
                            m_moving_kg={k: info[k]["mass_kg"] for k in FEED_PARTS + LIFT_PARTS}))
    return res


def _cross(a, b):
    return a[..., 0] * b[..., 1] - a[..., 1] * b[..., 0]


def strength(FD, FP, KIN, dog, vd, above, w, dphi, P_foot, mu, F_rod):
    """送布组各件的力和强度（每个 φ 按牛顿—欧拉解，单位 N、N·m、MPa）：
      牙架：受摆杆在 T 的力 F_A（y、z）、抬牙叉在 K 的力 F_K（只有 z：叉槽沿牙架方向）、布在牙上的力（牙在针板上面时：
        压脚压力 −P 向下、摩擦 μP 与牙的前后速度反向）、惯性力 m a；转动惯量小，略去 → 三个方程解 F_Ay、F_Az、F_Kz；
      送布摆轴：T_rock = I_Fr ε + (T − Fr) × F_A（L2 给的驱动力矩），L2 的力 = T_rock / |(C − Fr) × e_L2|；
      抬牙摆轴：T_lift = I_Lr ε + (K − Lr) × F_K，抬牙连杆的力 = T_lift / |(D − Lr) × e_L3|。"""
    g = FD["geo"]
    mm = lambda k: np.array(FP[k]) / 1000                                                          # noqa: E731
    T, K, C, Pp, D, EL = mm("T"), mm("K"), mm("C"), mm("P"), mm("D"), mm("EL")
    Fr, Lr = np.array(g["Fr"]) / 1000, np.array(g["Lr"]) / 1000
    b = KIN["feed_bar"]
    Fc = np.zeros_like(dog)
    Fc[:, 0] = np.where(above, -mu * P_foot * np.sign(vd[:, 0]), 0.0)
    Fc[:, 1] = np.where(above, -P_foot, 0.0)
    ma = b["m"] * b["a"]
    F_Ay = ma[:, 0] - Fc[:, 0]
    # 对 K 取矩（牙架转动惯量略去）：(T−K)×F_A + (dog−K)×Fc = (com−K)×m a
    rT, rD, rC = T - K, dog - K, b["com"] - K
    F_Az = (_cross(rC, ma) - _cross(rD, Fc) + rT[:, 1] * F_Ay) / rT[:, 0]
    F_Kz = ma[:, 1] - Fc[:, 1] - F_Az
    F_A = np.stack([F_Ay, F_Az], 1)
    F_K = np.stack([np.zeros_like(F_Kz), F_Kz], 1)

    def rock(k, piv, Fpt, F):
        q = KIN[k]
        I_p = q["I_c"] + q["m"] * np.sum((q["com"] - piv) ** 2, axis=1)
        return I_p * q["al"] + _cross(Fpt - piv, F)

    T_rock = rock("feed_rock", Fr, T, F_A)
    T_lift = rock("lift_rock", Lr, K, F_K)
    e2 = (C - Pp) / np.linalg.norm(C - Pp, axis=1)[:, None]
    e3 = (D - EL) / np.linalg.norm(D - EL, axis=1)[:, None]
    F_L2 = T_rock / np.abs(_cross(C - Fr, e2))
    F_L3 = T_lift / np.abs(_cross(D - Lr, e3))
    mx = lambda x: float(np.nanmax(np.abs(x)))                                                     # noqa: E731
    amp = lambda x: float((np.nanmax(x) - np.nanmin(x)) / 2)                                        # noqa: E731
    # ---- 校核（材料：送布连杆 ADC12 压铸铝 σ0.2 150、疲劳极限取 60；其余 45 钢调质 σs 355、σ−1 270、τ−1 155；缺口 Kf 2）
    out = {}
    Fr_max = float(np.nanmax(np.abs(F_rod)))
    A_r, I_r, L_r = 8.0 * 8.0, 8.0 ** 4 / 12, float(np.mean(np.linalg.norm(mm("P") - mm("E"), axis=1))) * 1000
    out["feed_rod"] = dict(F_max_N=round(Fr_max, 1), sigma_MPa=round(Fr_max / A_r, 2), L_mm=round(L_r, 1),
                           P_euler_N=round(math.pi ** 2 * 71000 * I_r / L_r ** 2, 0),
                           SF_buckling=round(math.pi ** 2 * 71000 * I_r / L_r ** 2 / Fr_max, 1),
                           SF_fatigue=round(60 / (2 * amp(np.nan_to_num(F_rod)) / A_r), 1),
                           big_end_pv=round(Fr_max / (22 * 8) * w * 0.011, 2))
    L2 = float(np.mean(np.linalg.norm(C - Pp, axis=1))) * 1000
    out["feed_link"] = dict(F_max_N=round(mx(F_L2), 1), sigma_MPa=round(mx(F_L2) / 48, 2),
                            SF_buckling=round(math.pi ** 2 * 206000 * (8 * 6 ** 3 / 12) / L2 ** 2 / mx(F_L2), 0))
    d_ = 10.0
    tau = lambda Tq: 16 * Tq * 1000 / (math.pi * d_ ** 3)                                           # noqa: E731
    Jp = math.pi * d_ ** 4 / 32
    tw = mx(T_rock) * 1000 * (316 - 30) / (79000 * Jp)
    out["feed_rock_shaft"] = dict(T_max_Nm=round(mx(T_rock), 4), tau_MPa=round(tau(mx(T_rock)), 2),
                                  SF_static=round(0.577 * 355 / tau(mx(T_rock)), 1), SF_fatigue=round(155 / (2 * tau(amp(T_rock))), 1),
                                  twist_rad=round(tw, 6), dog_y_error_mm=round(tw * g["ra"], 4),
                                  bush_pv=round(mx(F_L2) / (d_ * 13) * float(np.max(np.abs(np.gradient(np.unwrap(FP["beta"]), dphi)))) * w * 0.005, 3))
    out["lift_rock_shaft"] = dict(T_max_Nm=round(mx(T_lift), 4), tau_MPa=round(tau(mx(T_lift)), 2),
                                  SF_fatigue=round(155 / (2 * tau(amp(T_lift))), 1),
                                  bush_pv=round(mx(F_L3) / (d_ * 10) * float(np.max(np.abs(np.gradient(np.unwrap(FP["gam"]), dphi)))) * w * 0.005, 3))
    out["lift_link"] = dict(F_max_N=round(mx(F_L3), 1), sigma_MPa=round(mx(F_L3) / (7 * 8), 2))
    # 牙架弯矩：沿牙架的点力 F_A（T）、F_K（K）、布力（牙）、惯性（质心），在牙架坐标里求各截面的弯矩
    yb = np.linspace(0, 1, 41)
    Mmax_thin, Mmax_blk = 0.0, 0.0
    for i in range(len(T)):
        u = (T[i] - K[i]) / np.linalg.norm(T[i] - K[i])
        nrm = np.array([-u[1], u[0]])
        Lb = np.linalg.norm(T[i] - K[i])
        loads = [(0.0, float(F_K[i] @ nrm)), (Lb, float(F_A[i] @ nrm)), (float((dog[i] - K[i]) @ u), float(Fc[i] @ nrm)),
                 (float((b["com"][i] - K[i]) @ u), -float(ma[i] @ nrm))]
        s_dog = float((dog[i] - K[i]) @ u)
        for t in yb:
            sx = t * Lb
            M = sum(P * (sx - xp) for xp, P in loads if xp < sx)
            if abs(sx - s_dog) < 0.0143:
                Mmax_blk = max(Mmax_blk, abs(M))
            else:
                Mmax_thin = max(Mmax_thin, abs(M))
    hb = 3.9
    W_thin = hb * 5.0 ** 2 / 6
    zt = float(dog[0, 1]) * 1000
    h_blk = (zt - 4.3) - (float(T[0, 1]) * 1000 - 2.5) - 1.5
    W_blk = hb * h_blk ** 2 / 6
    out["feed_bar"] = dict(F_K_max_N=round(mx(F_Kz), 1), F_A_max_N=round(float(np.max(np.linalg.norm(F_A, axis=1))), 1),
                           M_thin_Nmm=round(Mmax_thin * 1000, 1), sigma_thin_MPa=round(Mmax_thin * 1000 / W_thin, 1),
                           h_block_mm=round(h_blk, 2), sigma_block_MPa=round(Mmax_blk * 1000 / W_blk, 1),
                           SF_fatigue=round(270 / (2 * max(Mmax_thin * 1000 / W_thin, Mmax_blk * 1000 / W_blk)), 1))
    pins = dict(P=(5.9, Fr_max), C=(5.9, mx(F_L2)), T=(4.9, float(np.max(np.linalg.norm(F_A, axis=1)))), K=(4.9, mx(F_Kz)))
    out["pins_tau_MPa"] = {k: round(F / (math.pi * dd ** 2 / 4), 2) for k, (dd, F) in pins.items()}
    return out


def main():
    mdir = Path(sys.argv[1])
    out = ROOT / "docs" / "设计" / "WQ-LS" / "G4"
    allr = {}
    for st in ("s5", "r5", "s3"):
        r = run(mdir, st)
        allr[st] = r
        print(st, json.dumps(r["summary"], ensure_ascii=False))
        print(st, "强度", json.dumps(r["strength"], ensure_ascii=False))
    (out / "送布动力.json").write_text(json.dumps(allr, ensure_ascii=False))


if __name__ == "__main__":
    main()
