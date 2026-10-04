"""1.5 安全系数与可靠度：应力—强度干涉（两者都按正态分布），可靠度 R = Φ(z)，z = (S − 1)/√(S²C_lim² + C_σ²)
（算例 1.5.1、1.5.2，图 1.5.1、1.5.2）。载荷的分散取自数字工厂跑合试验台的转矩记录。"""
import math

import numpy as np
from scipy.stats import norm

import _con as E
from bookout import T, figure, out, style
from sim.engine import torque_record          # 数字工厂仿真车间：跑合试验台“工况模拟”的转矩记录


def z_of(S, Cl, Cs):
    return (S - 1) / math.sqrt((S * Cl) ** 2 + Cs ** 2)


def R_of(S, Cl, Cs):
    return float(norm.cdf(z_of(S, Cl, Cs)))


def S_for(R, Cl, Cs):
    """给定可靠度要求的平均安全系数（解二次方程）"""
    z = norm.ppf(R)
    a = 1 - z * z * Cl * Cl
    b, c = -2.0, 1 - z * z * Cs * Cs
    return (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)


# ---- 跑合试验台：30 台减速器、每台 3 次起动的峰值（输送机工况）
peaks = []
for k in range(1, 31):
    r = torque_record("WQR-105-{:05d}".format(k), "WO-TS-1", "WQR-105")
    s = np.array(r["samples_nm"])
    seg = len(s) // 3
    peaks += [s[j * seg:j * seg + 20].max() / r["rated_nm"] for j in range(3)]
peaks = np.array(peaks)
k_mean, cov_bench = float(peaks.mean()), float(peaks.std(ddof=1) / peaks.mean())

# ---- 算例 1.5.1：外伸段（算例 1.4.1 的 Ø30）
S_nom = E.S_pick                                  # 名义安全系数：屈服强度取最小保证值、载荷取最大的一次峰值
S_mu = S_nom * E.K_PEAK / k_mean                  # 载荷取平均峰值（强度仍取最小保证值，偏于安全）
CL = 0.08                                         # 屈服强度的变异系数（钢材常见 0.05–0.10，假设）
CS_SHOCK = 0.25                                   # 冲击大的工作机（搅拌、破碎、偶尔卡死）的峰值变异系数（假设）
R1, R2 = R_of(S_mu, CL, cov_bench), R_of(S_mu, CL, CS_SHOCK)
# ---- 算例 1.5.2：失效概率不超过百万分之一
R_req = 1 - 1e-6
S_req1, S_req2 = S_for(R_req, CL, cov_bench), S_for(R_req, CL, CS_SHOCK)

# ---------------------------------------------------------------- 图 1.5.1：干涉
plt = style()
fig, ax = plt.subplots(figsize=(6.4, 2.9))
x = np.linspace(0, 2.8, 800)
for Cs, ls, lab in ((cov_bench, "-", T("应力（输送机，分散小）", "stress (conveyor, small scatter)")),
                    (CS_SHOCK, "--", T("应力（冲击大的工作机）", "stress (shock-loaded machine)"))):
    ax.plot(x, norm.pdf(x, 1.0, Cs), color="#c0392b", ls=ls, lw=1.4, label=lab)
ax.plot(x, norm.pdf(x, S_mu, CL * S_mu), color="#2c6fbb", lw=1.6, label=T("强度", "strength"))
ax.fill_between(x, 0, np.minimum(norm.pdf(x, 1.0, CS_SHOCK), norm.pdf(x, S_mu, CL * S_mu)), color="#c0392b", alpha=0.25, lw=0)
ymax = 1.9 * norm.pdf(S_mu, S_mu, CL * S_mu)            # 输送机那条很窄很高，画面里截顶
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

# ---------------------------------------------------------------- 图 1.5.2：安全系数与失效概率
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
