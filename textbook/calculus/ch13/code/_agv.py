"""第 12、13 章共用：一次 AGV 搬运的速度曲线（梯形：加速 0.5 m/s²，最高 1.2 m/s，全程 10 m）与“编码器”采样数据。
以下划线开头，构建时不单独运行。"""
import math
import random

A, VMAX, DIST = 0.5, 1.2, 10.0
TA = VMAX / A                       # 加速段时长
TC = (DIST - VMAX * TA) / VMAX      # 匀速段时长
T = 2 * TA + TC                     # 全程时长


def v(t):
    """真实速度（m/s）。"""
    if t <= 0 or t >= T:
        return 0.0
    if t < TA:
        return A * t
    if t < TA + TC:
        return VMAX
    return A * (T - t)


def acc(t):
    if t <= 0 or t >= T:
        return 0.0
    if t < TA:
        return A
    if t < TA + TC:
        return 0.0
    return -A


def samples(Ts=0.1, sigma=0.02, seed=12):
    """每隔 Ts 秒的速度读数（带噪声），从 t = 0 到超过 T 的第一个采样点。"""
    rnd = random.Random(seed)
    n = math.ceil(T / Ts)
    ts = [k * Ts for k in range(n + 1)]
    return ts, [v(t) + (rnd.gauss(0, sigma) if 0 < t < T else 0.0) for t in ts]


# 功率模型：车重 m（含货物），滚动阻力系数 mu，传动效率 eta，车载电子设备 P0；制动时不回收能量
M, MU, G, ETA, P0 = 100.0, 0.015, 9.81, 0.85, 30.0


def power(t):
    mech = (M * acc(t) + MU * M * G) * v(t)
    return max(mech, 0.0) / ETA + P0
