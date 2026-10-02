import sys, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
IDLE = (114.2, 325.8); SPAN = IDLE[1] - IDLE[0]; MARGIN = 10

# ---- left: switching window on the shaft-angle axis ----
W = 600
x0, x1 = 30, 575
X = lambda f: x0 + (x1 - x0) * f / 360
s = [arrow_defs((('ak', '#5a6570'),))]
a = s.append
for f in (0, 114.2, 180, 325.8, 360):
    a(f'<line x1="{X(f):.1f}" y1="30" x2="{X(f):.1f}" y2="245" stroke="{C["grid"]}" stroke-width="1"/>')
    a(f'<text x="{X(f):.1f}" y="268" font-size="12" fill="{C["muted"]}" text-anchor="middle">{f:g}°</text>')
a(f'<rect x="{X(0):.1f}" y="36" width="{X(114.2)-X(0):.1f}" height="42" fill="#f8ddd0"/>')
a(f'<rect x="{X(114.2):.1f}" y="36" width="{X(325.8)-X(114.2):.1f}" height="42" fill="#d5ecdc"/>')
a(f'<rect x="{X(325.8):.1f}" y="36" width="{X(360)-X(325.8):.1f}" height="42" fill="#f8ddd0"/>')
a(f'<text x="{X(57):.1f}" y="62" font-size="13" font-weight="700" fill="{C["orange"]}" text-anchor="middle">Feeding</text>')
a(f'<text x="{X(220):.1f}" y="62" font-size="13" font-weight="700" fill="{C["green"]}" text-anchor="middle">Feed dog below the plate (idle angle {SPAN:.1f}°)</text>')
a(f'<text x="{X(343):.1f}" y="62" font-size="11" font-weight="700" fill="{C["orange"]}" text-anchor="middle">Feeding</text>')
def run(y, n, col, extra=None):
    d = 6 * n * 0.018
    end = IDLE[0] + d
    a(f'<text x="{X(114.2):.1f}" y="{y-12}" font-size="12.5" font-weight="700" fill="{col}">{n} r/min: command → switch complete (18 ms = {d:.0f}°)</text>')
    a(f'<line x1="{X(114.2):.1f}" y1="{y}" x2="{X(min(end, 362)):.1f}" y2="{y}" stroke="{col}" stroke-width="2.4" marker-end="url(#ak)"/>')
    a(f'<circle cx="{X(114.2):.1f}" cy="{y}" r="5" fill="{col}"/>')
    if extra:
        for i, l in enumerate(extra.split('|')):
            a(f'<text x="{X(114.2)+6:.1f}" y="{y+24+i*16}" font-size="11.5" font-weight="700" fill="{C["red"]}">{l}</text>')
run(120, 1800, C['blue'])
run(180, 3000, C['red'], 'Beyond the idle angle: the feed dog has already risen above the plate,|so the stitch length of the first backtack stitch is wrong')
left = f'<svg width="{W}" height="280" style="display:block;overflow:visible">{"".join(s)}</svg>'

# ---- right: maximum backtack speed vs switching delay ----
ch = Chart(470, 370, (0, 30), (0, 8000), L=66, T=12, R=14, B=48)
ch.grid([0, 5, 10, 15, 20, 25, 30], [0, 2000, 4000, 6000, 8000], xlab='Delay of the switching mechanism (ms)', ylab='Max. backtack speed (r/min)', ylab_dx=-2)
ts = [3 + k * 0.05 for k in range(541)]
ch.line(ts, [min(8000, (SPAN - MARGIN) / (6 * t / 1000)) for t in ts], C['blue'])
ch.text(6, 6800, 'n_max = (211.6° − 10°) / (6 × delay)', C['blue'], fs=12.5, bold=True)
print('18 ms ->', (SPAN - MARGIN) / (6 * 0.018), '20 ms ->', (SPAN - MARGIN) / (6 * 0.020))

body = f'''<p class="title">Automatic backtack: switch the feed direction while the feed dog is below the throat plate</p>
<p class="sub">Worked example of Chapter 6 (timing chart of Chapter 8): the feed dog drops below the throat plate at 114.2° and rises above it at 325.8°; the switch must be completed within this “idle angle” (with a 10° margin); delays are illustrative</p>
<div style="display:flex;gap:30px;align-items:flex-start;margin-top:6px">
<div style="border:1.2px solid #e3e6e9;border-radius:8px;background:#fff;padding:16px 12px 10px">{left}</div>
<div style="margin-top:8px">{ch.svg()}</div></div>
<p class="note" style="color:#1b2430;font-size:13px;line-height:1.7;margin-top:16px">Backtacking is done either by a reverse-feed solenoid that moves the stitch-length regulator (mechanical feed) or by the feed stepper motor reversing directly (electronic feed). The former has to push a linkage and a spring, with a delay of a dozen to twenty-odd milliseconds; the latter only needs a short stepper move, a few milliseconds. So machines with mechanical feed must limit the backtack speed, while electronic feed allows much higher backtack speeds and better-aligned backtack stitches.</p>'''
render('fig_14_bt', body)
