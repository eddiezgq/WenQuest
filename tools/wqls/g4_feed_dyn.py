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
    T_parts, F_in = {}, np.zeros((N, 2))
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
    res = dict(setting=setting, n_rpm=n_rpm, phi=phi.tolist(),
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


def main():
    mdir = Path(sys.argv[1])
    out = ROOT / "docs" / "设计" / "WQ-LS" / "G4"
    allr = {}
    for st in ("s5", "r5", "s3"):
        r = run(mdir, st)
        allr[st] = r
        print(st, json.dumps(r["summary"], ensure_ascii=False))
    (out / "送布动力.json").write_text(json.dumps(allr, ensure_ascii=False))


if __name__ == "__main__":
    main()
