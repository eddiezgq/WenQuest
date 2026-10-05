"""18.3 节：Stewart 平台的逆解与正解（几何同算例 11.5.4，电动缸长度范围 0.55～0.85 m）。

(1) 算例 18.3.1：位姿 X1（平台中心 (0.05, −0.03, 0.62) m，横滚 6°、俯仰 −8°、偏航 12°）的六条腿长、万向节与球关节的转角，
    是否在行程以内；平台中心在中心轴上时的升降范围，原点高度 0.6 m 处单独横滚、俯仰、偏航的范围。
(2) 算例 18.3.2：腿长速度 l̇ = A𝒱_s。平台绕自身中心以 30°/s 横滚、同时以 0.1 m/s 上升时的六个腿速，用差商核对。
(3) 定理 18.3.2 的核对：左乘小位移 exp([ε]) 后腿长的变化与 Aε 之差为二阶小量。
(4) 算例 18.3.3：正解的牛顿法 (18.3.5)：从原点位姿出发求 X1，各步的残差（二次收敛）；与 X1 的差。
(5) 实时跟踪：一段 5 s 的多轴正弦运动，控制周期 1 ms，每个周期由测得的腿长求位姿：用上一周期的位姿作初值时的迭代次数，
    与每次都从原点位姿出发相比。
(6) 算例 18.3.4：多解。X1 的腿长下，从 4000 个随机初值出发做牛顿法，得到的不同实数解：上下各 4 个，互为镜像（定理 18.3.3）。
(7) 用多项式同伦法求同一组腿长的全部复数解，核对实数解恰为这 8 个（随机初值没有遗漏）。
"""
import math

import numpy as np

from _ch18 import (ST_A, ST_B, ST_HOME, ST_LMAX, ST_LMIN, distinct_poses, exp6, pose, random_rotations, rot, rpy, st_fk,
                   st_fk_batch, st_ik, st_points, st_W, skew)
from bookout import T, out

deg = math.degrees
rad = math.radians

# ---------------------------------------------------------------- (1) 逆解
X1 = pose(rpy(rad(6), rad(-8), rad(12)), [0.05, -0.03, 0.62])
L1 = st_ik(X1)
assert ((L1 > ST_LMIN) & (L1 < ST_LMAX)).all()
L0 = st_ik(ST_HOME)
q1 = st_points(X1)
s1 = (q1 - ST_A) / L1[:, None]
tiltU = np.degrees(np.arccos(s1[:, 2]))                 # 腿与机架法线（z 轴）的夹角：万向节要转过的角度
coneS = np.degrees(np.arccos(s1 @ X1[:3, 2]))           # 腿与平台法线的夹角：球关节要转过的角度


def first_out(f, step=0.01):
    """从 0 开始增大参数，直到有腿超出行程，返回最后一个可行值。"""
    a = 0.0
    while True:
        L = st_ik(f(a + step))
        if L.max() > ST_LMAX or L.min() < ST_LMIN:
            return a
        a += step


heave_up = first_out(lambda a: pose(np.eye(3), [0, 0, 0.6 + a]), 1e-4) + 0.6
heave_dn = 0.6 - first_out(lambda a: pose(np.eye(3), [0, 0, 0.6 - a]), 1e-4)
roll_max = first_out(lambda a: pose(rpy(rad(a), 0, 0), [0, 0, 0.6]))
pitch_p = first_out(lambda a: pose(rpy(0, rad(a), 0), [0, 0, 0.6]))
pitch_m = first_out(lambda a: pose(rpy(0, -rad(a), 0), [0, 0, 0.6]))
yaw_max = first_out(lambda a: pose(rpy(0, 0, rad(a)), [0, 0, 0.6]))

# ---------------------------------------------------------------- (2) 腿速
w = np.array([rad(30), 0, 0])                           # 绕平台中心横滚 30°/s（在 {s} 中表示）
pc = X1[:3, 3]
vc = np.array([0, 0, 0.1])                              # 平台中心上升 0.1 m/s
Vs = np.r_[w, vc - np.cross(w, pc)]                     # 空间运动旋量：v_s = ṗ − ω × p（式 (16.1.7)）
ldot = st_W(X1).T @ Vs
h = 1e-6
Xp = pose(rot(w / np.linalg.norm(w), np.linalg.norm(w) * h) @ X1[:3, :3], pc + vc * h)
Xm = pose(rot(w / np.linalg.norm(w), -np.linalg.norm(w) * h) @ X1[:3, :3], pc - vc * h)
ldot_fd = (st_ik(Xp) - st_ik(Xm)) / (2 * h)
assert np.abs(ldot - ldot_fd).max() < 1e-8

