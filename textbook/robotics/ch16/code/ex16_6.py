"""16.6 节：灵巧性指标。

(1) 条件数与长度单位：平移部分 J_v 的条件数与单位无关；局部条件指标 LCI = 1/κ ∈ [0, 1]。
(2) 定理 16.6.1：平面 2R 臂各向同性的充分必要条件 L1 = √2 L2、θ2 = ±135°；核对；本书的 2R 臂（0.425、0.392 m）
    条件数最小的 θ2 与最小值（黄金分割搜索）。
(3) 特征长度：UR5e 在 θ* 处，κ(diag(I, I/L) J_g) 随 L 的变化，使它最小的 L*；对 2000 组随机关节角，
    使平均局部条件指标最大的 L_g。
(4) 全局条件指标（戈塞林、安赫莱斯 1991）：总长 0.817 m 的平面 2R 臂，GCI 随 λ = L2/L1 的变化，
    最优 λ 与 1/√2 比较；本书 2R 臂的 GCI；工作空间面积元 dA = |det J| dθ1 dθ2。
(5) 算例 16.6.3：UR5e 法兰盘竖直朝下时，在过 θ* 的竖直半平面 (ρ, z) 上，姿态保持的线速度椭球的局部条件指标
    与可操作度的分布；闭式逆解（_jac.ur_down）与第 14 章解析逆解核对；最灵巧处的位置，LCI ≥ 0.5 的区域占可达区域的比例，
    θ* 处的值；工作空间的内、外边界上 LCI → 0。
"""
import math

import numpy as np

from _jac import (D4, H1, H2, L1, L2, TH_STAR, W4, held_ellipsoid, jac_2r, svals, ur_down, ur_fk, ur_ik, ur_jg, ur_jv, ur_labels,
                  wrap)
from bookout import T, out, vec

deg = np.degrees
rng = np.random.default_rng(166)
PHI = (math.sqrt(5) - 1) / 2


def golden(f, a, b, tol=1e-10):
    """黄金分割法求单峰函数 f 在 [a, b] 上的最小点。"""
    c, d = b - PHI * (b - a), a + PHI * (b - a)
    fc, fd = f(c), f(d)
    while b - a > tol:
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - PHI * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + PHI * (b - a)
            fd = f(d)
    return (a + b) / 2


def kap(J):
    s = svals(J)
    return s[0] / s[-1]


# ---------------------------------------------------------------- (1) 单位
Jv = ur_jv(TH_STAR)
k_m, k_mm = kap(Jv), kap(Jv * 1000)
assert abs(k_m - k_mm) < 1e-9

# ---------------------------------------------------------------- (2) 2R 臂的各向同性
Ls = 0.3
k_iso = kap(jac_2r([0.4, math.radians(135)], (math.sqrt(2) * Ls, Ls)))
assert abs(k_iso - 1) < 1e-12
# 任何其他比例都达不到 1：对每个比例，在 θ2 上求最小条件数
k_other = min(kap(jac_2r([0, golden(lambda t: kap(jac_2r([0, t], (1.0, lam))), 0.05, math.pi - 0.05)], (1.0, lam)))
              for lam in (0.5, 0.6, 0.8, 1.0))
assert k_other > 1.01
t2_best = golden(lambda t: kap(jac_2r([0, t], (0.425, 0.392))), 0.05, math.pi - 0.05)
k_best2 = kap(jac_2r([0, t2_best], (0.425, 0.392)))
# 条件数最小的肘角在 90° 与 180° 之间（各向同性时为 135°）
assert math.pi / 2 < t2_best < math.pi

# ---------------------------------------------------------------- (3) 特征长度
Jg = ur_jg(TH_STAR)


def kL(J, L):
    return kap(np.diag([1, 1, 1, 1 / L, 1 / L, 1 / L]) @ J)


Lstar = golden(lambda L: kL(Jg, L), 0.05, 3.0)
k_Lstar = kL(Jg, Lstar)
k_L1m = kL(Jg, 1.0)
# 2000 组随机关节角：平均 LCI 最大的 L
Q = rng.uniform(-math.pi, math.pi, (2000, 6))
Js = np.array([ur_jg(q) for q in Q])


