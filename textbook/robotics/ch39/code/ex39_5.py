"""算例 39.5.1：测力传感器测量链的标定（加载 0→100 N→0，每级 20 N，重复 3 次）。

传感器模型（测量链真实特性，标定前未知）：输出 V = G·(V0 + S·F + n(F) + h(F)) ，其中
零点 V0 = 0.03 mV（电桥不平衡），灵敏度 S = 0.1 mV/N（2 mV/V × 5 V / 100 N），非线性 n(F) = −0.04%·FS·4(F/FS)(1 − F/FS)，
迟滞 h：卸载时比加载时高 0.06%·FS·sin(πF/FS)，读数噪声 0.2 mV（放大后；每个读数是 100 次 ADC 采样的平均，可细于 1 个 LSB）。
参数取值使“迟滞最大”与随机种子无关（换 1000 个种子核对过）。
用最小二乘直线拟合加载与卸载的全部数据，求零点、灵敏度、线性度、迟滞和重复性（%FS）。
"""
import math

import numpy as np

from _meas import F_FS, GAIN
from bookout import out

rng = np.random.default_rng(395)
S = 0.1e-3                                      # V/N（放大前）
V0 = 0.03e-3
FS_V = S * F_FS


def chain(F, unloading):
    n = -0.0004 * FS_V * 4 * (F / F_FS) * (1 - F / F_FS)
    h = 0.0006 * FS_V * math.sin(math.pi * F / F_FS) if unloading else 0.0
    return GAIN * (V0 + S * F + n + h) + rng.normal(0, 0.2e-3)


loads = np.arange(0, F_FS + 1, 20.0)
up, down = [], []
for _ in range(3):
    up.append([chain(F, False) for F in loads])
    down.append([chain(F, True) for F in loads[::-1]][::-1])
up, down = np.array(up), np.array(down)
Fx = np.r_[np.tile(loads, 3), np.tile(loads, 3)]
Vy = np.r_[up.ravel(), down.ravel()]
b, a = np.polyfit(Fx, Vy, 1)                     # V = a + b·F
fit = a + b * loads
y_fs = b * F_FS                                  # 满量程输出（拟合）
lin = float(np.max(np.abs(np.r_[up.mean(0), down.mean(0)] - np.r_[fit, fit])) / y_fs * 100)
hyst = float(np.max(np.abs(down.mean(0) - up.mean(0))) / y_fs * 100)
rep = float(np.max(np.r_[up.std(0, ddof=1), down.std(0, ddof=1)]) * 2 / y_fs * 100)   # 2 倍标准差
assert hyst > lin and hyst > rep                # 正文：三项指标中迟滞最大
# 由拟合反算力：F = (V − a)/b
F_back = (up.mean(0) - a) / b

def f1(v):
    t = f"{v:.1f}"
    return "0.0" if t == "-0.0" else t


rows = r" \\ ".join(f"{F:.0f} & {f1(u * 1e3)} & {f1(d * 1e3)} & {f1((d - u) * 1e3)}" for F, u, d in zip(loads, up.mean(0), down.mean(0)))
out(a_mV=a * 1e3, b_mV=b * 1e3, y_fs=y_fs, lin=lin, hyst=hyst, rep=rep, rows=rows, gain=GAIN,
    S_true_mV=S * GAIN * 1e3, zero_true_mV=V0 * GAIN * 1e3, F_err_max=float(np.max(np.abs(F_back - loads))),
    _loads=loads.tolist(), _up=up.mean(0).tolist(), _down=down.mean(0).tolist(), _fit=[a, b])
