"""13.4 节的计算：

算例 13.4.1  自行车轮陀螺：轮子质量 2.0 kg，绕自身轴的转动惯量 0.15 kg·m²，以 5.0 r/s 自转；轮轴一端用绳吊起，
            轮心离吊点 0.20 m，轮轴水平。进动角速度和周期多大？自转慢到多少时，“慢进动”的近似就不能用了？
算例 13.4.2  同一个轮子从“轮轴水平、静止不进动”的状态松手。数值积分重陀螺的运动方程，看轮轴怎样一边进动一边上下点头（章动），
            与近似公式比较（图 13.4.1）。轮轴对吊点的转动惯量（垂直于轮轴）取 0.155 kg·m²（绕质心 0.075 加 m d²）。
"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import T, figure, out, style
from constants import g
import _draw as d

m, J3, n, l = 2.0, 0.15, 5.0, 0.20
w3 = 2 * math.pi * n
L = J3 * w3
Mg = m * g * l
Om = Mg / L
out(m=m, J3=J3, n=n, l=l, w3=w3, L=L, Mg=Mg, Om=Om, Tp=2 * math.pi / Om, ratio=Om / w3)

# ---- 重对称陀螺：欧拉角 θ（轮轴与竖直向上的夹角）、φ（进动角），ω3 = ψ' + φ' cos θ 守恒
J1 = 0.075 + m * l ** 2
Lz0 = J3 * w3 * math.cos(math.pi / 2)                          # 初始 φ' = 0，θ = 90°


def rhs(t, y):
    th, thd, ph = y
    s, c = math.sin(th), math.cos(th)
    phd = (Lz0 - J3 * w3 * c) / (J1 * s * s)
    thdd = (J1 * phd ** 2 * s * c - J3 * w3 * phd * s + Mg * s) / J1
    return [thd, thdd, phd]


sol = solve_ivp(rhs, (0, 3.0), [math.pi / 2, 0.0, 0.0], rtol=1e-10, atol=1e-12, max_step=1e-3, dense_output=True)
tt = np.linspace(0, 3.0, 3001)
th, _, ph = sol.sol(tt)
dip = np.degrees(th.max() - math.pi / 2)                        # 轮轴最多“点头”多少度（向下）
dip_est = math.degrees(2 * J1 * Mg / (J3 * w3) ** 2)
wn = J3 * w3 / J1                                                # 章动角频率（快陀螺近似）
Om_avg = ph[-1] / tt[-1]
out(J1=J1, dip=dip, dip_est=dip_est, Tn=2 * math.pi / wn, Om_avg=Om_avg, Om_err=abs(Om_avg - Om) / Om)
assert abs(dip - dip_est) / dip_est < 0.05 and abs(Om_avg - Om) / Om < 0.05

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
ax.plot(np.degrees(ph), 90 - np.degrees(th), color=d.VA, lw=1.6, label=T("数值解：进动 + 章动", "numerical: precession + nutation"))
ax.axhline(-dip / 2, color=d.VR, lw=1.2, ls="--", label=T("平均高度（近似）", "mean height (approx.)"))
ax.set_xlabel(T("进动角 φ / (°)", "precession angle φ / (°)")); ax.set_ylabel(T("轮轴仰角 / (°)", "axle elevation / (°)"))
ax.set_ylim(-dip * 1.6, dip * 0.6); ax.legend(frameon=False, fontsize=8, loc="upper right"); d.spines(ax)
figure(fig, "fig13_4_1")
