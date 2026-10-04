"""Examples 9.4.1–9.4.4: maximum likelihood and least squares.

9.4.1 Five ultrasonic range readings (mm): with the standard deviation known, the likelihood function is largest at the
      sample mean; a numerical search agrees with the formula.
9.4.2 AGV docking at a charger: laser rangefinder (σ = 3 mm) reads 152 mm, ultrasonic sensor (σ = 10 mm) reads 143 mm.
      Weighted least squares = maximum likelihood: x̂ and its standard deviation; compared with the plain average and with
      the laser alone, and the standard deviation of each estimator checked by Monte Carlo.
9.4.3 Calibration of a force sensor (see Section 39.5): u = a + bF, with noise std growing with the load,
      σᵢ = 0.05 + 0.002Fᵢ (mV). a, b and their covariance matrices by ordinary and weighted least squares; Eq. (9.4.9)
      checked by Monte Carlo, and the smaller variance of the weighted estimate verified (Theorem 9.4.3).
9.4.4 Nine ultrasonic readings, one of them an outlier caused by a multipath echo: mean, median and Huber estimate
      (iteratively reweighted) compared.
"""
import math

import numpy as np

from bookout import out, tex

rng = np.random.default_rng(904)

# ---------------------------------------------------------------- Example 9.4.1 likelihood function
zs = np.array([148.0, 155.0, 151.0, 144.0, 157.0])          # ultrasonic readings, mm
sig_u = 10.0
mu_grid = np.linspace(120, 180, 600001)
loglik = np.array([-0.5 * np.sum((zs[:, None] - mu_grid[None, :]) ** 2, axis=0) / sig_u ** 2])[0] \
    - len(zs) * math.log(sig_u * math.sqrt(2 * math.pi))
mu_ml = mu_grid[np.argmax(loglik)]
assert abs(mu_ml - zs.mean()) < 1e-3
sig_ml = math.sqrt(np.mean((zs - zs.mean()) ** 2))          # maximum likelihood estimate when σ is unknown (divides by n)
s_unb = zs.std(ddof=1)

# ---------------------------------------------------------------- Example 9.4.2 two sensors
s1, s2 = 3.0, 10.0                                          # mm
z1, z2 = 152.0, 143.0
A = np.array([[1.0], [1.0]])
W = np.diag([1 / s1 ** 2, 1 / s2 ** 2])
P = np.linalg.inv(A.T @ W @ A)
xhat = (P @ A.T @ W @ np.array([z1, z2]))[0]
sig_hat = math.sqrt(P[0, 0])
w1 = (1 / s1 ** 2) / (1 / s1 ** 2 + 1 / s2 ** 2)
assert abs(xhat - (w1 * z1 + (1 - w1) * z2)) < 1e-12
sig_avg = math.sqrt(s1 ** 2 + s2 ** 2) / 2
x_true = 150.0
M = 200000
Z1 = x_true + s1 * rng.standard_normal(M)
Z2 = x_true + s2 * rng.standard_normal(M)
mc_w = np.std(w1 * Z1 + (1 - w1) * Z2, ddof=1)
mc_avg = np.std((Z1 + Z2) / 2, ddof=1)
mc_l = np.std(Z1, ddof=1)
assert abs(mc_w / sig_hat - 1) < 0.01 and abs(mc_avg / sig_avg - 1) < 0.01
# variance w²σ1² + (1 − w)²σ2² for any weight w, smallest at w1
ws = np.linspace(0, 1, 100001)
vs = ws ** 2 * s1 ** 2 + (1 - ws) ** 2 * s2 ** 2
assert abs(ws[np.argmin(vs)] - w1) < 1e-4

