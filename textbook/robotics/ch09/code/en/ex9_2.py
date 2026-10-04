"""Examples 9.2.1-9.2.4: covariance, transformation of covariance matrices and uncertainty propagation, all checked
by Monte Carlo.

9.2.1 Two force sensors on one power supply: readings X = S + N1, Y = S + N2; find the covariance and the correlation
      coefficient; the difference X − Y cancels the common fluctuation.
9.2.2 Laser ranging on an AGV: in the body frame {b} the variances along and across the beam differ; with the heading at
      30° they are transformed to {s} (Eq. (9.2.6)).
9.2.3 Planar 2R arm (upper-arm and forearm lengths of the UR5e): joint-angle standard deviation 0.1°; from
      Σ_p = J Σ_θ Jᵀ find the covariance matrix of the end-effector, the standard deviations, the correlation
      coefficient and the uncertainty ellipse; two configurations, θ = (30°, 60°) and the nearly straight θ = (30°, 10°).
9.2.4 UR5e (Table 12.1.1): six joint-angle standard deviations of 0.02°, the configuration of Example 12.3.1; the 3×3
      covariance matrix of the end-effector position.
Also: the probability inside an ellipse, 1 − e^{−c²/2}; with joint-angle standard deviations of 8° the linearization
fails (mean shift, distorted ellipse).
"""
import math

import numpy as np

from _prob import fk2, jac2, num_jac, ur_fk, ur_jac_pos
from bookout import out, tex

rng = np.random.default_rng(902)
d = math.radians
NMC = 200000

# ---------------------------------------------------------------- Example 9.2.1 two sensors on one power supply
sS, sN = 0.06, 0.08                                  # common fluctuation from the supply, own noise of each, N
S = sS * rng.standard_normal(NMC)
X = 15 + S + sN * rng.standard_normal(NMC)
Y = 15 + S + sN * rng.standard_normal(NMC)
cov_xy = sS ** 2
var_x = sS ** 2 + sN ** 2
rho = cov_xy / var_x
cov_mc = np.cov(X, Y)[0, 1]
rho_mc = np.corrcoef(X, Y)[0, 1]
sd_diff = math.sqrt(2) * sN                          # Var(X − Y) = Var X + Var Y − 2Cov
sd_diff_mc = np.std(X - Y, ddof=1)
sd_sum = math.sqrt(2 * var_x + 2 * cov_xy)
se_cov = math.sqrt((var_x ** 2 + cov_xy ** 2) / NMC)                # standard error of the sample covariance
assert abs(cov_mc - cov_xy) < 4 * se_cov and abs(rho_mc - rho) < 0.01
assert abs(sd_diff_mc - sd_diff) / sd_diff < 0.01
assert abs(np.std(X + Y, ddof=1) - sd_sum) / sd_sum < 0.01

# ---------------------------------------------------------------- Example 9.2.2 covariance transformed between frames
sr, st = 0.02, 0.05                                  # standard deviations along and across the beam, m
Sig_b = np.diag([sr ** 2, st ** 2])
phi = d(30)
R = np.array([[math.cos(phi), -math.sin(phi)], [math.sin(phi), math.cos(phi)]])
Sig_s = R @ Sig_b @ R.T
e_b = rng.standard_normal((2, NMC)) * np.array([[sr], [st]])
e_s = R @ e_b
assert np.allclose(np.cov(e_s), Sig_s, atol=4 * st ** 2 * math.sqrt(2 / NMC))   # 4 standard errors
assert abs(np.trace(Sig_s) - np.trace(Sig_b)) < 1e-15 and abs(np.linalg.det(Sig_s) - np.linalg.det(Sig_b)) < 1e-15

# ---------------------------------------------------------------- Example 9.2.3 planar 2R arm
sth = d(0.1)
Sig_th = np.diag([sth ** 2, sth ** 2])


