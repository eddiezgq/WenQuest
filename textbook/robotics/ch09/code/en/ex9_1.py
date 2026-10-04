"""Examples 9.1.1-9.1.3: quantization error of an encoder, statistics of the readings of a gripper force sensor,
averaging several readings; Bessel's formula and the central limit theorem.

9.1.2 A force sensor carries a constant clamping force of 15 N and is sampled at 1 kHz for 2 s, 2,000 readings in all;
      the noise is Gaussian with a standard deviation of 0.08 N (generated with a fixed seed). Find the sample mean and
      the sample standard deviation, count the shares within ±1, ±2, ±3 standard deviations, and compare them with the
      theoretical values of the Gaussian distribution.
9.1.1 An encoder with 4,096 counts per revolution: the quantization error is uniform in ±q/2, with standard deviation
      q/√12 (Eq. (9.1.11)), checked by Monte Carlo.
9.1.3 Averaging every 16 readings: the standard deviation of the average is σ/4 (Theorem 9.1.4), checked by Monte Carlo.
Theorem 9.1.5: with 5 readings per group, the sample variance divided by n − 1 is unbiased and divided by n is too
small, checked by Monte Carlo.
Also: the sum of 12 uniform random numbers (central limit theorem); its share within ±1 standard deviation of the mean
is close to the value of the Gaussian distribution.
"""
import math

import numpy as np

from _prob import p_within
from bookout import out

rng = np.random.default_rng(901)

# ---------------------------------------------------------------- Example 9.1.2
F0, sig, n = 15.0, 0.08, 2000
x = F0 + sig * rng.standard_normal(n)
mean = x.mean()
s = x.std(ddof=1)
frac = [np.mean(np.abs(x - mean) < k * s) for k in (1, 2, 3)]
theory = [p_within(k) for k in (1, 2, 3)]
assert abs(mean - F0) < 4 * sig / math.sqrt(n)                     # the mean lies within the theoretical range
assert abs(s - sig) / sig < 0.05
assert all(abs(f - t) < 0.02 for f, t in zip(frac, theory))
# two ways agree: the definition term by term and the form E[X²] − (E[X])²
var_def = np.sum((x - mean) ** 2) / (n - 1)
var_alt = (np.sum(x ** 2) - n * mean ** 2) / (n - 1)
assert abs(var_def - var_alt) < 1e-9

# probabilities of ±1, ±2, ±3 σ for the Gaussian, two ways: error function and numerical integration
zz = np.linspace(-3, 3, 600001)
dens = np.exp(-zz ** 2 / 2) / math.sqrt(2 * math.pi)
for k in (1, 2, 3):
    m = np.abs(zz) <= k
    assert abs(np.trapezoid(dens[m], zz[m]) - p_within(k)) < 1e-6
k95 = 1.959963984540054                                          # the k with Pr(|Z| < k) = 0.95
assert abs(p_within(k95) - 0.95) < 1e-12
# Gaussian integral ∫ e^{−x²/2} dx = √(2π): checked by numerical integration
xx = np.linspace(-12, 12, 400001)
gint = np.trapezoid(np.exp(-xx ** 2 / 2), xx)
assert abs(gint - math.sqrt(2 * math.pi)) < 1e-9

# ---------------------------------------------------------------- Example 9.1.1 encoder quantization
counts = 4096
q_deg = 360.0 / counts
sig_q = q_deg / math.sqrt(12)
ang = rng.uniform(0, 360, 200000)
err = np.round(ang / q_deg) * q_deg - ang
sig_q_mc = err.std()
assert np.all(np.abs(err) <= q_deg / 2 + 1e-12)
assert abs(sig_q_mc - sig_q) / sig_q < 0.01

# ---------------------------------------------------------------- Example 9.1.3 averaging 16 readings
N16 = 16
groups = F0 + sig * rng.standard_normal((20000, N16))
avg = groups.mean(axis=1)
sig_avg = sig / math.sqrt(N16)
sig_avg_mc = avg.std(ddof=1)
assert abs(sig_avg_mc - sig_avg) / sig_avg < 0.02

# ---------------------------------------------------------------- Theorem 9.1.5 Bessel's formula
n5 = 5
g5 = sig * rng.standard_normal((200000, n5))
s2_unb = g5.var(axis=1, ddof=1).mean()
s2_b = g5.var(axis=1, ddof=0).mean()
assert abs(s2_unb / sig ** 2 - 1) < 0.01
assert abs(s2_b / sig ** 2 - (n5 - 1) / n5) < 0.01

# ---------------------------------------------------------------- central limit theorem: sum of 12 uniform random numbers
u12 = rng.uniform(0, 1, (200000, 12)).sum(axis=1) - 6.0
clt_var = u12.var()
clt_p1 = np.mean(np.abs(u12) < 1)
assert abs(clt_var - 1) < 0.01 and abs(clt_p1 - p_within(1)) < 0.01

# a die: expectation and variance (discrete random variable)
die = np.arange(1, 7)
die_mean = die.mean()
die_var = np.mean((die - die_mean) ** 2)
assert abs(die_var - 35 / 12) < 1e-12

out(F0=F0, sig=sig, n=n, mean=mean, s=s,
    f1=100 * frac[0], f2=100 * frac[1], f3=100 * frac[2],
    p1=100 * theory[0], p2=100 * theory[1], p3=100 * theory[2], k95=k95,
    out3=int(np.sum(np.abs(x - mean) >= 3 * s)), exp_out3=n * (1 - theory[2]),
    q_deg=q_deg, q_mrad=1000 * math.radians(q_deg), sig_q=sig_q, sig_q_mc=sig_q_mc, sig_q_mrad=1000 * math.radians(sig_q),
    N16=N16, sig_avg=sig_avg, sig_avg_mc=sig_avg_mc,
    s2_unb=s2_unb / sig ** 2, s2_b=s2_b / sig ** 2,
    clt_var=clt_var, clt_p1=100 * clt_p1,
    die_var=die_var, sqrt2pi=math.sqrt(2 * math.pi), gint=gint)
