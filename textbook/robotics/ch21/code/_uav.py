"""第 21 章共用：零件库四旋翼 X2（B-UAV-X2）的几何与推力数据，转动的基本运算，
由推力方向和偏航角求姿态，微分平坦映射，过航点的最小 k 阶导数样条。以下划线开头，构建时不单独运行。

数据来源：
- textbook/robotics/models/B-UAV-X2/entry.json：零件库条目（质量 1.325 kg）；
- 模型的 MJCF 原文件 skydio_x2/x2.xml（MuJoCo Menagerie，提交 4d038b3feae26ec82b46a4d586379114012a8ac7）。
  关节表之外的事实抄在下面的 MJCF 字典里，与第 1 章 code/_ch1.py 中的同名数据一致：
    <geom name="rotor1" class="rotor" pos="-.14 -.18 .05" mass=".25"/> …（四个旋翼，各 0.25 kg）
    <geom size=".16 .04 .02" pos="0 0 0.02" type="ellipsoid" mass=".325" …/>（机身，0.325 kg）
    <motor ctrlrange="0 13"/>；<motor … site="thrust1" gear="0 0 1 0 0 -.0201"/> …
    <site name="imu" pos="0 0 .02"/>；<key name="hover" … ctrl="3.2495625 …"/>
"""
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MODELS = HERE.parents[1] / "models"
G = 9.81                                               # 重力加速度 𝔤，m/s²（符号约定第九节）

MJCF = {
    "rotor_xyz": [(-0.14, -0.18, 0.05), (-0.14, 0.18, 0.05), (0.14, 0.18, 0.08), (0.14, -0.18, 0.08)],
    "rotor_mass": 0.25,
    "body_xyz": (0.0, 0.0, 0.02), "body_mass": 0.325,
    "yaw_gear": [-0.0201, 0.0201, -0.0201, 0.0201],     # gear 的第 6 个分量：每牛推力产生的绕 z_b 力矩（N·m/N = m）
    "thrust_max": 13.0,                                # ctrlrange="0 13"，每个旋翼的推力上限，N
    "hover_ctrl": 3.2495625,                           # 悬停关键帧的推力指令，N
    "imu_xyz": (0.0, 0.0, 0.02),
}


def entry():
    return json.loads((MODELS / "B-UAV-X2" / "entry.json").read_text(encoding="utf-8"))


def x2():
    """X2 的参数：质量、质心（MJCF 机体坐标系）、以质心为原点的旋翼位置、反扭矩系数与符号、推力上限。"""
    e = entry()
    m_entry = sum(l.get("mass_kg") or 0.0 for l in e["robot"]["links"])
    pts = [np.array(p) for p in MJCF["rotor_xyz"]] + [np.array(MJCF["body_xyz"])]
    ms = [MJCF["rotor_mass"]] * 4 + [MJCF["body_mass"]]
    m = sum(ms)
    assert abs(m - m_entry) < 1e-12                    # 零件库条目与 MJCF 的质量一致
    com = sum(mi * p for mi, p in zip(ms, pts)) / m
    r = [np.array(p) - com for p in MJCF["rotor_xyz"]]  # 以质心为原点的旋翼中心位置（{b} 中的分量）
    c = abs(MJCF["yaw_gear"][0])
    sig = [int(np.sign(g)) for g in MJCF["yaw_gear"]]  # 反扭矩的符号：−1 表示给机体顺时针（从上往下看）的力矩
    return dict(m=m, com=com, r=r, c=c, sig=sig, fmax=MJCF["thrust_max"], hover=MJCF["hover_ctrl"],
                lx=abs(MJCF["rotor_xyz"][0][0]), ly=abs(MJCF["rotor_xyz"][0][1]), imu=np.array(MJCF["imu_xyz"]) - com)


def alloc(P):
    """4×4 推力分配矩阵：(f, m_x, m_y, m_z) = A (f_1, …, f_4)；A6 为 6×4 的力旋量矩阵 ℱ_b = (m_b, f_b)。"""
    A6 = np.zeros((6, 4))
    for i, (ri, si) in enumerate(zip(P["r"], P["sig"])):
        fz = np.array([0.0, 0.0, 1.0])
        A6[0:3, i] = np.cross(ri, fz) + si * P["c"] * fz
        A6[3:6, i] = fz
    A = np.vstack([A6[5], A6[0], A6[1], A6[2]])
    return A, A6


