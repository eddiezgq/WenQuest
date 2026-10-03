"""33.11 工业平缝机上轴 LS-101：曲柄连杆惯性力与转矩波动 → 台阶处一转之内的应力变化 → 无限寿命安全系数（5 000 与
5 500 r/min）→ 临界转速（梁单元 + 集中质量）与有限元固有频率（算例 33.11.1–33.11.3，图 33.11.1–33.11.3）。"""
import math

import numpy as np

import _draw as D
import _fea
import _ls as L
from bookout import T, figure, out, style
import mdstd

mat = mdstd.material(L.MAT)
th = np.linspace(0, 2 * np.pi, 721)[:-1]


def section_stress(n, z_sec, d):
    """截面 z_sec 表面各点（相对曲柄的方位 φ0）一转之内的 σ(θ)、τ(θ)（名义值，MPa）"""
    W, WT = math.pi * d ** 3 / 32, math.pi * d ** 3 / 16
    Mx, My = [], []
    for a in th:
        z, mx, my = L.moments(a, n)
        i = int(np.argmin(abs(z - z_sec)))
        Mx.append(mx[i])
        My.append(my[i])
    Mx, My = np.array(Mx), np.array(My)
    tau = (L.crank_torque(th, n) + L.P_SEW / L.omega(n) * 1000) / WT          # 曲柄与电机之间的截面传全部转矩
    out_ = []
    for phi in np.linspace(0, 2 * np.pi, 72, endpoint=False):
        psi = th + phi                                         # 这个点随轴转动
        sig = (Mx * np.cos(psi) + My * np.sin(psi)) / W
        out_.append((phi, sig))
    return out_, tau


def safety(n, alpha):
    pts, tau = section_stress(n, L.Z_STEP, 12)
    f = dict(q_s=mdstd.notch_sensitivity(L.FILLET, mat["sigma_b"]), q_t=mdstd.notch_sensitivity(L.FILLET, mat["sigma_b"], torsion=True))
    k_s, k_t = 1 + f["q_s"] * (alpha[0] - 1), 1 + f["q_t"] * (alpha[1] - 1)
    eps, beta = mdstd.size_factor(12), mdstd.surface_factor("ground", mat["sigma_b"])
    K_s, K_t = k_s / eps + 1 / beta - 1, k_t / eps + 1 / beta - 1
    ps, pt = mat["sigma_1"] / mat["sigma_b"], mat["tau_1"] / (mat["sigma_b"] / math.sqrt(3))
    ta, tm = (tau.max() - tau.min()) / 2, (tau.max() + tau.min()) / 2
    S_t = mat["tau_1"] / (K_t * ta + pt * abs(tm))
    worst = None
    for phi, sig in pts:
        sa, sm = (sig.max() - sig.min()) / 2, (sig.max() + sig.min()) / 2
        S_s = mat["sigma_1"] / (K_s * sa + ps * abs(sm))
        S = S_s * S_t / math.sqrt(S_s ** 2 + S_t ** 2)
        if worst is None or S < worst["S"]:
            worst = dict(S=S, S_s=S_s, phi=phi, sa=sa, sm=sm, sig=sig)
    return dict(worst, S_t=S_t, ta=ta, tm=tm, tau=tau, k_s=k_s, k_t=k_t, K_s=K_s, K_t=K_t, eps=eps, beta=beta, **f)


# ---- 台阶 Ø12 → Ø16、r = 0.5 的理论应力集中系数：有限元（33.5.4 节同一个程序）
kt = _fea.stepped_bar_kt(12.0, 16.0, L.FILLET, fine=4)
alpha = (kt["alpha_sigma"], kt["alpha_tau"])
A5, A55 = safety(L.N_MAX, alpha), safety(L.N_UP, alpha)
fx, fy = L.crank_force(th, L.N_MAX)
F_abs = np.hypot(fx, fy)
Tq = L.crank_torque(th, L.N_MAX) / 1000                            # N·m
T_mean = L.P_SEW / L.omega(L.N_MAX)
amp1 = L.M_RECIP * L.R_CRANK / 1000 * L.omega(L.N_MAX) ** 2       # 一阶往复惯性力幅值
cyc_h = L.N_MAX * 60

