"""6.2 节的计算：

算例 6.2.1  地面参考系离惯性参考系有多远：地球自转与公转带来的加速度；
算例 6.2.2  AGV 急停：货箱不滑的最大减速度 μ_s g，以及刹车过猛时货箱在车板上滑过的距离（图 6.2.2）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 6.2.1
T_sid = 86164.1                     # 恒星日，s（地球相对恒星自转一周）
R_eq = 6.378e6                      # 赤道半径，m
w = 2 * math.pi / T_sid
a_rot = w ** 2 * R_eq               # 赤道处随地球自转的向心加速度
lat = math.radians(31.2)            # 上海的纬度
a_rot_sh = w ** 2 * R_eq * math.cos(lat)
AU = 1.496e11                       # 日地平均距离，m
year = 365.256 * 86400              # 恒星年，s
a_orb = (2 * math.pi / year) ** 2 * AU
v_agv = 1.5
a_cor = 2 * w * v_agv               # 运动物体的科里奥利加速度的上限 2ωv（7.5 节）
assert a_rot / g < 0.004

# ---- 算例 6.2.2：AGV 以 v0 行驶，以恒定减速度 a 刹车；货箱与车板 μs = μk = μ（第 7 章再区分两者）
v0, mu = 1.5, 0.30
a_max = mu * g                      # 静摩擦能给货箱的最大减速度


def brake(a, dt=1e-4):
    """AGV 与货箱的速度—时间曲线（地面参考系）和货箱相对车板滑过的距离。"""
    t, va, vb, rel = 0.0, v0, v0, 0.0
    ts, vas, vbs = [0.0], [v0], [v0]
    while va > 0 or vb > va + 1e-12:
        va = max(0.0, va - a * dt)
        if vb > va + 1e-12 or a > a_max:          # 滑动：动摩擦给货箱 μg 的减速度
            vb = max(va, vb - mu * g * dt)
        else:
            vb = va
        rel += (vb - va) * dt
        t += dt
        ts.append(t); vas.append(va); vbs.append(vb)
    return np.array(ts), np.array(vas), np.array(vbs), rel


a_hard = 5.0
ts, vas, vbs, slide = brake(a_hard)
# 解析核对：AGV 停在 v0/a，货箱停在 v0/(μg)，相对滑动距离 = v0²/(2μg) − v0²/(2a)
slide_th = v0 ** 2 / (2 * mu * g) - v0 ** 2 / (2 * a_hard)
assert abs(slide - slide_th) < 1e-3
_, _, _, slide_ok = brake(0.8 * a_max)
assert slide_ok < 1e-9

assert f"{T_sid:,.1f}".replace(",", " ") == "86 164.1"
out(T_sid_txt="86 164.1", a_cor=a_cor, a_cor_g=a_cor / g, a_rot=a_rot, a_rot_pct=100 * a_rot / g, a_rot_sh=a_rot_sh, a_orb=a_orb,
    v0=v0, mu=mu, a_max=a_max, a_hard=a_hard, t_agv=v0 / a_hard, t_crate=v0 / (mu * g),
    slide_cm=100 * slide_th, d_agv_cm=100 * v0 ** 2 / (2 * a_hard), d_crate_cm=100 * v0 ** 2 / (2 * mu * g))

# ---- 图 6.2.1：伽利略的两个斜面
plt = style()
fig, ax = plt.subplots(figsize=(6.4, 2.6))
h = 1.0
ax.plot([-2, 0], [h, 0], color=d.INK, lw=2)
for k, (slope, c) in enumerate([(1.0, "#1d6fb8"), (0.5, "#2ca02c"), (0.25, "#e67e22")]):
    L = h / slope
    ax.plot([0, L], [0, h if L < 4.5 else h * 4.5 / L], color=c, lw=2)
    if L < 4.5:
        ax.plot([L], [h], "o", color=c, ms=7)
ax.plot([0, 4.6], [0, 0], color=d.INK, lw=2)
ax.plot([4.6, 5.2], [0, 0], color=d.INK, lw=2, ls=":")
ax.plot([-2], [h], "o", color=d.INK, ms=8)
ax.plot([-2.3, 4.6], [h, h], color=d.MUTED, lw=1, ls="--")
ax.text(-2.0, h + 0.15, T("释放", "release"), ha="center", fontsize=10, color=d.INK)
ax.text(4.0, h + 0.12, T("同一高度", "same height"), ha="center", fontsize=10, color=d.MUTED)
ax.text(4.9, 0.12, T("水平：永远运动下去", "level: rolls on forever"), ha="center", fontsize=10, color=d.INK)
ax.set_xlim(-2.5, 5.6); ax.set_ylim(-0.2, 1.4)
d.clean(ax)
figure(fig, "fig6_2_1")

# ---- 图 6.2.2：刹车过猛时，AGV 与货箱的速度—时间曲线
fig, ax = plt.subplots(figsize=(5.6, 3.2))
ax.plot(ts, vas, color=d.BODY, lw=2, label=T("AGV", "AGV"))
ax.plot(ts, vbs, color=d.CRATE, lw=2, label=T("货箱", "crate"))
ax.fill_between(ts, vas, vbs, color=d.CRATE, alpha=0.18)
ax.annotate(T("阴影面积 = 货箱在车板上滑过的距离", "shaded area = slide of the crate on the deck"), xy=(0.36, 0.25), xytext=(0.2, 1.35),
            fontsize=9, color=d.INK, arrowprops=dict(arrowstyle="->", color=d.MUTED))
ax.set_xlabel(T("时间 $t$ / s", "time $t$ / s")); ax.set_ylabel(T("对地速度 $v$ / (m/s)", "velocity $v$ / (m/s)"))
ax.set_xlim(0, ts[-1] * 1.05); ax.set_ylim(0, v0 * 1.25)
ax.legend(frameon=False)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
figure(fig, "fig6_2_2")
