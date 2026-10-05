"""Section 4.7 Surface roughness: synthesizes a profile of a turned surface (residual left by the tool nose radius + random micro-irregularities + waviness from machine vibration),
separates the roughness profile with a Gaussian filter (ISO 16610-21, λc = 0.8 mm), and calculates Ra and Rz; compares the effects of feed and tool nose radius (Examples 4.7.1, 4.7.2, Figure 4.7.1)."""
import math

import numpy as np

import _ch4 as H
from bookout import T, figure, out, style

DX = 0.0005                    # Sampling interval, mm (0.5 μm)
LC = 0.8                       # Cut-off wavelength λc (the value specified by ISO 21920-3 / GB/T 10610 for surfaces of Ra 0.1-2 μm)
LN = 5 * LC                    # Evaluation length = 5 sampling lengths
ALPHA = math.sqrt(math.log(2) / math.pi)
WAVE = (2.5, 0.0015)           # Waviness left by machine vibration: wavelength 2.5 mm, amplitude 1.5 μm (set by this book)
NOISE = 0.00012                # Random micro-irregularities (tearing of the material, tiny chips in the cutting edge): standard deviation 0.12 μm, correlation length about 10 μm


def profile(f, r, seed=7):
    """Measured profile z(x) of a turned surface (mm), length LN + 2λc (one λc at each end to let the filter "warm up")."""
    L = LN + 2 * LC
    x = np.arange(0, L, DX)
    rng = np.random.default_rng(seed)
    xc = (x + rng.uniform(0, f)) % f - f / 2                        # Distance to the nearest center of the tool nose radius
    z = r - np.sqrt(r * r - xc ** 2)                                 # Residual left by the tool nose radius
    n = rng.normal(0, 1, x.size)
    k = np.exp(-0.5 * (np.arange(-40, 41) * DX / 0.005) ** 2)
    n = np.convolve(n, k / np.sqrt((k ** 2).sum()), mode="same") * NOISE
    w = WAVE[1] * np.sin(2 * math.pi * x / WAVE[0] + 0.7)
    return x, z + n + w


def gauss_mean(z):
    """Mean line by Gaussian filtering (ISO 16610-21): weighting function s(x) = exp(-π (x/(αλc))²)/(αλc)"""
    u = np.arange(-LC, LC + DX / 2, DX)
    s = np.exp(-math.pi * (u / (ALPHA * LC)) ** 2)
    s /= s.sum()
    return np.convolve(z, s, mode="same")


def evaluate(x, z):
    m = gauss_mean(z)
    rr = z - m
    keep = (x >= LC) & (x < LC + LN)
    rr, zz, mm = rr[keep], z[keep], m[keep]
    Ra = np.mean(np.abs(rr))
    n = int(round(LC / DX))
    Rz = np.mean([rr[i * n:(i + 1) * n].max() - rr[i * n:(i + 1) * n].min() for i in range(5)])
    return Ra * 1000, Rz * 1000, x[keep], zz, mm, rr


# Example 4.7.1: finish turning f = 0.2 mm/r, tool nose radius r = 0.8 mm
F1, R1 = 0.2, 0.8
x, z = profile(F1, R1)
Ra1, Rz1, xe, ze, me, re_ = evaluate(x, z)
Rth1 = F1 ** 2 / (8 * R1) * 1000
Rt_raw = (ze.max() - ze.min()) * 1000                     # Unfiltered: the waviness is included too
# Example 4.7.2: feed and tool nose radius
FEEDS = [0.05, 0.08, 0.1, 0.15, 0.2, 0.25, 0.3]
RADII = [0.4, 0.8, 1.2]
tab = {}
for r in RADII:
    for f in FEEDS:
        tab[(f, r)] = evaluate(*profile(f, r))[:2]
Ra_f01_r08 = tab[(0.1, 0.8)][0]
Ra_f005_r08 = tab[(0.05, 0.8)][0]
C_RA = 4 / (9 * math.sqrt(3)) / 8                       # Residual cross-section taken as a parabola z = x²/(2r): Ra = [4/(9√3)]·f²/(8r) ≈ 0.0321 f²/r
Ra_th_f01 = C_RA * 0.1 ** 2 / 0.8 * 1000
# Ratio of Ra to the theoretical residual height with geometric residual only (no noise, no waviness)
x0 = np.arange(0, LN + 2 * LC, DX)
xc0 = x0 % F1 - F1 / 2
z0 = R1 - np.sqrt(R1 * R1 - xc0 ** 2)
ratio = evaluate(x0, z0)[0] / Rth1
# Bearing seat Ra 0.8: can turning achieve it? Maximum feed for Ra ≤ 0.8 (r = 0.8)
f_ok = max((f for f in FEEDS if tab[(f, 0.8)][0] <= 0.8), default=None)

