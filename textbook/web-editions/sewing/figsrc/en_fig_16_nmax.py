# Fig. 16-3 (English): speed limit vs stitch length for 1/4/8/15/20 heads (model16: n_max = 204/6*sqrt(a_max/(2*pi*s)), capped at 1100)
import sys, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
WIN, CAP, FF = 204, 1100, 50
mass = lambda H: 6 if H == 1 else 10 + 4 * H
amax = lambda H: ((300 if H == 1 else 800) - FF) / mass(H)
nmax = lambda s, H: min(CAP, WIN / 6 * math.sqrt(amax(H) / (2 * math.pi * s * 1e-3)))
for H in (4, 8, 15): print(H, [round(nmax(s, H)) for s in (3, 5, 7)])

ch = Chart(760, 420, (0, 12), (0, 1200), L=66, T=12, R=14, B=48)
ch.grid([0, 2, 4, 6, 8, 10, 12], [0, 200, 400, 600, 800, 1000, 1200], xlab='Stitch length (mm)', ylab='Speed limit (r/min)', ylab_dx=-2)
ss = [0.5 + 0.02 * k for k in range(576)]
ser = [(1, C['grey'], 'Single head'), (4, C['green'], '4 heads'), (8, C['blue'], '8 heads'), (15, C['orange'], '15 heads'), (20, C['red'], '20 heads')]
ch.vline(7, '#6b7682', w=1.2, dash='5 4')
ch.text(7, 1200, '7 mm satin', C['muted'], fs=11.5, dx=5, dy=16)
for H, col, lab in ser:
    ch.line(ss, [nmax(s, H) for s in ss], col, w=2.2)
dy = {1: -14, 4: -9, 8: -9, 15: -10, 20: 16}
for H, col, lab in ser:
    ch.text(11.6, nmax(11.6, H), lab, col, fs=12.5, bold=True, anchor='end', dy=dy[H] - (6 if H in (1, 4, 8) else 0))

side = f'''<div style="border:1.2px solid #e3e6e9;border-radius:8px;background:#fff;padding:18px 20px;font-size:13.5px;line-height:1.75;min-height:420px">
<p style="margin:0 0 14px">From a = 2πs / T² and T = 204° / (6n):</p>
<p style="margin:0 0 14px">n_max = (204/6) × √(a_max / (2π s))</p>
<p style="margin:0 0 14px">The speed limit is inversely proportional to √(stitch length).</p>
<p style="margin:0 0 4px">• With few heads and short stitches there is no limit; the speed is set by the head itself. An 8-head machine is already slightly limited at 3–4 mm.</p>
<p style="margin:0 0 4px">• Long satin stitches need lower speed; the controller sets the speed automatically from each stitch’s length (look-ahead, Chapter 15).</p>
<p style="margin:0 0 4px">• Going from 4 to 15 heads, the limit for a 7 mm stitch drops from about {round(nmax(7,4),-1):.0f} to about {round(nmax(7,15),-1):.0f} r/min.</p>
<p style="margin:0">• A DST record holds at most 12.1 mm in each direction; longer moves must be split into several records.</p></div>'''

body = f'''<p class="title">Speed limit: the longer the stitch and the more heads, the slower the machine runs</p>
<p class="sub">Worked example: Y-axis drive force 800 N (single head 300 N), friction 50 N, equivalent frame mass 10 + 4 × heads kg, machine maximum 1100 r/min; all values illustrative</p>
<div style="display:flex;gap:26px;align-items:flex-start;margin-top:30px;padding-left:6px">
<div>{ch.svg()}</div><div style="flex:1;margin-top:-4px">{side}</div></div>'''
render('fig_16_nmax', body, width=1260)
