"""13.6 节：积分的运动学意义——由加速度积分出速度、位置；陀螺仪零偏使航向角线性漂移、使横向位置二次漂移；
加速度计零偏使位置误差按 t² 增长；静止标定零偏后的残差；随机噪声的角度随机游走（按 √t 增长）。"""
import math
import random

from bookout import out

# 9.2.6：最大角加速度 300°/s²，从静止开始 0.1 s
amax, t = 300.0, 0.1
out(w_max=amax * t, th_mvt=amax * t * t, th_int=amax * t * t / 2)

# 加速度计零偏 b（m/s²）：速度误差 bt，位置误差 bt²/2
b = 0.02
out(acc_tab="\n".join(f"| {tt:g} | {b * tt:.2f} | {b * tt * tt / 2:.2f} |" for tt in (1, 10, 60, 600)))

# 陀螺仪零偏 0.05°/s：航向误差 = bias·t；AGV 以 1 m/s 直行时横向偏差 ≈ ∫₀ᵗ v sin(bias·τ) dτ
bias = 0.05
rows = []
for tt in (10, 60, 300, 600):
    e = bias * tt
    br = math.radians(bias)
    lat = (1 - math.cos(br * tt)) / br            # ∫₀ᵗ sin(br τ) dτ，v = 1 m/s
    rows.append(f"| {tt} | {e:.1f} | {lat:.2f} |")
out(gyro_tab="\n".join(rows), lat60_approx=0.5 * math.radians(bias) * 60 ** 2)

# 仿真：100 Hz 陀螺仪，零偏 0.05°/s，噪声标准差 0.1°/s；AGV 前 5 s 静止（用于标定），然后每 20 s 转 90°
Ts, Tend, sig = 0.01, 65.0, 0.1
rnd = random.Random(13)


def yaw_rate(tt):
    """真实角速度（°/s）：5 s 后每 20 s 一次 90° 转弯，历时 2 s，正弦形速度。"""
    if tt < 5:
        return 0.0
    u = (tt - 5) % 20
    return 45 * (1 - math.cos(math.pi * u)) if u < 2 else 0.0   # 2 s 内积分为 90°


n = int(round(Tend / Ts))
ts = [k * Ts for k in range(n + 1)]
true_w = [yaw_rate(tt) for tt in ts]
meas = [w + bias + rnd.gauss(0, sig) for w in true_w]
true_th = [0.0]
raw = [0.0]
for k in range(n):
    true_th.append(true_th[-1] + (true_w[k] + true_w[k + 1]) / 2 * Ts)
    raw.append(raw[-1] + (meas[k] + meas[k + 1]) / 2 * Ts)
k5 = int(round(5 / Ts))
b_hat = sum(meas[:k5]) / k5
cal = [r - b_hat * tt for r, tt in zip(raw, ts)]
out(b_hat=b_hat, err_raw=raw[-1] - true_th[-1], err_cal=cal[-1] - true_th[-1], true_end=true_th[-1],
    arw=sig * math.sqrt(Ts * (Tend - 5)), bias_se=sig / math.sqrt(k5))


def end_point(h):
    """由航向（°）和车速（5 s 后 1 m/s）推算终点位置。"""
    x = y = 0.0
    for k in range(1, n + 1):
        vv = 1.0 if ts[k] >= 5 else 0.0
        x += vv * math.cos(math.radians(h[k])) * Ts
        y += vv * math.sin(math.radians(h[k])) * Ts
    return x, y


p_true = end_point(true_th)
out(dev_raw=math.dist(p_true, end_point(raw)), dev_cal=math.dist(p_true, end_point(cal)))
