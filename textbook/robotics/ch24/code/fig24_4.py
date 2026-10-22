"""24.4 节的示意图。

图 24.4.1：算例 24.4.2：UR5e 关节 2、3（两自由度模型，空手）从水平伸直自由下落 60 s，h = 1 ms，机械能偏差 E(t) − E(0)。
          (a) 显式欧拉、半隐式欧拉；(b) RK4（单位 10⁻⁸ J）。
图 24.4.2：(a) 算例 24.4.3：四种错误方程自由下落 2 s 的机械能偏差（RK4，1 ms）；
          (b) 算例 24.4.5：双摆（两根 0.3 m、0.2 kg 的均匀细杆）从 (120°, 60°) 放开，初值差 10⁻⁹ rad 的两次仿真，上杆的转角（前 14 s）；
          (c) 两次仿真的机械能，第一次仿真的动能、势能（以两杆下垂为零点）。
"""
import math

import numpy as np

from _ch24 import Planar2, mjcf_text, parse_links, planar_params, rk4_step
from bookout import COLORS as C, T, figure, style

plt = style()
links = parse_links(mjcf_text())
P0 = planar_params(links)
X0 = np.zeros(4)


def integrate(P, x0, h, Tend, method="rk4", c_fun=None):
    x = np.array(x0, float)
    N = int(round(Tend / h))
    X = np.zeros((N + 1, 4))
    X[0] = x
    f = P.rhs((0.0, 0.0), c_fun)
    for k in range(N):
        if method == "rk4":
            x = rk4_step(f, x, h)
        else:
            a = P.fd(x[:2], x[2:], (0.0, 0.0), c_fun)
            if method == "euler":
                x = np.r_[x[:2] + h * x[2:], x[2:] + h * a]
            else:
                v = x[2:] + h * a
                x = np.r_[x[:2] + h * v, v]
        X[k + 1] = x
    return X


def dE(P, X, every=1):
    E = np.array([P.E(x[:2], x[2:]) for x in X[::every]])
    return E - E[0]


# ---------------------------------------------------------------- 图 24.4.1
h, TL, ev = 1e-3, 60.0, 20
t = np.arange(0, int(round(TL / h)) + 1, ev) * h
D = {m: dE(P0, integrate(P0, X0, h, TL, m), ev) for m in ("euler", "symp", "rk4")}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.0, 4.0))
a1.plot(t, D["euler"], color=C["x"], lw=1.0, label=T("显式欧拉", "explicit Euler"))
a1.plot(t, D["symp"], color=C["z"], lw=1.0, label=T("半隐式欧拉 = MuJoCo Euler", "semi-implicit Euler = MuJoCo Euler"))
a1.axhline(0, color=C["ink"], lw=0.6)
a1.set_xlabel(T("时间 t / s", "time t / s"))
a1.set_ylabel(T("机械能偏差 / J", "energy error / J"))
a1.legend(frameon=False, fontsize=9.5, loc="upper left")
a1.set_title(T("(a) 一阶方法：显式欧拉累积，半隐式欧拉慢得多", "(a) first order: explicit Euler drifts, semi-implicit Euler far less"),
             fontsize=11, loc="left")
a2.plot(t, D["rk4"] * 1e8, color=C["y"], lw=1.0, label="RK4")
a2.axhline(0, color=C["ink"], lw=0.6)
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.set_ylabel(T("机械能偏差 / (10⁻⁸ J)", "energy error / (10⁻⁸ J)"))
a2.legend(frameon=False, fontsize=9.5, loc="lower left")
a2.set_title(T("(b) RK4：误差极小，缓慢累积", "(b) RK4: tiny error, slowly accumulating"), fontsize=11, loc="left")
for ax in (a1, a2):
    ax.set_xlim(0, TL)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
figure(fig, "fig24_4_1")

# ---------------------------------------------------------------- 图 24.4.2
def c_half(P, p, pd):
    hh = P.hh(p[1])
    return np.array([-hh * (pd[0] * pd[1] + pd[1] ** 2), hh * pd[0] ** 2])


def c_sign(P, p, pd):
    hh = P.hh(p[1])
    return np.array([-hh * (2 * pd[0] * pd[1] + pd[1] ** 2), -hh * pd[0] ** 2])


class NoBeta(Planar2):
    def M(self, p):
        A = super().M(p)
        b = self.beta(p[1])
        return A - np.array([[0.0, b], [b, 0.0]])


class NoG2(Planar2):
    def g(self, p):
        A = super().g(p)
        return A - np.array([self.m2 * self.g0 * (self.a1 * math.cos(p[0]) + self.r2 * math.cos(p[0] + p[1])
                                                  - self.s2 * math.sin(p[0] + p[1])), 0.0])


