"""算例 M2.2.1—M2.2.3：链式法则与计算图（M2.2 节）。

反向传播就是链式法则按计算图的拓扑序算一遍。本程序把一个两层小网络的梯度手推一遍，
再与数值梯度核对——这正是 2.5 节写自动微分时该做的检查。最后数一数：反向比前向贵多少。
"""
import numpy as np

from bookout import out

v = {}
# ---------- 一个两层网络：h = tanh(W1 x + b1)，ŷ = w2ᵀ h + b2，损失取平方误差
rng = np.random.default_rng(2)
d_in, d_h = 4, 5
W1 = rng.normal(0, 0.5, (d_h, d_in))
b1 = rng.normal(0, 0.1, d_h)
w2 = rng.normal(0, 0.5, d_h)
b2 = 0.3
x = rng.normal(0, 1, d_in)
y = 0.7


def forward(W1, b1, w2, b2, x, y):
    z1 = W1 @ x + b1
    h = np.tanh(z1)
    yhat = w2 @ h + b2
    return 0.5 * (yhat - y) ** 2, (z1, h, yhat)


L, (z1, h, yhat) = forward(W1, b1, w2, b2, x, y)
v["loss"] = float(L)
v["yhat"] = float(yhat)

# ---------- 手推的反向：从损失一路乘回去
dL_dyhat = yhat - y                                   # ∂ℒ/∂ŷ
dL_dw2 = dL_dyhat * h                                 # ŷ = w2ᵀh + b2
dL_db2 = dL_dyhat
dL_dh = dL_dyhat * w2
dL_dz1 = dL_dh * (1 - np.tanh(z1) ** 2)               # tanh 的导数
dL_dW1 = np.outer(dL_dz1, x)                          # z1 = W1 x + b1
dL_db1 = dL_dz1
v["dL_dw2"] = [round(float(a), 4) for a in dL_dw2]
v["dL_db2"] = float(dL_db2)

# ---------- 与数值梯度核对
def num(fun, p, h=1e-6):
    p = np.asarray(p, dtype=float)
    g = np.zeros_like(p)
    it = np.nditer(p, flags=["multi_index"])
    while not it.finished:
        e = np.zeros_like(p)
        e[it.multi_index] = h
        g[it.multi_index] = (fun(p + e) - fun(p - e)) / (2 * h)
        it.iternext()
    return g


gW1 = num(lambda P: forward(P, b1, w2, b2, x, y)[0], W1)
gw2 = num(lambda P: forward(W1, b1, P, b2, x, y)[0], w2)
gb1 = num(lambda P: forward(W1, P, w2, b2, x, y)[0], b1)
v["err_W1"] = float(np.abs(gW1 - dL_dW1).max())
v["err_w2"] = float(np.abs(gw2 - dL_dw2).max())
v["err_b1"] = float(np.abs(gb1 - dL_db1).max())
assert max(v["err_W1"], v["err_w2"], v["err_b1"]) < 1e-7, "手推的梯度必须与数值梯度一致"
v["n_param"] = W1.size + b1.size + w2.size + 1

# ---------- 前向与反向各要多少次乘加
fwd = d_h * d_in + d_h                                # W1 x 与 w2ᵀh
bwd = d_h * d_in + d_h                                # 对 W1 的梯度、对 x 的梯度各一遍
v["mac_fwd"], v["mac_bwd"] = fwd, 2 * fwd
v["ratio"] = v["mac_bwd"] / v["mac_fwd"]
v["note_6N"] = 6                                      # 一个词元的训练约 6N FLOP（1.4 节）：前向 2N + 反向 4N

# ---------- 为什么不用数值梯度训练：每个参数要算两次前向
v["num_fwd_per_step"] = 2 * v["n_param"]
v["num_vs_back"] = v["num_fwd_per_step"] / 3          # 反向传播一步约等于 3 次前向的代价
GPT3_N = 175e9
v["gpt3_fwd"] = 2 * GPT3_N                            # 数值梯度：1750 亿参数 × 2 次前向
out(**v)
