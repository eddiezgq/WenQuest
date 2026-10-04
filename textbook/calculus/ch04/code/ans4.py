"""本章“部分习题答案”中的数值。"""
import json
import math
from pathlib import Path

from bookout import out


def bisect(f, a, b, n=200):
    fa = f(a)
    for _ in range(n):
        m = (a + b) / 2
        if (f(m) > 0) == (fa > 0):
            a, fa = m, f(m)
        else:
            b = m
    return (a + b) / 2


# 习题 4.3.5：tanh(t/8) = 0.99
out(e435=8 * math.atanh(0.99))
# 习题 4.3.6：C/√(R − r) · v ≤ π，C = ½√(2R/(l₁l₂))，l₁、l₂ 取自 UR5e 模型
e = json.loads((Path(__file__).resolve().parents[2] / "models" / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))
js = {j["name"]: j for j in e["robot"]["joints"]}
l1, l2 = js["elbow_joint"]["origin"]["xyz"][2], js["wrist_1_joint"]["origin"]["xyz"][2]
R = l1 + l2
C = 0.5 * math.sqrt(2 * R / (l1 * l2))
out(e436_mm=(C * 0.1 / math.pi) ** 2 * 1000)
# 习题 4.4.8：√x 在 a = 0.01 处，ε = 1e−3 的最大 δ（两侧中较小者）与证明给出的 δ = min(a, √a ε)
a, eps = 0.01, 1e-3
dmax = min(a - (math.sqrt(a) - eps) ** 2, (math.sqrt(a) + eps) ** 2 - a)
out(e448_max=dmax, e448_proof=min(a, math.sqrt(a) * eps))
# 习题 4.4.9：d = 2√(ρ² − x²)，ρ = 50，x₀ = 40，|d − d₀| < 0.01 的最大 δ
rho, x0 = 50.0, 40.0
d = lambda x: 2 * math.sqrt(rho * rho - x * x)
d0 = d(x0)
right = bisect(lambda t: abs(d(x0 + t) - d0) - 0.01, 0.0, 1.0)
left = bisect(lambda t: abs(d(x0 - t) - d0) - 0.01, 0.0, 1.0)
out(e449=min(right, left))
# 习题 4.5.7：轮距 0.5 m，左 0.95、右 1.05 m/s，T = 20 ms
v, w, T = 1.0, (1.05 - 0.95) / 0.5, 0.02
out(e457_w=w, e457_dx=v / w * math.sin(w * T) * 1000, e457_dy=v / w * 2 * math.sin(w * T / 2) ** 2 * 1000)
# 习题 4.6.5：sin θ ≈ θ 与 cos θ ≈ 1 相对误差 2% 的角度
t_sin = bisect(lambda t: t / math.sin(t) - 1.02, 0.01, 1.5)
t_cos = bisect(lambda t: 1 / math.cos(t) - 1.02, 0.01, 1.5)      # 用 1 代替 cos θ 的相对误差 (1 − cos θ)/cos θ
out(e465_sin=math.degrees(t_sin), e465_cos=math.degrees(t_cos))
# 习题 4.7.6：x² − 1e6 x + 1 = 0
b = 1e6
small_naive = (b - math.sqrt(b * b - 4)) / 2
small_good = 2 / (b + math.sqrt(b * b - 4))
out(e476_naive=small_naive, e476_good=small_good, e476_rel=abs(small_naive - small_good) / small_good)
