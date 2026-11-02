"""图 21.2.1：工具姿态从 R₀ 转到 R₁ 的两种插值。(a) 工具坐标系三根轴的端点在单位球上走过的路径（正交投影）：
指数插值 R₀exp(t·log(R₀ᵀR₁)) 绕一根固定的轴匀速转动；元素线性插值得到的矩阵不是旋转矩阵，轴变短、不再正交；
(b) 已转过的角度与 t 的关系：指数插值是直线，线性插值后再正交化（取最近的旋转矩阵）的转速不均匀；
线性插值的 ‖RᵀR − I‖₂ 与 det R。"""
import math

import numpy as np
from scipy.linalg import expm, logm

from _fig import BLUE, GREEN, INK, MUTED, RED, T, arrow3, figure, plt, view3


def rot(axis, ang):
    k = np.asarray(axis, float) / np.linalg.norm(axis)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K


R0 = rot([0, 0, 1], math.radians(20))
R1 = rot([1, 0, 0], math.radians(90)) @ rot([0, 0, 1], math.radians(30))
W = np.real(logm(R0.T @ R1))
ts = np.linspace(0, 1, 101)
Rexp = [R0 @ expm(t * W) for t in ts]
Rlin = [(1 - t) * R0 + t * R1 for t in ts]
P, _ = view3(35, 22)
fig = plt.figure(figsize=(12, 4.8))
a1 = fig.add_subplot(1, 2, 1)
a1.set_aspect("equal")
a1.axis("off")
u = np.linspace(0, 2 * math.pi, 200)
for M in (np.array([np.cos(u), np.sin(u), 0 * u]), np.array([np.cos(u), 0 * u, np.sin(u)]), np.array([0 * u, np.cos(u), np.sin(u)])):
    q = np.array([P(p) for p in M.T])
    a1.plot(q[:, 0], q[:, 1], color=MUTED, lw=0.5, alpha=0.5)
cols = (RED, GREEN, BLUE)
for j in range(3):
    pe = np.array([P(R[:, j]) for R in Rexp])
    pl = np.array([P(R[:, j]) for R in Rlin])
    a1.plot(pe[:, 0], pe[:, 1], color=cols[j], lw=2)
    a1.plot(pl[:, 0], pl[:, 1], color=cols[j], lw=1.3, ls="--")
    arrow3(a1, P, (0, 0, 0), R0[:, j], cols[j], lw=1.2)
    arrow3(a1, P, (0, 0, 0), R1[:, j], cols[j], lw=2.2)
    arrow3(a1, P, (0, 0, 0), Rlin[50][:, j], INK, lw=1.0)
ax_ = np.array([W[2, 1], W[0, 2], W[1, 0]])
ax_ = ax_ / np.linalg.norm(ax_)
pa = P(1.25 * ax_)
pb = P(-1.25 * ax_)
a1.plot([pb[0], pa[0]], [pb[1], pa[1]], color=INK, lw=1, ls=":")
a1.text(pa[0], pa[1] + 0.05, T("转轴", "axis"), fontsize=9, color=INK)
a1.set_title(T("(a) 三根轴的端点：实线为指数插值，虚线为元素线性插值\n（细箭头 R₀，粗箭头 R₁，黑箭头为线性插值 t = 0.5）",
               "(a) Tips of the three axes: solid = exponential, dashed = entrywise linear\n(thin arrows R₀, thick R₁, black: linear at t = 0.5)"), fontsize=10)
a2 = fig.add_subplot(1, 2, 2)
ang = lambda R: math.degrees(math.acos(max(-1, min(1, (np.trace(R0.T @ R) - 1) / 2))))
ae = [ang(R) for R in Rexp]
al = []
for R in Rlin:
    U, _, Vt = np.linalg.svd(R)
    al.append(ang(U @ Vt))
a2.plot(ts, ae, color=BLUE, lw=2, label=T("指数插值：转角 ∝ t", "exponential: angle ∝ t"))
a2.plot(ts, al, color=RED, lw=1.6, ls="--", label=T("线性插值后正交化", "linear, then orthogonalized"))
a2.set_xlabel("t")
a2.set_ylabel(T("已转过的角度 / (°)", "angle turned / (°)"))
a3 = a2.twinx()
a3.plot(ts, [np.linalg.norm(R.T @ R - np.eye(3), 2) for R in Rlin], color=MUTED, lw=1.2, label=T("线性插值的 ‖RᵀR − I‖₂", "linear: ‖RᵀR − I‖₂"))
a3.plot(ts, [np.linalg.det(R) for R in Rlin], color=GREEN, lw=1.2, label=T("线性插值的 det R", "linear: det R"))
a3.set_ylim(0, 1.05)
a3.set_ylabel(T("‖RᵀR − I‖₂，det R", "‖RᵀR − I‖₂, det R"))
h1, l1 = a2.get_legend_handles_labels()
h2, l2 = a3.get_legend_handles_labels()
a2.legend(h1 + h2, l1 + l2, frameon=False, fontsize=8.5, loc="upper left")
a2.set_title(T("(b) 转角随 t 的变化；线性插值离旋转矩阵多远", "(b) Angle turned versus t; how far linear interpolation is from a rotation"), fontsize=10)
fig.tight_layout()
figure(fig, "fig21_2_1")
