"""第 7 章共用：本章的几个模型（关节电机、连杆单摆、陀螺仪的锥形运动、2R 臂）和几种数值方法。
以下划线开头，构建时不单独运行。

每种方法都按本章的公式编号实现；各程序再用独立的办法（解析解、椭圆积分、矩阵指数、scipy）核对。
"""
import math

import numpy as np

G = 9.81                      # 重力加速度 𝔤，m/s²

# ---------------------------------------------------------------- 关节电机（7.1、7.4 节）
# 一台小型直流伺服电机，带一级负载，参数折算到电机轴。
MOTOR = dict(
    R=1.2,                    # 电枢电阻，Ω
    L=0.6e-3,                 # 电枢电感，H（7.4 节用）
    Kt=0.05,                  # 转矩常数，N·m/A
    Ke=0.05,                  # 反电动势常数，V·s/rad
    Jm=4.0e-5,                # 折算到电机轴的总转动惯量，kg·m²
    b=2.0e-5,                 # 黏性摩擦系数，N·m·s/rad
)


def motor_first_order(m=MOTOR):
    """忽略电感时的一阶模型 τ ω̇ + ω = K u（式 (7.1.4)）：返回 (τ, K)。"""
    den = m["R"] * m["b"] + m["Kt"] * m["Ke"]
    return m["Jm"] * m["R"] / den, m["Kt"] / den


# ---------------------------------------------------------------- 连杆单摆（7.1、7.2 节）
# 刹车松开后自由摆动的一段均匀连杆：长 Lk、质量 mk，绕一端的水平轴转动。
LINK = dict(Lk=0.5, mk=2.0)


def link_params(p=LINK):
    """返回 (J_o, l_c, ω_n²)：绕轴的转动惯量、质心到轴的距离、小角度固有角频率的平方（式 (7.1.9)）。"""
    Jo = p["mk"] * p["Lk"] ** 2 / 3
    lc = p["Lk"] / 2
    return Jo, lc, p["mk"] * G * lc / Jo


def pend_f(wn2, damp=0.0):
    """状态方程 ẋ = f(x)，x = (θ, θ̇)（式 (7.1.11)）；damp 为 b/J_o，单位 1/s。"""
    def f(t, x):
        return np.array([x[1], -wn2 * math.sin(x[0]) - damp * x[1]])
    return f


def pend_energy(x, wn2):
    """单位转动惯量的能量 E/J_o = θ̇²/2 + ω_n²(1 − cos θ)（式 (7.1.13)），单位 1/s²。"""
    x = np.asarray(x)
    return 0.5 * x[..., 1] ** 2 + wn2 * (1 - np.cos(x[..., 0]))


# ---------------------------------------------------------------- 单步方法（7.2 节）

def euler(f, t, x, h):
    """显式欧拉法（式 (7.2.2)）。"""
    return x + h * f(t, x)


def midpoint(f, t, x, h):
    """中点法，二阶龙格-库塔法（式 (7.2.8)）。"""
    k1 = f(t, x)
    return x + h * f(t + h / 2, x + h / 2 * k1)


def rk4(f, t, x, h):
    """经典四阶龙格-库塔法（式 (7.2.10)）。"""
    k1 = f(t, x)
    k2 = f(t + h / 2, x + h / 2 * k1)
    k3 = f(t + h / 2, x + h / 2 * k2)
    k4 = f(t + h, x + h * k3)
    return x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def run(step, f, x0, T, h, t0=0.0, keep=False):
    """从 t0 积分到 t0 + T，步长 h（T/h 取整）。keep=True 时返回整条轨迹。"""
    n = int(round(T / h))
    x = np.array(x0, float)
    xs = [x.copy()] if keep else None
    for k in range(n):
        x = step(f, t0 + k * h, x, h)
        if keep:
            xs.append(x.copy())
    return (np.array(xs) if keep else x)


def symp_euler(wn2, x, h):
    """辛欧拉法（式 (7.2.13)）：先用旧位置更新速度，再用新速度更新位置。"""
    th, om = x
    om = om - h * wn2 * math.sin(th)
    th = th + h * om
    return np.array([th, om])


def verlet(wn2, x, h):
    """速度形式的施特默-韦莱法（式 (7.2.16)）。"""
    th, om = x
    a = -wn2 * math.sin(th)
    om_half = om + h / 2 * a
    th = th + h * om_half
    om = om_half + h / 2 * (-wn2 * math.sin(th))
    return np.array([th, om])


