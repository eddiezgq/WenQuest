# Fig. 15-5 (English): electronic cam - needle height, X position and X velocity over two stitches.
import numpy as np
from en_ch15_style import *

r, l = 15.5, 55.0; lam = r / l
def h(deg):
    p = np.radians(deg)
    return 18 - (r * (1 - np.cos(p)) - l * (1 - np.sqrt(1 - lam**2 * np.sin(p)**2)))
s, n = 3.0, 1600.0
ws, we = 258.3 + 10, 360 + 101.7 - 10          # used window 268.3 .. 451.7 (183.4 deg)
dphi = we - ws; dt = dphi / 360 * 60 / n      # 19.1 ms
def xpos(phi):
    out = np.zeros_like(phi, dtype=float)
    for k in range(2):
        tau = np.clip((phi - ws - 360 * k) / dphi, 0, 1)
        out += s * (tau - np.sin(2 * np.pi * tau) / (2 * np.pi))
    return out
def xvel(phi):
    out = np.zeros_like(phi, dtype=float)
    for k in range(2):
        tau = (phi - ws - 360 * k) / dphi
        m = (tau >= 0) & (tau <= 1)
        out[m] += (s / 1000) / dt * (1 - np.cos(2 * np.pi * tau[m]))
    return out
H = 862
fy = lambda px: 1 - px / H
L, Wd = 0.157, 0.790
fig = figure(H / 1344)
header(fig, 'Electronic cam: X position is a function of main-shaft angle, moving 3 mm within each out-of-fabric window',
       f'Cycloidal motion law; 10° margin at each end of the window, {dphi:.1f}° used; at n = 1600 r/min peak velocity {2*s/1000/dt:.2f} m/s, peak acceleration {2*np.pi*s/1000/dt**2:.0f} m/s²',
       y0=0.962, dy=0.042)
bg = fig.add_axes([L, fy(772), Wd, fy(117) - fy(772)]); bg.set_axis_off(); bg.set_xlim(180, 900); bg.set_ylim(0, 1)
for k in range(2): bg.axvspan(ws + 360 * k, we + 360 * k, color=WIN, lw=0)
bg.text((ws + we) / 2, 0.965, 'Out-of-fabric window', color=BLUE, ha='center', va='center', fontweight='bold', fontsize=11)
bg.text(540, 0.965, 'Needle in fabric: X stays still', color=MUTED, ha='center', va='center')
phi = np.linspace(180, 900, 1441); pts = np.arange(180, 901, 10)
def panel(top, bot, ylo, yhi):
    ax = fig.add_axes([L, fy(bot), Wd, fy(top) - fy(bot)]); ax.patch.set_alpha(0)
    clean(ax, bottom=False); ax.set_xlim(180, 900); ax.set_ylim(ylo, yhi); ax.set_xticks([])
    return ax
a1 = panel(146, 300, -14, 19.5)
a1.axhspan(0, 1.5, color=FABRIC, alpha=0.85, lw=0, zorder=0.3)
a1.plot(pts, h(pts), '-o', color=GREY, lw=2.2, ms=3.2)
a1.set_yticks([-10, 0, 10])
a2 = panel(360, 540, -0.38, 6.54)
a2.axhline(0, color=AXIS, lw=1)
a2.plot(pts, xpos(pts), '-o', color=BLUE, lw=2.4, ms=3.2); a2.set_yticks([0, 3, 6])
a3 = panel(600, 772, -0.025, 0.338)
a3.axhline(0, color=AXIS, lw=1)
a3.plot(pts, xvel(pts), '-o', color=ORANGE, lw=2.2, ms=3.2); a3.set_yticks([0, 0.1, 0.2, 0.3]); a3.set_yticklabels(['0', '0.1', '0.2', '0.3'])
a3.text(360, 0.322, f'{2*s/1000/dt:.2f} m/s', color=ORANGE, ha='center', va='bottom')
a3.set_xticks([180, 360, 540, 720, 900]); a3.set_xticklabels(['180°', '360°', '540°', '720°', '900°'])
a3.tick_params(axis='x', pad=18)
for ax, nm, u, px in [(a1, 'Needle-point\nheight', 'mm', 222), (a2, 'X position', 'mm', 440), (a3, 'X velocity', 'm/s', 668)]:
    fig.text(0.032, fy(px), nm, fontsize=11, fontweight='bold', color=INK, va='bottom')
    fig.text(0.032, fy(px) - 0.008, u, fontsize=10.5, color=MUTED, va='top')
fig.text(0.032, fy(800), 'Main-shaft angle φ', fontsize=10.5, color=MUTED, va='center')
foot(fig, ['360° and 720° are top dead centre; when the main shaft changes speed the curve keeps its shape, only the time to traverse it changes'], fy(820))
save(fig, 'w_c8dfdae2')
