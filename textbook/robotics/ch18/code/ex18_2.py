"""18.2 节：用旋量理论分析并联机构的约束与奇异。

(1) 算例 18.2.1：Delta 的一条支链。平行四边形宽 0.06 m（零件库模型）。按“两根杆长不变”写出下横杆相对上横杆的速度约束，
    求支链允许的动平台运动旋量（运动旋量系）和与之互易的约束力旋量（约束力旋量系）；与定理 18.2.2 的约束力偶
    n_k = t_k × u_k 比较。锁住电机后多出的驱动力旋量：沿杆的方向、过肘点的力；它对电机轴的功率系数等于 B_kk。
    三条支链合起来：动平台的运动旋量系是三维的纯平移（与程序 11.2.1 的结论一致）。
(2) 算例 18.2.2：Delta 的静力。动平台受竖直向下 10 N 的力和绕 z 轴 0.5 N·m 的力矩：把力旋量分解为三根杆的驱动力
    与三个约束力偶，电机力矩 τ = B f；力矩完全由约束力偶承担，电机感觉不到。用正解的差商（虚功）核对电机力矩。
(3) 算例 18.2.3：平面五杆沿 y 轴向下运动：det A、det B、末端受 20 N 向下力时的电机力矩、另一种装配模式的位置；
    正运动学奇异 y* = √(l₁² − c²)，此时两种装配模式重合（两圆相切）。逆运动学奇异：y = √((l₁ + l₂)² − c²)。
(4) 算例 18.2.4：Stewart 平台（几何同算例 11.5.4）。每条腿的驱动力旋量是沿腿的单位力（定理 18.2.3）；
    绕 z 轴转 ψ 时 det A(ψ)：在 ±90° 处为零（三个高度都如此），零空间给出绕竖直轴的螺旋运动；
    托住 500 N 竖直载荷时的最大腿力随 ψ 增大；ψ = 90° 时的腿长超出 18.3 节取定的行程。
(5) Delta 的约束奇异：主动臂转到 120°（超出限位）时三根杆都竖直，约束力偶共面；工作空间内 det N 的最小值。
"""
import math

import numpy as np

from _ch18 import (D_HI, D_LO, DELTA, FIVE, ST_A, ST_B, ST_LMAX, ST_LMIN, delbow, delta_AB, delta_couples, delta_fk,
                   delta_ik, delta_ok, delta_u, ek, elbow, five_AB, five_fk, five_ik, force_wrench, null_space, pose, rot,
                   screw_revolute, st_ik, st_W, tk)
from bookout import T, out, vec

deg = math.degrees
W_PAR = 0.06                                      # 平行四边形宽 (m)

