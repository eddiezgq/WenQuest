"""8.5 节的计算：

算例 8.5.1  对弹簧振子 x'' = −ω²x，三种显式方法每走一步，误差（或能量）放大多少倍？画出放大倍数与 ωh 的关系，求各自的稳定界限
            （图 8.5.1）。欧拉法：√(1 + (ωh)²)，任何步长都不稳定；半隐式欧拉法：ωh ≤ 2 时为 1；RK4：ωh ≤ 2√2 时不超过 1。
算例 8.5.2  刚性问题：0.10 kg 的传感器用橡胶减振垫粘在机架上，垫的劲度 k = 1.0×10⁵ N/m、阻尼 c = 20 N·s/m（阻尼比 0.1）。
            机架随机械臂以 1 Hz、振幅 5 mm 慢慢往复运动，我们只关心传感器 2 s 内跟着机架的运动。步长 5 ms 时，
            半隐式欧拉法和隐式欧拉法的结果各是什么？半隐式欧拉法稳定需要多小的步长（计入阻尼）？
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d


def radius(M):
    return max(abs(np.linalg.eigvals(M)))


def G(method, z):                                             # z = ωh；单步的放大矩阵（状态 x, v/ω）
    if method == "euler":
        return np.array([[1, z], [-z, 1]])
    if method == "semi":
        return np.array([[1 - z * z, z], [-z, 1]])
    A = np.array([[0, 1], [-1, 0]]) * z                       # RK4：1 + A + A²/2 + A³/6 + A⁴/24
    return np.eye(2) + A + A @ A / 2 + A @ A @ A / 6 + A @ A @ A @ A / 24


zs = np.linspace(0.01, 3.2, 400)
rad = {mth: np.array([radius(G(mth, z)) for z in zs]) for mth in ("euler", "semi", "rk4")}
z_rk4 = zs[np.argmax(rad["rk4"] > 1 + 1e-9)]
out(z_semi=2.0, z_rk4=z_rk4, z_rk4_exact=2 * math.sqrt(2), rad_euler_01=math.sqrt(1 + 0.01))

# ---- 算例 8.5.2：减振垫上的传感器随机架慢慢运动（1 Hz、5 mm），垫很硬
m, k, c = 0.10, 1.0e5, 20.0
w = math.sqrt(k / m); zeta = c / (2 * math.sqrt(k * m))
Ab, fb = 0.005, 1.0
xb = lambda t: Ab * math.sin(2 * math.pi * fb * t)
vb = lambda t: 2 * math.pi * fb * Ab * math.cos(2 * math.pi * fb * t)
x_eq = -m * g / k                                              # 相对机架的静平衡位置（垫被压下）
Tend = 2.0


def semi(h):
    x, v, t = x_eq, 0.0, 0.0
    X = [x]
    for i in range(int(round(Tend / h))):
        v += h * (-k * (x - xb(t)) - c * (v - vb(t)) - m * g) / m
        x += h * v; t += h
        X.append(x)
        if abs(x) > 1.0:                                       # 偏离超过 1 m：已经发散
            return None, (i + 1) * h
    return np.array(X), None


def implicit(h):                                               # 隐式欧拉：每步解 2×2 线性方程
    x, v, t = x_eq, 0.0, 0.0
    X = [x]
    M = np.array([[1, -h], [h * k / m, 1 + h * c / m]])
    for _ in range(int(round(Tend / h))):
        t += h
        rhs = np.array([x, v + h * (k * xb(t) + c * vb(t) - m * g) / m])
        x, v = np.linalg.solve(M, rhs)
        X.append(x)
    return np.array(X)


h = 0.005
Xref, _ = semi(1e-5)                                           # 参考解：步长 0.01 ms
ref_on = lambda hh: Xref[::int(round(hh / 1e-5))]
_, t_blow = semi(h)
XI = implicit(h)
tt = np.arange(len(XI)) * h
late = tt > 0.1                                                # 起始的快速瞬态过去以后
err_I = np.abs(XI - ref_on(h))[late].max()
z_crit = -2 * zeta + 2 * math.sqrt(zeta ** 2 + 1)              # 有阻尼时半隐式欧拉法的稳定界限：(ωh)² + 4ζωh < 4
X1, _ = semi(0.001)
err_S1 = np.abs(X1 - ref_on(0.001))[np.arange(len(X1)) * 0.001 > 0.1].max()
out(w5=w, zeta=zeta, wh5=w * h, T5_ms=1000 * 2 * math.pi / w, dx_um=1e6 * m * g / k, t_blow_ms=1000 * t_blow, n_blow=round(t_blow / h),
    h_crit_ms=1000 * z_crit / w, z_crit=z_crit, h_crit0_ms=1000 * 2 / w, errI_um=1e6 * err_I, errS1_um=1e6 * err_S1, Ab_mm=1000 * Ab, fb=fb)

plt = style()
fig, ax = plt.subplots(figsize=(5.0, 3.1))
for mth, col, name in (("euler", d.VR, T("欧拉法", "Euler")), ("semi", d.VA, T("半隐式欧拉法", "semi-implicit Euler")), ("rk4", d.VB, "RK4")):
    ax.plot(zs, rad[mth], color=col, lw=2, label=name)
ax.axhline(1, color=d.INK, lw=0.8, ls=":")
ax.axvline(2, color=d.VA, lw=0.8, ls="--"); ax.axvline(2 * math.sqrt(2), color=d.VB, lw=0.8, ls="--")
ax.set_xlabel(r"$\omega h$"); ax.set_ylabel(T("每步的放大倍数", "growth factor per step")); ax.set_ylim(0.0, 2.0)
ax.legend(frameon=False, fontsize=8.5, loc="upper left"); d.spines(ax)
figure(fig, "fig8_5_1")
