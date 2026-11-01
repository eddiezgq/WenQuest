"""9.2 节的计算：

算例 9.2.1  接算例 9.1.1：料车由静止被拉上 8.0 m 长的坡道，到坡顶时速度多大？
算例 9.2.2  AGV 的停车距离：满载 M = 800 kg，制动减速度 2.0 m/s²，从发现障碍到开始制动的反应时间 0.15 s。
            速度 1.0、1.5、2.0 m/s 时停车距离各是多少？制动力做了多少功？货物（与车板 μ_s = 0.30）会不会滑？（图 9.2.1）
算例 9.2.3  有空气阻力的网球：m = 0.057 kg，直径 67 mm，C_d = 0.55，空气 ρ = 1.20 kg/m³，从 2.5 m 高处以 30 m/s、
            仰角 10° 击出，到落地为止。用 RK4（第 8 章）算出轨迹，沿轨迹求重力与阻力做的功，验证 W = ΔE_k（图 9.2.2）。
估一估      满载 AGV 以 1.5 m/s 行驶的动能，相当于把 10 kg 的重物从多高处落下。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 9.2.1（数据同算例 9.1.1）
m, alpha, s, F, phi, Crr = 60.0, math.radians(5.0), 8.0, 80.0, math.radians(20.0), 0.020
W_tot = F * s * math.cos(phi) - m * g * s * math.sin(alpha) - Crr * (m * g * math.cos(alpha) - F * math.sin(phi)) * s
v_top = math.sqrt(2 * W_tot / m)
a_cart = W_tot / (m * s)                                       # 合力沿坡道不变，也可以由 a 求 v 作核对
assert abs(v_top - math.sqrt(2 * a_cart * s)) < 1e-12
out(W_tot=W_tot, v_top=v_top)

# ---- 算例 9.2.2：停车距离
M, ab, tr, mus_load = 800.0, 2.0, 0.15, 0.30
rows = []
for v in (1.0, 1.5, 2.0):
    d_react, d_brake = v * tr, v * v / (2 * ab)
    rows.append((v, d_react, d_brake, d_react + d_brake, 0.5 * M * v * v))
out(M=M, ab=ab, tr=tr, Fb=M * ab, mus_load=mus_load, a_load=mus_load * g,
    **{f"dr{i}": r[1] for i, r in enumerate(rows)}, **{f"db{i}": r[2] for i, r in enumerate(rows)},
    **{f"ds{i}": r[3] for i, r in enumerate(rows)}, **{f"Ka{i}": r[4] for i, r in enumerate(rows)},
    ratio_brake=rows[2][2] / rows[0][2], ratio_stop=rows[2][3] / rows[0][3])
assert mus_load * g > ab                                       # 货物不滑

# ---- 算例 9.2.3：有阻力的网球，沿轨迹求功
mb, Db, Cd, rho = 0.057, 0.067, 0.55, 1.20
kd = 0.5 * rho * Cd * math.pi * Db ** 2 / 4                     # 阻力 = −kd |v| v
v0, th0, y0 = 30.0, math.radians(10.0), 2.5


def acc(v):
    return np.array([0.0, -g]) - kd / mb * np.linalg.norm(v) * v


def rhs(z):
    return np.concatenate([z[2:], acc(z[2:])])


h = 1e-4
z = np.array([0.0, y0, v0 * math.cos(th0), v0 * math.sin(th0)])
ts, Z = [0.0], [z.copy()]
while z[1] > 0:
    k1 = rhs(z); k2 = rhs(z + h / 2 * k1); k3 = rhs(z + h / 2 * k2); k4 = rhs(z + h * k3)
    z = z + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    ts.append(ts[-1] + h); Z.append(z.copy())
Z, ts = np.array(Z), np.array(ts)
f = Z[-2, 1] / (Z[-2, 1] - Z[-1, 1])                             # 线性插值到 y = 0
Z[-1] = Z[-2] + f * (Z[-1] - Z[-2]); ts[-1] = ts[-2] + f * h
V = Z[:, 2:]
P_g = -mb * g * V[:, 1]                                         # 各力的功率 F·v
P_d = -kd * np.linalg.norm(V, axis=1) ** 3
cum = lambda P: np.concatenate([[0.0], np.cumsum((P[1:] + P[:-1]) / 2 * np.diff(ts))])
Wg_t, Wd_t = cum(P_g), cum(P_d)
K = 0.5 * mb * np.sum(V ** 2, axis=1)
Wg, Wd, K0, K1 = Wg_t[-1], Wd_t[-1], K[0], K[-1]
assert abs(Wg - mb * g * y0) < 1e-6                             # 重力的功只与高度差有关
err = (K0 + Wg + Wd) - K1
assert abs(err) < 1e-4 * K0
out(mb=mb, Db_mm=Db * 1000, Cd=Cd, rho=rho, v0=v0, th0=10.0, y0=y0, K0=K0, K1=K1, Wg=Wg, Wd=Wd, v1=math.sqrt(2 * K1 / mb),
    range_=Z[-1, 0], t_fly=ts[-1], err=abs(err), rel_err=abs(err) / K0, dK=K1 - K0, Wsum=Wg + Wd, drag0=kd * v0 ** 2,
    loss=-Wd / K0, nWd=-Wd, ndK=K0 - K1, nWsum=-(Wg + Wd))

# ---- 估一估
v_e, m_drop = 1.5, 10.0
K_e = 0.5 * M * v_e ** 2
out(v_e=v_e, K_e=K_e, m_drop=m_drop, h_drop=K_e / (m_drop * g))

plt = style()
# ---- 图 9.2.1：停车距离
fig, ax = plt.subplots(figsize=(4.8, 3.1))
vv = np.linspace(0, 2.2, 200)
ax.fill_between(vv, 0, vv * tr, color=d.MUTED, alpha=0.35, lw=0, label=T(r"反应距离 $vt_\mathrm{r}$", r"reaction distance $vt_\mathrm{r}$"))
ax.fill_between(vv, vv * tr, vv * tr + vv ** 2 / (2 * ab), color=d.FIT, alpha=0.25, lw=0,
                label=T(r"制动距离 $v^2/(2a)$", r"braking distance $v^2/(2a)$"))
ax.plot(vv, vv * tr + vv ** 2 / (2 * ab), color=d.FIT, lw=2)
for r in rows:
    ax.plot(r[0], r[3], "o", color=d.FIT)
    ax.text(r[0] - 0.05, r[3] + 0.08, f"{r[3]:.2f} m", fontsize=8.5, ha="right")
ax.set_xlabel(T("速度 v / (m/s)", "speed v / (m/s)")); ax.set_ylabel(T("停车距离 / m", "stopping distance / m"))
ax.set_xlim(0, 2.2); ax.set_ylim(0, 1.8); ax.legend(frameon=False, fontsize=8.5, loc="upper left"); d.spines(ax)
figure(fig, "fig9_2_1")

# ---- 图 9.2.2：网球的能量账
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.9), gridspec_kw={"width_ratios": [1.15, 1]})
a1.plot(Z[::20, 0], Z[::20, 1], color=d.VA, lw=2)
for i in range(0, len(Z), len(Z) // 6):
    p, v = Z[i, :2], Z[i, 2:]
    Fd = -kd * np.linalg.norm(v) * v
    d.arrow(a1, p, p + 2.2 * v / np.linalg.norm(v), d.INK, lw=1.0, ms=8)
    d.arrow(a1, p, p + Fd * 4.0, d.VR, lw=1.4, ms=8)
a1.text(1, 0.6, T("黑：速度方向\n红：空气阻力（总与速度相反）", "black: direction of motion\nred: drag (always against it)"), fontsize=8)
a1.set_xlabel("x / m"); a1.set_ylabel("y / m"); a1.set_xlim(-1, Z[-1, 0] + 1); a1.set_ylim(0, 5.5); d.spines(a1)
a2.plot(ts[::20], K[::20], color=d.INK, lw=2.4, label=T("动能 $E_\\mathrm{k}$", "kinetic energy $E_\\mathrm{k}$"))
a2.plot(ts[::20], (K0 + Wg_t + Wd_t)[::20], color=d.VB, lw=1.2, ls="--", label=T("$E_\\mathrm{k0}$ + 重力的功 + 阻力的功", "$E_\\mathrm{k0}$ + work of gravity + of drag"))
a2.plot(ts[::20], Wg_t[::20], color=d.VA, lw=1.4, label=T("重力的功", "work of gravity"))
a2.plot(ts[::20], Wd_t[::20], color=d.VR, lw=1.4, label=T("阻力的功", "work of drag"))
a2.axhline(0, color=d.MUTED, lw=0.6)
a2.set_xlabel(T("时间 t / s", "time t / s")); a2.set_ylabel(T("能量 / J", "energy / J")); a2.legend(frameon=False, fontsize=7.5, loc="center right")
d.spines(a2)
fig.tight_layout()
figure(fig, "fig9_2_2")