# ---------------------------------------------------------------- Example 9.4.3 calibration line
F = np.array([0.0, 20, 40, 60, 80, 100])                   # reference forces, N
a0, b0 = 0.3, 0.2                                           # true zero point mV, sensitivity mV/N
sig_i = 0.05 + 0.002 * F                                    # noise std at each point, mV
u = a0 + b0 * F + sig_i * rng.standard_normal(len(F))       # readings of this calibration
Ad = np.column_stack([np.ones_like(F), F])
Wd = np.diag(1 / sig_i ** 2)
ols = np.linalg.solve(Ad.T @ Ad, Ad.T @ u)
wls = np.linalg.solve(Ad.T @ Wd @ Ad, Ad.T @ Wd @ u)
C_wls = np.linalg.inv(Ad.T @ Wd @ Ad)                       # Eq. (9.4.9)
Lo = np.linalg.solve(Ad.T @ Ad, Ad.T)
C_ols = Lo @ np.diag(sig_i ** 2) @ Lo.T                     # true covariance of ordinary least squares (Eq. (9.2.5))
# two algorithms: normal equations and "ordinary least squares after dividing each row by σᵢ" (QR)
Aw = Ad / sig_i[:, None]
uw = u / sig_i
assert np.allclose(np.linalg.lstsq(Aw, uw, rcond=None)[0], wls, atol=1e-12)
# Monte Carlo: the calibration repeated 200,000 times
K = 200000
U = a0 + b0 * F[None, :] + sig_i[None, :] * rng.standard_normal((K, len(F)))
est_w = np.linalg.solve(Ad.T @ Wd @ Ad, Ad.T @ Wd @ U.T)
est_o = Lo @ U.T
Cw_mc = np.cov(est_w)
Co_mc = np.cov(est_o)
assert np.allclose(Cw_mc, C_wls, rtol=0.03, atol=1e-12) and np.allclose(Co_mc, C_ols, rtol=0.03, atol=1e-12)
assert np.all(np.linalg.eigvalsh(C_ols - C_wls) > -1e-15)   # Theorem 9.4.3: the difference is positive semidefinite
assert abs(est_w.mean(axis=1)[1] - b0) < 1e-4                 # unbiased

# ---------------------------------------------------------------- Example 9.4.4 outlier
zr = np.array([150.0, 148, 153, 151, 149, 152, 147, 150, 236])
mean_r = zr.mean()
med_r = float(np.median(zr))
k_h = 1.345                                                 # threshold of the Huber function (in units of the noise std)
c = k_h * 2.0                                               # noise std taken as 2 mm
m = med_r
for _ in range(100):                                        # iterative reweighting
    r = zr - m
    wgt = np.where(np.abs(r) <= c, 1.0, c / np.maximum(np.abs(r), 1e-12))
    m_new = np.sum(wgt * zr) / np.sum(wgt)
    if abs(m_new - m) < 1e-12:
        break
    m = m_new
hub = m
# check: the Huber estimate satisfies Σ ψ(zᵢ − m) = 0
psi = np.clip(zr - hub, -c, c)
assert abs(psi.sum()) < 1e-9
w_out = c / abs(zr[-1] - hub)
mean_clean = zr[:-1].mean()
# the median minimizes the sum of absolute deviations
grid = np.linspace(140, 160, 200001)
lad = np.abs(zr[:, None] - grid[None, :]).sum(axis=0)
assert abs(grid[np.argmin(lad)] - med_r) < 1e-3

out(
    zs=", ".join(f"{v:.0f}" for v in zs), mu_ml=mu_ml, zbar=zs.mean(), sig_ml=sig_ml, s_unb=s_unb,
    s1=s1, s2=s2, z1=z1, z2=z2, w1=w1, w2=1 - w1, xhat=xhat, sig_hat=sig_hat, sig_avg=sig_avg, avg=(z1 + z2) / 2,
    mc_w=mc_w, mc_avg=mc_avg, mc_l=mc_l, M=M,
    F=", ".join(f"{v:.0f}" for v in F), u=", ".join(f"{v:.3f}" for v in u), sig_list=", ".join(f"{v:.2f}" for v in sig_i),
    a_ols=ols[0], b_ols=ols[1], a_wls=wls[0], b_wls=wls[1],
    sa_wls=math.sqrt(C_wls[0, 0]), sb_wls=math.sqrt(C_wls[1, 1]), sa_ols=math.sqrt(C_ols[0, 0]), sb_ols=math.sqrt(C_ols[1, 1]),
    sa_wmc=math.sqrt(Cw_mc[0, 0]), sb_wmc=math.sqrt(Cw_mc[1, 1]), sa_omc=math.sqrt(Co_mc[0, 0]), sb_omc=math.sqrt(Co_mc[1, 1]),
    rho_ab=C_wls[0, 1] / math.sqrt(C_wls[0, 0] * C_wls[1, 1]), K=K,
    k_h=k_h, zr=", ".join(f"{v:.0f}" for v in zr), mean_r=mean_r, med_r=med_r, hub=hub, c=c, w_out=w_out, mean_clean=mean_clean,
)
