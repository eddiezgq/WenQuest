"""第 138 轮 G8.0：刺布机构的计算（针杆导套、滑块与导轨、连杆大头滚针轴承）→ docs/设计/WQ-LS/G8/刺布机构计算.json

    python3 tools/wqls/g8_needlebar.py

曲柄滑块（偏置 0）：r、l、往复质量 mr 取 spec.SEW；5000 r/min。针杆轴向力 = 往复惯性力 + 重力（刺布阻力只有几牛，不计）。
连杆斜角 β 产生的侧向力 F·tanβ：没有滑块时由两个针杆导套承受；有滑块时由滑块和导轨承受。
滚针轴承 HK0810（INA：C = 3800 N，C0 = 3950 N，油润滑极限 29500 r/min，RS 137-1724 的数据）：
  当量载荷取一转内曲柄销力的立方平均，相对转速取主轴转速，L10h = (C/P)^(10/3) × 10^6 /(60 n)。
许用 pv：烧结含油青铜 1.8 MPa·m/s（G4.6 同一取值）。
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import spec as S  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "设计" / "WQ-LS" / "G8" / "刺布机构计算.json"
N = S.PERF["speed"]
R, L, M = S.SEW["r"] / 1000, S.SEW["l"] / 1000, S.SEW["mr"]
D_BAR = 8.0                     # 针杆直径 mm（现值）
L_BUSH = (12.0, 20.0)           # 上、下导套长 mm（现值，G4.1）
M_ROD_ROT = 0.010               # 连杆大头折算的旋转质量 kg（估计，G4 零件质量表待细化后替换）
C_HK0810, C0_HK0810, NLIM_OIL = 3800.0, 3950.0, 29500.0
# 比较用：曲柄销加粗到 Ø10 时的 HK1012（INA：C = 5500 N，C0 = 6800 N，油润滑 24300 r/min，RS 137-1728）
BEARINGS = {"HK0810（销 Ø8，现值）": (3800.0, 3950.0), "HK1012（销 Ø10）": (5500.0, 6800.0)}
PV_SINTER = 1.8                 # MPa·m/s


def main():
    w = N * 2 * math.pi / 60
    lam = R / L
    rows = []
    for k in range(720):
        th = k * math.pi / 360
        s_b = lam * math.sin(th)
        beta = math.asin(s_b)
        # 针杆位移（从上止点向下为正）x = r(1 − cosθ) + l(1 − cosβ)，加速度用精确式数值差分
        rows.append((th, R * (1 - math.cos(th)) + L * (1 - math.cos(beta)), beta))
    dt = (math.pi / 360) / w
    out = []
    for i, (th, x, beta) in enumerate(rows):
        xp, xn = rows[i - 1][1], rows[(i + 1) % len(rows)][1]
        acc = (xn - 2 * x + xp) / dt ** 2
        v = (xn - xp) / (2 * dt)
        f_ax = M * acc - M * 9.81 * 0               # 方向：向下为正；重力相对惯性力 < 0.2 %，不计
        f_side = abs(f_ax * math.tan(beta))
        f_pin = math.hypot(abs(f_ax) / max(math.cos(beta), 1e-9), M_ROD_ROT * R * w * w)
        out.append(dict(th=math.degrees(th), v=v, f_ax=f_ax, f_side=f_side, f_pin=f_pin))
    f_ax_max = max(abs(o["f_ax"]) for o in out)
    side_max = max(o["f_side"] for o in out)
    side_mean = sum(o["f_side"] for o in out) / len(out)
    v_mean = sum(abs(o["v"]) for o in out) / len(out)
    v_max = max(abs(o["v"]) for o in out)
    # 没有滑块：侧向力全由导套承担（按两导套平均分担，偏乐观）
    a_bush = D_BAR * sum(L_BUSH)                     # mm²（投影面积）
    p_bush = side_mean / a_bush
    pv_bush = p_bush * v_mean
    # 有滑块：需要的接触面积（pv ≤ 许用）
    a_need = side_mean * v_mean / PV_SINTER
    # 滚针轴承
    p_eq = (sum(o["f_pin"] ** 3 for o in out) / len(out)) ** (1 / 3)
    l10h = (C_HK0810 / p_eq) ** (10 / 3) * 1e6 / (60 * N)
    res = dict(
        input=dict(n_rpm=N, r_mm=R * 1000, l_mm=L * 1000, lambda_=round(lam, 3), m_recip_kg=M, d_bar_mm=D_BAR,
                   l_bush_mm=L_BUSH, m_rod_rot_kg=M_ROD_ROT, hk0810=dict(C=C_HK0810, C0=C0_HK0810, n_oil=NLIM_OIL)),
        needle_bar=dict(f_axial_max_N=round(f_ax_max, 1), beta_max_deg=round(math.degrees(math.asin(lam)), 2),
                        side_max_N=round(side_max, 1), side_mean_N=round(side_mean, 1),
                        v_mean_m_s=round(v_mean, 2), v_max_m_s=round(v_max, 2)),
        bushes_without_slide=dict(area_mm2=a_bush, p_MPa=round(p_bush, 3), pv=round(pv_bush, 2),
                                  limit_pv=PV_SINTER, ok=pv_bush <= PV_SINTER),
        slide_block=dict(area_needed_mm2=round(a_need, 1),
                         note="滑块与导轨接触面积要不小于这个值（按烧结含油材料 pv 1.8 算；有油芯供油时可取更大许用值）"),
        rod_bearing_HK0810=dict(P_eq_N=round(p_eq, 1), P_max_N=round(max(o["f_pin"] for o in out), 1),
                               static_safety=round(C0_HK0810 / max(o["f_pin"] for o in out), 2),
                               L10h=round(l10h)),
        rod_bearing_compare={k: dict(L10h=round((c / p_eq) ** (10 / 3) * 1e6 / (60 * N)),
                                     static_safety=round(c0 / max(o["f_pin"] for o in out), 2))
                             for k, (c, c0) in BEARINGS.items()},
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
