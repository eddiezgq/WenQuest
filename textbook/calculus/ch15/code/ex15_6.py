"""15.6 节：无界函数的反常积分——∫₀¹ dx/√x 用中点公式收敛很慢（误差 ∝ h^{1/2}），换元 x = u² 后变成普通积分；
∫₀¹ ln x dx = −1；摆的四分之一周期积分 ∫₀^{θ₀} dθ/√(cos θ − cos θ₀) 在上端无界：直接用中点公式与换元后用高斯求积的比较。"""
import math

from scipy import special

from _quad import gauss
from bookout import T, out


def mid(f, a, b, n):
    h = (b - a) / n
    return sum(f(a + (k + 0.5) * h) for k in range(n)) * h


rows = []
for n in (10, 100, 1000, 10000):
    e = mid(lambda x: 1 / math.sqrt(x), 0, 1, n) - 2
    rows.append(f"| {n} | {e:.3e} | {e * math.sqrt(n):.4f} |")
out(sing_tab="\n".join(rows), sub_gauss=gauss(lambda u: 2.0, 0, 1, 2), lnx=mid(math.log, 0, 1, 100000))
# 摆：θ₀ = 90°，准确值 √2·K(sin 45°)；（T = 4√(L/2g)·I，I = √2 K(k)）
t0 = math.pi / 2
k = math.sin(t0 / 2)
I_ex = math.sqrt(2) * special.ellipk(k * k)
g = lambda th: 1 / math.sqrt(max(math.cos(th) - math.cos(t0), 1e-300))
rows = []
for n in (10, 100, 1000, 10000):
    rows.append(f"| {T('中点公式，', 'midpoint rule, ')}{n}{T(' 段', ' subintervals')} | {n} | {abs(mid(g, 0, t0, n) - I_ex) / I_ex:.1e} |")
for n in (4, 8):
    v = math.sqrt(2) * gauss(lambda p: 1 / math.sqrt(1 - k * k * math.sin(p) ** 2), 0, math.pi / 2, n)
    rows.append(f"| {T('换元后高斯，', 'Gauss after substitution, ')}{n}{T(' 点', ' points')} | {n} | {abs(v - I_ex) / I_ex:.1e} |")
out(pend_tab="\n".join(rows), I_ex=I_ex)
