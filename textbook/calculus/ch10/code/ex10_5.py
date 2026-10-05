"""10.5 节：曲率——抛物线与椭圆的曲率核对；AGV 换道路径（横移 1 m、长 4 m）三种设计的最大曲率、入口处的曲率跳变、
侧向加速度 1 m/s² 限制下的最高车速 v = √(a/κ)，以及过最大曲率点时左右轮的速度。"""
import math

from _path import A_LAT, B_TRACK, curvature, lane
from bookout import out

# 抛物线 y = x² 在顶点 κ = 2；椭圆 a = 2、b = 1 的顶点
a, b = 2.0, 1.0
out(ell_k_major=a / b ** 2, ell_k_minor=b / a ** 2)

d, L = 1.0, 4.0
names = {"cubic": "三次多项式", "cos": "余弦", "quintic": "五次多项式"}
rows = []
res = {}
for kind in ("cubic", "cos", "quintic"):
    y, yp, ypp = lane(kind, d, L)
    N = 40000
    xs = [L * k / N for k in range(N + 1)]
    km = max(curvature(yp, ypp, x) for x in xs)
    xm = max(xs, key=lambda x: curvature(yp, ypp, x))
    k0 = curvature(yp, ypp, 0.0)
    v = math.sqrt(A_LAT / km)
    res[kind] = (km, v)
    rows.append(f"| {names[kind]} | {k0:.4f} | {km:.4f} | {1 / km:.2f} | {xm:.2f} | {v:.2f} |")
out(lane_tab="\n".join(rows), d=d, L=L, a_lat=A_LAT)
km, v = res["quintic"]
# 差速 AGV：v_R,L = v(1 ± bκ/2)
out(q_v=v, q_vR=v * (1 + B_TRACK * km / 2), q_vL=v * (1 - B_TRACK * km / 2), q_w=v * km)
# 直线接圆弧：半径 R = 1 m 的 90° 转弯，v = 1 m/s 时角速度从 0 突变到 1 rad/s
out(arc_R=1.0, arc_vmax=math.sqrt(A_LAT * 1.0))
