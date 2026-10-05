"""11.2 节：格拉姆–施密特正交化。a = (1, −1, 0)、b = (2, 0, −2)、c = (3, −3, 3) 化为标准正交基；
病态矩阵（列几乎相关）上经典与修正格拉姆–施密特的正交性损失；IMU 陀螺积分得到的姿态矩阵逐渐失去正交性，每一步重新正交化后保持正交。"""
import numpy as np

from _gs import cgs, cgs2, mgs, orth_err
from _num import sci
from bookout import out, tex, vec

A = np.array([[1.0, -1, 0], [2, 0, -2], [3, -3, 3]]).T
Q, R = cgs(A)
B = A[:, 1] - (Q[:, 0] @ A[:, 1]) * Q[:, 0]
C = A[:, 2] - (Q[:, 0] @ A[:, 2]) * Q[:, 0] - (Q[:, 1] @ A[:, 2]) * Q[:, 1]
out(B=vec(B, 0), C=vec(C, 0), q1=vec(Q[:, 0], 4), q2=vec(Q[:, 1], 4), q3=vec(Q[:, 2], 4), QtQ=float(np.abs(Q.T @ Q - np.eye(3)).max()))
# 病态的例子：希尔伯特矩阵 H_ij = 1/(i + j − 1) 的前 n 列
rows = []
for n in (6, 8, 10, 12):
    H = 1.0 / (np.arange(1, n + 1)[:, None] + np.arange(1, n + 1)[None, :] - 1)
    kap = np.linalg.cond(H)
    rows.append((n, kap, orth_err(cgs(H)[0]), orth_err(mgs(H)[0]), orth_err(cgs2(H)[0]), orth_err(np.linalg.qr(H)[0])))
for n, kap, e1, e2, e3, e4 in rows:
    out(**{f"k{n}": sci(kap, 0), f"c{n}": sci(e1, 0), f"m{n}": sci(e2, 0), f"c2{n}": sci(e3, 0), f"h{n}": sci(e4, 0)})


# IMU：角速度 ω(t) 积分得到姿态 R(t)，一阶欧拉法 R ← R (I + [ω]× dt)
def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def omega(t):
    return np.array([0.6 * np.sin(0.7 * t), 0.4 * np.cos(0.5 * t), 0.9 + 0.3 * np.sin(1.1 * t)])   # rad/s


dt, T = 0.01, 60.0
Ra, Rb = np.eye(3), np.eye(3)
log = []
for k in range(int(T / dt)):
    W = np.eye(3) + skew(omega(k * dt)) * dt
    Ra = Ra @ W
    Rb = Rb @ W
    Rb, _ = mgs(Rb)                       # 每一步重新正交化（列做格拉姆–施密特）
    if (k + 1) % 1000 == 0:
        log.append(((k + 1) * dt, orth_err(Ra), orth_err(Rb), np.linalg.det(Ra)))
out(imu=[[int(round(t)), float(e1), float(e2), float(d)] for t, e1, e2, d in log])
t60, ea, eb, da = log[-1]
tool = np.array([0.0, 0.0, 0.2])                               # 工具在法兰坐标系中 0.2 m 处
out(ea60=sci(ea, 1), eb60=sci(eb, 0), det60=float(da), ea10=sci(log[0][1], 1),
    toollen=float(np.linalg.norm(Ra @ tool)) * 1000, toollen_b=float(np.linalg.norm(Rb @ tool)) * 1000)
