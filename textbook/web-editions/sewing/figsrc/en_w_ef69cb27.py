# Fig. 15-1d (English): timing of the intermediate presser foot and the needle.
import numpy as np
from en_ch15_style import *

r, l = 15.5, 55.0; lam = r / l
def h(deg):
    p = np.radians(deg)
    return 18 - (r * (1 - np.cos(p)) - l * (1 - np.sqrt(1 - lam**2 * np.sin(p)**2)))
def blend(t): return (1 - np.cos(np.pi * np.clip(t, 0, 1))) / 2
def foot(d):   # bottom of the intermediate foot (mm): 6 mm when up, 1.5 mm on the fabric
    down = blend((d - 55) / 45)          # lowers from 55° to 100°
    up = blend((d - 258.3) / 41.7)       # lifts from 258.3° to 300°
    return 6 - 4.5 * down + 4.5 * up

fig = figure(808 / 1344)
header(fig, 'Foot down before the needle enters, up after it exits; the template moves only while the foot is up',
       'Fabric + lower template plate 1.5 mm thick; foot lift 4.5 mm; the foot’s lowering and lifting angles are example values')
ax = fig.add_axes([0.145, 0.161, 0.802, 0.699])
clean(ax, bottom=False)
ax.set_xlim(0, 360); ax.set_ylim(-14.5, 22)
ax.axvspan(0, 91.7, color=WIN, lw=0, zorder=0.2); ax.axvspan(268.3, 360, color=WIN, lw=0, zorder=0.2)
ax.axvspan(100, 258.3, color=STILL, lw=0, zorder=0.2)
ax.axhspan(0, 1.5, color=FABRIC, alpha=0.85, lw=0, zorder=0.3)
ax.axhline(0, color=AXIS, lw=1)
pts = np.arange(0, 361, 10)
ax.plot(pts, h(pts), '-o', color=GREY, lw=2.2, ms=3.5)
ax.plot(pts, foot(pts), '-o', color=BLUE, lw=2.6, ms=3.5)
ax.text(91.7 / 2, 21.0, 'Template moves', color=BLUE, ha='center', va='center')
ax.text((268.3 + 360) / 2, 21.0, 'Template moves', color=BLUE, ha='center', va='center')
ax.text(179, 21.0, 'Foot holds the fabric down', color=MUTED, ha='center', va='center')
ax.text(15, 7.2, 'Intermediate-foot bottom', color=BLUE, ha='left', va='bottom', fontweight='bold', fontsize=11)
ax.text(180, -14.6, 'Needle-point height', color=MUTED, ha='center', va='top')
ax.set_yticks([-10, 0, 10, 20])
ax.set_xticks([0, 90, 180, 270, 360]); ax.set_xticklabels(['0°', '90°', '180°', '270°', '360°'])
ax.tick_params(axis='x', pad=30)
ylabel(fig, ax, 'Height', 'mm', yfrac=0.55)
fig.text(0.032, 0.101, 'Main-shaft angle φ', fontsize=10.5, color=MUTED, va='center')
foot_ = ['Lowering finishes before the entry angle 101.7° and lifting starts after the exit angle 258.3°; the template moves 10° after',
         'needle exit, when the foot has already left the fabric']
for i, t in enumerate(foot_): fig.text(0.032, 0.068 - i * 0.032, t, fontsize=10.5, color=MUTED, va='top')
save(fig, 'w_ef69cb27')
