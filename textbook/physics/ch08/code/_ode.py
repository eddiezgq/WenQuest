"""第 8 章程序共用的积分器。状态 y 是一维数组，f(t, y) 返回 dy/dt。

二阶方程 x'' = a(t, x, v) 写成 y = [x, v]（x、v 可以是矢量，按 [x..., v...] 拼接），
半隐式欧拉法要分开处理位置和速度，所以单独写成 semi_implicit(acc, ...)。
"""
import numpy as np


def euler_step(f, t, y, h):
    return y + h * f(t, y)


def rk2_step(f, t, y, h):                         # 中点法（二阶龙格–库塔）
    k1 = f(t, y)
    k2 = f(t + h / 2, y + h / 2 * k1)
    return y + h * k2


def rk4_step(f, t, y, h):
    k1 = f(t, y)
    k2 = f(t + h / 2, y + h / 2 * k1)
    k3 = f(t + h / 2, y + h / 2 * k2)
    k4 = f(t + h, y + h * k3)
    return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


STEPS = {"euler": euler_step, "rk2": rk2_step, "rk4": rk4_step}


def run(f, y0, h, n, method="rk4", t0=0.0):
    """从 y0 起走 n 步，返回 t（n + 1 个）和 Y（n + 1 行）。"""
    step = STEPS[method]
    Y = np.empty((n + 1, len(y0)))
    Y[0] = y0
    t = t0
    for k in range(n):
        Y[k + 1] = step(f, t, Y[k], h)
        t += h
    return t0 + h * np.arange(n + 1), Y


def semi_implicit(acc, x0, v0, h, n, t0=0.0):
    """半隐式欧拉法：先用当前的 x、v 求加速度更新速度，再用新速度更新位置。返回 t、X、V。"""
    x, v = np.array(x0, float), np.array(v0, float)
    X, V = [x.copy()], [v.copy()]
    t = t0
    for _ in range(n):
        v = v + h * acc(t, x, v)
        x = x + h * v
        t += h
        X.append(x.copy()); V.append(v.copy())
    return t0 + h * np.arange(n + 1), np.array(X), np.array(V)
