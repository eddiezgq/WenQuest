"""18.1 节：达布上和与下和——f(x) = x² 在 [0, 1] 上 n 等分的上和、下和与 U − L = 1/n；
AGV 制动：速度单调减小，按采样间隔 Δt 得到制动距离的有保证的上下界，U − L = (v₀ − v_end)Δt。"""
import math

from scipy import integrate

from bookout import out

rows = []
for n in (4, 10, 100, 1000):
    h = 1 / n
    L = sum((k * h) ** 2 * h for k in range(n))
    U = sum(((k + 1) * h) ** 2 * h for k in range(n))
    rows.append(f"| {n} | {L:.6f} | {U:.6f} | {U - L:.6f} |")
out(sq_tab="\n".join(rows))
# AGV 制动：v(t) = v0 (1 − t/T)^1.5，v0 = 1.5 m/s，T = 1.2 s（单调减小）
v0, T = 1.5, 1.2
v = lambda t: v0 * max(1 - t / T, 0) ** 1.5
D = integrate.quad(v, 0, T)[0]
rows = []
for dt in (0.2, 0.1, 0.05, 0.01):
    n = round(T / dt)
    L = sum(v((k + 1) * dt) * dt for k in range(n))      # 递减：右端点给下和
    U = sum(v(k * dt) * dt for k in range(n))
    rows.append(f"| {dt:g} | {n + 1} | {L * 100:.2f} | {U * 100:.2f} | {(U - L) * 100:.2f} |")
out(v0=v0, T=T, D=D * 100, brake_tab="\n".join(rows))
