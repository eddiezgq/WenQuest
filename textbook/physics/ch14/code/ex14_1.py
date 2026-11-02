"""14.1 节的计算：

算例 14.1.1  杠杆：长 1.00 m、质量 1.0 kg 的均匀杆，左端挂 6.0 kg，右端挂 2.0 kg。支点放在离左端 x 处，合力矩怎样随 x 变化？
            支点在哪里杆能平衡？平衡时支点受多大的力？分别对支点、对左端、对右端取矩核对（图 14.1.1）。
算例 14.1.2  机械臂静止持重：大臂 8.4 kg（质心离肩 0.21 m，长 0.425 m），小臂 2.3 kg（质心离肘 0.196 m，长 0.392 m），
            末端负载 5.0 kg。大臂与水平方向成 φ₁、小臂成 φ₂，求肩、肘两个关节的静力矩：先把小臂连同负载“切”下来求肘，
            再对整条臂求肩；并用“力矩 = 雅可比矩阵的转置 × 末端力”核对负载的那一份（图 14.1.2）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 14.1.1：杠杆
Lb, mb, mL, mR = 1.00, 1.0, 6.0, 2.0
Mnet = lambda x: g * (mL * x - mb * (Lb / 2 - x) - mR * (Lb - x))       # 绕支点，逆时针（左端向下）为正
x0 = (mb * Lb / 2 + mR * Lb) / (mL + mb + mR)                             # 合力矩为零：支点在整体重心下面
N = (mL + mb + mR) * g
assert abs(Mnet(x0)) < 1e-12
# 对左端取矩：支点的力 N 在 x0，向上；各重力向下
M_left = N * x0 - mb * g * Lb / 2 - mR * g * Lb
M_right = -N * (Lb - x0) + mL * g * Lb + mb * g * Lb / 2
assert abs(M_left) < 1e-9 and abs(M_right) < 1e-9
out(Lb=Lb, mb=mb, mL=mL, mR=mR, x0=x0, N=N, M_at_04=Mnet(0.40), M_at_02=Mnet(0.20))

# ---- 算例 14.1.2：两连杆机械臂的静力矩
m1, c1, L1 = 8.4, 0.21, 0.425
m2, c2, L2 = 2.3, 0.196, 0.392
mp = 5.0


def torques(p1, p2):
    """返回 (肩, 肘) 的静力矩（N·m，正值表示关节要向上托）。p1、p2 是大臂、小臂与水平方向的夹角。"""
    x_c2 = c2 * math.cos(p2); x_e = L2 * math.cos(p2)            # 从肘量起的水平距离
    Me = g * (m2 * x_c2 + mp * x_e)                               # 切下小臂和负载，对肘取矩
    xs1 = c1 * math.cos(p1); xe = L1 * math.cos(p1)               # 从肩量起
    Ms = g * (m1 * xs1 + m2 * (xe + x_c2) + mp * (xe + x_e))      # 整条臂对肩取矩
    return Ms, Me


Ms0, Me0 = torques(0.0, 0.0)
# 雅可比转置：末端受力 F = (0, −mp g)，τ = Jᵀ F 给出负载那一份（关节要出的力矩与之相反）
p1, p2 = math.radians(30), math.radians(-20)
J = np.array([[-L1 * math.sin(p1) - L2 * math.sin(p2), -L2 * math.sin(p2)],
              [L1 * math.cos(p1) + L2 * math.cos(p2), L2 * math.cos(p2)]])  # 以关节转角 q₁ = φ₁、q₂ = φ₂ − φ₁ 为坐标（不是绝对角）
tau_load = -(J.T @ np.array([0.0, -mp * g]))
Ms_a, Me_a = torques(p1, p2)
Ms_noload = g * (m1 * c1 * math.cos(p1) + m2 * (L1 * math.cos(p1) + c2 * math.cos(p2)))
Me_noload = g * m2 * c2 * math.cos(p2)
assert abs((Ms_a - Ms_noload) - tau_load[0]) < 1e-9 and abs((Me_a - Me_noload) - tau_load[1]) < 1e-9
out(Ms0=Ms0, Me0=Me0, Ms_a=Ms_a, Me_a=Me_a, tl_s=tau_load[0], tl_e=tau_load[1], frac_e=g * mp * L2 / Me0)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
xx = np.linspace(0, 1, 201)
ax.plot(xx, Mnet(xx), color=d.VR, lw=2)
ax.axhline(0, color=d.MUTED, lw=0.7); ax.axvline(x0, color=d.MUTED, lw=0.7, ls=":")
ax.plot(x0, 0, "o", color=d.VA, ms=6)
ax.text(x0 + 0.03, 6, T(f"平衡：x = {x0:.3f} m", f"balance: x = {x0:.3f} m"), fontsize=8.5)
ax.text(0.02, 8, T("右端下沉", "right end drops"), fontsize=8.5, color=d.MUTED)
ax.text(0.70, 18, T("左端下沉", "left end drops"), fontsize=8.5, color=d.MUTED)
ax.set_xlabel(T("支点离左端的距离 x / m", "fulcrum distance from left end x / m")); ax.set_ylabel(T("绕支点的合力矩 / (N·m)", "net torque about fulcrum / (N·m)"))
d.spines(ax)
figure(fig, "fig14_1_1")

fig, ax = plt.subplots(figsize=(4.8, 2.9))
ph = np.radians(np.linspace(-90, 90, 181))
for p2d, ls in ((0, "-"), (-45, "--")):
    lab_ = str(p2d).replace("-", "−")
    S_ = [torques(p, math.radians(p2d)) for p in ph]
    ax.plot(np.degrees(ph), [s_[0] for s_ in S_], color=d.VR, lw=1.8, ls=ls, label=T(f"肩（小臂 {lab_}°）", f"shoulder (forearm {lab_}°)"))
    ax.plot(np.degrees(ph), [s_[1] for s_ in S_], color=d.VA, lw=1.8, ls=ls, label=T(f"肘（小臂 {lab_}°）", f"elbow (forearm {lab_}°)"))
ax.set_xlabel(T("大臂与水平方向的夹角 φ₁ / (°)", "upper-arm angle φ₁ / (°)")); ax.set_ylabel(T("静力矩 / (N·m)", "static torque / (N·m)"))
ax.set_xlim(-90, 90); ax.set_xticks([-90, -45, 0, 45, 90]); ax.legend(frameon=False, fontsize=7.5, ncol=2, loc="upper center"); ax.set_ylim(-5, 90); d.spines(ax)
figure(fig, "fig14_1_2")
