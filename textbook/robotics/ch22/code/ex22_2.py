"""22.2 节的计算：梯形与 S 形速度曲线。

(1) 算例 22.2.1：UR5e 从 A 到 B（同算例 22.1.1）。关节 1 的梯形速度曲线（速度 π rad/s、加速度 6 rad/s²）：
    加速、匀速时间与总时间；其余关节同步（同一加速时间、同一总时间，式 (22.2.6)），检查都不超限；与多项式比较。
    逐点积分核对：梯形曲线走过的角度等于 Δθ。另取一个小转角 0.5 rad，速度达不到上限，曲线为三角形。
(2) 定理 22.2.1 的数值核对：随机生成 2000 条满足 |v| ≤ v_max、|a| ≤ a_max、起止静止的分段常加速度运动，
    凡走完 L 的，用时都不少于梯形曲线。
(3) 算例 22.2.3：加加速度上限 60 rad/s³ 的七段 S 形曲线：各段时长、实际达到的速度、总时间。
    核对定理 22.2.2：S 形曲线 = 同一 v′、a 的梯形曲线用宽 t_j = a/j 的盒形窗滑动平均；T = L/v′ + v′/a + a/j；
    v′ 由二次方程 v′²/a + v′a/j = L 求出，与二分法一致。
(4) 算例 22.2.2、22.2.4：残余振动。手臂与轴绕关节 1 的扭转模态（固有频率 8 Hz、阻尼比 0.02，示意值），
    φ'' + 2ζω φ' + ω² φ = −θ̈₁；TCP 的振幅 = r × φ 的振幅，r 为 B 处 TCP 到关节 1 轴线的距离。
    比较梯形、S 形（t_j = 0.1 s 与 t_j = 1/f_n = 0.125 s）、三次、五次的残余振幅；
    无阻尼时核对定理 22.2.3：S 形的残余振幅 = 梯形（同一 v′）的残余振幅 × |sin(π f t_j)/(π f t_j)|。
"""
import math

import numpy as np

from _traj import (AMAX, FN_TOOL, JMAX, VMAX, ZETA_TOOL, accel_breaks, box_filter, cell_joints, fourier_pw, poly_breaks, response_pw,
                   s_cubic, s_quintic, scurve_eval, scurve_plan, sinc_factor, tcp_fk, trap_eval, trap_plan, trap_sync)
from bookout import out
import ex22_1 as E1

deg = np.degrees
thR, thA, thB, thC = cell_joints()
dq = thB - thA
L1 = abs(dq[0])

# ---------------------------------------------------------------- (1) 梯形
P1 = trap_plan(L1, VMAX[0], AMAX[0])
assert P1["tc"] > 0                                     # 能达到 π rad/s
# 各关节单独走的最短时间：关节 1 最慢
Tj = [trap_plan(abs(d), v, a)["T"] for d, v, a in zip(dq, VMAX, AMAX)]
assert int(np.argmax(Tj)) == 0
T_trap = P1["T"]
# 同步：同一 ta、T
sync = [trap_sync(T_trap, P1["ta"], abs(d)) for d in dq]
v_sync = np.array([p["vp"] for p in sync])
a_sync = np.array([p["a"] for p in sync])
assert np.all(v_sync <= VMAX + 1e-12) and np.all(a_sync <= AMAX + 1e-12)
# 积分核对
t = np.linspace(0, T_trap, 200001)
_, v, _ = trap_eval(P1, t)
assert abs(np.trapezoid(v, t) - L1) < 1e-8
save_c = 1 - T_trap / E1.T3
save_q = 1 - T_trap / E1.T5
# 三角形
Ps = trap_plan(0.5, VMAX[0], AMAX[0])
assert Ps["tc"] == 0 and abs(Ps["T"] - 2 * math.sqrt(0.5 / 6)) < 1e-12

# ---------------------------------------------------------------- (2) 定理 22.2.1 的随机核对
rng = np.random.default_rng(2202)
n_ok = 0
worst = math.inf
for _ in range(2000):
    m = 40
    h = rng.uniform(0.01, 0.06, m)
    acc = rng.uniform(-1, 1, m) * AMAX[0]
    vel = np.concatenate([[0.0], np.cumsum(acc * h)])
    # 让末速度为零：最后一段用来刹车（若刹车需要的加速度超限，丢掉这条）
    if np.any(np.abs(vel) > VMAX[0]):
        continue
    if vel[-1] == 0:
        continue
    hb = abs(vel[-1]) / AMAX[0]
    dist = float(np.sum((vel[:-1] + vel[1:]) / 2 * h) + vel[-1] * hb / 2)
    if dist <= 0:
        continue
    Ttot = float(h.sum() + hb)
    n_ok += 1
    worst = min(worst, Ttot / trap_plan(dist, VMAX[0], AMAX[0])["T"])
assert n_ok > 500 and worst >= 1.0

