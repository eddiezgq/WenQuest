"""8.7 厚壁圆筒与过盈配合的应力：GR-302 装在 SH-301 B 版的 Ø40 齿轮位上，配合 H7/r6（第 33 章）。
极限偏差取本书标准表（ISO 286），轮毂外径 Ø64（第 33 章 GR-302 B 版的毂），轴和轮毂都是 40Cr 调质（材料库）。
1. 最小、最大过盈下的接触压力（拉梅公式），轮毂内壁的周向应力、轴的应力；考虑配合面粗糙度被压平（DIN 7190 的做法：
   有效过盈 = 过盈 − 0.4(Rz轴 + Rz孔)（DIN 7190-1:2017；旧版取 0.8），Rz 取本书设定的磨削轴、精镗孔的典型值）；
2. 一维轴对称有限元核对：沿半径划分单元（平面应力），轴和轮毂各自建模、在配合面加“径向位移差 = 过盈/2”的约束，
   约束力就是接触压力，与拉梅公式比较；
3. 热装：轮毂要加热到多少度才能套上去（装配间隙按 0.001d，本书取值；DIN 7190 的思路）。
强度与可传转矩在第 25 章。算例 8.7.1、8.7.2，图 8.7.1。"""
import math

import numpy as np

import _ch8 as H
import mdstd
from bookout import T, figure, out, style

d = 40.0
D_HUB = 64.0                                      # GR-302 B 版的毂径（第 33 章 _shaft.gear_mass）
ES, EH = H.mat("40Cr-QT"), H.mat("40Cr-QT")     # 轴：SH-301 B 版 40Cr 调质；轮毂：GR-302 40Cr
es_hi, es_lo = mdstd.shaft_dev("r", 6, d)
ES_hi, EI_lo = mdstd.hole_dev("H", 7, d)
dmax = (es_hi - EI_lo) / 1000                    # mm
dmin = (es_lo - ES_hi) / 1000
RZ_S, RZ_H = 3.2, 6.3                            # µm（本书设定）
smooth = 0.4 * (RZ_S + RZ_H) / 1000              # DIN 7190-1:2017
smooth_old = 0.8 * (RZ_S + RZ_H) / 1000          # 旧版 DIN 7190（1988）
deff_min, deff_max = max(dmin - smooth, 0.0), dmax - smooth


def lame_fit(delta):
    p = H.fit_pressure(delta, d, D_HUB, EH["E"], EH["nu"], ES["E"], ES["nu"])
    sr_h, st_h = H.lame(p, 0.0, d / 2, D_HUB / 2, d / 2)
    st_out = H.lame(p, 0.0, d / 2, D_HUB / 2, D_HUB / 2)[1]
    return p, st_h, st_out


# 一维轴对称有限元（平面应力）
def fe_ring(r0, r1, n, E, nu):
    r = np.linspace(r0, r1, n + 1)
    K = np.zeros((n + 1, n + 1))
    Dm = E / (1 - nu * nu) * np.array([[1, nu], [nu, 1]])
    gp, gw = np.array([-1 / math.sqrt(3), 1 / math.sqrt(3)]), np.array([1.0, 1.0])
    for e in range(n):
        ra, rb = r[e], r[e + 1]
        h = rb - ra
        ke = np.zeros((2, 2))
        for xi, w in zip(gp, gw):
            N = np.array([(1 - xi) / 2, (1 + xi) / 2])
            rr = N @ np.array([ra, rb])
            B = np.array([[-1 / h, 1 / h], N / rr])
            ke += B.T @ Dm @ B * 2 * math.pi * rr * w * h / 2
        K[e:e + 2, e:e + 2] += ke
    return r, K, Dm


def fe_fit(delta, n=60):
    rs, Ks, Ds = fe_ring(1e-6, d / 2, n, ES["E"], ES["nu"])
    rh, Kh, Dh = fe_ring(d / 2, D_HUB / 2, n, EH["E"], EH["nu"])
    N = len(rs) + len(rh)
    K = np.zeros((N + 1, N + 1))
    K[:len(rs), :len(rs)] = Ks
    K[len(rs):N, len(rs):N] = Kh
    f = np.zeros(N + 1)
    c = np.zeros(N)
    c[len(rs) - 1], c[len(rs)] = -1.0, 1.0       # u_hub(a) − u_shaft(a) = δ/2
    K[:N, N], K[N, :N] = c, c
    f[N] = delta / 2
    K[0, :] = 0.0
    K[0, 0] = 1.0                                # 轴心：u = 0
    f[0] = 0.0
    x = np.linalg.solve(K, f)
    lam = x[N]
    p = -lam / (2 * math.pi * d / 2)             # 约束力 / 配合面周长 = 接触压力
    uh = x[len(rs):N]
    e_r = (uh[1] - uh[0]) / (rh[1] - rh[0])
    e_t = uh[0] / rh[0]
    st_in = (Dh @ np.array([e_r, e_t]))[1]
    return p, st_in


