"""6.3 节的计算：

算例 6.3.1  由加速度之比求货箱的质量（定义 6.3.1）；
算例 6.3.2  AGV 的驱动力一定，带载与空载的加速度；
算例 6.3.3  UR5e 沿水平方向加速搬运零件时，夹爪对零件的力（图 6.3.3）；
图 6.3.1    实验 6.3 那样的测量：不同质量下 a 与 F 的数据和拟合（仿真数据，带测量噪声）。
"""
import json
import math
from pathlib import Path

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 6.3.1：同一个驱动力下，空车与载着货箱时的加速度之比
a1_cmp, a2_cmp = 1.50, 0.945
m_cmp = 80.0 * a1_cmp / a2_cmp

# ---- 算例 6.3.2
F_drive = 120.0          # 驱动力（地面对驱动轮的摩擦力，6.4 节），N
m_agv, m_load = 80.0, 40.0
a_loaded = F_drive / (m_agv + m_load)
a_empty = F_drive / m_agv
v_target = 1.5           # 巡航速度，m/s
t_loaded, t_empty = v_target / a_loaded, v_target / a_empty
s_loaded = v_target ** 2 / (2 * a_loaded)

# ---- 算例 6.3.3：UR5e 搬运零件（额定负载取自零件库模型的产品数据）
entry = json.loads((Path(__file__).resolve().parents[2] / "models" / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))
payload = entry["datasheet"]["values"]["payload_kg"]
m_part, a_arm = 2.0, 3.0
F = np.array([m_part * a_arm, m_part * g])          # 夹爪对零件的力：F + m g = m a
F_mag = float(np.linalg.norm(F))
F_ang = math.degrees(math.atan2(F[1], F[0]))
assert m_part <= payload

# ---- 图 6.3.1：仿真测量数据
rng = np.random.default_rng(6)
masses = [100.0, 120.0, 140.0]
forces = np.arange(40.0, 161.0, 20.0)
sigma_a = 0.02                                       # 加速度测量的标准差，m/s²
fits = []
plt = style()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.4, 3.3))
cols = ["#1d6fb8", "#2ca02c", "#e67e22"]
for m, c in zip(masses, cols):
    a_meas = forces / m + rng.normal(0, sigma_a, forces.size)
    (k, b), cov = np.polyfit(forces, a_meas, 1, cov=True)
    u_m = math.sqrt(cov[0, 0]) / k ** 2                   # u(1/k) = u(k)/k²
    fits.append((m, 1 / k, b, u_m))
    ax1.plot(forces, a_meas, "o", color=c, ms=5)
    ff = np.linspace(0, 170, 2)
    ax1.plot(ff, k * ff + b, color=c, lw=1.5, label=f"$m$ = {m:.0f} kg")
ax1.set_xlabel(T("合力 $F$ / N", "net force $F$ / N")); ax1.set_ylabel(T("加速度 $a$ / (m/s²)", "acceleration $a$ / (m/s²)"))
ax1.set_xlim(0, 170); ax1.set_ylim(0, 1.8); ax1.legend(frameon=False, fontsize=9)
ax1.set_title(T(r"(a) 质量一定：$a \propto F$", r"(a) fixed mass: $a \propto F$"), fontsize=11)
m_list = np.array([80.0, 100.0, 120.0, 140.0, 160.0, 180.0])     # AGV 自身 80 kg，载货 0–100 kg
a_m = 120.0 / m_list + rng.normal(0, sigma_a, m_list.size)
k2 = float(np.sum(a_m / m_list) / np.sum(1 / m_list ** 2))     # 过原点拟合 a = k (1/m)，k 即合力
ax2.plot(1 / m_list, a_m, "o", color=d.INK, ms=5)
xx = np.linspace(0, 1 / 70, 2)
ax2.plot(xx, k2 * xx, color=d.INK, lw=1.5)
ax2.set_xlabel(T("质量的倒数 $1/m$ / kg$^{-1}$", "inverse mass $1/m$ / kg$^{-1}$")); ax2.set_ylabel(T("加速度 $a$ / (m/s²)", "acceleration $a$ / (m/s²)"))
ax2.set_xlim(0, 1 / 70); ax2.set_ylim(0, 1.8)
ax2.set_title(T(r"(b) 合力 120 N：$a \propto 1/m$", r"(b) net force 120 N: $a \propto 1/m$"), fontsize=11)
for ax in (ax1, ax2):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig6_3_1")
for m, mf, b, um in fits:
    assert abs(mf - m) < 3 * um and abs(b) < 0.06

