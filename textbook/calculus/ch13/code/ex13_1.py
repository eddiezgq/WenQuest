"""13.1 节：变上限积分——Φ(x) = ∫₀ˣ e^{−t²} dt 的值与数值导数（核对 Φ' = f）；被积函数有跳跃时 Φ 出现折角；
AGV 的累计里程 s(t) = ∫₀ᵗ v 及其导数；上限为函数时的求导 d/dx ∫₀^{x²} sin t dt = 2x sin x²。"""
import math

from _agv import T, v
from bookout import out

f = lambda t: math.exp(-t * t)


def Phi(x, n=20000):
    """中点和计算 ∫₀ˣ e^{−t²} dt。"""
    h = x / n
    return sum(f((k + 0.5) * h) for k in range(n)) * h


rows = []
for x in (0.5, 1.0, 1.5, 2.0):
    h = 1e-3
    d = (Phi(x + h) - Phi(x - h)) / (2 * h)
    rows.append(f"| {x:.1f} | {Phi(x):.6f} | {d:.6f} | {f(x):.6f} |")
out(phi_tab="\n".join(rows), phi_inf=math.sqrt(math.pi) / 2, phi1=0.5 * math.sqrt(math.pi) * math.erf(1.0))

# 阶跃：f = 1（t < 1），f = 2（t ≥ 1）。Φ 在 x = 1 处的左、右导数
g = lambda t: 1.0 if t < 1 else 2.0
G = lambda x: x if x < 1 else 1 + 2 * (x - 1)
h = 1e-6
out(step_left=(G(1) - G(1 - h)) / h, step_right=(G(1 + h) - G(1)) / h)


# AGV 累计里程（解析式），与速度比较
def s(t):
    a, vm = 0.5, 1.2
    ta = vm / a
    tc = T - 2 * ta
    if t <= ta:
        return a * t * t / 2
    if t <= ta + tc:
        return vm * ta / 2 + vm * (t - ta)
    return 10 - a * (T - t) ** 2 / 2


rows = []
for t in (1.0, 4.0, 9.5):
    h = 1e-5
    rows.append(f"| {t:.1f} | {s(t):.4f} | {(s(t + h) - s(t - h)) / (2 * h):.4f} | {v(t):.4f} |")
out(agv_tab="\n".join(rows), T=T)

# 上限为 x²
Gs = lambda x: 1 - math.cos(x * x)          # ∫₀^{x²} sin t dt
x0 = 1.2
h = 1e-5
out(chain_num=(Gs(x0 + h) - Gs(x0 - h)) / (2 * h), chain_formula=2 * x0 * math.sin(x0 * x0))
