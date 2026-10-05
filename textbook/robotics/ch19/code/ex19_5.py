"""19.5 节的计算：里程计。

算例 19.5.1  编码器的分辨率：每转 4096 个计数时，一个计数对应的转角和车轮滚过的距离。
算例 19.5.2  三种更新公式（欧拉、中点、圆弧精确）沿半径 0.5 m 的圆左转 90°，采样周期 10 ms 和 100 ms 时的终点误差；
             用“圆弧精确 = 中点方向 × sinc(Δφ/2)”的关系核对。
算例 19.5.3  系统误差：两轮半径相差 0.1% 时“直行”10 m 的横向偏差与航向偏差；平均半径偏大 0.5% 的距离误差；
             轮距偏大 1% 时原地转一圈的角度误差。指南车的例子（轮距 3 m、两轮相差千分之一、直行 1 km）。
算例 19.5.4  标定：直行 10 m 量横向偏差求两轮半径之比，原地转 10 圈量实际转角求轮距；标定前后沿 4 m 正方形走一圈的终点误差。
算例 19.5.5  随机误差：每个轮子滚过的距离有方差 k|Δs| 的噪声，直行 10 m 后位置与航向的方差：闭式、线性化的方差传播、
             2000 次蒙特卡洛三者比较；要求横向标准差不超过 5 mm 时地标的最大间距。
"""
import math

import numpy as np

from _mob import diff_cart
from bookout import T, out

P = diff_cart()
r, b = P["r"], P["b"]

# ---------------------------------------------------------------- 算例 19.5.1
N_enc = 4096
dth_q = 2 * math.pi / N_enc
ds_q = r * dth_q

# ---------------------------------------------------------------- 算例 19.5.2：三种更新公式


def upd(q, dsR, dsL, bb, method):
    ds, dphi = (dsR + dsL) / 2, (dsR - dsL) / bb
    x, y, f = q
    if method == "euler":
        return np.array([x + ds * math.cos(f), y + ds * math.sin(f), f + dphi])
    if method == "mid":
        return np.array([x + ds * math.cos(f + dphi / 2), y + ds * math.sin(f + dphi / 2), f + dphi])
    if abs(dphi) < 1e-12:                                      # 圆弧精确：式 (19.5.5)
        return np.array([x + ds * math.cos(f), y + ds * math.sin(f), f])
    return np.array([x + ds / dphi * (math.sin(f + dphi) - math.sin(f)), y - ds / dphi * (math.cos(f + dphi) - math.cos(f)), f + dphi])


def lap(Ts, method, Rc=0.5, v=0.5):
    """沿半径 Rc 的圆走四分之一圈（左转 90°），终点与精确值 (Rc, Rc) 之差。"""
    om = v / Rc
    n = int(round(math.pi / 2 / om / Ts))
    Ts = math.pi / 2 / om / n                                  # 让 n 个周期恰好是四分之一圈
    vR, vL = v + om * b / 2, v - om * b / 2
    q = np.zeros(3)
    for _ in range(n):
        q = upd(q, vR * Ts, vL * Ts, b, method)
    return float(math.hypot(q[0] - Rc, q[1] - Rc)), n


errs = {(m, Ts): lap(Ts, m)[0] for m in ("euler", "mid", "exact") for Ts in (0.01, 0.1)}
assert errs[("exact", 0.01)] < 1e-12 and errs[("exact", 0.1)] < 1e-12
# 阶：周期缩小 10 倍，欧拉误差约缩小 10 倍，中点约 100 倍
ratio_euler = errs[("euler", 0.1)] / errs[("euler", 0.01)]
ratio_mid = errs[("mid", 0.1)] / errs[("mid", 0.01)]
assert 8 < ratio_euler < 12 and 80 < ratio_mid < 120
# 圆弧精确 = 中点方向、长度乘以 sinc(Δφ/2)
for dphi in (0.01, 0.1, 0.5, 1.0):
    ds = 0.3
    a = upd(np.zeros(3), ds + dphi * b / 2, ds - dphi * b / 2, b, "exact")
    m = upd(np.zeros(3), ds + dphi * b / 2, ds - dphi * b / 2, b, "mid")
    sinc = math.sin(dphi / 2) / (dphi / 2)
    assert np.allclose(a[:2], sinc * m[:2], atol=1e-12)
sinc01 = math.sin(0.05) / 0.05

# ---------------------------------------------------------------- 算例 19.5.3：系统误差
eps = 0.001                                                    # 两轮半径之差与平均半径之比
D = 10.0
kap = eps / b
head_err = kap * D
y_err = (1 - math.cos(kap * D)) / kap
y_err_approx = kap * D * D / 2


def run_straight(rR, rL, D, bb=b, n=10000):
    """控制器让两轮编码器读数相等（按名义值走直线 D）；真实车按真实半径 rR、rL 和真实轮距 bb 积分。"""
    dth = D / r / n                                            # 每步每个轮子转过的角度（按名义半径算出来的）
    q = np.zeros(3)
    for _ in range(n):
        q = upd(q, rR * dth, rL * dth, bb, "exact")
    return q


