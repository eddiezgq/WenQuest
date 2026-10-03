"""2.8 节：从数据到函数——舵机角度—脉宽数据的线性与三次拟合（与实验 2.8 用同一组数据）；
开普勒第三定律的幂律（对数坐标）；一杯热茶的冷却（指数模型）；北京的昼长（周期模型）。"""
import math

import numpy as np

from _data import P, TH, mulberry32, servo_true
from bookout import out

out(servo_table="\n".join(f"| {int(p)} | {th:.1f} |" for p, th in zip(P[::2], TH[::2])), n_servo=P.size)
u = (P - 1500) / 1000                     # 换成标准区间，改善数值条件


def fit(deg):
    c = np.polyfit(u, TH, deg)
    res = TH - np.polyval(c, u)
    return c, res, float(np.sqrt(np.mean(res**2)))


c1, res1, rms1 = fit(1)
c3, res3, rms3 = fit(3)
c10, res10, rms10 = fit(10)
# 直线：θ = b + k (p − 1500)/1000，斜率换成 °/μs
out(k1=c1[0] / 1000, b1=c1[1], rms1=rms1, rms3=rms3, rms10=rms10, res1_end=float(res1[0]), res1_mid=float(res1[P.size // 2]))
# 残差的模式：直线拟合的残差左端正、右端负，1/4 处为负、3/4 处为正（S 形）；三次拟合的残差没有规律
out(res1_q=float(res1[4]), res1_q3=float(res1[14]), res1_max=float(np.abs(res1).max()), res3_max=float(np.abs(res3).max()))
# 外推到 p = 2500 μs：三次模型、十次多项式与“真值”
pe = 2500
ue = (pe - 1500) / 1000
out(ext3=float(np.polyval(c3, ue)), ext10=float(np.polyval(c10, ue)), ext_true=servo_true(pe), ext1=float(np.polyval(c1, ue)))
# 反函数：转到 150° 需要多大的脉宽？三次模型用二分法反解
target = 150.0
f3 = lambda p: float(np.polyval(c3, (p - 1500) / 1000)) - target
lo, hi = 1500.0, 2400.0
for _ in range(60):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if f3(m) < 0 else (lo, m)
p3 = (lo + hi) / 2
p1 = 1500 + 1000 * (target - c1[1]) / c1[0]
lo, hi = 1500.0, 2400.0
for _ in range(60):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if servo_true(m) < target else (lo, m)
pt = (lo + hi) / 2
out(p150_3=p3, p150_1=p1, p150_true=pt, p150_dp=abs(p1 - pt), p150_dth=abs(p1 - pt) * c1[0] / 1000)

# ---------- 开普勒第三定律：轨道半长轴 a（天文单位）与公转周期 T（年）
planets = [("水星", "0.387", "0.241"), ("金星", "0.723", "0.615"), ("地球", "1.000", "1.000"),
           ("火星", "1.524", "1.881"), ("木星", "5.203", "11.86"), ("土星", "9.537", "29.46")]
la = np.log10([float(p[1]) for p in planets])
lT = np.log10([float(p[2]) for p in planets])
kk, bb = np.polyfit(la, lT, 1)
out(kepler_table="\n".join(f"| {n} | {a} | {T} |" for n, a, T in planets), kepler_k=kk, kepler_b=bb)

# ---------- 热茶冷却：室温 20 °C，T(t) = 20 + 65 e^(−t/22)（t 以分钟计），每 5 分钟读一次，误差 σ = 0.3 °C
_, g2 = mulberry32(5)
tt = np.arange(0, 61, 5, dtype=float)
TT = np.array([round((20 + 65 * math.exp(-t / 22) + 0.3 * g2()) * 10) / 10 for t in tt])
y = np.log(TT - 20)
s_, i_ = np.polyfit(tt, y, 1)
out(tea_tau=-1 / s_, tea_A=math.exp(i_), tea_n=tt.size, tea_first=float(TT[0]), tea_last=float(TT[-1]),
    tea_lin_rms=float(np.sqrt(np.mean((TT - np.polyval(np.polyfit(tt, TT, 1), tt)) ** 2))))
# 茶降到 50 °C 要多久（模型的反函数）
out(tea_50=-1 / s_ * math.log(math.exp(i_) / 30))

# ---------- 北京（北纬 39.9°）的昼长：由太阳赤纬的近似公式算出，再用正弦模型拟合
lat = math.radians(39.9)
n = np.arange(1, 366, 7, dtype=float)
dec = np.radians(23.44) * np.sin(2 * np.pi * (284 + n) / 365)
day = 2 / 15 * np.degrees(np.arccos(-np.tan(lat) * np.tan(dec)))
A = np.column_stack([np.ones_like(n), np.sin(2 * np.pi * n / 365), np.cos(2 * np.pi * n / 365)])
cf, *_ = np.linalg.lstsq(A, day, rcond=None)
amp = math.hypot(cf[1], cf[2])
peak = (math.atan2(cf[1], cf[2]) / (2 * math.pi) * 365) % 365          # c1 sin + c2 cos = amp cos(2πn/365 − φ)
out(day_mean=float(cf[0]), day_amp=amp, day_peak=peak, day_max=float(day.max()), day_min=float(day.min()),
    day_rms=float(np.sqrt(np.mean((day - A @ cf) ** 2))) * 60)
