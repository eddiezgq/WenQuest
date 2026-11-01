"""10.1 节的计算：

算例 10.1.1  沿闭合路径绕一周，四种力各做多少功（数值线积分，图 10.1.1）：
            （a）重力 m = 2.0 kg，竖直面内矩形回路 2.0 m × 1.0 m；
            （b）各向同性弹簧力 F = −k r，k = 50 N/m，圆心 (1.0, 0.5) m、半径 0.5 m 的圆；
            （c）AGV 的滚动阻力（大小 73.6 N，与运动方向相反），水平面上同一矩形回路；
            （d）旋涡状的力 F = c(−y, x)，c = 3.0 N/m，单位圆，逆时针与顺时针。
            另按 ∂F_y/∂x − ∂F_x/∂y 检验（a）（b）（d）。
算例 10.1.2  码垛机器人的夹爪（3.0 kg）在一个循环中抬高 1.2 m、平移、下降、回到原处：重力做的总功；
            末端在空气中走 4.0 m、平均阻力 2.0 N，阻力做的功。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d


def loop_work(F, path, n=8000):
    u = np.linspace(0, 1, n + 1)
    r = np.array([path(t) for t in u])
    dr = np.diff(r, axis=0)
    mid = (r[1:] + r[:-1]) / 2
    return float(sum(np.dot(F(p, q), q) for p, q in zip(mid, dr)))


def rect(t, w=2.0, h=1.0):                                      # 逆时针矩形，从 (0, 0) 出发
    s = 2 * (w + h) * t
    if s < w:
        return np.array([s, 0.0])
    if s < w + h:
        return np.array([w, s - w])
    if s < 2 * w + h:
        return np.array([w - (s - w - h), h])
    return np.array([0.0, h - (s - 2 * w - h)])


m, k, f_roll, c = 2.0, 50.0, 73.6, 3.0
F_grav = lambda p, q: np.array([0.0, -m * g])
F_spring = lambda p, q: -k * p
F_roll = lambda p, q: -f_roll * q / np.linalg.norm(q)
F_vort = lambda p, q: c * np.array([-p[1], p[0]])
circ = lambda t, c0=np.array([1.0, 0.5]), R=0.5: c0 + R * np.array([math.cos(2 * math.pi * t), math.sin(2 * math.pi * t)])
unit_ccw = lambda t: np.array([math.cos(2 * math.pi * t), math.sin(2 * math.pi * t)])
unit_cw = lambda t: np.array([math.cos(2 * math.pi * t), -math.sin(2 * math.pi * t)])
Wa = loop_work(F_grav, rect)
Wb = loop_work(F_spring, circ)
Wc = loop_work(F_roll, rect)
Wd_ccw, Wd_cw = loop_work(F_vort, unit_ccw), loop_work(F_vort, unit_cw)
assert abs(Wa) < 1e-9 and abs(Wb) < 1e-6 and abs(Wc + f_roll * 6.0) < 1e-2 * f_roll   # 跨过拐角的小段走的是弦，略短
assert abs(Wd_ccw - 2 * math.pi * c) < 1e-3 and abs(Wd_cw + 2 * math.pi * c) < 1e-3


def curl(F, p, h=1e-5):                                        # ∂F_y/∂x − ∂F_x/∂y（中心差分）
    ex, ey = np.array([h, 0]), np.array([0, h])
    return (F(p + ex, None)[1] - F(p - ex, None)[1]) / (2 * h) - (F(p + ey, None)[0] - F(p - ey, None)[0]) / (2 * h)


pt = np.array([0.7, 0.3])
out(m=m, k=k, f_roll=f_roll, c=c, Wa=abs(Wa), Wb=abs(Wb), Wc=-Wc, Wd_ccw=Wd_ccw, Wd_cw=-Wd_cw, two_pi_c=2 * math.pi * c,
    curl_g=abs(curl(F_grav, pt)), curl_s=abs(curl(F_spring, pt)), curl_v=curl(F_vort, pt))

# ---- 算例 10.1.2：码垛循环中的夹爪（3.0 kg）：抬高 1.2 m、平移、下降、返回原处
mt, hb, L_air, f_air = 3.0, 1.2, 4.0, 2.0
W_tool_up, W_tool_down = -mt * g * hb, mt * g * hb
out(mt=mt, hb=hb, W_tool_up=-W_tool_up, W_tool_down=W_tool_down, L_air=L_air, f_air=f_air, W_air=f_air * L_air)

plt = style()
# ---- 图 10.1.1
fig, axs = plt.subplots(1, 4, figsize=(8.4, 2.6))
X, Y = np.meshgrid(np.linspace(-1.3, 2.3, 9), np.linspace(-1.3, 1.5, 8))


def quiver(ax, F, scale):
    U = np.zeros_like(X); V = np.zeros_like(Y)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            U[i, j], V[i, j] = F(np.array([X[i, j], Y[i, j]]), np.array([1.0, 0.0]))
    ax.quiver(X, Y, U, V, color=d.MUTED, scale=scale, width=0.006, alpha=0.7)


R1 = np.array([rect(t) for t in np.linspace(0, 1, 200)])
C1 = np.array([circ(t) for t in np.linspace(0, 1, 200)])
U1 = np.array([unit_ccw(t) for t in np.linspace(0, 1, 200)])
panels = [(F_grav, 120, R1, T("(a) 重力", "(a) gravity"), T("一周的功 = 0", "work per loop = 0")),
          (F_spring, 600, C1, T("(b) 弹簧力", "(b) spring force"), T("一周的功 = 0", "work per loop = 0")),
          (None, None, R1, T("(c) 滚动阻力", "(c) rolling resistance"), T(f"一周 −{-Wc:.0f} J", f"per loop −{-Wc:.0f} J")),
          (F_vort, 40, U1, T("(d) 旋涡状的力", "(d) swirling force"), T(f"逆时针一周 +{Wd_ccw:.1f} J", f"CCW loop +{Wd_ccw:.1f} J"))]
for ax, (F, sc, P, title, note) in zip(axs, panels):
    if F is not None:
        quiver(ax, F, sc)
    ax.plot(P[:, 0], P[:, 1], color=d.VR, lw=2)
    i = len(P) // 8
    d.arrow(ax, P[i], P[i + 3], d.VR, lw=2, ms=12)
    if F is None:
        for j in (33, 83, 133, 183):                       # 每条边的中点
            q = P[j + 1] - P[j]; q = q / np.linalg.norm(q)
            d.arrow(ax, P[j], P[j] - 0.45 * q, d.VA, lw=1.4, ms=9)
    ax.set_title(title, fontsize=9.5); ax.text(0.5, -0.12, note, transform=ax.transAxes, ha="center", fontsize=9, color=d.INK)
    ax.set_aspect("equal"); ax.set_xlim(-1.4, 2.4); ax.set_ylim(-1.4, 1.6); ax.set_xticks([]); ax.set_yticks([])
    for s_ in ax.spines.values():
        s_.set_color(d.MUTED); s_.set_linewidth(0.5)
fig.tight_layout()
figure(fig, "fig10_1_1")
