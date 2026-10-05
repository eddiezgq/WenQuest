"""9.2 节：拉格朗日中值定理——区间测速：平均速度一定等于某一时刻的瞬时速度；
中值点的位置 θ（f(x + h) − f(x) = f′(x + θh)h）；关节限速给出每个控制周期的位置变化上界；
cos 在 [0, 1] 上的压缩系数（6.4 节）；几个由中值定理得到的不等式。"""
import math

from bookout import out

# 区间测速：区间长 L = 15 km，用时 7.5 min，平均 120 km/h；车速 v(t) 是一条光滑曲线
L, Tm = 15.0, 7.5 / 60                       # km, h
# 车速（km/h）：经过两端的测速点时减到 95，中间开到 145：v = 95 + 50 sin²(πt/Tm)，区间限速 100
v = lambda t: 95 + 50 * math.sin(math.pi * t / Tm) ** 2
s = lambda t: 95 * t + 50 * (t / 2 - Tm * math.sin(2 * math.pi * t / Tm) / (4 * math.pi))   # 位置，s′ = v
avg = s(Tm) / Tm
# 找出所有 v(ξ) = 平均速度 的时刻
xs = []
N = 20000
for k in range(N):
    t0, t1 = k * Tm / N, (k + 1) * Tm / N
    f0, f1 = v(t0) - avg, v(t1) - avg
    if f0 == 0 or f0 * f1 < 0:
        lo, hi = t0, t1
        for _ in range(60):
            mid = (lo + hi) / 2
            if (v(lo) - avg) * (v(mid) - avg) <= 0:
                hi = mid
            else:
                lo = mid
        xs.append(lo)
out(L=L, Tmin=Tm * 60, avg=avg, vmax=max(v(k * Tm / 1000) for k in range(1001)), vmin=min(v(k * Tm / 1000) for k in range(1001)),
    n_xi=len(xs), xi_min=", ".join(f"{x * 60:.2f}" for x in xs))

# 中值点的位置：f(x) = eˣ 在 0 处，eʰ − 1 = h e^{θh}，θ = ln((eʰ − 1)/h)/h → 1/2
rows = []
for h in (1.0, 0.1, 0.01, 0.001):
    th = math.log(math.expm1(h) / h) / h
    rows.append(f"| {h:g} | {th:.6f} |")
out(theta_tab="\n".join(rows))

# 关节限速：UR5e 各关节最大速度 180°/s，控制周期 2 ms（500 Hz）
vmax, Ts = 180.0, 0.002
out(step_deg=vmax * Ts, step_mm=math.radians(vmax * Ts) * 0.817 * 1000)

# cos 在 [0, 1] 上：|cos x − cos y| = |sin ξ||x − y| ≤ sin 1·|x − y|
xi = 0.7390851332151607
out(sin1=math.sin(1), k_star=math.sin(xi))
x, rs = 1.0, []
for k in range(40):
    xn = math.cos(x)
    rs.append(abs(xn - xi) / abs(x - xi))
    x = xn
out(cos_ratio=rs[-1])

# 不等式：x/(1 + x) < ln(1 + x) < x（x > 0）
rows = []
for x in (0.01, 0.1, 1.0, 10.0):
    rows.append(f"| {x:g} | {x / (1 + x):.6f} | {math.log1p(x):.6f} | {x:g} |")
out(ineq_tab="\n".join(rows))