def mean_lci(L):
    D = np.diag([1, 1, 1, 1 / L, 1 / L, 1 / L])
    s = np.linalg.svd(D @ Js, compute_uv=False)
    return float(np.mean(s[:, -1] / s[:, 0]))


Lg = golden(lambda L: -mean_lci(L), 0.05, 3.0, tol=1e-6)
lci_g = mean_lci(Lg)
lci_g1 = mean_lci(1.0)
lci_g01 = mean_lci(0.1)
assert lci_g > lci_g1 and lci_g > lci_g01

# ---------------------------------------------------------------- (4) 全局条件指标
def gci(l1, l2, n=4001):
    """GCI = ∫ (1/κ) dA / ∫ dA，dA = |det J| dθ1 dθ2 = l1 l2 |sin θ2| dθ1 dθ2；θ1 不影响 κ，积分只对 θ2（辛普森法）。"""
    t = np.linspace(0, math.pi, n)
    c, s = np.cos(t), np.sin(t)
    # 2R 臂的 Jᵀ J = [[l1² + l2² + 2 l1 l2 c, l2² + l1 l2 c], [l2² + l1 l2 c, l2²]]
    a, b, d = l1 * l1 + l2 * l2 + 2 * l1 * l2 * c, l2 * l2 + l1 * l2 * c, l2 * l2
    tr, det = a + d, a * d - b * b
    disc = np.sqrt(np.maximum(tr * tr / 4 - det, 0))
    lmax, lmin = tr / 2 + disc, np.maximum(tr / 2 - disc, 0)
    lci = np.sqrt(lmin / lmax)
    wgt = l1 * l2 * np.abs(s)
    h = t[1] - t[0]
    simp = lambda y: h / 3 * (y[0] + y[-1] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum())
    return float(simp(lci * wgt) / simp(wgt))


TOT = 0.817
lam_star = golden(lambda lam: -gci(TOT / (1 + lam), TOT * lam / (1 + lam)), 0.2, 2.0, tol=1e-9)
gci_star = gci(TOT / (1 + lam_star), TOT * lam_star / (1 + lam_star))
gci_ours = gci(0.425, 0.392)
gci_eq = gci(TOT / 2, TOT / 2)
d_lam = abs(lam_star - 1 / math.sqrt(2))
assert d_lam < 1e-4
# 与逐点数值求 κ 的结果核对
tt = np.linspace(1e-3, math.pi - 1e-3, 2001)
chk = np.trapezoid([1 / kap(jac_2r([0, x], (0.425, 0.392))) * abs(math.sin(x)) for x in tt], tt) / np.trapezoid(np.abs(np.sin(tt)), tt)
assert abs(chk - gci_ours) < 1e-5

# 定理 16.6.2：κ + 1/κ = (g(λ) + 2cos θ2)/sin θ2，g(λ) = 1/λ + 2λ ≥ 2√2（λ = 1/√2 时取等号）
#   推论：(i) 对每个 θ2，LCI(λ, θ2) ≤ LCI(1/√2, θ2)；(ii) LCI(λ, θ2) = LCI(1/(2λ), θ2)；
#        (iii) 固定 λ，条件数最小的肘角满足 cos θ2 = −2/g(λ)，最小值满足 κ + 1/κ = √(g² − 4)
gfun = lambda lam: 1 / lam + 2 * lam
e_x, worst_pt = 0.0, -1.0
for _ in range(2000):
    lam, t = rng.uniform(0.1, 3.0), rng.uniform(0.02, math.pi - 0.02)
    k = kap(jac_2r([0.0, t], (1.0, lam)))
    e_x = max(e_x, abs((k + 1 / k) - (gfun(lam) + 2 * math.cos(t)) / math.sin(t)))
    k_iso_t = kap(jac_2r([0.0, t], (1.0, 1 / math.sqrt(2))))
    worst_pt = max(worst_pt, 1 / k - 1 / k_iso_t)                 # 应 ≤ 0
    k_mirror = kap(jac_2r([0.0, t], (1.0, 1 / (2 * lam))))
    e_x = max(e_x, abs(k - k_mirror))
