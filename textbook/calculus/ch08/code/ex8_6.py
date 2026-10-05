"""8.6 节：自动微分——对偶数（前向模式）求两节连杆末端坐标对关节角的导数、腕心距离 r(θ₂) 的导数；
对一个“程序”（牛顿迭代求平方根）求导；反向模式一次得到目标函数对所有关节角的梯度，与有限差分比较。"""
import math

from _ad import Dual, Var, dcos, dsin, dsqrt, vcos, vsin
from _traj import ur5e_links
from bookout import out

l1, l2 = ur5e_links()
t1, t2 = math.radians(30), math.radians(60)

# 前向模式：对 θ₂ 求导，令 θ₂ = t2 + 1·ε
th2 = Dual(t2, 1.0)
r = dsqrt(l1 * l1 + l2 * l2 + 2 * l1 * l2 * dcos(th2))
exact = -l1 * l2 * math.sin(t2) / math.sqrt(l1 * l1 + l2 * l2 + 2 * l1 * l2 * math.cos(t2))
out(ad_r=r.b * 1000, exact_r=exact * 1000, ad_err=abs(r.b - exact))
# 雅可比矩阵：两次前向传播，每次对一个关节角求导
def fk(a, b):
    return l1 * dcos(a) + l2 * dcos(a + b), l1 * dsin(a) + l2 * dsin(a + b)
x1, y1 = fk(Dual(t1, 1), Dual(t2, 0))
x2, y2 = fk(Dual(t1, 0), Dual(t2, 1))
Jex = [[-l1 * math.sin(t1) - l2 * math.sin(t1 + t2), -l2 * math.sin(t1 + t2)],
       [l1 * math.cos(t1) + l2 * math.cos(t1 + t2), l2 * math.cos(t1 + t2)]]
Jad = [[x1.b, x2.b], [y1.b, y2.b]]
out(jac="\n".join(f"| {Jad[i][0]:.12f} | {Jad[i][1]:.12f} | {Jex[i][0]:.12f} | {Jex[i][1]:.12f} |" for i in range(2)),
    jac_err=max(abs(Jad[i][k] - Jex[i][k]) for i in range(2) for k in range(2)))

# 对“程序”求导：用牛顿迭代 x ← (x + a/x)/2 算 √a，迭代 6 次；对 a 求导应得 1/(2√a)
a = Dual(2.0, 1.0)
x = Dual(1.0, 0.0)
for _ in range(6):
    x = (x + a / x) * 0.5
out(prog_val=x.a, prog_der=x.b, prog_true=1 / (2 * math.sqrt(2)))

# 反向模式：L(θ₁, θ₂) = |p(θ) − p*|²，一次反向传播得到 ∂L/∂θ₁、∂L/∂θ₂
tx, ty = 0.45, 0.35
A, Bv = Var(t1), Var(t2)
X = l1 * vcos(A) + l2 * vcos(A + Bv)
Y = l1 * vsin(A) + l2 * vsin(A + Bv)
L = (X - tx) * (X - tx) + (Y - ty) * (Y - ty)
L.backward()
def Lf(a, b):
    x = l1 * math.cos(a) + l2 * math.cos(a + b)
    y = l1 * math.sin(a) + l2 * math.sin(a + b)
    return (x - tx) ** 2 + (y - ty) ** 2
h = 1e-6
g1 = (Lf(t1 + h, t2) - Lf(t1 - h, t2)) / (2 * h)
g2 = (Lf(t1, t2 + h) - Lf(t1, t2 - h)) / (2 * h)
out(rev_g1=A.g, rev_g2=Bv.g, fd_g1=g1, fd_g2=g2, rev_nodes=Var.count)
