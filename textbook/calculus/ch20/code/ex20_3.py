"""20.3 节：常系数齐次方程。阻尼比不同的二阶系统 ẍ + 2ζω_n ẋ + ω_n² x = 0 的特征根（ω_n = 10 rad/s）；
机械臂上臂在减速器扭转刚度上的自由振动（刚度与阻尼比为假设值）：固有频率、衰减时间常数；重根情形的数值核对。"""
import cmath
import math

from scipy.integrate import solve_ivp

from bookout import T, out

wn = 10.0
rows = []
for z in (0.0, 0.2, 0.7, 1.0, 2.0):
    d = cmath.sqrt(z * z - 1)
    r1, r2 = -z * wn + wn * d, -z * wn - wn * d
    kind = T("无阻尼", "undamped") if z == 0 else T("欠阻尼", "underdamped") if z < 1 else T("临界阻尼", "critical") if z == 1 else T("过阻尼", "overdamped")
    def fmt(r):
        re_ = 0.0 if abs(r.real) < 1e-12 else r.real
        if abs(r.imag) < 1e-12:
            return f"{re_:.2f}"
        sg = "+" if r.imag > 0 else "−"
        return f"{sg}{abs(r.imag):.2f}i" if re_ == 0 else f"{re_:.2f} {sg} {abs(r.imag):.2f}i"
    rows.append(f"| {z:g} | {fmt(r1)} | {fmt(r2)} | {kind} |")
out(root_tab="\n".join(rows))

# 上臂在减速器扭转刚度上的振动：J = 0.5129 kg·m²（17.4 节，绕肩轴），k = 2×10⁴ N·m/rad，ζ = 0.02（假设）
J, k, z = 0.5129, 2e4, 0.02
w = math.sqrt(k / J)
wd = w * math.sqrt(1 - z * z)
out(fx_J=J, fx_k=k, fx_z=z, fx_wn=w, fx_f=w / (2 * math.pi), fx_wd=wd, fx_tau=1 / (z * w), fx_c=2 * z * math.sqrt(k * J),
    fx_n5=math.log(20) / (z * w) * wd / (2 * math.pi), fx_t5=math.log(20) / (z * w))
# 末端被碰一下：肘端（离肩轴 0.425 m）初速度 0.05 m/s，求最大摆角与末端位移
v0 = 0.05 / 0.425
out(fx_amp_urad=v0 / wd * 1e6, fx_tip_um=v0 / wd * 0.425 * 1e6)
tpk = math.atan(wd / (z * w)) / wd                # 第一个峰：θ′ = 0
pk = v0 / wd * math.exp(-z * w * tpk) * math.sin(wd * tpk)
out(fx_pk_urad=pk * 1e6, fx_pk_tip_um=pk * 0.425 * 1e6)

# 重根：y″ + 2y′ + y = 0，y(0) = 1，y′(0) = 0 的解 (1 + x)e^(−x)
s = solve_ivp(lambda x, y: [y[1], -2 * y[1] - y[0]], (0, 3), [1.0, 0.0], rtol=1e-12, atol=1e-14)
out(rep_num=float(s.y[0, -1]), rep_formula=4 * math.exp(-3))
