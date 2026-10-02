"""算例 5.1.1、5.1.2：同一点在原点不同的两个坐标系中的坐标。

5.1.1 工作台坐标系 {w} 与 UR5e 基座坐标系 {s}：{s} 的原点在 {w} 中为 (0.30, 0.40, 0) m，绕 z 转 180°。
      工件中心 P 在 {w} 中为 (0.80, 0.45, 0.02) m，求它在 {s} 中的坐标。
      做法一：定理 5.1.1，p_s = R_wsᵀ (p_w − p_ws)；做法二：逐轴的几何推理（x_s = −x_w，y_s = −y_w）。
5.1.2 车间地图 {m} 与 AGV 坐标系 {v}：AGV 在 (12.0, 5.0) m，航向 30°。货架工位 Q 在 (14.5, 8.0) m。
      做法一：定理 5.1.1；做法二：先求距离和方位角，再减去航向（极坐标）。
两种做法必须一致；并验证到原点的距离、两点之间的距离与坐标系无关，自由矢量只按 R 变换。
"""
import math

import numpy as np

from _frames import rot_z
from bookout import out

# ---------------------------------------------------------------- 算例 5.1.1
p_ws = np.array([0.30, 0.40, 0.0])          # {s} 的原点在 {w} 中，m
R_ws = rot_z(math.pi)                        # {s} 相对 {w} 绕 z 转 180°
p_w = np.array([0.80, 0.45, 0.02])          # 工件中心 P 在 {w} 中，m

p_s = R_ws.T @ (p_w - p_ws)                  # 定理 5.1.1 解出 p_s
d = p_w - p_ws
p_s_geo = np.array([-d[0], -d[1], d[2]])     # x_s 与 x_w 反向，y_s 与 y_w 反向，z 相同
assert np.allclose(p_s, p_s_geo, atol=1e-15)
assert np.allclose(p_ws + R_ws @ p_s, p_w)   # 反过来代回式 (5.1.3)

# 位置矢量依赖原点：|O_w P| 与 |O_s P| 不同；而 O_s 到 P 的距离在两个坐标系中算出来相同
dist_s = np.linalg.norm(p_s)
dist_s_from_w = np.linalg.norm(p_w - p_ws)
assert abs(dist_s - dist_s_from_w) < 1e-15
dist_w = np.linalg.norm(p_w)

# 第二点：夹具定位销 Q 在 {w} 中为 (0.80, 0.25, 0.02) m；两点间距离与坐标系无关
q_w = np.array([0.80, 0.25, 0.02])
q_s = R_ws.T @ (q_w - p_ws)
assert abs(np.linalg.norm(p_w - q_w) - np.linalg.norm(p_s - q_s)) < 1e-15

# ---------------------------------------------------------------- 算例 5.1.2（平面）
p_mv = np.array([12.0, 5.0])                 # AGV 坐标系 {v} 的原点在地图 {m} 中，m
psi = math.radians(30)                       # 航向：x_v 相对 x_m 逆时针 30°
c, s = math.cos(psi), math.sin(psi)
R_mv = np.array([[c, -s], [s, c]])
q_m = np.array([14.5, 8.0])                  # 货架工位 Q 在 {m} 中

q_v = R_mv.T @ (q_m - p_mv)                  # 做法一
dq = q_m - p_mv
rng = math.hypot(*dq)                        # 做法二：距离与方位
bearing_m = math.atan2(dq[1], dq[0])         # 在地图中看的方位角
bearing_v = bearing_m - psi                  # 相对 AGV 车头的方位角
q_v_polar = rng * np.array([math.cos(bearing_v), math.sin(bearing_v)])
assert np.allclose(q_v, q_v_polar, atol=1e-13)

# 自由矢量：AGV 以 1.0 m/s 沿车头方向行驶；速度在 {m} 中为 R_mv (1, 0)，换回 {v} 只用 R，不减原点
v_v = np.array([1.0, 0.0])
v_m = R_mv @ v_v
assert np.allclose(R_mv.T @ v_m, v_v)
wrong = R_mv.T @ (v_m - p_mv)               # 误把速度当作点来变换，得到荒谬的结果
assert np.linalg.norm(wrong) > 10

out(
    ps_x=p_s[0], ps_y=p_s[1], ps_z=p_s[2], dx=d[0], dy=d[1],
    dist_s=dist_s, dist_w=dist_w, qs_x=q_s[0], qs_y=q_s[1], dist_pq=np.linalg.norm(p_w - q_w),
    c30=c, s30=s, qv_x=q_v[0], qv_y=q_v[1], rng=rng,
    bear_m_deg=math.degrees(bearing_m), bear_v_deg=math.degrees(bearing_v),
    vm_x=v_m[0], vm_y=v_m[1], wrong_x=wrong[0], wrong_y=wrong[1],
)
