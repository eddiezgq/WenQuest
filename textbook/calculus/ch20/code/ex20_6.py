"""20.6 节：质量–弹簧–阻尼系统。对数衰减率与阻尼比；受迫振动的幅值放大系数与共振峰；
电机转矩波动激励转子–减速器–上臂的两惯量扭转振动：关节转速多大时发生共振（每转波动次数、波动幅值为假设值）；数值核对。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import out

# 对数衰减率
for z, key in ((0.02, "ld_002"), (0.2, "ld_02")):
    out(**{key: 2 * math.pi * z / math.sqrt(1 - z * z)})
# 放大系数
M = lambda r, z: 1 / math.sqrt((1 - r * r) ** 2 + (2 * z * r) ** 2)
rows = []
for z in (0.02, 0.1, 0.2, 0.5, 0.7):
    rp = math.sqrt(max(1 - 2 * z * z, 0))
    Mp = M(rp, z) if rp > 0 else 1.0
    rows.append(f"| {z:g} | {rp:.3f} | {Mp:.2f} | {1 / (2 * z):.2f} |")
out(rs_tab="\n".join(rows))

# 转矩波动激励：电机每转波动 6 次（假设），幅值为额定转矩 187 mN·m 的 2%（假设），减速比 101。
# 关节匀速转动时电机侧不被锁住：转子（折算到关节 J_r）与上臂（J_a）经减速器扭簧 k 相连，波动作用在转子一侧。
# 扭转角 φ = θ_r − θ_a 满足 φ″ + 2ζω φ′ + ω² φ = T(t)/J_r，ω² = k(1/J_a + 1/J_r)。
Ja, Jr, k, z = 0.5129, 137e-7 * 101 ** 2, 2e4, 0.02
mu = 1 / Ja + 1 / Jr
wn = math.sqrt(k * mu)
N, nper, Trip = 101, 6, 0.02 * 0.187 * 101
w_res = wn / (N * nper)                       # 共振时的关节转速 rad/s
phi_st = Trip / (Jr * k * mu)                 # 等效静态扭转角
arm = Jr / (Ja + Jr)                          # 上臂摆动 = 扭转角 × J_r/(J_a + J_r)
out(rp_Ja=Ja, rp_Jr=Jr, rp_wn=wn, rp_f=wn / (2 * math.pi), rp_wlock=math.sqrt(k / Ja), rp_T=Trip, rp_wj=w_res, rp_deg=math.degrees(w_res),
    rp_static_urad=phi_st * 1e6, rp_res_urad=phi_st * M(1, z) * 1e6, rp_res_tip_um=phi_st * M(1, z) * arm * 0.425 * 1e6,
    rp_n=nper, rp_N=N, rp_arm=arm)
rows = []
for frac in (0.5, 0.9, 1.0, 1.1, 2.0):
    wj = frac * w_res
    amp = phi_st * M(frac, z)
    rows.append(f"| {math.degrees(wj):.1f} | {frac * wn / (2 * math.pi):.1f} | {M(frac, z):.2f} | {amp * 1e6:.1f} | {amp * arm * 0.425 * 1e6:.1f} |")
out(rp_tab="\n".join(rows))
# 数值核对：两惯量模型，共振时从静止开始，3 s 后的扭转振幅
c = 2 * z * wn / mu                           # 扭簧并联的阻尼系数


def two(t, y):
    tr, wr, ta, wa = y
    ph, dph = tr - ta, wr - wa
    Tm = Trip * math.cos(wn * t)
    return [wr, (Tm - k * ph - c * dph) / Jr, wa, (k * ph + c * dph) / Ja]


s = solve_ivp(two, (0, 3), [0, 0, 0, 0], max_step=2 * math.pi / wn / 40, rtol=1e-9, atol=1e-13)
ph = s.y[0] - s.y[2]
tail = ph[s.t > 2.7]
out(rp_num_urad=float(np.max(np.abs(tail))) * 1e6, rp_build_s=1 / (z * wn))