# ---------------------------------------------------------------- (1) Delta 一条支链的旋量分析
p1 = np.array([0.05, -0.08, -0.47])
th1 = delta_ik(p1)
U = delta_u(p1, th1)
legs = []
for k in range(3):
    e, t = ek(k), tk(k)
    H, E = DELTA["Rb"] * e, elbow(k, th1[k])
    Pp = p1 + DELTA["Rp"] * e
    SR = screw_revolute(t, H)
    rows = []
    for s in (+1, -1):                            # 两根杆：上端 Uj 在主动臂上，下端 Qj 在动平台上，|Qj − Uj| 不变
        Uj, Qj = E + s * W_PAR / 2 * t, Pp + s * W_PAR / 2 * t
        d = Qj - Uj
        vU = SR[3:] + np.cross(SR[:3], Uj)        # 电机转动时 Uj 的速度（每 rad/s）
        rows.append(np.r_[np.cross(Qj, d), d, -d @ vU])     # d·(v + ω × Qj) − θ̇ d·vU = 0，未知数 (ω, v, θ̇)
    M = np.array(rows)
    Nfree, _ = null_space(M)                      # (𝒱, θ̇) 的全部解
    Tfree = Nfree[:6]                             # 支链允许的动平台运动旋量（张成运动旋量系）
    rank_T = np.linalg.matrix_rank(Tfree, 1e-9)
    Wc, _ = null_space(Tfree.T)                   # 与运动旋量系互易的力旋量：约束力旋量系
    n = np.cross(t, U[k])
    n /= np.linalg.norm(n)
    wc = Wc[:, 0] / np.linalg.norm(Wc[:, 0])
    assert Wc.shape[1] == 1 and rank_T == 5
    assert np.abs(wc[3:]).max() < 1e-12                            # 纯力偶（力的部分为零）
    assert min(np.abs(wc[:3] - n).max(), np.abs(wc[:3] + n).max()) < 1e-10   # 方向为 t_k × u_k
    # 锁住电机：θ̇ = 0
    Nlock, _ = null_space(M[:, :6])
    Wl, _ = null_space(Nlock.T)
    Fa = force_wrench(U[k], E)                    # 沿杆、过肘点的单位力
    assert Wl.shape[1] == 2 and np.abs(Fa @ Nlock).max() < 1e-12 and abs(Fa @ Tfree).max() > 1e-3
    Bk = Fa @ SR                                  # 驱动力旋量对电机轴旋量的功率系数
    assert abs(Bk - U[k] @ delbow(k, th1[k])) < 1e-12
    legs.append(dict(T=Tfree, n=n, Fa=Fa, B=Bk))
# 三条支链的运动旋量系之交 = 与三个约束力偶都互易的运动旋量
Cmat = np.array([np.r_[L["n"], 0, 0, 0] for L in legs])      # 约束力偶按行
Vplat, r_c = null_space(Cmat)
assert r_c == 3 and Vplat.shape[1] == 3 and np.abs(Vplat[:3]).max() < 1e-12     # 三维、纯平移
detN1 = np.linalg.det(np.array([L["n"] for L in legs]))
nk_txt = [vec(L["n"], 3) for L in legs]

# ---------------------------------------------------------------- (2) Delta 的静力
A, B = delta_AB(p1, th1)
G = np.vstack([np.hstack([np.array([np.cross(elbow(k, th1[k]), U[k]) for k in range(3)]), U]),     # 驱动力旋量 (E×u, u)
               np.hstack([np.array([L["n"] for L in legs]), np.zeros((3, 3))])])                    # 约束力偶 (n, 0)
F_ext = np.r_[0, 0, 0.5, 0, 0, -10.0]             # 平台对外施加的力旋量（对 {s} 原点）：绕 z 0.5 N·m，向下 10 N
# 力系作用在平台中心 p1：对原点的力矩要加上 p1 × f
F_ext[:3] += np.cross(p1, F_ext[3:])
fm = np.linalg.solve(G.T, F_ext)                  # F = Gᵀ (f; μ)
f_rod, mu = fm[:3], fm[3:]
tau = np.diag(B) * f_rod                          # τ_k = B_kk f_k
# 只有力矩（无力）时，电机力矩为零
fm_m = np.linalg.solve(G.T, np.r_[0, 0, 0.5, 0, 0, 0])
assert np.abs(fm_m[:3]).max() < 1e-12
# 虚功核对：电机 k 转一点，平台中心的位移 δp，τ_k = f·δp/δθ（平台只平移，力矩不做功）
fz = np.array([0, 0, -10.0])
for k in range(3):
    d = np.eye(3)[k] * 1e-7
    dp = (delta_fk(th1 + d) - delta_fk(th1 - d)) / 2e-7
    assert abs(fz @ dp - tau[k]) < 1e-6
tau_fz = tau.copy()

