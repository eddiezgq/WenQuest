"""1.3 节：复利与数 e；药物在血液中按指数规律衰减；最速下降找“谷底”的几步。"""
import math

from bookout import out

# 年利率 100%，一年结息 n 次：(1 + 1/n)^n
for n in (1, 2, 12, 365, 8760):
    out(**{f"c{n}": (1 + 1 / n) ** n})
out(e=math.e)

# 药物：血药浓度 C(t) = C0 e^(−kt)，半衰期 6 h；12 h 后剩几成，衰减速率与浓度成正比
k = math.log(2) / 6
out(k=k, left12=math.exp(-k * 12), left24=math.exp(-k * 24))

# 一维“下山”：f(x) = (x − 3)² + 1，从 x = 0 出发，每步 x ← x − 0.25 f'(x)
x, path = 0.0, []
for _ in range(6):
    path.append(x)
    x = x - 0.25 * 2 * (x - 3)
path.append(x)
out(gd=", ".join(f"{v:.4g}" for v in path))
