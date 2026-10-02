"""算例 1.2.1、1.2.2：感知机学习零件检验数据；诺维科夫界的验证；异或问题上感知机不收敛。

式 (1.2.3)：w ← w + η y x̃（判错时）。定理 1.2.1：更新次数 k ≤ (R/γ)²。
"""
import numpy as np

from _perceptron import PARTS, XOR, augmented, max_margin, perceptron
from bookout import out

X, y = augmented(PARTS)
n = len(PARTS)
n_pos = int(np.sum(y > 0))

# 算例 1.2.1：从 w = 0 开始，η = 1
w, k, epochs, hist, ok = perceptron(PARTS, eta=1.0)
assert ok
assert np.all(y * (X @ w) > 0)                 # 学到的 w 把训练数据全部分对

# 学习率不影响更新次数（从 w = 0 出发时，w 只差一个正的倍数）
w2, k2, epochs2, _, ok2 = perceptron(PARTS, eta=0.1)
assert ok2 and k2 == k and np.allclose(w2, 0.1 * w)

# 诺维科夫界：R 与最大间隔 γ*
R = float(np.max(np.linalg.norm(X, axis=1)))
w_star, gamma = max_margin(PARTS)
assert np.all(y * (X @ w_star) >= 1 - 1e-7)
bound = (R / gamma) ** 2
assert k <= bound
# 用感知机自己学到的分界面算出的间隔（任何一个能分开数据的单位向量都可以代入定理）
gamma_w = float(np.min(y * (X @ w)) / np.linalg.norm(w))
assert gamma_w <= gamma + 1e-9

# 分界线写成 x₂ = a x₁ + c 的形式（w = (w1, w2, b)）
a, c = -w[0] / w[1], -w[2] / w[1]
a_s, c_s = -w_star[0] / w_star[1], -w_star[2] / w_star[1]

# 算例 1.2.2：异或
wx, kx, ex, histx, okx = perceptron(XOR, eta=1.0, max_epochs=100)
assert not okx
Xx, yx = augmented(XOR)
errors_last = int(np.sum(yx * (Xx @ wx) <= 0))
period = None                                    # 权重序列最终是周期的：找出周期
for p in range(1, 50):
    if np.allclose(histx[-1], histx[-1 - p]):
        period = p
        break

g2_star = float(np.min(y * (X @ w_star)) / np.linalg.norm(w_star[:2]))      # 平面上点到直线的距离
g2_w = float(np.min(y * (X @ w)) / np.linalg.norm(w[:2]))
out(g2_star=g2_star, g2_w=g2_w, n=n, n_pos=n_pos, n_neg=n - n_pos, k=k, epochs=epochs, w1=w[0], w2=w[1], b=w[2], a=a, c=c,
    k2=k2, R=R, gamma=gamma, gamma_w=gamma_w, bound=bound, bound_w=(R / gamma_w) ** 2,
    a_star=a_s, c_star=c_s, xor_epochs=ex, xor_updates=kx, xor_errors=errors_last, xor_period=period)
