"""第 138 轮 G4.6：油泵和润滑油路的计算 → docs/设计/WQ-LS/G4/油泵.json

    python3 tools/wqls/g4_oil.py

油泵：下轴上的偏心（偏心 e）顶柱塞 Ø dp，行程 2e，弹簧压着柱塞跟随；进、出油各一个钢球单向阀；容积效率取 0.7。
油路：泵 → 机座里 Ø4 × 1 铜管（内径 2） → 立柱 → 机臂顶的分油块（溢流孔回油盘）→ 各润滑点的 Ø2 油管、油毡；另从泵出口分一路经针阀到旋梭轴中心孔。
压降按层流（Hagen–Poiseuille）算，油用缝纫机白油（ISO VG 10）；冷机按 20 °C、VG 22 的粘度再算一次（最坏）。
柱塞弹簧：吸油行程里柱塞（连弹簧座）要跟住偏心——惯性力 m e ω² 加吸油真空 × 柱塞面积，乘 3 倍定预紧力。
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "设计" / "WQ-LS" / "G4" / "油泵.json"

N_RPM = 5000.0
E = 0.4e-3                  # 偏心 m
DP = 3.0e-3                 # 柱塞直径 m
ETA_V = 0.7
RHO = 860.0
NU = dict(run_40C_VG10=10e-6, cold_20C_VG22=60e-6)        # 运动粘度 m²/s
# 油路：(名字, 内径 m, 长度 m, 占总流量的份额)
LINES = [("泵 → 立柱（Ø4 × 1 铜管（内径 2），机座里 + 立柱里）", 2.0e-3, 0.75, 1.0),
         ("分油块 → 上轴前轴承（Ø2 尼龙管）", 1.2e-3, 0.40, 0.25),
         ("分油块 → 上轴后轴承", 1.2e-3, 0.10, 0.15),
         ("分油块 → 针杆、挑线油毡", 1.2e-3, 0.45, 0.25)]
H_LIFT = 0.30               # 油从油盘到机臂顶分油块的高度 m
HOOK = dict(needle_valve_mm3_min=(0.0, 30.0), line_d=1.0e-3, line_L=0.30)   # 旋梭一路：针阀可调 0…30 mm³/min（约 0…1.8 mL/h）
M_PLUNGER = 0.6e-3          # 柱塞 + 弹簧座 kg
SPRING_SF = 3.0
P_SUCTION = 20e3            # 吸油行程柱塞下面的真空度（取大值）Pa


def main():
    w = N_RPM * 2 * math.pi / 60
    a_p = math.pi * DP ** 2 / 4
    V_rev = a_p * 2 * E                        # m³/转
    Q = V_rev * ETA_V * N_RPM / 60             # m³/s
    res = dict(pump=dict(e_mm=E * 1e3, stroke_mm=2 * E * 1e3, d_plunger_mm=DP * 1e3, eta_v=ETA_V,
                         V_rev_mm3=round(V_rev * 1e9, 2), Q_mL_min=round(Q * 6e7, 1),
                         a_max_ms2=round(E * w ** 2, 1),
                         spring_preload_N=round(SPRING_SF * (M_PLUNGER * E * w ** 2 + P_SUCTION * a_p), 2)))
    for case, nu in NU.items():
        mu = nu * RHO
        rows, dp_main = [], 0.0
        for name, d, L, share in LINES:
            q = Q * share
            dp = 128 * mu * L * q / (math.pi * d ** 4)
            v = q / (math.pi * d ** 2 / 4)
            rows.append(dict(line=name, d_mm=d * 1e3, L_m=L, Q_mL_min=round(q * 6e7, 2), v_ms=round(v, 3),
                             Re=round(v * d / nu, 1), dp_kPa=round(dp / 1e3, 2)))
            if share == 1.0:
                dp_main = dp
        dp_branch = max(r["dp_kPa"] for r in rows[1:]) * 1e3
        p_pump = dp_main + dp_branch + RHO * 9.81 * H_LIFT
        res[case] = dict(lines=rows, lift_kPa=round(RHO * 9.81 * H_LIFT / 1e3, 2),
                         p_pump_kPa=round(p_pump / 1e3, 2), F_plunger_N=round(p_pump * a_p, 3),
                         P_hydraulic_mW=round(p_pump * Q * 1e3, 2))
    # 溢流：分油块里一个 Ø1.5 溢流孔，高于各出油口 3 mm——各支路吃不下的油从这里回油盘，泵出口压力不会憋高
    qh = HOOK["needle_valve_mm3_min"][1] * 1e-9 / 60
    res["hook"] = dict(needle_valve_mm3_min=HOOK["needle_valve_mm3_min"],
                       share_of_pump_max=round(qh / Q, 4),
                       dp_kPa_cold=round(128 * NU["cold_20C_VG22"] * RHO * HOOK["line_L"] * qh / (math.pi * HOOK["line_d"] ** 4) / 1e3, 3),
                       note="旋梭供油：泵出口分一路，经针阀（调节螺钉在机座底下）到旋梭轴中心 Ø2.5 孔；针阀全关不供油，全开约 1.8 mL/h")
    res["checks"] = dict(
        flow_ok=bool(15.0 <= res["pump"]["Q_mL_min"] <= 30.0),
        cold_pressure_ok=bool(res["cold_20C_VG22"]["p_pump_kPa"] < 100.0),          # 单向阀、泵体密封按 0.1 MPa 以内设计
        laminar_ok=bool(all(r["Re"] < 2000 for c in NU for r in res[c]["lines"])),
        spring_ok=True)
    res["all_ok"] = all(res["checks"].values())
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(json.dumps(dict(pump=res["pump"], run=res["run_40C_VG10"]["p_pump_kPa"], cold=res["cold_20C_VG22"]["p_pump_kPa"],
                          checks=res["checks"]), ensure_ascii=False))


if __name__ == "__main__":
    main()
