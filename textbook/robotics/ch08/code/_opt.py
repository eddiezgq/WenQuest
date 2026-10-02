"""第 8 章共用：平面 2R、3R 臂与 UR5e 的运动学（尺寸与第 2、12 章相同），以及本章讲到的几种优化算法。
以下划线开头，构建时不单独运行。

算法都按正文的公式逐行写出，不调用现成的优化库；每个算例程序再用 scipy.optimize 独立地算一遍，互相核对。
"""
import math

import numpy as np

L2R = (0.425, 0.392)          # 平面 2R 臂：UR5e 的大臂、小臂长度，m
L3R = (0.425, 0.392, 0.1)     # 平面 3R 臂：再加 0.1 m 的末端（与 12.1 节相同）


def d(deg):
    return math.radians(deg)


# ---------------------------------------------------------------- 平面串联臂

def arm_points(th, lengths):
    """各关节中心与末端的位置（每个关节角相对前一连杆，rad）。"""
    pts, a = [np.zeros(2)], 0.0
    for t, l in zip(th, lengths):
        a += t
        pts.append(pts[-1] + l * np.array([math.cos(a), math.sin(a)]))
    return np.array(pts)


def tip(th, lengths):
    return arm_points(th, lengths)[-1]


def jac(th, lengths):
    """末端位置的雅可比矩阵：第 i 列是“关节 i 指向末端”的矢量逆时针转 90°。"""
    pts = arm_points(th, lengths)
    e = pts[-1]
    return np.array([[-(e - pts[i])[1], (e - pts[i])[0]] for i in range(len(th))]).T


def tip_hessians(th, lengths):
    """末端位置对关节角的二阶导数：∂²p/∂θi∂θj = −(p − p_k)，k = max(i, j)（p_k 为关节 k 的中心）。
    返回 H[c] 为末端第 c 个坐标的 n×n 二阶导数矩阵。"""
    pts = arm_points(th, lengths)
    e = pts[-1]
    n = len(th)
    H = np.zeros((2, n, n))
    for i in range(n):
        for j in range(n):
            H[:, i, j] = -(e - pts[max(i, j)])
    return H


def ik_closed_2r(p, lengths=L2R, elbow=+1):
    """平面 2R 臂的解析逆解（余弦定理），elbow = +1 取 θ2 > 0（肘部在下方的一支）。"""
    l1, l2 = lengths
    c2 = (p @ p - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    t2 = elbow * math.acos(max(-1.0, min(1.0, c2)))
    t1 = math.atan2(p[1], p[0]) - math.atan2(l2 * math.sin(t2), l1 + l2 * math.cos(t2))
    return np.array([t1, t2])


# ---------------------------------------------------------------- UR5e（表 12.1.1 的旋量轴，{s} 为基座坐标系）

UR = dict(H1=0.163, W1=0.138, L1=0.425, W2=0.131, L2=0.392, W3=0.127, H2=0.1, W4=0.1)


def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]], dtype=float)


def ur5e_axes():
    """六个关节在零位时的转轴方向 ω_i 与轴上一点 q_i，以及零位时法兰盘中心的位置。"""
    H1, W1, L1, W2, L2, W3, H2, W4 = (UR[k] for k in ("H1", "W1", "L1", "W2", "L2", "W3", "H2", "W4"))
    yd = [0, -1, 0]
    w = np.array([[0, 0, 1], yd, yd, yd, [0, 0, -1], yd], float)
    q = np.array([[0, 0, H1], [0, -W1, H1], [-L1, -W1 + W2, H1], [-L1 - L2, -W1 + W2, H1],
                  [-L1 - L2, -W1 + W2 - W3, H1], [-L1 - L2, -W1 + W2 - W3, H1 - H2]], float)
    p0 = np.array([-L1 - L2, -W1 + W2 - W3 - W4, H1 - H2])
    return w, q, p0


def _rot(w, t):
    K = skew(w)
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def ur5e_flange(th):
    """法兰盘中心的位置（指数积公式：每个关节绕当前位置的轴转动，从最后一个关节算起）。"""
    w, q, p0 = ur5e_axes()
    p = p0.copy()
    for i in range(5, -1, -1):
        R = _rot(w[i], th[i])
        p = R @ (p - q[i]) + q[i]
    return p


def ur5e_flange_jac(th):
    """法兰盘中心位置的雅可比矩阵（3×6）：第 i 列 = ω_i(θ) × (p − q_i(θ))，ω_i(θ)、q_i(θ) 为关节 i 当前的轴。"""
    w, q, p0 = ur5e_axes()
    p = ur5e_flange(th)
    R, t = np.eye(3), np.zeros(3)          # 关节 1…i−1 合起来的刚体变换 (R, t)
    J = np.zeros((3, 6))
    for i in range(6):
        wi, qi = R @ w[i], R @ q[i] + t
        J[:, i] = np.cross(wi, p - qi)
        Ri = _rot(w[i], th[i])
        t = R @ (q[i] - Ri @ q[i]) + t
        R = R @ Ri
    return J


