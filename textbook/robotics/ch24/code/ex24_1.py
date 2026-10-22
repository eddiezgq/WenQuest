"""24.1 节的计算：广义坐标与拉格朗日方程。

(1) 算例 24.1.1：秋千（示意值：绳长 2.5 m，人连座板 30 kg，看作单摆，不计绳的质量和空气阻力）。
    拉格朗日方程 φ̈ = −(𝔤/l) sin φ；小摆角周期 2π√(l/𝔤)；摆幅 60° 的周期（第一类完全椭圆积分，与 RK4 积分核对）；
    最低点的绳拉力 m𝔤(3 − 2 cos φ₀)：拉格朗日方程里没有拉力，要另求。两种求法核对：
    (a) 沿绳方向的牛顿第二定律；(b) 用直角坐标和拉格朗日乘子写约束方程，乘子就是拉力（8.2 节）；
    再与 MuJoCo 的约束力（mj_rnePostConstraint 给出的 cfrc_int）核对。
(2) 算例 24.1.2：桁架小车吊运（示意值：小车 50 kg，吊重 20 kg，吊绳 1.0 m）。广义坐标 (x, φ)，两个方程；
    线性化后的摆动周期；小车以 0.5 m/s² 匀加速 t_a 秒后匀速：残留摆幅的线性预测 (2a/𝔤)|sin(ω t_a/2)|，
    与非线性方程的数值解比较；t_a 取摆动周期时不残留摆动。由第一个方程算出小车电机要出的力，
    把这个力加到 MuJoCo 的小车-摆模型上（滑动关节 + 转动关节），小车和吊重的运动与本程序的解一致。
(3) 算例 24.1.3：UR5e 只转关节 2（其余关节锁住，小臂伸直，装夹爪 + 毛坯）：J φ̈ + m𝔤d cos φ = τ，
    J、m、d 由 24.2 节的等效参数得到；与式 (23.3.6) 一致。
(4) 习题答案。
"""
import math

import numpy as np
from scipy.special import ellipk

from _ch24 import G0, mj_load, mjcf_text, parse_links, payload_parts, planar_params, rk4_step
from bookout import out

# ---------------------------------------------------------------- (1) 秋千
l_s, m_s, ph0 = 2.5, 30.0, math.radians(60)
T0_s = 2 * math.pi * math.sqrt(l_s / G0)
k = math.sin(ph0 / 2)
T60 = 4 * math.sqrt(l_s / G0) * ellipk(k * k)                       # scipy 的 ellipk 以 m = k² 为参数
ratio60 = T60 / T0_s


def swing_rhs(x):
    return np.array([x[1], -G0 / l_s * math.sin(x[0])])


# RK4：从 60° 静止释放，找第一次回到 60° 的时刻（半周期 = 第一次 φ̇ 由负变正的时刻）
x, h, tt = np.array([ph0, 0.0]), 1e-4, 0.0
while True:
    xn = rk4_step(swing_rhs, x, h)
    if x[1] < 0 <= xn[1]:
        T60_num = 2 * (tt + h * (-x[1]) / (xn[1] - x[1]))
        break
    x, tt = xn, tt + h
assert abs(T60_num - T60) < 1e-6
# 最低点：v² = 2𝔤l(1 − cos φ₀)；沿绳 T − m𝔤 = m v²/l
v_bot = math.sqrt(2 * G0 * l_s * (1 - math.cos(ph0)))
Tn_newton = m_s * G0 + m_s * v_bot ** 2 / l_s
Tn = m_s * G0 * (3 - 2 * math.cos(ph0))
assert abs(Tn - Tn_newton) < 1e-9
# 拉格朗日乘子：直角坐标 (X, Y)，约束 ψ = (X² + Y² − l²)/2 = 0；m Ẍ = −λX，m Ÿ = −m𝔤 − λY；拉力 = λ l
# 由约束的二阶导数 X Ẍ + Y Ÿ + Ẋ² + Ẏ² = 0 解出 λ = m(Ẋ² + Ẏ² − 𝔤Y)/l²
X, Y, Xd, Yd = 0.0, -l_s, v_bot, 0.0                                   # 最低点
lam = m_s * (Xd ** 2 + Yd ** 2 - G0 * Y) / l_s ** 2
assert abs(lam * l_s - Tn) < 1e-9
# MuJoCo：一个转动关节吊着质点，从 60° 释放，最低点时关节对摆的约束力
import mujoco                                                           # noqa: E402

