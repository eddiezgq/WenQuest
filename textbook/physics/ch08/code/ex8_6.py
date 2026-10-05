"""8.6 节的计算：

算例 8.6.1  网球（m = 58 g）从 1.0 m 高处落到地面。地面用“罚函数”弹簧—阻尼器表示：球压进地面 δ 时，地面推球的力为
            kδ − c·dδ/dt（只推不拉），k = 3.0×10⁴ N/m，c 取使恢复系数约 0.75 的值。用半隐式欧拉法，步长取 0.1 ms（参考）、
            2 ms（MuJoCo 的默认步长）和 1/60 s（游戏常用的帧长），第一次反弹的高度各是多少（图 8.6.1）？
            再用游戏引擎常用的“冲量法”（检测到穿入地面时，把速度按恢复系数反向、把球放回地面）在 1/60 s 步长下计算。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

m, k, e, H = 0.058, 3.0e4, 0.75, 1.0
zeta = -math.log(e) / math.sqrt(math.pi ** 2 + math.log(e) ** 2)
c = 2 * zeta * math.sqrt(k * m)
w = math.sqrt(k / m)


def penalty(h, T_=2.0):
    y, v, t = H, 0.0, 0.0
    ys, ts = [y], [t]
    while t < T_:
        F = -m * g + (max(0.0, -k * y - c * v) if y < 0 else 0.0)     # 只推不拉
        v += h * F / m
        y += h * v
        t += h
        ys.append(y); ts.append(t)
    return np.array(ts), np.array(ys)


def impulse(h, T_=2.0):
    y, v, t = H, 0.0, 0.0
    ys, ts = [y], [t]
    while t < T_:
        v -= g * h
        y += h * v
        if y < 0:                                                    # 穿入地面：速度按恢复系数反向，球放回地面（略高于 0）
            y, v = 1e-9, -e * v
        t += h
        ys.append(y); ts.append(t)
    return np.array(ts), np.array(ys)


def first_bounce(ts, ys):
    """第一次着地之后的最高点。"""
    dy = np.diff(ys)
    i = int(np.argmax(dy > 0))                                     # 第一次开始上升（反弹）
    j = i + int(np.argmax(dy[i:] < 0))                             # 之后第一次开始下降：最高点
    return ys[j]


hs = {"ref": 1e-4, "mj": 0.002, "game": 1 / 60}
runs = {n_: penalty(h) for n_, h in hs.items()}
hb = {n_: first_bounce(*runs[n_]) for n_ in ("ref", "mj")}            # 1/60 s 的球已飞走，不求反弹高度
ti, yi = impulse(1 / 60)
tg, yg = runs["game"]
ig = int(np.argmax(yg < 0))
v_game = (yg[ig + 1] - yg[ig]) * 60
out(v_game=v_game, hb_game_km=v_game ** 2 / (2 * g) / 1000, v_impact=math.sqrt(2 * g * H), k=k, c=c, zeta=zeta, w=w, Tc_ms=1000 * math.pi / w, wh_mj=w * 0.002, wh_game=w / 60,
    hb_exact=e * e * H, hb_ref=hb["ref"], hb_mj=hb["mj"], hb_imp=first_bounce(ti, yi),
    pen_game_mm=-1000 * runs["game"][1].min(), pen_ref_mm=-1000 * runs["ref"][1].min())

plt = style()
fig, ax = plt.subplots(figsize=(5.4, 3.0))
for n_, col, name in (("ref", d.MUTED, T("罚函数，h = 0.1 ms（参考）", "penalty, h = 0.1 ms (reference)")),
                      ("mj", d.VA, T("罚函数，h = 2 ms", "penalty, h = 2 ms")),
                      ("game", d.VR, T("罚函数，h = 1/60 s", "penalty, h = 1/60 s"))):
    ts, ys = runs[n_]
    ax.plot(ts, ys, color=col, lw=1.8 if n_ != "ref" else 3.0, alpha=0.9 if n_ != "ref" else 0.5, label=name)
ax.plot(ti, yi, color=d.VB, lw=1.4, ls="--", label=T("冲量法，h = 1/60 s", "impulse, h = 1/60 s"))
ax.axhline(0, color=d.INK, lw=0.8)
ax.text(0.5, 1.5, T(f"以 {v_game:.0f} m/s 飞走", f"flies off at {v_game:.0f} m/s"), color=d.VR, fontsize=8.5)
ax.set_xlabel("t / s"); ax.set_ylabel(T("球的高度 / m", "height / m")); ax.set_ylim(-0.3, 2.2); ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper right"); d.spines(ax)
figure(fig, "fig8_6_1")
