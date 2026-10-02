"""第 6 章共用：反对称矩阵、so(3) 与 se(3) 的指数和对数、伴随矩阵、李括号，UR5e 的旋量轴，以及示意图的画法。
以下划线开头，构建时不单独运行。

每个公式都按本章的编号实现；各程序再用与之独立的算法（级数、scipy 的 expm/logm、数值求导、几何作图）核对。
"""
import math

import numpy as np

from bookout import COLORS

C = COLORS
AXIS = (C["x"], C["y"], C["z"])


# ---------------------------------------------------------------- so(3)

def skew(w):
    """[ω]：叉积矩阵，[ω] p = ω × p（第 3 章）。"""
    w = np.asarray(w, float)
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def unskew(W):
    """由反对称矩阵读出矢量。"""
    return np.array([W[2, 1], W[0, 2], W[1, 0]])


def exp3(w_theta):
    """e^{[ω̂]θ}：罗德里格斯公式 (4.4.5)。参数为指数坐标 ω̂θ。"""
    w_theta = np.asarray(w_theta, float)
    t = float(np.linalg.norm(w_theta))
    if t < 1e-15:
        return np.eye(3)
    K = skew(w_theta / t)
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def log3(R):
    """SO(3) 的对数映射（4.4.6 节）：返回 (ω̂, θ)，θ ∈ [0, π]；R = I 时返回 (None, 0)。"""
    c = float(np.clip((np.trace(R) - 1) / 2, -1, 1))
    t = math.acos(c)
    if t < 1e-12:
        return None, 0.0
    if math.pi - t < 1e-6:
        B = (R + np.eye(3)) / 2
        j = int(np.argmax(np.diag(B)))
        w = B[:, j] / math.sqrt(B[j, j])
        return w / np.linalg.norm(w), math.pi
    return unskew((R - R.T) / (2 * math.sin(t))), t


def rot_x(t):
    return exp3([t, 0, 0])


def rot_y(t):
    return exp3([0, t, 0])


def rot_z(t):
    return exp3([0, 0, t])


# ---------------------------------------------------------------- se(3)

def bracket(V):
    """[V] = [[ω] v; 0 0]，式 (6.3.6)。"""
    V = np.asarray(V, float)
    m = np.zeros((4, 4))
    m[:3, :3] = skew(V[:3])
    m[:3, 3] = V[3:]
    return m


def unbracket(Vm):
    return np.r_[unskew(Vm[:3, :3]), Vm[:3, 3]]


def pose(R, p):
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = p
    return T


def inv(T):
    """T⁻¹ = (Rᵀ, −Rᵀp)（第 5 章）。"""
    R, p = T[:3, :3], T[:3, 3]
    return pose(R.T, -R.T @ p)


def G(w, t):
    """G(θ) = Iθ + (1 − cos θ)[ω̂] + (θ − sin θ)[ω̂]²，式 (6.4.3)。"""
    K = skew(w)
    return np.eye(3) * t + (1 - math.cos(t)) * K + (t - math.sin(t)) * K @ K


def G_inv(w, t):
    """G(θ)⁻¹ = I/θ − [ω̂]/2 + (1/θ − cot(θ/2)/2)[ω̂]²，式 (6.4.8)。"""
    K = skew(w)
    return np.eye(3) / t - K / 2 + (1 / t - 0.5 / math.tan(t / 2)) * K @ K


def exp6(S, t):
    """e^{[S]θ}，定理 6.4.1：转动部分用罗德里格斯公式，平移部分为 G(θ)v；ω = 0 时为平移 vθ。"""
    S = np.asarray(S, float)
    w, v = S[:3], S[3:]
    if np.linalg.norm(w) < 1e-12:
        return pose(np.eye(3), v * t)
    n = np.linalg.norm(w)              # 允许 ‖ω‖ ≠ 1：化成单位旋量轴乘以 ‖ω‖θ
    w, v, t = w / n, v / n, t * n
    return pose(exp3(w * t), G(w, t) @ v)


def log6(T):
    """SE(3) 的对数映射，定理 6.4.3：返回 (S, θ)，S 为旋量轴（‖ω‖ = 1，或 ω = 0、‖v‖ = 1）。"""
    R, p = T[:3, :3], T[:3, 3]
    w, t = log3(R)
    if w is None:
        d = float(np.linalg.norm(p))
        if d < 1e-15:
            return np.zeros(6), 0.0
        return np.r_[np.zeros(3), p / d], d
    return np.r_[w, G_inv(w, t) @ p], t


def expm_series(A, n=60):
    """矩阵指数的级数定义 (4.4.7)，用来独立核对闭式公式。"""
    S, term = np.eye(A.shape[0]), np.eye(A.shape[0])
    for k in range(1, n):
        term = term @ A / k
        S = S + term
    return S


def screw_from_axis(q, s, h):
    """由几何量（轴上一点 q、方向 ŝ、节距 h）写出旋量轴 S = (ŝ, −ŝ × q + hŝ)，式 (6.3.13)。"""
    s = np.asarray(s, float)
    return np.r_[s, -np.cross(s, np.asarray(q, float)) + h * s]