assert e_x < 1e-9 and worst_pt < 1e-12
lam0 = 0.392 / 0.425
t2_formula = math.acos(-2 / gfun(lam0))
assert abs(t2_formula - t2_best) < 1e-6
x0 = math.sqrt(gfun(lam0) ** 2 - 4)
assert abs((k_best2 + 1 / k_best2) - x0) < 1e-9
assert abs(gci(1.0, 0.5) - gci(1.0, 1.0)) < 1e-9 and abs(gci(1.0, 0.3) - gci(1.0, 1 / 0.6)) < 1e-9   # GCI(λ) = GCI(1/(2λ))


# ---------------------------------------------------------------- (5) UR5e 的灵巧性地图
p0 = ur_fk(TH_STAR)[:3, 3]
az = math.atan2(p0[1], p0[0])
lab0 = ur_labels(TH_STAR)
# 闭式逆解与第 14 章解析逆解核对
e_ik = 0.0
for _ in range(50):
    r, z = rng.uniform(0.2, 0.85), rng.uniform(-0.2, 0.6)
    q = ur_down(r, z)
    if q is None:
        continue
    Td = ur_fk(q)
    e_ik = max(e_ik, float(np.abs(Td[:3, 3] - np.array([r * math.cos(az), r * math.sin(az), z])).max()),
               float(np.abs(Td[:3, :3] - ur_fk(TH_STAR)[:3, :3]).max()))
    sols = [s for s, _ in ur_ik(Td)]
    assert min(max(abs(wrap(a - b)) for a, b in zip(s, q)) for s in sols) < 1e-9
assert e_ik < 1e-12
RH = np.linspace(0.14, 0.95, 82)
ZS = np.linspace(-0.45, 0.95, 141)
LCI = np.full((len(ZS), len(RH)), np.nan)
WH = np.full_like(LCI, np.nan)
for i, z in enumerate(ZS):
    for j, r in enumerate(RH):
        q = ur_down(r, z)
        if q is None:
            continue
        a, _ = held_ellipsoid(q)
        LCI[i, j] = a[-1] / a[0]
        WH[i, j] = np.prod(a)
ok = ~np.isnan(LCI)
imax = np.unravel_index(np.nanargmax(LCI), LCI.shape)
lci_max, r_best, z_best = float(LCI[imax]), float(RH[imax[1]]), float(ZS[imax[0]])
frac05 = float(np.mean(LCI[ok] >= 0.5))
a_star, _ = held_ellipsoid(TH_STAR)
lci_star = float(a_star[-1] / a_star[0])
# 外边界（肘部伸直）附近 LCI → 0
q_edge = None
for r in np.linspace(0.6, 1.0, 4001):
    q = ur_down(r, float(p0[2]))
    if q is None:
        break
    q_edge = q
a_e, _ = held_ellipsoid(q_edge)
lci_edge = float(a_e[-1] / a_e[0])
assert lci_edge < 0.05 and lci_max > 0.7

# 生活中的例子：人的上臂 0.30 m、前臂到手 0.32 m
h_t2 = golden(lambda t: kap(jac_2r([0, t], (0.30, 0.32))), 0.05, math.pi - 0.05)
h_lci = 1 / kap(jac_2r([0, h_t2], (0.30, 0.32)))
assert abs(h_t2 - math.acos(-2 / gfun(0.32 / 0.30))) < 1e-6        # 与定理 16.6.2 (iii) 一致
out(h_t2=float(deg(h_t2)), h_in=float(180 - deg(h_t2)), h_lci=h_lci, e_x=e_x)
out(k_m=k_m, k_iso=k_iso, t2_best=float(deg(t2_best)), k_best2=k_best2,
    Lstar=Lstar, k_Lstar=k_Lstar, k_L1m=k_L1m, Lg=Lg, lci_g=lci_g, lci_g1=lci_g1, lci_g01=lci_g01,
    lam_star=lam_star, gci_star=gci_star, gci_ours=gci_ours, gci_eq=gci_eq, d_lam=d_lam, l1_star=TOT / (1 + lam_star),
    e_ik=e_ik, lci_max=lci_max, r_best=r_best, z_best=z_best, frac05=frac05 * 100, lci_star=lci_star, lci_edge=lci_edge,
    t3_best=float(deg(ur_down(r_best, z_best)[2])))