# ---------------------------------------------------------------- (3) 五杆沿 y 轴
c, l1, l2 = FIVE["c"], FIVE["l1"], FIVE["l2"]
y_star = math.sqrt(l1 ** 2 - c ** 2)                       # 正运动学奇异：B1、P、B2 共线（肘点在 (∓0.3, y)）
y_I = math.sqrt((l1 + l2) ** 2 - c ** 2)                   # 逆运动学奇异：支链伸直
ys = [0.40, 0.30, 0.20, 0.16, 0.14, 0.135]
rows5 = []
f20 = np.array([0, -20.0])
for y in ys:
    P = np.array([0.0, y])
    th = five_ik(P)
    A5, B5 = five_AB(P, th)
    J = np.linalg.solve(A5, B5)
    tau5 = J.T @ f20
    other = five_fk(th, -1)
    rows5.append((y, np.linalg.det(A5), np.linalg.det(B5), np.abs(tau5).max(), other[1]))
th_s = five_ik(np.array([0.0, y_star]))
A_s, _ = five_AB(np.array([0.0, y_star]), th_s)
assert abs(np.linalg.det(A_s)) < 1e-12
assert np.abs(five_fk(th_s, 1) - five_fk(th_s, -1)).max() < 1e-6          # 两种装配模式重合
th_I = five_ik(np.array([0.0, y_I - 1e-12]))
_, B_I = five_AB(np.array([0.0, y_I - 1e-12]), th_I)
assert abs(np.linalg.det(B_I)) < 1e-6
# 力矩 ∝ 1/|det A|：y → y* 时 |τ|·|det A| 趋于常数
k_ratio = [r[3] * abs(r[1]) for r in rows5[-3:]]
table5 = "\n".join(f"| {r[0]:.3f} | {r[1]:.4f} | {r[2]:.5f} | {r[3]:.1f} | {r[4] * 1000:.1f} |" for r in rows5)

# ---------------------------------------------------------------- (4) Stewart 平台
Th = pose(np.eye(3), [0, 0, 0.6])
Wh = st_W(Th)
detW0 = np.linalg.det(Wh)
# 定理 18.2.3 的核对：驱动力旋量（沿腿的力）与万向节两根轴、球关节三根轴的旋量都互易
for i in range(6):
    s = Wh[3:, i]
    a = ST_A[i]
    q = Th[:3, :3] @ ST_B[i] + Th[:3, 3]
    u1 = np.cross([0, 0, 1.0], s); u1 /= np.linalg.norm(u1)          # 万向节：第一根轴取水平，第二根轴垂直于第一根和腿
    u2 = np.cross(s, u1)
    for S in [screw_revolute(u1, a), screw_revolute(u2, a)] + [screw_revolute(w, q) for w in np.eye(3)]:
        assert abs(Wh[:, i] @ S) < 1e-12
    assert abs(Wh[:, i] @ np.r_[0, 0, 0, s] - 1) < 1e-12               # 对移动关节：功率系数为 1


def detW(psi, h):
    return np.linalg.det(st_W(pose(rot([0, 0, 1], psi), [0, 0, h])))


roots = {}
for h in (0.5, 0.6, 0.7):
    rr = []
    for a0 in (math.radians(80), math.radians(-100)):        # 在 ±90° 附近用二分法求根
        lo, hi = a0, a0 + math.radians(20)
        assert detW(lo, h) * detW(hi, h) < 0
        for _ in range(80):
            mid = (lo + hi) / 2
            if detW(lo, h) * detW(mid, h) <= 0:
                hi = mid
            else:
                lo = mid
        rr.append(deg((lo + hi) / 2))
    roots[h] = rr
