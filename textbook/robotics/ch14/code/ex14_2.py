"""14.2 节：平面两连杆、三连杆。

(1) 算例 14.2.1：2R 臂到达 (0.45, 0.35) m。几何法（余弦定理 + 两个方向角）与代数法（把 cos θ1、sin θ1 当作
    线性方程组的未知数）分别计算，结果相同，也与第 7 章牛顿法的结果相同（程序 14.1.1 已核对）。
(2) 数值上的细节：恰在外边界上（手臂伸直）的目标，arccos 写法因舍入把一部分判为“够不着”，
    式 (14.2.6) 的因式分解写法一个也不漏；手臂接近伸直时 θ2 对目标位置极其敏感（式 (14.2.7)），用差商核对。
(3) 算例 14.2.2：平面 3R 臂（加 L3 = 0.1 m 的工具）到达 (0.6, 0.05) m、工具朝下（φ = −90°）。
(4) 只给位置、不给朝向时的一族解：目标 (0.75, 0.10) m，工具朝向 φ 只能在一段范围内取值（腕点必须在 2R 的圆环内）。
(5) UR5e 的关节 2、3、4：手腕点 P56 在关节 2–4 的平面内的位置，与平面 3R 臂的公式一致。
"""
import math

import numpy as np

from _ik import H1, H2, L1, L2, W4, fk2r, fk3r, ik2r, ik2r_naive, ik3r, ur_fk, wrap
from bookout import out

l1, l2, l3 = 0.425, 0.392, 0.1

# ---------------------------------------------------------------- (1) 算例 14.2.1：两种方法
x, y = 0.45, 0.35
r = math.hypot(x, y)
c2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2)
beta = math.atan2(y, x)
psi = math.acos((l1 * l1 + r * r - l2 * l2) / (2 * l1 * r))     # 大臂与连线的夹角（余弦定理）
geo = [(beta - psi, math.acos(c2)), (beta + psi, -math.acos(c2))]   # 肘下、肘上
alg = []
for t2 in (math.acos(c2), -math.acos(c2)):
    k1, k2 = l1 + l2 * math.cos(t2), l2 * math.sin(t2)
    c1 = (k1 * x + k2 * y) / (k1 * k1 + k2 * k2)
    s1 = (k1 * y - k2 * x) / (k1 * k1 + k2 * k2)
    alg.append((math.atan2(s1, c1), t2))
lib = ik2r(x, y, l1, l2)
for g, a, b in zip(geo, alg, lib):
    assert abs(wrap(g[0] - a[0])) < 1e-12 and abs(g[1] - a[1]) < 1e-12
    assert abs(wrap(g[0] - b[0])) < 1e-12 and abs(g[1] - b[1]) < 1e-12
    assert np.linalg.norm(fk2r(g, l1, l2) - [x, y]) < 1e-12
k1d, k2d = l1 + l2 * math.cos(geo[0][1]), l2 * math.sin(geo[0][1])

# ---------------------------------------------------------------- (2) 数值精度
rng = np.random.default_rng(142)
N = 1000
fail_naive = fail_stable = 0
c_bad = None
for a in rng.uniform(-math.pi, math.pi, N):           # 恰在外边界上（手臂伸直）的目标
    p = (l1 + l2) * np.array([math.cos(a), math.sin(a)])
    if len(ik2r_naive(p[0], p[1], l1, l2)) == 0:
        fail_naive += 1
        c = (p[0] ** 2 + p[1] ** 2 - l1 * l1 - l2 * l2) / (2 * l1 * l2)
        c_bad = c_bad or repr(float(c))              # 舍入后略大于 1 的 cos θ2
    fail_stable += len(ik2r(p[0], p[1], l1, l2)) == 0
assert fail_stable == 0 and fail_naive > 0

# 手臂接近伸直时，目标沿径向的微小变化引起 θ2 的大幅变化：由 r² = l1² + l2² + 2 l1 l2 cos θ2（式 (14.2.1)），
# dθ2/dr = −r / (l1 l2 sin θ2)（式 (14.2.7)）。θ2 = 1° 时，目标沿径向内移 1 μm：
t2s = math.radians(1.0)
pS = fk2r((0.4, t2s), l1, l2)
rS = float(np.linalg.norm(pS))
dr = -1e-6                                             # 向内移 1 μm（θ2 = 1° 时离外边界约 62 μm）
pS2 = pS * (rS + dr) / rS
d_ik = ik2r(pS2[0], pS2[1], l1, l2)[0][1] - ik2r(pS[0], pS[1], l1, l2)[0][1]
d_formula = -rS * dr / (l1 * l2 * math.sin(t2s))
assert abs(d_ik - d_formula) < 0.03 * abs(d_formula)
t2m = math.radians(90)                                  # 对照：θ2 = 90° 时同样移动 1 μm
pM = fk2r((0.4, t2m), l1, l2)
rM = float(np.linalg.norm(pM))
d_mid = -rM * dr / (l1 * l2 * math.sin(t2m))

