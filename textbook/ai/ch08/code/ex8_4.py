"""算例 8.4.1：训练后量化与量化感知训练。用 NumPy 训练一个两层网络（16 → 64 → 1，GELU），拟合一个固定的“老师”网络
生成的回归数据；然后把两层权重按逐通道对称量化到 INT4：
（1）训练后量化（PTQ）：训练好的权重直接量化，看测试误差升高多少；
（2）量化感知训练（QAT）：从训练好的权重出发再训练一段，前向时用“伪量化”的权重（量化再反量化），反向时把伪量化当作恒等映射，
    梯度直接传给浮点权重（直通估计，straight-through estimator），训练结束后再量化；
（3）作为对照，同样再训练一段但不做伪量化，再量化。
测试误差用均方误差，相对于数据本身的方差报告。"""
import numpy as np

from bookout import out

rng = np.random.default_rng(84)
d, h, n = 16, 64, 4096


def gelu(z):
    return 0.5 * z * (1 + np.tanh(np.sqrt(2 / np.pi) * (z + 0.044715 * z ** 3)))


def dgelu(z):
    c = np.sqrt(2 / np.pi)
    u = np.tanh(c * (z + 0.044715 * z ** 3))
    return 0.5 * (1 + u) + 0.5 * z * (1 - u * u) * c * (1 + 3 * 0.044715 * z * z)


T1, T2 = rng.normal(0, 1, (d, 32)) / np.sqrt(d), rng.normal(0, 1, (32, 1)) / np.sqrt(32)   # 老师网络
X = rng.normal(0, 1, (n, d))
Xt = rng.normal(0, 1, (n, d))
Y = gelu(X @ T1) @ T2
Yt = gelu(Xt @ T1) @ T2


def fq(w, bits=4):
    """逐输出通道（列）对称伪量化：量化再反量化。"""
    qmax = 2 ** (bits - 1) - 1
    s = np.abs(w).max(axis=0, keepdims=True) / qmax
    return np.clip(np.round(w / s), -qmax, qmax) * s


def loss(W1, W2, x, y):
    return float(np.mean((gelu(x @ W1) @ W2 - y) ** 2) / np.var(y))


def train(W1, W2, steps, lr, quant):
    W1, W2 = W1.copy(), W2.copy()
    m = [np.zeros_like(W1), np.zeros_like(W2)]
    v = [np.zeros_like(W1), np.zeros_like(W2)]
    for t in range(1, steps + 1):
        idx = rng.integers(0, n, 256)
        x, y = X[idx], Y[idx]
        A, B = (fq(W1), fq(W2)) if quant else (W1, W2)       # 伪量化只用在前向
        z = x @ A
        a = gelu(z)
        e = 2 * (a @ B - y) / len(y)
        gB = a.T @ e
        gA = x.T @ ((e @ B.T) * dgelu(z))
        for i, (W, g) in enumerate(((W1, gA), (W2, gB))):    # 直通估计：对伪量化权重的梯度直接给浮点权重（Adam）
            m[i] = 0.9 * m[i] + 0.1 * g
            v[i] = 0.999 * v[i] + 0.001 * g * g
            W -= lr * (m[i] / (1 - 0.9 ** t)) / (np.sqrt(v[i] / (1 - 0.999 ** t)) + 1e-8)
    return W1, W2


W1, W2 = rng.normal(0, 1, (d, h)) / np.sqrt(d), rng.normal(0, 1, (h, 1)) / np.sqrt(h)
W1, W2 = train(W1, W2, 4000, 3e-3, False)
fp = loss(W1, W2, Xt, Yt)
ptq = loss(fq(W1), fq(W2), Xt, Yt)
q1, q2 = train(W1, W2, 1500, 1e-3, True)
qat = loss(fq(q1), fq(q2), Xt, Yt)
c1, c2 = train(W1, W2, 1500, 1e-3, False)
more = loss(fq(c1), fq(c2), Xt, Yt)
out(fp_pct=100 * fp, ptq_pct=100 * ptq, qat_pct=100 * qat, more_pct=100 * more, more_fp_pct=100 * loss(c1, c2, Xt, Yt))
