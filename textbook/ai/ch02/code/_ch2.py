"""第 2 章共用的数据与模型规格。以下划线开头，构建时不单独运行。

教学数据都由固定的随机种子生成，读者重跑得到完全相同的数。数据的量级参照数字工厂的设备，但它们是生成的，不是实测记录；
正文第一次用到时如实说明。
"""
import numpy as np

# ---------------------------------------------------------------- 2.2：跑合试验台（线性回归）
# 减速器跑合试验：负载转矩 x（N·m）与 30 分钟后的油温温升 y（K）。按 y = 0.42 x + 3.0 + 噪声（σ = 1.5 K）生成 40 组。
RIG_TRUE = (0.42, 3.0)
RIG_SIGMA = 1.5


def rig_data(n=40, seed=2026):
    rng = np.random.default_rng(seed)
    x = np.round(rng.uniform(5, 60, n), 1)
    y = np.round(RIG_TRUE[0] * x + RIG_TRUE[1] + rng.normal(0, RIG_SIGMA, n), 2)
    return x, y


# ---------------------------------------------------------------- 1.2 节的零件检验数据（逻辑回归沿用）
PARTS = [
    (0.2, 0.4, 1), (0.6, 0.2, 1), (0.4, 1.2, 1), (1.0, 0.6, 1), (0.2, 1.8, 1), (1.4, 0.2, 1), (0.8, 1.0, 1),
    (0.0, 0.8, 1), (1.2, 1.0, 1), (0.6, 1.6, 1), (1.6, 0.4, 1), (0.2, 2.2, 1), (1.0, 1.2, 1), (0.4, 0.6, 1),
    (1.8, 0.0, 1),
    (2.6, 0.4, -1), (2.2, 1.0, -1), (1.6, 1.6, -1), (1.0, 2.4, -1), (0.4, 3.0, -1), (2.8, 1.8, -1), (1.8, 2.6, -1),
    (0.8, 3.4, -1), (3.0, 0.6, -1), (2.4, 2.4, -1), (1.2, 3.0, -1), (0.0, 3.4, -1), (2.6, 1.2, -1), (1.4, 2.0, -1),
    (2.0, 1.6, -1),
]


# ---------------------------------------------------------------- 2.5：两个“月牙”（非线性可分的二分类数据）
def moons(n=200, noise=0.12, seed=7):
    """两个交错的半圆，各 n/2 个点；标签 0、1。"""
    rng = np.random.default_rng(seed)
    m = n // 2
    t = np.linspace(0, np.pi, m)
    a = np.c_[np.cos(t), np.sin(t)]
    b = np.c_[1 - np.cos(t), 0.5 - np.sin(t)]
    X = np.r_[a, b] + rng.normal(0, noise, (n, 2))
    y = np.r_[np.zeros(m), np.ones(m)]
    return X, y


# ---------------------------------------------------------------- 2.7：多项式拟合（过拟合）
def poly_data(n_train=15, n_test=200, sigma=0.15, seed=11):
    """y = sin(2πx) + 噪声，x ∈ [0, 1]。"""
    rng = np.random.default_rng(seed)
    xt = np.sort(rng.uniform(0, 1, n_train))
    yt = np.sin(2 * np.pi * xt) + rng.normal(0, sigma, n_train)
    xs = np.linspace(0, 1, n_test)
    ys = np.sin(2 * np.pi * xs) + rng.normal(0, sigma, n_test)
    return xt, yt, xs, ys


# ---------------------------------------------------------------- 贯穿全书的小型 Transformer（2.9、2.10 节）
# 只有解码器的语言模型（GPT 式），前置层归一化，词元嵌入与输出层共享权重，可学习的位置嵌入。
TINY = {
    "vocab": 2048,      # 词表大小 V
    "ctx": 256,         # 上下文长度 T_max
    "d": 384,           # 模型宽度 d_model
    "layers": 6,        # 层数 L
    "heads": 6,         # 注意力头数 h（每头 d/h = 64）
    "ff": 1536,         # 前馈层宽度 d_ff = 4d
}


def tiny_params(c=TINY):
    """各部分参数量（含偏置与层归一化的增益、偏移）。"""
    d, f, V, T, L = c["d"], c["ff"], c["vocab"], c["ctx"], c["layers"]
    per = {
        "ln1": 2 * d,
        "qkv": 3 * (d * d + d),
        "proj": d * d + d,
        "ln2": 2 * d,
        "ff1": d * f + f,
        "ff2": f * d + d,
    }
    out = {"tok_emb": V * d, "pos_emb": T * d, "per_layer": per, "layer_total": sum(per.values()),
           "ln_f": 2 * d}
    out["blocks"] = L * out["layer_total"]
    out["total"] = out["tok_emb"] + out["pos_emb"] + out["blocks"] + out["ln_f"]   # 输出层与词元嵌入共享，不另计
    out["non_emb"] = out["blocks"] + out["ln_f"]
    return out
