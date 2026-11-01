"""10.5 节的计算：

算例 10.5.1  分拣线的溜槽：5.0 kg 的包裹从溜槽顶端由静止滑下，槽长 3.0 m、倾角 30°，μ_k = 0.30。
            重力势能减少多少，摩擦生热多少，到底端的动能和速度（图 10.5.1）。
算例 10.5.2  满载 AGV（800 kg）以 2.0 m/s 紧急制动停下：动能全部变成制动器的内能。制动盘共 0.80 kg 钢，
            比热容 460 J/(kg·K)（第 22 章），只算制动盘，温度升高多少？若每小时紧急制动 20 次而且来不及散热呢？
"""
import math

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 10.5.1
m, L, th, mu = 5.0, 3.0, math.radians(30.0), 0.30
dU = m * g * L * math.sin(th)
Q = mu * m * g * math.cos(th) * L
K = dU - Q
v = math.sqrt(2 * K / m)
a = g * (math.sin(th) - mu * math.cos(th))
assert abs(v - math.sqrt(2 * a * L)) < 1e-12                    # 与牛顿第二定律的结果一致
out(m=m, L=L, th=30.0, mu=mu, dU=dU, Q=Q, K=K, v=v, v_nofric=math.sqrt(2 * g * L * math.sin(th)), Q_frac=Q / dU)

# ---- 算例 10.5.2
M, v0, mdisc, c = 800.0, 2.0, 0.80, 460.0
E = 0.5 * M * v0 ** 2
dT = E / (mdisc * c)
out(M=M, v0=v0, E=E, mdisc=mdisc, c=c, dT=dT, dT20=20 * dT)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.8))
bars = [(T("顶端：势能", "top: potential"), 0, dU, d.VA), (T("摩擦生热", "heat from friction"), K, Q, d.MUTED),
        (T("底端：动能", "bottom: kinetic"), 0, K, d.VR)]
for i, (name, left, w, col) in enumerate(bars):
    ax.barh(-i, w, left=left, color=col, height=0.55, alpha=0.85)
    ax.text(left + w + 1.2, -i, f"{w:.1f} J", va="center", fontsize=9)
ax.set_yticks([0, -1, -2]); ax.set_yticklabels([b_[0] for b_ in bars], fontsize=9)
ax.plot([K, K], [-0.3, -2.3], color=d.MUTED, lw=0.6, ls=":")
ax.set_xlim(0, dU * 1.25); ax.set_xlabel(T("能量 / J", "energy / J")); d.spines(ax)
figure(fig, "fig10_5_1")
