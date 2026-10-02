# Fig. 16-7 (English): overall efficiency and pieces per hour vs number of heads (model16 / embroid lab page B)
import sys, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
S, NSEW, NRESEW, COL, TC, TH, B = 20000, 800, 600, 6, 6, 40, 8
def exp(H, lam):
    Tsew = S * 60 / NSEW; Nb = H * lam * S / 1e4; resew = B * 60 / NRESEW * 2
    tot = Tsew + Nb * (TH + resew) + COL * TC
    return Tsew / tot, H * 3600 / tot
for H in (4, 8, 15, 20): print(H, [round(exp(H, 0.5)[0] * 100, 1), round(exp(H, 0.5)[1], 1)])
Hs = [1 + 0.1 * k for k in range(191)]

a = Chart(560, 470, (0, 20), (0, 100), L=66, T=12, R=12, B=48)
a.grid([0, 4, 8, 12, 16, 20], [0, 20, 40, 60, 80, 100], yfmt=lambda v: f'{v}%', xlab='Number of heads', ylab='Overall efficiency (sewing time / total time)', ylab_dx=-6)
for lam, col, dy in ((0.25, C['green'], -34), (0.5, C['blue'], -46), (1.0, C['orange'], -62)):
    a.line(Hs, [exp(h, lam)[0] * 100 for h in Hs], col)
    a.text(19.8, exp(19.8, lam)[0] * 100, (f'{lam:.1f}' if lam!=0.25 else '0.25')+' per head per 10,000 stitches', col, fs=12, bold=True, anchor='end', dy=dy)

b = Chart(420, 470, (0, 20), (0, 50), L=50, T=12, R=12, B=48)
b.grid([0, 4, 8, 12, 16, 20], [0, 10, 20, 30, 40, 50], xlab='Number of heads', ylab='Pieces per hour (whole machine)', ylab_dx=6)
b.line(Hs, [h * 3600 / (S * 60 / NSEW) for h in Hs], C['grey'], w=1.6, dash='6 4')
b.line(Hs, [exp(h, 0.5)[1] for h in Hs], C['blue'])
b.text(11.2, 33, 'No breaks,', C['grey'], fs=12, bold=True, anchor='end', dy=-8)
b.text(11.2, 33, 'no colour changes', C['grey'], fs=12, bold=True, anchor='end', dy=8)
b.text(13.5, 20, 'Breaks 0.5 per head', C['blue'], fs=12, bold=True, dy=0)
b.text(13.5, 20, 'per 10,000 stitches', C['blue'], fs=12, bold=True, dy=16)

body = f'''<p class="title">The more heads, the more frequent the stops: overall efficiency and thread-break rate</p>
<p class="sub">Worked example: design of 20,000 stitches at 800 r/min; each thread break takes 40 s to deal with, plus backing up and mending; 6 colour changes of 6 s each; break rate in breaks per head per 10,000 stitches; all values illustrative</p>
<div style="display:flex;gap:36px;align-items:flex-start;margin-top:30px;padding-left:24px">
<div>{a.svg()}</div><div>{b.svg()}</div></div>
<p class="note" style="color:#1b2430;font-size:13px;margin-top:14px">Doubling the heads less than doubles the output: a break on any head stops the whole machine. Machines with many heads therefore rely more on fast thread-break detection, automatic mending and quick threading, and the operator has to watch them more closely.</p>'''
render('fig_16_eff', body, width=1200)
