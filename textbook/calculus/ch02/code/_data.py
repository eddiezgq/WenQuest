"""第 2 章插图与程序共用的数据：与问渠实验工具包相同的随机数；舵机的示意模型与实测数据。以下划线开头，构建时不单独运行。"""
import math

import numpy as np


def mulberry32(seed):
    """与问渠实验工具包 api.calc.rng 完全相同的随机数（同一种子在书和实验里给出同一组数）。"""
    s = seed & 0xFFFFFFFF

    def i32(x):
        x &= 0xFFFFFFFF
        return x - (1 << 32) if x >= (1 << 31) else x

    def imul(a, b):
        return i32((a & 0xFFFFFFFF) * (b & 0xFFFFFFFF))

    def u():
        nonlocal s
        s = (s + 0x6D2B79F5) & 0xFFFFFFFF
        t = imul(i32(s) ^ (s >> 15), i32(s) | 1)
        t = i32(t ^ i32(t + imul(t ^ ((t & 0xFFFFFFFF) >> 7), t | 61)))
        return ((t ^ ((t & 0xFFFFFFFF) >> 14)) & 0xFFFFFFFF) / 4294967296

    def gauss():
        a = 0.0
        while a == 0.0:
            a = u()
        return math.sqrt(-2 * math.log(a)) * math.cos(2 * math.pi * u())

    return u, gauss


# ---------- 舵机：脉宽 p（μs）→ 角度 θ（°）。示意模型：中段近似线性，两端略有压缩；读数误差 σ = 0.3°，取到 0.1°
servo_true = lambda p: 90 + 0.095 * (p - 1500) - 1.5e-8 * (p - 1500) ** 3
P = np.arange(600, 2401, 100, dtype=float)
_, gauss = mulberry32(28)
TH = np.array([round((servo_true(p) + 0.3 * gauss()) * 10) / 10 for p in P])
