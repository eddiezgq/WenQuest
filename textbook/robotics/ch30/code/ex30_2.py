"""30.2 节的计算：构型选择。

(1) 算例 30.2.1：工具竖直朝下时，偏置腕（WQ-CR5、UR5e 的构型）与球形腕（同样的肩高、大臂、小臂、法兰距）在手臂平面里
    能到达的区域：r–z 平面上 1 mm 网格数格子；偏置腕在 J1 轴周围有一个半径 d4 的圆柱够不着，手腕翻转（朝外 / 朝里）又补回一块。
(2) 算例 30.2.2：SCARA（零件库 B-SCA-WQ4 的默认参数）能不能做部件装配工位：竖直行程与工位各点的高差。
(3) 算例 30.2.3：四种构型的评分表（权重与打分是设计者的判断，列出来是为了让判断可以讨论）。
(4) 七轴、偏置腕、球形腕各有几个关节模组的“型号”，自重与负载比（零件库的厂商参数）。
"""
import math

import numpy as np

from _ch30 import STATION, APPROACH, cr_dh, library_arms, wqcr5
from bookout import out

W = wqcr5()
dh = cr_dh()
a2, a3 = abs(dh[1]["a"]), abs(dh[2]["a"])
d1, d4, d5, d6 = dh[0]["d"], dh[3]["d"], dh[4]["d"], dh[5]["d"]
TOOL = 0.15


def reach_offset(r, z):
    if r < d4:
        return False
    rp = math.sqrt(r * r - d4 * d4)
    h = z + TOOL + d6 - d1
    return any(abs(a2 - a3) <= math.hypot(x, h) <= a2 + a3 for x in (rp - d5, rp + d5))


def reach_spherical(r, z):
    """球形腕：腕心在 TCP 正上方 d6 + 工具处，腕心到 J2 的距离在 [|a2 − a3|, a2 + a3]（这里小臂长取 a3 + d5，使臂展相同）"""
    a3s = a3 + d5
    h = z + TOOL + d6 - d1
    return abs(a2 - a3s) <= math.hypot(r, h) <= a2 + a3s


step = 0.002
rs = np.arange(step / 2, 1.0, step)
zs = np.arange(-0.8 + step / 2, 1.0, step)
A_off = sum(reach_offset(r, z) for r in rs for z in zs) * step * step
A_sph = sum(reach_spherical(r, z) for r in rs for z in zs) * step * step
r_hole = min(r for r in rs if any(reach_offset(r, z) for z in zs)) - step / 2      # 离 J1 轴最近能到的地方
r_hole_s = min(r for r in rs if any(reach_spherical(r, z) for z in zs)) - step / 2
assert abs(r_hole - d4) < 2 * step and r_hole_s < step and A_off < A_sph
# 只用一种手腕（朝外）
A_out = sum((r >= d4 and abs(a2 - a3) <= math.hypot(math.sqrt(r * r - d4 * d4) - d5, z + TOOL + d6 - d1) <= a2 + a3)
            for r in rs for z in zs) * step * step
out(a2=a2, a3=a3, d1=d1, d4=d4, d5=d5, d6=d6, A_off=A_off, A_sph=A_sph, A_ratio=A_off / A_sph * 100, r_hole_mm=r_hole * 1000,
    A_out=A_out, r_hole_s=r_hole_s * 1000, flip_gain=(A_off - A_out) / A_out * 100)

# ---------------------------------------------------------------- (2) SCARA
import yaml                                                    # noqa: E402
from _ch30 import ROOT                                         # noqa: E402
sc = yaml.safe_load((ROOT / "library" / "catalog" / "B" / "B-SCA-WQ4" / "entry.yaml").read_text(encoding="utf-8"))["defaults"]
z_lo = min(z for *_, z in STATION)
z_hi = max(z for *_, z in STATION) + APPROACH
span = z_hi - z_lo
sc_reach = sc["arm1_m"] + sc["arm2_m"]
r_far = max(r for *_, r, z in STATION)
assert span > 3 * sc["stroke_m"] and r_far > sc_reach
out(sc_stroke=sc["stroke_m"], sc_reach=sc_reach, z_span=span, r_far=r_far, sc_arm1=sc["arm1_m"], sc_arm2=sc["arm2_m"])

# ---------------------------------------------------------------- (3) 评分表
CRIT = [("与人同场（外形光滑、没有夹手的缝、功率与力限制）", 0.25), ("模组化（关节都是同一类模组）", 0.20),
        ("工作空间（工位的高差、桌面下的料箱）", 0.20), ("逆解与编程（闭式逆解、示教方便）", 0.15),
        ("成本（关节数、专用零件）", 0.10), ("刚度与精度", 0.10)]
SCORE = {"偏置腕六轴": [5, 5, 4, 4, 4, 3], "球形腕六轴": [3, 2, 5, 5, 4, 4], "七轴": [5, 4, 4, 2, 2, 3], "SCARA": [2, 3, 1, 5, 5, 5]}
w = np.array([c[1] for c in CRIT])
assert abs(w.sum() - 1) < 1e-12
total = {k: float(np.dot(w, v)) for k, v in SCORE.items()}
best = max(total, key=total.get)
assert best == "偏置腕六轴"
out(**{f"w{i + 1}": int(round(c[1] * 100)) for i, c in enumerate(CRIT)},
    s_off=total["偏置腕六轴"], s_sph=total["球形腕六轴"], s_7=total["七轴"], s_sc=total["SCARA"])

# ---------------------------------------------------------------- (4) 自重与负载比
arms = {a["id"]: a for a in library_arms()}
fr3, ir, kr = arms["B-ARM-FR3"], arms["B-ARM-IRB1200"], arms["B-ARM-LRMATE200ID7L"]
out(fr3_p=fr3["payload_kg"], fr3_w=fr3["weight_kg"], fr3_r=fr3["reach_mm"], ir_p=ir["payload_kg"], ir_w=ir["weight_kg"], ir_r=ir["reach_mm"],
    lr_p=kr["payload_kg"], lr_w=kr["weight_kg"], lr_r=kr["reach_mm"], fr3_ratio=fr3["payload_kg"] / fr3["weight_kg"],
    ir_ratio=ir["payload_kg"] / ir["weight_kg"])
