"""算例 1.3.1：SCARA 与 UR5e 的工作空间——同是“机械臂”，结构不同，能到达的区域形状完全不同。

SCARA（零件库 B-SCA-WQ4）：两段水平臂 a1、a2 绕竖直轴转动，关节限位取自模型。末端在水平面内能到达的面积用两种方法算：
  (1) 网格 + 逆解：对每个网格点按平面两连杆的逆解判断是否有一组关节角落在限位之内；
  (2) 随机撒关节角：按正运动学算出末端，统计落到的网格。
两者之差必须小于 2%。竖直方向的行程乘以面积即工作空间体积。
UR5e（B-ARM-UR5E）：关节都能转 ±360°，随机撒关节角，求法兰中心到肩部中心的最大距离。
"""
import math

import numpy as np

from _ch1 import ALL8, dof_summary, entry, fk_point
from bookout import out

rng = np.random.default_rng(13)

# ---------------------------------------------------------------- SCARA
sc = entry("B-SCA-WQ4")
J = {j["name"]: j for j in sc["robot"]["joints"]}
a1 = J["J2"]["origin"]["xyz"][0]               # 0.35 m：关节 1 到关节 2
a2 = J["J3"]["origin"]["xyz"][0]               # 0.25 m：关节 2 到丝杠
t1lo, t1hi = J["J1"]["limit"]["lower"], J["J1"]["limit"]["upper"]
t2lo, t2hi = J["J2"]["limit"]["lower"], J["J2"]["limit"]["upper"]
stroke = J["J3"]["limit"]["upper"] - J["J3"]["limit"]["lower"]
r_max = a1 + a2
r_min = math.sqrt(a1 ** 2 + a2 ** 2 + 2 * a1 * a2 * math.cos(t2hi))   # 关节 2 转到极限时离轴线最近


def reachable(x, y):
    """平面两连杆逆解：有一组 (θ1, θ2) 落在限位内即可达。"""
    r2 = x * x + y * y
    c2 = (r2 - a1 * a1 - a2 * a2) / (2 * a1 * a2)
    if c2 > 1 or c2 < math.cos(t2hi):
        return False
    for t2 in (math.acos(c2), -math.acos(c2)):
        t1 = math.atan2(y, x) - math.atan2(a2 * math.sin(t2), a1 + a2 * math.cos(t2))
        t1 = (t1 + math.pi) % (2 * math.pi) - math.pi
        if t1lo <= t1 <= t1hi and t2lo <= t2 <= t2hi:
            return True
    return False


h = 0.005                                       # 网格边长 5 mm
xs = np.arange(-r_max - h, r_max + h, h) + h / 2
grid = np.array([[reachable(x, y) for x in xs] for y in xs])
area_grid = grid.sum() * h * h

N = 400000
th1 = rng.uniform(t1lo, t1hi, N)
th2 = rng.uniform(t2lo, t2hi, N)
px = a1 * np.cos(th1) + a2 * np.cos(th1 + th2)
py = a1 * np.sin(th1) + a2 * np.sin(th1 + th2)
ix = np.floor((px - xs[0] + h / 2) / h).astype(int)
iy = np.floor((py - xs[0] + h / 2) / h).astype(int)
hit = np.zeros_like(grid)
hit[iy, ix] = True
area_mc = hit.sum() * h * h
assert abs(area_mc - area_grid) / area_grid < 0.02          # 两种算法一致
# 用模型的正运动学核对一点：两种运动学（手写的两连杆、模型关节表）给出同一末端
q = {"J1": 0.4, "J2": -0.9, "J3": 0.05, "J4": 0.0}
p_model = fk_point(sc, q, "tool")
p_hand = (a1 * math.cos(0.4) + a2 * math.cos(0.4 - 0.9), a1 * math.sin(0.4) + a2 * math.sin(0.4 - 0.9))
assert abs(p_model[0] - p_hand[0]) < 1e-9 and abs(p_model[1] - p_hand[1]) < 1e-9
annulus = math.pi * (r_max ** 2 - r_min ** 2)
vol_sc = area_grid * stroke

# ---------------------------------------------------------------- UR5e
ur = entry("B-ARM-UR5E")
names = [j["name"] for j in ur["robot"]["joints"]]
shoulder = fk_point(ur, {}, "upper_arm_link")            # 肩关节（关节 2）轴上的点
M = 20000
d_sh = []
for _ in range(M):
    qq = dict(zip(names, rng.uniform(-math.pi, math.pi, 6)))
    d_sh.append(np.linalg.norm(fk_point(ur, qq, "wrist_3_link", (0, 0.1, 0)) - shoulder))
d_sh = np.array(d_sh)
d_sh_max = d_sh.max()
out_pct = float((d_sh > 0.85).mean() * 100)          # 离肩部超过厂家工作半径 0.85 m 的样本所占比例
# 上界：从肩部到法兰，各段相对位移的长度之和（三角不等式），实际距离不会超过它
segs = [j["origin"]["xyz"] for j in ur["robot"]["joints"][2:]] + [(0, 0.1, 0)]
bound = sum(float(np.linalg.norm(s_)) for s_ in segs)
assert d_sh_max <= bound + 1e-9
vol_ur = 4 / 3 * math.pi * 0.85 ** 3                      # 以手册工作半径 0.85 m 为半径的球

# ---------------------------------------------------------------- 八台模型的类别信息
rows = [dof_summary(e) for e in ALL8]
n_fixed = sum(r["base"] == "fixed" for r in rows)
n_mobile = len(rows) - n_fixed

out(a1=a1, a2=a2, t1_deg=math.degrees(t1hi), t2_deg=math.degrees(t2hi), stroke=stroke, r_max=r_max, r_min=r_min,
    area_grid=area_grid, area_mc=area_mc, area_diff_pct=abs(area_mc - area_grid) / area_grid * 100, annulus=annulus,
    vol_sc=vol_sc, d_sh_max=d_sh_max, out_pct=out_pct, bound=bound, vol_ur=vol_ur, vol_ratio=vol_ur / vol_sc, N=N, M=M,
    n_fixed=n_fixed, n_mobile=n_mobile)
