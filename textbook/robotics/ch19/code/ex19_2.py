"""19.2 节的计算：差速驱动的正、逆运动学，SE(2) 指数映射，数字工厂中的真实路线。

算例 19.2.1  给定车速和角速度求两轮转速与瞬心，用式 (19.2.4) 的两种写法核对转弯半径。
算例 19.2.2  两轮匀速转动 2 s：按式 (19.2.6) 的闭式、矩阵指数的级数、细步长数值积分三种方法求终点，三者一致；
             与欧拉法（步长 0.1 s）比较。
算例 19.2.3  轮速限制下 (v, ω) 的可行范围；在半径 ρ 的圆弧上，轮速和横向加速度各自允许的最高车速。
算例 19.2.4  数字工厂的真实路线：从热处理炉 ht-01 到数控车床 B（输出轴 SH-301 的第 3 次搬运，路线由工厂仿真的
             同一套布置与规则给出）。两种走法：(A) 每个拐角停车、原地转 90°；(B) 拐角用半径 0.5 m 的圆弧过渡。
             在轮速、切向加速度、横向加速度三种限制下求最短时间的速度曲线、两轮转速和行驶时间；
             再把算出的两轮转速按 1 ms 的步长（每步按圆弧精确积分）积分回去，核对车停在目标上下料点。
"""
import math

import numpy as np

from _mob import (diff_cart, profile, exp_se2, expm, bracket_mat, factory, q_of, qdot, round_corners, se2, seg_len, seg_point,
                  step_euler, step_exact, to_book)
from bookout import T, out

P = diff_cart()
r, b, wmax = P["r"], P["b"], P["wmax"]

# ---------------------------------------------------------------- 算例 19.2.1
J = np.array([[r / b, -r / b], [r / 2, r / 2]])           # (ω, v) = J (ω_R, ω_L)
Jinv = np.linalg.inv(J)
v1, om1 = 0.5, 0.5
wR1, wL1 = Jinv @ np.array([om1, v1])
assert abs(wR1 - (v1 + om1 * b / 2) / r) < 1e-12 and abs(wL1 - (v1 - om1 * b / 2) / r) < 1e-12
R1 = v1 / om1
R_formula = b / 2 * (wR1 + wL1) / (wR1 - wL1)
assert abs(R1 - R_formula) < 1e-12
detJ = np.linalg.det(J)
assert abs(detJ - r * r / b) < 1e-15

# ---------------------------------------------------------------- 算例 19.2.2：两轮匀速 2 s
t2 = 2.0
V2 = np.array([om1, v1, 0.0])
T_closed = exp_se2(V2, t2)
T_series = expm(bracket_mat(V2) * t2)
assert np.allclose(T_closed, T_series, atol=1e-12)
q_closed = q_of(T_closed)
x_arc, y_arc = R1 * math.sin(om1 * t2), R1 * (1 - math.cos(om1 * t2))
assert abs(q_closed[0] - x_arc) < 1e-12 and abs(q_closed[1] - y_arc) < 1e-12
# 细步长数值积分（四阶龙格-库塔，h = 1 ms）
q = np.zeros(3)
h = 1e-3
for _ in range(int(round(t2 / h))):
    k1 = qdot(q, V2)
    k2 = qdot(q + h / 2 * k1, V2)
    k3 = qdot(q + h / 2 * k2, V2)
    k4 = qdot(q + h * k3, V2)
    q = q + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
assert np.allclose(q, q_closed, atol=1e-10)
# 欧拉法，步长 0.1 s
qe = np.zeros(3)
for _ in range(20):
    qe = step_euler(qe, V2, 0.1)
err_euler = float(np.hypot(*(qe[:2] - q_closed[:2])))
# 圆弧精确更新，步长 0.1 s：每一步都精确
qx = np.zeros(3)
for _ in range(20):
    qx = step_exact(qx, V2, 0.1)
assert np.allclose(qx, q_closed, atol=1e-12)

# ---------------------------------------------------------------- 算例 19.2.3：速度限制
a_lim = 0.5                                       # 横向、切向加速度限制，m/s²（与算例 1.1.1 的制动减速度相同）
vmax_line = r * wmax                              # 直行最高车速
om_spin = 2 * r * wmax / b                        # 原地转动的最高角速度（轮速限制）
rho = 0.5                                         # 拐角圆弧半径，m
v_wheel_arc = r * wmax / (1 + b / (2 * rho))      # 轮速限制下圆弧上的最高车速
v_lat_arc = math.sqrt(a_lim * rho)                # 横向加速度限制下圆弧上的最高车速
v_arc = min(v_wheel_arc, v_lat_arc)
wo_arc = v_arc * (1 + b / (2 * rho)) / r          # 外侧轮转速
wi_arc = v_arc * (1 - b / (2 * rho)) / r
# 车上货物最远点（车台对角线的一半）在原地转动时的向心加速度不超过 a_lim
r_deck = math.hypot(P["length"], P["width"]) / 2
om_deck = math.sqrt(a_lim / r_deck)
alpha_spin = a_lim / r_deck                        # 车台最远点的切向加速度不超过 a_lim 时，原地转动的角加速度上限

