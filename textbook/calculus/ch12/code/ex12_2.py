"""12.2 节：求和记号与黎曼和——Σk、Σk²、Σk³ 的公式核对；∫₀¹ x³ dx 的左、右、中点和，误差随 n 的变化（1/n 与 1/n²）。"""
from bookout import out

n = 100
out(s1=sum(range(1, n + 1)), s1f=n * (n + 1) // 2, s2=sum(k * k for k in range(1, n + 1)), s2f=n * (n + 1) * (2 * n + 1) // 6,
    s3=sum(k ** 3 for k in range(1, n + 1)), s3f=(n * (n + 1) // 2) ** 2)
f = lambda x: x ** 3
rows = []
for n in (10, 20, 40, 80, 160):
    h = 1 / n
    L = sum(f(k * h) for k in range(n)) * h
    R = sum(f(k * h) for k in range(1, n + 1)) * h
    M = sum(f((k + 0.5) * h) for k in range(n)) * h
    rows.append(f"| {n} | {abs(L - 0.25):.3e} | {abs(R - 0.25):.3e} | {abs(M - 0.25):.3e} | {abs(M - 0.25) * n * n:.4f} |")
out(cube_tab="\n".join(rows))
