"""4.3 节：单侧极限、无穷远处的极限与渐近线——2^(1/x) 在 0 两侧；有理函数的斜渐近线；
两节连杆手臂接近伸直时，肘关节角对腕心距离的“灵敏度”无限增大（铅直渐近线）。"""
import json
import math
from pathlib import Path

import numpy as np

from bookout import out

# 2^(1/x)：x → 0⁺ 时 → +∞，x → 0⁻ 时 → 0
out(p_plus=2 ** (1 / 0.1), p_minus=2 ** (1 / -0.1), p_minus2=2 ** (1 / -0.01))

# 斜渐近线：f(x) = (x² + 1)/(x − 1) = x + 1 + 2/(x − 1)
f = lambda x: (x * x + 1) / (x - 1)
out(f100=f(100), gap100=f(100) - 101, f1e4=f(1e4) - (1e4 + 1))

# 两节连杆：腕心到肩的距离 r 时的肘关节角 θ₂ = arccos((r² − l₁² − l₂²)/(2 l₁ l₂))
e = json.loads((Path(__file__).resolve().parents[2] / "models" / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))
js = {j["name"]: j for j in e["robot"]["joints"]}
l1, l2 = js["elbow_joint"]["origin"]["xyz"][2], js["wrist_1_joint"]["origin"]["xyz"][2]
R = l1 + l2
th2 = lambda r: math.acos(min(1.0, (r * r - l1 * l1 - l2 * l2) / (2 * l1 * l2)))
rows = []
for gap_mm in (100, 10, 1, 0.1, 0.01):
    r = R - gap_mm / 1000
    d = gap_mm / 1000 / 1000                      # 腕心再外伸 gap 的千分之一
    s = (th2(r) - th2(r + d)) / d                 # 每外伸 1 m 肘关节要转过的弧度（灵敏度）
    rows.append((gap_mm, math.degrees(th2(r)), s))
out(R=R, sens_tab="\n".join(f"| {g:g} | {a:.3f} | {s:.1f} |" for g, a, s in rows))
# 灵敏度 ≈ C/√(R − r)，C = ½√(2R/(l₁l₂))（由 cos θ ≈ 1 − θ²/2 推出，第 9 章）
C = rows[-1][2] * math.sqrt(rows[-1][0] / 1000)
out(C=C, C_pred=0.5 * math.sqrt(2 * R / (l1 * l2)))
