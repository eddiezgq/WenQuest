"""22.3 节：步长自适应。RE 40 计入电感的启动（状态 i、ω），30 ms 时突加负载转矩 0.15 N·m，仿真 60 ms：
自己写的休恩–欧拉嵌入式方法（2 阶，用 1 阶解估计误差）按误差自动调步长；与固定步长、scipy 的 RK45 比较步数。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import out

V, R, L, k, J = 48.0, 1.13, 0.33e-3, 60.3e-3, 137e-7
TL = lambda t: 0.15 if t >= 0.03 else 0.0


def f(t, y):
    i, w = y
    return np.array([(V - R * i - k * w) / L, (k * i - TL(t)) / J])


T = 0.06
refs = solve_ivp(f, (0, T), [0, 0], method="DOP853", rtol=1e-12, atol=1e-12, max_step=1e-5, dense_output=True)
ref = refs.sol(T)


def adaptive(tol):
    t, y, h = 0.0, np.zeros(2), 1e-6
    hs, ts, rej = [], [], 0
    ys.clear()
    scale = np.array([40.0, 800.0])                 # 电流、转速的典型量级，用来把误差无量纲化
    while t < T - 1e-15:
        h = min(h, T - t)
        k1 = f(t, y)
        k2 = f(t + h, y + h * k1)
        y_hi = y + h / 2 * (k1 + k2)                # 休恩法（2 阶）
        y_lo = y + h * k1                           # 欧拉法（1 阶）
        err = np.max(np.abs(y_hi - y_lo) / scale)
        if err <= tol:
            t += h; y = y_hi; hs.append(h); ts.append(t); ys.append(y.copy())
        else:
            rej += 1
        h *= min(4.0, max(0.2, 0.9 * math.sqrt(tol / max(err, 1e-300))))
    return y, np.array(hs), np.array(ts), rej, np.array(ys)


ys = []
y, hs, ts, rej, Y = adaptive(1e-5)
maxerr = float(np.max(np.abs(Y[:, 1] - refs.sol(ts)[1])))
out(ad_tol=1e-5, ad_maxerr=maxerr, ad_n=len(hs), ad_rej=rej, ad_hmin_us=float(hs.min() * 1e6), ad_hmax_us=float(hs.max() * 1e6),
    ad_err_w=float(abs(y[1] - ref[1])), ad_h_at_load_us=float(hs[(ts > 0.0299) & (ts < 0.0301)].min() * 1e6),
    ad_h_after_us=float(hs[np.argmin(np.abs(ts - 0.0301))] * 1e6))
# 固定步长休恩法要使全程最大误差不超过自适应的结果，需要多少步。为了公平，让它在 30 ms 处分段
# （前半段负载为 0，后半段为 0.15 N·m，网格恰好落在突变时刻上），否则跨过突变的那一步误差很大
def fixed_maxerr(n):                                  # n 为偶数
    h = T / n
    yy = np.zeros(2); me = 0.0
    for j in range(n):
        load = 0.15 if j >= n // 2 else 0.0
        g = lambda y: np.array([(V - R * y[0] - k * y[1]) / L, (k * y[0] - load) / J])
        k1 = g(yy); k2 = g(yy + h * k1)
        yy = yy + h / 2 * (k1 + k2)
        me = max(me, abs(yy[1] - refs.sol((j + 1) * h)[1]))
    return me


lo, hi = 500, 10000                                  # 以 2 步为单位二分
while hi - lo > 1:
    mid = (lo + hi) // 2
    if fixed_maxerr(2 * mid) <= maxerr:
        hi = mid
    else:
        lo = mid
n = 2 * hi
out(fx_n=n, fx_h_us=T / n * 1e6, fx_err_unaligned=fixed_maxerr(n + 1))


# scipy 的 RK45：rtol = atol = 1e-5 时的步数与全程最大误差；再把容差调小到全程最大误差与自适应休恩法相当
def rk45(tol):
    s = solve_ivp(f, (0, T), [0, 0], method="RK45", rtol=tol, atol=tol)
    return s, float(np.max(np.abs(s.y[1] - refs.sol(s.t)[1])))


s, e = rk45(1e-5)
out(sp_nfev=int(s.nfev), sp_steps=len(s.t) - 1, sp_maxerr=e)
tol = 1e-5
while e > maxerr:
    tol /= 1.5
    s, e = rk45(tol)
out(sp2_tol=tol, sp2_nfev=int(s.nfev), sp2_steps=len(s.t) - 1, sp2_maxerr=e)
# 步数分布：开始 1 ms 内、负载突变后 1 ms 内各用了多少步
out(ad_n_start=int(np.sum(ts <= 1e-3)), ad_n_load=int(np.sum((ts > 0.03) & (ts <= 0.031))),
    ad_h_mid_us=float(hs[np.argmin(np.abs(ts - 0.025))] * 1e6), ad_ratio=n / len(hs))
