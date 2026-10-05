"""11.6 节：一维数值优化——由带噪声的阶跃响应数据估计电机的时间常数 τ：最小化 S(τ) = Σ(yᵢ − (1 − e^{−tᵢ/τ}))²。
比较黄金分割法、梯度下降（两种步长）与牛顿法的迭代次数；梯度下降的稳定条件 η < 2/S″(τ*)。"""
import math
import random

from bookout import out

random.seed(116)
tau_true, sigma = 0.08, 0.01
ts = [0.01 * i for i in range(41)]
ys = [1 - math.exp(-t / tau_true) + random.gauss(0, sigma) for t in ts]
S = lambda tau: sum((y - (1 - math.exp(-t / tau))) ** 2 for t, y in zip(ts, ys))
dS = lambda tau: sum(-2 * (y - (1 - math.exp(-t / tau))) * (-math.exp(-t / tau) * t / tau ** 2) for t, y in zip(ts, ys))
h = 1e-7
ddS = lambda tau: (dS(tau + h) - dS(tau - h)) / (2 * h)
out(n_data=len(ts), tau_true=tau_true, sigma=sigma)

# 黄金分割法：[0.02, 0.3]，区间长度缩到 1e-8
g = (math.sqrt(5) - 1) / 2
a, b = 0.02, 0.30
c, d = b - g * (b - a), a + g * (b - a)
fc, fd = S(c), S(d)
k = 0
while b - a > 1e-8:
    if fc < fd:
        b, d, fd = d, c, fc
        c = b - g * (b - a)
        fc = S(c)
    else:
        a, c, fc = c, d, fd
        d = a + g * (b - a)
        fd = S(d)
    k += 1
tau_g = (a + b) / 2
out(gold_n=k, gold_tau=tau_g, gold_evals=k + 2)

# 牛顿法：τ ← τ − S′/S″
tau, n = 0.15, 0
while True:
    step = dS(tau) / ddS(tau)
    tau -= step
    n += 1
    if abs(step) < 1e-12 or n > 50:
        break
tau_n = tau
c2 = ddS(tau_n)
out(newton_n=n, newton_tau=tau_n, Spp=c2, eta_crit=2 / c2, S_min=S(tau_n), rms=math.sqrt(S(tau_n) / len(ts)))


# 梯度下降：τ ← τ − η S′(τ)
def gd(eta, tau=0.15, tol=1e-10, kmax=100000):
    for i in range(1, kmax + 1):
        step = eta * dS(tau)
        tau -= step
        if not math.isfinite(tau) or tau <= 0:
            return i, float("nan")
        if abs(step) < tol:
            return i, tau
    return kmax, tau


eta1 = 0.5 / c2
eta2 = 1.9 / c2
n1, t1 = gd(eta1)
n2, t2 = gd(eta2)
n3, t3 = gd(2.2 / c2, kmax=200)
x = 0.15
for _ in range(400):
    x -= 2.2 / c2 * dS(x)
cyc_a, cyc_b = sorted((x, x - 2.2 / c2 * dS(x)))
out(gd_cyc_a=cyc_a, gd_cyc_b=cyc_b)
out(gd_eta1=eta1, gd_n1=n1, gd_t1=t1, gd_eta2=eta2, gd_n2=n2, gd_t2=t2, gd_n3=n3, gd_t3_ok=int(math.isfinite(t3) and abs(t3 - tau_n) < 1e-6))