# ---------------------------------------------------------------- 无约束优化（8.1 节）

def gradient_descent(f, grad, x0, alpha=None, tol=1e-10, kmax=100000, c1=1e-4, shrink=0.5, alpha0=1.0):
    """梯度下降。alpha 给定时用固定步长，否则用阿米霍回溯线搜索（式 (8.1.14)）。返回 (x, 迭代点列表, 求值次数)。"""
    x = np.asarray(x0, float)
    path, nf = [x.copy()], 0
    for _ in range(kmax):
        g = grad(x)
        if np.linalg.norm(g) < tol:
            break
        if alpha is not None:
            x = x - alpha * g
        else:
            a, fx = alpha0, f(x)
            nf += 1
            while f(x - a * g) > fx - c1 * a * (g @ g):
                a *= shrink
                nf += 1
            x = x - a * g
        path.append(x.copy())
        if not np.all(np.isfinite(x)) or np.linalg.norm(x) > 1e6:
            break
    return x, np.array(path), nf


def newton(grad, hess, x0, tol=1e-12, kmax=100, f=None, safeguard=False):
    """牛顿法：解 H d = −g。safeguard=True 时，把 H 的负特征值换成绝对值使其正定，并做回溯线搜索（8.1.5 节）。"""
    x = np.asarray(x0, float)
    path = [x.copy()]
    for _ in range(kmax):
        g = grad(x)
        if np.linalg.norm(g) < tol:
            break
        H = hess(x)
        if safeguard:                       # 把特征值换成绝对值（不小于最大者的 1%），保证 H 正定
            lam, V = np.linalg.eigh(H)
            lam = np.maximum(np.abs(lam), 0.01 * np.abs(lam).max())
            H = V @ np.diag(lam) @ V.T
        dx = np.linalg.solve(H, -g)
        a = 1.0
        if safeguard and f is not None:
            while f(x + a * dx) > f(x) + 1e-4 * a * (g @ dx) and a > 1e-8:
                a *= 0.5
        x = x + a * dx
        path.append(x.copy())
    return x, np.array(path)


# ---------------------------------------------------------------- 二次规划：有效集法（8.3 节）

def qp_active_set(Q, c, A=None, b=None, E=None, e=None, x0=None, kmax=2000, tol=1e-12):
    """严格凸二次规划  min ½xᵀQx + cᵀx  s.t.  Ex = e，Ax ≤ b  的原始有效集法（8.3.3 节）。
    x0 必须是可行点。返回 dict：x、λ（等式乘子）、μ（不等式乘子，全长）、active、history（每步的 x 与工作集）。"""
    n = len(c)
    A = np.zeros((0, n)) if A is None else np.asarray(A, float)
    b = np.zeros(0) if b is None else np.asarray(b, float)
    E = np.zeros((0, n)) if E is None else np.asarray(E, float)
    e = np.zeros(0) if e is None else np.asarray(e, float)
    x = np.asarray(x0, float).copy()
    W = []                                                               # 初始工作集：空（起点最好严格可行）
    hist = [(x.copy(), list(W))]
    me = len(e)
    for _ in range(kmax):
        Aw = np.vstack([E, A[W]]) if len(W) else E
        m = Aw.shape[0]
        g = Q @ x + c
        K = np.block([[Q, Aw.T], [Aw, np.zeros((m, m))]])
        sol = np.linalg.solve(K, np.r_[-g, np.zeros(m)])
        p, mult = sol[:n], sol[n:]
        if np.linalg.norm(p) < 1e-12:
            mu_w = mult[me:]
            if len(W) == 0 or mu_w.min() >= -tol:
                mu = np.zeros(len(b))
                for k, i in enumerate(W):
                    mu[i] = mu_w[k]
                return dict(x=x, lam=mult[:me], mu=mu, active=sorted(W), history=hist)
            W.pop(int(np.argmin(mu_w)))                  # 乘子为负：这条约束不该起作用，移出工作集
            hist.append((x.copy(), list(W)))
            continue
        a, block = 1.0, None
        for i in range(len(b)):
            if i in W:
                continue
            ap = A[i] @ p
            if ap > 1e-14:
                ai = (b[i] - A[i] @ x) / ap
                if ai < a:
                    a, block = ai, i
        x = x + a * p
        if block is not None:
            W.append(block)                             # 被挡住：挡住的约束加入工作集
        hist.append((x.copy(), list(W)))
    raise RuntimeError("active set: no convergence")


def kkt_residuals(Q, c, A, b, E, e, x, lam, mu):
    """KKT 条件 (8.3.3) 的四项残差：驻点、原始可行、对偶可行、互补松弛。"""
    A = np.zeros((0, len(x))) if A is None else A
    E = np.zeros((0, len(x))) if E is None else E
    b = np.zeros(0) if b is None else b
    e = np.zeros(0) if e is None else e
    stat = Q @ x + c + E.T @ lam + A.T @ mu
    prim = max([0.0] + list(np.abs(E @ x - e)) + list(np.maximum(A @ x - b, 0)))
    dual = max([0.0] + list(np.maximum(-mu, 0)))
    comp = max([0.0] + list(np.abs(mu * (A @ x - b))))
    return float(np.linalg.norm(stat, np.inf)), float(prim), float(dual), float(comp)


