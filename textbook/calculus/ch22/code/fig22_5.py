"""图 22.5.1：左：UR5e 上臂自由摆动（h = 10 ms）四种方法的能量误差；右：简谐振子一圈初值在显式欧拉与辛欧拉下走 40 步后的像（面积）。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

m, d, I, g = 8.393, 0.2125, 0.5129, 9.81
c = m * g * d / I
acc = lambda q: -c * np.cos(q)
E = lambda q, v: 0.5 * v * v + c * np.sin(q)
h, TT = 0.01, 100.0
N = round(TT / h)


def run(kind):
    q, v = 0.0, 0.0
    es = np.empty(N)
    for n in range(N):
        if kind == "eu":
            q, v = q + h * v, v + h * acc(q)
        elif kind == "sy":
            v = v + h * acc(q); q = q + h * v
        elif kind == "lf":
            v = v + h / 2 * acc(q); q = q + h * v; v = v + h / 2 * acc(q)
        else:
            y = np.array([q, v]); F = lambda y: np.array([y[1], acc(y[0])])
            k1 = F(y); k2 = F(y + h / 2 * k1); k3 = F(y + h / 2 * k2); k4 = F(y + h * k3)
            q, v = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        es[n] = E(q, v) / c
    return es


tt = np.arange(1, N + 1) * h
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
env = lambda e: np.abs(e).reshape(-1, 100).max(axis=1)     # 每 1 s 内 |ΔE| 的最大值
t1 = np.arange(1, N // 100 + 1) * 1.0
a1.semilogy(t1, env(run("eu")), color=RED, lw=2, label=T("显式欧拉", "explicit Euler"))
a1.semilogy(t1, env(run("sy")), color=GREEN, lw=2, label=T("辛欧拉（半隐式）", "symplectic (semi-implicit) Euler"))
a1.semilogy(t1, env(run("lf")), color=ACC, lw=2, label=T("蛙跳法", "leapfrog"))
a1.semilogy(t1, env(run("rk4")), color=BLUE, lw=2, label="RK4")
a1.set_ylim(1e-8, 1e2)
a1.set_xlabel(T("时间 t / s", "time t / s")); a1.set_ylabel(T("每秒内最大的 |ΔE| / (mgd)", "max |ΔE| in each second / (mgd)"))
a1.set_title(T("步长 10 ms：欧拉法能量越来越大，辛欧拉有界，RK4 很小", "h = 10 ms: Euler gains energy, symplectic bounded, RK4 tiny"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="lower right", ncol=2); clean(a1, zero=False)
w, hh, n = 1.0, 0.15, 40
th = np.linspace(0, 2 * np.pi, 200)
q0, v0 = 1.0 + 0.25 * np.cos(th), 0.25 * np.sin(th)
for kind, col, lab in (("eu", RED, T("显式欧拉", "explicit Euler")), ("sy", GREEN, T("辛欧拉", "symplectic Euler"))):
    q, v = q0.copy(), v0.copy()
    for j in range(n):
        if kind == "eu":
            q, v = q + hh * v, v - hh * w * w * q
        else:
            v = v - hh * w * w * q; q = q + hh * v
    area = 0.5 * abs(np.sum(q * np.roll(v, -1) - np.roll(q, -1) * v))
    a2.fill(q, v, color=col, alpha=0.35, label=lab + T(f"：面积 × {area / (np.pi * 0.0625):.2f}", f": area × {area / (np.pi * 0.0625):.2f}"))
a2.fill(q0, v0, color=INK, alpha=0.5, label=T("初值（面积 × 1）", "initial set (area × 1)"))
ts = np.linspace(0, 2 * np.pi, 200)
a2.plot(np.cos(ts), np.sin(ts), color=MUTED, lw=0.8, ls="--")
a2.set_aspect("equal"); a2.set_xlabel(T("位移 q", "position q")); a2.set_ylabel(T("速度 v", "velocity v"))
a2.set_title(T(f"简谐振子 hω = {hh}，走 {n} 步", f"Harmonic oscillator hω = {hh}, {n} steps"), fontsize=10)
a2.legend(fontsize=8.5, frameon=False, loc="lower left", bbox_to_anchor=(0.0, -0.02)); clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig22_5_1")
