"""算例 8.5.1—8.5.3：大模型的量化。
（1）激活中的离群通道：一批激活 X（512 个词元 × 1024 个通道，标准正态）里有 4 个通道的幅度大 50 倍（示意；大模型中这样的
    “离群特征”在少数固定的通道上出现）。逐张量 INT8 量化 X 与权重 W 后相乘，输出的相对误差：
    - 没有离群通道时；- 有离群通道时；
    - LLM.int8() 的做法：离群通道（幅度超过 6）单独用浮点计算，其余按 INT8；
    - SmoothQuant 的做法：按通道把难度从激活“搬”到权重，X' = X / s、W' = s·W，s_j = max|X_j|^α / max|W_j|^(1−α)，α = 0.5，
      再都按逐张量 INT8。
（2）仅权重量化：W 按逐通道 INT4 与按每 128 个输入一组的分组 INT4（每组一个比例），误差各多少。
（3）显存与逐词生成：读一遍权重的时间（A10，600 GB/s）——小型 Transformer 与 70 亿参数的模型在 FP16、INT8、INT4（分组，
    每组另存一个 FP16 比例）下的权重大小。大模型逐词生成受显存带宽限制（3.8.4 节），权重小一半，读权重的时间就少一半。"""
import numpy as np

from _ch8 import A10
from bookout import out

rng = np.random.default_rng(85)
ntok, dm, do = 512, 1024, 1024
X0 = rng.normal(0, 1, (ntok, dm))
W = rng.normal(0, 1, (dm, do)) / np.sqrt(dm)
out_ch = rng.choice(dm, 4, replace=False)
X = X0.copy()
X[:, out_ch] *= 50


def q8(x):
    s = np.abs(x).max() / 127
    return np.clip(np.round(x / s), -127, 127) * s


rel = lambda a, b: float(np.linalg.norm(a - b) / np.linalg.norm(b) * 100)
e_clean = rel(q8(X0) @ q8(W), X0 @ W)
e_out = rel(q8(X) @ q8(W), X @ W)
big = np.abs(X).max(axis=0) > 6                             # LLM.int8()：幅度超过 6 的通道走浮点
e_int8llm = rel(q8(X[:, ~big]) @ q8(W[~big]) + X[:, big] @ W[big], X @ W)
s = np.abs(X).max(axis=0) ** 0.5 / np.abs(W).max(axis=1) ** 0.5
e_smooth = rel(q8(X / s) @ q8(W * s[:, None]), X @ W)


def q4(w, group=None):
    if group:
        g = w.reshape(-1, group, w.shape[1])
        sc = np.abs(g).max(axis=1, keepdims=True) / 7
        return (np.clip(np.round(g / sc), -7, 7) * sc).reshape(w.shape)
    sc = np.abs(w).max(axis=0, keepdims=True) / 7
    return np.clip(np.round(w / sc), -7, 7) * sc


W_out = W * np.exp(rng.normal(0, 0.5, (dm, 1)))             # 各输入行尺度不同，分组才有用（示意）
e_w4c = rel(q4(W_out), W_out)
e_w4g = rel(q4(W_out, 128), W_out)

# （3）显存与读权重的时间
small = 11532288                                             # 小型 Transformer 的参数个数（输出层与嵌入共享，2.9 节）
big_n = 7e9
size = lambda n, bits, group=128: n * bits / 8 + (n / group * 2 if bits == 4 else 0)   # INT4 分组：每组一个 FP16 比例
v = {}
for name, n in (("s", small), ("b", big_n)):
    for tag, bits in (("16", 16), ("8", 8), ("4", 4)):
        b = size(n, bits)
        v[f"{name}{tag}_MB"] = b / 1e6
        v[f"{name}{tag}_ms"] = b / A10["bw"] * 1e3
out(n_big=int(big.sum()), e_clean=e_clean, e_out=e_out, e_int8llm=e_int8llm, e_smooth=e_smooth, e_w4c=e_w4c, e_w4g=e_w4g,
    fits16=bool(size(big_n, 16) < A10["mem"]), fits4=bool(size(big_n, 4) < A10["mem"]), **v)