kw = {k: getattr(P0, k) for k in ("a1", "m1", "r1", "s1", "J1", "m2", "r2", "s2", "J2")}
TB = 2.0
tb = np.arange(int(round(TB / h)) + 1) * h
bugs = [(T("正确", "correct"), P0, None, C["ink"]),
        (T("(a) 科氏项漏系数 2", "(a) Coriolis without factor 2"), P0, c_half, C["x"]),
        (T("(b) 离心项符号反", "(b) centrifugal sign flipped"), P0, c_sign, C["accent"]),
        (T("(c) M₁₂ 漏 β", "(c) M₁₂ missing β"), NoBeta(**kw, arm=P0.arm), None, C["z"]),
        (T("(d) g₁ 漏连杆 2", "(d) g₁ missing link 2"), NoG2(**kw, arm=P0.arm), None, C["y"])]
fig = plt.figure(figsize=(13.4, 4.2))
gs = fig.add_gridspec(1, 3, wspace=0.32)
b1, b2, b3 = (fig.add_subplot(gs[0, k]) for k in range(3))
for lab, P, cf, col in bugs:
    X = integrate(P, X0, h, TB, "rk4", cf)
    b1.plot(tb, dE(P, X), color=col, lw=1.3, label=lab)
b1.set_yscale("symlog", linthresh=1.0)
b1.set_xlabel(T("时间 t / s", "time t / s"))
b1.set_ylabel(T("机械能偏差 / J", "energy error / J"))
b1.legend(frameon=False, fontsize=8.6, loc="upper left")
b1.set_title(T("(a) 能量检验找出错误", "(a) the energy test catches the bugs"), fontsize=11, loc="left")

Ld, md = 0.3, 0.2
DP = Planar2(Ld, md, Ld / 2, 0.0, md * Ld ** 2 / 3, md, Ld / 2, 0.0, md * Ld ** 2 / 3)
xd = np.array([math.radians(120), math.radians(60), 0.0, 0.0])
TD = 20.0
A_ = integrate(DP, xd, h, TD)
B_ = integrate(DP, xd + np.array([1e-9, 0, 0, 0]), h, TD)
td = np.arange(len(A_)) * h
TS = 14.0
ns = int(round(TS / h)) + 1
b2.plot(td[:ns], A_[:ns, 0], color=C["z"], lw=1.0, label=T("初值 (120°, 60°)", "start (120°, 60°)"))
b2.plot(td[:ns], B_[:ns, 0], color=C["x"], lw=1.0, ls="--", label=T("φ₁ 多 10⁻⁹ rad", "φ₁ + 10⁻⁹ rad"))
gap = np.abs(A_[:, :2] - B_[:, :2]).max(1)
t_div = float(np.argmax(gap > 0.1) * h)
b2.axvline(t_div, color=C["muted"], lw=0.8, ls=":")
yl = b2.get_ylim()
b2.text(t_div - 0.3, yl[1] - 0.06 * (yl[1] - yl[0]), T(f"{t_div:.1f} s 后分开", f"apart after {t_div:.1f} s"), fontsize=9.5,
        color=C["muted"], ha="right")
b2.set_xlabel(T("时间 t / s", "time t / s"))
b2.set_ylabel(T("上杆的转角 φ₁ / rad（不折回）", "upper rod angle φ₁ / rad (unwrapped)"))
b2.set_xlim(0, TS)
b2.legend(frameon=False, fontsize=8.8, loc="lower left")
b2.set_title(T("(b) 双摆：初值相差 10⁻⁹ rad", "(b) double pendulum: start 10⁻⁹ rad apart"), fontsize=11, loc="left")
U0 = DP.U(np.array([-math.pi / 2, 0.0]))
EA = None
for X, ls, lw in ((A_, "-", 1.6), (B_, "--", 1.6)):
    K = np.array([DP.K(x[:2], x[2:]) for x in X[::10]])
    U = np.array([DP.U(x[:2]) for x in X[::10]]) - U0
    if EA is None:
        b3.plot(td[::10], K, color=C["x"], lw=0.6, alpha=0.8)
        b3.plot(td[::10], U, color=C["z"], lw=0.6, alpha=0.8)
        EA = K + U
    b3.plot(td[::10], K + U, color=C["ink"], lw=lw, ls=ls)
b3.text(0.4, EA[0] + 0.1, T("机械能 E = K + U（两次仿真重合）", "E = K + U (both runs coincide)"), fontsize=9.5)
b3.text(20.3, 1.2, T("动能 K", "K"), fontsize=9.5, color=C["x"])
b3.text(20.3, 0.5, T("势能 U", "U"), fontsize=9.5, color=C["z"])
b3.set_xlabel(T("时间 t / s", "time t / s"))
b3.set_ylabel(T("能量 / J", "energy / J"))
b3.set_ylim(-0.1, 2.4)
b3.set_xlim(0, 23)
b3.set_title(T("(c) 轨迹不同，能量都守恒", "(c) different paths, both conserve energy"), fontsize=11, loc="left")
for ax in (b1, b2, b3):
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
figure(fig, "fig24_4_2")
