"""28.1 节的计算：轮式动力学与打滑。

牵引式 AGV（19.4 节，L = 1.2 m，w = 0.8 m）满载 800 kg，质心离前轴 0.65 m、离地 0.65 m，轮胎侧偏刚度每轴 20 kN/rad（示意值）。
(1) 算例 28.1.1：后轮驱动的最大加速度与只用后轮制动的最大减速度（计入载荷转移），四轮制动；干（μ = 0.7）、湿（μ = 0.4）地面；
    从最高车速 2 m/s 停下的距离（含 0.1 s 反应时间）。
(2) 算例 28.1.2：半径 R = 3 m 的弯道（后轴中点），侧滑与侧翻的极限侧向加速度 μ𝔤、𝔤w/(2h)，对应的车速；临界质心高度 h* = w/(2μ)。
    MuJoCo 中让 AGV 沿圆周匀速行驶，核对内侧车轮的法向力 m𝔤/2 − m a_y h/w；湿地面上缓慢加速，侧向加速度的最大值与 μ𝔤 比较；
    干地面上在 4.3 m/s 与 4.4 m/s 之间侧翻。
(3) 算例 28.1.3：2 m/s 通过 R = 3 m 的弯道，转向角取运动学值 arctan(L/R)，线性自行车模型的稳态：前、后轮侧偏角，后轴的侧滑速度，
    转过 90° 积累的位置偏差。
(4) 算例 28.1.4：轿车（生活例子）的不足转向度 K、特征车速；100 km/h 过 R = 200 m 的弯所需的转向角；阶跃转向的响应（图 28.1.2）。
"""
import math

import numpy as np

from _ch28 import AGV, CAR, G, MU_DRY, MU_WET, agv_circle, axle_loads, bicycle_rhs, bicycle_steady, understeer_K
from bookout import out

P = AGV
m, L, w, a, b, h = P["m"], P["L"], P["w"], P["a"], P["b"], P["h"]
Fzf0, Fzr0 = axle_loads(P)
out(m=m, L=L, w=w, lf=a, lr=b, h=h, Iz=P["Iz"], Cf_kN=P["Cf"] / 1e3, Fzr_share=Fzr0 / (m * G) * 100, v_max=P["v_max"],
    mu_dry=MU_DRY, mu_wet=MU_WET)

# ---------------------------------------------------------------- (1) 加速与制动
T_REACT = 0.1


def acc_rear(mu):
    return mu * G * a / (L - mu * h)          # 后轮驱动：F_x = μ F_zr，F_zr = m(𝔤a + ẍh)/L


def brake_rear(mu):
    return mu * G * a / (L + mu * h)          # 只用后轮制动：载荷移向前轴


def stop_dist(dec, v=P["v_max"]):
    return v * T_REACT + v * v / (2 * dec)


acc_dry, acc_wet = acc_rear(MU_DRY), acc_rear(MU_WET)
acc_dry_nt = MU_DRY * G * a / L               # 不计载荷转移
br_dry, br_wet = brake_rear(MU_DRY), brake_rear(MU_WET)
br4_dry, br4_wet = MU_DRY * G, MU_WET * G
Fzr_acc = axle_loads(P, acc_dry)[1]
out(acc_dry=acc_dry, acc_wet=acc_wet, acc_dry_nt=acc_dry_nt, br_dry=br_dry, br_wet=br_wet, br4_dry=br4_dry, br4_wet=br4_wet,
    Fzr_acc_share=Fzr_acc / (m * G) * 100, s_br_dry=stop_dist(br_dry), s_br_wet=stop_dist(br_wet),
    s_br4_dry=stop_dist(br4_dry), s_br4_wet=stop_dist(br4_wet), t_react=T_REACT)
# 制动时向前翻倒的减速度：前轴为支点，𝔤 a/h
out(dec_pitch=G * a / h)

# ---------------------------------------------------------------- (2) 侧滑与侧翻
R = 3.0
a_tip = G * w / (2 * h)
R_com = math.hypot(R, b)                       # 质心的转弯半径（后轴中点走半径 R 的圆）
v_of_ay = lambda ay: R * math.sqrt(ay / R_com)  # noqa: E731  后轴中点的车速：质心的向心加速度 (v/R)² R_com = a_y
v_tip = v_of_ay(a_tip)
v_skid_dry, v_skid_wet = v_of_ay(MU_DRY * G), v_of_ay(MU_WET * G)
h_star = w / (2 * MU_DRY)
out(R=R, a_tip=a_tip, a_skid_dry=MU_DRY * G, a_skid_wet=MU_WET * G, v_tip=v_tip, v_skid_dry=v_skid_dry, v_skid_wet=v_skid_wet,
    h_star=h_star, ssf=w / (2 * h))