# ---------------------------------------------------------------- (3) 左乘小位移的一阶展开
rng = np.random.default_rng(183)
err2 = []
for eps in (1e-2, 1e-3, 1e-4):
    e = rng.normal(size=6)
    e = eps * e / np.linalg.norm(e)
    err2.append(np.abs(st_ik(exp6(e) @ X1) - st_ik(X1) - st_W(X1).T @ e).max())
assert err2[1] < err2[0] / 50 and err2[2] < err2[1] / 50           # 误差按 ε² 减小

# ---------------------------------------------------------------- (4) 牛顿法求 X1
hist = []
Tn, it, ok = st_fk(L1, ST_HOME, tol=1e-13, hist=hist)
assert ok
pose_err = max(np.abs(Tn[:3, 3] - X1[:3, 3]).max(), np.abs(Tn[:3, :3] - X1[:3, :3]).max())
assert pose_err < 1e-12
res_txt = "、".join(f"{r:.1e}".replace("e-0", "e-").replace("e+0", "e+") for r in hist)
res_txt_en = ", ".join(f"{r:.1e}".replace("e-0", "e-").replace("e+0", "e+") for r in hist)
ratio = [hist[k + 1] / hist[k] ** 2 for k in range(len(hist) - 1) if hist[k + 1] > 1e-14]

# ---------------------------------------------------------------- (5) 实时跟踪
dt, Tend = 1e-3, 5.0
ts = np.arange(0, Tend + dt / 2, dt)


def motion(t):
    """多轴正弦运动：升降、前后、横滚、俯仰、偏航，频率不同。"""
    return pose(rpy(rad(8) * math.sin(2 * math.pi * 0.5 * t), rad(6) * math.sin(2 * math.pi * 0.7 * t + 1.0),
                    rad(10) * math.sin(2 * math.pi * 0.3 * t)),
                [0.04 * math.sin(2 * math.pi * 0.4 * t), 0.03 * math.sin(2 * math.pi * 0.6 * t + 0.5), 0.6 + 0.05 * math.sin(2 * math.pi * 0.8 * t)])


its_prev, its_home, err_track = [], [], 0.0
Tp = motion(0.0)
Lall = []
for t in ts:
    Tt = motion(t)
    L = st_ik(Tt)
    Lall.append(L)
    assert L.max() < ST_LMAX and L.min() > ST_LMIN
    Tq, k, ok = st_fk(L, Tp, tol=1e-10)
    assert ok
    its_prev.append(k)
    err_track = max(err_track, np.abs(Tq[:3, 3] - Tt[:3, 3]).max())
    Tp = Tq
    if int(round(t / dt)) % 50 == 0:
        _, k2, ok2 = st_fk(L, ST_HOME, tol=1e-10)
        assert ok2
        its_home.append(k2)
its_prev, its_home = np.array(its_prev), np.array(its_home)
Lall = np.array(Lall)

# ---------------------------------------------------------------- (6) 多解
N = 4000
T0 = np.zeros((N, 4, 4))
T0[:, :3, :3] = random_rotations(N, rng)
T0[:, :3, 3] = rng.uniform([-0.8, -0.8, -0.9], [0.8, 0.8, 0.9], (N, 3))
T0[:, 3, 3] = 1
Tb, okb = st_fk_batch(L1, T0, itmax=80)
sols = distinct_poses(Tb[okb])
sols.sort(key=lambda S: -S[2, 3])
n_sols = len(sols)
above = [S for S in sols if S[2, 3] > 0]
Sm = np.diag([1.0, 1.0, -1.0])
for S in above:                                          # 定理 18.3.3：关于机架平面的镜像也是解
    M = pose(Sm @ S[:3, :3] @ Sm, Sm @ S[:3, 3])
    assert np.abs(st_ik(M) - L1).max() < 1e-9
    assert any(np.abs(M - Q).max() < 1e-6 for Q in sols)
for S in sols:
    assert np.abs(st_ik(S) - L1).max() < 1e-10