# ---------------------------------------------------------------- (3) S 形
S1 = scurve_plan(L1, VMAX[0], AMAX[0], JMAX[0])
tj = AMAX[0] / JMAX[0]
assert abs(S1["tj"] - tj) < 1e-12 and S1["tv"] == 0.0         # 达不到 π rad/s
a, j = AMAX[0], JMAX[0]
vq = (-a / j + math.sqrt((a / j) ** 2 + 4 * L1 / a)) / (2 / a)    # v′²/a + v′ a/j = L
assert abs(vq - S1["vp"]) < 1e-9 and vq >= a * a / j
T_s = S1["T"]
assert abs(T_s - (L1 / vq + vq / a + a / j)) < 1e-9
# 定理 22.2.2：同一 v′ 的梯形曲线滑动平均
Pq = dict(trap_plan(L1, vq, a))
dt = 1e-4
tt = np.arange(0, T_s + dt / 2, dt)
pos_trap = trap_eval(Pq, tt)[0]
pos_box = box_filter(tt, pos_trap, tj)
pos_s = scurve_eval(S1, tt)[0]
err_box = float(np.max(np.abs(pos_box - pos_s)))
assert err_box < 1e-7
# 加加速度只有 ±j 和 0
Sx = scurve_eval(S1, np.linspace(0, T_s, 4001))
assert np.max(np.abs(Sx[3])) <= j + 1e-9 and np.max(np.abs(Sx[2])) <= a + 1e-9 and np.max(Sx[1]) <= VMAX[0] + 1e-12
assert abs(Sx[0][-1] - L1) < 1e-9
# 达到 v 的条件：L ≥ v (v/a + a/j)
L_need = VMAX[0] * (VMAX[0] / a + a / j)

# ---------------------------------------------------------------- (4) 残余振动
r_B = float(np.hypot(*tcp_fk(thB)[:2, 3]))
fn, ze = FN_TOOL, ZETA_TOOL
w = 2 * math.pi * fn


def breaks(kind, tjj=None):
    if kind == "trap":
        return accel_breaks("trap", P1)
    if kind == "cubic":
        return [(0.0, 6 * L1 / E1.T3 ** 2), (E1.T3, -6 * L1 / E1.T3 ** 2)]          # 三次的加速度是 t 的一次函数
    if kind == "quintic":
        return poly_breaks(lambda t: L1 * s_quintic(t / E1.T5, 2) / E1.T5 ** 2, E1.T5)
    return accel_breaks("s", scurve_plan(L1, VMAX[0], a, a / tjj))


amp, hist = {}, {}
for key, kind, tjj in (("trap", "trap", None), ("s10", "s", 0.1), ("s125", "s", 1 / fn), ("cubic", "cubic", None), ("quintic", "quintic", None)):
    tt, xx, A = response_pw(breaks(kind, tjj), fn, ze)
    amp[key] = A * r_B * 1000                                                   # mm
    hist[key] = (tt, xx * r_B * 1000)
P125 = scurve_plan(L1, VMAX[0], a, a * fn)
T_s125 = P125["T"]
assert amp["s125"] < 0.05 * amp["trap"] and amp["s10"] < amp["trap"]
# 定理 22.2.3（无阻尼）：S 形 = 同一 v′ 的梯形 × sinc；用逐段精确的傅里叶积分核对，并与无阻尼的精确响应核对
for tjj in (0.05, 0.1, 1 / fn, 0.2):
    P = scurve_plan(L1, VMAX[0], a, a / tjj)
    Pt = trap_plan(L1, P["vp"], a)
    A_s = abs(fourier_pw(accel_breaks("s", P), w)) / w
    A_t = abs(fourier_pw(accel_breaks("trap", Pt), w)) / w
    assert abs(A_s - A_t * sinc_factor(fn, tjj)) < 1e-12 * (1 + A_t)
    A_s2 = response_pw(accel_breaks("s", P), fn, 0.0, extra=0.0, nsub=1)[2]
    assert abs(A_s2 - A_s) < 1e-9 * (1 + A_t)
# t_j 扫描（作图用）
tj_scan = np.linspace(0.0, 0.32, 129)
amp_scan, amp_pred = [], []
A_tr0 = None
for tjj in tj_scan:
    br = breaks("trap") if tjj == 0 else breaks("s", tjj)
    amp_scan.append(response_pw(br, fn, ze, extra=0.0, nsub=1)[2] * r_B * 1000)
amp_scan = np.array(amp_scan)
k_min = int(np.argmin(amp_scan[:80]))

# 振幅衰减到 0.05 mm 所需的等待时间（之后的自由振动按 e^{−ζωt} 衰减）
TOL = 0.05
settle = {k: max(0.0, math.log(v / TOL) / (ze * w)) for k, v in amp.items()}
assert settle["s125"] == 0.0 and settle["s10"] > 0

out(L1=L1, L1_deg=deg(L1), tol=TOL, st_trap=settle["trap"], st_qui=settle["quintic"], st_s10=settle["s10"], st_cub=settle["cubic"],
    tot_trap=T_trap + settle["trap"], tot_s125=T_s125, tot_qui=E1.T5 + settle["quintic"], tot_s10=T_s + settle["s10"],
    qs_static=AMAX[0] / w ** 2 * r_B * 1000, ta=P1["ta"], tc=P1["tc"], T_trap=T_trap, save_c=100 * save_c, save_q=100 * save_q,
    v_need=VMAX[0] ** 2 / AMAX[0],
    v4=v_sync[3], a4=a_sync[3], v4_deg=deg(v_sync[3]), v2_deg=deg(v_sync[1]), a2=a_sync[1],
    T_small=Ps["T"], v_small=Ps["vp"], n_rand=n_ok, worst=worst,
    tj=tj, vq=vq, vq_deg=deg(vq), T_s=T_s, L_need=L_need, err_box=err_box, s_more=100 * (T_s / T_trap - 1),
    r_B=r_B, A_trap=amp["trap"], A_s10=amp["s10"], A_s125=amp["s125"], A_cub=amp["cubic"], A_qui=amp["quintic"],
    T_s125=T_s125, j125=a * fn, sinc10=sinc_factor(fn, 0.1), tj_best=tj_scan[k_min])
