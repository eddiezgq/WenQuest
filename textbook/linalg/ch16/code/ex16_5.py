"""16.5 节：反对称矩阵的指数是旋转。
(1) [ω]× 的指数：罗德里格斯公式 e^{[ω]×θ} = I + sinθ[ω]× + (1 − cosθ)[ω]×²（‖ω‖ = 1）与 expm 比较；正交、行列式为 1、转轴是 ω；
(2) 二维：e^{θJ}，J = [[0, −1], [1, 0]]，就是转角 θ 的旋转矩阵；
(3) det e^A = e^{tr A}（随机矩阵检验）；
(4) IMU 姿态积分（11.2 节）：陀螺仪读数 ω = (0.3, −0.5, 1.2) rad/s 恒定，Δt = 0.01 s，积分 60 s。
    欧拉法 R ← R(I + [ω]×Δt) 的正交性误差与姿态误差；指数法 R ← R e^{[ω]×Δt} 保持正交，姿态与精确值 e^{[ω]×t} 一致。"""
import math

import numpy as np
import scipy.linalg as sl

from _num import sci
from bookout import out, tex, vec


def hat(w):
    return np.array([[0.0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def rodrigues(w, th):
    K = hat(w)
    return np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * K @ K


wv = np.array([1.0, 2, 2]) / 3
th = math.radians(60)
R = rodrigues(wv, th)
out(K=tex(hat(wv), 3), R=tex(R, 4), err_rod=sci(float(np.abs(R - sl.expm(hat(wv) * th)).max()) + 1e-18, 0),
    orth=sci(float(np.abs(R.T @ R - np.eye(3)).max()) + 1e-18, 0), detR=float(np.linalg.det(R)),
    axis_ok=bool(np.allclose(R @ wv, wv)), trace_angle=float(math.degrees(math.acos((np.trace(R) - 1) / 2))))
# K³ = −K
out(K3=bool(np.allclose(np.linalg.matrix_power(hat(wv), 3), -hat(wv))))
# (2)
Jm = np.array([[0.0, -1], [1, 0]])
out(e2=tex(sl.expm(Jm * th), 4), rot_ok=bool(np.allclose(sl.expm(Jm * th), [[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])))
# (3)
rng = np.random.default_rng(165)
Ar = rng.normal(size=(4, 4))
out(det_e=float(np.linalg.det(sl.expm(Ar))), e_tr=float(math.exp(np.trace(Ar))))
# (4) IMU
w = np.array([0.3, -0.5, 1.2])
dt, n = 0.01, 6000
Re, Rx = np.eye(3), np.eye(3)
Ee, Ex = np.eye(3) + hat(w) * dt, sl.expm(hat(w) * dt)
for _ in range(n):
    Re, Rx = Re @ Ee, Rx @ Ex
Rt = sl.expm(hat(w) * dt * n)


def ang(Ra, Rb):
    c = (np.trace(Ra.T @ Rb) - 1) / 2
    return math.degrees(math.acos(max(-1, min(1, c))))


U, _, Vt = np.linalg.svd(Re)
out(orth_e=float(np.abs(Re.T @ Re - np.eye(3)).max()), det_e60=float(np.linalg.det(Re)),
    orth_x=sci(float(np.abs(Rx.T @ Rx - np.eye(3)).max()) + 1e-18, 0), err_x=sci(float(np.abs(Rx - Rt).max()) + 1e-18, 0),
    ang_e=ang(U @ Vt, Rt), stretch=float(np.linalg.svd(Re, compute_uv=False).max()),
    step_norm=float(np.linalg.svd(Ee, compute_uv=False).max()), wnorm=float(np.linalg.norm(w)))
