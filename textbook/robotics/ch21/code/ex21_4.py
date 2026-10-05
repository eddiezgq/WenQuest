"""21.4 节的计算：微分平坦与过航点的轨迹。

算例 21.4.1  “8”字形轨迹上某一时刻（示意值）：由平坦输出及其导数求 R、f、ω_b、ω̇_b（式 (21.4.2)～(21.4.4)），
             与差商核对（ω_b 由对数映射，ω̇_b 由 ω_b 的中心差商）。
算例 21.4.2  数字工厂巡检：7 个航点（示意值）。最小 snap 样条（定理 21.4.2 的线性方程组）；
             总时间不变时优化各段时间的分配；按倾角 ≤ 30°、总推力 ≤ 39 N、物体角速度 ≤ 2 rad/s（示意值）求最短总时间（时间缩放）。
算例 21.4.3  同一组航点与时间分配下，最小加速度（k = 2）、最小加加速度（k = 3）、最小 snap（k = 4）三种轨迹的比较：
             航点处 ω_b、ω̇_b 是否连续（k = 2 时 ω_b 跳变；k = 3、4 时两者都连续），角速度、角加速度与倾角的最大值。
算例 21.4.4  把最小 snap 轨迹算出的 f(t)、ω_b(t) 代回运动方程 (21.2.1) 与 Ṙ = R[ω_b] 积分（李-中点法，步长 1 ms），
             核对积分出的位置与样条一致。
"""
import math

import numpy as np
from scipy.optimize import minimize

from _uav import EZ, G, expso3, flat, logso3, min_deriv_spline, spline_eval, spline_eval_seg, x2
from bookout import out, tex

P = x2()
m = P["m"]

# ---------------------------------------------------------------- 算例 21.4.1
Ax, Ay, w8, h8, k_psi = 2.0, 1.0, 0.8, 1.5, 0.3


def fig8(t):
    """p(t) = (A_x sin ωt, A_y sin 2ωt, 1.5) 及其 1～4 阶导数；ψ(t) = k t。"""
    out_ = []
    for r in range(5):
        dx = Ax * w8 ** r * math.sin(w8 * t + r * math.pi / 2)
        dy = Ay * (2 * w8) ** r * math.sin(2 * w8 * t + r * math.pi / 2)
        dz = h8 if r == 0 else 0.0
        out_.append(np.array([dx, dy, dz]))
    return out_


t1 = 1.3
F1 = flat(fig8(t1), k_psi * t1, k_psi, 0.0, m)
hh = 1e-5
Fp = flat(fig8(t1 + hh), k_psi * (t1 + hh), k_psi, 0.0, m)
Fm = flat(fig8(t1 - hh), k_psi * (t1 - hh), k_psi, 0.0, m)
w_fd = logso3(Fm["R"].T @ Fp["R"]) / (2 * hh)
dw_fd = (Fp["w"] - Fm["w"]) / (2 * hh)
assert np.allclose(w_fd, F1["w"], atol=1e-8)
assert np.allclose(dw_fd, F1["dw"], atol=1e-6)
err_w = np.max(np.abs(w_fd - F1["w"]))
err_dw = np.max(np.abs(dw_fd - F1["dw"]))
# ω_z 的公式 (21.4.4) 与 W 矩阵的第三行一致
th1, ph1 = F1["th"], F1["phi"]
assert abs(F1["w"][2] - (math.cos(th1) * k_psi - math.sin(ph1) * F1["w"][1]) / math.cos(ph1)) < 1e-12

# ---------------------------------------------------------------- 算例 21.4.2：数字工厂巡检
# 航点（本章坐标：x 沿车间长边，y = 28 − y_工厂，z 向上；示意值）：起点在左侧主通道上方 1 m，
# 经热处理炉 ht-01 顶部、磨床 grd-01 顶部、检测台 qc-01 顶部，降到第二条主通道上方 1 m。
WP = np.array([(7, 19, 1.0), (12, 19, 3.0), (17, 15, 3.5), (24, 19, 3.0), (31, 15, 3.0), (38, 15, 3.0), (38, 9.5, 1.0)])
NAMES = ["W0", "W1", "W2", "W3", "W4", "W5", "W6"]
dseg = np.linalg.norm(np.diff(WP, axis=0), axis=1)
L_poly = dseg.sum()
K4 = 4
TILT_MAX, F_MAX, W_MAX = math.radians(30), 39.0, 2.0     # 示意值：倾角、总推力（4 × 13 N 的 75%）、物体角速度


def gauss_cost(C, Ts, k):
    """∫‖p⁽ᵏ⁾‖² dt：每段 12 点高斯-勒让德积分（被积函数是次数不超过 2(2k−1−k) 的多项式，结果精确）。"""
    xs, ws = np.polynomial.legendre.leggauss(12)
    tot = 0.0
    for j in range(len(Ts)):
        for x, w in zip(xs, ws):
            tot += w * Ts[j] / 2 * np.sum(spline_eval_seg(C, Ts, j, (x + 1) / 2 * Ts[j], k) ** 2)
    return tot


