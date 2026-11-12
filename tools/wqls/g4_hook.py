"""第 138 轮 G4.5：旋梭组的计算（齿轮、下轴、轴承、旋梭轴轴套、同步带）。

    python3 tools/wqls/g4_hook.py [<零件目录（cad/mech.py 的输出，读 parts.json 里的质量和转动惯量）>]

输出 docs/设计/WQ-LS/G4/旋梭组计算.json。
载荷工况：
  稳态：5000 r/min 缝纫，旋梭摩擦 0.02 N·m（G2 计算书）；
  峰值：上轴角加速度取两项之和（偏保守）：
    ① 电机用峰值力矩 3 N·m 急停（G2 选型），总惯量 5.2×10⁻⁴ kg·m²（转子加手轮 4×10⁻⁴ 的那一档）→ 约 5 800 rad/s²，0.09 s 停下；
    ② 一转之内的转速波动（G2：5000 r/min 时 ±1.37%，每转两次）→ Δω·2πf 约 7 500 rad/s²。
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital")]
import spec as S  # noqa: E402
from cae import gears as GR  # noqa: E402

OUT = ROOT / "docs" / "设计" / "WQ-LS" / "G4"
N = S.SEW["n"]                       # 5000 r/min
W = N * 2 * math.pi / 60
G2 = json.loads((ROOT / "docs" / "设计" / "WQ-LS" / "G2" / "结果.json").read_text())["motor"]
_row = min(G2["rows"], key=lambda r: abs(r["J_rotor"] - 4e-4))
T_MOTOR_PEAK = 3.0                   # N·m（G2：峰值力矩 ≥ 3）
ALPHA_STOP = T_MOTOR_PEAK / _row["J_total"]                              # ① 急停
ALPHA_RIPPLE = (_row["ripple_pct"] / 100 / 2) * W * (2 * 2 * math.pi * N / 60)   # ② 转速波动（幅值 = 峰峰值的一半，频率 2 倍转频）
ALPHA_PEAK = ALPHA_STOP + ALPHA_RIPPLE
T_FRIC_HOOK = 0.02                   # N·m（旋梭轴上）
# G4.6 核过：抬牙链 5 mm 针距时下轴力矩最大 0.053 N·m（G4/送布动力.json T_low_max），油泵冷机 73 kPa × 柱塞面积 × 偏心 0.4 ≈ 0.0002 N·m
_FD = ROOT / "docs" / "设计" / "WQ-LS" / "G4" / "送布动力.json"
_FDJ = __import__("json").loads(_FD.read_text()) if _FD.exists() else None
T_PUMP_LIFT = max(0.05, (_FDJ["s5"]["summary"]["T_low_max"] + 0.001) if _FDJ else 0.05)   # N·m（下轴上：油泵、抬牙偏心）
F_LIFT_LINK = _FDJ["s5"]["strength"]["lift_link"]["F_max_N"] if _FDJ and "strength" in _FDJ["s5"] else 0.0   # 抬牙连杆力，加在抬牙偏心 x 112
BRG_6201 = S.BRG_6201
BELT_ALLOW_N = 300.0                 # HTD 3M 宽 15 的许用拉力（MiSUMi 经济型目录：6 mm 136 N、15 mm 309 N），取 300
BELT_T0 = 20.0                       # 安装张力（每边）N
BRONZE = dict(p=15.0, v=10.0, pv=15.0)   # ZCuSn10P1 加油润滑的许用值（机械设计手册通行取值）


def masses(d: Path | None):
    """零件质量与转动惯量；没有零件目录时用 cad/hook.py 试算时的值"""
    est = dict(m=dict(hook=0.0466, hook_shaft=0.0461, gear_hook=0.0216, gear_lower=0.0863, pulley_lower=0.055, lower_shaft=0.279,
                      pulley_upper=0.0431),
               J=dict(hook=4.5e-6, lower=2.6e-5, upper=4e-6))
    if d and (d / "parts.json").exists():
        info = json.loads((d / "parts.json").read_text())
        est["m"].update({k: v["mass_kg"] for k, v in info["parts"].items() if k in est["m"]})
        J = info["balance"].get("J_hook_train_kgm2")
        if J:
            est["J"] = J
    return est


def shaft_critical(L_pos, d, supports, masses_at, E=206e3, rho=7.85e-6, n_el=120):
    """欧拉梁有限元（每节点挠度、转角），刚性简支，加集中质量；返回一阶临界转速 r/min"""
    x0, x1 = L_pos
    xs = np.linspace(x0, x1, n_el + 1)
    for xp in list(supports) + [x for x, _ in masses_at]:
        xs = np.append(xs, xp)
    xs = np.unique(np.round(xs, 6))
    n = len(xs)
    K = np.zeros((2 * n, 2 * n))
    M = np.zeros((2 * n, 2 * n))
    I = math.pi * d ** 4 / 64
    A = math.pi * d ** 2 / 4
    for e in range(n - 1):
        h = xs[e + 1] - xs[e]
        k = E * I / h ** 3 * np.array([[12, 6 * h, -12, 6 * h], [6 * h, 4 * h * h, -6 * h, 2 * h * h],
                                       [-12, -6 * h, 12, -6 * h], [6 * h, 2 * h * h, -6 * h, 4 * h * h]])
        m = rho * A * h / 420 * np.array([[156, 22 * h, 54, -13 * h], [22 * h, 4 * h * h, 13 * h, -3 * h * h],
                                          [54, 13 * h, 156, -22 * h], [-13 * h, -3 * h * h, -22 * h, 4 * h * h]])
        idx = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        K[np.ix_(idx, idx)] += k
        M[np.ix_(idx, idx)] += m
    for x, mk in masses_at:
        i = int(np.argmin(abs(xs - x)))
        M[2 * i, 2 * i] += mk                       # kg
    fixed = [2 * int(np.argmin(abs(xs - x))) for x in supports]
    free = [i for i in range(2 * n) if i not in fixed]
    Kf, Mf = K[np.ix_(free, free)], M[np.ix_(free, free)]
    # K: N/mm，M: kg → ω² = K/M 的单位 N/(mm·kg) = 1000 /s²
    lam = np.linalg.eigvals(np.linalg.solve(Mf, Kf))
    w1 = math.sqrt(min(lam.real[lam.real > 1e-9]) * 1000)
    return w1 * 60 / (2 * math.pi)


def main():
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    ms = masses(d)
    J = ms["J"]
    g = GR.geometry(S.GEAR["mn"], S.GEAR["z_hook"], S.GEAR["z_lower"], S.GEAR["beta"], b=S.GEAR["b"])
    # 力矩（旋梭轴、下轴）
    a_hook = 2 * ALPHA_PEAK
    T_hook_peak = J["hook"] * a_hook + T_FRIC_HOOK
    T_low_steady = 2 * T_FRIC_HOOK + T_PUMP_LIFT
    T_low_peak = 2 * T_hook_peak + J["lower"] * ALPHA_PEAK + T_PUMP_LIFT
    # 齿轮：小齿轮（z 20）在旋梭轴上，10 000 r/min；使用系数 1.5（伺服急起急停），20 000 h
    gear = GR.check(T_hook_peak, 2 * N, g, "20CrMnTi-carburized", KA=1.5, Kv=1.2, Ka=1.1, Kb=1.1, hours=20000, SHmin=1.2, SFmin=1.5)
    gear_steady = GR.check(T_FRIC_HOOK, 2 * N, g, "20CrMnTi-carburized", KA=1.0, Kv=1.2, Ka=1.1, Kb=1.1, hours=20000)
    Ft_peak = 2 * T_hook_peak * 1000 / g["d1"]
    at = math.radians(g["alpha_t"])
    Fr_peak, Fa_peak = Ft_peak * math.tan(at), Ft_peak * math.tan(math.radians(S.GEAR["beta"]))
    # 同步带
    r_p = S.BELT["z"] * S.BELT["pitch"] / math.pi / 2
    Fe_peak = T_low_peak * 1000 / r_p
    Fe_steady = T_low_steady * 1000 / r_p
    belt = dict(type=f"{S.BELT['profile']} {S.BELT['teeth'] * 3}-3M-{int(S.BELT['width'])}（{S.BELT['teeth']} 齿）", center_mm=S.C_BELT,
                pulley_z=S.BELT["z"], pd_mm=round(2 * r_p, 2), v_ms=round(W * r_p / 1000, 2),
                Fe_steady_N=round(Fe_steady, 1), Fe_peak_N=round(Fe_peak, 1), T0_each_side_N=BELT_T0,
                tight_side_peak_N=round(BELT_T0 + Fe_peak / 2 + Fe_peak / 2, 1), allow_N=BELT_ALLOW_N,
                margin=round(BELT_ALLOW_N / (BELT_T0 + Fe_peak), 2),
                note="中心距固定：带长 2C + 3z = 570 正好是节距 3 的整数倍（190 齿），不用张紧轮；安装张力靠带长公差和中心距公差保证")
    # 下轴：两个 6201（x 97、371），带轮 x 352（带的合力约 2T0 + Fe，方向沿两轮连线），齿轮 x 76（悬伸）
    xb1, xb2 = 97.0, 371.0
    F_belt = 2 * BELT_T0 + Fe_steady                      # 稳态
    F_gear = math.hypot(2 * T_low_steady * 1000 / g["d2"], 2 * T_low_steady * 1000 / g["d2"] * math.tan(at))
    # 静力：两支点简支，带轮力在 352、齿轮力在 76
    xp, xg = S.X_BELT, 76.0
    R2 = (F_belt * (xp - xb1) - F_gear * (xb1 - xg)) / (xb2 - xb1)
    R1 = F_belt + F_gear - R2
    # G4.6：抬牙偏心（x 112）上的抬牙连杆力，方向不定，两个支反力按同号叠加（偏保守）
    x_le = 112.0
    R1 = abs(R1) + F_LIFT_LINK * (xb2 - x_le) / (xb2 - xb1)
    R2 = abs(R2) + F_LIFT_LINK * (x_le - xb1) / (xb2 - xb1)
    life = {}
    for name, R in (("左 6201", abs(R1)), ("右 6201", abs(R2))):
        P = max(R, 10.0)
        L10 = (BRG_6201["C"] / P) ** 3 * 1e6 / (60 * N)
        life[name] = dict(P_N=round(P, 1), L10h=round(L10))
    M_max = max(abs(R2) * (xb2 - xp), F_gear * (xb1 - xg))     # N·mm
    sig_b = 32 * M_max / (math.pi * 12 ** 3)
    tau = 16 * T_low_peak * 1000 / (math.pi * 12 ** 3)
    S_fat = 280.0 / math.sqrt((sig_b * 1.8) ** 2 + 3 * (tau * 1.5) ** 2)   # 45 钢调质 σ-1 ≈ 280 MPa，Kσ 1.8、Kτ 1.5（卡簧槽）
    n_crit = shaft_critical((70.0, 384.0), 12.0, (xb1, xb2), [(76.0, ms["m"]["gear_lower"]), (S.X_BELT, ms["m"]["pulley_lower"])])
    # 旋梭轴：两个铜套（x 32–46、50–64，内径 10；G4.6 左套由 26 右移到 32，cad/hook.py X_BUSH），齿轮在 76（悬伸），旋梭在 x 12 附近（悬伸）
    xa, xb = 39.0, 57.0
    Fg = math.hypot(Ft_peak, Fr_peak)
    F_hook = ms["m"]["hook"] * 9.81 + 5.0                  # 旋梭自重 + 线环拉力（几牛）
    Rb = (Fg * (76.0 - xa) + F_hook * (xa - 12.0)) / (xb - xa)
    Ra = Rb - Fg + F_hook
    p_max = max(abs(Ra), abs(Rb)) / (10.0 * 14.0)
    v = math.pi * 10.0 * 2 * N / 60000
    bush = dict(Ra_N=round(Ra, 1), Rb_N=round(Rb, 1), p_MPa=round(p_max, 3), v_ms=round(v, 2), pv=round(p_max * v, 2), allow=BRONZE,
                ok=p_max <= BRONZE["p"] and v <= BRONZE["v"] and p_max * v <= BRONZE["pv"])
    res = dict(
        loads=dict(n_rpm=N, alpha_stop_rad_s2=round(ALPHA_STOP), alpha_ripple_rad_s2=round(ALPHA_RIPPLE), alpha_peak_rad_s2=round(ALPHA_PEAK), J_kgm2=J, T_hook_peak_Nm=round(T_hook_peak, 4),
                   T_low_steady_Nm=round(T_low_steady, 3), T_low_peak_Nm=round(T_low_peak, 3)),
        layout=dict(ZL=round(S.ZL, 3), YL=round(S.YL, 3), a_gear=round(S.A_GEAR, 3), C_belt=S.C_BELT),
        gear=dict(geom={k: (round(v, 4) if isinstance(v, float) else v) for k, v in g.items()},
                  peak={k: (round(v, 3) if isinstance(v, float) else v) for k, v in gear.items()},
                  steady=dict(sigma_H=round(gear_steady["sigma_H"], 1), SH=round(gear_steady["SH"], 1), SF=round(gear_steady["SF"], 1)),
                  Ft_peak_N=round(Ft_peak, 1), Fr_peak_N=round(Fr_peak, 1), Fa_peak_N=round(Fa_peak, 1),
                  material="20CrMnTi 渗碳淬火 58–62 HRC，磨齿 6 级", hands="下轴齿轮右旋、旋梭轴齿轮左旋"),
        belt=belt,
        lower_shaft=dict(d_mm=12, span_mm=xb2 - xb1, R_N=[round(R1, 1), round(R2, 1)], bearing_life=life,
                         sigma_b_MPa=round(sig_b, 2), tau_peak_MPa=round(tau, 2), S_fatigue=round(S_fat, 1),
                         n_crit_rpm=round(n_crit), ratio_to_max=round(n_crit / N, 2)),
        hook_shaft=dict(bushes=bush, n_rpm=2 * N, hook_tip_speed_ms=round(2 * W * 13.5e-3, 1)),
    )
    res["checks"] = {
        "齿轮接触安全系数 ≥ 1.2": (round(gear["SH"], 2), gear["SH"] >= 1.2),
        "齿轮弯曲安全系数 ≥ 1.5": (round(gear["SF"], 2), gear["SF"] >= 1.5),
        "下轴临界转速 ≥ 2 × 5000": (round(n_crit), n_crit >= 2 * N),
        "下轴疲劳安全系数 ≥ 2": (round(S_fat, 1), S_fat >= 2),
        "6201 寿命 ≥ 20 000 h": (min(v["L10h"] for v in life.values()), min(v["L10h"] for v in life.values()) >= 20000),
        "旋梭轴轴套 p、v、pv 在许用内": (bush["pv"], bush["ok"]),
        "同步带余量 ≥ 3": (belt["margin"], belt["margin"] >= 3),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "旋梭组计算.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))
    for k, (v, ok) in res["checks"].items():
        print(("OK  " if ok else "NG  ") + k, v)
    print("T_hook_peak", res["loads"]["T_hook_peak_Nm"], "T_low_peak", res["loads"]["T_low_peak_Nm"], "gear sH", round(gear["sigma_H"]), "sF", round(gear["sigma_F1"]))


if __name__ == "__main__":
    main()