def propagate(th_deg, sig_rad, n=NMC):
    th = np.array([d(v) for v in th_deg])
    J = jac2(th)
    assert np.allclose(J, num_jac(fk2, th), atol=1e-8)          # analytic Jacobian (2.1.9) agrees with differences
    Sp = J @ np.diag(sig_rad ** 2) @ J.T
    samples = th[:, None] + np.asarray(sig_rad)[:, None] * rng.standard_normal((2, n))
    P = fk2(samples)
    return th, J, Sp, P


resA = propagate((30, 60), np.array([sth, sth]))
resB = propagate((30, 10), np.array([sth, sth]))
outA, outB = {}, {}
for (th, J, Sp, P), o in ((resA, outA), (resB, outB)):
    p0 = fk2(th)
    Smc = np.cov(P)
    lam, V = np.linalg.eigh(Sp)
    sx, sy = math.sqrt(Sp[0, 0]), math.sqrt(Sp[1, 1])
    r = Sp[0, 1] / (sx * sy)
    assert np.allclose(Smc, Sp, rtol=0.02, atol=1e-11)
    # Mahalanobis distance and the share inside the ellipses
    Di = np.linalg.inv(Sp)
    dP = P - p0[:, None]
    m2 = np.einsum("in,ij,jn->n", dP, Di, dP)
    o.update(J=J, Sp=Sp, sx=sx, sy=sy, r=r, l1=math.sqrt(lam[1]), l2=math.sqrt(lam[0]),
             ang=math.degrees(math.atan2(V[1, 1], V[0, 1])) % 180, sx_mc=math.sqrt(Smc[0, 0]), sy_mc=math.sqrt(Smc[1, 1]),
             r_mc=Smc[0, 1] / math.sqrt(Smc[0, 0] * Smc[1, 1]), m2=m2, p0=p0)
c95 = math.sqrt(-2 * math.log(0.05))
pin = {c: 1 - math.exp(-c * c / 2) for c in (1, 2, c95)}
fin = {c: float(np.mean(outA["m2"] <= c * c)) for c in (1, 2, c95)}
assert all(abs(pin[c] - fin[c]) < 0.005 for c in pin)
# variance two ways: matrix form and "sum of squared joint contributions" (independent joints)
th = resA[0]
JA = outA["J"]
assert abs(outA["Sp"][0, 0] - (JA[0, 0] ** 2 + JA[0, 1] ** 2) * sth ** 2) < 1e-18

# ---------------------------------------------------------------- Example 9.2.4 UR5e
th_ur = np.array([d(v) for v in (30, -60, 90, -120, -90, 45)])
sur = d(0.02)
Jur = ur_jac_pos(th_ur)
Jnum = num_jac(lambda t: ur_fk(t)[:3, 3], th_ur)
assert np.allclose(Jur, Jnum, atol=1e-8)                        # geometric method agrees with differences
Sur = sur ** 2 * Jur @ Jur.T
lam_u, V_u = np.linalg.eigh(Sur)
n_ur = 100000
samp = th_ur[:, None] + sur * rng.standard_normal((6, n_ur))
Pur = np.array([ur_fk(samp[:, k])[:3, 3] for k in range(n_ur)]).T
Sur_mc = np.cov(Pur)
assert np.allclose(np.sqrt(np.diag(Sur_mc)), np.sqrt(np.diag(Sur)), rtol=0.02)
p_ur = ur_fk(th_ur)[:3, 3]
contrib = (Jur ** 2) * sur ** 2                                 # contribution of each joint to the variance of each coordinate
share_xyz = contrib.sum(axis=0) / contrib.sum()
v1 = V_u[:, 2] * np.sign(V_u[np.argmax(np.abs(V_u[:, 2])), 2])