def alloc_opt(Ttot, k):
    """总时间 Ttot 不变，优化各段时间的比例使 ∫‖p⁽ᵏ⁾‖² 最小（Richter 等，2016）。"""
    def J(z):
        Ts = Ttot * np.exp(z) / np.exp(z).sum()
        C, _ = min_deriv_spline(WP, Ts, k)
        return gauss_cost(C, Ts, k)
    z0 = np.log(dseg / dseg.sum())
    r = minimize(J, z0, method="Nelder-Mead", options=dict(maxiter=6000, xatol=1e-7, fatol=1e-10))
    Ts = Ttot * np.exp(r.x) / np.exp(r.x).sum()
    return Ts, J(z0), r.fun


def sweep(C, Ts, n=4000, psi=0.0):
    """沿轨迹取样：速度、倾角、总推力、角速度、角加速度的最大值。"""
    tt = np.linspace(0, Ts.sum(), n + 1)
    vs, tilts, fs, ws, dws = [], [], [], [], []
    for t in tt:
        D = [spline_eval(C, Ts, t, r) for r in range(5)]
        F = flat(D, psi, 0.0, 0.0, m)
        vs.append(np.linalg.norm(D[1]))
        tilts.append(math.acos(F["zb"][2]))
        fs.append(F["f"])
        ws.append(np.linalg.norm(F["w"]))
        dws.append(np.linalg.norm(F["dw"]))
    return dict(t=tt, v=np.array(vs), tilt=np.array(tilts), f=np.array(fs), w=np.array(ws), dw=np.array(dws))


T_nom = L_poly / 2.0                                   # 名义总时间：平均 2 m/s
Ts_dist = T_nom * dseg / L_poly
Ts_opt, J_dist, J_opt = alloc_opt(T_nom, K4)
ratio = Ts_opt / T_nom
C_d, _ = min_deriv_spline(WP, Ts_dist, K4)
S_d = sweep(C_d, Ts_dist)
C_o, _ = min_deriv_spline(WP, Ts_opt, K4)
S_o = sweep(C_o, Ts_opt)


def feasible(lam):
    Ts = lam * Ts_opt
    C, _ = min_deriv_spline(WP, Ts, K4)
    S = sweep(C, Ts, n=2000)
    return S["tilt"].max() <= TILT_MAX and S["f"].max() <= F_MAX and S["w"].max() <= W_MAX, S


lo, hi = 0.2, 1.0
assert feasible(hi)[0] and not feasible(lo)[0]
for _ in range(40):
    mid = 0.5 * (lo + hi)
    if feasible(mid)[0]:
        hi = mid
    else:
        lo = mid
lam_star = hi
Ts_fast = lam_star * Ts_opt
T_fast = Ts_fast.sum()
C_f, _ = min_deriv_spline(WP, Ts_fast, K4)
S_f = sweep(C_f, Ts_fast)
binding = max(("tilt", S_f["tilt"].max() / TILT_MAX), ("f", S_f["f"].max() / F_MAX), ("w", S_f["w"].max() / W_MAX), key=lambda x: x[1])[0]
# 时间缩放：p_λ(t) = p(t/λ)，加速度缩小 λ² 倍
C_1, _ = min_deriv_spline(WP, Ts_opt, K4)
for tq in (3.3, 11.7):
    a1 = spline_eval(C_1, Ts_opt, tq, 2)
    a2 = spline_eval(C_f, Ts_fast, lam_star * tq, 2)
    assert np.allclose(a2, a1 / lam_star ** 2, atol=1e-9)

# ---------------------------------------------------------------- 算例 21.4.3：k = 2、3、4 的比较（各段时间取优化后的分配）
cmp = {}
tt_wp = np.cumsum(np.r_[0.0, Ts_opt])[1:-1]           # 中间航点的时刻
for k in (2, 3, 4):
    C, _ = min_deriv_spline(WP, Ts_opt, k)
    S = sweep(C, Ts_opt, n=3000)
    jw, jdw = 0.0, 0.0
    for tw in tt_wp:
        e = 1e-9
        Dm = [spline_eval(C, Ts_opt, tw - e, r) for r in range(5)]
        Dp = [spline_eval(C, Ts_opt, tw + e, r) for r in range(5)]
        Fm_, Fp_ = flat(Dm, 0.0, 0.0, 0.0, m), flat(Dp, 0.0, 0.0, 0.0, m)
        jw = max(jw, np.linalg.norm(Fp_["w"] - Fm_["w"]))
        jdw = max(jdw, np.linalg.norm(Fp_["dw"] - Fm_["dw"]))
    w_start = np.linalg.norm(flat([spline_eval(C, Ts_opt, 0.0, r) for r in range(5)], 0.0, 0.0, 0.0, m)["w"])
    cmp[k] = dict(w_start=w_start, jw=jw, jdw=jdw, wmax=S["w"].max(), dwmax=S["dw"].max(), tilt=math.degrees(S["tilt"].max()), cost4=gauss_cost(C, Ts_opt, 4) if k == 4 else None,
                  vmax=S["v"].max())