def run_pend(method, wn2, x0, T, h, every=1):
    """单摆专用的积分循环（辛方法不是 f(t, x) 的形式）。method: euler / rk4 / symp / verlet。"""
    n = int(round(T / h))
    f = pend_f(wn2)
    x = np.array(x0, float)
    xs = [x.copy()]
    for k in range(n):
        if method == "euler":
            x = euler(f, k * h, x, h)
        elif method == "rk4":
            x = rk4(f, k * h, x, h)
        elif method == "midpoint":
            x = midpoint(f, k * h, x, h)
        elif method == "symp":
            x = symp_euler(wn2, x, h)
        elif method == "verlet":
            x = verlet(wn2, x, h)
        else:
            raise ValueError(method)
        if (k + 1) % every == 0:
            xs.append(x.copy())
    return np.array(xs)


def pend_exact_period(wn2, th0):
    """大摆角单摆的精确周期：T = 4K(k)/ω_n，k = sin(θ0/2)（第一类完全椭圆积分）。"""
    from scipy.special import ellipk
    return 4 * ellipk(math.sin(th0 / 2) ** 2) / math.sqrt(wn2)


# ---------------------------------------------------------------- SO(3)（7.2.5 节）

def skew(w):
    """[ω]：反对称矩阵，[ω] p = ω × p（第 3 章 3.2 节）。"""
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]], float)


def unskew(W):
    return np.array([W[2, 1], W[0, 2], W[1, 0]])


def exp3(v):
    """罗德里格斯公式 e^{[v]}（式 (4.4.5)），v 为指数坐标。"""
    v = np.asarray(v, float)
    t = float(np.linalg.norm(v))
    if t < 1e-14:
        return np.eye(3) + skew(v)
    K = skew(v / t)
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def rot_x(t):
    return exp3([t, 0, 0])


def rot_z(t):
    return exp3([0, 0, t])


def angle_between(A, B):
    """两个姿态之差的转角（式 (4.8.2)），单位 rad。对不严格正交的矩阵先取最近的旋转矩阵。"""
    U, _, Vt = np.linalg.svd(A)
    A = U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
    # 与 arccos((tr(AᵀB) − 1)/2) 相同，但小角度时不损失精度：‖A − B‖ = 2√2 sin(φ/2)
    return 2 * math.asin(min(1.0, float(np.linalg.norm(A - B)) / (2 * math.sqrt(2))))


# 锥形运动：R(t) = Rot(ẑ, a t) Rot(x̂, b t)，物体角速度 ω_b(t) = (b, a sin bt, a cos bt)（式 (7.2.19)）
CONE = dict(a=2.0, b=3.0)


def cone_R(t, c=CONE):
    return rot_z(c["a"] * t) @ rot_x(c["b"] * t)


def cone_wb(t, c=CONE):
    a, b = c["a"], c["b"]
    return np.array([b, a * math.sin(b * t), a * math.cos(b * t)])


# ---------------------------------------------------------------- 陀螺仪积分（7.2.5 节）
S3 = math.sqrt(3)


def lie_step(meth, R, t, h):
    """由陀螺仪读数 ω_b(t) 积分 Ṙ = R[ω_b] 的一步（7.2.5 节的五种方法）。"""
    if meth == "euler":
        return R @ (np.eye(3) + h * skew(cone_wb(t)))
    if meth == "rk4":
        F = lambda s, X: X @ skew(cone_wb(s))
        k1 = F(t, R)
        k2 = F(t + h / 2, R + h / 2 * k1)
        k3 = F(t + h / 2, R + h / 2 * k2)
        k4 = F(t + h, R + h * k3)
        return R + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    if meth == "lie":
        return R @ exp3(h * cone_wb(t))
    if meth == "mid":
        return R @ exp3(h * cone_wb(t + h / 2))
    if meth == "mag4":
        w1 = cone_wb(t + (0.5 - S3 / 6) * h)
        w2 = cone_wb(t + (0.5 + S3 / 6) * h)
        return R @ exp3(h / 2 * (w1 + w2) + S3 / 12 * h * h * np.cross(w1, w2))
    raise ValueError(meth)


def lie_integrate(meth, T, h):
    R = cone_R(0.0)
    n = int(round(T / h))
    for k in range(n):
        R = lie_step(meth, R, k * h, h)
    return R


def orth(R):
    return float(np.linalg.norm(R.T @ R - np.eye(3)))



# ---------------------------------------------------------------- 2R 臂（7.3 节）
# 取 UR5e 大臂、小臂的长度（与第 12 章实验 12.2 相同）。
L1, L2 = 0.425, 0.392


def fk2(th, l1=L1, l2=L2):
    """2R 臂末端位置（第 2 章 2.1 节）。th 可以是 (..., 2) 数组。"""
    th = np.asarray(th, float)
    t1, t12 = th[..., 0], th[..., 0] + th[..., 1]
    return np.stack([l1 * np.cos(t1) + l2 * np.cos(t12), l1 * np.sin(t1) + l2 * np.sin(t12)], axis=-1)