def axis_of(S):
    """由旋量轴（‖ω‖ = 1）读出几何量：ŝ、轴上离原点最近的点 q、节距 h，式 (6.3.11)、(6.3.12)。"""
    w, v = S[:3], S[3:]
    n2 = float(w @ w)
    return w / math.sqrt(n2), np.cross(w, v) / n2, float(w @ v) / n2


def adjoint(T):
    """[Ad_T] = [[R 0]; [[p]R R]]，式 (6.5.4)。"""
    R, p = T[:3, :3], T[:3, 3]
    A = np.zeros((6, 6))
    A[:3, :3] = R
    A[3:, 3:] = R
    A[3:, :3] = skew(p) @ R
    return A


def ad(V):
    """[ad_V] = [[ω] 0; [v] [ω]]，式 (6.7.5)。"""
    V = np.asarray(V, float)
    A = np.zeros((6, 6))
    A[:3, :3] = skew(V[:3])
    A[3:, 3:] = skew(V[:3])
    A[3:, :3] = skew(V[3:])
    return A


def lie(V1, V2):
    """李括号 [V1, V2]：矩阵对易子 [V1][V2] − [V2][V1] 再读出六维矢量，定义 6.7.1。"""
    A, B = bracket(V1), bracket(V2)
    return unbracket(A @ B - B @ A)


def clean(x, tol=1e-12):
    x = np.array(x, float)
    x[np.abs(x) < tol] = 0.0
    return x


# ---------------------------------------------------------------- UR5e（第 12 章表 12.1.1，零件库模型的尺寸）

H1, W1, L1, W2, L2, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1
_yd = np.array([0, -1.0, 0])
UR_AXES = [  # (ω̂, q)，{s} 为机器人基座坐标系
    (np.array([0, 0, 1.0]), np.array([0, 0, H1])),
    (_yd, np.array([0, -W1, H1])),
    (_yd, np.array([-L1, -W1 + W2, H1])),
    (_yd, np.array([-L1 - L2, -W1 + W2, H1])),
    (np.array([0, 0, -1.0]), np.array([-L1 - L2, -W1 + W2 - W3, H1])),
    (_yd, np.array([-L1 - L2, -W1 + W2 - W3, H1 - H2])),
]
UR_S = [np.r_[w, -np.cross(w, q)] for w, q in UR_AXES]
UR_M = np.array([[1.0, 0, 0, -L1 - L2], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]])


def ur_fk(theta, Slist=UR_S, M=UR_M):
    """指数积公式的空间形式（第 12 章式 (12.2.3)）。"""
    T = np.eye(4)
    for S, t in zip(Slist, theta):
        T = T @ exp6(S, t)
    return T @ M


# ---------------------------------------------------------------- 三维示意图

def axes3d(plt, size=(5.4, 4.4), elev=22, azim=-58):
    fig = plt.figure(figsize=size)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_proj_type("ortho")
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    return fig, ax


def equal3d(ax, pts, pad=0.05, zoom=1.0):
    pts = np.asarray(pts)
    lo, hi = pts.min(0) - pad, pts.max(0) + pad
    c, r = (lo + hi) / 2, (hi - lo).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1), zoom=zoom)


def tight3d(ax, pts, pad=0.03, zoom=1.0):
    """按各方向的实际范围设坐标范围和长宽比（不变形，也不留大片空白）。"""
    pts = np.asarray(pts)
    lo, hi = pts.min(0) - pad, pts.max(0) + pad
    ax.set_xlim(lo[0], hi[0])
    ax.set_ylim(lo[1], hi[1])
    ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect(tuple(hi - lo), zoom=zoom)


def frame3d(ax, T, size, label="", fs=11, lw=1.8, alpha=1.0, names=("x", "y", "z"), sub=None, show_axes_labels=True):
    o = T[:3, 3]
    for k in range(3):
        d = T[:3, k] * size
        ax.quiver(*o, *d, color=AXIS[k], lw=lw, arrow_length_ratio=0.15, alpha=alpha)
        if show_axes_labels:
            p = o + d * 1.18
            lab = rf"$\hat {names[k]}_{{{sub}}}$" if sub else rf"$\hat {names[k]}$"
            ax.text(*p, lab, color=AXIS[k], fontsize=fs - 1, ha="center", va="center", alpha=alpha)
    if label:
        ax.text(*(o - 0.25 * size * (T[:3, 0] + T[:3, 1])), label, fontsize=fs, ha="center", va="center", color=C["ink"])


def box3d(ax, T, dims=(0.12, 0.08, 0.05), face="#e9dfc8", edge="#8a6d2b", alpha=0.8):
    """一个长方体零件，中心与姿态由 T 给出。"""
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    a, b, c = (d / 2 for d in dims)
    V = np.array([[x, y, z] for x in (-a, a) for y in (-b, b) for z in (-c, c)])
    W = (T[:3, :3] @ V.T).T + T[:3, 3]
    faces = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
    ax.add_collection3d(Poly3DCollection([W[f] for f in faces], facecolor=face, edgecolor=edge, lw=0.6, alpha=alpha))
    return W


def helix(S, theta, p0, n=200):
    """点 p0 在螺旋运动 e^{[S]t}（t 从 0 到 θ）下的轨迹。"""
    pts = []
    for t in np.linspace(0, theta, n):
        pts.append((exp6(S, t) @ np.r_[p0, 1])[:3])
    return np.array(pts)