# ---------------------------------------------------------------- 障碍函数法（8.4 节）

def barrier_qp(Q, c, A, b, x0, t0=1.0, factor=10.0, eps=1e-9, E=None, e=None):
    """min ½xᵀQx + cᵀx  s.t. Ax ≤ b（及 Ex = e）的对数障碍函数法：对 t = t0, 10t0, … 依次用牛顿法最小化
    t·f(x) − Σ log(b − Ax)，直到 m/t < eps。x0 须严格可行。返回 (x, 每个 t 的中心点列表, μ 的估计, 牛顿步总数)。"""
    x = np.asarray(x0, float).copy()
    n, m = len(x), len(b)
    E = np.zeros((0, n)) if E is None else E
    e = np.zeros(0) if e is None else e
    t, centers, steps = t0, [], 0
    lam = np.zeros(len(e))
    while True:
        for _ in range(200):
            s = b - A @ x
            g = t * (Q @ x + c) + A.T @ (1 / s)
            H = t * Q + A.T @ np.diag(1 / s ** 2) @ A
            me = E.shape[0]
            K = np.block([[H, E.T], [E, np.zeros((me, me))]])
            sol = np.linalg.solve(K, np.r_[-g, np.zeros(me)])
            dx, w = sol[:n], sol[n:]
            dec = float(-g @ dx)                 # 牛顿减量的平方
            if dec / 2 < 1e-10:
                break
            a = 1.0
            while np.min(b - A @ (x + a * dx)) <= 0:
                a *= 0.5
            def phi(z):
                return t * (0.5 * z @ Q @ z + c @ z) - np.sum(np.log(b - A @ z))
            while phi(x + a * dx) > phi(x) - 0.25 * a * dec:
                a *= 0.5
            x = x + a * dx
            steps += 1
            lam = w / t
        centers.append((t, x.copy()))
        if m / t < eps:
            break
        t *= factor
    mu = 1 / (t * (b - A @ x))
    return x, centers, mu, lam, steps


# ---------------------------------------------------------------- 非线性最小二乘（8.5 节）

def gauss_newton(res, jacf, x0, tol=1e-12, kmax=50):
    """高斯-牛顿法：解 JᵀJ Δ = −Jᵀr（用最小二乘求解，不形成 JᵀJ）。返回 (x, 迭代点, 每步的 ½‖r‖²)。"""
    x = np.asarray(x0, float)
    path, F = [x.copy()], [0.5 * float(res(x) @ res(x))]
    for _ in range(kmax):
        r, J = res(x), jacf(x)
        dx = np.linalg.lstsq(J, -r, rcond=None)[0]
        x = x + dx
        path.append(x.copy())
        F.append(0.5 * float(res(x) @ res(x)))
        if np.linalg.norm(dx) < tol * (1 + np.linalg.norm(x)) or not np.isfinite(F[-1]) or F[-1] > 1e12:
            break
    return x, np.array(path), np.array(F)


def levenberg_marquardt(res, jacf, x0, tau=1e-3, tol=1e-12, kmax=200, scale=False):
    """列文伯格-马夸特法：解 (JᵀJ + μD) Δ = −Jᵀr，D = I（列文伯格）或 diag(JᵀJ)（马夸特）；
    阻尼系数 μ 按增益比 ρ 调整（尼尔森的规则，式 (8.5.9)）。返回 (x, 迭代点, ½‖r‖², μ 的历史)。"""
    x = np.asarray(x0, float)
    r, J = res(x), jacf(x)
    A, g = J.T @ J, J.T @ r
    lam = tau * float(np.max(np.diag(A)))
    nu = 2.0
    path, F, lams = [x.copy()], [0.5 * float(r @ r)], [lam]
    for _ in range(kmax):
        if np.linalg.norm(g, np.inf) < tol:
            break
        D = np.diag(np.diag(A)) if scale else np.eye(len(x))
        dx = np.linalg.solve(A + lam * D, -g)
        if np.linalg.norm(dx) < tol * (1 + np.linalg.norm(x)):
            break
        xn = x + dx
        rn = res(xn)
        pred = 0.5 * float(dx @ (lam * D @ dx - g))       # 线性化模型预计的下降量，式 (8.5.8)
        rho = (0.5 * float(r @ r) - 0.5 * float(rn @ rn)) / pred
        if rho > 0:
            x, r, J = xn, rn, jacf(xn)
            A, g = J.T @ J, J.T @ r
            lam *= max(1 / 3, 1 - (2 * rho - 1) ** 3)
            nu = 2.0
            path.append(x.copy())
            F.append(0.5 * float(r @ r))
        else:
            lam *= nu
            nu *= 2
        lams.append(lam)
    return x, np.array(path), np.array(F), np.array(lams)
