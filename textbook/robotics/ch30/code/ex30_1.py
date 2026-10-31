"""30.1 节的计算：需求分析。

(1) 设计任务书里的几个数：臂展、关节伸直时 J1 转动带来的 TCP 速度、自重与负载比（与零件库 UR5e 比较）。
(2) 算例 30.1.1：还没有设计，先估肩关节 J2 的力矩：负载在臂展处，手臂运动部分的质量按负载的 2.4 倍（经验值）、质心在臂展一半处；
    与 30.3 节按完整模型算出的最大重力矩比较；对照谐波减速器的规格。
(3) 算例 30.1.2：减速器厂部件装配工位的取放点（工具朝下，还要从上方 0.1 m 处接近）要多大的臂展：
    按 30.3 节的分配规则（a2 − a3 = 4 cm）找出所有点都留 5% 裕量的最小臂展；WQ-CR5 的裕量。
(4) 算例 30.1.3：节拍。取放一个零件：J1 转 90°，在两头各下、上 0.1 m，夹爪开合两次；
    围栏内按设计速度，与人同场时 TCP 限速 0.25 m/s（示例）；一套中间轴组件 SA-200 的 7 个零件。
(5) 算例 30.1.4：精度。重复定位精度（单向接近）与反向时谐波减速器背隙让 TCP 走多少：机器人厂关节测试台的背隙名义值。
(6) 生活中的例子：夹在书桌后沿中间的台灯，要照到 1.2 m × 0.6 m 桌面的每个角。
"""
import math

from _ch30 import G0, TOOL, cr_dh, library_arms, move_time, reach_margin, robot_plant, station_points, wqcr5
from bookout import out

W = wqcr5()
S = W.summary()
R = S["reach_mm"] / 1000
# ---------------------------------------------------------------- (1) 任务书
w_max = W.DESIGN_SPEED
v_tcp = w_max * R
ur = next(a for a in library_arms() if a["id"] == "B-ARM-UR5E")
ratio_cr = W.PAYLOAD_KG / S["mass_kg"]
ratio_ur = ur["payload_kg"] / ur["weight_kg"]
assert 0.25 < ratio_cr < 0.35 and ratio_ur < ratio_cr
out(payload=W.PAYLOAD_KG, reach_mm=S["reach_mm"], w_deg=math.degrees(w_max), a_deg=math.degrees(W.DESIGN_ACCEL["standard"]),
    v_tcp=v_tcp, mass=S["mass_kg"], ratio_cr=ratio_cr, ur_mass=ur["weight_kg"], ratio_ur=ratio_ur, ur_reach=ur["reach_mm"])

# ---------------------------------------------------------------- (2) 第一估计
k_arm = 2.4
m_arm = k_arm * W.PAYLOAD_KG
tau_est = G0 * (W.PAYLOAD_KG * R + m_arm * R / 2)
d = W.design()
g2 = d["joints"][1]["g_max"]
err_est = (tau_est - g2) / g2 * 100
assert abs(err_est) < 10
L = W.MODULES["L"]["gear"]
out(k_arm=k_arm, m_arm=m_arm, tau_est=tau_est, g2=g2, err_est=err_est, err_abs=abs(err_est), gear_L=L[0], rated_L=L[1], peak_L=L[2],
    moving=S["moving_mass_kg"], k_real=S["moving_mass_kg"] / W.PAYLOAD_KG)

# ---------------------------------------------------------------- (3) 工位要多大的臂展
pts = station_points()
need = None
for k in range(600, 900):
    Rk = k / 1000
    a2, a3 = W.split(Rk)
    dh = cr_dh(a2, a3)
    if min(reach_margin(p[2], p[3], dh) for p in pts) >= 0.05:
        need = Rk
        break
dh0 = cr_dh()
margins = {p[0]: reach_margin(p[2], p[3], dh0) for p in pts}
worst = min(margins, key=margins.get)
assert worst.startswith("AGV") and 0.7 < need < 0.8
out(n_pts=len(pts), reach_need_mm=need * 1000, margin_cr=margins[worst] * 100, worst_pt=worst, tool_mm=TOOL * 1000,
    margin_need=5)

# ---------------------------------------------------------------- (4) 节拍
a_lin, v_fast, v_coop = 1.0, 0.5, 0.25                      # 直线接近：加速度 m/s²、速度 m/s（围栏内 / 与人同场，示例）
t_j1 = move_time(math.pi / 2, w_max, W.DESIGN_ACCEL["standard"])
t_up = move_time(0.1, v_fast, a_lin)
t_grip = 0.3
t_fast = 2 * t_j1 + 4 * t_up + 2 * t_grip
r_mid = 0.55
t_j1_coop = move_time(math.pi / 2 * r_mid, v_coop, a_lin)     # 与人同场：TCP 沿圆弧不超过 0.25 m/s
t_up_coop = move_time(0.1, v_coop, a_lin)
t_coop = 2 * t_j1_coop + 4 * t_up_coop + 2 * t_grip
F = __import__("_ch30").factory_data()
n_sa200 = int(sum(q for _, q in F.BOMS["SA-200"][1]))
manual_min = dict(F.ROUTINGS["RT-部件装配 Shaft sub-assembly"])["部件装配 Sub-assembly"]
assert n_sa200 == 7 and t_fast < t_coop
out(t_j1=t_j1, t_up=t_up, t_grip=t_grip, t_fast=t_fast, v_coop=v_coop, t_coop=t_coop, n_sa200=n_sa200,
    sa_fast=n_sa200 * t_fast, sa_coop=n_sa200 * t_coop, manual_min=manual_min, r_mid=r_mid, a_lin=a_lin, v_fast=v_fast)

# ---------------------------------------------------------------- (5) 精度
P = robot_plant()
ch = {m["item"]: {c["code"]: c for c in m["chars"]} for m in P["measurements"]}
bl = [ch[W.MODULES[s]["code"]]["joint_backlash"]["nominal"] for s in W.JOINT_MODULE]       # arcmin
rep = ch["WQ-CR5"]["cr_repeat"]
acc = ch["WQ-CR5"]["cr_abs"]
arcmin = math.radians(1 / 60)
lever = [R, R, abs(W.DH[2]["a"]) + W.DH[4]["d"]]               # 手臂伸直时，J1、J2、J3 到 TCP 的距离（不计工具）
d_bl = [b * arcmin * l * 1000 for b, l in zip(bl[:3], lever)]
assert d_bl[0] > 5 * rep["hi"]
out(bl_L=bl[0], bl_M=bl[2], bl_S=bl[3], d_bl1=d_bl[0], d_bl_sum=sum(d_bl), rep_nom=rep["nominal"], rep_hi=rep["hi"],
    acc_nom=acc["nominal"], acc_hi=acc["hi"], lever3=lever[2])

# ---------------------------------------------------------------- (6) 台灯
desk_w, desk_d = 1.2, 0.6
lamp_reach = math.hypot(desk_w / 2, desk_d)
out(desk_w=desk_w, desk_d=desk_d, lamp_reach=lamp_reach)
