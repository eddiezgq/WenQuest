"""第 6 章 送布机构 —— 课程包数值题的计算（模型与教材 6.4–6.8 节、虚拟实验 6-1 一致）。"""
from math import pi, sqrt, cos, sin, acos, atan, tan, radians, degrees

R, L = 15.5, 55.0; LAM = R / L
TIP0, EYE = 18.0, 2.0           # 针尖在上止点高出针板 18 mm；针眼上沿高出针尖 2 mm


def xN(f):
    a = radians(f)
    return R * (1 - cos(a)) - L * (1 - sqrt(1 - (LAM * sin(a)) ** 2))


def tip(f):
    return TIP0 - xN(f)


def cross(level):
    """针尖下行到高度 level 的主轴转角（0–180°）。"""
    a, b = 0.0, 180.0
    for _ in range(80):
        m = (a + b) / 2
        a, b = (m, b) if tip(m) > level else (a, m)
    return (a + b) / 2


A = 1.1
FE = cross(-EYE)                # 针眼上沿到达针板 → 114.2°


def half(h):
    return degrees(acos((A - h) / A))


H0 = 0.8
PHL0 = FE - half(H0)
EFF0 = (1 - cos(2 * radians(half(H0)))) / 2   # 0.926


def feed(s=3.0, dT=0.0, dP=0.0, h=0.8, t=1.5):
    """返回 (升出角, 落下角, 布在针中移动 mm, 回拖 mm, 实际针距 mm)。"""
    hf = half(h)
    phL, phF = PHL0 + dT, FE + dT + dP
    rise, drop = phL - hf, phL + hf
    S = s / EFF0
    X = lambda p: S / 2 * cos(radians(p - phF))
    ain = cross(t); aout = 360 - ain
    drag = back = 0.0; n = 4000
    for i in range(n):
        p0 = rise + (drop - rise) * i / n; p1 = rise + (drop - rise) * (i + 1) / n
        dx = X(p1) - X(p0); pm = ((p0 + p1) / 2) % 360
        if ain < pm < aout:
            drag += abs(dx)
        if dx < 0:
            back += -dx
    return rise % 360, drop % 360, drag, back, X(drop) - X(rise)


out = {}
out["针眼上沿到针板/落牙角"] = FE
out["α(0.8)"] = half(0.8); out["抓布区间(0.8)"] = 2 * half(0.8)
out["抓布区间(1.0)"] = 2 * half(1.0)
out["送布效率 0.926"] = EFF0
out["3mm 所需行程"] = 3 / EFF0; out["4mm 所需行程"] = 4 / EFF0
out["布厚1.5 入布/出布"] = (cross(1.5), 360 - cross(1.5))
out["标准定时"] = feed()
out["定时 -10"] = feed(dT=-10); out["定时 +10"] = feed(dT=10); out["定时 +20"] = feed(dT=20)
out["相位 -30（水平提前）"] = feed(dP=-30); out["相位 +30"] = feed(dP=30)
out["牛仔4mm 入布角"] = cross(4.0)
out["牛仔 标准"] = feed(t=4.0); out["牛仔 定时-8"] = feed(t=4.0, dT=-8); out["牛仔 仅水平-8"] = feed(t=4.0, dP=-8)
out["牙高1.0"] = feed(h=1.0)
# 针距调节器 s = 0.926 * 2 e i tanθ
e, i_ = 3.0, 1.0
theta = lambda s: degrees(atan(s / (EFF0 * 2 * e * i_)))
out["θ(3)"] = theta(3); out["θ(5)"] = theta(5); out["θ(2.5)"] = theta(2.5)
out["每 1 mm 的转角"] = [theta(k + 1) - theta(k) for k in range(5)]
w = lambda n: 2 * pi * n / 60
out["v,a @5000 3mm"] = (3 / EFF0 / 2e3 * w(5000), 3 / EFF0 / 2e3 * w(5000) ** 2)
out["v,a @5000 4mm"] = (4 / EFF0 / 2e3 * w(5000), 4 / EFF0 / 2e3 * w(5000) ** 2)
# 针送布：牙最高点 180°
out["针送布抓布区间"] = (180 - half(0.8), 180 + half(0.8))
# 上下层错位（衬里示意参数：μf 0.15, K 10, F0 0.32, μd 0.55）
muf, K, F0, mud = 0.15, 10, 0.32, 0.55
Pmin = F0 / (mud - muf)
out["衬里 Pmin"] = Pmin; out["衬里 错位@Pmin 40cm"] = muf * Pmin / K * 400
out["1% 40cm"] = 0.01 * 400
out["针送布 错位(0.3)"] = 0.3 * out["衬里 错位@Pmin 40cm"]
# ---- 课程包新增题 ----
out["Q α(h=0.9)区间"] = 2 * half(0.9)
out["Q 3.5mm 行程"] = 3.5 / EFF0
out["Q θ(4)"] = theta(4)
out["Q v @4000 3mm"] = 3 / EFF0 / 2e3 * w(4000)
out["E a @4000 3mm"] = 3 / EFF0 / 2e3 * w(4000) ** 2
out["E 衬里 P=1.0 错位 40cm"] = muf * 1.0 / K * 400
out["E 1.5% 50cm"] = 0.015 * 500
out["E 牛仔 定时-4"] = feed(t=4.0, dT=-4)
out["机器人 0.8% 30 cm"] = 0.008 * 300
for k, v in out.items():
    print(k, ":", v)