# ---------------------------------------------------------------- (3) 算例 14.2.2：平面 3R，给定位置与朝向
px, py, phi = 0.6, 0.05, math.radians(-90)
wx, wy = px - l3 * math.cos(phi), py - l3 * math.sin(phi)
s3 = ik3r(px, py, phi, l1, l2, l3)
assert len(s3) == 2
for s in s3:
    f = fk3r(s, l1, l2, l3)
    assert abs(f[0] - px) < 1e-12 and abs(f[1] - py) < 1e-12 and abs(wrap(f[2] - phi)) < 1e-12
s3d = [tuple(math.degrees(t) for t in s) for s in s3]

# ---------------------------------------------------------------- (4) 只给位置：工具朝向 φ 的可行范围
pB = np.array([0.75, 0.10])
rB = float(np.linalg.norm(pB))
# 腕点 w = p − l3 e(φ) 必须满足 |w| ≤ l1 + l2（内边界 0.033 m 这里不起作用）：|p|² + l3² − 2 l3 |p| cos(φ − β) ≤ (l1 + l2)²
bB = math.atan2(pB[1], pB[0])
cmin = (rB * rB + l3 * l3 - (l1 + l2) ** 2) / (2 * l3 * rB)
half = math.acos(cmin)
lo, hi = bB - half, bB + half
grid = np.linspace(-math.pi, math.pi, 7201)
ok = np.array([len(ik3r(pB[0], pB[1], f, l1, l2, l3)) > 0 for f in grid])
inside = np.array([abs(wrap(f - bB)) <= half for f in grid])
assert (ok == inside).all()

# ---------------------------------------------------------------- (5) UR5e 的关节 2、3、4 构成平面 3R 臂
worst = 0.0
for _ in range(1000):
    t2, t3, t4 = rng.uniform(-math.pi, math.pi, 3)
    T = ur_fk([0, t2, t3, t4, 0, 0])
    pw = T[:3, 3] - W4 * T[:3, 1]                       # 手腕点 P56
    # 侧视（沿 −y 方向看）：水平坐标 u = −x，高度 z；关节角按 −θ 计（关节轴朝 −y）；第三段零位时竖直向下
    a1, a2, a3 = -t2, -t2 - t3, -t2 - t3 - t4 - math.pi / 2
    u = L1 * math.cos(a1) + L2 * math.cos(a2) + H2 * math.cos(a3)
    z = H1 + L1 * math.sin(a1) + L2 * math.sin(a2) + H2 * math.sin(a3)
    worst = max(worst, abs(-pw[0] - u), abs(pw[2] - z))
assert worst < 1e-12

out(x=x, y=y, r=r, c2=c2, beta_deg=math.degrees(beta), psi_deg=math.degrees(psi), t2_deg=math.degrees(math.acos(c2)),
    k1=k1d, k2=k2d,
    geo1=f"({math.degrees(geo[0][0]):.2f}°, {math.degrees(geo[0][1]):.2f}°)",
    geo2=f"({math.degrees(geo[1][0]):.2f}°, {math.degrees(geo[1][1]):.2f}°)",
    t1d=math.degrees(geo[0][0]), t1u=math.degrees(geo[1][0]),
    N=N, fail_naive=fail_naive, c_bad=c_bad, fail_pct=100 * fail_naive / N,
    d_ik_deg=math.degrees(abs(d_ik)), d_mid_deg=math.degrees(abs(d_mid)), d_ratio=abs(d_ik / d_mid), rS=rS,
    wx=wx, wy=wy, s3a=f"({s3d[0][0]:.2f}°, {s3d[0][1]:.2f}°, {s3d[0][2]:.2f}°)", s3b=f"({s3d[1][0]:.2f}°, {s3d[1][1]:.2f}°, {s3d[1][2]:.2f}°)",
    rB=rB, phi_lo=math.degrees(lo), phi_hi=math.degrees(hi), phi_span=math.degrees(2 * half), bB_deg=math.degrees(bB),
    ur_planar=worst)