# ---------------------------------------------------------------- 算例 19.2.4：数字工厂的真实路线
lay = factory()
W_f, D_f = lay.FLOOR
a_dock, b_dock = lay.dock("ht-01"), lay.dock("cnc-l01-b")
path_f = lay.route(a_dock, b_dock)                # 工厂坐标（y 向下）
L_poly = lay.length(path_f)
path = to_book(path_f, D_f)                       # 本章坐标（y 向上）
pts = np.array(path)
# 拐角的转角（逆时针为正）
turns = []
for k in range(1, len(pts) - 1):
    u, w = pts[k] - pts[k - 1], pts[k + 1] - pts[k]
    turns.append(math.degrees(math.atan2(u[0] * w[1] - u[1] * w[0], u @ w)))
segs = round_corners(path, rho)
L_round = sum(seg_len(s) for s in segs)
assert abs((L_poly - L_round) - len(turns) * (2 - math.pi / 2) * rho) < 1e-9

# (B) 圆弧过渡：沿弧长离散，ds = 1 mm；速度上限 v_lim(s)，再做正、反两遍，使 |dv/dt| ≤ a_lim、起止速度为零
pr = profile(segs, vmax_line, v_arc, a_lim)
S, v, KAP, XY, t_round = pr["S"], pr["v"], pr["kap"], pr["xy"], pr["T"]
tt = np.r_[0.0, pr["t"], t_round]
om_path = v * KAP
wR_path = (v + om_path * b / 2) / r
wL_path = (v - om_path * b / 2) / r
wmax_used = float(max(np.abs(wR_path).max(), np.abs(wL_path).max()))
assert wmax_used <= wmax + 1e-9
# 把轮速按时间重新采样（1 ms），用圆弧精确更新积分回去
hs = 1e-3
tq = np.arange(0, t_round, hs)
wR_t = np.interp(tq + hs / 2, np.r_[0.0, tt[1:-1], t_round], np.r_[0.0, wR_path, 0.0])
wL_t = np.interp(tq + hs / 2, np.r_[0.0, tt[1:-1], t_round], np.r_[0.0, wL_path, 0.0])
q = np.array([pts[0][0], pts[0][1], math.atan2(pts[1][1] - pts[0][1], pts[1][0] - pts[0][0])])
dev_max = 0.0
for k in range(len(tq)):
    Vk = np.array([r * (wR_t[k] - wL_t[k]) / b, r * (wR_t[k] + wL_t[k]) / 2, 0.0])
    q = step_exact(q, Vk, min(hs, t_round - tq[k]))
    if k % 50 == 0:                                            # 偏离路线的最大距离（每 50 ms 查一次）
        dev_max = max(dev_max, float(np.min(np.hypot(XY[:, 0] - q[0], XY[:, 1] - q[1]))))
end_err = float(np.hypot(q[0] - pts[-1][0], q[1] - pts[-1][1]))
end_head = math.degrees(math.atan2(math.sin(q[2] - math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0])),
                                   math.cos(q[2] - math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0]))))
assert end_err < 0.02 and abs(end_head) < 0.5

# (A) 停车、原地转向：每段直线从静止加速到 1.0 m/s 再减速到零；每个拐角原地转 90°
def trap_time(dist, vm, acc):
    if dist >= vm * vm / acc:
        return dist / vm + vm / acc
    return 2 * math.sqrt(dist / acc)


seg_lens = [math.dist(path[k], path[k + 1]) for k in range(len(path) - 1)]
t_lines = sum(trap_time(Ls, vmax_line, a_lim) for Ls in seg_lens)
om_s = min(om_deck, om_spin)
t_spin_one = trap_time(math.pi / 2, om_s, alpha_spin)
t_stop = t_lines + len(turns) * t_spin_one
t_sim = L_poly / vmax_line                         # 工厂仿真的算法：路线长度除以车速
v_mean = L_round / t_round

out(r=r, b=b, wmax=wmax, detJ=detJ, v1=v1, om1=om1, wR1=wR1, wL1=wL1, R1=R1,
    t2=t2, x2=q_closed[0], y2=q_closed[1], phi2_deg=math.degrees(q_closed[2]), err_euler=err_euler,
    xe=qe[0], ye=qe[1],
    a_lim=a_lim, vmax_line=vmax_line, om_spin=om_spin, rho=rho, v_wheel_arc=v_wheel_arc, v_lat_arc=v_lat_arc, v_arc=v_arc,
    wo_arc=wo_arc, wi_arc=wi_arc, r_deck=r_deck, om_deck=om_deck, alpha_spin=alpha_spin,
    a_dock=f"({a_dock[0]:g}, {a_dock[1]:g})", b_dock=f"({b_dock[0]:g}, {b_dock[1]:g})",
    path_f=", ".join(f"({x:g}, {y:g})" for x, y in path_f), path_b=", ".join(f"({x:g}, {y:g})" for x, y in path),
    n_turns=len(turns), turns="、".join(f"{t:+.0f}°".replace("-", "−") for t in turns), n_right=sum(1 for t in turns if t < 0),
    L_poly=L_poly, L_round=L_round, t_round=t_round, v_mean=v_mean, wmax_used=wmax_used, end_err_mm=end_err * 1000,
    end_head=end_head, dev_max_mm=dev_max * 1000, t_lines=t_lines, t_spin_one=t_spin_one, om_s=om_s, t_stop=t_stop,
    t_sim=t_sim, save=t_stop - t_round, over_pct=(t_round / t_sim - 1) * 100, n_seg=len(seg_lens), floor_d=D_f)
