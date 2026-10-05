"""10.2 节：极值——关节阶跃响应的峰值时刻 t_p = π/ω_d 与超调量 M_p = e^{−ζπ/√(1−ζ²)}，与逐点计算的最大值比较；
由超调要求反求阻尼比；一阶、二阶判别法的核对。"""
import math

from bookout import out

wn = 10.0
rows = []
for z in (0.3, 0.5, 0.6, 0.7, 0.8, 0.9):
    s = math.sqrt(1 - z * z)
    wd = wn * s
    q = lambda t: 1 - math.exp(-z * wn * t) * (math.cos(wd * t) + z / s * math.sin(wd * t))
    tp = math.pi / wd
    Mp = math.exp(-z * math.pi / s)
    N = 20000
    tm = max((k * 2.0 / N for k in range(N + 1)), key=q)
    rows.append(f"| {z} | {tp:.4f} | {tm:.4f} | {Mp * 100:.2f} | {(q(tm) - 1) * 100:.2f} |")
out(peak_tab="\n".join(rows))
# 要求超调不超过 5%：ζ = −ln M / √(π² + ln² M)
M = 0.05
out(z_req=-math.log(M) / math.sqrt(math.pi ** 2 + math.log(M) ** 2))
# ζ = 0.6 时 q″(t_p) < 0：q″ = (ωₙ²/ω_d)e^{−ζωₙt}(ω_d cos ω_d t − ζωₙ sin ω_d t)
z = 0.6
wd = wn * math.sqrt(1 - z * z)
tp = math.pi / wd
out(qpp_tp=(wn ** 2 / wd) * math.exp(-z * wn * tp) * (wd * math.cos(wd * tp) - z * wn * math.sin(wd * tp)), tp6=tp,
    Mp6=math.exp(-z * math.pi / math.sqrt(1 - z * z)))