# ---- 临界转速：梁单元 + 集中质量（33.7 节的方法）；不带集中质量的光轴与有限元固有频率对照
nc, zb, modes = L.critical_speeds()
nc0, _, _ = L.critical_speeds(masses=[])
from cae import geometry as GEO, materials as MATS, modal as MO  # noqa: E402
step = L.step_bytes()
faces, _, _ = GEO.faces(step)
seats = []
for zb0, zb1 in ((L.LAY[1][0], L.LAY[1][1]), (L.LAY[3][0], L.LAY[3][1])):
    seats.append(next(f["id"] for f in faces if f["kind"] == "cylinder" and abs((f["bbox"][3] - f["bbox"][0]) / 2 - 6) < 0.05
                      and abs(f["bbox"][2] - zb0) < 0.6 and abs(f["bbox"][5] - zb1) < 0.6))
ax_ = {"origin": [0, 0, 0], "dir": [0, 0, 1]}
mst, _ = MO.solve(step, {"material": MATS.get(L.MAT), "mesh": {"size_mm": 3.0}, "loads": [
    {"type": "cyl_support", "faces": [seats[0]], "dofs": ["radial", "axial"], "axis": ax_, "band_mm": 1},
    {"type": "cyl_support", "faces": [seats[1]], "dofs": ["radial"], "axis": ax_, "band_mm": 1}]}, n_modes=3)
mst_full, _ = MO.solve(step, {"material": MATS.get(L.MAT), "mesh": {"size_mm": 3.0}, "loads": [      # 整个轴承位都限径向（对照）
    {"type": "cyl_support", "faces": [seats[0]], "dofs": ["radial", "axial"], "axis": ax_},
    {"type": "cyl_support", "faces": [seats[1]], "dofs": ["radial"], "axis": ax_}]}, n_modes=1)
f_fe = mst["freqs"][0]["hz"]
err_fe = (f_fe * 60 - nc0[0]) / nc0[0] * 100

# ---------------------------------------------------------------- 图
plt = style()
deg = np.degrees(th)
fig, axs = plt.subplots(2, 1, figsize=(6.6, 4.6), sharex=True)
axs[0].plot(deg, fy, color=D.FORCE, lw=1.4, label=T("铅垂分力 Fy（沿针杆）", "vertical Fy (along needle bar)"))
axs[0].plot(deg, fx, color=D.MOMENT, lw=1.4, label=T("水平分力 Fx（平衡块）", "horizontal Fx (counterweight)"))
axs[0].plot(deg, F_abs, color=D.INK, lw=1.0, ls="--", label=T("合力", "resultant"))
axs[0].set_ylabel(T("曲柄对上轴的力 / N", "force on shaft / N"))
axs[0].legend(fontsize=7.5, frameon=False, ncol=3, loc="upper center")
axs[1].plot(deg, Tq, color=D.TORQUE, lw=1.4, label="5 000 r/min")
axs[1].plot(deg, L.crank_torque(th, L.N_UP) / 1000, color=D.TORQUE, lw=1.0, ls="--", label="5 500 r/min")
axs[1].axhline(T_mean, color=D.MUTED, lw=0.8)
axs[1].text(355, T_mean, T("平均（缝纫功率）", "mean (sewing power)"), fontsize=7.5, ha="right", va="bottom", color=D.MUTED)
axs[1].set_ylabel(T("惯性转矩 / N·m", "inertia torque / N·m"))
axs[1].set_xlabel(T("曲柄转角 θ / (°)（针杆上止点为 0）", "crank angle θ / ° (needle bar at top = 0)"))
axs[1].set_xticks(range(0, 361, 90))
axs[1].legend(fontsize=7.5, frameon=False)
fig.tight_layout()
figure(fig, "fig33_11_1")

