"""9.5 节的计算：

算例 9.5.1  直流电机的特性：电源 24 V，电枢电阻 R = 0.40 Ω，转矩常数 K = 0.050 N·m/A（= 反电动势常数，V·s/rad），
            空载电流 0.40 A（内部摩擦）。求堵转转矩、空载转速、最大输出功率、最高效率，画特性曲线（图 9.5.1）。
算例 9.5.2  电机 + 谐波减速器（效率 0.75）驱动关节：关节要输出 60 N·m、2.0 rad/s。传动比 100 时电机的电流、电压、
            各处的功率与损耗；驱动器效率 0.95。传动比从 40 变到 220，总效率怎样变（图 9.5.2）。
算例 9.5.3  单关节机械臂（实验 9.5 的模型）：连杆 4.0 kg、质心离轴 0.25 m，末端负载 5.0 kg、离轴 0.50 m，
            在竖直面内从 −30° 转到 +60°，梯形角速度曲线、用时 1.5 s（加速、减速各占 1/4）。
            求关节转矩、角速度、功率随时间的变化，功的总和，峰值；从三种伺服电机和五种传动比中选最小的电机（图 9.5.3）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 9.5.1：直流电机
U, R, k, I0 = 24.0, 0.40, 0.050, 0.40
Is = U / R
tau_s = k * (Is - I0)
w0 = (U - I0 * R) / k
w = np.linspace(0, w0, 20001)
I = (U - k * w) / R
tau = k * (I - I0)
Pout = tau * w
eta = Pout / (U * I)
iP, iE = int(np.argmax(Pout)), int(np.argmax(eta))
eta_formula = (1 - math.sqrt(I0 / Is)) ** 2
assert abs(eta[iE] - eta_formula) < 2e-3
rpm = 60 / (2 * math.pi)
out(U=U, R=R, k=k, I0=I0, Is=Is, tau_s=tau_s, w0=w0, n0=w0 * rpm, Pmax=Pout[iP], w_Pmax=w[iP], n_Pmax=w[iP] * rpm,
    tau_Pmax=tau[iP], eta_Pmax=eta[iP], eta_max=eta[iE], n_etamax=w[iE] * rpm, tau_etamax=tau[iE], I_etamax=I[iE],
    eta_formula=eta_formula, tau_f=k * I0, Pin_stall=U * Is, Pcu_stall=Is ** 2 * R)

# ---- 算例 9.5.2：电机 + 减速器 + 驱动器
tj, wj, eg, ed = 60.0, 2.0, 0.75, 0.95


def chain(i):
    tm, wm = tj / (i * eg), wj * i
    Im = tm / k + I0
    Um = Im * R + k * wm
    Pel = Um * Im
    return dict(tm=tm, wm=wm, nm=wm * rpm, Im=Im, Um=Um, Pel=Pel, Pcu=Im ** 2 * R, Pfr=k * I0 * wm, Pmech=tm * wm,
                Pgear=tm * wm * (1 - eg), Pj=tj * wj, Pbat=Pel / ed, Pdrv=Pel / ed - Pel, eta=tj * wj / (Pel / ed))


c = chain(100)
assert abs(c["Pel"] - (c["Pcu"] + c["Pfr"] + c["Pmech"])) < 1e-9 and abs(c["Pmech"] * eg - c["Pj"]) < 1e-9
out(tj=tj, wj=wj, eg=eg, ed=ed, Pj=tj * wj, **{f"c_{key}": val for key, val in c.items()}, eta_motor=c["Pmech"] / c["Pel"])
ii = np.arange(40, 221)
etas = np.array([chain(i)["eta"] for i in ii])
Ums = np.array([chain(i)["Um"] for i in ii])
ok = Ums <= U
i_best = int(ii[ok][np.argmax(etas[ok])])
cb, c50 = chain(i_best), chain(50)
out(i_best=i_best, eta_best=cb["eta"], Um_best=cb["Um"], Im_best=cb["Im"], eta50=c50["eta"], Im50=c50["Im"], Pcu50=c50["Pcu"])

# ---- 算例 9.5.3：单关节机械臂
mL, rL, mp, Lp = 4.0, 0.25, 5.0, 0.50
th_a, th_b, Tm = math.radians(-30), math.radians(60), 1.5
J = mL * rL ** 2 + mp * Lp ** 2                                # 各质点 m r² 之和（第 12 章称为转动惯量）
G = (mL * rL + mp * Lp) * g                                   # 重力矩 = G cos θ


def move(Tm_, n=30001):
    ta = Tm_ / 4
    wmax = (th_b - th_a) / (Tm_ - ta)
    al = wmax / ta
    t = np.linspace(0, Tm_, n)
    om = np.where(t < ta, al * t, np.where(t < Tm_ - ta, wmax, al * (Tm_ - t)))
    alp = np.where(t < ta, al, np.where(t < Tm_ - ta, 0.0, -al))
    th = th_a + np.concatenate([[0.0], np.cumsum((om[1:] + om[:-1]) / 2 * np.diff(t))])
    tq = J * alp + G * np.cos(th)
    return t, th, om, tq, tq * om, wmax, al


t, th, om, tq, P, wmax, al = move(Tm)
Wj = float(np.sum((P[1:] + P[:-1]) / 2 * np.diff(t)))
dU = G * (math.sin(th_b) - math.sin(th_a))                      # 连杆和负载升高所需的功
assert abs(th[-1] - th_b) < 1e-6 and abs(Wj - dU) < 2e-2
MOT = {"A": (0.32, 0.95), "B": (0.64, 1.91), "C": (1.27, 3.82)}   # 额定、峰值转矩 N·m；最高转速都按 5000 r/min
NMAX, RATIOS = 5000 / rpm, (50, 80, 100, 120, 160)


def feasible(name, i, tq_pk, w_pk):
    rated, peak = MOT[name]
    return tq_pk / (i * eg) <= peak and G / (i * eg) <= rated and i * w_pk <= NMAX


tq_pk, w_pk = float(np.max(np.abs(tq))), wmax
table = {name: [i for i in RATIOS if feasible(name, i, tq_pk, w_pk)] for name in MOT}
smallest = next(n for n in MOT if table[n])
out(mL=mL, rL=rL, mp=mp, Lp=Lp, Tm=Tm, J=J, G=G, wmax=wmax, alpha=al, tq_pk=tq_pk, t_pk=float(t[np.argmax(np.abs(tq))]),
    P_pk=float(P.max()), P_min=float(P.min()), Wj=Wj, dU=dU, G_hold=G, nmax_rpm=5000,
    hold_A=G / (160 * eg), hold_B100=G / (100 * eg), speed160=160 * w_pk * rpm, speed100=100 * w_pk * rpm,
    pkA160=tq_pk / (160 * eg), pkB100=tq_pk / (100 * eg),
    okA=", ".join(map(str, table["A"])) or "—", okB=", ".join(map(str, table["B"])), okC=", ".join(map(str, table["C"])),
    smallest=smallest)

plt = style()
# ---- 图 9.5.1：电机特性
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.9))
sl = slice(None, None, 20)
n_ = w * rpm
a1.plot(n_[sl], tau[sl], color=d.VA, lw=2, label=T("输出转矩", "output torque"))
a1.set_xlabel(T("转速 / (r/min)", "speed / (r/min)")); a1.set_ylabel(T("转矩 / (N·m)", "torque / (N·m)"), color=d.VA)
a1.set_ylim(0, 3.3); a1.set_xlim(0, 4800)
b1 = a1.twinx()
b1.plot(n_[sl], Pout[sl], color=d.VR, lw=2)
b1.set_ylabel(T("输出功率 / W", "output power / W"), color=d.VR); b1.set_ylim(0, 400)
b1.plot(w[iP] * rpm, Pout[iP], "o", color=d.VR)
b1.text(w[iP] * rpm + 150, Pout[iP] + 8, T(f"最大 {Pout[iP]:.0f} W", f"max {Pout[iP]:.0f} W"), fontsize=8.5, color=d.VR)
a1.text(200, 3.0, T("转矩", "torque"), color=d.VA, fontsize=9); b1.text(3300, 110, T("功率", "power"), color=d.VR, fontsize=9)
a1.spines["top"].set_visible(False); b1.spines["top"].set_visible(False)
a2.plot(tau[sl], eta[sl] * 100, color=d.VB, lw=2)
a2.plot(tau[iE], eta[iE] * 100, "o", color=d.VB)
a2.text(tau[iE] + 0.15, eta[iE] * 100 + 1, T(f"最高 {eta[iE] * 100:.0f}%", f"max {eta[iE] * 100:.0f}%"), fontsize=8.5, color=d.VB)
a2.plot(tau[iP], eta[iP] * 100, "o", color=d.VR)
a2.text(tau[iP] + 0.1, eta[iP] * 100 + 3, T("最大功率处", "at max power"), fontsize=8.5, color=d.VR)
a2.set_xlabel(T("输出转矩 / (N·m)", "output torque / (N·m)")); a2.set_ylabel(T("效率 / %", "efficiency / %"))
a2.set_xlim(0, 3.1); a2.set_ylim(0, 100); d.spines(a2)
fig.tight_layout()
figure(fig, "fig9_5_1")

# ---- 图 9.5.2：功率的去向（传动比 100）与总效率随传动比的变化
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.9), gridspec_kw={"width_ratios": [1.25, 1]})
steps = [(T("电池", "battery"), c["Pbat"], None), (T("驱动器损耗", "driver loss"), -c["Pdrv"], d.MUTED),
         (T("铜损 I²R", "copper loss I²R"), -c["Pcu"], d.VR), (T("电机摩擦", "motor friction"), -c["Pfr"], d.MUTED),
         (T("减速器损耗", "gear loss"), -c["Pgear"], d.VR), (T("关节输出", "joint output"), c["Pj"], None)]
level, y = 0.0, 0
for name, val, col in steps:
    if col is None:
        a1.barh(y, val, color=d.VA if y == 0 else d.VB, height=0.6)
        a1.text(val + 5, y, f"{val:.0f} W", va="center", fontsize=8.5)
        level = val
    else:
        a1.barh(y, -val, left=level + val, color=col, height=0.6, alpha=0.8)
        a1.text(level + 5, y, f"−{-val:.0f} W", va="center", fontsize=8.5)
        level += val
    y -= 1
a1.set_yticks(range(0, -len(steps), -1)); a1.set_yticklabels([s_[0] for s_ in steps], fontsize=8.5)
a1.set_xlim(0, 360); a1.set_xlabel(T("功率 / W", "power / W")); d.spines(a1)
a1.set_title(T("(a) 传动比 100 时功率的去向", "(a) where the power goes, ratio 100"), fontsize=9.5)
a2.plot(ii[ok], etas[ok] * 100, color=d.VB, lw=2)
a2.plot(ii[ii >= ii[ok][-1]], etas[ii >= ii[ok][-1]] * 100, color=d.VB, lw=1, ls=":")
assert ok[0], "传动比 40 时应能达到"
hi = int(ii[ok][-1])
a2.axvspan(hi, 220, color=d.MUTED, alpha=0.15, lw=0)
a2.text(hi - 4, 18, T("24 V 电源\n电压不够 →", "24 V supply\ntoo low →"), fontsize=8, color=d.MUTED, ha="right")
a2.plot(100, c["eta"] * 100, "o", color=d.VB)
a2.set_xlabel(T("传动比 i", "gear ratio i")); a2.set_ylabel(T("总效率 / %", "overall efficiency / %"))
a2.set_xlim(40, 220); a2.set_ylim(0, 80); d.spines(a2)
a2.set_title(T("(b) 总效率与传动比", "(b) overall efficiency vs ratio"), fontsize=9.5)
fig.tight_layout()
figure(fig, "fig9_5_2")

# ---- 图 9.5.3：单关节的转矩、角速度、功率（画图只取每 20 个点中的 1 个）
t, th, om, tq, P = (a_[::20] for a_ in (t, th, om, tq, P))
fig, axs = plt.subplots(3, 1, figsize=(4.8, 4.6), sharex=True)
axs[0].plot(t, om, color=d.VA, lw=2); axs[0].set_ylabel(T("角速度\n/ (rad/s)", "angular speed\n/ (rad/s)"))
axs[1].plot(t, tq, color=d.VB, lw=2); axs[1].plot(t, G * np.cos(th), color=d.MUTED, lw=1, ls="--")
axs[1].text(0.02, 24, T("只有重力矩", "gravity torque only"), fontsize=8, color=d.MUTED)
axs[1].set_ylabel(T("关节转矩\n/ (N·m)", "joint torque\n/ (N·m)"))
axs[2].fill_between(t, P, color=d.VR, alpha=0.15, lw=0); axs[2].plot(t, P, color=d.VR, lw=2); axs[2].axhline(0, color=d.MUTED, lw=0.6)
axs[2].text(0.5, 8, T(f"面积 = {Wj:.1f} J = 升高所需的功", f"area = {Wj:.1f} J = work to raise"), fontsize=8.5, color=d.VR)
axs[2].set_ylabel(T("功率 / W", "power / W")); axs[2].set_xlabel(T("时间 t / s", "time t / s"))
for a_ in axs:
    d.spines(a_)
fig.align_ylabels(axs)
fig.tight_layout()
figure(fig, "fig9_5_3")
