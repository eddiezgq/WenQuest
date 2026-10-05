"""8.4 节的计算：

算例 8.4.1  仍用算例 8.1.1 的网球。欧拉法、半隐式欧拉法、中点法（二阶 RK）、四阶 RK 四种方法，步长从 0.1 s 到 0.0005 s，
            落地点误差与步长的关系，各是几阶？要求落地点误差不超过 1 mm，各需多大的步长、计算多少次加速度（RK4 另试 0.2、0.3、0.5 s 的大步长，插值求出）（图 8.4.1）？
            再用自适应步长的 RK45（scipy 的 solve_ivp）求同一个问题，比较计算次数。
"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import T, figure, out, style
import _draw as d
from _ball import landing, f, S0

Xref = landing(1e-4, "rk4")
hs = np.array([0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 0.0005])
hs4 = np.array([0.5, 0.3, 0.2, 0.1, 0.05])                       # RK4 另试几个大步长
cost = {"euler": 1, "semi": 1, "rk2": 2, "rk4": 4}
err = {m_: np.array([abs(landing(h, m_) - Xref) for h in hs]) for m_ in cost}
Tf = 1.0395                                                   # 飞行时间约 1.04 s（算例 8.1.1）
res = {}
for m_, e in err.items():
    ok = e > 0
    p = np.polyfit(np.log(hs[ok][-5:] if m_ == "rk4" else hs[ok]), np.log(e[ok][-5:] if m_ == "rk4" else e[ok]), 1)
    order = p[0] if m_ != "rk4" else np.polyfit(np.log(hs[:4]), np.log(e[:4]), 1)[0]
    if m_ == "rk4":                                         # 在大步长处对数插值，求误差恰为 1 mm 的步长
        e4 = np.array([abs(landing(h, "rk4") - Xref) for h in hs4])
        h1 = math.exp(np.interp(math.log(1e-3), np.log(e4[::-1]), np.log(hs4[::-1])))
    else:
        h1 = math.exp((math.log(1e-3) - p[1]) / p[0])
    res[m_] = (order, h1, cost[m_] * math.ceil(Tf / h1))
out(**{f"ord_{k}": v[0] for k, v in res.items()}, **{f"h1mm_{k}": v[1] for k, v in res.items()}, **{f"nf_{k}": v[2] for k, v in res.items()},
    e_rk4_01=err["rk4"][0], e_euler_01=err["euler"][0], e_rk4_001=err["rk4"][3],
    e_rk4_05_mm=1000 * abs(landing(0.5, "rk4") - Xref), e_rk4_02_mm=1000 * abs(landing(0.2, "rk4") - Xref), e_rk4_03_mm=1000 * abs(landing(0.3, "rk4") - Xref))


def hit(t, s): return s[1]
hit.terminal, hit.direction = True, -1
sol = solve_ivp(f, (0, 3), S0, method="RK45", rtol=1e-6, atol=1e-9, events=hit)
out(nfev45=sol.nfev, X45=sol.y_events[0][0][0], e45=abs(sol.y_events[0][0][0] - Xref), nstep45=len(sol.t) - 1)

plt = style()
fig, ax = plt.subplots(figsize=(5.0, 3.3))
for m_, col, name in (("euler", d.VR, T("欧拉法", "Euler")), ("semi", d.MUTED, T("半隐式欧拉法", "semi-implicit Euler")),
                      ("rk2", d.VB, T("中点法（RK2）", "midpoint (RK2)")), ("rk4", d.VA, "RK4")):
    ok = err[m_] > 1e-12
    ax.loglog(cost[m_] * Tf / hs[ok], err[m_][ok], "o-", color=col, lw=1.6, ms=3.5, label=name)
ax.axhline(1e-3, color=d.INK, lw=0.8, ls=":"); ax.text(12, 1.3e-3, "1 mm", fontsize=8.5)
ax.set_xlabel(T("计算加速度的次数", "evaluations of the acceleration")); ax.set_ylabel(T("落地点误差 / m", "landing error / m"))
ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
figure(fig, "fig8_4_1")
