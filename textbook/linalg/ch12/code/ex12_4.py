"""12.4 节：里斯表示定理；伴随算子。
𝒫₂ 上取内积 ⟨p, q⟩ = ∫₀¹ pq dx，线性泛函 ℓ(p) = p(1/2) 由唯一的 u ∈ 𝒫₂ 表示：解格拉姆（希尔伯特）矩阵方程；
次数 n 增大时表示元的长度 ‖u_n‖² = u_n(1/2) 不断增大（无穷维时“取值”没有表示元，12.6 节）。
机器人：静止的三连杆臂上加关节力矩 τ，功率 τᵀw 是关节速度 w 的线性泛函；在动能内积下它的表示元是 M⁻¹τ，正是关节角加速度。
伴随：J 从 (ℝ³, M-内积) 到 (ℝ², 点积) 的伴随是 M⁻¹Jᵀ；求导算子在两端为零的函数上的伴随是 −D（分部积分）。"""
import numpy as np
from numpy.polynomial import legendre as Lg

from _arm3 import jac, mass
from _frac import fvec
from _num import sci
from bookout import out, vec

# 里斯表示：𝒫₂，ℓ(p) = p(1/2)
G = np.array([[1 / (i + j + 1) for j in range(3)] for i in range(3)])
rhs = np.array([0.5 ** k for k in range(3)])
c = np.linalg.solve(G, rhs)
out(u=fvec(c), u_half=float(np.polyval(c[::-1], 0.5)))
# 检验：对 p = 1 + 2x − 3x²
pc = np.array([1.0, 2, -3])
xx = np.linspace(0, 1, 200001)
u_x, p_x = np.polyval(c[::-1], xx), np.polyval(pc[::-1], xx)
out(chk_ip=float(np.trapezoid(u_x * p_x, xx)), chk_val=float(np.polyval(pc[::-1], 0.5)))
# 次数增大时 ‖u_n‖² = Σ φ_k(1/2)²，φ_k = √(2k+1) P_k(2x − 1)
rows = []
for n in (2, 4, 8, 16, 32, 64):
    s = sum((2 * k + 1) * Lg.legval(0.0, [0] * k + [1]) ** 2 for k in range(n + 1))
    rows.append(f"{n}: {s:.2f}")
    out(**{f"un{n}": float(s)})
# 机器人：力矩的表示元是加速度
q = np.radians([30.0, 60.0, -45.0])
M, J = mass(q), jac(q)
tau = np.array([0.0, 0.0, 1.0])
acc = np.linalg.solve(M, tau)
rng = np.random.default_rng(124)
worst = max(abs(tau @ w - acc @ M @ w) for w in rng.normal(size=(100, 3)))
out(tau=vec(tau, 0), acc=vec(acc, 1), riesz_chk=sci(float(worst) + 1e-30, 0))
# 伴随：J*（M-内积 → 点积）= M⁻¹Jᵀ
Jstar = np.linalg.solve(M, J.T)
worst = 0.0
for _ in range(100):
    w, y = rng.normal(size=3), rng.normal(size=2)
    worst = max(worst, abs((J @ w) @ y - w @ M @ (Jstar @ y)))
out(adj_chk=sci(worst + 1e-30, 0), adj_plain=float(max(abs((J @ w) @ y - w @ M @ (J.T @ y)) for w, y in zip(rng.normal(size=(5, 3)), rng.normal(size=(5, 2))))))
# 求导的伴随：f = sin πx，g = x²(1 − x) 在 [0, 1] 两端为零
f, df = np.sin(np.pi * xx), np.pi * np.cos(np.pi * xx)
g, dg = xx ** 2 * (1 - xx), 2 * xx - 3 * xx ** 2
out(Dfg=float(np.trapezoid(df * g, xx)), fDg=float(np.trapezoid(f * dg, xx)))
