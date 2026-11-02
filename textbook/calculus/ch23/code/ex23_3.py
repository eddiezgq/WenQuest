"""23.3 节：正项级数的判别法。
(1) p 级数与积分判别法：Σ1/k² 的部分和、用积分估计余项，与 π²/6 比较；
(2) 数字控制器的单位脉冲响应 h_n = n rⁿ（离散时间系统的重根极点 r）：比值判别法判断 Σ|h_n| 收敛（有界输入有界输出），
    求和 r/(1 − r)²，以及 Σh_n²（脉冲响应的能量）。"""
import math

from bookout import out

zeta2 = math.pi ** 2 / 6
rows = []
for n in (10, 100, 1000, 10000):
    S = math.fsum(1 / k ** 2 for k in range(1, n + 1))
    lo, hi = S + 1 / (n + 1), S + 1 / n                    # 余项在 ∫_{n+1}^∞ 与 ∫_n^∞ 之间
    mid = S + 1 / (n + 0.5)
    rows.append(f"| {n} | {S:.8f} | {zeta2 - S:.2e} | {lo:.8f} | {hi:.8f} | {abs(mid - zeta2):.1e} |")
out(z_tab="\n".join(rows), z_val=zeta2)
# 只用部分和、要准到 6 位小数（误差 < 5e-7）需要的项数
out(z_n6=math.ceil(1 / 5e-7))
# 脉冲响应
for r in (0.9, 0.99):
    s1 = math.fsum(n * r ** n for n in range(1, 20000))
    s2 = math.fsum((n * r ** n) ** 2 for n in range(1, 20000))
    tag = f"{round(r * 100)}"
    out(**{f"ir_s1_{tag}": s1, f"ir_formula_{tag}": r / (1 - r) ** 2, f"ir_s2_{tag}": s2,
           f"ir_s2f_{tag}": r * r * (1 + r * r) / (1 - r * r) ** 3, f"ir_peak_{tag}": max(n * r ** n for n in range(1, 2000)),
           f"ir_npeak_{tag}": max(range(1, 2000), key=lambda n: n * r ** n)})
# 比值 (n+1)/n · r → r
out(ir_ratio_10=11 / 10 * 0.9, ir_ratio_100=101 / 100 * 0.9)
