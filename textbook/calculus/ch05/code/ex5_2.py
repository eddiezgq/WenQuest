"""5.2 节：间断点——航向角读数的“解卷绕”（消去 2π 跳变，恢复连续的航向）；
关节库仑摩擦 F_c·sgn(v) 在 v = 0 处的跳跃间断引起数值仿真中的抖振，以及用连续函数 tanh 光滑化的代价。"""
import math

import numpy as np

from bookout import out

# 解卷绕：相邻读数之差超过 π，就认为跨过了 ±π，补上 ∓2π
w, T = 0.5, 0.02
t = np.arange(0, 30, T)
theta = 2.5 + w * t
read = np.arctan2(np.sin(theta), np.cos(theta))


def unwrap(a):
    out_ = [a[0]]
    k = 0
    for p, q in zip(a, a[1:]):
        d = q - p
        if d > math.pi:
            k -= 1
        elif d < -math.pi:
            k += 1
        out_.append(q + 2 * math.pi * k)
    return np.array(out_)


u = unwrap(read)
out(n_jumps=int(np.sum(np.abs(np.diff(read)) > math.pi)), unwrap_err=float(np.max(np.abs(u - theta))),
    np_unwrap_same=int(np.allclose(u, np.unwrap(read))), turns=float((theta[-1] - theta[0]) / (2 * math.pi)))
# 采样太慢时解卷绕失效：每个周期转过的角度超过 π，就分不清是正转还是反转
for wf in (100.0, 160.0, 200.0):
    th = wf * t[:50]
    rd = np.arctan2(np.sin(th), np.cos(th))
    out(**{f"fast_{int(wf)}": float(np.max(np.abs(unwrap(rd) - th)))})
out(w_limit=math.pi / T)

# 关节库仑摩擦：J dv/dt = τ − F_c·s(v) − b·v，τ < F_c，理论上关节应停住
J, Fc, b, tau, dt = 0.5, 2.0, 0.1, 1.0, 1e-3


def sim(fric, v0=0.2, n=2000):
    v, vs = v0, []
    for _ in range(n):
        v += dt * (tau - fric(v) - b * v) / J
        vs.append(v)
    return np.array(vs)


sgn = sim(lambda v: Fc * np.sign(v))
tail = sgn[1000:]
out(t_stop=float(np.argmax(np.abs(sgn) < 1e-2) * dt), chatter_flips=int(np.sum(np.diff(np.sign(tail)) != 0)),
    chatter_pp=float(np.max(tail) - np.min(tail)), chatter_pred=(Fc + tau) * dt / J, chatter_down=(Fc - tau) * dt / J,
    chatter_mean=float(np.mean(tail)))
for vs_ in (0.01, 0.001):
    sm = sim(lambda v: Fc * math.tanh(v / vs_), n=20000)
    out(**{f"creep_{int(round(1 / vs_))}": float(sm[-1]),
           f"creep_pred_{int(round(1 / vs_))}": vs_ * math.atanh(tau / Fc),
           f"flips_{int(round(1 / vs_))}": int(np.sum(np.diff(np.sign(sm[1000:])) != 0))})

# 可去间断：sin x / x 在 0 处补充定义为 1（numpy 的 sinc 就是这样做的，它算的是 sin(πx)/(πx)）
out(sinc0=float(np.sinc(0.0)), sinc_small=float(np.sinc(1e-8 / math.pi)))
