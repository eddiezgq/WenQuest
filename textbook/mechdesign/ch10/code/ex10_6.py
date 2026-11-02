"""10.7 统计观点：用数字孪生现场一年的数据算可靠度。

算例 10.7.1  WQR-105 输出轴外伸段（Ø30，传扭）在矿山现场（第 7 章 site_year：数字孪生的客户现场模拟器，一年 365 天的日最大转矩）。
            线弹性：等效应力与转矩成正比，σ_eq = √3 · 16T/(πd³)（静强度，塑性材料不计应力集中，10.4 节；键槽处的净截面略去）。
            强度取正态分布：材料库的屈服强度当作 5% 分位的下限值，变异系数 7%（手册典型值，本书取值）。
            一根轴的强度是一个固定的数，一年里坏不坏只看这一年的最大应力 S_max 是否超过它：P_f = ∫ F_R(s) dF_Smax(s)。
            S_max 的分布按“各天独立”由日最大应力的分布求：F_Smax = F_day^365。F_day 两种取法：(1) 365 个日最大值的经验分布；
            (2) 同均值、同标准差的正态分布。比较两者，并看强度的变异系数从 7% 降到 4% 时失效概率怎样变；A 版（45 钢调质）与 B 版
            （40Cr 调质，第 33.8 节）各算一次；
图 10.7.1。
"""
import math

import numpy as np
from scipy.stats import norm

import _ch10 as H
import _ch7 as C7
from bookout import T, figure, out, style

D = 30.0
COV = 0.07
Tday = np.array([d["torque_max_nm"] for d in C7.site_year("mine")])
c = math.sqrt(3) * 16 / (math.pi * D ** 3) * 1e3          # MPa / (N·m)
s = Tday * c
mu_s, sd_s = float(s.mean()), float(s.std(ddof=1))


N_DAY = len(s)
xs_int = np.linspace(s.min() - 6 * sd_s, max(s.max(), 700.0) + 6 * sd_s, 20001)


def p_fail(mid, cov=COV):
    sy = H.mat(mid)["yield_mpa"]
    mu_r = sy / (1 - 1.645 * cov)
    sd_r = cov * mu_r
    FR = lambda x: norm.cdf((x - mu_r) / sd_r)                                  # noqa: E731
    # (1) 经验分布：S_max 只能取观测到的值，P(S_max ≤ s_(k)) = (k / n)^365
    ss_ = np.sort(s)
    Fk = (np.arange(1, N_DAY + 1) / N_DAY) ** N_DAY
    dF = np.diff(np.concatenate([[0.0], Fk]))
    P_emp = float(np.sum(dF * FR(ss_)))
    # (2) 正态分布：F_Smax = Φ((x − μ)/σ)^365，数值积分
    Fn = norm.cdf((xs_int - mu_s) / sd_s) ** N_DAY
    P_norm = float(np.sum(np.diff(Fn) * FR(0.5 * (xs_int[1:] + xs_int[:-1]))))
    return sy, mu_r, sd_r, P_emp, P_norm


def reliability(mid):
    sy, mu_r, sd_r, P_emp, P_norm = p_fail(mid)
    _, _, _, P4e, P4n = p_fail(mid, 0.04)
    return sy, mu_r, sd_r, P_emp, P_norm, P4e, P4n, mu_r / mu_s


