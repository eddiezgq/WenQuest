"""本章共用：数字工厂减速器车间的出厂检测数据（模拟数据，只用于教学）。以下划线开头，构建时不单独运行。

检测项目、过程均值与标准差与第 2 章（ex2_7_data.py）相同。各项目并不独立：齿轮啮合质量、轴承与润滑、配合松紧
三个“看不见的因素”同时影响好几个项目。按标准化单位写成因子模型

    z = L f + e,   f ~ N(0, I₃),   e ~ N(0, Ψ),   Ψ = I − diag(L Lᵀ)，

于是各项目方差为 1、相关矩阵为 R = L Lᵀ + Ψ。原始单位的记录为 x = μ + σ ⊙ z。
实验 19.6 用同一模型和同一个线性同余发生器（lcg）在浏览器里生成相同的数据。
"""
import math

import numpy as np

ITEMS = ["输出轴直径偏差", "齿圈径向跳动", "空载噪声", "温升", "振动速度", "回差"]
ITEMS_EN = ["shaft diameter deviation", "gear runout", "no-load noise", "temperature rise", "vibration velocity", "backlash"]
SHORT = ["直径", "跳动", "噪声", "温升", "振动", "回差"]
SHORT_EN = ["diam.", "runout", "noise", "temp.", "vib.", "backlash"]
UNITS = ["μm", "μm", "dB(A)", "K", "mm/s", "arcmin"]
MU = np.array([0.0, 12.0, 60.0, 15.0, 1.2, 3.0])
SIGMA = np.array([3.0, 3.0, 1.5, 2.0, 0.25, 0.4])
# 因子载荷（标准化单位）：列为 啮合质量、轴承与润滑、配合松紧
L = np.array([
    [0.00, 0.00, 0.60],
    [0.80, 0.00, 0.00],
    [0.60, 0.70, 0.00],
    [0.10, 0.85, 0.30],
    [0.50, 0.78, 0.00],
    [0.50, 0.00, -0.45],
])
PSI = 1.0 - np.sum(L ** 2, axis=1)
R_TRUE = L @ L.T + np.diag(PSI)

# 第二阶段（监控）的故障：润滑油用错牌号（黏度偏高）——搅油损失大、温升高，油膜阻尼大、噪声和振动略低（标准化单位的偏移）
FAULT_OIL = np.array([0.0, 0.0, -1.0, 1.8, -1.0, 0.0])


class lcg:
    """整数线性同余发生器 + 博克斯–穆勒变换。JavaScript 版（实验 19.6）逐个得到相同的数。"""

    def __init__(self, seed):
        self.s = seed % 2147483647

    def u(self):
        self.s = (self.s * 48271) % 2147483647
        return self.s / 2147483647

    def n(self):
        u1, u2 = self.u(), self.u()
        return math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)


def sample_z(n, seed, shift=None, start=0):
    """n 件减速器的标准化检测值（n×6）。shift 从第 start 件（从 0 数）起加到每件上。"""
    g = lcg(seed)
    Z = np.empty((n, 6))
    for k in range(n):
        f = np.array([g.n() for _ in range(3)])
        e = np.array([g.n() for _ in range(6)]) * np.sqrt(PSI)
        Z[k] = L @ f + e
        if shift is not None and k >= start:
            Z[k] += shift
    return Z


def raw(Z):
    return MU + SIGMA * Z


# 第 2 章（2.7 节）的八份检测记录（原始单位），与 ch02/code/ex2_7_data.py 相同：
# 记录 2、6 像轴承磨损，记录 3、7 像齿轮偏心，记录 4、8 像装配过紧，记录 1、5 正常
RECORDS2 = np.array([
    [1.0, 13.0, 60.5, 15.5, 1.25, 3.1], [-2.0, 12.5, 63.6, 18.6, 1.95, 3.1], [0.5, 19.5, 62.0, 15.6, 1.75, 3.9],
    [3.5, 11.5, 61.2, 19.8, 1.35, 2.3], [-1.0, 11.0, 59.4, 14.2, 1.10, 2.9], [0.0, 13.5, 64.4, 19.0, 2.10, 3.3],
    [-0.5, 18.0, 61.8, 15.0, 1.60, 3.6], [2.5, 12.0, 60.9, 17.4, 1.30, 2.6]])

SEED_I, SEED_II = 20261101, 20261102
N_I = 200                                   # 第一阶段：受控的 200 件，用来估计均值和协方差
X_I = raw(sample_z(N_I, SEED_I))
N_II, START_II = 60, 30                     # 第二阶段：再生产 60 件，从第 31 件起用错了润滑油
X_II = raw(sample_z(N_II, SEED_II, FAULT_OIL, START_II))
