"""图 19.7.1：左：RE 40 在两倍额定电流下的绕组温度，单节点模型与双节点模型；
右：带噪声的电机阶跃响应数据，以及 63.2% 点、切线、最小二乘得到的模型曲线。"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
R, Rth1, Rth2, tw, tm, Ta = 1.13, 4.65, 1.93, 41.5, 809.0, 25.0
P = (2 * 3.17) ** 2 * R
t = np.linspace(0, 600, 600)
a1.plot(t, Ta + P * (Rth1 + Rth2) * (1 - np.exp(-t / tm)), color=BLUE, lw=2, label=T("单节点（τ = 809 s）", "one node (τ = 809 s)"))
Cw, Ch = tw / Rth2, tm / Rth1
s = solve_ivp(lambda t, z: [(P - (z[0] - z[1]) / Rth2) / Cw, ((z[0] - z[1]) / Rth2 - (z[1] - Ta) / Rth1) / Ch], (0, 600), [Ta, Ta],
              t_eval=t, max_step=1.0)
a1.plot(t, s.y[0], color=RED, lw=2, label=T("双节点：绕组", "two nodes: winding"))
a1.plot(t, s.y[1], color=RED, lw=1.2, ls="--", label=T("双节点：外壳", "two nodes: housing"))
a1.axhline(155, color=MUTED, ls=":", lw=1)
a1.text(5, 160, T("绕组最高 155 °C", "winding limit 155 °C"), fontsize=9, color=MUTED)
a1.set_xlabel(T("时间 t / s", "time t / s"))
a1.set_ylabel(T("温度 / °C", "temperature / °C"))
a1.set_title(T("两倍额定电流：单节点模型偏于乐观", "Twice rated current: the one-node model is optimistic"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="lower right")
clean(a1, zero=False)
k, J, L, I0 = 60.3e-3, 137e-7, 0.33e-3, 68.6e-3
Tf = k * I0
rng = np.random.default_rng(19)
ts = np.arange(0, 0.03 + 1e-12, 0.25e-3)
s = solve_ivp(lambda t, z: [(k * z[1] - Tf) / J, (48 - R * z[1] - k * z[0]) / L], (0, 0.03), [0, 0], t_eval=ts, rtol=1e-9, atol=1e-9, max_step=2e-5)
wm = s.y[0] + 5.0 * rng.standard_normal(ts.size)
we = wm[ts > 0.025].mean()
j = int(np.argmax(wm > 0.632 * we))
t63 = ts[j - 1] + (0.632 * we - wm[j - 1]) / (wm[j] - wm[j - 1]) * (ts[j] - ts[j - 1])
sl = np.polyfit(ts[ts <= 1e-3], wm[ts <= 1e-3], 1)[0]
tls = minimize_scalar(lambda tau: np.sum((wm - we * (1 - np.exp(-ts / tau))) ** 2), bounds=(1e-3, 0.02), method="bounded").x
a2.plot(ts * 1000, wm, ".", color=MUTED, ms=4, label=T("“实测”数据", "'measured' data"))
tt = np.linspace(0, 30, 300)
a2.plot(tt, we * (1 - np.exp(-tt / (tls * 1000))), color=BLUE, lw=2, label=T(f"最小二乘 τ = {tls * 1000:.2f} ms", f"least squares τ = {tls * 1000:.2f} ms"))
a2.plot([0, we / sl * 1000], [0, we], color=ACC, lw=1.4, ls="--", label=T(f"切线法 τ = {we / sl * 1000:.2f} ms", f"tangent τ = {we / sl * 1000:.2f} ms"))
a2.plot([t63 * 1000], [0.632 * we], "o", color=RED, label=T(f"63.2% 点 τ = {t63 * 1000:.2f} ms", f"63.2% point τ = {t63 * 1000:.2f} ms"))
a2.axhline(we, color=MUTED, ls=":", lw=1)
a2.set_xlabel(T("时间 t / ms", "time t / ms"))
a2.set_ylabel(T("转速 / (rad/s)", "speed / (rad/s)"))
a2.set_title(T("RE 40 阶跃响应：读出时间常数", "RE 40 step response: reading the time constant"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="lower right")
clean(a2)
fig.tight_layout()
figure(fig, "fig19_7_1")
