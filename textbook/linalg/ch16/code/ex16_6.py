"""16.6 节：状态空间预告。
关节伺服的状态空间模型：x = (θ, ω)，J θ̈ = −bθ̇ + u，J = 0.01 kg·m²，b = 0.1 N·m·s/rad；ẋ = Ax + Bu，y = Cx（编码器只测 θ）。
(1) 开环特征值 0、−b/J；
(2) 状态反馈 u = −Kx = −(k_pθ + k_dω)：把闭环特征值放到 −20 ± 20i，由特征多项式 s² + 40s + 800 求出 k_p、k_d；
(3) 零阶保持的精确离散化：A_d = e^{AT}，B_d = ∫₀ᵀ e^{As}ds·B，用分块矩阵的指数一次算出；
    数字控制器 u_k = −Kx_k 的闭环矩阵 A_d − B_dK，特征值的模随采样周期 T 变化，找出失稳的 T；
(4) 阶跃指令：θ 从 0 转到 1 rad（u = −K(x − x_ref)），连续与 T = 5 ms 的数字控制比较。"""
import numpy as np
import scipy.linalg as sl
from scipy.optimize import brentq

from bookout import out, tex, vec

J, b = 0.01, 0.1
A = np.array([[0.0, 1], [0, -b / J]])
B = np.array([[0.0], [1 / J]])
out(A=tex(A, 0), B=tex(B, 0), ol=", ".join(f"{v:g}" for v in np.sort(np.linalg.eigvals(A).real)[::-1]))
# (2) 极点配置：det(sI − (A − BK)) = s² + (b + k_d)/J s + k_p/J
kp, kd = 800 * J, 40 * J - b
K = np.array([[kp, kd]])
Acl = A - B @ K
out(kp=kp, kd=kd, Acl=tex(Acl, 0), cl=", ".join(f"{z.real:.0f} {'+' if z.imag > 0 else '−'} {abs(z.imag):.0f}i" for z in np.linalg.eigvals(Acl)))


# (3) 零阶保持离散化
def zoh(T):
    Mb = np.zeros((3, 3))
    Mb[:2, :2], Mb[:2, 2:] = A, B
    E = sl.expm(Mb * T)
    return E[:2, :2], E[:2, 2:]


T = 0.005
Ad, Bd = zoh(T)
out(Ad=tex(Ad, 4), Bd=tex(Bd, 5))
rho = lambda T: max(abs(np.linalg.eigvals(zoh(T)[0] - zoh(T)[1] @ K)))
out(rho5=rho(0.005), rho20=rho(0.02), rho40=rho(0.04))
Tcrit = brentq(lambda T: rho(T) - 1, 0.01, 0.2)
out(Tcrit_ms=1000 * Tcrit)
# 连续极点映射：e^{λT}
out(map5=float(abs(np.exp((-20 + 20j) * 0.005))))
# (4) 阶跃
xr = np.array([1.0, 0])
ts = np.arange(0, 0.4 + 1e-12, T)
xc = [sl.expm(Acl * t) @ (-xr) + xr for t in ts]                # 连续闭环：x − x_ref 按 e^{A_cl t} 衰减
x, xd = np.zeros(2), []
for _ in ts:
    xd.append(x.copy())
    u = -K @ (x - xr)
    x = Ad @ x + (Bd @ u)
xc, xd = np.array(xc), np.array(xd)
over = lambda th: 100 * (th.max() - 1)
out(over_c=over(xc[:, 0]), over_d=over(xd[:, 0]), dev_max=float(np.abs(xc[:, 0] - xd[:, 0]).max()),
    zeta=float(20 / np.hypot(20, 20)))