# ---------------------------------------------------------------- 转动

def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def unskew(S):
    return np.array([S[2, 1], S[0, 2], S[1, 0]])


def rotx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def roty(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rotz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def eul(psi, th, phi):
    """ZYX 欧拉角 (ψ, θ, φ) → R（式 (4.5.2)）。"""
    return rotz(psi) @ roty(th) @ rotx(phi)


def eul_of(R):
    """式 (4.5.4)：R → (ψ, θ, φ)，θ ∈ [−90°, 90°]。"""
    th = math.atan2(-R[2, 0], math.hypot(R[0, 0], R[1, 0]))
    return math.atan2(R[1, 0], R[0, 0]), th, math.atan2(R[2, 1], R[2, 2])


def expso3(w):
    """罗德里格斯公式：exp([w])。"""
    t = np.linalg.norm(w)
    if t < 1e-14:
        return np.eye(3) + skew(w)
    K = skew(w / t)
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def logso3(R):
    c = max(-1.0, min(1.0, (np.trace(R) - 1) / 2))
    t = math.acos(c)
    if t < 1e-10:
        return unskew(R - R.T) / 2
    return t / (2 * math.sin(t)) * unskew(R - R.T)


def Wmat(phi, th):
    """ω_b = W(φ, θ) (φ̇, θ̇, ψ̇)：ZYX 欧拉角速率与物体角速度。"""
    return np.array([[1, 0, -math.sin(th)],
                     [0, math.cos(phi), math.sin(phi) * math.cos(th)],
                     [0, -math.sin(phi), math.cos(phi) * math.cos(th)]])


# ---------------------------------------------------------------- 姿态与位置的耦合（21.2 节）

EZ = np.array([0.0, 0.0, 1.0])


def attitude(zb, psi):
    """定理 21.2.1：由推力方向 z_b 和偏航角 ψ 求 R（构造法），并用欧拉角公式 (21.2.6) 核对。"""
    yc = np.array([-math.sin(psi), math.cos(psi), 0.0])
    xb = np.cross(yc, zb)
    xb /= np.linalg.norm(xb)
    yb = np.cross(zb, xb)
    R = np.column_stack([xb, yb, zb])
    w = rotz(psi).T @ zb
    phi = math.atan2(-w[1], math.hypot(w[0], w[2]))
    th = math.atan2(w[0], w[2])
    assert np.allclose(R, eul(psi, th, phi), atol=1e-12)
    return R, th, phi


def flat(d, psi, dpsi, ddpsi, m):
    """微分平坦映射（21.4 节）：d = [p, ṗ, p̈, p⃛, p⁽⁴⁾]（各为 3 维），偏航 ψ 及其一、二阶导数 →
    姿态 R、总推力 f、物体角速度 ω_b、物体角加速度 ω̇_b，以及欧拉角 (θ, φ) 与它们的速率。"""
    a, j, s = d[2], d[3], d[4]
    t = a + G * EZ
    nt = np.linalg.norm(t)
    f = m * nt
    zb = t / nt
    R, th, phi = attitude(zb, psi)
    xb, yb = R[:, 0], R[:, 1]
    P = np.eye(3) - np.outer(zb, zb)
    h = P @ j / nt                                     # ż_b，式 (21.2.8)
    wx, wy = -yb @ h, xb @ h                           # 式 (21.2.10)、(21.4.2)
    wz = (math.cos(th) * dpsi - math.sin(phi) * wy) / math.cos(phi)   # 式 (21.4.3)
    w = np.array([wx, wy, wz])
    # 欧拉角速率：(φ̇, θ̇, ψ̇) = W⁻¹ ω_b
    rates = np.linalg.solve(Wmat(phi, th), w)
    assert abs(rates[2] - dpsi) < 1e-9
    # 角加速度：对 ż_b 再求导
    dnt = zb @ j
    dP = -(np.outer(h, zb) + np.outer(zb, h))
    dh = (dP @ j + P @ s) / nt - P @ j * dnt / nt ** 2
    dxb = R @ np.cross(w, [1, 0, 0])
    dyb = R @ np.cross(w, [0, 1, 0])
    dwx = -(dyb @ h + yb @ dh)
    dwy = dxb @ h + xb @ dh
    dphi, dth = rates[0], rates[1]
    # ω_z = (cθ ψ̇ − sφ ω_y)/cφ 对时间求导
    num = math.cos(th) * dpsi - math.sin(phi) * wy
    dnum = -math.sin(th) * dth * dpsi + math.cos(th) * ddpsi - math.cos(phi) * dphi * wy - math.sin(phi) * dwy
    dwz = (dnum * math.cos(phi) + num * math.sin(phi) * dphi) / math.cos(phi) ** 2
    return dict(R=R, f=f, w=w, dw=np.array([dwx, dwy, dwz]), th=th, phi=phi, rates=rates, zb=zb, h=h, df=m * dnt)


# ---------------------------------------------------------------- 过航点的最小 k 阶导数样条（21.4 节）

def _fact(n, r):
    """d^r/ds^r s^n 的系数 n!/(n−r)!（n < r 时为 0）。"""
    if r > n:
        return 0.0
    out = 1.0
    for i in range(r):
        out *= n - i
    return out


def min_deriv_spline(W, Ts, k):
    """最小化 ∫‖p⁽ᵏ⁾‖² dt 的插值：每段 2k−1 次多项式，中间航点处 1…2k−2 阶导数连续，起止点 1…k−1 阶导数为零（定理 21.4.2）。
    W：(n+1)×dim 航点；Ts：各段时长。每段用归一化时间 s = τ/T_j ∈ [0, 1]，系数 c[j] 为 2k×dim。返回 (C, Ts)。"""
    W = np.asarray(W, float)
    M, dim, N = len(Ts), W.shape[1], 2 * k
    A = np.zeros((N * M, N * M))
    B = np.zeros((N * M, dim))
    row = 0

    def put(j, s, r, scale=1.0):
        """第 j 段在 s 处的 r 阶导数（对真实时间）作为一行的系数。"""
        v = np.zeros(N * M)
        for n in range(N):
            if n >= r:
                v[j * N + n] = _fact(n, r) * s ** (n - r) / Ts[j] ** r * scale
        return v

    A[row] = put(0, 0.0, 0); B[row] = W[0]; row += 1
    for r in range(1, k):
        A[row] = put(0, 0.0, r); row += 1
    for j in range(M - 1):
        A[row] = put(j, 1.0, 0); B[row] = W[j + 1]; row += 1
        A[row] = put(j + 1, 0.0, 0); B[row] = W[j + 1]; row += 1
        for r in range(1, 2 * k - 1):
            A[row] = put(j, 1.0, r) - put(j + 1, 0.0, r); row += 1
    A[row] = put(M - 1, 1.0, 0); B[row] = W[-1]; row += 1
    for r in range(1, k):
        A[row] = put(M - 1, 1.0, r); row += 1
    assert row == N * M
    C = np.linalg.solve(A, B).reshape(M, N, dim)
    return C, np.asarray(Ts, float)


def spline_eval(C, Ts, t, r=0):
    """t 时刻（总时间轴）r 阶导数。"""
    tt = np.cumsum(np.r_[0.0, Ts])
    j = int(np.clip(np.searchsorted(tt, t, side="right") - 1, 0, len(Ts) - 1))
    s = (t - tt[j]) / Ts[j]
    N = C.shape[1]
    return sum((C[j, n] * _fact(n, r) * s ** (n - r) for n in range(r, N)), np.zeros(C.shape[2])) / Ts[j] ** r


def spline_cost(C, Ts, k, n=2000):
    """∫‖p⁽ᵏ⁾‖² dt（每段用复合辛普森法，n 为偶数）。"""
    tot = 0.0
    tt = np.cumsum(np.r_[0.0, Ts])
    for j in range(len(Ts)):
        x = np.linspace(tt[j], tt[j + 1], n + 1)
        y = np.array([np.sum(spline_eval_seg(C, Ts, j, xi - tt[j], k) ** 2) for xi in x])
        h = Ts[j] / n
        tot += h / 3 * (y[0] + y[-1] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum())
    return tot


def spline_eval_seg(C, Ts, j, tau, r=0):
    s = tau / Ts[j]
    N = C.shape[1]
    return sum((C[j, n] * _fact(n, r) * s ** (n - r) for n in range(r, N)), np.zeros(C.shape[2])) / Ts[j] ** r
