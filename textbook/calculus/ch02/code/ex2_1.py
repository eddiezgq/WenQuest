"""2.1 节：实数与不等式——0.1 在计算机里的真实值；用二分法逐位夹出 √2；机械臂末端误差的上界（三角不等式）。"""
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np

from bookout import out

# 浮点数都是有理数：0.1 在双精度下的精确值是一个分母为 2^55 的分数
f = Fraction(0.1)
assert f.denominator == 2**55 and f != Fraction(1, 10)
out(f01_num=str(f.numerator), f01_den=str(f.denominator), f01_den_pow=55,
    f01_err=float(f - Fraction(1, 10)), eps=np.finfo(float).eps)

# 有理数的小数展开终将循环：1/7 = 0.142857 142857 …（长除法的余数只能取 1–6，至多 6 步就重复）
rem, digits = 1, []
for _ in range(12):
    rem *= 10
    digits.append(rem // 7)
    rem %= 7
out(seventh="".join(map(str, digits)))

# 用二分法逐步夹出 √2：每一步把区间一分为二，保留 x² − 2 变号的那一半
a, b = 1.0, 2.0
rows = []
for k in range(1, 21):
    m = (a + b) / 2
    if m * m < 2:
        a = m
    else:
        b = m
    rows.append((k, a, b))
out(bis_table="\n".join(f"| {k} | {lo:.7f} | {hi:.7f} | $2^{{-{k}}}$ |" for k, lo, hi in rows[:6] + rows[9:10] + rows[19:20]),
    bis20_lo=rows[19][1], bis20_hi=rows[19][2], bis20_w=rows[19][2] - rows[19][1], sqrt2=math.sqrt(2))

# 算例 2.1.3：UR5e 的上臂、前臂长（零件库模型）；肩、肘两关节各有 ±δ 的角度误差时，腕心位置误差的上界
e = json.loads((Path(__file__).resolve().parents[2] / "models" / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))
js = {j["name"]: j for j in e["robot"]["joints"]}
l1, l2 = js["elbow_joint"]["origin"]["xyz"][2], js["wrist_1_joint"]["origin"]["xyz"][2]
d = math.radians(0.01)
bound = (l1 + l2) * d + l2 * d                 # 三角不等式：两项误差之和
out(l1=l1, l2=l2, d_rad=d, err1_mm=(l1 + l2) * d * 1000, err2_mm=l2 * d * 1000, bound_mm=bound * 1000)
# 用数值核对：在若干姿态、若干误差组合下实际的腕心偏差都不超过上界
worst = 0.0
for t1 in np.linspace(-math.pi, math.pi, 37):
    for t2 in np.linspace(-math.pi, math.pi, 37):
        p = np.array([l1 * math.cos(t1) + l2 * math.cos(t1 + t2), l1 * math.sin(t1) + l2 * math.sin(t1 + t2)])
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                u1, u2 = t1 + s1 * d, t2 + s2 * d
                q = np.array([l1 * math.cos(u1) + l2 * math.cos(u1 + u2), l1 * math.sin(u1) + l2 * math.sin(u1 + u2)])
                worst = max(worst, float(np.linalg.norm(q - p)))
assert worst <= bound
out(worst_mm=worst * 1000)

# 编码器：设每转 2^17 个计数，一个计数对应的角度
out(cnt=2**17, res_deg=360 / 2**17)
