"""22.4 节：刚性方程与隐式方法。
(1) 标量刚性方程 y' = −λ(y − cos t)：显式欧拉、隐式欧拉在不同步长下的表现；
(2) RE 40 的“电–机–热”四状态模型（电流、转速、绕组温升、机壳温升），负载转矩每 2 s 通断一次，
    比较 scipy 的 RK45（显式）与 BDF、Radau（隐式）所用的函数调用次数；
(3) 自己写的隐式欧拉法 + 牛顿迭代，步长 10 ms。"""
import math
import time

import numpy as np
from scipy.integrate import solve_ivp

from bookout import T as TT, out

# ---------- (1) 标量刚性方程 ----------
lam = 1000.0
g = lambda t, y: -lam * (y - math.cos(t))
exact = lambda t: (lam ** 2 * math.cos(t) + lam * math.sin(t)) / (lam ** 2 + 1) - lam ** 2 / (lam ** 2 + 1) * math.exp(-lam * t)


def euler_fw(h, T=1.0):
    y, t = 0.0, 0.0
    for _ in range(round(T / h)):
        y += h * g(t, y); t += h
        if abs(y) > 1e6:
            return math.inf
    return y


def euler_bw(h, T=1.0):
    y, t = 0.0, 0.0
    for _ in range(round(T / h)):
        t += h
        y = (y + h * lam * math.cos(t)) / (1 + h * lam)   # 方程是线性的，隐式方程可以直接解出
    return y


rows = []
for h in (1e-3, 1.9e-3, 2.1e-3, 1e-2, 1e-1):
    ef, eb = euler_fw(h), euler_bw(h)
    tn = round(1.0 / h) * h                              # 实际到达的时刻（步数取整）
    fe = f"{abs(ef - exact(tn)):.2e}" if math.isfinite(ef) else TT("发散", "diverges")
    rows.append(f"| {h * 1000:g} | {h * lam:g} | {fe} | {abs(eb - exact(tn)):.2e} |")
# RK4 稳定区域与负实轴的交点：|1 − x + x²/2 − x³/6 + x⁴/24| = 1
from scipy.optimize import brentq
rk4lim = brentq(lambda x: abs(1 - x + x * x / 2 - x ** 3 / 6 + x ** 4 / 24) - 1, 2.0, 3.0)
# 多尔芒–普林斯五阶方法（RK45）的稳定函数：e^z 的五次泰勒多项式加 z⁶/600，与负实轴的交点
dp = lambda x: 1 - x + x ** 2 / 2 - x ** 3 / 6 + x ** 4 / 24 - x ** 5 / 120 + x ** 6 / 600
out(st_dplim=brentq(lambda x: abs(dp(x)) - 1, 2.5, 4.0))
out(st_rk4lim=rk4lim, st_rk4h_ms=rk4lim / lam * 1000)
out(st_lam=lam, st_hcrit=2 / lam, st_exact=exact(1.0), st_tab="\n".join(rows))

# ---------- (2) 电–机–热模型 ----------
V, R0, L, k, J = 48.0, 1.13, 0.33e-3, 60.3e-3, 137e-7
alpha = 0.0039                                   # 铜电阻温度系数（1/K）
R1, R2 = 4.65, 1.93
Cw, Ch = 41.5 / R2, 809.0 / R1
Bv = k * 68.6e-3 / (V / k)                       # 由空载电流折算的粘性摩擦系数
Vd = 24.0                                        # 驱动器给定的电压（半速运行）


def TL(t):
    return 0.15 if (t % 2.0) < 1.0 else 0.0     # 每 2 s 通断一次


def F(t, x):
    i, w, Tw, Th = x
    R = R0 * (1 + alpha * Tw)
    return np.array([(Vd - R * i - k * w) / L,
                     (k * i - Bv * w - TL(t)) / J,
                     (R * i * i - (Tw - Th) / R2) / Cw,
                     ((Tw - Th) / R2 - Th / R1) / Ch])


def jac(t, x, eps=1e-7):
    f0 = F(t, x); Jm = np.zeros((4, 4))
    for j in range(4):
        dx = np.zeros(4); dx[j] = eps * max(1.0, abs(x[j]))
        Jm[:, j] = (F(t, x + dx) - f0) / dx[j]
    return Jm


# 线性化的特征值：刚性比
x_typ = np.array([1.5, 330.0, 20.0, 8.0])
ev = np.sort(np.abs(np.linalg.eigvals(jac(0.5, x_typ)).real))[::-1]
out(mt_ev1=float(ev[0]), mt_ev2=float(ev[1]), mt_ev3=float(ev[2]), mt_ev4=float(ev[3]), mt_ratio=float(ev[0] / ev[-1]),
    mt_tau1_ms=1000 / float(ev[0]), mt_tau2_ms=1000 / float(ev[1]), mt_tau3_s=1 / float(ev[2]), mt_tau4_s=1 / float(ev[3]))

T = 120.0
res = {}
for m in ("RK45", "BDF", "Radau"):
    calls = [0]

    def Fc(t, x):                                    # 自己计数：含差分估计雅可比矩阵所用的调用
        calls[0] += 1
        return F(t, x)
    t0 = time.perf_counter()
    s = solve_ivp(Fc, (0, T), [0, 0, 0, 0], method=m, rtol=1e-6, atol=[1e-6, 1e-4, 1e-6, 1e-6], max_step=0.5)
    res[m] = dict(nfev=calls[0], steps=len(s.t) - 1, Tw=float(s.y[2, -1]), sec=time.perf_counter() - t0)
out(mt_T=T, mt_rk45_nfev=res["RK45"]["nfev"], mt_rk45_steps=res["RK45"]["steps"], mt_bdf_nfev=res["BDF"]["nfev"],
    mt_bdf_steps=res["BDF"]["steps"], mt_radau_nfev=res["Radau"]["nfev"], mt_radau_steps=res["Radau"]["steps"],
    mt_Tw_rk45=res["RK45"]["Tw"], mt_Tw_bdf=res["BDF"]["Tw"], mt_rk45_hmean_ms=T / res["RK45"]["steps"] * 1000,
    mt_speedup=res["RK45"]["nfev"] / res["BDF"]["nfev"])

# ---------- (3) 隐式欧拉 + 牛顿迭代，h = 10 ms ----------
def backward_euler(h, T):
    x, t, newton = np.zeros(4), 0.0, 0
    for _ in range(round(T / h)):
        t += h
        z = x.copy()
        for _it in range(20):                         # 解 z − x − h F(t, z) = 0
            G = z - x - h * F(t, z)
            Jg = np.eye(4) - h * jac(t, z)
            dz = np.linalg.solve(Jg, -G)
            z += dz; newton += 1
            if np.max(np.abs(dz) / np.array([1, 10, 1, 1])) < 1e-10:
                break
        x = z
    return x, newton


xb, nn = backward_euler(0.01, T)
ref = solve_ivp(F, (0, T), [0, 0, 0, 0], method="Radau", rtol=1e-10, atol=1e-10, max_step=0.05).y[:, -1]
out(be_h=0.01, be_steps=round(T / 0.01), be_newton_avg=nn / round(T / 0.01), be_Tw=float(xb[2]), be_Tw_ref=float(ref[2]),
    be_Tw_err=float(abs(xb[2] - ref[2])), be_Th=float(xb[3]))
# 显式欧拉在同样 10 ms 步长下发散
x = np.zeros(4); t = 0.0
for j in range(50):
    x = x + 0.01 * F(t, x); t += 0.01
    if not np.all(np.isfinite(x)) or np.max(np.abs(x)) > 1e12:
        break
out(fe_blow_steps=j + 1)
