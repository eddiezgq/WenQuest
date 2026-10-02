import sys, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
# Worked example (model14): servo capability ALPHA = (Tmax + Tf)/J; accel/decel at 60 %, final stop at 100 %
ALPHA = (2.5 + 0.15) / 6e-4
A6 = 0.6 * ALPHA
w = lambda n: n * 2 * math.pi / 60
rpm = lambda om: om * 60 / (2 * math.pi)

def profile(nmax=4000, nslow=400, nslow_st=3, ntrim=300, nst=40):
    t, th, om, dt = 0.0, 0.0, w(nslow), 1e-4
    T, N, REV = [], [], []
    phase = 'slow'
    rev = lambda: th / (2 * math.pi)
    trim_start = nst - 1
    dec_revs = (w(nmax) ** 2 - w(ntrim) ** 2) / (2 * A6) / (2 * math.pi)
    while True:
        if phase == 'slow' and rev() >= nslow_st: phase = 'acc'
        if phase == 'acc' and om >= w(nmax): om = w(nmax); phase = 'run'
        if phase == 'run' and rev() >= trim_start - dec_revs: phase = 'dec'
        if phase == 'dec' and om <= w(ntrim): om = w(ntrim); phase = 'trim'
        if phase == 'trim' and rev() >= trim_start + 415 / 360: phase = 'stop'
        if phase == 'stop' and om <= 0: break
        a = {'slow': 0, 'acc': A6, 'run': 0, 'dec': -A6, 'trim': 0, 'stop': -ALPHA}[phase]
        om = max(0.0, om + a * dt); th += om * dt; t += dt
        T.append(t); N.append(rpm(om)); REV.append(rev())
    return T, N, REV

T, N, REV = profile()
print('total', T[-1])
ch = Chart(660, 440, (0, 1.5), (0, 4400), L=64, T=16, R=14, B=48)
ch.grid([0, 0.25, 0.5, 0.75, 1, 1.25, 1.5], [0, 1000, 2000, 3000, 4000], xfmt=lambda v: f'{v:g}', xlab='Time (s)', ylab='Main-shaft speed (r/min)', ylab_dx=-2)
ch.line([0] + T[::5], [400] + N[::5], C['blue'], w=2.2)
# stitch-count ticks
for k in range(0, 41, 5):
    i = next(j for j, r in enumerate(REV) if r >= k) if k else 0
    tk = T[i] if k else 0
    ch.raw(f'<line x1="{ch.X(tk):.1f}" y1="{ch.y1-12}" x2="{ch.X(tk):.1f}" y2="{ch.y1}" stroke="{C["ink"]}" stroke-width="1.3"/>')
    ch.text(tk, 0, str(k), C['muted'], fs=11, anchor='middle', dy=-17)
ch.text(0.025, 0, '(stitch no.)', C['muted'], fs=11, dy=-17)
ch.text(0.02, 680, 'Soft start', C['orange'], fs=13, bold=True)
ch.text(0.45, 4150, 'Constant speed', C['blue'], fs=13, bold=True)
ch.text(1.08, 2200, 'Decelerate', C['blue'], fs=13, bold=True)
ch.text(1.25, 680, 'Trim, stop', C['red'], fs=13, bold=True, anchor='middle')

# right: time to stop and trim from 4000 r/min
def parts(ntrim):
    return ((w(4000) - w(ntrim)) / A6, 415 / (6 * ntrim), w(ntrim) / ALPHA)
rows = [200, 300, 500]
bx0, bx1 = 128, 340
BX = lambda t: bx0 + (bx1 - bx0) * t / 0.6
rb = []
for i, n in enumerate(rows):
    y = 40 + i * 92
    a, b, c = parts(n); x = 0
    for d, col in ((a, '#2f6fd8'), (b, '#c0392b'), (c, '#e0662f')):
        rb.append(f'<rect x="{BX(x):.1f}" y="{y}" width="{BX(x+d)-BX(x):.1f}" height="34" fill="{col}"/>'); x += d
    rb.append(f'<text x="{bx0-6}" y="{y+22}" font-size="13" font-weight="700" fill="{C["ink"]}" text-anchor="end">Trim at {n} r/min</text>')
    rb.append(f'<text x="{BX(x)+8:.1f}" y="{y+22}" font-size="13" font-weight="700" fill="{C["ink"]}">{x*1000:.0f} ms</text>')
    print(n, [round(v * 1000, 1) for v in (a, b, c)], round(x * 1000))
for k in range(4):
    t = k * 0.2
    rb.append(f'<text x="{BX(t):.1f}" y="324" font-size="12" fill="{C["muted"]}" text-anchor="middle">{t:.1f} s</text>')
rb.append(f'<text x="0" y="356" font-size="12" fill="{C["muted"]}">Blue: deceleration&#160;&#160; Red: the trimming stitch&#160;&#160; Orange: needle stop</text>')
rsvg = f'<svg width="388" height="366" style="display:block;overflow:visible">{"".join(rb)}</svg>'

body = f'''<p class="title">Main-shaft speed profile: soft start, acceleration, constant speed, deceleration, trimming, needle stop</p>
<p class="sub">Worked example: a 40-stitch seam, maximum 4000 r/min, first 3 stitches at 400 r/min, last stitch trimmed at 300 r/min; acceleration and deceleration taken as 60% of the servo’s capability (illustrative)</p>
<div style="display:flex;gap:22px;align-items:flex-start;margin-top:26px;padding-left:6px">
<div>{ch.svg()}</div>
<div style="border:1.2px solid #e3e6e9;border-radius:8px;background:#fff;padding:14px 16px 12px;width:420px;flex:none;margin-top:2px">
<p style="font-size:15px;font-weight:700;margin:0 0 8px">How long to stop and trim from 4000 r/min</p>{rsvg}</div></div>
<p class="note" style="color:#1b2430;font-size:13px;line-height:1.7;margin-top:18px">Soft start: when a seam begins, the needle-thread end is short and the bobbin thread is not yet pulled tight; if the first stitches run too fast the thread pulls out of the needle or tangles under the fabric, so the first 3 stitches are speed-limited (one mode in a manufacturer’s manual: first 3 stitches at 400 sti/min, 4000 sti/min from the 4th).<br>
The lower the trimming speed, the more reliable the trim, but the longer it takes; with thousands of trims a day, every 100 r/min added to the trimming speed saves a noticeable amount of time.</p>'''
render('fig_14_speed', body)
