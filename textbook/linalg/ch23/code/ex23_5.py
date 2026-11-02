"""23.5 节：非线性最小二乘。
(1) AGV 的 UWB 定位：仓库四角的 4 个基站测出到 AGV 的距离（噪声 5 cm），求 AGV 的位置——残差对位置是非线性的。
高斯–牛顿法从仓库中心出发，记录每步的位置误差：残差为零时（无噪声）近似二次收敛，有噪声时线性收敛但几步就够；
(2) 关节电机绕组的冷却曲线：停机后测 20 分钟（每 10 s 一点，噪声 0.2 K），拟合两指数模型 T(t) = c₁e^{−t/τ₁} + c₂e^{−t/τ₂}（16.1 节的两节点模型）。
初值较好时高斯–牛顿与列文伯格–马夸特都收敛到同一组参数；初值差（τ₁ = 5 s、τ₂ = 2000 s）时高斯–牛顿把 τ₂ 推成负数、停在错误的地方，
列文伯格–马夸特仍收敛；(3) 参数的标准差：σ²(JᵀJ)⁻¹。"""
import numpy as np

from _num import sci
from bookout import out, vec

rng = np.random.default_rng(23051)
# (1) UWB 定位
anchors = np.array([[0.0, 0.0], [30.0, 0.0], [30.0, 20.0], [0.0, 20.0]])
p_true = np.array([22.0, 6.0])
d_true = np.linalg.norm(anchors - p_true, axis=1)


def gn_uwb(d, p, steps=8):
    hist = [p.copy()]
    for _ in range(steps):
        diff = p - anchors
        rr = np.linalg.norm(diff, axis=1)
        J = diff / rr[:, None]
        r = d - rr
        p = p + np.linalg.lstsq(J, r, rcond=None)[0]
        hist.append(p.copy())
    return np.array(hist)


h0 = gn_uwb(d_true, np.array([15.0, 10.0]))
e0 = [float(np.linalg.norm(q - p_true)) for q in h0]
d_noisy = d_true + rng.normal(0, 0.05, 4)
h1 = gn_uwb(d_noisy, np.array([15.0, 10.0]))
pstar = h1[-1]
e1 = [float(np.linalg.norm(q - pstar)) for q in h1]
out(u_e0=", ".join(sci(e, 1) if e > 0 else "0" for e in e0[:6]), u_e1=", ".join(sci(e, 1) if e > 0 else "0" for e in e1[:6]),
    u_p=vec(pstar, 3), u_err=float(np.linalg.norm(pstar - p_true) * 100))
J = (pstar - anchors) / np.linalg.norm(pstar - anchors, axis=1)[:, None]
cov = 0.05 ** 2 * np.linalg.inv(J.T @ J)
out(u_sx=float(np.sqrt(cov[0, 0]) * 100), u_sy=float(np.sqrt(cov[1, 1]) * 100))

# (2) 冷却曲线
t = np.linspace(0, 1200, 121)
pt = np.array([25.0, 22.0, 35.0, 550.0])                 # c₁ (K), τ₁ (s), c₂ (K), τ₂ (s)
f = lambda p: p[0] * np.exp(-t / p[1]) + p[2] * np.exp(-t / p[3])
y = f(pt) + rng.normal(0, 0.2, t.size)


def jac(p):
    e1, e2 = np.exp(-t / p[1]), np.exp(-t / p[3])
    return np.column_stack([e1, p[0] * t / p[1] ** 2 * e1, e2, p[2] * t / p[3] ** 2 * e2])


def gauss_newton(p, it=12):
    for _ in range(it):
        dp = np.linalg.lstsq(jac(p), y - f(p), rcond=None)[0]
        p = p + dp
    return p


def lm(p, it=100, mu=1e-2):
    F = np.sum((y - f(p)) ** 2)
    k = 0
    for k in range(it):
        Jk = jac(p)
        H = Jk.T @ Jk
        dp = np.linalg.solve(H + mu * np.diag(np.diag(H)), Jk.T @ (y - f(p)))
        pn = p + dp
        Fn = np.sum((y - f(pn)) ** 2)
        if Fn < F:
            p, F, mu = pn, Fn, mu / 3
            if np.linalg.norm(dp) < 1e-9 * np.linalg.norm(p):
                break
        else:
            mu *= 4
    return p, k + 1


rms = lambda p: float(np.sqrt(np.mean((y - f(p)) ** 2)))
good = np.array([30.0, 100.0, 30.0, 300.0])
bad = np.array([50.0, 5.0, 10.0, 2000.0])
pg = gauss_newton(good)
pl, nl = lm(good)
pgb = gauss_newton(bad)
plb, nlb = lm(bad)
out(c_good_gn=vec(pg, 1), c_good_lm=vec(pl, 1), c_rms=rms(pl), c_bad_gn=vec(pgb[:3], 1), c_bad_gn_tau2=sci(float(pgb[3]), 1), c_bad_gn_rms=rms(pgb), c_bad_lm=vec(plb, 1), c_bad_lm_rms=rms(plb),
    c_it=nlb, c_init_rms=rms(bad))
Jl = jac(plb)
cov = 0.2 ** 2 * np.linalg.inv(Jl.T @ Jl)
out(c_sd=vec(np.sqrt(np.diag(cov)), 2))
