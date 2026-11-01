"""10.2 节的计算：

算例 10.2.1  势能零点：20 kg 的箱子从输送线（离地 0.80 m）搬到货架（离地 2.00 m）。分别以地面和输送线为零点，
            求两处的重力势能和势能的变化。
算例 10.2.2  机械臂关节的重力平衡弹簧：连杆连同工具、负载共 6.0 kg，质心离转轴 0.30 m；φ 为连杆偏离竖直向上的角度。
            弹簧一端固定在转轴正上方 a = 0.10 m 处，另一端挂在连杆上离转轴 b = 0.15 m 处。
            （1）用“零长度弹簧”（势能 ½ks²，s 为两端距离）时，k 取多大能使总势能与 φ 无关；
            （2）改用自由长度 L0 = 0.05 m 的普通拉簧，残余的保持转矩最大多少；与不装弹簧时比较（图 10.2.2；弹簧布置见图 10.2.1）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 10.2.1
mb, y_conv, y_shelf = 20.0, 0.80, 2.00
U_floor = (mb * g * y_conv, mb * g * y_shelf)
U_conv = (0.0, mb * g * (y_shelf - y_conv))
assert abs((U_floor[1] - U_floor[0]) - (U_conv[1] - U_conv[0])) < 1e-9
out(mb=mb, U1f=U_floor[0], U2f=U_floor[1], U1c=U_conv[0], U2c=U_conv[1], dU=U_conv[1])

# ---- 算例 10.2.2：重力平衡
m, r, a, b, L0 = 6.0, 0.30, 0.10, 0.15, 0.05
k = m * g * r / (a * b)
phi = np.radians(np.linspace(0, 150, 1501))
s = np.sqrt(a * a + b * b - 2 * a * b * np.cos(phi))
Ug = m * g * r * np.cos(phi)                                  # 以转轴高度为零点
Us0 = 0.5 * k * s ** 2                                        # 零长度弹簧
Us1 = 0.5 * k * (s - L0) ** 2                                 # 自由长度 L0 的拉簧
assert np.all(s >= L0 - 1e-12)                                # 弹簧始终受拉
Ut0, Ut1 = Ug + Us0, Ug + Us1
assert np.ptp(Ut0) < 1e-9                                     # 完全平衡：总势能不随角度变化
tau_none = m * g * r * np.sin(phi)                            # 保持转矩 = dU/dφ 的大小
tau1 = np.abs(np.gradient(Ut1, phi))
i1 = int(np.argmax(tau1))
out(m=m, r=r, a=a, b=b, L0_mm=L0 * 1000, k=k, tau_none_max=m * g * r, tau1_max=float(tau1[i1]),
    phi1_max=float(np.degrees(phi[i1])), ratio1=float(tau1[i1] / (m * g * r)), Ut0=float(Ut0[0]),
    smin_mm=float(s.min() * 1000), smax_mm=float(s.max() * 1000))

plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.9))
deg = np.degrees(phi)
a1.plot(deg, Ug, color=d.VA, lw=2, label=T("重力势能", "gravitational PE"))
a1.plot(deg, Us0, color=d.VB, lw=2, label=T("弹性势能（零长度弹簧）", "elastic PE (zero-length spring)"))
a1.plot(deg, Ut0, color=d.VR, lw=2.4, label=T("总势能", "total PE"))
a1.axhline(0, color=d.MUTED, lw=0.6)
a1.set_xlabel(T("连杆偏离竖直向上的角度 φ / (°)", "link angle from vertical φ / (°)")); a1.set_ylabel(T("势能 / J", "potential energy / J"))
a1.set_xlim(0, 150); a1.legend(frameon=False, fontsize=7.5, loc="lower left"); d.spines(a1)
a1.set_title(T("(a) 完全平衡：总势能不变", "(a) perfect balance: total PE constant"), fontsize=9.5)
a2.plot(deg, tau_none, color=d.VA, lw=2, label=T("不装弹簧", "no spring"))
a2.plot(deg, tau1, color=d.VR, lw=2, label=T(f"拉簧，自由长度 {L0 * 1000:.0f} mm", f"real spring, free length {L0 * 1000:.0f} mm"))
a2.plot(deg, np.zeros_like(deg), color=d.VB, lw=2, ls="--", label=T("零长度弹簧", "zero-length spring"))
a2.set_xlabel(T("φ / (°)", "φ / (°)")); a2.set_ylabel(T("保持转矩 / (N·m)", "holding torque / (N·m)"))
a2.set_xlim(0, 150); a2.set_ylim(-0.5, 19); a2.legend(frameon=False, fontsize=7.5, loc="upper left"); d.spines(a2)
a2.set_title(T("(b) 关节要提供的保持转矩", "(b) torque the joint must hold"), fontsize=9.5)
fig.tight_layout()
figure(fig, "fig10_2_2")

# ---- 图 10.2.1：平衡弹簧的布置（示意）
fig, ax = plt.subplots(figsize=(3.2, 3.0))
ph = math.radians(60)
P0 = np.array([0.0, 0.0]); A = np.array([0.0, a]); B = b * np.array([math.sin(ph), math.cos(ph)]); E = 0.42 * np.array([math.sin(ph), math.cos(ph)])
C = r * np.array([math.sin(ph), math.cos(ph)])
ax.plot([P0[0], E[0]], [P0[1], E[1]], color=d.INK, lw=6, solid_capstyle="round")
ax.plot([0, 0], [0, a + 0.03], color=d.MUTED, lw=3)
nz = 12; zz = np.linspace(0, 1, nz * 2 + 1); off = np.array([-(B - A)[1], (B - A)[0]]) / np.linalg.norm(B - A) * 0.012
pts = [A + (B - A) * t + off * (1 if i % 2 else -1) * (0 < i < len(zz) - 1) for i, t in enumerate(zz)]
ax.plot([p[0] for p in pts], [p[1] for p in pts], color=d.VB, lw=1.4)
ax.plot(*P0, "o", color=d.INK, ms=9); ax.plot(*A, "o", color=d.VB, ms=5); ax.plot(*B, "o", color=d.VB, ms=5)
ax.plot(*C, "s", color=d.VR, ms=9)
d.arrow(ax, C, C + np.array([0, -0.12]), d.VR, label="mg", off=(0.04, 0.0), fs=10)
ax.plot([0, 0], [0, 0.4], color=d.MUTED, lw=0.8, ls=":")
th = np.linspace(math.pi / 2, math.pi / 2 - ph, 30); ax.plot(0.12 * np.cos(th), 0.12 * np.sin(th), color=d.INK, lw=0.8)
ax.text(0.035, 0.135, "φ", fontsize=11)
ax.text(-0.075, a, "A", fontsize=10, color=d.VB); ax.text(B[0] + 0.005, B[1] - 0.05, "B", fontsize=10, color=d.VB)
ax.text(-0.04, -0.045, "O", fontsize=10)
ax.text(C[0] + 0.02, C[1] + 0.02, T("质心", "centre of mass"), fontsize=9, color=d.VR)
ax.text(0.17, -0.06, T("OA = a，OB = b", "OA = a, OB = b"), fontsize=9)
ax.set_aspect("equal"); ax.set_xlim(-0.1, 0.42); ax.set_ylim(-0.08, 0.42); d.clean(ax)
figure(fig, "fig10_2_1")