# ---- 图 6.3.2：同样的力，总质量加倍，加速度减半
fig, ax = plt.subplots(figsize=(6.4, 2.6))
for row, (y, nload, lab) in enumerate([(1.1, 1, T("总质量 $m$", "total $m$")), (0.0, 2, T("总质量 $2m$", "total $2m$"))]):
    deck = d.agv(ax, 0.0, y, w=1.0)
    for k in range(nload):
        d.crate(ax, 0.15 + k * 0.36, deck, 0.3)
    d.arrow(ax, 0.8, y + 0.0, 0.7, 0, d.FORCE, r"$\boldsymbol{F}_\mathrm{d}$", off=(0.15, -0.06))
    d.arrow(ax, 2.3, y + 0.35, 0.8 / nload, 0, d.ACC, r"$\boldsymbol{a}$" if nload == 1 else r"$\boldsymbol{a}/2$", off=(0.18, 0))
    ax.text(-0.15, y + 0.3, lab, ha="right", va="center", fontsize=11, color=d.INK)
    d.floor(ax, -0.4, 3.6, y)
ax.set_xlim(-1.4, 3.7); ax.set_ylim(-0.15, 2.0)
d.clean(ax)
figure(fig, "fig6_3_2")

# ---- 图 6.3.3：零件受的两个力与 m a
fig, ax = plt.subplots(figsize=(4.6, 3.6))
s = 0.08
ax.add_patch(plt.Rectangle((-0.25, -0.2), 0.5, 0.4, fc=d.CRATE, ec=d.INK, lw=1.2, zorder=3))
d.arrow(ax, 0, 0, 0, -m_part * g * s, d.FORCE, r"$m\boldsymbol{g}$", off=(0.25, 0))
d.arrow(ax, 0, 0, F[0] * s, F[1] * s, d.FORCE, r"$\boldsymbol{F}$" + T("（夹爪）", " (gripper)"), off=(0.15, 0.15), ha="left")
d.arrow(ax, 0, 0, m_part * a_arm * s, 0, d.ACC, r"$m\boldsymbol{a}$", off=(0.1, -0.15), lw=2.6)
ax.plot([F[0] * s, F[0] * s], [F[1] * s, 0], color=d.MUTED, ls="--", lw=1)
ax.text(F[0] * s + 0.05, F[1] * s / 2, r"$mg$", color=d.MUTED, fontsize=10)
ax.add_patch(plt.matplotlib.patches.Arc((0, 0), 0.5, 0.5, theta1=0, theta2=F_ang, color=d.MUTED, lw=1))
ax.text(0.3, 0.12, r"$\theta$", color=d.MUTED, fontsize=11)
d.arrow(ax, -1.2, 1.4, 0.45, 0, d.ACC, "", lw=1.6)
ax.text(-1.2, 1.55, T("运动方向", "direction of motion"), fontsize=9, color=d.MUTED)
ax.set_xlim(-1.3, 1.6); ax.set_ylim(-1.9, 1.9)
d.clean(ax)
figure(fig, "fig6_3_3")

out(a1_cmp=a1_cmp, a2_cmp=a2_cmp, m_cmp=m_cmp, m_crate=m_cmp - 80.0, F_drive=F_drive, m_agv=m_agv, m_load=m_load, m_total=m_agv + m_load, a_loaded=a_loaded, a_empty=a_empty,
    t_loaded=t_loaded, t_empty=t_empty, s_loaded=s_loaded,
    payload=payload, m_part=m_part, a_arm=a_arm, Fx=F[0], Fy=F[1], F_mag=F_mag, F_ang=F_ang, F_ratio=F_mag / (m_part * g),
    fit_m1=fits[0][1], fit_m2=fits[1][1], fit_m3=fits[2][1], u_m1=fits[0][3], u_m2=fits[1][3], u_m3=fits[2][3], fit_F=k2, sigma_a=sigma_a)
