"""7.4 节：非易失存储器概览。

算例 7.4.1  机器人每隔 interval 秒把里程与标定计数记一次到片上闪存，每个存储块擦写寿命 endurance 次（教学设定）。
            三种做法的寿命：(a) 总写同一个地址（每次都要擦整块）；(b) 在一块里顺着往后记，记满一块才擦一次；
            (c) 再把 sectors 块轮流使用（磨损均衡）。要用够 years 年需要几块。
图 7.4.1    浮栅存储管的剖面：控制栅、浮栅、隧穿氧化层。
"""
import math

from bookout import T, figure, out, style
import _draw as d
from mos import P

q = P["problems"]["p74"]
dt, E, n, S, Y = q["interval_s"], q["endurance"], q["entries_per_sector"], q["sectors"], q["years"]
year = 365.25 * 24 * 3600
life_a = E * dt
life_b = E * n * dt
life_c = E * n * S * dt
need = math.ceil(Y * year / life_b)
out(interval_s=dt, endurance=E, entries=n, sectors=S, years=Y, life_a_h=life_a / 3600, life_b_d=life_b / 86400,
    life_c_y=life_c / year, need=need, writes_10y=Y * year / dt)

plt = style()
import matplotlib.patches as mp  # noqa: E402
fig, ax = plt.subplots(figsize=(6.4, 3.0))
ax.add_patch(mp.Rectangle((0, 0), 8, 1.2, color="#e8ecef"))
ax.text(4, 0.35, T("p 型衬底", "p-type substrate"), ha="center", fontsize=9.5, color=d.MUTED)
for x, lab in ((0.6, "n+"), (6.0, "n+")):
    ax.add_patch(mp.Rectangle((x, 0.75), 1.4, 0.45, color="#9cc3e6"))
    ax.text(x + 0.7, 0.97, lab, ha="center", va="center", fontsize=9)
ax.text(1.3, 0.5, T("源", "source"), ha="center", fontsize=9); ax.text(6.7, 0.5, T("漏", "drain"), ha="center", fontsize=9)
ax.add_patch(mp.Rectangle((2.0, 1.2), 4.0, 0.12, color="#f2d9a6"))
ax.add_patch(mp.Rectangle((2.0, 1.32), 4.0, 0.45, color=d.LOAD, alpha=0.8))
ax.add_patch(mp.Rectangle((2.0, 1.77), 4.0, 0.22, color="#f2d9a6"))
ax.add_patch(mp.Rectangle((2.0, 1.99), 4.0, 0.5, color=d.NMOS, alpha=0.8))
ax.text(4.0, 2.24, T("控制栅", "control gate"), ha="center", va="center", fontsize=9.5, color="white")
ax.text(4.0, 1.54, T("浮栅（存电荷）", "floating gate (stores charge)"), ha="center", va="center", fontsize=9.5)
ax.annotate(T("隧穿氧化层（很薄）", "tunnel oxide (thin)"), xy=(6.0, 1.26), xytext=(6.4, 1.75), fontsize=9,
            arrowprops=dict(arrowstyle="->", lw=0.8))
ax.annotate(T("层间介质", "inter-poly dielectric"), xy=(2.0, 1.88), xytext=(-0.2, 2.35), fontsize=9,
            arrowprops=dict(arrowstyle="->", lw=0.8))
for x in (3.0, 3.6, 4.2, 4.8):
    ax.annotate("", xy=(x, 1.36), xytext=(x, 1.08), arrowprops=dict(arrowstyle="->", color=d.PMOS, lw=1.0))
ax.text(5.2, 0.98, T("e⁻ 写入", "e⁻ program"), fontsize=8.5, color=d.PMOS)
ax.set_xlim(-0.4, 8.4); ax.set_ylim(0, 2.7); ax.axis("off")
figure(fig, "fig7_4_1")