assert all(abs(abs(r) - 90) < 1e-9 for rr in roots.values() for r in rr)
T90 = pose(rot([0, 0, 1], math.pi / 2), [0, 0, 0.6])
W90 = st_W(T90)
Nv, rk = null_space(W90.T, 1e-9)
assert rk == 5
v90 = Nv[:, 0] * np.sign(Nv[2, 0])
assert np.abs(v90[[0, 1, 3, 4]]).max() < 1e-9            # 只有 ω_z 和 v_z：绕竖直轴的螺旋运动
pitch90 = v90[5] / v90[2]
Nf, _ = null_space(W90, 1e-9)                              # 六条腿力的一组“自应力”：合力旋量为零
selfstress = Nf[:, 0] / np.abs(Nf[:, 0]).max()
legs90 = st_ik(T90)
F500 = np.r_[0, 0, 0, 0, 0, 500.0]                         # 平台托住载荷：对载荷施加竖直向上 500 N，作用线沿中心轴
fmax = []
for a in (0, 30, 60, 80, 85, 89):
    Ta = pose(rot([0, 0, 1], math.radians(a)), [0, 0, 0.6])
    fl = np.linalg.solve(st_W(Ta), F500)                   # 式 (18.2.7)：平台对外施加的力旋量 = Aᵀ f（st_W 返回 Aᵀ）
    fmax.append((a, np.abs(fl).max()))
f0 = fmax[0][1]
lo, hi = 0.0, math.pi / 2                                  # 腿长超出行程的最小转角（二分法）
for _ in range(60):
    mid = (lo + hi) / 2
    L = st_ik(pose(rot([0, 0, 1], mid), [0, 0, 0.6]))
    if L.max() > ST_LMAX or L.min() < ST_LMIN:
        hi = mid
    else:
        lo = mid
psi_stroke = deg(hi)
assert abs(f0 - 500 / 6 / (0.6 / st_ik(Th)[0])) < 1e-9     # ψ = 0：六条腿等分，f = 500/(6 cos α)

# ---------------------------------------------------------------- (5) Delta 的约束奇异
th120 = np.full(3, math.radians(120))
p120 = delta_fk(th120)
N120 = delta_couples(p120, th120)
detN120 = np.linalg.det(N120)
assert abs(detN120) < 1e-12 and np.abs(delta_u(p120, th120)[:, :2]).max() < 1e-12     # 三根杆都竖直
h = 0.02
gx = np.arange(-0.5, 0.5 + 1e-9, h)
gz = np.arange(-0.8, -0.15, h)
detN_min, detA_min, detB_min, nws = 9.0, 9.0, 9.0, 0
for x in gx:
    for y in gx:
        for z in gz:
            p = np.array([x, y, z])
            th = delta_ok(p)
            if th is None:
                continue
            nws += 1
            A_, B_ = delta_AB(p, th)
            detN_min = min(detN_min, abs(np.linalg.det(delta_couples(p, th))))
            detA_min = min(detA_min, abs(np.linalg.det(A_)))
            detB_min = min(detB_min, abs(np.linalg.det(B_)))
th_rest = delta_ik(np.array([0, 0, -0.42]))
detN_rest = np.linalg.det(delta_couples(np.array([0, 0, -0.42]), th_rest))

out(p1=vec(p1, 2), th1=", ".join(f"{deg(t):.2f}°" for t in th1), n1=nk_txt[0], n2=nk_txt[1], n3=nk_txt[2], detN1=detN1,
    B1=legs[0]["B"], B2=legs[1]["B"], B3=legs[2]["B"],
    f1=f_rod[0], f2=f_rod[1], f3=f_rod[2], mu1=mu[0], mu2=mu[1], mu3=mu[2], tau1=tau_fz[0], tau2=tau_fz[1], tau3=tau_fz[2],
    y_star=y_star, y_I=y_I, table5=table5, k_ratio_min=min(k_ratio), k_ratio_max=max(k_ratio),
    tau_04=rows5[0][3], tau_0135=rows5[-1][3],
    detW0=detW0, pitch90=pitch90, legs90_a=legs90[0], legs90_b=legs90[1], ss_a=selfstress[0], ss_b=selfstress[1],
    f0=f0, f60=fmax[2][1], f80=fmax[3][1], f85=fmax[4][1], f89=fmax[5][1],
    detN120=detN120, detN_min=detN_min, detA_min=detA_min, detB_min=detB_min, detN_rest=detN_rest, nws=nws,
    lmax=ST_LMAX, psi_stroke=psi_stroke)