fig, ax = plt.subplots(figsize=(6.4, 3.2))
ax.plot(deg, A5["sig"], color=D.MOMENT, lw=1.5, label=T("弯曲正应力 σ（最危险点）", "bending σ (worst point)"))
ax.plot(deg, A5["tau"], color=D.TORQUE, lw=1.5, label=T("扭转切应力 τ", "torsional τ"))
ax.axhline(0, color=D.MUTED, lw=0.6)
ax.set_xlabel(T("曲柄转角 θ / (°)", "crank angle θ / °"))
ax.set_ylabel(T("名义应力 / MPa（台阶 Ø12→Ø16）", "nominal stress / MPa (step Ø12→Ø16)"))
ax.set_xticks(range(0, 361, 90))
ax.legend(fontsize=8, frameon=False)
fig.tight_layout()
figure(fig, "fig33_11_2")

fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.8, 3.9), gridspec_kw={"height_ratios": [1.2, 1]}, sharex=True)
D.shaft(a1, [(z0, z1, d) for z0, z1, d, _ in L.LAY])
for zc in L.Z_BRG:
    D.bearing(a1, zc, 12, 32, 10)
OFF = [(-6, 24, "right"), (8, 24, "left"), (0, 24, "center"), (-4, -30, "right"), (6, -30, "left")]     # 标注错开，不重叠
for (name, zm, mk), (dx, dy, ha) in zip(L.MASSES, OFF):
    a1.plot([zm], [0], "o", ms=4 + 20 * mk, mfc=D.GEAR, mec=D.INK, mew=0.8, zorder=5)
    a1.annotate(name, (zm, 0), xytext=(dx, dy), textcoords="offset points", ha=ha, fontsize=7,
                arrowprops=dict(arrowstyle="-", color=D.MUTED, lw=0.6))
a1.set_ylim(-30, 30)
a1.set_aspect("equal")
a1.axis("off")
a2.plot(zb, modes[0], color=D.MOMENT, lw=1.6, label=T("一阶振型", "1st mode"))
a2.axhline(0, color=D.MUTED, lw=0.6)
for zc in L.Z_BRG:
    a2.plot([zc], [0], "^", color=D.INK, ms=6)
a2.set_xlabel(T("z / mm（从机头前端算起）", "z / mm (from the head end)"))
a2.set_yticks([])
a2.legend(fontsize=8, frameon=False)
fig.tight_layout()
figure(fig, "fig33_11_3")

out(n_max=L.N_MAX, n_up=L.N_UP, r=L.R_CRANK, l=L.L_ROD, lam=L.LAMBDA, m_r=L.M_RECIP, bal=L.BALANCE, w=L.omega(L.N_MAX),
    amp1=amp1, F_max=float(F_abs.max()), Fy_max=float(fy.max()), Fx_max=float(abs(fx).max()), T_mean=T_mean,
    T_pp=float(Tq.max() - Tq.min()), T_max=float(abs(Tq).max()), P_sew=L.P_SEW, cyc_h=cyc_h, belt=L.BELT_N,
    alpha_s=alpha[0], alpha_t=alpha[1], q_s=A5["q_s"], q_t=A5["q_t"], k_s=A5["k_s"], k_t=A5["k_t"], eps=A5["eps"], beta=A5["beta"],
    K_s=A5["K_s"], K_t=A5["K_t"], sa5=A5["sa"], sm5=A5["sm"], ta5=A5["ta"], tm5=A5["tm"], S5=A5["S"], Ss5=A5["S_s"], St5=A5["S_t"],
    sa55=A55["sa"], S55=A55["S"], phi5=math.degrees(A5["phi"]), sigma_1=mat["sigma_1"], tau_1=mat["tau_1"], sigma_b=mat["sigma_b"],
    nc1=float(nc[0]), nc2=float(nc[1]), ratio=float(nc[0] / L.N_MAX), nc0=float(nc0[0]), hz0=float(nc0[0]) / 60, bal_pct=L.BALANCE * 100, k_up=(L.N_UP / L.N_MAX) ** 2, f_fe=f_fe, n_fe=f_fe * 60, err_fe=err_fe,
    f_full=mst_full["freqs"][0]["hz"], f_fe2=mst["freqs"][1]["hz"], f_fe3=mst["freqs"][2]["hz"], n_el_modal=mst["elements"], hz5=L.N_MAX / 60, hz55=L.N_UP / 60,
    length=L.LEN, fillet=L.FILLET, m_total=sum(m for _, _, m in L.MASSES))