qs = run_straight(r * (1 + eps / 2), r * (1 - eps / 2), D)
assert abs(qs[1] - y_err) < 1e-9 and abs(qs[2] - head_err) < 1e-9
eps_m = 0.005
dist_err = eps_m * D
eps_b = 0.01
spin_err_deg = 360 * eps_b                                     # 里程计以为转了 360°(1 + ε_b)
# 指南车：轮距 3 m，两轮周长相差千分之一，直行 1 km
chariot_deg = math.degrees(1e-3 * 1000 / 3.0)

# ---------------------------------------------------------------- 算例 19.5.4：标定
rR_t, rL_t, b_t = 0.05003, 0.04997, 0.2626                    # “真实”参数（实验者不知道）
eps_t = (rR_t - rL_t) / ((rR_t + rL_t) / 2)
# 实验 1：直行 10 m（按名义参数），量得终点的横向偏差和沿原方向的距离（卷尺，读到 1 mm）
q1 = run_straight(rR_t, rL_t, D, b_t)                          # 真车：真实半径、真实轮距
y_meas = round(q1[1], 3)
x_meas = round(q1[0], 3)
# 弦与起始方向的夹角 u 是航向偏转的一半（定理 19.5.1）；由弦长求实际走过的弧长，弧长 / D = 平均半径 / 名义半径
chord = math.hypot(x_meas, y_meas)                             # 起点到终点的直线距离
u = math.atan2(y_meas, x_meas)
arc = chord * u / math.sin(u)
rbar_hat = r * arc / D
# 实验 2：原地转，里程计（名义 r、b）计到 10 圈时停下，量实际转过的角度（读到 0.1°）
odo_turns = 10
dth_spin = odo_turns * 2 * math.pi * b / 2 / r                 # 每个轮子转过的角度（一正一负）
true_angle = (rR_t + rL_t) * dth_spin / b_t                    # 两轮滚过的距离之差 / 真实轮距
meas_deg = round(math.degrees(true_angle), 1)
b_hat = 2 * rbar_hat * dth_spin / math.radians(meas_deg)       # φ_m = 2 r̄ Δθ / b
# 最后由式 (19.5.8) 求两轮半径之差，用标定后的轮距 b̂
eps_hat = 2 * b_hat * y_meas / D ** 2
rR_hat, rL_hat = rbar_hat * (1 + eps_hat / 2), rbar_hat * (1 - eps_hat / 2)
assert abs(eps_hat - eps_t) / eps_t < 0.01 and abs(b_hat - b_t) < 2e-4 and abs(rbar_hat - (rR_t + rL_t) / 2) < 5e-6


