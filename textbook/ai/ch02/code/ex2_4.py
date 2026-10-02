"""算例 2.4.1、2.4.2：两个 ReLU 隐藏单元实现异或；线性层的复合仍是线性的；用 ReLU 网络逼近 sin x。

式 (2.4.5)：g(x) = f(a) + Σ_{k=1}^{N} c_k ReLU(x − x_{k−1})，c_1 为第一段斜率，c_k 为第 k 段与第 k−1 段的斜率之差；
式 (2.4.4)：分段线性插值的误差 ≤ h² max|f''| / 8。
"""
import numpy as np

from bookout import out

relu = lambda z: np.maximum(z, 0)

# 算例 2.4.1：异或
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
W1 = np.array([[1.0, 1.0], [1.0, 1.0]])
b1 = np.array([0.0, -1.0])
w2 = np.array([1.0, -2.0])
H = relu(X @ W1.T + b1)
yhat = H @ w2
assert np.allclose(yhat, [0, 1, 1, 0])

# 两层线性映射的复合等于一层
rng = np.random.default_rng(0)
A1, a1 = rng.normal(size=(5, 3)), rng.normal(size=5)
A2, a2 = rng.normal(size=(2, 5)), rng.normal(size=2)
x = rng.normal(size=3)
assert np.allclose(A2 @ (A1 @ x + a1) + a2, (A2 @ A1) @ x + (A2 @ a1 + a2))


# 算例 2.4.2：ReLU 网络逼近 f(x) = sin x，x ∈ [0, 2π]
def relu_interp(f, a, b, N):
    """N 段等距分段线性插值写成单隐藏层 ReLU 网络：返回 (节点, 系数 c, 常数)。"""
    xs = np.linspace(a, b, N + 1)
    ys = f(xs)
    slopes = np.diff(ys) / np.diff(xs)
    c = np.r_[slopes[0], np.diff(slopes)]          # c_1 = 第一段斜率，c_k = 第 k 段与第 k−1 段斜率之差
    return xs, c, ys[0]


def net(xq, xs, c, y0):
    return y0 + relu(xq[:, None] - xs[None, :-1]) @ c


a, b = 0.0, 2 * np.pi
xq = np.linspace(a, b, 20001)
rows = []
for N in (4, 8, 16, 32, 64):
    xs, c, y0 = relu_interp(np.sin, a, b, N)
    g = net(xq, xs, c, y0)
    assert np.allclose(net(xs, xs, c, y0), np.sin(xs), atol=1e-12)   # 在节点上精确插值
    err = float(np.max(np.abs(g - np.sin(xq))))
    h = (b - a) / N
    bound = h ** 2 / 8                              # max|sin''| = 1
    assert err <= bound + 1e-12
    rows.append((N, err, bound, 3 * N + 1))          # 参数：N 个权重 1（固定）、N 个偏置、N 个输出权重，加 1 个常数
ratio = rows[2][1] / rows[3][1]                     # N 加倍，误差缩小到约 1/4

# 参数量：输入 d、隐藏层宽 m、输出 k 的单隐藏层网络
d_in, m, k = 784, 256, 10
n_params = d_in * m + m + m * k + k

out(yhat=str(yhat.astype(int).tolist()), e4=rows[0][1], b4=rows[0][2], e8=rows[1][1], b8=rows[1][2],
    e16=rows[2][1], b16=rows[2][2], e32=rows[3][1], b32=rows[3][2], e64=rows[4][1], b64=rows[4][2],
    ratio=ratio, n_params=n_params, d_in=d_in, m=m, k=k)
