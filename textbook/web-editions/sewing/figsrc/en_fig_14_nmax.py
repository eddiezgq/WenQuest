import sys, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
D = math.pi / 180
ALPHA = (2.5 + 0.15) / 6e-4            # max deceleration of the servo, rad/s^2 (model13/14)
STOP = (360 + 101.7 - 5) - 415          # 41.7°: from cut (55°) to 96.7°
n_stop = math.sqrt(2 * ALPHA * STOP * D) * 60 / (2 * math.pi)
win = lambda dt_ms: 30 / (6 * dt_ms / 1000)
print('stop limit', n_stop, 'win(4)', win(4), 'win(10)', win(10))

ch = Chart(700, 400, (0, 16), (0, 2000), L=66, T=12, R=14, B=48)
ch.grid([0, 4, 8, 12, 16], [0, 500, 1000, 1500, 2000], xlab='Range of solenoid delay t_max − t_min (ms)', ylab='Max. trimming speed (r/min)', ylab_dx=-2)
ts = [1.5 + k * 0.02 for k in range(726)]
ch.hline(n_stop, C['orange'], w=1.8, dash='7 5')
ch.line(ts, [min(2000, win(t)) for t in ts], C['blue'])
ch.text(3.5, 2000, 'Knife-entry window limit: 30° / (6 × delay range)', C['blue'], fs=12.5, bold=True, dy=24)
ch.text(16, n_stop, f'Stopping limit: about {n_stop:.0f} r/min', C['orange'], fs=12.5, bold=True, anchor='end', dx=-4, dy=-10)
n1 = min(win(4), n_stop)
ch.dot(4, n1, C['green'], r=6)
ch.text(4, n1, f'Delay 6–10 ms: {n1:.0f} r/min', C['green'], fs=12.5, bold=True, anchor='end', dx=-10, dy=26)
ch.dot(10, win(10), C['red'], r=6)
ch.text(10, win(10), f'Delay 5–15 ms: {win(10):.0f} r/min', C['red'], fs=12.5, bold=True, dx=4, dy=-14)

side = f'''<div style="border:1.2px solid #e3e6e9;border-radius:8px;background:#fff;padding:18px 20px;font-size:13px;line-height:1.7">
<p style="margin:0 0 14px;font-weight:700">How to raise the trimming speed</p>
<p style="margin:0 0 14px">• Make the solenoid delay consistent: regulated supply, boost, Zener freewheeling (Chapter 13). Cutting the delay range from 10 ms to 4 ms raises the knife-entry limit from 500 to 1250 r/min, and the stopping limit (about 770) becomes the bottleneck.</p>
<p style="margin:0 0 14px">• Advance the command angle according to the measured speed and delay: the controller issues the command 6n·t earlier, so the mean delay no longer matters, only its range.</p>
<p style="margin:0">• The stopping limit depends on the servo’s deceleration capability and on the angle between the cut and the needle entering the fabric; both are fixed by the mechanism.</p></div>'''

body = f'''<p class="title">Upper limit of trimming speed: the less consistent the delay, the lower the speed must be</p>
<p class="sub">Worked example: knife-entry window 30°; after the cut (55°) the servo stops at maximum deceleration and must be at rest before 96.7°; all values illustrative</p>
<div style="display:flex;gap:26px;align-items:flex-start;margin-top:30px;padding-left:6px">
<div>{ch.svg()}</div><div style="flex:1;margin-top:-4px">{side}</div></div>
<p class="note" style="color:#1b2430;font-size:13px;margin-top:14px">Real machines trim at speeds far below the sewing speed, set by a parameter; the numbers here only illustrate which factors set the upper limit.</p>'''
render('fig_14_nmax', body)
