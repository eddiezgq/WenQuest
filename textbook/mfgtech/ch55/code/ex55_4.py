"""算例 55.4.1–55.4.2：表层残余应力（hub/surface.py）。
55.4.1：热态塑性变形产生残余拉应力（示意模型）：表层被加热 ΔT 而受里层约束，按双向约束的热应力 σ = −EαΔT/(1 − ν)；
        超过该温度下的屈服强度就被压缩屈服，冷却后变成残余拉应力 σres = min(σs, EαΔT/(1 − ν) − σs(T))。
        屈服强度随温度线性下降到 900 ℃ 时为零（示意）。SH-101（20CrMnTi）在 55.5 节算出的几种磨削温度下的残余应力；
55.4.2：X 射线法测残余应力（sin²ψ 法）：晶面间距随 sin²ψ 线性变化，斜率 ∝ σ。用一组示意读数拟合出应力。
画图 55.4.2（热态塑性变形的应力—温度过程）、55.4.3（几种加工的残余应力分布）、55.4.4（sin²ψ 法）。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

S = M.surf()
mat = M.mats().get("20CrMnTi-CQ")
E, nu, sy = mat["E_mpa"], mat["nu"], mat["yield_mpa"]
alpha = 11.9e-6                               # 线膨胀系数（cae/materials.py 的热物性）
k = E * alpha / (1 - nu)                      # 双向约束时每度的热应力 MPa/K


def sy_t(theta):
    return max(0.0, sy * (1 - (theta - 20) / 880))


def residual(theta):
    dT = theta - 20
    return min(sy, max(0.0, k * dT - sy_t(theta)))


dT_yield = next(t for t in range(1, 900) if k * t >= sy_t(20 + t))       # 开始压缩屈服的温升
res = {th: residual(th) for th in (200, 300, 400, 500)}

plt = style()
# ---- 图 55.4.2：热态塑性变形：加热—冷却过程中的表层应力
fig, ax = plt.subplots(figsize=(6.0, 3.0))
thmax = 500
up = np.linspace(20, thmax, 60)
el = [-min(k * (t - 20), sy_t(t)) for t in up]
down = np.linspace(thmax, 20, 60)
s_peak = el[-1]
dn = [s_peak + k * (thmax - t) for t in down]
dn = [min(v, sy) for v in dn]
ax.plot(up, el, color=M.RED, lw=1.5, label=T("加热：受里层约束，压应力；超过屈服强度后压缩屈服", "heating: constrained, compressive; yields"))
ax.plot(down, dn, color=M.ACCENT, lw=1.5, label=T("冷却：按弹性收缩，变成拉应力", "cooling: elastic shrinkage turns it tensile"))
ax.plot(up, [-sy_t(t) for t in up], color=M.MUTED, ls=":", lw=0.9, label=T("屈服强度随温度下降（示意）", "yield strength falling with temperature (illustr.)"))
ax.axhline(0, color=M.INK, lw=0.6)
ax.plot([20], [dn[-1]], "o", color=M.ACCENT, ms=5)
ax.text(30, dn[-1] - 120, T(f"残余拉应力 ≈ {dn[-1]:.0f} MPa", f"residual tension ≈ {dn[-1]:.0f} MPa"), fontsize=7.5, color=M.ACCENT)
ax.set_xlabel(T("表层温度 / ℃", "surface temperature / °C")); ax.set_ylabel(T("表层应力 / MPa（拉为正）", "surface stress / MPa (tension +)"))
ax.set_ylim(-1000, 1000); ax.grid(lw=0.3, alpha=0.5); ax.legend(fontsize=6.8, loc="lower right")
ax.set_title(T(f"SH-101 表层被磨到 {thmax} ℃（20CrMnTi，E = {E / 1000:.0f} GPa，σs = {sy} MPa）", f"SH-101 surface heated to {thmax} °C"), fontsize=8.5)
figure(fig, "fig55_4_2")

# ---- 图 55.4.3：几种加工后的残余应力分布（典型，示意）
fig, ax = plt.subplots(figsize=(6.4, 3.2))
z = np.linspace(0, 1.2, 400)
EN = {"turned": "finish turned", "ground": "normal grinding", "ground_burn": "grinding burn", "shot_peened": "shot peened", "rolled": "deep rolled"}
cols = {"turned": M.WARM, "ground": M.GREEN, "ground_burn": M.RED, "shot_peened": M.ACCENT, "rolled": "#6a4fa0"}
for kind, c in cols.items():
    zz = z[z <= S.RESIDUAL[kind][-1][0]]
    ax.plot(zz, S.residual_stress(kind, zz), color=c, lw=1.4, label=T(S.RESIDUAL_NAME[kind], EN[kind]))
ax.axhline(0, color=M.INK, lw=0.6)
ax.text(0.42, 0.8, T("拉应力：降低疲劳强度", "tension: lowers fatigue strength"), fontsize=7.5, color=M.RED, transform=ax.transAxes)
ax.text(0.02, 0.04, T("压应力：提高疲劳强度", "compression: raises fatigue strength"), fontsize=7.5, color=M.ACCENT, transform=ax.transAxes)
ax.set_xlabel(T("离表面的深度 / mm", "depth below the surface / mm")); ax.set_ylabel(T("轴向残余应力 / MPa", "axial residual stress / MPa"))
ax.set_xscale("symlog", linthresh=0.05); ax.set_xlim(0, 1.6); ax.set_ylim(-900, 700)
ax.set_xticks([0, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 1.5]); ax.set_xticklabels(["0", "0.02", "0.05", "0.1", "0.2", "0.5", "1", "1.5"])
ax.grid(lw=0.3, alpha=0.5); ax.legend(fontsize=7, loc="upper right", ncol=2)
figure(fig, "fig55_4_3")

# ---- 图 55.4.4：X 射线 sin²ψ 法（示意读数）
nu_x, E_x = 0.28, 210000.0
d0 = 0.11702                                   # α-Fe (211) 无应力时的晶面间距 nm（示意）
sin2 = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
true = {"磨削烧伤": 450.0, "正常磨削": -180.0, "喷丸": -520.0}
true_en = {"磨削烧伤": "grinding burn", "正常磨削": "normal grinding", "喷丸": "shot peened"}
rng = np.random.default_rng(55)
fits = {}
fig, ax = plt.subplots(figsize=(5.8, 3.0))
for (name, sig), c in zip(true.items(), (M.RED, M.GREEN, M.ACCENT)):
    d = d0 * (1 + (1 + nu_x) / E_x * sig * sin2) + rng.normal(0, 2e-7, sin2.size)
    a, b = np.polyfit(sin2, d, 1)
    fits[name] = a / d0 * E_x / (1 + nu_x)
    ax.plot(sin2, (d - d0) * 1e6, "o", color=c, ms=4)
    ax.plot(sin2, (a * sin2 + b - d0) * 1e6, color=c, lw=1.2,
            label=T(f"{name}：斜率 → σ = {fits[name]:.0f} MPa", f"{true_en[name]}: σ = {fits[name]:.0f} MPa"))
ax.set_xlabel("sin²ψ"); ax.set_ylabel(T("晶面间距的变化 d − d₀ / (10⁻⁶ nm)", "d − d₀ / (10⁻⁶ nm)"))
ax.grid(lw=0.3, alpha=0.5); ax.legend(fontsize=7, loc="upper left")
ax.set_title(T("σ = E/(1 + ν) · (∂d/∂sin²ψ)/d₀（示意读数）", "σ = E/(1 + ν) · (∂d/∂sin²ψ)/d₀ (illustrative)"), fontsize=8.5)
figure(fig, "fig55_4_4")

out(E=E, nu=nu, sy=sy, k=k, dT_yield=dT_yield, res200=res[200], res300=res[300], res400=res[400], res500=res[500],
    sig_burn=fits["磨削烧伤"], sig_ground=fits["正常磨削"], sig_peen=fits["喷丸"],
    r_turn=float(S.residual_stress("turned", np.array([0.0]))[0]), r_grind=float(S.residual_stress("ground", np.array([0.0]))[0]),
    r_burn=float(S.residual_stress("ground_burn", np.array([0.0]))[0]), r_peen_max=min(v for _, v in S.RESIDUAL["shot_peened"]), r_roll_max=min(v for _, v in S.RESIDUAL["rolled"]))