rows = []
for name, dl in ((T("最小有效过盈", "min effective"), deff_min), (T("最大有效过盈", "max effective"), deff_max)):
    p, st_h, st_o = lame_fit(dl)
    pf, stf = fe_fit(dl)
    rows.append((name, dl, p, st_h, st_o, pf, stf))
ALPHA = H.ALPHA["steel"]
gap = 0.001 * d
dT = (dmax + gap) / (ALPHA * d)

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
p, st_h, st_o = lame_fit(deff_max)
rr = np.linspace(d / 2, D_HUB / 2, 100)
sr, sth = H.lame(p, 0.0, d / 2, D_HUB / 2, rr)
a0.plot(rr, sth, color="#d62728", lw=1.4, label=T("轮毂周向应力 σθ", "hub hoop stress σθ"))
a0.plot(rr, sr, color="#1f77b4", lw=1.4, label=T("轮毂径向应力 σr", "hub radial stress σr"))
a0.plot([0, d / 2], [-p, -p], color="#2ca02c", lw=1.4, label=T("轴：σr = σθ = −p", "shaft: σr = σθ = −p"))
a0.axhline(0, color=H.MUTED, lw=0.5)
a0.axvline(d / 2, color=H.MUTED, lw=0.6, ls=":")
a0.set_xlabel(T("半径 / mm", "Radius / mm"), fontsize=7.2)
a0.set_ylabel(T("应力 / MPa", "Stress / MPa"), fontsize=7.2)
a0.legend(fontsize=6.2, frameon=False, loc="upper right")
a0.tick_params(labelsize=6.3)
a0.set_title(T(f"(a) 最大有效过盈 {deff_max * 1000:.0f} µm 时的应力", f"(a) Stresses at the max effective interference {deff_max * 1000:.0f} µm"), fontsize=7.4)
dl = np.linspace(0, dmax, 60)
a1.plot(dl * 1000, [lame_fit(x)[0] for x in dl], color="#1f77b4", lw=1.4, label=T("拉梅公式", "Lamé"))
a1.plot([r[1] * 1000 for r in rows], [r[5] for r in rows], "s", color="#d62728", ms=5, label=T("一维轴对称有限元", "1D axisymmetric FE"))
for x, lab in ((dmin, T("名义最小", "nominal min")), (dmax, T("名义最大", "nominal max"))):
    a1.axvline(x * 1000, color=H.MUTED, lw=0.6, ls=":")
    a1.text(x * 1000, 2, lab, rotation=90, fontsize=6.0, color=H.MUTED, va="bottom", ha="right")
a1.set_xlabel(T("有效过盈 / µm", "Effective interference / µm"), fontsize=7.2)
a1.set_ylabel(T("接触压力 p / MPa", "Contact pressure p / MPa"), fontsize=7.2)
a1.legend(fontsize=6.2, frameon=False, loc="upper left")
a1.tick_params(labelsize=6.3)
a1.set_title(T(f"(b) Ø{d:.0f} H7/r6 的接触压力", f"(b) Contact pressure of Ø{d:.0f} H7/r6"), fontsize=7.4)
fig.tight_layout()
figure(fig, "fig8_7_1")

o = {}
for k, r in zip(("min", "max"), rows):
    o.update({f"delta_{k}": r[1] * 1000, f"p_{k}": r[2], f"sth_{k}": r[3], f"sto_{k}": r[4], f"pfe_{k}": r[5], f"sthfe_{k}": r[6],
              f"err_{k}": 100 * abs(r[5] - r[2]) / r[2] if r[2] else 0.0})
out(d=d, D_hub=D_HUB, es=es_hi, ei=es_lo, ES=ES_hi, EI=EI_lo, dmin=dmin * 1000, dmax=dmax * 1000, rz_s=RZ_S, rz_h=RZ_H, smooth=smooth * 1000,
    sy_hub=EH["sy"], S_hub=EH["sy"] / rows[1][3], gap=gap * 1000, dT=dT, T_heat=20 + dT, smooth_old=smooth_old * 1000, p_min_old=lame_fit(max(dmin - smooth_old, 0.0))[0], delta_min_old=max(dmin - smooth_old, 0.0) * 1000, alpha=ALPHA * 1e6, **o)
