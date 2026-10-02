import sys, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *

# timeline numbers (worked example, same model as fig_14_speed: decel at 60% of servo capability)
ALPHA = (2.5 + 0.15) / 6e-4
w = lambda n: n * 2 * math.pi / 60
t_dec = (w(4000) - w(300)) / (0.6 * ALPHA)
t_trim = 415 / (6 * 300)
t_stop = w(300) / ALPHA
t_wipe = 0.080  # wipe + foot lift (illustrative, as in the original figure)
print(t_dec, t_trim, t_stop)

BW, GAP, BH = 184, 55, 108
xs = [i * (BW + GAP) for i in range(5)]
Y1, Y2 = 0, 206
RED = 'border-color:#c8382a'
top = [('k', 'Idle', 'stopped at needle-up<br>foot raised', ''),
       ('o', 'Foot down', 'pedal pressed forward<br>solenoid / cylinder', ''),
       ('o', 'Start backtack', 'reverse, then forward,<br>a few stitches each<br>backtack speed limit (14.3)', ''),
       ('b', 'Soft start', 'first stitches speed-limited<br>(14.2)', ''),
       ('b', 'Sewing', 'speed follows the pedal;<br>stitch length and tension<br>by program', '')]
bot = [('o', 'Wipe, lift foot', 'wipe the thread end<br>raise the presser foot', ''),
       ('r', 'Cut, needle stop', 'cut at take-up lever top<br>stop at needle-up', RED),
       ('r', 'Trimming stitch', 'trim command, release<br>tension; knife enters<br>the loop (14.4)', RED),
       ('b', 'Decelerate', 'down to trimming speed<br>(14.2)', ''),
       ('o', 'End backtack', 'heel pressed fully back:<br>backtack first (14.3)', '')]
h = []
def box(x, y, c, t, sub, ex):
    tc = 'color:#b32d20' if c == 'r' else ''
    cls = 'k' if c == 'k' else ('o' if c == 'r' else c)
    extra = 'border-color:#5a6570;' if c == 'k' else ''
    h.append(f'<div class="box {cls}" style="position:absolute;left:{x}px;top:{y}px;width:{BW}px;height:{BH}px;{extra}{ex};display:flex;flex-direction:column;justify-content:flex-start;padding-top:12px">'
             f'<b style="{tc}">{t}</b><span style="margin-top:4px;line-height:1.4;font-size:11.5px">{sub}</span></div>')
for x, b in zip(xs, top): box(x, Y1, *b)
for x, b in zip(xs, bot): box(x, Y2, *b)
sv = [arrow_defs((('ak', '#5a6570'),))]
def harrow(x1, x2, y, lab):
    sv.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#5a6570" stroke-width="2" marker-end="url(#ak)"/>')
    for i, l in enumerate(lab.split('|')):
        sv.append(f'<text x="{(x1+x2)/2}" y="{y-10-14*(len(lab.split("|"))-1-i)}" font-size="11.5" fill="#1b2430" text-anchor="middle">{l}</text>')
tl = ['pedal|forward', 'foot|down', 'backtack|done', 'soft start|done']
for i in range(4):
    harrow(xs[i] + BW + 4, xs[i + 1] - 4, Y1 + 46, tl[i])
bl = ['stopped', 'at trim|angle', 'at trim|speed', 'backtack|done']
for i in range(4):
    harrow(xs[i + 1] - 4, xs[i] + BW + 4, Y2 + 46, bl[i])
xc = xs[4] + BW / 2
sv.append(f'<line x1="{xc}" y1="{Y1+BH+2}" x2="{xc}" y2="{Y2-4}" stroke="#5a6570" stroke-width="2" marker-end="url(#ak)"/>')
sv.append(f'<text x="{xc-10}" y="{(Y1+BH+Y2)/2+5}" font-size="12.5" font-weight="700" fill="#1b2430" text-anchor="end">heel pressed fully back</text>')
xc0 = xs[0] + BW / 2
sv.append(f'<line x1="{xc0}" y1="{Y2-2}" x2="{xc0}" y2="{Y1+BH+4}" stroke="#5a6570" stroke-width="2" marker-end="url(#ak)"/>')
sv.append(f'<text x="{xc0+10}" y="{(Y1+BH+Y2)/2+5}" font-size="12.5" font-weight="700" fill="#1b2430">pedal released</text>')
SH = Y2 + BH + 4
state = f'<div style="position:relative;height:{SH}px;margin-top:30px">{"".join(h)}<svg width="1140" height="{SH}" style="position:absolute;left:0;top:0;overflow:visible">{"".join(sv)}</svg></div>'

# timeline bar
x0, x1 = 56, 1100
X = lambda t: x0 + (x1 - x0) * t / 0.5
segs = [(0, t_dec, '#4a83dc', 'Decelerate to 300 r/min', C['blue']),
        (t_dec, t_dec + t_trim, '#c9564a', 'Trimming stitch', C['red']),
        (t_dec + t_trim, t_dec + t_trim + t_stop, '#e07a45', 'Stop', C['orange']),
        (t_dec + t_trim + t_stop, t_dec + t_trim + t_stop + t_wipe, '#78838e', 'Wipe, lift foot', '#3f4954')]
tb = []
for i, (a, b, col, lab, tc) in enumerate(segs):
    rx = 4 if i in (0, 3) else 0
    tb.append(f'<rect x="{X(a):.1f}" y="10" width="{X(b)-X(a):.1f}" height="28" rx="{rx}" fill="{col}"/>')
    cx = (X(a) + X(b)) / 2
    if lab == 'Stop': cx += 4
    if lab == 'Wipe, lift foot': cx += 24
    tb.append(f'<text x="{cx:.1f}" y="70" font-size="12.5" font-weight="700" fill="{tc}" text-anchor="middle">{lab}</text>')
for k in range(6):
    t = k * 0.1
    tb.append(f'<line x1="{X(t):.1f}" y1="44" x2="{X(t):.1f}" y2="50" stroke="#1b2430" stroke-width="1.4"/>')
    tb.append(f'<text x="{X(t):.1f}" y="88" font-size="12" fill="{C["muted"]}" text-anchor="middle">{t:.1f} s</text>')
tsvg = f'<svg width="1140" height="96" style="display:block">{"".join(tb)}</svg>'

tot = t_dec + t_trim + t_stop
body = f'''<p class="title">One working cycle of an electronically controlled lockstitch machine</p>
<p class="sub">Illustrative. Boxes are states, arrows carry the trigger conditions; the controller runs them in order as a state machine. Section numbers of this chapter in brackets</p>
{state}
<p style="font-weight:700;font-size:14px;margin:34px 0 4px">After the pedal is released (from 4000 r/min, worked example)</p>
{tsvg}
<p class="note" style="color:#1b2430;font-size:13px;margin-top:10px">Deceleration {t_dec*1000:.0f} ms + trimming stitch about {t_trim*1000:.0f} ms + needle stop {t_stop*1000:.0f} ms ≈ {tot*1000:.0f} ms; with wiping and foot lift, about half a second (deceleration taken as 60% of the servo’s capability; illustrative)</p>'''
render('fig_14_cycle', body)
