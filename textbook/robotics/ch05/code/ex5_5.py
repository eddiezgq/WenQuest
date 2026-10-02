"""算例 5.5.1、5.5.2：相机-机械臂-工件的坐标链。

工作站（图 5.5.1）：工作台 {w}；UR5e 基座 {s}（台面 (0.30, 0.40) m，绕 z 转 180°）；固定相机 {c}（高 0.90 m，
光轴偏离竖直 15°）；齿轮坯 {o}；抓取坐标系 {g}（工件上、z_g 向下）；夹爪工具坐标系 {t}（法兰外 0.15 m）。
为了能核对，虚拟工作站里先把齿轮坯放在已知位置：中心 (0.80, 0.45) m，放在 20 mm 高的料盘上，绕 z 转 25°；
相机的位姿估计给出 T_co（这里由已知位置算出，代表一次理想的测量）。

5.5.1 由相机读数求机械臂应到达的位姿：
      T_sg = T_sw T_wc T_co T_og，法兰目标 T_sb* = T_sg T_bt⁻¹。
      做法一：按链手写相乘；做法二：坐标系树的通用路径算法；做法三：与工件的已知位置比较。
      再用数值逆运动学（第 15 章）求关节角 θ*，用网页三维模型的算法算 T_sb(θ*)，应与 T_sb* 一致。
5.5.2 误差沿链传播：相机安装角有 0.5° 的误差（分别绕 x_c、y_c、z_c），夹爪到达点偏离多少？
      与一阶估计 |δ × r|（r 为从相机原点到抓取点的矢量）比较。
"""
import math

import numpy as np

from _frames import (DEG, FrameTree, P_WC, T, T_bt, T_og, T_wc, T_ws, clean, hom, inv, log_rot, rot_axis, rot_x, rot_y, rot_z,
                     texm, ur_fk_glb, ur_fk_poe, ur_ik, vecm)
from bookout import T as TT, out

# 虚拟工作站里工件的已知位置（只用来产生相机读数和最后核对）
Two_true = T(rot_z(25 * DEG), (0.80, 0.45, 0.02))
Tco = inv(T_wc()) @ Two_true                     # 相机的位姿估计结果

# ---------------------------------------------------------------- 算例 5.5.1
Tsw = inv(T_ws())
Tsg_1 = Tsw @ T_wc() @ Tco @ T_og()               # 做法一：手写的链
tree = FrameTree("w")
tree.add("s", "w", T_ws())
tree.add("c", "w", T_wc())
tree.add("o", "c", Tco)                           # 相机看到的工件：挂在 {c} 下
tree.add("g", "o", T_og())
Tsg_2 = tree.T("s", "g")                          # 做法二：树的路径算法
assert np.allclose(Tsg_1, Tsg_2, atol=1e-15)
Tsg_3 = Tsw @ Two_true @ T_og()                   # 做法三：与已知位置比较
assert np.allclose(Tsg_1, Tsg_3, atol=1e-15)
Two = T_wc() @ Tco
assert np.allclose(Two, Two_true, atol=1e-15)

Tsb_goal = Tsg_1 @ inv(T_bt())
# 闭合方程 (5.5.1) 两边相等：机器人一侧与相机一侧算出的 T_wt 相同
# 预抓取位姿：工具中心点在抓取点正上方 50 mm（沿 −z_g），T_gt = Trans(0, 0, −0.05)
Tsb_pre = Tsg_1 @ T(None, (0, 0, -0.05)) @ inv(T_bt())
assert np.allclose(Tsb_pre[:3, 3] - Tsb_goal[:3, 3], [0, 0, 0.05])
# 齿轮坯外圆上的一个标记点（{o} 中 (0.04, 0, 0.03)，即顶面边缘）两条路换到 {s}
mark_o = np.array([0.04, 0.0, 0.03])
m1 = (Tsw @ T_wc() @ Tco @ hom(mark_o))[:3]
m2 = (tree.T("s", "o") @ hom(mark_o))[:3]
assert np.allclose(m1, m2)

