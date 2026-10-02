"""34.2 节的计算：

图 34.2.1    楞次定律的四种情形：N 极靠近、N 极离开、S 极靠近、S 极离开时线圈中感应电流的方向；
算例 34.2.1  钕铁硼磁铁在铜管中下落：由测得的下落时间求末速度、阻力和管壁发热的功率，
             并用 m dv/dt = mg − bv 的模型画出速度随时间的变化（图 34.2.2）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 34.2.1（题目给定的测量数据）
m, L_tube, t_fall = 0.010, 1.00, 2.5        # 磁铁质量 kg、铜管长 m、实测下落时间 s
v_t = L_tube / t_fall                       # 近似：很快达到末速度
b = m * g / v_t                             # 阻力系数 F = b v
tau = m / b                                 # 达到末速度的时间常数
P = m * g * v_t                             # 匀速下落时，重力做功全部变成管壁的焦耳热
t_free = math.sqrt(2 * L_tube / g)
tt = np.linspace(0, 0.3, 601)
vv = v_t * (1 - np.exp(-tt / tau))
# 时间常数远小于下落时间，“很快达到末速度”的近似成立；用精确解核对下落时间
t_exact = L_tube / v_t + tau                # x(t) = v_t (t − τ(1 − e^{−t/τ}))，t ≫ τ 时
assert tau / t_fall < 0.02 and abs(t_exact - t_fall) / t_fall < 0.02

out(m_g=m * 1000, v_t=v_t, b=b, tau_ms=tau * 1000, P_mW=P * 1000, F=m * g, t_free=t_free, t_exact=t_exact)

plt = style()
# ---- 图 34.2.1：四种情形
fig, axs = plt.subplots(1, 4, figsize=(9.6, 2.9))
cases = [(True, True, T("N 极靠近", "N pole approaches")), (True, False, T("N 极离开", "N pole recedes")),
         (False, True, T("S 极靠近", "S pole approaches")), (False, False, T("S 极离开", "S pole recedes"))]
from matplotlib.patches import Ellipse
for ax, (north, approach, title) in zip(axs, cases):
    # 磁铁在左，线圈在右；磁铁朝向线圈的一端是 N（north=True）或 S
    d.magnet(ax, -0.55, 0, w=0.5, h=0.2, north_right=north)
    ax.add_patch(Ellipse((0.45, 0), 0.16, 0.9, fc="none", ec=d.CURR, lw=2.5))
    d.arrow(ax, -0.85 if approach else -0.45, -0.38, 0.3 if approach else -0.3, 0, d.INK, r"$\boldsymbol{v}$", off=(0.08 if approach else -0.08, 0.1))
    # 磁铁在线圈处的磁场：N 朝右 → B 向右；靠近 → Φ 增大 → 感应电流的磁场向左
    B_right = north
    grow = approach
    Bind_right = (not B_right) if grow else B_right
    d.arrow(ax, 0.3, 0.62, 0.3 if B_right else -0.3, 0, d.FIELD, r"$\boldsymbol{B}$", off=(0.12 if B_right else -0.12, 0))
    d.arrow(ax, 0.3, -0.62, 0.3 if Bind_right else -0.3, 0, d.EFIELD, r"$\boldsymbol{B}'$", off=(0.13 if Bind_right else -0.13, 0))
    # 从右往左看（沿 −x），B' 向右（朝向观察者）时电流逆时针
    ccw_from_right = Bind_right
    ax.text(0.45, -0.9, T("从右看：", "seen from right: ") + (T("逆时针", "CCW") if ccw_from_right else T("顺时针", "CW")),
            ha="center", fontsize=9, color=d.CURR)
    ax.set_title(title, fontsize=10)
    ax.set_xlim(-1.0, 0.95); ax.set_ylim(-1.05, 0.95)
    d.clean(ax)
fig.text(0.5, 0.01, T("B：磁铁在线圈处的磁场；B′：感应电流产生的磁场，总是阻碍线圈中磁通量的变化",
                      "B: the magnet's field at the coil; B′: the field of the induced current, always opposing the change of flux"),
         ha="center", fontsize=8.5, color=d.MUTED)
figure(fig, "fig34_2_1")

# ---- 图 34.2.2：铜管中的下落速度
fig, ax = plt.subplots(figsize=(5.4, 3.0))
ax.plot(tt * 1000, vv, color=d.FORCE, lw=2, label=T("铜管中", "in the copper tube"))
ax.plot(tt * 1000, g * tt, color=d.MUTED, lw=1.5, ls="--", label=T("自由下落", "free fall"))
ax.axhline(v_t, color=d.FORCE, lw=0.8, ls=":")
ax.text(200, v_t + 0.05, T("末速度", "terminal speed") + f" {v_t:.2f} m/s", fontsize=9, color=d.FORCE)
ax.set_xlabel(T("时间 $t$ / ms", "time $t$ / ms")); ax.set_ylabel(T("速度 $v$ / (m/s)", "speed $v$ / (m/s)"))
ax.set_ylim(0, 1.0); ax.set_xlim(0, 300); ax.legend(frameon=False, loc="lower right"); d.spines(ax)
figure(fig, "fig34_2_2")