def square(side, rR_true, rL_true, b_true, rR_cal, rL_cal, b_cal, sgn=1, n=2000):
    """按标定参数（rR_cal, rL_cal, b_cal）控制：直行 side、原地转 90°（sgn = 1 逆时针，−1 顺时针），重复四次；
    真车按真实参数走。返回终点与起点的距离。"""
    q = np.zeros(3)
    for _ in range(4):
        # 直行：控制器让两轮滚过的距离（按标定半径算）都等于 side
        thR, thL = side / rR_cal, side / rL_cal
        for _ in range(n):
            q = upd(q, rR_true * thR / n, rL_true * thL / n, b_true, "exact")
        ang = sgn * math.pi / 2                                 # 原地转 90°：两轮滚过 ±b_cal·(π/2)/2
        thR, thL = ang * b_cal / 2 / rR_cal, -ang * b_cal / 2 / rL_cal
        for _ in range(n // 4):
            q = upd(q, rR_true * thR / (n // 4), rL_true * thL / (n // 4), b_true, "exact")
    return float(math.hypot(q[0], q[1])), q


sq_ccw0, _ = square(4.0, rR_t, rL_t, b_t, r, r, b, 1)
sq_cw0, _ = square(4.0, rR_t, rL_t, b_t, r, r, b, -1)
sq_ccw1, _ = square(4.0, rR_t, rL_t, b_t, rR_hat, rL_hat, b_hat, 1)
sq_cw1, _ = square(4.0, rR_t, rL_t, b_t, rR_hat, rL_hat, b_hat, -1)
sq_ideal, _ = square(4.0, r, r, b, r, r, b)
assert sq_ideal < 1e-9 and max(sq_ccw1, sq_cw1) < min(sq_ccw0, sq_cw0) / 5

# ---------------------------------------------------------------- 算例 19.5.5：随机误差
k_n = 1e-6                                                     # 每滚过 1 m，距离误差的方差 1e-6 m²（标准差 1 mm）
Dr = 10.0
var_x = k_n * Dr / 2
var_phi = 2 * k_n * Dr / b ** 2
var_y = 2 * k_n * Dr ** 3 / (3 * b ** 2)
cov_yphi = k_n * Dr ** 2 / b ** 2
# 线性化的方差传播：P ← F P Fᵀ + G Σ Gᵀ（中点公式的雅可比）
nst = 1000
ds = Dr / nst
Pm = np.zeros((3, 3))
q = np.zeros(3)
for _ in range(nst):
    dsR = dsL = ds
    dsm, dph = (dsR + dsL) / 2, (dsR - dsL) / b
    a = q[2] + dph / 2
    F = np.array([[1, 0, -dsm * math.sin(a)], [0, 1, dsm * math.cos(a)], [0, 0, 1]])
    G = np.array([[0.5 * math.cos(a) - dsm / (2 * b) * math.sin(a), 0.5 * math.cos(a) + dsm / (2 * b) * math.sin(a)],
                  [0.5 * math.sin(a) + dsm / (2 * b) * math.cos(a), 0.5 * math.sin(a) - dsm / (2 * b) * math.cos(a)],
                  [1 / b, -1 / b]])
    S = np.diag([k_n * abs(dsR), k_n * abs(dsL)])
    Pm = F @ Pm @ F.T + G @ S @ G.T
    q = upd(q, dsR, dsL, b, "mid")
assert abs(Pm[0, 0] / var_x - 1) < 0.01 and abs(Pm[1, 1] / var_y - 1) < 0.01 and abs(Pm[2, 2] / var_phi - 1) < 1e-9
# 蒙特卡洛
rng = np.random.default_rng(1905)
M = 2000
Q = np.zeros((M, 3))
for _ in range(nst):
    nR = rng.normal(0, math.sqrt(k_n * ds), M)
    nL = rng.normal(0, math.sqrt(k_n * ds), M)
    dsR, dsL = ds + nR, ds + nL
    dsm, dph = (dsR + dsL) / 2, (dsR - dsL) / b
    Q[:, 0] += dsm * np.cos(Q[:, 2] + dph / 2)
    Q[:, 1] += dsm * np.sin(Q[:, 2] + dph / 2)
    Q[:, 2] += dph
sd_mc = Q.std(axis=0)
assert abs(sd_mc[1] / math.sqrt(var_y) - 1) < 0.06 and abs(sd_mc[2] / math.sqrt(var_phi) - 1) < 0.06 and abs(sd_mc[0] / math.sqrt(var_x) - 1) < 0.06
inside = float(np.mean(np.einsum("ij,jk,ik->i", Q - Q.mean(0), np.linalg.inv(Pm), Q - Q.mean(0)) <= 7.815))   # χ²(3) 的 95% 分位
# 地标间距：σ_y ≤ 5 mm
sy_req = 0.005
D_land = (3 * b * b * sy_req ** 2 / (2 * k_n)) ** (1 / 3)
assert abs(math.sqrt(2 * k_n * D_land ** 3 / (3 * b * b)) - sy_req) < 1e-12

out(N_enc=N_enc, dth_q=dth_q, ds_q_um=ds_q * 1e6,
    e_eu_10=errs[("euler", 0.01)] * 1000, e_eu_100=errs[("euler", 0.1)] * 1000, e_mid_10=errs[("mid", 0.01)] * 1000,
    e_mid_100=errs[("mid", 0.1)] * 1000, e_ex_100=errs[("exact", 0.1)], ratio_euler=ratio_euler, ratio_mid=ratio_mid, sinc01=sinc01,
    eps_pct=eps * 100, kap=kap, head_err_deg=math.degrees(head_err), y_err=y_err, y_err_approx=y_err_approx,
    eps_m_pct=eps_m * 100, dist_err_cm=dist_err * 100, eps_b_pct=eps_b * 100, spin_err_deg=spin_err_deg, chariot_deg=chariot_deg,
    rR_t=rR_t, rL_t=rL_t, b_t=b_t, eps_t_pct=eps_t * 100, y_meas=y_meas, x_meas=x_meas, eps_hat_pct=eps_hat * 100, rbar_hat=rbar_hat,
    meas_deg=meas_deg, b_hat=b_hat, chord=chord, arc=arc, sq_ccw0=sq_ccw0 * 100, sq_cw0=sq_cw0 * 100, sq_ccw1=sq_ccw1 * 1000, sq_cw1=sq_cw1 * 1000,
    k_n=k_n, Dr=Dr, sx=math.sqrt(var_x) * 1000, sy=math.sqrt(var_y) * 1000, sphi_deg=math.degrees(math.sqrt(var_phi)),
    sy_lin=math.sqrt(Pm[1, 1]) * 1000, sy_mc=sd_mc[1] * 1000, sx_mc=sd_mc[0] * 1000, sphi_mc_deg=math.degrees(sd_mc[2]),
    rho_yphi=cov_yphi / math.sqrt(var_y * var_phi), inside_pct=inside * 100, M=M, D_land=D_land, sy_req_mm=sy_req * 1000)
