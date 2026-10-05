"""12.6 节：无穷维的预告：希尔伯特空间。
帕塞瓦尔等式：方波 sign x 在 [−π, π] 上 ‖f‖² = 2π = π Σ b_k²，由此 Σ_{k 奇} 1/k² = π²/8；部分和与极限的差。
ℓ²：(1, 1/2, 1/3, …) 的长度平方 π²/6；(1, 1/√2, 1/√3, …) 不在 ℓ² 中（部分和发散）。
不完备：连续函数 f_n(x) = tanh(nx) 在 [−1, 1] 上按 L² 距离越来越接近，极限却是不连续的 sign x。"""
import numpy as np

from bookout import out

# 帕塞瓦尔
for N in (1, 11, 101, 1001):
    s = sum(16 / (k * k * np.pi ** 2) for k in range(1, N + 1, 2)) * np.pi
    out(**{f"par{N}": float(s), f"gap{N}": float(2 * np.pi - s)})
out(twopi=2 * np.pi, pi2_8=np.pi ** 2 / 8)
# ℓ²
for N in (10, 1000, 100000):
    k = np.arange(1, N + 1)
    out(**{f"l2a{N}": float(np.sum(1 / k ** 2)), f"l2b{N}": float(np.sum(1 / k))})
out(pi2_6=np.pi ** 2 / 6)
# tanh(nx) → sign x
x = np.linspace(-1, 1, 2000001)
d = lambda f, g: float(np.sqrt(np.trapezoid((f - g) ** 2, x)))
for n in (1, 10, 100, 1000):
    out(**{f"ds{n}": d(np.tanh(n * x), np.sign(x)), f"dn{n}": d(np.tanh(n * x), np.tanh(2 * n * x))})
