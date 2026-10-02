"""7.5 节：电机—减速器—上臂的链式法则；用 SymPy 核对几个复合函数的导数；2^x 在 0 点的导数。"""
import math

import sympy as sp

from _traj import quintic, ur5e_links
from bookout import out

l1, l2 = ur5e_links()
n_motor = 3000.0                      # r/min
N = 101                               # 减速比（谐波减速器常用值）
w_m = n_motor * 2 * math.pi / 60      # rad/s
w_j = w_m / N
th = math.radians(30)
vy = l1 * math.cos(th) * w_j          # 肘关节中心的竖直速度 dy/dt = l1 cos θ · dθ/dt
out(l1=l1, l2=l2, w_m=w_m, w_j=w_j, w_j_deg=math.degrees(w_j), vy=vy, dydth=l1 * math.cos(th))

# 五次多项式运动（T = 2 s，Δ = 90°）中 t = 0.5 s 时肘关节中心的竖直速度
T, D = 2.0, math.pi / 2
th5, w5, _, _ = quintic(0.5, T, D)
out(th5_deg=math.degrees(float(th5)), w5=float(w5), vy5=l1 * math.cos(float(th5)) * float(w5))

# 用 SymPy 核对算例 7.5.1–7.5.3
x = sp.symbols("x")
checks = {
    "d1": (sp.sin(x**2), 2 * x * sp.cos(x**2)),
    "d2": ((1 + x**2) ** 10, 20 * x * (1 + x**2) ** 9),
    "d3": (sp.exp(-x**2 / 2), -x * sp.exp(-x**2 / 2)),
    "d4": (sp.sqrt(1 + sp.sin(x) ** 2), sp.sin(x) * sp.cos(x) / sp.sqrt(1 + sp.sin(x) ** 2)),
}
for k, (f, d) in checks.items():
    assert sp.simplify(sp.diff(f, x) - d) == 0, k
out(n_checked=len(checks), d2x_at_0=float(sp.diff(2**x, x).subs(x, 0)), ln2=math.log(2))
