"""16.1 节：du/dt = Au，用特征向量解耦。
(1) 伺服电机两节点热模型（_motor.py）：停机后从稳态温升 x₀ = (60, 40) K 冷却。A 的特征值、特征向量、两个时间常数；
    x(t) = c₁e^{λ₁t}v₁ + c₂e^{λ₂t}v₂，c = V⁻¹x₀；与数值积分（solve_ivp）比较；绕组温升降到 10 K 需要多久；
(2) 解空间的维数：y'' + y = 0 化为 u' = Au（u = (y, y')），A = [[0, 1], [−1, 0]]，特征值 ±i，
    实的基本解 (cos t, −sin t)、(sin t, cos t)；u(0) ↦ u(t) 的映射可逆，解空间是 2 维的。"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from _motor import A, B
from _num import sci
from bookout import out, tex, vec

lam, V = np.linalg.eig(A)
order = np.argsort(-lam)              # λ₁ 为慢的（绝对值小）
lam, V = lam[order].real, V[:, order].real
V = V / V[0]                          # 第一个分量归一为 1
out(A=tex(A, 4), lam=vec(lam, 5), tau=vec(-1 / lam, 1), tau1=float(-1 / lam[0]), tau2=float(-1 / lam[1]),
    v1=vec(V[:, 0], 3), v2=vec(V[:, 1], 3))
# 稳态：P = 40 W 时 x_ss = −A⁻¹bP
xss = -np.linalg.solve(A, B * 40)
out(xss=vec(xss, 1))
x0 = np.array([60.0, 40.0])
c = np.linalg.solve(V, x0)
out(c=vec(c, 2))
x = lambda t: (V * np.exp(lam * t)) @ c
sol = solve_ivp(lambda t, y: A @ y, (0, 3000), x0, rtol=1e-10, atol=1e-12, dense_output=True)
ts = np.linspace(0, 3000, 301)
out(err_ivp=sci(float(max(np.abs(sol.sol(t) - x(t)).max() for t in ts)) + 1e-17, 0))
for t in (10, 60, 600):
    out(**{f"x_{t}": vec(x(t), 1)})
t10 = brentq(lambda t: x(t)[0] - 10, 1, 5000)
out(t10=float(t10), t10_min=float(t10 / 60))
# 快模态衰减完以后：x ≈ c₁e^{λ₁t}v₁，绕组与外壳温升之比趋于 v₁ 的分量比
out(ratio_slow=float(V[1, 0] / V[0, 0]), x_100=vec(x(100), 1), ratio_100=float(x(100)[1] / x(100)[0]))
# (2) y'' + y = 0
A2 = np.array([[0.0, 1], [-1, 0]])
y0 = np.array([0.3, -0.5])
s2 = solve_ivp(lambda t, y: A2 @ y, (0, 10), y0, rtol=1e-11, atol=1e-12, dense_output=True)
ex = lambda t: y0[0] * np.array([np.cos(t), -np.sin(t)]) + y0[1] * np.array([np.sin(t), np.cos(t)])
out(err2=sci(float(max(np.abs(s2.sol(t) - ex(t)).max() for t in np.linspace(0, 10, 101))) + 1e-17, 0))
