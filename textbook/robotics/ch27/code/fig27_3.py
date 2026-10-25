"""27.3 节的示意图。

图 27.3.1：(a) 恢复系数与阻尼比 ζ：线性弹簧-阻尼的公式 e = exp(−πζ/√(1 − ζ²))、接触力降为零即分离时的数值解、MuJoCo 中球落地的实测值；
          (b) Ø10 mm 钢球以 1.40 m/s 撞钢板时的接触力：赫兹（完全弹性）、亨特-克罗斯利（e = 0.7）、
              同样 e 的线性弹簧-阻尼（刚度取与赫兹峰值相同的割线刚度），线性模型一碰上去力就跳变；
          (c) 恢复系数与撞击速度：线性模型的 e 不随速度变，亨特-克罗斯利（c 按 1 m/s 时 e = 0.8 选定）的 e 随速度增大而减小。
"""
import math

import numpy as np

from _ch27 import G0, RHO_STEEL, ball_xml, contact_ode, e_star, hertz_impact, kv_restitution_no_tension, mj_drop
from bookout import COLORS as C, T, figure, style

plt = style()
fig, axs = plt.subplots(1, 3, figsize=(13.2, 3.9))
ax = axs[0]
z = np.linspace(0.01, 0.8, 200)
ax.plot(z, np.exp(-math.pi * z / np.sqrt(1 - z * z)), color=C["z"], lw=1.8, label=T("线性公式", "linear formula"))
zz = np.linspace(0.02, 0.8, 30)
ax.plot(zz, [kv_restitution_no_tension(x) for x in zz], color=C["accent"], lw=1.6, ls="--", label=T("力为零即分离", "separate when force is zero"))
Zm = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7]
ax.plot(Zm, [mj_drop(ball_xml(solref=f"0.02 {x}", dt=1e-4))[0] for x in Zm], "o", color=C["x"], ms=6, label=T("MuJoCo 实测", "MuJoCo"))
ax.set_xlabel(T("阻尼比 ζ（solref 的第二个数）", "damping ratio ζ (second number of solref)"))
ax.set_ylabel(T("恢复系数 e", "coefficient of restitution e"))
ax.set_title(T("(a) 线性接触模型的恢复系数", "(a) restitution of a linear contact"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False)
ax.grid(alpha=0.25)
# (b) 力-时间
R = 0.005
m = RHO_STEEL * 4 / 3 * math.pi * R ** 3
v = math.sqrt(2 * G0 * 0.1)
K = 4 / 3 * e_star() * math.sqrt(R)
dmax, Fmax, tc = hertz_impact(m, R, v)
ax = axs[1]
_, _, _, (t0, d0, f0) = contact_ode(m, v, K, 1.5, 0.0, "hc", dt=1e-9, tmax=1e-3)
ax.plot(t0 * 1e6, f0, color=C["z"], lw=1.8, label=T("赫兹，e = 1", "Hertz, e = 1"))
e_t = 0.7
c = 8 * (1 - e_t) / (5 * e_t * v)
e_hc, _, _, (t1, d1, f1) = contact_ode(m, v, K, 1.5, c, "hc", dt=1e-9, tmax=1e-3)
ax.plot(t1 * 1e6, f1, color=C["accent"], lw=1.8, label=T(f"亨特-克罗斯利，e = {e_hc:.2f}", f"Hunt–Crossley, e = {e_hc:.2f}"))
k_lin = Fmax / dmax
zeta = -math.log(e_t) / math.sqrt(math.pi ** 2 + math.log(e_t) ** 2)
c_lin = 2 * zeta * math.sqrt(k_lin * m)
e_kv, _, _, (t2, d2, f2) = contact_ode(m, v, k_lin, 1.0, c_lin, "kv", dt=1e-9, tmax=1e-3)
ax.plot(t2 * 1e6, f2, color=C["x"], lw=1.5, ls="--", label=T(f"线性弹簧-阻尼，e = {e_kv:.2f}", f"linear spring-damper, e = {e_kv:.2f}"))
ax.set_xlabel(T("时间 / µs", "time / µs"))
ax.set_ylabel(T("接触力 / N", "contact force / N"))
ax.set_title(T("(b) Ø10 mm 钢球撞钢板（1.40 m/s）", "(b) Ø10 mm steel ball on steel (1.40 m/s)"), fontsize=11)
ax.legend(fontsize=8, frameon=False, loc="upper right")
ax.grid(alpha=0.25)
ax.set_xlim(0, 40)
# (c) e 与速度
ax = axs[2]
c_fix = 8 * (1 - 0.8) / (5 * 0.8 * 1.0)
vs = np.geomspace(0.05, 5, 14)
ax.semilogx(vs, [contact_ode(m, x, K, 1.5, c_fix, "hc", dt=min(2e-9, 1e-9 / x * 2), tmax=1e-3)[0] for x in vs], "o-", color=C["accent"], ms=4,
            label=T("亨特-克罗斯利（c 固定）", "Hunt–Crossley (fixed c)"))
ax.axhline(0.8, color=C["x"], lw=1.4, ls="--", label=T("线性弹簧-阻尼（ζ 固定）", "linear spring-damper (fixed ζ)"))
ax.set_xlabel(T("撞击速度 / (m/s)", "impact speed / (m/s)"))
ax.set_ylabel(T("恢复系数 e", "coefficient of restitution e"))
ax.set_title(T("(c) 恢复系数随撞击速度的变化", "(c) restitution against impact speed"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="lower left")
ax.grid(alpha=0.25, which="both")
ax.set_ylim(0, 1.05)
fig.tight_layout()
figure(fig, "fig27_3_1")