# MuJoCo：匀速转圈，核对载荷转移
mj = {}
for v in (2.0, 3.0, 4.0):
    _, _, ay, inner, slip, hc = agv_circle(MU_DRY, lambda t, v=v: v, R=R, T=6.0)
    pred = m * G / 2 - m * ay * hc / w
    mj[v] = (ay, inner, pred, slip)
    assert abs((m * G / 2 - inner) / (m * G / 2 - pred) - 1) < 0.03     # 载荷转移量相差不到 3%
out(mj_ay2=mj[2.0][0], mj_in2=mj[2.0][1], mj_pr2=mj[2.0][2], mj_ay4=mj[4.0][0], mj_in4=mj[4.0][1], mj_pr4=mj[4.0][2],
    mj_ay3=mj[3.0][0], mj_in3=mj[3.0][1], mj_pr3=mj[3.0][2], mj_slip4_cm=mj[4.0][3] * 100,
    mj_dT4=(m * G / 2 - mj[4.0][1]) / (m * G / 2 - mj[4.0][2]) * 100 - 100,
    mj_dT4_abs=abs((m * G / 2 - mj[4.0][1]) / (m * G / 2 - mj[4.0][2]) * 100 - 100))
# 干地面：4.3 m/s 仍四轮着地，4.4 m/s 翻车
r43 = agv_circle(MU_DRY, lambda t: 4.3, R=R, T=8.0)
r44 = agv_circle(MU_DRY, lambda t: 4.4, R=R, T=8.0)
assert r43[3] > 100 and r43[5] > 0.6 and r44[5] < 0.3
out(mj_in43=r43[3], mj_ay43=r43[2])
# 湿地面：从 2.5 m/s 每秒加 0.05 m/s，0.5 s 平均的侧向加速度的最大值
recs = []
agv_circle(MU_WET, lambda t: 2.5 + 0.05 * max(t - 3, 0), R=R, T=33.0, stop=lambda r: recs.append(r) or False)
rr = np.array(recs)
k = 50
ma = np.convolve(rr[:, 2], np.ones(k) / k, "valid")
mj_ay_wet = float(ma.max())
assert abs(mj_ay_wet / (MU_WET * G) - 1) < 0.02
out(mj_ay_wet=mj_ay_wet)

# ---------------------------------------------------------------- (3) 侧偏角与里程计的横向偏差
v3 = 2.0
delta3 = math.atan(L / R)                       # 运动学（式 (19.4.4)）给的虚拟前轮转角
# 转向角不小（21.8°），不用线性化的稳态公式，直接解式 (28.1.9)（侧偏角取 arctan、前轮侧向力乘 cos δ，轮胎仍按线性）的稳态
from scipy.optimize import fsolve  # noqa: E402
x3 = fsolve(lambda x: bicycle_rhs(P, x, delta3, v3)[0], [b * v3 / R, v3 / R], xtol=1e-14)
vy3, r3 = x3
_, af3, ar3, _, _ = bicycle_rhs(P, x3, delta3, v3)
vy_rear = vy3 - b * r3                           # 后轴中点的侧向速度（负为向外）
# 后轴的侧滑速度在车身坐标系中不变，方向随车身转动：转过 90° 积累的位置偏差 |∫R(φ)(0, v_y)dt| = √2 |v_y|/ω
drift90 = math.sqrt(2) * abs(vy_rear) / r3
K_agv = understeer_K(P)
Fyr3 = P["Cr"] * ar3
out(v3=v3, delta3_deg=math.degrees(delta3), af3_deg=math.degrees(af3), ar3_deg=math.degrees(ar3), r3=r3, r3_kin=v3 / R,
    vy_rear_cm=abs(vy_rear) * 100, drift90_cm=drift90 * 100, K_agv_deg=math.degrees(K_agv * G), Fyr3=Fyr3,
    ay3=v3 * r3, R3_act=v3 / r3)