hit_true = 100 * np.mean([np.abs(T_ - X1).max() < 1e-6 for T_ in Tb[okb]])
conv_pct = 100 * okb.mean()
z_above = [S[2, 3] for S in above]
tilt_above = [deg(math.acos(max(-1.0, min(1.0, S[2, 2])))) for S in above]  # 平台法线与 z 轴的夹角
assert n_sols == 8 and len(above) == 4

# ---------------------------------------------------------------- (7) 全部复数解：多项式同伦法
# 位姿用施图迪参数 (x, y) ∈ ℂ⁸ 表示：x 是表示转动的四元数（不必归一化），y = ½ t x（t 为平移，纯四元数），
# 施图迪二次曲面 x·y = 0。腿长方程乘以 x·x 后化为 (x, y) 的二次齐次式：
#   (|a|² + |b|² − l²) x·x + 4 y·y + 4 Re(x b ȳ) − 2 a·vec(x b x̄) − 4 a·vec(y x̄) = 0。
# 七个二次方程加一个随机的线性方程（射影空间中的一个仿射片），按总次数从 2⁷ = 128 个起点出发跟踪。


def qmul(p_, q_):
    return np.concatenate([[p_[0] * q_[0] - p_[1:] @ q_[1:]], p_[0] * q_[1:] + q_[0] * p_[1:] + np.cross(p_[1:], q_[1:])])


def qconj(q_):
    return np.concatenate([[q_[0]], -q_[1:]])


def rot2quat(R):
    w = math.sqrt(max(0.0, 1 + np.trace(R))) / 2
    if w > 1e-6:
        return np.array([w, (R[2, 1] - R[1, 2]) / (4 * w), (R[0, 2] - R[2, 0]) / (4 * w), (R[1, 0] - R[0, 1]) / (4 * w)])
    raise ValueError("near 180°")


def quat2rot(q_):
    q_ = q_ / np.linalg.norm(q_)
    return np.array([qmul(qmul(q_, np.r_[0, e]), qconj(q_))[1:] for e in np.eye(3)]).T


def leg_poly(z, i, L):
    x, y = z[:4], z[4:]
    a, b = ST_A[i], np.r_[0, ST_B[i]]
    return ((a @ a + b @ b - L[i] ** 2) * (x @ x) + 4 * (y @ y) + 4 * qmul(qmul(x, b), qconj(y))[0]
            - 2 * a @ qmul(qmul(x, b), qconj(x))[1:] - 4 * a @ qmul(y, qconj(x))[1:])


def quad_form(f, n=8):
    E = np.eye(n)
    Q = np.diag([f(E[i]) for i in range(n)])
    for i in range(n):
        for j in range(i + 1, n):
            Q[i, j] = Q[j, i] = (f(E[i] + E[j]) - Q[i, i] - Q[j, j]) / 2
    return Q


Qs = np.array([quad_form(lambda z, i=i: leg_poly(z, i, L1)) for i in range(6)] + [quad_form(lambda z: z[:4] @ z[4:])])
x1 = rot2quat(X1[:3, :3])
z1 = np.r_[x1, 0.5 * qmul(np.r_[0, X1[:3, 3]], x1)]
assert np.abs(np.einsum("kij,i,j->k", Qs, z1, z1)).max() < 1e-12          # X1 满足这组二次方程
hrng = np.random.default_rng(1803)
cpatch = hrng.normal(size=8) + 1j * hrng.normal(size=8)
gamma = np.exp(2j * math.pi * hrng.uniform())


def Hfun(z, t):
    F = np.einsum("kij,i,j->k", Qs, z, z)
    G = z[:7] ** 2 - z[7] ** 2
    return np.r_[(1 - t) * gamma * G + t * F, cpatch @ z - 1]


def Hz(z, t):
    JF = 2 * np.einsum("kij,j->ki", Qs, z)
    JG = np.zeros((7, 8), complex)
    JG[np.arange(7), np.arange(7)] = 2 * z[:7]
    JG[:, 7] = -2 * z[7]
    return np.vstack([(1 - t) * gamma * JG + t * JF, cpatch])


def Ht(z, t):
    return np.r_[np.einsum("kij,i,j->k", Qs, z, z) - gamma * (z[:7] ** 2 - z[7] ** 2), 0]


