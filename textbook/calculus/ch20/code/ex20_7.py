"""20.7 节：关节的 PD 控制。关节侧总惯量 = 上臂绕肩轴 0.5129 kg·m²（17.4 节）+ RE 40 转子经减速比 101 折算（19.4 节）；
粘性摩擦 0.5 N·m·s/rad（假设）。按超调 ≤ 5%、2% 调节时间 ≤ 0.6 s 设计 Kp、Kd；肘端加负载、重力矩、转矩限幅的影响。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import out

Ja, Jr, b = 0.5129, 137e-7 * 101 ** 2, 0.5
J = Ja + Jr
z, wn = 0.7, 10.0
Kp = J * wn * wn
Kd = 2 * z * wn * J - b
Tmax = 10 * 60.3e-3 * 101                    # 驱动器限流 10 A（19.1 节习题）折算到关节
Tcont = 0.187 * 101                          # 额定转矩折算到关节
out(pd_Ja=Ja, pd_J=J, pd_Jr=Jr, pd_b=b, pd_Kp=Kp, pd_Kd=Kd, pd_Tmax=Tmax, pd_Tcont=Tcont, pd_Mp=100 * math.exp(-math.pi * z / math.sqrt(1 - z * z)),
    pd_ts_est=4 / (z * wn))


def sim(Kp, Kd, J, step=0.5, grav=0.0, lim=None, T=2.0):
    def rhs(t, y):
        q, w = y
        tau = Kp * (step - q) - Kd * w
        if lim is not None:
            tau = max(-lim, min(lim, tau))
        return [w, (tau - b * w - grav * math.cos(q)) / J]
    ts = np.linspace(0, T, 4001)
    s = solve_ivp(rhs, (0, T), [0, 0], t_eval=ts, rtol=1e-9, atol=1e-11, max_step=1e-3)
    q = s.y[0]
    tau = Kp * (step - q) - Kd * s.y[1]
    if lim is not None:
        tau = np.clip(tau, -lim, lim)
    over = (q.max() - step) / step * 100
    band = np.abs(q - q[-1]) > 0.02 * step
    ts2 = ts[np.nonzero(band)[0][-1] + 1] if band.any() else 0.0
    return dict(over=over, ts=ts2, tpk=float(np.max(np.abs(tau))), qend=float(q[-1]))


r0 = sim(Kp, Kd, J)
out(pd_over=r0["over"], pd_ts=r0["ts"], pd_tpk=r0["tpk"])
# 上升时间（10% → 90%），线性阶跃响应的公式
qq = lambda t: 1 - math.exp(-z * wn * t) * (math.cos(wn * math.sqrt(1 - z * z) * t) + z / math.sqrt(1 - z * z) * math.sin(wn * math.sqrt(1 - z * z) * t))
tt = np.linspace(0, 1, 100001)
qv = np.array([qq(t) for t in tt])
out(pd_tr=float(tt[np.argmax(qv >= 0.9)] - tt[np.argmax(qv >= 0.1)]))
r = sim(Kp, Kd, J, lim=Tmax)
out(pd_over_lim=r["over"], pd_ts_lim=r["ts"])
r = sim(Kp, Kd, J, lim=Tcont)
out(pd_over_cont=r["over"], pd_ts_cont=r["ts"])
# 肘端加 2 kg
Jl = J + 2 * 0.425 ** 2
zl = (b + Kd) / (2 * math.sqrt(Kp * Jl))
rl = sim(Kp, Kd, Jl)
out(ld_J=Jl, ld_z=zl, ld_wn=math.sqrt(Kp / Jl), ld_over=rl["over"], ld_ts=rl["ts"])
# 重力：上臂水平附近，重力矩 m g d cos q（17.1 节约 17.5 N·m）
mg_d = 8.393 * 9.81 * 0.2125
rg = sim(Kp, Kd, J, grav=mg_d)
out(gv_tau=mg_d, gv_err=0.5 - rg["qend"], gv_err_est=mg_d * math.cos(0.5) / Kp)
# 结构共振频率与闭环带宽
out(fx_wn=math.sqrt(2e4 / Ja), fx_ratio=math.sqrt(2e4 / Ja) / wn)