# ---------------------------------------------------------------- (4) 轿车：不足转向
C = CAR
K = understeer_K(C)
v_ch = math.sqrt(C["L"] / K)
v4, R4 = 100 / 3.6, 200.0
ay4 = v4 * v4 / R4
d_kin = C["L"] / R4
d_dyn = d_kin + K * ay4
out(car_m=C["m"], car_L=C["L"], car_a=C["a"], car_b=C["b"], car_Iz=C["Iz"], car_Cf_kN=C["Cf"] / 1e3, car_Cr_kN=C["Cr"] / 1e3,
    K_car=K, K_car_deg=math.degrees(K * G), v_ch=v_ch, v_ch_kmh=v_ch * 3.6, ay4=ay4, d_kin_deg=math.degrees(d_kin),
    d_dyn_deg=math.degrees(d_dyn), d_ratio=d_dyn / d_kin, R4_act=(C["L"] + K * v4 * v4) / d_kin)
# 线性模型的特征值（100 km/h）：两个稳定的实特征值或一对复特征值
_, A4, _ = bicycle_steady(C, d_kin, v4)
lam = np.linalg.eigvals(A4)
out(lam_re=float(max(lam.real)))
# 阶跃转向：转向角 1° 突加，100 km/h；横摆角速度的稳态值与运动学值之比（图 28.1.2 用）
d_step = math.radians(1.0)
xs, _, _ = bicycle_steady(C, d_step, v4)
r_ss = xs[1]
r_kin = v4 * math.tan(d_step) / C["L"]
out(r_ratio=r_ss / r_kin, r_ratio_formula=1 / (1 + K * v4 * v4 / C["L"]))
assert abs(r_ss / r_kin - 1 / (1 + K * v4 * v4 / C["L"])) < 2e-3
# 过度转向：把质心移到后面（a = 1.6 m，b = 1.1 m）后的临界车速
C2 = dict(C, a=1.6, b=1.1)
K2 = understeer_K(C2)
v_cr = math.sqrt(-C2["L"] / K2)
out(K2=K2, v_cr_kmh=v_cr * 3.6)


def step_response(P_, v, dsteer, T=2.0, dt=1e-3, mu=None):
    """阶跃转向的响应（RK4）。返回 t、横摆角速度 r、质心侧偏角 β = v_y/v。"""
    x = np.zeros(2)
    ts, rs, bs = [0.0], [0.0], [0.0]
    f = lambda x_: bicycle_rhs(P_, x_, dsteer, v, mu)[0]  # noqa: E731
    for i in range(int(T / dt)):
        k1 = f(x)
        k2 = f(x + dt / 2 * k1)
        k3 = f(x + dt / 2 * k2)
        k4 = f(x + dt * k3)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        ts.append((i + 1) * dt)
        rs.append(x[1])
        bs.append(x[0] / v)
    return np.array(ts), np.array(rs), np.array(bs)


t_s, r_s, _ = step_response(C, v4, d_step, T=3.0)
assert abs(r_s[-1] / r_ss - 1) < 1e-3
t63 = float(t_s[np.argmax(r_s >= 0.632 * r_ss)])
out(t63_ms=t63 * 1000)

# ---------------------------------------------------------------- 习题
# 28.1.1 前轮驱动（湿地面）的最大加速度：F_x = μF_zf，F_zf = m(𝔤 l_r − ẍ h)/L
acc_front_wet = MU_WET * G * b / (L + MU_WET * h)
# 28.1.2 货物堆高，质心升到 0.9 m：侧翻的侧向加速度与 R = 3 m 时的车速
h2 = 0.9
a_tip2 = G * w / (2 * h2)
out(acc_front_wet=acc_front_wet, h2=h2, a_tip2=a_tip2, v_tip2=v_of_ay(a_tip2))
# 28.1.4 轿车 60 km/h 过 R = 50 m 的弯：运动学转向角与所需转向角
v5, R5 = 60 / 3.6, 50.0
out(d5_kin_deg=math.degrees(C["L"] / R5), d5_deg=math.degrees(C["L"] / R5 + K * v5 * v5 / R5))
# 28.1.5 骑自行车 5 m/s 过半径 10 m 的弯，车身的倾角
out(lean_deg=math.degrees(math.atan(5.0 ** 2 / (G * 10.0))))
