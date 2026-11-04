"""17.2 节的计算：

算例 17.2.1  仓储机器人的剪叉式顶升机构：两根长 0.50 m 的杆交叉铰接成 X 形，下端一个铰支、一个由丝杠推着水平滑动，
            平台上货架连同货物 500 kg。杆与水平方向的夹角为 θ 时，丝杠要推多大的力？丝杠导程 5.0 mm，电机经丝杠要出多大的力矩？
            （不计摩擦和杆的重量；用虚功原理；图 17.2.1）
算例 17.2.2  用虚功原理求两连杆机械臂的关节静力矩（参数同算例 14.1.2）：重力的广义力由势能对关节角求偏导，
            负载的那一份由 τ = −JᵀF 求出。大臂与水平方向成 30°、小臂相对大臂转过 −50° 时，与第 14 章“切开取矩”的结果核对；
            末端再水平向前推工件 20 N 时，两个关节的力矩各要增加多少？
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 17.2.1：剪叉式顶升。高 h = ℓ sinθ，滑动端到铰支端的距离 x = ℓ cosθ。
ell, M, lead = 0.50, 500.0, 5.0e-3
W = M * g


def push(theta):
    """虚功原理：F(−δx) − mg δh = 0（丝杠推滑动端靠近铰支端时 δx < 0），δh/(−δx) = cotθ。"""
    return W / math.tan(theta)


# 用数值的虚位移核对：给 θ 一个小增量，看两边的功是否相等
for th_deg in (10, 25, 40):
    th = math.radians(th_deg); e = 1e-7
    dh = ell * (math.sin(th + e) - math.sin(th - e)) / 2
    dx = ell * (math.cos(th + e) - math.cos(th - e)) / 2
    assert abs(push(th) * (-dx) - W * dh) < 1e-6 * W * abs(dh)
th10, th40 = math.radians(10), math.radians(40)
out(W=W, F10=push(th10), F40=push(th40), h10=ell * math.sin(th10), h40=ell * math.sin(th40),
    tq10=push(th10) * lead / (2 * math.pi), tq40=push(th40) * lead / (2 * math.pi))

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
th = np.radians(np.linspace(6, 50, 200))
ax.plot(ell * np.sin(th) * 100, W / np.tan(th) / 1000, color=d.VR, lw=2)
ax.axhline(W / 1000, color=d.MUTED, lw=0.8, ls="--")
ax.text(14, W / 1000 - 2.6, T("负载的重力 mg", "the load's weight mg"), fontsize=8.5, color=d.MUTED)
for thd in (10, 40):
    t = math.radians(thd)
    ax.plot([ell * math.sin(t) * 100], [W / math.tan(t) / 1000], "o", color=d.VR, ms=5)
    ax.annotate(f"θ = {thd}°", (ell * math.sin(t) * 100, W / math.tan(t) / 1000), xytext=(8, 4), textcoords="offset points", fontsize=8.5)
ax.set_xlabel(T("平台高度 h / cm", "platform height h / cm")); ax.set_ylabel(T("丝杠推力 F / kN", "screw force F / kN"))
ax.set_ylim(0, 50)
ax.set_title(T("F = mg cot θ：平台越低，丝杠越费力", "F = mg cot θ: the lower the platform, the harder the screw works"), fontsize=9)
d.spines(ax)
figure(fig, "fig17_2_1")

# ---- 算例 17.2.2：两连杆机械臂（q₁ 是大臂与水平方向的夹角，q₂ 是小臂相对大臂的转角）
m1, c1, L1 = 8.4, 0.21, 0.425
m2, c2, L2 = 2.3, 0.196, 0.392
mp = 5.0


def V(q):
    """两根连杆的重力势能（不含负载）。"""
    q1, q2 = q
    return g * (m1 * c1 * math.sin(q1) + m2 * (L1 * math.sin(q1) + c2 * math.sin(q1 + q2)))


def J(q):
    """末端位置对关节角的雅可比矩阵 ∂(x, y)/∂(q₁, q₂)。"""
    q1, q2 = q
    return np.array([[-L1 * math.sin(q1) - L2 * math.sin(q1 + q2), -L2 * math.sin(q1 + q2)],
                     [L1 * math.cos(q1) + L2 * math.cos(q1 + q2), L2 * math.cos(q1 + q2)]])


def grad(f, q, e=1e-6):
    return np.array([(f(q + e * np.eye(2)[k]) - f(q - e * np.eye(2)[k])) / (2 * e) for k in range(2)])


q = np.radians([30.0, -50.0])
F_load = np.array([0.0, -mp * g])                      # 负载对末端的力
tau_links = grad(V, q)                                 # 平衡：τ + Q = 0，重力的广义力 Q = −∂V/∂q
tau_load = -J(q).T @ F_load
tau = tau_links + tau_load

# 第 14 章的办法：切开取矩（φ₁ = q₁，φ₂ = q₁ + q₂ 是两根连杆与水平方向的夹角）
p1, p2 = q[0], q[0] + q[1]
Me = g * (m2 * c2 * math.cos(p2) + mp * L2 * math.cos(p2))
Ms = g * (m1 * c1 * math.cos(p1) + m2 * (L1 * math.cos(p1) + c2 * math.cos(p2)) + mp * (L1 * math.cos(p1) + L2 * math.cos(p2)))
assert abs(tau[0] - Ms) < 1e-6 and abs(tau[1] - Me) < 1e-6

F_push = np.array([20.0, 0.0])                         # 末端推工件的力；工件对末端的力是 −F_push
dtau = J(q).T @ F_push
out(tau_s=tau[0], tau_e=tau[1], tl_s=tau_load[0], tl_e=tau_load[1], dtau_s_less=-dtau[0], dtau_e=dtau[1])
assert dtau[0] < 0 < dtau[1]