# ---------------------------------------------------------------- linearization fails: joint-angle standard deviation 8°
sbig = d(8)
thL, JL, SpL, PL = propagate((30, 60), np.array([sbig, sbig]), n=NMC)
p0L = fk2(thL)
mean_shift = np.linalg.norm(PL.mean(axis=1) - p0L)
SmcL = np.cov(PL)
ratio_tr = math.sqrt(np.trace(SmcL) / np.trace(SpL))
# mean shift from the second-order term (compared with Monte Carlo): E[f] ≈ f(μ) + ½ Σ_ij H_ij Σθ_ij
h = 1e-4
corr = np.zeros(2)
for i in range(2):
    e = np.zeros(2)
    e[i] = h
    Hii = (fk2(thL + e) - 2 * fk2(thL) + fk2(thL - e)) / h ** 2
    corr += 0.5 * Hii * sbig ** 2
shift2 = np.linalg.norm(corr)
assert abs(shift2 - mean_shift) / shift2 < 0.1

mm = 1000
out(
    # 9.2.1
    sS=sS, sN=sN, cov_xy=cov_xy * 1e4, var_x=var_x * 1e4, rho=rho, cov_mc=cov_mc * 1e4, rho_mc=rho_mc,
    sd_x=math.sqrt(var_x), sd_diff=sd_diff, sd_diff_mc=sd_diff_mc, sd_sum=sd_sum, sd_sum_indep=math.sqrt(2 * var_x),
    # 9.2.2
    Sig_b=tex(Sig_b * 1e4, 1), Sig_s=tex(Sig_s * 1e4, 3), Sig_s_mc=tex(np.cov(e_s) * 1e4, 3),
    sxs=math.sqrt(Sig_s[0, 0]) * mm, sys_=math.sqrt(Sig_s[1, 1]) * mm, rho_s=Sig_s[0, 1] / math.sqrt(Sig_s[0, 0] * Sig_s[1, 1]),
    # 9.2.3 configuration A
    sth_mrad=sth * 1000, JA=tex(outA["J"], 4), SpA=tex(outA["Sp"] * 1e6, 4),
    sxA=outA["sx"] * mm, syA=outA["sy"] * mm, rA=outA["r"], l1A=outA["l1"] * mm, l2A=outA["l2"] * mm, angA=outA["ang"],
    sxA_mc=outA["sx_mc"] * mm, syA_mc=outA["sy_mc"] * mm, rA_mc=outA["r_mc"],
    a95A=c95 * outA["l1"] * mm, b95A=c95 * outA["l2"] * mm, pxA=outA["p0"][0], pyA=outA["p0"][1],
    # configuration B
    SpB=tex(outB["Sp"] * 1e6, 4), l1B=outB["l1"] * mm, l2B=outB["l2"] * mm, angB=outB["ang"],
    ratioB=outB["l1"] / outB["l2"], ratioA=outA["l1"] / outA["l2"], sxB_mc=outB["sx_mc"] * mm, syB_mc=outB["sy_mc"] * mm,
    sxB=outB["sx"] * mm, syB=outB["sy"] * mm, rB=outB["r"],
    # probability inside the ellipses
    p1=100 * pin[1], p2=100 * pin[2], c95=c95, f1=100 * fin[1], f2=100 * fin[2], f95=100 * fin[c95], NMC=NMC,
    # 9.2.4 UR5e
    sur_deg=0.02, pur=tex(p_ur, 4), Sur=tex(Sur * 1e8, 3), sdur=tex(np.sqrt(np.diag(Sur)) * mm, 4),
    sdur_mc=tex(np.sqrt(np.diag(Sur_mc)) * mm, 4), lmax=math.sqrt(lam_u[2]) * mm, lmid=math.sqrt(lam_u[1]) * mm,
    lmin=math.sqrt(lam_u[0]) * mm, v1=tex(v1, 3), n_ur=n_ur,
    shareJ1=100 * share_xyz[0], shareJ2=100 * share_xyz[1], shareJ3=100 * share_xyz[2],
    # linearization fails
    big_deg=8, shift_mm=mean_shift * mm, shift2_mm=shift2 * mm, ratio_tr=ratio_tr,
)
