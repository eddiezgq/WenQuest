"""19.6 节：欧拉法。y′ = x − y 的误差随步长的变化（一阶收敛）；y′ = y 的欧拉解 (1 + h)^(1/h) → e；
y′ = −y/τ 的稳定性（RE 40 空载 τ ≈ 4.26 ms，步长 1、5、10 ms）；用欧拉法算水箱流空的时间。"""
import math

from bookout import out


def euler(f, x0, y0, x1, h):
    n = round((x1 - x0) / h)
    x, y = x0, y0
    for _ in range(n):
        y += h * f(x, y)
        x += h
    return y


f = lambda x, y: x - y
exact = 2 - 1 + 3 * math.exp(-2)          # y(0) = 2 时 y(2)
rows, prev = [], None
for h in (0.2, 0.1, 0.05, 0.025, 0.0125):
    e = abs(euler(f, 0, 2.0, 2, h) - exact)
    rows.append(f"| {h:g} | {round(2 / h)} | {euler(f, 0, 2.0, 2, h):.6f} | {e:.2e} | {'—' if prev is None else f'{prev / e:.2f}'} |")
    prev = e
out(err_tab="\n".join(rows), err_exact=exact)
# y′ = y，y(0) = 1，欧拉法到 x = 1：(1 + h)^(1/h)
out(e_tab="\n".join(f"| {h:g} | {(1 + h) ** round(1 / h):.6f} | {math.e - (1 + h) ** round(1 / h):.2e} |" for h in (0.1, 0.01, 0.001, 0.0001)))

# 稳定性：电机 ω′ = (ω∞ − ω)/τ，从 0 启动，看第 1～8 步
tau = 1.13 * 137e-7 / 60.3e-3 ** 2
w_inf = 48 / 60.3e-3
st = {}
for hms in (1.0, 5.0, 10.0):
    h = hms / 1000
    w, seq = 0.0, []
    for _ in range(8):
        w += h * (w_inf - w) / tau
        seq.append(w)
    st[hms] = seq
    out(**{f"st_{int(hms)}_r": 1 - h / tau, f"st_{int(hms)}_w8": seq[-1]})
out(st_tau=tau * 1000, st_2tau=2 * tau * 1000,
    st_tab="\n".join(f"| {k + 1} | {st[1.0][k]:.0f} | {st[5.0][k]:.0f} | {st[10.0][k]:.0f} |" for k in range(6)))

# 水箱：欧拉法算流空时间（第一次 h ≤ 0 的时刻）
c = 0.6 * math.pi * 4e-3 ** 2 / 4 * math.sqrt(2 * 9.81) / 0.03
Te = 2 * math.sqrt(0.2) / c
rows = []
for h in (100.0, 50.0, 10.0, 1.0):
    t, y = 0.0, 0.2
    while y > 0:
        y += -h * c * math.sqrt(y)
        t += h
    rows.append(f"| {h:g} | {t:.0f} | {t - Te:+.0f} |")
out(tk_tab="\n".join(rows), tk_Te=Te)