A = reliability("45-QT")
B = reliability("40Cr-QT")
q99, smax = float(np.percentile(s, 99)), float(s.max())
z_tail = (smax - mu_s) / sd_s                              # 一年最大值离平均值几个标准差
p_tail_norm = 1 - norm.cdf(z_tail)
gap = 0.5 * (np.sort(s)[:-1] + np.sort(s)[1:])[np.argmax(np.diff(np.sort(s)))]     # 两堆之间最大的空档
n_jam = int(np.sum(s > gap))
jam_lo, jam_hi = float(s[s > gap].min()), float(s[s > gap].max())
# 正态分布给出的一年最大值的中位数（F_Smax = 0.5）
smax_norm_med = mu_s + sd_s * norm.ppf(0.5 ** (1 / N_DAY))

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
bins = np.linspace(s.min() * 0.95, s.max() * 1.02, 40)
a0.hist(s, bins=bins, density=True, color="#1f77b4", alpha=0.75, label=T("日最大应力（现场一年）", "daily max stress (one year on site)"))
xs = np.linspace(bins[0], B[1] + 3.5 * B[2], 600)
a0.plot(xs, norm.pdf(xs, mu_s, sd_s), color="#1f77b4", lw=1.0, ls="--", label=T("同均值、同标准差的正态分布", "normal, same mean and SD"))
a0.plot(xs, norm.pdf(xs, A[1], A[2]), color="#d62728", lw=1.3, label=T("A 版 45 钢的强度", "strength, A (1045)"))
a0.plot(xs, norm.pdf(xs, B[1], B[2]), color="#2ca02c", lw=1.3, label=T("B 版 40Cr 的强度", "strength, B (40Cr)"))
a0.set_xlabel(T("应力 / 强度 / MPa", "Stress / strength / MPa"), fontsize=7.0)
a0.set_ylabel(T("概率密度", "Probability density"), fontsize=7.0)
a0.legend(fontsize=5.7, frameon=False, loc="upper right")
a0.tick_params(labelsize=6.2)
a0.set_title(T("(a) 应力—强度干涉（矿山现场，外伸段 Ø30）", "(a) Stress–strength interference (mine, Ø30 extension)"), fontsize=7.0)
ss = np.sort(s)
a1.step(ss, (np.arange(1, N_DAY + 1) / N_DAY) ** N_DAY, where="post", color="#1f77b4", lw=1.3, label=T("由实际的 365 天", "from the actual 365 days"))
xx = np.linspace(ss[-1] - 40, A[0] + 10, 400)
a1.plot(xx, norm.cdf((xx - mu_s) / sd_s) ** N_DAY, color="#1f77b4", lw=1.0, ls="--", label=T("由正态分布", "from the normal"))
a1.axvline(A[0], color="#d62728", lw=0.8, ls=":")
a1.text(A[0] - 1, 0.5, T("A 版屈服强度（下限）", "A yield (min)"), fontsize=6.0, color="#d62728", ha="right", rotation=90)
a1.set_xlim(ss[-1] - 40, A[0] + 10)
a1.set_xlabel(T("一年里的最大应力 S_max / MPa", "Annual max stress S_max / MPa"), fontsize=7.0)
a1.set_ylabel(T("累积概率", "Cumulative probability"), fontsize=7.0)
a1.legend(fontsize=6.0, frameon=False, loc="center left")
a1.tick_params(labelsize=6.2)
a1.set_title(T("(b) 一年里最大应力的分布", "(b) Distribution of the annual maximum"), fontsize=7.0)
fig.tight_layout()
figure(fig, "fig10_7_1")

out(D=D, cov=COV * 100, T_mean=float(Tday.mean()), T_max=float(Tday.max()), T_p99=float(np.percentile(Tday, 99)), c=c,
    mu_s=mu_s, sd_s=sd_s, s_max=smax, s_p99=q99, z_tail=z_tail, p_tail_norm=p_tail_norm,
    n_day=N_DAY, n_jam=n_jam, jam_pct=n_jam / N_DAY * 100, jam_lo=jam_lo, jam_hi=jam_hi, smax_norm_med=smax_norm_med,
    syA=A[0], muA=A[1], PA_emp=A[3], PA_norm=A[4], PA4_emp=A[5], PA4_norm=A[6], nA=A[7], rA=A[3] / A[4], r4A=A[3] / A[5],
    syB=B[0], muB=B[1], PB_emp=B[3], PB_norm=B[4], nB=B[7])
