"""4.1 节：函数极限的直观意义——AGV 的平均速度 v̄(h)；sin x / x 与 (1 − cos x)/x² 的数值表；
sin(π/x) 在 x = 1/n 处的“假象”；(x² − 1)/(x − 1) 在 x = 1 处无定义而极限存在。"""
import math

from bookout import out


def sci(v):
    m, e = f"{v:.2e}".split("e")
    return f"${m}\\times 10^{{{int(e)}}}$"


# AGV：x(t) = 0.25 t²，[2, 2 + h] 上的平均速度
vbar = lambda h: (0.25 * (2 + h) ** 2 - 1) / h
hs = [0.5, 0.1, 0.01, -0.01, -0.1, -0.5]
out(vbar_tab="\n".join(f"| {h:g} | {vbar(h):.4f} |" for h in hs))

# sin x / x 与 (1 − cos x)/x²（x 不太小，不受舍入影响）
rows = []
for x in (1.0, 0.5, 0.1, 0.01, 0.001):
    rows.append(f"| {x:g} | {math.sin(x) / x:.10f} | {(1 - math.cos(x)) / x**2:.10f} |")
out(sinc_tab="\n".join(rows))

# sin(π/x)：x = 1/n 时全为 0（舍入后约 1e−15），x = 2/(4n + 1) 时全为 1
z = [abs(math.sin(math.pi * n)) for n in range(1, 11)]
o = [math.sin(math.pi * (4 * n + 1) / 2) for n in range(1, 11)]
out(sinpi_zero_max=max(z), sinpi_one_min=min(o))

# (x² − 1)/(x − 1)
g = lambda x: (x * x - 1) / (x - 1)
out(g09=g(0.9), g0999=g(0.999), g1001=g(1.001))
