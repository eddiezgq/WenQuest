"""18.3 节：可积函数类——电机 PWM 驱动电压（10 ms 内有 400 个跳变点）的积分等于 V∫d(t)dt；
黎曼 1854 年的例子 R(x) = Σ ((kx))/k²：在每个分母为偶数的有理数处间断，间断点在 [0, 1] 中稠密，却是可积的，
随机取点的黎曼和随细度趋于 0。"""
import math
import random

from bookout import out

# PWM：24 V，开关频率 20 kHz，占空比 d(t) 在 10 ms 内从 0.2 线性升到 0.8
V, fs, Tt = 24.0, 20000.0, 0.01
d = lambda t: 0.2 + 0.6 * t / Tt
Tp = 1 / fs
N = round(Tt / Tp)
exact_pwm = sum(V * d(k * Tp) * Tp for k in range(N))          # 每个周期开始时锁存占空比，导通 d·Tp
avg = V * (0.2 + 0.8) / 2 * Tt
out(pwm_N=N, pwm_jumps=2 * N, pwm_int=exact_pwm * 1000, pwm_avg=avg * 1000, pwm_err=(exact_pwm - avg) * 1e6)


# 黎曼的例子
def saw(x):          # ((x))：x 减去最近的整数，半整数处取 0
    r = x - math.floor(x)
    return 0.0 if abs(r - 0.5) < 1e-15 else (r if r < 0.5 else r - 1)


K = 400
R = lambda x: sum(saw(k * x) / (k * k) for k in range(1, K + 1))
random.seed(18)
rows = []
for n in (10, 100, 1000):
    h = 1 / n
    s_left = sum(R(i * h) * h for i in range(n))
    s_rand = sum(R((i + random.random()) * h) * h for i in range(n))
    rows.append(f"| {n} | {s_left:+.5f} | {s_rand:+.5f} |")
# 在 x = 1/2 处的跳跃：左右极限之差约 π²/8 · ... 用数值估计
eps = 1e-7
jump = R(0.5 - eps) - R(0.5 + eps)
out(riem_tab="\n".join(rows), riem_jump=jump, riem_jump_ex=math.pi ** 2 / 8)
