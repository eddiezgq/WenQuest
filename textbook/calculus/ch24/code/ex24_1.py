"""24.1 节：函数项级数与幂级数；收敛半径。
(1) 几个幂级数的收敛半径：比值公式与根值公式（柯西–阿达马）；
(2) 1/(1 + x²) = 1 − x² + x⁴ − …：在实轴上处处光滑，级数却只在 |x| < 1 收敛（复平面上 ±i 是奇点）；
(3) arctan x 的级数在不同 x 处要多少项才能使误差小于 1e-7——离收敛半径越近越慢。"""
import math

from bookout import T, out

# (1) 收敛半径：a_n 的比值与 n 次根的数值（n = 50, 200）
rows = []
cases = [("1", lambda n: 1.0, "1"), ("\\frac1n", lambda n: 1 / n, "1"), ("\\frac1{n^2}", lambda n: 1 / n ** 2, "1"),
         ("n!", lambda n: math.lgamma(n + 1), "0"), ("\\frac1{n!}", lambda n: -math.lgamma(n + 1), "∞"),
         ("\\frac{2^n}{n}", lambda n: n * math.log(2) - math.log(n), "1/2")]
for name, a, R in cases:
    vals = []
    for n in (50, 200):
        if "!" in name or "2^n" in name:
            la = a(n)
        else:
            la = math.log(a(n))
        vals.append(math.exp(-la / n))              # 1 / ⁿ√|a_n|
    rows.append(f"| ${name}$ | {vals[0]:.3g} | {vals[1]:.3g} | {R} |")
out(r_tab="\n".join(rows))
# (2) 1/(1+x²) 的部分和在 x = 0.9、1.1
for x in (0.5, 0.9, 1.1):
    tag = f"{round(x * 10)}"
    S = [sum((-x * x) ** k for k in range(n + 1)) for n in (5, 10, 20, 40)]
    out(**{f"g_{tag}_{n}": s for n, s in zip((5, 10, 20, 40), S)}, **{f"g_{tag}_true": 1 / (1 + x * x)})
# (3) arctan 级数：误差 < 1e-7 所需项数
rows = []
for x in (0.1, math.tan(math.pi / 12), 0.5, 0.9, 0.99, 1.0):
    n, S = 0, 0.0
    while True:
        S += (-1) ** n * x ** (2 * n + 1) / (2 * n + 1)
        n += 1
        if abs(S - math.atan(x)) < 1e-7 or n > 10 ** 7:
            break
    rows.append(f"| {x:.4g} | {n} |" if abs(x - math.tan(math.pi / 12)) > 1e-9 else f"| tan 15° ≈ {x:.3f} | {n} |")
out(at_tab="\n".join(rows))