def jac2(th, l1=L1, l2=L2):
    """2R 臂的雅可比矩阵 ∂p/∂θ（式 (7.3.10)）。"""
    t1, t12 = th[0], th[0] + th[1]
    return np.array([[-l1 * math.sin(t1) - l2 * math.sin(t12), -l2 * math.sin(t12)],
                     [l1 * math.cos(t1) + l2 * math.cos(t12), l2 * math.cos(t12)]])


def ik2_analytic(p, l1=L1, l2=L2):
    """2R 臂逆运动学的解析解（余弦定理）：返回 [肘部朝上（θ2 > 0）, 肘部朝下（θ2 < 0）] 两组解。"""
    x, y = p
    c2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    sols = []
    for s in (1, -1):
        t2 = s * math.acos(max(-1.0, min(1.0, c2)))
        t1 = math.atan2(y, x) - math.atan2(l2 * math.sin(t2), l1 + l2 * math.cos(t2))
        sols.append(np.array([t1, t2]))
    return sols


def wrap(a):
    """角度化到 (−π, π]。"""
    return (np.asarray(a) + math.pi) % (2 * math.pi) - math.pi


def newton2_batch(th0, p, iters=40, tol=1e-10, l1=L1, l2=L2):
    """从许多初值同时做 2R 逆运动学的牛顿迭代（式 (7.3.9)）。th0: (N, 2)。
    返回 (最终关节角, 是否收敛, 所用迭代次数)。雅可比矩阵奇异或迭代 iters 次仍未收敛的算作失败。"""
    th = np.array(th0, float)
    n = th.shape[0]
    ok = np.zeros(n, bool)
    used = np.full(n, iters)
    alive = np.ones(n, bool)
    for k in range(iters):
        t1, t12 = th[:, 0], th[:, 0] + th[:, 1]
        r = fk2(th, l1, l2) - p
        nr = np.hypot(r[:, 0], r[:, 1])
        newly = alive & (nr < tol)
        ok |= newly
        used[newly] = k
        alive &= ~newly
        a, b = -l1 * np.sin(t1) - l2 * np.sin(t12), -l2 * np.sin(t12)
        c, d = l1 * np.cos(t1) + l2 * np.cos(t12), l2 * np.cos(t12)
        det = a * d - b * c
        bad = alive & (np.abs(det) < 1e-12)
        alive &= ~bad
        det = np.where(np.abs(det) < 1e-12, 1.0, det)
        dx = (d * r[:, 0] - b * r[:, 1]) / det          # J⁻¹ r，2×2 矩阵的逆直接写出
        dy = (-c * r[:, 0] + a * r[:, 1]) / det
        th[alive, 0] -= dx[alive]
        th[alive, 1] -= dy[alive]
        th[~np.isfinite(th).all(axis=1)] = 0.0
    return th, ok, used


def newton2_batch_ls(th0, p, iters=60, tol=1e-10, l1=L1, l2=L2):
    """同 newton2_batch，但每步做回溯线搜索：步长从 1 起逐次减半，直到残差变小（式 (7.3.11)）。"""
    th = np.array(th0, float)
    n = th.shape[0]
    ok = np.zeros(n, bool)
    used = np.full(n, iters)
    alive = np.ones(n, bool)
    res = lambda t: np.hypot(*(fk2(t, l1, l2) - p).T)
    for k in range(iters):
        r = fk2(th, l1, l2) - p
        nr = np.hypot(r[:, 0], r[:, 1])
        newly = alive & (nr < tol)
        ok |= newly
        used[newly] = k
        alive &= ~newly
        t1, t12 = th[:, 0], th[:, 0] + th[:, 1]
        a, b = -l1 * np.sin(t1) - l2 * np.sin(t12), -l2 * np.sin(t12)
        c, d = l1 * np.cos(t1) + l2 * np.cos(t12), l2 * np.cos(t12)
        det = a * d - b * c
        alive &= np.abs(det) >= 1e-12
        det = np.where(np.abs(det) < 1e-12, 1.0, det)
        step = np.column_stack([(d * r[:, 0] - b * r[:, 1]) / det, (-c * r[:, 0] + a * r[:, 1]) / det])
        alpha = np.ones(n)
        for _ in range(30):
            worse = res(th - alpha[:, None] * step) >= nr
            worse &= alive
            if not worse.any():
                break
            alpha[worse] /= 2
        th[alive] -= alpha[alive, None] * step[alive]
    return th, ok, used
