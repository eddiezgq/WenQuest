"""Examples 9.3.1–9.3.3: Bayes' rule.

9.3.1 Visual inspection in the reducer workshop: defect rate 1%, alarm probability 95% for a defective part, false-alarm
      probability 5% for a good one. Find the probability that a part raising an alarm is really defective, and the same
      when two independent inspection stations both raise an alarm. Checked by simulating one million parts.
9.3.2 Localizing an AGV in an aisle of 20 cells: cells 2, 6, 7 and 15 carry reflective tags; the detector says "tag" with
      probability 0.9 on a tag cell and 0.1 on any other cell.
      Uniform prior; measure "tag" -> move one cell (one cell with probability 0.8, stay put or two cells with 0.1 each)
      -> measure "tag" -> move -> measure "no tag".
      The step-by-step Bayesian computation must agree with the direct computation that enumerates every start and move.
9.3.3 AGV position along the aisle: odometry gives the prior N(5.20, 0.10^2) m; the lidar measures 0.75 m to the tag at
      6.00 m (std 0.03 m). Find the posterior by Theorem 9.3.3 and check it by a numerical Bayesian computation on a grid;
      a second measurement of 0.77 m: sequential updating and a single combined update agree.
"""
import itertools
import math

import numpy as np

from _prob import gauss_pdf
from bookout import out, T

rng = np.random.default_rng(903)

# ---------------------------------------------------------------- Example 9.3.1 visual inspection
pD, sens, fa = 0.01, 0.95, 0.05
p_alarm = sens * pD + fa * (1 - pD)                        # law of total probability (9.3.3)
post1 = sens * pD / p_alarm                                 # Bayes' rule (9.3.5)
p_alarm2 = sens ** 2 * pD + fa ** 2 * (1 - pD)
post2 = sens ** 2 * pD / p_alarm2
post2_seq = sens * post1 / (sens * post1 + fa * (1 - post1))   # first posterior used as the prior
assert abs(post2 - post2_seq) < 1e-12
N = 1_000_000
defect = rng.random(N) < pD
alarm1 = np.where(defect, rng.random(N) < sens, rng.random(N) < fa)
alarm2 = np.where(defect, rng.random(N) < sens, rng.random(N) < fa)
mc1 = defect[alarm1].mean()
mc2 = defect[alarm1 & alarm2].mean()
assert abs(mc1 - post1) < 0.01 and abs(mc2 - post2) < 0.03
# natural frequencies for 1000 parts
n_def = 1000 * pD
n_hit = n_def * sens
n_fa = 1000 * (1 - pD) * fa

# ---------------------------------------------------------------- Example 9.3.2 the AGV in an aisle
ncell = 20
tags = {2, 6, 7, 15}
hit, false = 0.9, 0.1
move = {0: 0.1, 1: 0.8, 2: 0.1}                             # probabilities of moving 0, 1, 2 cells (stops at the last cell)
zs = [1, 1, 0]                                              # three measurements: tag, tag, no tag


def like(z, cell):
    p = hit if cell in tags else false
    return p if z == 1 else 1 - p


def predict(b):
    nb = np.zeros(ncell)
    for i in range(ncell):
        for k, pk in move.items():
            nb[min(i + k, ncell - 1)] += pk * b[i]            # law of total probability (9.3.6)
    return nb


bel = np.full(ncell, 1 / ncell)
steps = [bel.copy()]
for j, z in enumerate(zs):
    bel = np.array([like(z, i) for i in range(ncell)]) * bel
    bel /= bel.sum()                                        # Bayes' rule (9.3.5)
    steps.append(bel.copy())
    if j < len(zs) - 1:
        bel = predict(bel)
        steps.append(bel.copy())
# direct computation: enumerate starts and both moves, joint probability of each "path" by the product rule, summed by end cell
direct = np.zeros(ncell)
for x0 in range(ncell):
    for k1, k2 in itertools.product(move, move):
        x1 = min(x0 + k1, ncell - 1)
        x2 = min(x1 + k2, ncell - 1)
        pr = (1 / ncell) * like(zs[0], x0) * move[k1] * like(zs[1], x1) * move[k2] * like(zs[2], x2)
        direct[x2] += pr
direct /= direct.sum()
assert np.allclose(direct, bel, atol=1e-14)
after1 = steps[1]
p_tags1 = sum(after1[i] for i in tags)
best = int(np.argmax(bel))
assert best == 8

# ---------------------------------------------------------------- Example 9.3.3 Gaussian prior and Gaussian measurement
mu0, s0 = 5.20, 0.10
lm, dz, sz = 6.00, 0.75, 0.03
z1 = lm - dz
K = s0 ** 2 / (s0 ** 2 + sz ** 2)
mu1 = mu0 + K * (z1 - mu0)
var1 = 1 / (1 / s0 ** 2 + 1 / sz ** 2)
s1 = math.sqrt(var1)
assert abs(mu1 - (sz ** 2 * mu0 + s0 ** 2 * z1) / (s0 ** 2 + sz ** 2)) < 1e-12
assert abs(var1 - (1 - K) * s0 ** 2) < 1e-15
# numerical Bayes on a grid: posterior ∝ likelihood × prior
x = np.linspace(4.5, 6.0, 300001)
post = gauss_pdf(x, mu0, s0) * gauss_pdf(z1, x, sz)
post /= np.trapezoid(post, x)
mu_g = np.trapezoid(x * post, x)
s_g = math.sqrt(np.trapezoid((x - mu_g) ** 2 * post, x))
assert abs(mu_g - mu1) < 1e-8 and abs(s_g - s1) < 1e-8
# second measurement: sequential updating = one combined update
dz2 = 0.77
z2 = lm - dz2
K2 = var1 / (var1 + sz ** 2)
mu2 = mu1 + K2 * (z2 - mu1)
var2 = (1 - K2) * var1
var_b = 1 / (1 / s0 ** 2 + 2 / sz ** 2)
mu_b = var_b * (mu0 / s0 ** 2 + (z1 + z2) / sz ** 2)
assert abs(mu2 - mu_b) < 1e-12 and abs(var2 - var_b) < 1e-15

out(
    pD=100 * pD, sens=100 * sens, fa=100 * fa, p_alarm=100 * p_alarm, post1=100 * post1, post2=100 * post2,
    mc1=100 * mc1, mc2=100 * mc2, n_def=n_def, n_hit=n_hit, n_fa=n_fa, N=N,
    ncell=ncell, tags=T("第 2、6、7、15 格", "cells 2, 6, 7 and 15"), p_tag1=after1[2], p_other1=after1[0], p_tags1=100 * p_tags1,
    best=best, p_best=bel[best], p_second=float(np.sort(bel)[-2]),
    bel_final=", ".join(f"{v:.3f}" for v in bel[5:12]),
    mu0=mu0, s0=s0, z1=z1, K=K, mu1=mu1, s1=s1, s1_mm=1000 * s1, mu_g=mu_g, s_g=s_g,
    z2=z2, K2=K2, mu2=mu2, s2=math.sqrt(var2), s2_mm=1000 * math.sqrt(var2),
    w_prior=100 * (1 - K), w_meas=100 * K,
)