# 机械臂能不能到：数值逆运动学（第 15 章）
seed = np.array([0, -60, 100, -130, -90, 0]) * DEG
th = ur_ik(Tsb_goal, seed)
th = (th + math.pi) % (2 * math.pi) - math.pi
Tsb_reach = ur_fk_glb(th)                         # 用三维模型的算法独立核对
err_reach = np.abs(Tsb_reach - Tsb_goal).max()
assert err_reach < 1e-12
Tst_reach = Tsb_reach @ T_bt()
assert np.allclose(Tst_reach, Tsg_1, atol=1e-12)
assert np.allclose(T_ws() @ Tsb_reach @ T_bt(), T_wc() @ Tco @ T_og(), atol=1e-12)        # 闭合方程 (5.5.1)
# UR 控制器的显示形式 (x, y, z, rx, ry, rz)：位置用 mm，姿态用转动矢量（4.4 节的指数坐标）
rv = log_rot(Tsg_1[:3, :3])
assert np.allclose(rot_axis(rv, np.linalg.norm(rv)), Tsg_1[:3, :3], atol=1e-12)      # 由转动矢量还原姿态

# ---------------------------------------------------------------- 算例 5.5.2 误差传播
delta = 0.5 * DEG
p_g_w = (T_wc() @ Tco @ T_og())[:3, 3]
r_cg_w = p_g_w - P_WC                                 # 从相机原点到抓取点，{w} 中
errs, est = [], []
for k, R_err in enumerate((rot_x(delta), rot_y(delta), rot_z(delta))):
    Twc_bad = T_wc() @ T(R_err)                       # 相机实际姿态绕自身轴偏了 δ，而程序仍用名义值
    p_bad = (Twc_bad @ Tco @ T_og())[:3, 3]
    errs.append(np.linalg.norm(p_bad - p_g_w))
    axis_w = T_wc()[:3, k]                             # 误差转轴在 {w} 中
    est.append(np.linalg.norm(np.cross(delta * axis_w, r_cg_w)))
for e, a in zip(errs, est):
    assert abs(e - a) < 0.01 * a + 1e-6                # 一阶估计与精确值相差不到 1%
lever = np.linalg.norm(r_cg_w)
# 同样 0.5° 的误差出现在机器人基座的安装上（绕 z_s）：抓取点到 z_s 轴的距离为杠杆
Tws_bad = T_ws() @ T(rot_z(delta))
p_bad_s = (inv(Tws_bad) @ hom(p_g_w))[:3]
err_base = np.linalg.norm(p_bad_s - Tsg_1[:3, 3])
r_base = math.hypot(Tsg_1[0, 3], Tsg_1[1, 3])
assert abs(err_base - 2 * r_base * math.sin(delta / 2)) < 1e-12

out(
    Tco=texm(clean(Tco), 4), pco=vecm(Tco[:3, 3], 4), dist_co=np.linalg.norm(Tco[:3, 3]),
    Tsw=texm(clean(Tsw), 2), Tog=texm(clean(T_og()), 3),
    Two=texm(clean(Two), 4), Tsg=texm(clean(Tsg_1), 4), psg=vecm(Tsg_1[:3, 3], 4),
    Tsb_goal=texm(clean(Tsb_goal), 4), psb=vecm(Tsb_goal[:3, 3], 4), psb_pre=vecm(Tsb_pre[:3, 3], 4),
    m_s=vecm(m1, 4), th_deg=TT("，", ", ").join(f"{math.degrees(x):.2f}°".replace("-", "−") for x in th),
    th=[math.degrees(x) for x in th], err_reach=err_reach,
    ur_x=Tsg_1[0, 3] * 1000, ur_y=Tsg_1[1, 3] * 1000, ur_z=Tsg_1[2, 3] * 1000, rx=rv[0], ry=rv[1], rz=float(clean([rv[2]])[0]),
    rv_deg=math.degrees(np.linalg.norm(rv)),
    ex_mm=errs[0] * 1000, ey_mm=errs[1] * 1000, ez_mm=errs[2] * 1000,
    ax_mm=est[0] * 1000, ay_mm=est[1] * 1000, az_mm=est[2] * 1000,
    lever=lever, delta_rad=delta, base_mm=err_base * 1000, r_base=r_base,
    rcg=vecm(r_cg_w, 4),
)
