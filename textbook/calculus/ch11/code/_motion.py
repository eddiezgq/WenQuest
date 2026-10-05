"""第 11 章共用：给定位移 D、速度上限 V、加速度上限 A（S 形曲线另加加加速度上限 J）的最短时间运动。
返回时间网格上的 (t, θ, ω, α, j)。以下划线开头，构建时不单独运行。"""
import numpy as np


def _integrate(segs, dt):
    """segs：[(时长, 加速度或加加速度的取值, 类型)]，按分段常值积分（解析地逐段推进）。"""
    t, th, w, a = [0.0], [0.0], [0.0], [0.0]
    jj = [0.0]
    for dur, val, kind in segs:
        n = max(1, int(round(dur / dt)))
        h = dur / n
        for _ in range(n):
            if kind == "j":
                a0 = a[-1]
                a1 = a0 + val * h
                w1 = w[-1] + a0 * h + val * h * h / 2
                th1 = th[-1] + w[-1] * h + a0 * h * h / 2 + val * h ** 3 / 6
                jj.append(val)
            else:
                a1 = val
                w1 = w[-1] + val * h
                th1 = th[-1] + w[-1] * h + val * h * h / 2
                jj.append(0.0)
            t.append(t[-1] + h)
            th.append(th1)
            w.append(w1)
            a.append(a1)
    return np.array(t), np.array(th), np.array(w), np.array(a), np.array(jj)


def trapezoid(D, V, A, dt=1e-4):
    if D >= V * V / A:
        ta, tv = V / A, D / V - V / A
    else:
        ta, tv = np.sqrt(D / A), 0.0
    return _integrate([(ta, A, "a"), (tv, 0.0, "a"), (ta, -A, "a")], dt)


def scurve_plan(D, V, A, J):
    """对称七段 S 形曲线的实际最高速度 Vr、最大加速度 Ar 与各段时长（达不到 V 或 A 时自动降低）。"""
    dist = lambda v: v * (v / min(A, (v * J) ** 0.5) + min(A, (v * J) ** 0.5) / J)
    Vr = V
    if dist(V) > D:
        lo, hi = 0.0, V
        for _ in range(100):
            m = (lo + hi) / 2
            lo, hi = (lo, m) if dist(m) > D else (m, hi)
        Vr = lo
    Ar = min(A, (Vr * J) ** 0.5)
    tj, ta = Ar / J, max(0.0, Vr / Ar - Ar / J)
    tv = max(0.0, (D - dist(Vr)) / Vr)
    return Vr, Ar, tj, ta, tv


def scurve(D, V, A, J, dt=1e-4):
    Vr, Ar, tj, ta, tv = scurve_plan(D, V, A, J)
    segs = [(tj, J, "j"), (ta, 0.0, "j"), (tj, -J, "j"), (tv, 0.0, "j"), (tj, -J, "j"), (ta, 0.0, "j"), (tj, J, "j")]
    return _integrate([sg for sg in segs if sg[0] > 0], dt)
