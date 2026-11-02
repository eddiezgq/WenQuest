"""第 21 章部分习题答案中的数值。"""
import math

from bookout import out

g = 9.81
out(e2122=math.sqrt(2 * g / 1.0))
m, h = 5.0, 0.6
I, mgh = m * h * h, m * g * h
out(e2144_I=I, e2144_mgh=mgh, e2144_Kp=I * 64 + mgh, e2144_Kd=2 * 0.7 * 8 * I)
# 21.4.6：以 1 rad/s 倒向外侧时能救回的最大倾角（与 ex21_4 相同的模型）
from scipy.integrate import solve_ivp

m, h = 5.0, 0.4
I, mgl = m * h * h, m * g * h
Kp, Kd, Tmax = I * 64 + mgl, 2 * 0.7 * 8 * I, 15.0


def recovers(th0, w0=1.0):
    def rhs(t, y):
        tau = max(-Tmax, min(Tmax, -Kp * y[0] - Kd * y[1]))
        return [y[1], (mgl * math.sin(y[0]) + tau) / I]
    ev = lambda t, y: abs(y[0]) - math.pi / 2
    ev.terminal = True
    s = solve_ivp(rhs, (0, 5), [th0, w0], events=ev, max_step=1e-3, rtol=1e-9, atol=1e-11)
    return s.status == 0 and abs(s.y[0, -1]) < 1e-3


lo, hi = 0.0, 1.5
for _ in range(40):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if recovers(mid) else (lo, mid)
out(e2146=math.degrees(lo))
