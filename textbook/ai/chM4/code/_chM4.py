"""数学篇第 M4 章共用的东西：浮点数的拆解、几种数值格式的参数，以及一个小语言模型的概率表。

本章两条线：信息论（熵、交叉熵、困惑度、互信息）与数值计算（浮点、条件数、稳定的写法）。
两条线在"取对数"这件事上汇合：概率要在对数域里算，既是信息论的要求，也是数值的要求。

各种数值格式的位数、范围与精度不在本章重复，见表 8.1.1；本章只借 NumPy 自带的 FP64、FP32、FP16
讲"有效数字"与"误差怎样累积"。
"""
from __future__ import annotations

import struct

import numpy as np

# 数值格式不在本章重复列表：各格式的位数、范围与精度见表 8.1.1（第 8 章用一套统一的舍入函数算出）。
# 本章只用 NumPy 自带的三种（FP64、FP32、FP16），讲"有效数字"与"误差怎样累积"这两件事。
NP_FORMATS = {"fp64": np.float64, "fp32": np.float32, "fp16": np.float16}


def spec(key: str) -> dict:
    """这种格式的机器精度、十进制有效数字与范围（取自 NumPy 的 finfo，与第 8 章的算法一致）。"""
    f = np.finfo(NP_FORMATS[key])
    return dict(name=key.upper(), bits=f.bits, eps=float(f.eps), digits=-np.log10(float(f.eps)),
                max=float(f.max), min_normal=float(f.tiny))


def bits_of(x: float) -> tuple[int, int, int]:
    """把一个双精度数拆成（符号, 指数, 尾数）三段，用来把"浮点是什么"摊开给读者看。"""
    b = struct.unpack(">Q", struct.pack(">d", x))[0]
    return b >> 63, (b >> 52) & 0x7FF, b & ((1 << 52) - 1)


def logsumexp(z: np.ndarray, axis=None):
    """数值稳定的 log Σ exp：先减最大值（M4.5 节）。"""
    zmax = np.max(z, axis=axis, keepdims=True)
    return np.squeeze(zmax, axis=axis) + np.log(np.exp(z - zmax).sum(axis=axis))


def softmax(z: np.ndarray, axis=-1):
    z = z - np.max(z, axis=axis, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)


def toy_lm(seed: int = 0, vocab: int = 32, n: int = 4000):
    """一个最小的"语言模型"：词表 vocab，真实分布是幂律（齐普夫），模型给出一个带噪声的估计。
    用它算熵、交叉熵与困惑度（M4.1、M4.2 节），比拿真模型省事，而且每个数都能复算。"""
    g = np.random.default_rng(2026_1008 + seed)
    rank = np.arange(1, vocab + 1)
    p = 1 / rank ** 1.1
    p /= p.sum()                                           # 真实分布：少数词很常见，长尾很长
    tokens = g.choice(vocab, size=n, p=p)
    counts = np.bincount(tokens, minlength=vocab)
    q = (counts + 0.5) / (counts.sum() + 0.5 * vocab)      # 模型：加了平滑的频率估计
    return p, q, tokens