xml_s = f"""<mujoco><option timestep="0.0001" integrator="RK4"><flag contact="disable"/></option>
<worldbody><body name="seat" pos="0 0 0"><joint name="rope" type="hinge" axis="0 1 0"/>
<geom type="sphere" size="0.05" pos="0 0 {-l_s}" mass="{m_s}"/></body></worldbody></mujoco>"""
mj, ms, ds = mj_load(xml_s)
ms.geom_size[0][0] = 0.05
ds.qpos[0] = ph0
T_mj = None
prev = ds.qpos[0]
for _ in range(200000):
    mj.mj_step(ms, ds)
    if prev > 0 >= ds.qpos[0]:                                          # 过最低点
        mj.mj_rnePostConstraint(ms, ds)
        T_mj = float(np.linalg.norm(ds.cfrc_int[1][3:]))               # body 1 受父体的力（力在后三个分量）
        w_bot = abs(ds.qvel[0])
        break
    prev = ds.qpos[0]
# 球的转动惯量很小但不为零：用 MuJoCo 的实际惯量算出最低点拉力的理论值再比较
J_s = ms.body_inertia[1][1] + m_s * l_s ** 2
assert abs(w_bot - math.sqrt(2 * m_s * G0 * l_s * (1 - math.cos(ph0)) / J_s)) < 1e-3
T_mj_theory = m_s * G0 + m_s * l_s * w_bot ** 2
err_T_mj = abs(T_mj - T_mj_theory) / T_mj_theory
assert err_T_mj < 1e-3

# ---------------------------------------------------------------- (2) 桁架小车吊运
Mc, mL, lc, acc = 50.0, 20.0, 1.0, 0.5
w_c = math.sqrt(G0 / lc)
Tp = 2 * math.pi / w_c


def cart_profile(t, ta, T_end):
    """小车加速度：0～t_a 匀加速 a，之后匀速（只看一次起动）。"""
    return acc if t < ta else 0.0


def phi_rhs(ta):
    """小车按给定的加速度运动时，吊重的方程（第二个拉格朗日方程）：l φ̈ + ẍ cos φ + 𝔤 sin φ = 0。状态 (x, ẋ, φ, φ̇, t)。"""
    def f(s):
        a = cart_profile(s[4], ta, None)
        return np.array([s[1], a, s[3], -(a * math.cos(s[2]) + G0 * math.sin(s[2])) / lc, 1.0])
    return f


def run_cart(ta, T=8.0, h=1e-3):
    s = np.zeros(5)
    n = int(round(T / h))
    S = np.zeros((n + 1, 5))
    S[0] = s
    for i in range(n):
        # 加速段结束的时刻落在步长的整数倍上，避免跨过间断点
        s = rk4_step(phi_rhs(ta), s, h)
        S[i + 1] = s
    return S


def residual(S, ta, h=1e-3):
    """加速结束后的摆幅：由能量 ½l²φ̇² + 𝔤l(1 − cos φ) 换算成等效摆角。"""
    i0 = int(round(ta / h)) + 1
    E = 0.5 * lc ** 2 * S[i0:, 3] ** 2 + G0 * lc * (1 - np.cos(S[i0:, 2]))
    return float(np.arccos(1 - E.max() / (G0 * lc)))


def lin_residual(ta):
    return 2 * acc / G0 * abs(math.sin(w_c * ta / 2))


ta_half = round(Tp / 2, 3)
ta_full = round(Tp, 3)
S_half = run_cart(ta_half)
S_full = run_cart(ta_full)
res_half, res_full = residual(S_half, ta_half), residual(S_full, ta_full)
lin_half, lin_full = lin_residual(ta_half), lin_residual(ta_full)
assert abs(res_half - lin_half) / lin_half < 0.01 and res_full < 2e-3
max_swing_full = float(np.abs(S_full[: int(round(ta_full / 1e-3)) + 1, 2]).max())     # 加速过程中的最大摆角
assert abs(max_swing_full - 2 * acc / G0) < 1e-3                                     # 线性预测：加速时摆角在 0～2a/𝔤 之间

# 第一个拉格朗日方程给出小车电机的力：F = (M + m)ẍ + m l (φ̈ cos φ − φ̇² sin φ)
def cart_force(S, ta, h=1e-3):
    F = np.zeros(len(S))
    f = phi_rhs(ta)
    for i, s in enumerate(S):
        a = cart_profile(s[4], ta, None)
        pdd = f(s)[3]
        F[i] = (Mc + mL) * a + mL * lc * (pdd * math.cos(s[2]) - s[3] ** 2 * math.sin(s[2]))
    return F


