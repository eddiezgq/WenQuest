"""16.4 节：二阶系统与振动模态。
(1) Go2 一条腿的三质量链（_leg.py）。无阻尼：Kv = ω²Mv，振型 M-正交；模态坐标 q = Φη 把 Mq̈ + Kq = 0 解耦为 η̈ⱼ + ωⱼ²ηⱼ = 0；
(2) 有阻尼：化为一阶系统 u = (q, q̇)，A = [[0, I], [−M⁻¹K, −M⁻¹C]]（6×6），特征值为三对共轭复数 −ζω ± iω√(1−ζ²)；
    与“只取 C 在振型上的对角元”的近似阻尼比 ζⱼ ≈ φⱼᵀCφⱼ/(2ωⱼ) 比较；
(3) 落地：机器人从低台阶落下，触地瞬间三个质量的速度都是 −0.3 m/s，用 u(t) = e^{At}u₀ 求躯干位移；
(4) 生活中的例子：四分之一汽车模型（车身 300 kg、车轮 40 kg、悬架刚度 2×10⁴ N/m、轮胎刚度 2×10⁵ N/m）的两个固有频率。"""
import numpy as np
import scipy.linalg as sl

from _leg import C3, K3, MASS, chain, state_matrix
from _num import fix_sign, sci
from bookout import out, tex, vec

M, K, C = np.diag(MASS), chain(K3), chain(C3)
out(M=tex(M, 3), K=tex(K, 0), mass=vec(MASS, 3))
lam, Phi = sl.eigh(K, M)                    # Φ 的列 M-正交归一：ΦᵀMΦ = I
Phi = fix_sign(Phi)
w = np.sqrt(lam)
f = w / (2 * np.pi)
out(f=vec(f, 2), f1=float(f[0]), f2=float(f[1]), f3=float(f[2]))
shape = Phi / np.abs(Phi).max(0)
out(**{f"phi{j + 1}": vec(shape[:, j], 3) for j in range(3)})
out(PMP=tex(Phi.T @ M @ Phi, 3), PKP=tex(Phi.T @ K @ Phi, 0), orth=sci(float(np.abs(Phi.T @ M @ Phi - np.eye(3)).max()) + 1e-18, 0))
# (2) 阻尼
A = state_matrix(M, K, C)
ev = np.linalg.eigvals(A)
ev = ev[ev.imag > 0]
ev = ev[np.argsort(np.abs(ev))]
zeta = -ev.real / np.abs(ev)
fd = ev.imag / (2 * np.pi)
out(ev=", ".join(f"{z.real:.1f} \\pm {z.imag:.1f}\\mathrm i" for z in ev), zeta=vec(zeta, 3), zeta1=float(zeta[0]), fd=vec(fd, 2), fn=vec(np.abs(ev) / (2 * np.pi), 2))
PCP = Phi.T @ C @ Phi
zeta_m = np.diag(PCP) / (2 * w)
out(PCP=tex(PCP, 1), zeta_m=vec(zeta_m, 3), offdiag=float(np.abs(PCP - np.diag(np.diag(PCP))).max() / np.abs(np.diag(PCP)).max()))
# (3) 落地：q 以静平衡位置为零点。触地瞬间弹簧未受力，三个质量在静平衡位置上方 K⁻¹Mg 处，速度 −0.3 m/s
q0 = np.linalg.solve(K, M @ np.full(3, 9.81))
out(q0_mm=vec(1000 * q0, 1))
u0 = np.r_[q0, -0.3 * np.ones(3)]
ts = np.linspace(0, 1.0, 2001)
U = np.array([sl.expm(A * t) @ u0 for t in ts])
qb = U[:, 0]
i_min = int(np.argmin(qb))
out(qb_min_mm=float(1000 * qb[i_min]), t_min=float(ts[i_min]), qb_05_mm=float(1000 * U[np.searchsorted(ts, 0.5), 0]))
# 模态贡献：ηⱼ(0) = φⱼᵀMq₀，η̇ⱼ(0) = φⱼᵀMq̇₀；无阻尼时第 j 模态的幅值 √(ηⱼ(0)² + (η̇ⱼ(0)/ωⱼ)²)，乘 φ₁ⱼ 得躯干位移的幅值
eta0, eta_dot = Phi.T @ M @ u0[:3], Phi.T @ M @ u0[3:]
out(eta0=vec(eta0, 4), eta_dot=vec(eta_dot, 3))
out(body_mode_amp_mm=vec(1000 * np.abs(Phi[0]) * np.hypot(eta0, eta_dot / w), 2))
# (4) 四分之一汽车
Mc, Kc = np.diag([300.0, 40.0]), np.array([[2e4, -2e4], [-2e4, 2.2e5]])
lc, Vc = sl.eigh(Kc, Mc)
Vc = fix_sign(Vc)
out(car_f=vec(np.sqrt(lc) / (2 * np.pi), 2), car_v1=vec(Vc[:, 0] / Vc[0, 0], 3), car_v2=vec(Vc[:, 1] / Vc[1, 1], 3),
    car_f1=float(np.sqrt(lc[0]) / (2 * np.pi)), car_f2=float(np.sqrt(lc[1]) / (2 * np.pi)))
