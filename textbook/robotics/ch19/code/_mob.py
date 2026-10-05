"""第 19 章共用：平面位姿与物体运动旋量、车轮约束、SE(2) 指数映射、矢量场的李括号、数字工厂的路线。
以下划线开头，构建时不单独运行。

记号（与正文一致）：
- 位姿 q = (x, y, φ)：车体参考点在 {s} 中的位置和车头方向，φ 逆时针为正，单位 rad；
- 平面物体运动旋量 V_b = (ω, v_x, v_y)：角速度在前（与第 6 章相同），v_x、v_y 是参考点的速度在 {b} 中的分量；
- 车轮 i：接地点（标准轮为轮心正下方）在 {b} 中的位置 (x_i, y_i)，轮平面（滚动方向）与 x_b 的夹角 β_i，半径 r_i；
  瑞典轮另有辊子角 γ_i（辊子轴线与轮平面的夹角）。
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MODELS = HERE.parents[1] / "models"


def diff_cart():
    """零件库差速小车 B-EDU-DIFF 的参数：轮半径 r、轮距 b、轮子最高转速、车体长宽。"""
    e = json.loads((MODELS / "B-EDU-DIFF" / "entry.json").read_text(encoding="utf-8"))
    d, k = e["defaults"], e["robot"]["kinematics"]
    js = {j["name"]: j for j in e["robot"]["joints"]}
    yl, yr = js["left_wheel_joint"]["origin"]["xyz"][1], js["right_wheel_joint"]["origin"]["xyz"][1]
    assert abs(k["wheel_radius_m"] - d["wheel_radius_m"]) < 1e-12 and abs(k["track_m"] - (yl - yr)) < 1e-12
    return dict(r=k["wheel_radius_m"], b=k["track_m"], wmax=d["wheel_speed_rad_s"],
                length=d["chassis_length_m"], width=d["chassis_width_m"], yl=yl, yr=yr)


# ---------------------------------------------------------------- 车轮约束（19.1 节）

def contact(xi, yi):
    """2×3 矩阵：由 V_b = (ω, v_x, v_y) 得车体上与接地点重合的那一点的速度（{b} 中的分量）。"""
    return np.array([[-yi, 1.0, 0.0], [xi, 0.0, 1.0]])


def noslip_row(xi, yi, beta):
    """标准轮不侧滑：接地点速度在轮轴方向 n = (−sin β, cos β) 上的分量为零。"""
    n = np.array([-math.sin(beta), math.cos(beta)])
    return n @ contact(xi, yi)


def roll_row(xi, yi, beta):
    """标准轮纯滚动：接地点速度在滚动方向 e = (cos β, sin β) 上的分量等于 r θ̇。"""
    e = np.array([math.cos(beta), math.sin(beta)])
    return e @ contact(xi, yi)


def swedish_row(xi, yi, beta, gamma, r):
    """瑞典轮：θ̇ = a·v_P /(r cos γ)，a 为接地辊子轴线的方向（与轮平面成 γ 角）。"""
    a = np.array([math.cos(beta + gamma), math.sin(beta + gamma)])
    return a @ contact(xi, yi) / (r * math.cos(gamma))


def rank(A, tol=1e-9):
    return int(np.linalg.matrix_rank(np.atleast_2d(A), tol))


def icr(V):
    """瞬心在 {b} 中的位置（ω ≠ 0 时）：速度为零的点 (−v_y/ω, v_x/ω)。"""
    w, vx, vy = V
    return np.array([-vy / w, vx / w])


def nullspace(A, tol=1e-9):
    _, s, Vt = np.linalg.svd(np.atleast_2d(A))
    k = int((s > tol).sum())
    return Vt[k:].T


# ---------------------------------------------------------------- 位姿、SE(2) 指数映射（19.2 节）

def qdot(q, V):
    """由物体运动旋量得位姿变量的导数 (ẋ, ẏ, φ̇)。"""
    w, vx, vy = V
    c, s = math.cos(q[2]), math.sin(q[2])
    return np.array([c * vx - s * vy, s * vx + c * vy, w])


def se2(q):
    x, y, f = q
    c, s = math.cos(f), math.sin(f)
    return np.array([[c, -s, x], [s, c, y], [0, 0, 1.0]])


def q_of(T):
    return np.array([T[0, 2], T[1, 2], math.atan2(T[1, 0], T[0, 0])])


def bracket_mat(V):
    """[V_b] ∈ se(2)，3×3。"""
    w, vx, vy = V
    return np.array([[0, -w, vx], [w, 0, vy], [0, 0, 0.0]])


def exp_se2(V, t):
    """exp([V_b] t)，按式 (19.2.6) 的闭式计算；ω→0 时取极限（直线）。"""
    w, vx, vy = V
    th = w * t
    if abs(th) < 1e-9:
        A = t * (1 - th * th / 6)          # sin(θ)/ω
        B = t * (th / 2)                   # (1 − cos θ)/ω
    else:
        A = math.sin(th) / w
        B = (1 - math.cos(th)) / w
    c, s = math.cos(th), math.sin(th)
    return np.array([[c, -s, A * vx - B * vy], [s, c, B * vx + A * vy], [0, 0, 1.0]])


def step_exact(q, V, h):
    return q_of(se2(q) @ exp_se2(V, h))


def step_euler(q, V, h):
    return q + h * qdot(q, V)


def step_mid(q, V, h):
    """中点法（二阶龙格-库塔）：用区间中点的车头方向。"""
    qm = q + 0.5 * h * qdot(q, V)
    return q + h * qdot(qm, V)


def expm(A, terms=40):
    """矩阵指数的级数（用于核对闭式）。"""
    E, P = np.eye(len(A)), np.eye(len(A))
    for k in range(1, terms):
        P = P @ A / k
        E = E + P
    return E


# ---------------------------------------------------------------- 矢量场的李括号（19.1、19.4 节）

def jac(f, q, eps=1e-6):
    q = np.asarray(q, float)
    n = len(q)
    J = np.zeros((len(f(q)), n))
    for j in range(n):
        d = np.zeros(n)
        d[j] = eps
        J[:, j] = (f(q + d) - f(q - d)) / (2 * eps)
    return J


def lie(f, g):
    """矢量场的李括号 [f, g](q) = (∂g/∂q) f − (∂f/∂q) g，返回一个新的矢量场（数值求导）。"""
    return lambda q: jac(g, q) @ f(q) - jac(f, q) @ g(q)


def flow(f, q, t, n=400):
    """沿矢量场 f 走时间 t（四阶龙格-库塔，n 步）。"""
    q = np.asarray(q, float).copy()
    h = t / n
    for _ in range(n):
        k1 = f(q)
        k2 = f(q + h / 2 * k1)
        k3 = f(q + h / 2 * k2)
        k4 = f(q + h * k3)
        q = q + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return q


# ---------------------------------------------------------------- 数字工厂（19.2、19.5 节）

def factory():
    """数字工厂的车间布置模块（factory/digital/wqbus/layout.py），与工厂仿真、第 1 章同一份数据。"""
    p = ROOT / "factory" / "digital"
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
    from wqbus import layout          # noqa: E402
    return layout


def to_book(pts, floor_w):
    """工厂平面 (x, y 向下) → 本章的 {s}（x 不变，y = 车间宽 − y_f，向上为正，逆时针为正）。"""
    return [(float(x), float(floor_w - y)) for x, y in pts]


def round_corners(pts, rho):
    """把折线的每个直角拐角换成半径 rho 的相切圆弧。返回段列表：('line', p0, p1) 或 ('arc', 圆心, 半径, 起始角, 转角)。"""
    P = [np.array(p, float) for p in pts]
    segs = []
    cur = P[0]
    for k in range(1, len(P) - 1):
        a, b, c = P[k - 1], P[k], P[k + 1]
        u = (b - a) / np.linalg.norm(b - a)
        w = (c - b) / np.linalg.norm(c - b)
        turn = math.atan2(u[0] * w[1] - u[1] * w[0], u @ w)          # 逆时针为正
        d = rho * math.tan(abs(turn) / 2)                            # 切点到拐角的距离
        t1, t2 = b - d * u, b + d * w
        segs.append(("line", cur, t1))
        nrm = np.array([-u[1], u[0]]) * (1 if turn > 0 else -1)      # 指向圆心
        cen = t1 + rho * nrm
        a0 = math.atan2(t1[1] - cen[1], t1[0] - cen[0])
        segs.append(("arc", cen, rho, a0, turn))
        cur = t2
    segs.append(("line", cur, P[-1]))
    return segs


def seg_len(s):
    return float(np.linalg.norm(s[2] - s[1])) if s[0] == "line" else abs(s[4]) * s[2]


def seg_point(s, u):
    """段 s 上走过长度 u 处的位置、切线方向角、曲率（逆时针转弯为正）。"""
    if s[0] == "line":
        d = (s[2] - s[1]) / np.linalg.norm(s[2] - s[1])
        p = s[1] + u * d
        return p, math.atan2(d[1], d[0]), 0.0
    cen, rho, a0, turn = s[1], s[2], s[3], s[4]
    sg = 1.0 if turn > 0 else -1.0
    a = a0 + sg * u / rho
    p = cen + rho * np.array([math.cos(a), math.sin(a)])
    return p, a + sg * math.pi / 2, sg / rho


def profile(segs, v_line, v_arc, acc, ds=1e-3):
    """沿段列表求最短时间的速度曲线：直线上 v ≤ v_line，圆弧上 v ≤ v_arc，|dv/dt| ≤ acc，起止静止。
    返回 dict：S（弧长）、v、kap（曲率）、xy、head、t（各点的时刻）、T（总时间）、L（总长）。"""
    S, KAP, HEAD, XY = [], [], [], []
    s0 = 0.0
    for sg in segs:
        Ls = seg_len(sg)
        n = max(1, int(round(Ls / ds)))
        for i in range(n):
            u = (i + 0.5) * Ls / n
            p, hd, kap = seg_point(sg, u)
            S.append(s0 + u)
            KAP.append(kap)
            HEAD.append(hd)
            XY.append(p)
        s0 += Ls
    L = s0
    S, KAP, XY, HEAD = np.array(S), np.array(KAP), np.array(XY), np.array(HEAD)
    v = np.where(np.abs(KAP) > 0, v_arc, v_line).astype(float)
    v[0] = min(v[0], math.sqrt(2 * acc * S[0]))
    for i in range(1, len(v)):                                    # 正向：加速度不超过 acc
        v[i] = min(v[i], math.sqrt(v[i - 1] ** 2 + 2 * acc * (S[i] - S[i - 1])))
    v[-1] = min(v[-1], math.sqrt(2 * acc * (L - S[-1])))
    for i in range(len(v) - 2, -1, -1):                           # 反向：减速度不超过 acc
        v[i] = min(v[i], math.sqrt(v[i + 1] ** 2 + 2 * acc * (S[i + 1] - S[i])))
    vv = np.r_[0.0, v, 0.0]
    ss = np.r_[0.0, S, L]
    dt = 2 * np.diff(ss) / (vv[:-1] + vv[1:])                     # 相邻两点间按匀加速计算
    tt = np.cumsum(dt)
    return dict(S=S, v=v, kap=KAP, xy=XY, head=HEAD, t=tt[:-1], T=float(tt[-1]), L=L)