assert cmp[4]["w_start"] < 1e-9 and cmp[3]["w_start"] > 1e-3
assert cmp[2]["jw"] > 1e-3 and cmp[3]["jw"] < 1e-6 and cmp[3]["jdw"] < 1e-6 and cmp[4]["jdw"] < 1e-6

# ---------------------------------------------------------------- 算例 21.4.4：把 f(t)、ω_b(t) 积分回去
Ttot = T_fast


def fw(t):
    D = [spline_eval(C_f, Ts_fast, min(max(t, 0.0), Ttot), r) for r in range(5)]
    F = flat(D, 0.0, 0.0, 0.0, m)
    return F["f"], F["w"], D[0]


def fly(h):
    """以步长 h 积分：姿态用李-中点法（式 (7.2.15)），平移用辛普森公式。返回 (步数, 终点误差, 全程最大偏离)。"""
    N = int(round(Ttot / h))
    D0 = [spline_eval(C_f, Ts_fast, 0.0, r) for r in range(5)]
    R = flat(D0, 0.0, 0.0, 0.0, m)["R"]
    p, v = WP[0].astype(float).copy(), np.zeros(3)
    dev = 0.0
    f0, _, _ = fw(0.0)
    for i in range(N):
        t = i * h
        fm_, wm_, _ = fw(t + h / 2)
        f1, _, pref = fw(t + h)
        # 平移：p̈ = (f/m) R ẑ − 𝔤ẑ，姿态的中点值 R·exp(h/2 [ω])
        a0 = f0 / m * R[:, 2] - G * EZ
        Rm = R @ expso3(h / 2 * wm_)
        am = fm_ / m * Rm[:, 2] - G * EZ
        R1 = R @ expso3(h * wm_)                        # 李-中点法（式 (7.2.15)）
        a1 = f1 / m * R1[:, 2] - G * EZ
        p = p + h * v + h * h / 6 * (a0 + 2 * am)        # 辛普森：∫∫ a
        v = v + h / 6 * (a0 + 4 * am + a1)
        R = R1
        f0 = f1
        dev = max(dev, np.linalg.norm(p - pref))
    return N, np.linalg.norm(p - WP[-1]), dev


N, end_err, dev = fly(1e-3)
assert end_err < 1e-3 and dev < 1e-3
_, end_err2, dev2 = fly(2e-3)                           # 步长加倍，误差约为 4 倍（二阶方法）
assert 2.5 < dev2 / dev < 6
dev_ratio = dev2 / dev

out(err_w=err_w, err_dw=err_dw, t1=t1,
    R1=tex(F1["R"], 4), f1=F1["f"], w1x=F1["w"][0], w1y=F1["w"][1], w1z=F1["w"][2],
    dw1x=F1["dw"][0], dw1y=F1["dw"][1], dw1z=F1["dw"][2], th1=math.degrees(th1), ph1=math.degrees(ph1), psi1=math.degrees(k_psi * t1),
    L_poly=L_poly, T_nom=T_nom, J_dist=J_dist, J_opt=J_opt, J_ratio=J_dist / J_opt,
    tilt_d=math.degrees(S_d["tilt"].max()), tilt_o=math.degrees(S_o["tilt"].max()), v_d=S_d["v"].max(), v_o=S_o["v"].max(),
    w_d=S_d["w"].max(), w_o=S_o["w"].max(),
    Ts_opt=Ts_opt.tolist(), Ts_dist=Ts_dist.tolist(), ratio=ratio.tolist(),
    T_fast=T_fast, lam=lam_star, binding=binding, tilt_f=math.degrees(S_f["tilt"].max()), f_f=S_f["f"].max(), w_f=S_f["w"].max(),
    v_f=S_f["v"].max(), vmean_f=L_poly / T_fast,
    jw2=cmp[2]["jw"], ws2=cmp[2]["w_start"], ws3=cmp[3]["w_start"], jdw3=cmp[3]["jdw"], dw2=cmp[2]["dwmax"], dw3=cmp[3]["dwmax"], dw4=cmp[4]["dwmax"], w2=cmp[2]["wmax"], w3=cmp[3]["wmax"], w4=cmp[4]["wmax"],
    tilt2=cmp[2]["tilt"], tilt3=cmp[3]["tilt"], tilt4=cmp[4]["tilt"], v2=cmp[2]["vmax"], v3=cmp[3]["vmax"], v4=cmp[4]["vmax"],
    end_err_mm=end_err * 1000, dev_mm=dev * 1000, N=N, dev2_mm=dev2 * 1000, dev_ratio=dev_ratio)
out(**{f"ts{i}": float(x) for i, x in enumerate(Ts_opt)}, **{f"td{i}": float(x) for i, x in enumerate(Ts_dist)},
    **{f"tf{i}": float(x) for i, x in enumerate(Ts_fast)})
