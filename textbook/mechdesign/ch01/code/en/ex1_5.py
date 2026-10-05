"""Section 1.5, safety factor and reliability: stress-strength interference (both normally distributed), reliability
R = Φ(z), z = (S − 1)/√(S²C_lim² + C_σ²) (Examples 1.5.1 and 1.5.2, Figs. 1.5.1 and 1.5.2).
The scatter of the load is taken from the torque records of the digital factory's run-in test bench."""
import math

import numpy as np
from scipy.stats import norm

import _con as E
from bookout import T, figure, out, style
from sim.engine import torque_record          # digital-factory simulation shop: torque records of the run-in bench "duty simulation"


def z_of(S, Cl, Cs):
    return (S - 1) / math.sqrt((S * Cl) ** 2 + Cs ** 2)


def R_of(S, Cl, Cs):
    return float(norm.cdf(z_of(S, Cl, Cs)))


def S_for(R, Cl, Cs):
    """Mean safety factor for a required reliability (solves a quadratic equation)"""
    z = norm.ppf(R)
    a = 1 - z * z * Cl * Cl
    b, c = -2.0, 1 - z * z * Cs * Cs
    return (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)


# ---- run-in bench: starting peaks of 30 reducers, 3 starts each (conveyor duty)
peaks = []
for k in range(1, 31):
    r = torque_record("WQR-105-{:05d}".format(k), "WO-TS-1", "WQR-105")
    s = np.array(r["samples_nm"])
    seg = len(s) // 3
    peaks += [s[j * seg:j * seg + 20].max() / r["rated_nm"] for j in range(3)]
peaks = np.array(peaks)
k_mean, cov_bench = float(peaks.mean()), float(peaks.std(ddof=1) / peaks.mean())

# ---- Example 1.5.1: the extension (the Ø30 of Example 1.4.1)
S_nom = E.S_pick                                  # nominal safety factor: guaranteed minimum yield strength, largest recorded peak load
S_mu = S_nom * E.K_PEAK / k_mean                  # load at the mean peak (strength still the guaranteed minimum, on the safe side)
CL = 0.08                                         # coefficient of variation of yield strength (0.05–0.10 is usual for steel; assumed)
CS_SHOCK = 0.25                                   # coefficient of variation of the peaks for a shock-loaded machine (mixer, crusher, occasional jamming; assumed)
R1, R2 = R_of(S_mu, CL, cov_bench), R_of(S_mu, CL, CS_SHOCK)
# ---- Example 1.5.2: probability of failure not above one in a million
R_req = 1 - 1e-6
S_req1, S_req2 = S_for(R_req, CL, cov_bench), S_for(R_req, CL, CS_SHOCK)

# ---------------------------------------------------------------- Fig. 1.5.1: interference
plt = style()
fig, ax = plt.subplots(figsize=(6.4, 2.9))
x = np.linspace(0, 2.8, 800)
for Cs, ls, lab in ((cov_bench, "-", T("应力（输送机，分散小）", "stress (conveyor, small scatter)")),
                    (CS_SHOCK, "--", T("应力（冲击大的工作机）", "stress (shock-loaded machine)"))):
    ax.plot(x, norm.pdf(x, 1.0, Cs), color="#c0392b", ls=ls, lw=1.4, label=lab)
ax.plot(x, norm.pdf(x, S_mu, CL * S_mu), color="#2c6fbb", lw=1.6, label=T("强度", "strength"))
ax.fill_between(x, 0, np.minimum(norm.pdf(x, 1.0, CS_SHOCK), norm.pdf(x, S_mu, CL * S_mu)), color="#c0392b", alpha=0.25, lw=0)
ymax = 1.9 * norm.pdf(S_mu, S_mu, CL * S_mu)            # the conveyor curve is very narrow and tall; its top is cut off in the plot
ax.annotate(T("干涉区：可能失效", "interference: may fail"), (1.52, 0.05 * ymax), (0.05, 0.62 * ymax), fontsize=8,
            arrowprops=dict(arrowstyle="->", lw=0.8))
for xv, lab in ((1.0, r"$\mu_\sigma$"), (S_mu, r"$\mu_\mathrm{lim}$")):
    ax.axvline(xv, color="#1d2327", lw=0.6, ls=":")
    ax.text(xv + 0.03, ymax * 0.98, lab, ha="left", va="top", fontsize=9)
ax.set_ylim(0, ymax)
ax.set_xlabel(T("应力或强度（以平均应力为 1）", "stress or strength (mean stress = 1)"))
ax.set_yticks([])
ax.legend(fontsize=7.5, frameon=False, loc="upper right")
for s_ in ("top", "right", "left"):
    ax.spines[s_].set_visible(False)
fig.tight_layout()
figure(fig, "fig1_5_1")

# ---------------------------------------------------------------- Fig. 1.5.2: safety factor and probability of failure
fig, ax = plt.subplots(figsize=(6.4, 3.2))
Ss = np.linspace(1.0, 3.0, 300)
for (Cl, Cs), col in (((0.05, 0.05), "#2ca02c"), ((CL, cov_bench), "#2c6fbb"), ((CL, CS_SHOCK), "#c0392b"), ((0.15, 0.30), "#8e44ad")):
    pf = [max(1 - R_of(S, Cl, Cs), 1e-12) for S in Ss]
    ax.semilogy(Ss, pf, color=col, lw=1.5, label=r"$C_\mathrm{lim}$ = %.2f, $C_\sigma$ = %.2f" % (Cl, Cs))
ax.axhline(1e-6, color="#1d2327", lw=0.7, ls="--")
ax.text(2.98, 1.6e-6, T("百万分之一", "one in a million"), ha="right", fontsize=7.5)
ax.plot([S_mu], [max(1 - R2, 1e-12)], "o", color="#c0392b", ms=5)
ax.set_ylim(1e-10, 1)
ax.set_xlabel(T(r"平均安全系数 $S = \mu_\mathrm{lim} / \mu_\sigma$", r"mean safety factor $S = \mu_\mathrm{lim} / \mu_\sigma$"))
ax.set_ylabel(T("失效概率 1 − R", "probability of failure 1 − R"))
ax.legend(fontsize=7.5, frameon=False)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)
fig.tight_layout()
figure(fig, "fig1_5_2")

out(S_nom=S_nom, K_max=E.K_PEAK, k_mean=k_mean, cov_bench=cov_bench, n_peaks=len(peaks), S_mu=S_mu, CL=CL, CS_shock=CS_SHOCK,
    z1=z_of(S_mu, CL, cov_bench), pf1=1 - R1, z2=z_of(S_mu, CL, CS_SHOCK), pf2=1 - R2, pf2_per1000=(1 - R2) * 1000,
    S_req1=S_req1, S_req2=S_req2, z_req=float(norm.ppf(R_req)))