# ---------------------------------------------------------------- Figure
plt = style()
fig = plt.figure(figsize=(7.6, 4.4))
g = fig.add_gridspec(2, 2, width_ratios=[1.55, 1.0], hspace=0.55, wspace=0.28)
a0 = fig.add_subplot(g[0, 0])
a0.plot(xe, ze * 1000, color=H.INK, lw=0.45)
a0.plot(xe, me * 1000, color="#d62728", lw=1.0)
a0.set_ylabel("z / μm", fontsize=7.5)
a0.tick_params(labelsize=6.5)
a0.set_title(T(f"(a) 实测轮廓与高斯中线（f = {F1} mm/r，rε = {R1} mm，λc = {LC} mm）",
               f"(a) Measured profile and Gaussian mean line (f = {F1} mm/rev, rε = {R1} mm, λc = {LC} mm)"), fontsize=7.6)
a1 = fig.add_subplot(g[1, 0])
a1.plot(xe, re_ * 1000, color=H.INK, lw=0.45)
a1.axhline(Ra1, color="#1f77b4", lw=0.8, ls="--")
a1.axhline(-Ra1, color="#1f77b4", lw=0.8, ls="--")
for i in range(1, 5):
    a1.axvline(LC + i * LC, color=H.MUTED, lw=0.5, ls=":")
a1.text(LC + 0.05, Ra1 + 0.35, f"±Ra = ±{Ra1:.2f} μm", fontsize=6.8, color="#1f77b4")
a1.set_xlabel("x / mm", fontsize=7.5)
a1.set_ylabel(T("粗糙度 / μm", "roughness / μm"), fontsize=7.5)
a1.tick_params(labelsize=6.5)
a1.set_title(T(f"(b) 粗糙度轮廓：5 个取样长度，Rz = {Rz1:.2f} μm", f"(b) Roughness profile: 5 sampling lengths, Rz = {Rz1:.2f} μm"), fontsize=7.6)
a2 = fig.add_subplot(g[:, 1])
mk = {0.4: "o", 0.8: "s", 1.2: "^"}
for r in RADII:
    a2.plot(FEEDS, [tab[(f, r)][0] for f in FEEDS], mk[r], ms=3.5, label=f"rε = {r} mm")
    ff = np.linspace(0.04, 0.31, 60)
    a2.plot(ff, C_RA * ff ** 2 / r * 1000, color=H.MUTED, lw=0.6)
a2.axhline(0.8, color="#d62728", lw=0.7, ls="--")
a2.text(0.05, 0.85, "Ra 0.8", fontsize=6.6, color="#d62728")
a2.set_xlabel(T("进给量 f / (mm/r)", "Feed f / (mm/rev)"), fontsize=7.5)
a2.set_ylabel("Ra / μm", fontsize=7.5)
a2.tick_params(labelsize=6.5)
a2.legend(fontsize=6.5, frameon=False)
a2.set_title(T("(c) Ra 随进给量变化\n灰线：只算几何残留", "(c) Ra versus feed\ngrey: geometric cusps only"), fontsize=7.6)
figure(fig, "fig4_7_1")

F_TH = math.sqrt(0.8 * 0.8 / (C_RA * 1000))              # Feed giving a theoretical Ra = 0.8 μm (r = 0.8 mm)
out(f1=F1, f_th=F_TH, c_ra_um=C_RA * 1000, r1=R1, lc=LC, ln=LN, Ra1=Ra1, Rz1=Rz1, Rth1=Rth1, Rt_raw=Rt_raw, wave_l=WAVE[0], wave_a=WAVE[1] * 1000,
    ratio=ratio, Ra_f01=Ra_f01_r08, Ra_th_f01=Ra_th_f01, Ra_f005=Ra_f005_r08, f_ok=f_ok,
    Ra_f03_r04=tab[(0.3, 0.4)][0], Ra_f03_r12=tab[(0.3, 1.2)][0], Rz_Ra=Rz1 / Ra1, c_ra=C_RA, ratio_th=C_RA * 8)
