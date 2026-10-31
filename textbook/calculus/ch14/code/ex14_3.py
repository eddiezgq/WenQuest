"""14.3 节：三角代换——卧式圆柱水箱的液位与水量：V(h) = L[r² arccos((r − h)/r) − (r − h)√(2rh − h²)]，
数值积分核对；反求 25%、50%、75% 水量对应的液位；∫dx/√(x² + 1) = arsinh x 的核对。"""
import math

from bookout import out

r, L = 0.15, 0.6        # 半径、长度（m）


def V(h):
    return L * (r * r * math.acos((r - h) / r) - (r - h) * math.sqrt(max(2 * r * h - h * h, 0.0)))


def V_num(h, n=20000):
    """把水看成一层层厚 dy 的薄片：宽 2√(r² − y²)，y 从 −r 积到 h − r。"""
    a, bb = -r, h - r
    d = (bb - a) / n
    return L * sum(2 * math.sqrt(max(r * r - (a + (k + 0.5) * d) ** 2, 0.0)) for k in range(n)) * d


full = math.pi * r * r * L
rows = []
for h in (0.03, 0.075, 0.15, 0.225, 0.27):
    rows.append(f"| {h * 100:.1f} | {h / (2 * r) * 100:.0f} | {V(h) * 1000:.3f} | {V_num(h) * 1000:.3f} | {V(h) / full * 100:.1f} |")
out(tank_tab="\n".join(rows), full_L=full * 1000)


def level(frac):
    lo, hi = 0.0, 2 * r
    for _ in range(80):
        m = (lo + hi) / 2
        if V(m) < frac * full:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


out(h25=level(0.25) * 100, h50=level(0.5) * 100, h75=level(0.75) * 100)
n = 200000
d = 2 / n
out(asinh_num=sum(1 / math.sqrt(((k + 0.5) * d) ** 2 + 1) for k in range(n)) * d, asinh2=math.asinh(2))
