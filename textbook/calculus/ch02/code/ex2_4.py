"""2.4 节：基本初等函数——指数增长与幂增长的比较；小角度下 sin x ≈ x；arctan 与 atan2 的区别；
算例 2.4.1：UR5e 上臂、前臂两节连杆的逆运动学（反余弦给出肘关节角，两组解）。"""
import json
import math
from pathlib import Path

import numpy as np

from bookout import out

# 2^x 与 x^10：x > 1 时比较 x ln 2 与 10 ln x，二分法求交点
F = lambda x: x * math.log(2) - 10 * math.log(x)
a, b = 2.0, 100.0           # F(2) < 0 < F(100)
for _ in range(80):
    m = (a + b) / 2
    a, b = (m, b) if F(m) < 0 else (a, m)
c_hi = (a + b) / 2
a, b = 1.01, 2.0            # F(1.01) > 0 > F(2)：较小的那个交点
for _ in range(80):
    m = (a + b) / 2
    a, b = (m, b) if F(m) > 0 else (a, m)
out(cross_lo=(a + b) / 2)
out(cross=c_hi, p2_10=2**10, p10_10=10**10, p2_100=f"{2**100:.3e}".replace("e+", "\\times 10^{") + "}",
    p100_10=f"{100**10:.0e}".replace("e+", "\\times 10^{") + "}")

# 2^√2 的有理逼近：√2 的截断小数 1.4, 1.41, 1.414, 1.4142, 1.41421
qs = [math.floor(math.sqrt(2) * 10**k) / 10**k for k in range(1, 6)]
out(sq_seq="、".join(f"{q:.{k}f}" for k, q in enumerate(qs, 1)), pow_seq="、".join(f"{2**q:.6f}" for q in qs),
    pow_true=2 ** math.sqrt(2), one_plus=repr(float(1 + np.finfo(float).eps)))

# 小角度：sin x ≈ x（x 用弧度）
for k, x in enumerate((0.5, 0.1, 0.01)):
    out(**{f"sx{k}": math.sin(x), f"sxr{k}": abs(math.sin(x) - x) / x})
out(deg1=math.radians(1), sin1deg=math.sin(1.0))      # sin(1) 在弧度下，常被误当作 sin 1°

# arctan(y/x) 与 atan2(y, x)：点 (−0.3, −0.4)
x0, y0 = -0.3, -0.4
out(at=math.degrees(math.atan(y0 / x0)), at2=math.degrees(math.atan2(y0, x0)))

# 算例 2.4.1：两节连杆逆运动学
e = json.loads((Path(__file__).resolve().parents[2] / "models" / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))
js = {j["name"]: j for j in e["robot"]["joints"]}
l1, l2 = js["elbow_joint"]["origin"]["xyz"][2], js["wrist_1_joint"]["origin"]["xyz"][2]
px, py = 0.5, 0.3
r2 = px * px + py * py
c2 = (r2 - l1 * l1 - l2 * l2) / (2 * l1 * l2)
sols = []
for s in (+1, -1):
    t2 = s * math.acos(c2)
    t1 = math.atan2(py, px) - math.atan2(l2 * math.sin(t2), l1 + l2 * math.cos(t2))
    fx, fy = l1 * math.cos(t1) + l2 * math.cos(t1 + t2), l1 * math.sin(t1) + l2 * math.sin(t1 + t2)
    assert abs(fx - px) < 1e-12 and abs(fy - py) < 1e-12        # 正运动学核对
    sols.append((math.degrees(t1), math.degrees(t2)))
out(l1=l1, l2=l2, r=math.sqrt(r2), c2=c2, t1a=sols[0][0], t2a=sols[0][1], t1b=sols[1][0], t2b=sols[1][1],
    rmin=abs(l1 - l2), rmax=l1 + l2)

# 对数：分贝与编码器位数
out(db10=10 * math.log10(10), db20=10 * math.log10(100), bits=math.log2(131072), ln10=math.log(10), e=math.e)
