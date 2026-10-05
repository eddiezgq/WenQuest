"""第 4 章程序共用的运动曲线：梯形速度曲线（匀加速—匀速—匀减速）与 S 形速度曲线（加加速度有限）。"""
import numpy as np


def trapezoid(L, vm, am):
    """走完距离 L（> 0）的梯形速度曲线。返回 dict：总时间 T、实际最大速度 vp、加速时间 ta、匀速时间 tc，
    以及位置、速度、加速度函数 x(t)、v(t)、a(t)（t 从 0 起，超出 [0, T] 时取端点值）。"""
    ta = vm / am
    if am * ta ** 2 > L:                       # 达不到最大速度：三角形速度曲线
        ta = np.sqrt(L / am); vp = am * ta; tc = 0.0
    else:
        vp = vm; tc = (L - am * ta ** 2) / vm
    Tm = 2 * ta + tc

    def a(t):
        t = np.asarray(t, float)
        return np.where((t >= 0) & (t < ta), am, np.where((t >= ta + tc) & (t < Tm), -am, 0.0))

    def v(t):
        t = np.clip(np.asarray(t, float), 0, Tm)
        return np.where(t < ta, am * t, np.where(t < ta + tc, vp, np.maximum(0, vp - am * (t - ta - tc))))

    def x(t):
        t = np.clip(np.asarray(t, float), 0, Tm)
        u = np.clip(t - ta - tc, 0, ta)
        return 0.5 * am * np.minimum(t, ta) ** 2 + vp * np.clip(t - ta, 0, tc) + vp * u - 0.5 * am * u ** 2
    return dict(T=Tm, vp=vp, ta=ta, tc=tc, x=x, v=v, a=a)


def scurve(L, vm, am, jm, n=20001):
    """走完距离 L 的 S 形速度曲线（七段式：加加速度 ±jm，加速度不超过 am，速度不超过 vm）。
    数值构造：加速度曲线是“梯形”，由加速段与减速段对称拼成；若距离不够，按比例降低峰值速度（二分法）。
    返回 dict：T、vp，以及按细网格插值的 x、v、a、j 函数。"""
    def accel_phase(vp):
        tj = min(am / jm, np.sqrt(vp / jm))     # 加加速度段时长
        ap = jm * tj                            # 实际最大加速度
        tca = max(0.0, vp / ap - tj)            # 匀加速段时长
        ta = 2 * tj + tca                       # 加速段总时长
        da = vp * ta / 2                        # 加速段走过的距离（对称，平均速度 vp/2）
        return tj, ap, tca, ta, da

    vp = vm
    if 2 * accel_phase(vp)[4] > L:              # 距离不够：降低峰值速度
        lo, hi = 0.0, vm
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if 2 * accel_phase(mid)[4] <= L else (lo, mid)
        vp = lo
    tj, ap, tca, ta, da = accel_phase(vp)
    tc = (L - 2 * da) / vp if vp > 0 else 0.0
    Tm = 2 * ta + tc
    t = np.linspace(0, Tm, n)

    def acc(t):                                 # 加速度：两个对称的梯形（加速段为正、减速段为负）
        def bump(u):
            return np.clip(np.minimum(jm * u, np.minimum(ap, jm * (ta - u))), 0, None) * ((u >= 0) & (u <= ta))
        return bump(t) - bump(t - ta - tc)
    aa = acc(t)
    jj = np.gradient(aa, t)
    dt = t[1] - t[0]
    vv = np.concatenate([[0], np.cumsum((aa[1:] + aa[:-1]) / 2) * dt])
    xx = np.concatenate([[0], np.cumsum((vv[1:] + vv[:-1]) / 2) * dt])
    f = lambda arr: (lambda q: np.interp(q, t, arr))
    return dict(T=Tm, vp=vp, tj=tj, ap=ap, tca=tca, tc=tc, t=t, x=f(xx), v=f(vv), a=f(aa), j=f(jj), xend=xx[-1])