F_full = cart_force(S_full, ta_full)
F_peak = float(np.abs(F_full).max())
i_ta = int(round(ta_full / 1e-3))
F_acc = F_full[:i_ta + 1]
F_min_acc, F_max_acc = float(F_acc.min()), float(F_acc.max())
t_Fmax = float(np.argmax(F_acc) * 1e-3)
assert abs(F_max_acc - F_peak) < 1e-9
F_rigid = (Mc + mL) * acc
# MuJoCo：小车（滑动关节）+ 吊重（转动关节，质点），把上面的力加到小车上
xml_c = f"""<mujoco><option timestep="0.001" integrator="RK4" gravity="0 0 {-G0}"><flag contact="disable"/></option>
<worldbody><body name="cart"><joint name="x" type="slide" axis="1 0 0"/><geom type="box" size="0.1 0.1 0.05" mass="{Mc}"/>
<body name="load"><joint name="phi" type="hinge" axis="0 -1 0"/>
<geom type="sphere" size="0.01" pos="0 0 {-lc}" mass="{mL}"/></body></body></worldbody>
<actuator><motor joint="x" gear="1"/></actuator></mujoco>"""
mj, mc_, dc = mj_load(xml_c)
# 质点的转动惯量设为零（与本程序的质点模型一致）
mc_.body_inertia[2][:] = 0
err_cart = err_phi = 0.0
for i in range(len(S_full) - 1):
    dc.ctrl[0] = 0.5 * (F_full[i] + F_full[i + 1])                      # 一步内力取常数（两端的平均）：与连续变化的力差 O(h²)
    mj.mj_step(mc_, dc)
    err_cart = max(err_cart, abs(dc.qpos[0] - S_full[i + 1, 0]))
    err_phi = max(err_phi, abs(dc.qpos[1] - S_full[i + 1, 2]))
assert err_cart < 1e-3 and err_phi < 1e-4                              # 力在一步内取常数造成的差

# ---------------------------------------------------------------- (3) UR5e 只转关节 2
links = parse_links(mjcf_text())
PL = planar_params(links, payload=payload_parts())
J_j2 = float(PL.M(np.zeros(2))[0, 0])                                  # 小臂伸直（φ₂ = 0）时 M₁₁，含转子惯量
md = PL.m1 * PL.r1 + PL.m2 * (PL.a1 + PL.r2)                            # 关节 2 以外的质量 × 质心到轴的距离
m_out = PL.m1 + PL.m2
d_out = md / m_out
tau_hold = G0 * md                                                     # 水平伸直时的重力矩
assert abs(tau_hold - PL.g(np.zeros(2))[0]) < 1e-12
alpha_free = tau_hold / J_j2                                           # 水平位置突然断电（τ = 0）时的角加速度

# ---------------------------------------------------------------- (4) 习题答案
# 24.1.3：绳长 2.5 m 的秋千，最低点速度 3 m/s 时的拉力（30 kg）
T_ex = m_s * G0 + m_s * 3.0 ** 2 / l_s
# 24.1.5：桁架吊运的加速时间取 1.5 个周期时的残留摆幅（线性）
lin_15 = lin_residual(1.5 * Tp)

out(l_s=l_s, m_s=m_s, T0_s=T0_s, T60=T60, ratio60=ratio60, ratio60_pct=(ratio60 - 1) * 100, T60_num=T60_num, v_bot=v_bot, Tn=Tn, Tn_ratio=Tn / (m_s * G0),
    lam=lam, T_mj=T_mj, err_T_mj=err_T_mj,
    Mc=Mc, mL=mL, lc=lc, acc=acc, Tp=Tp, ta_half=ta_half, ta_full=ta_full, res_half_deg=math.degrees(res_half),
    lin_half_deg=math.degrees(lin_half), res_full_deg=math.degrees(res_full), max_swing_deg=math.degrees(max_swing_full),
    F_peak=F_peak, F_rigid=F_rigid, F_min_acc=F_min_acc, t_Fmax=t_Fmax, err_cart=err_cart, err_phi=err_phi,
    J_j2=J_j2, m_out=m_out, d_out=d_out, tau_hold=tau_hold, alpha_free=alpha_free,
    T_ex=T_ex, lin_15_deg=math.degrees(lin_15))