def track(z):
    """沿 t: 0 → 1 跟踪一条路径：四阶龙格-库塔预测，牛顿校正，步长自适应。"""
    t, dt = 0.0, 0.01
    while t < 1:
        dt = min(dt, 1 - t)
        f = lambda zz, tt: -np.linalg.solve(Hz(zz, tt), Ht(zz, tt))
        k1 = f(z, t); k2 = f(z + dt / 2 * k1, t + dt / 2); k3 = f(z + dt / 2 * k2, t + dt / 2); k4 = f(z + dt * k3, t + dt)
        zp = z + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        good = False
        for _ in range(3):
            dz = np.linalg.solve(Hz(zp, t + dt), Hfun(zp, t + dt))
            zp = zp - dz
            if np.linalg.norm(dz) < 1e-10 * (1 + np.linalg.norm(zp)):
                good = True
                break
        if good and np.linalg.norm(zp - z) < 0.3 * (1 + np.linalg.norm(z)):
            z, t, dt = zp, t + dt, min(dt * 1.5, 0.05)
        else:
            dt /= 2
            if dt < 1e-12:
                return z, False
    return z, True


cplx = []
n_paths = n_degen = 0
for sg in np.array(np.meshgrid(*[[1, -1]] * 7)).reshape(7, -1).T:
    z0 = np.r_[sg, 1].astype(complex)
    z0 = z0 / (cpatch @ z0)
    n_paths += 1
    try:
        z, ok = track(z0)
    except np.linalg.LinAlgError:
        ok = False
    if not ok:                                            # 路径终止在奇异的端点上：x → 0，不对应任何转动
        n_degen += 1
        for _ in range(30):                               # 在 t = 1 处用牛顿法逼近端点（奇异端点处收敛很慢）
            z = z - np.linalg.lstsq(Hz(z, 1.0), Hfun(z, 1.0), rcond=None)[0]
        assert np.linalg.norm(z[:4]) < 1e-4 * np.linalg.norm(z)
        continue
    for _ in range(5):
        z = z - np.linalg.solve(Hz(z, 1.0), Hfun(z, 1.0))
    assert np.linalg.norm(Hfun(z, 1.0)) < 1e-10 and np.linalg.cond(Hz(z, 1.0)) < 1e8
    zn = z / z[np.argmax(np.abs(z))]
    if not any(np.abs(zn - u).max() < 1e-7 for u in cplx):
        cplx.append(zn)
n_cplx = len(cplx)
real_h = [u.real for u in cplx if np.abs(u.imag).max() < 1e-8]
for u in real_h:                                          # 每个实数解换回位姿，与随机初值找到的 8 个逐一对应
    x, y = u[:4], u[4:]
    S = pose(quat2rot(x), 2 * qmul(y, qconj(x))[1:] / (x @ x))
    assert np.abs(st_ik(S) - L1).max() < 1e-9
    assert sum(np.abs(S - Q).max() < 1e-6 for Q in sols) == 1
assert len(real_h) == n_sols == 8 and n_cplx % 2 == 0

out(L1=L1, L1_txt=T("、".join(f"{v:.4f}" for v in L1), ", ".join(f"{v:.4f}" for v in L1)), L0=L0[0],
    L1_min=L1.min(), L1_max=L1.max(), tiltU_max=tiltU.max(), coneS_max=coneS.max(),
    heave_up=heave_up, heave_dn=heave_dn, roll_max=roll_max, pitch_p=pitch_p, pitch_m=pitch_m, yaw_max=yaw_max,
    ldot_txt=T("、".join(f"{v:.4f}" for v in ldot), ", ".join(f"{v:.4f}" for v in ldot)), ldot_max=np.abs(ldot).max(),
    err2_a=err2[0], err2_b=err2[1], err2_c=err2[2],
    n_it=it, res_txt=T(res_txt, res_txt_en), ratio_max=max(ratio), pose_err=pose_err,
    it_prev_mean=its_prev[1:].mean(), it_prev_max=its_prev[1:].max(), it_home_mean=its_home.mean(), it_home_max=its_home.max(),
    err_track=err_track, n_steps=len(ts), Lmin_track=Lall.min(), Lmax_track=Lall.max(),
    n_sols=n_sols, conv_pct=conv_pct, hit_true=hit_true, N=N, n_paths=n_paths, n_degen=n_degen, n_cplx=n_cplx, n_real_h=len(real_h),
    z_above=T("、".join(f"{z:.3f}" for z in z_above), ", ".join(f"{z:.3f}" for z in z_above)),
    tilt_above=T("、".join(f"{a:.1f}°" for a in tilt_above), ", ".join(f"{a:.1f}°" for a in tilt_above)))
