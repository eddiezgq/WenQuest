import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
# electronic tension assembly: T = T0 + 2·mu·F ; F = 4 N/A · I (voice coil) or 4 N · I^2 (solenoid, normalised at 1 A)
T0, MU, KF = 20, 0.2, 4.0
I = [k / 100 for k in range(101)]
ch = Chart(520, 400, (0, 1), (0, 200), L=66, T=12, R=14, B=48)
ch.grid([0, 0.25, 0.5, 0.75, 1], [0, 50, 100, 150, 200], xfmt=lambda v: f'{v:g}', xlab='Coil current (A)', ylab='Needle-thread tension (cN)', ylab_dx=-2)
ch.line(I, [T0 + 2 * MU * KF * i * 100 for i in I], C['blue'])
ch.line(I, [T0 + 2 * MU * KF * i * i * 100 for i in I], C['orange'])
ch.text(0.01, 200, 'Tension = pre-tension + 2μ × clamping force (Chapter 7)', C['muted'], fs=12, dy=18)
ch.text(0.62, 132, 'Voice coil: force ∝ current', C['blue'], fs=12.5, bold=True, anchor='end')
ch.text(0.99, 52, 'Solenoid: force ∝ current²', C['orange'], fs=12.5, bold=True, anchor='end', raw=True)

sv = [arrow_defs((('ak', '#1b2430'),))]
sv.append('<line x1="152" y1="56" x2="194" y2="56" stroke="#1b2430" stroke-width="2" marker-end="url(#ak)"/>')
sv.append('<line x1="357" y1="56" x2="399" y2="56" stroke="#1b2430" stroke-width="2" marker-end="url(#ak)"/>')
flow = f'''<div style="position:relative;height:112px;margin-top:20px">
<div class="box b fill-b" style="position:absolute;left:0;top:0;width:150px;height:112px;display:flex;flex-direction:column;justify-content:center"><b>Feed stepper</b><span>motor + encoder</span></div>
<div class="box k" style="position:absolute;left:196px;top:0;width:160px;height:112px;display:flex;flex-direction:column;justify-content:center"><b>Stitch-length rocker</b><span>angle → feed amount and direction</span></div>
<div class="box g" style="position:absolute;left:401px;top:0;width:126px;height:112px;display:flex;flex-direction:column;justify-content:center"><b>Feed dog</b><span>horizontal motion amplitude</span></div>
<svg width="580" height="112" style="position:absolute;left:0;top:0">{"".join(sv)}</svg></div>
<ul style="font-size:13px;line-height:1.75;margin:24px 0 0;padding-left:18px">
<li>Stitch length and direction are set by the stepper angle and entered directly on the panel;</li>
<li>the stitch length changes in the idle angle while the feed dog is below the throat plate, and takes effect on the next stitch;</li>
<li>backtacking no longer relies on a reverse-feed solenoid: fast switching, well-aligned stitches (14.3);</li>
<li>stitch length can change segment by segment by program: denser at the seam start and at corners, matching stripes and checks;</li>
<li>on some models the feed-dog lift is motor-driven too, so the feed-dog path (Chapter 6) can be adapted to thin and thick fabrics.</li></ul>'''

card = 'border:1.2px solid #e3e6e9;border-radius:8px;background:#fff;padding:16px 18px 14px'
hd = 'font-size:14.5px;font-weight:700;margin:0'
body = f'''<p class="title">Electronic feed and electronic tension assembly: stitch length and tension become numbers in a program</p>
<p class="sub">Illustrative. Left: a stepper motor replaces the stitch-length regulator; right: clamping force and needle-thread tension of an electronic tension assembly (illustrative parameters)</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
<div style="{card}"><p style="{hd}">a&nbsp;&nbsp; Electronic feed (one design)</p>{flow}</div>
<div style="{card}"><p style="{hd}">b&nbsp;&nbsp; Electronic tension assembly: current → clamping force → tension</p><div style="margin-top:22px">{ch.svg()}</div></div></div>
<p class="note" style="color:#1b2430;font-size:13px;line-height:1.7;margin:16px 12px 0">Worked example: pre-tension 20 cN, friction coefficient 0.2, clamping force 4 N per ampere. The tension program can switch by seam segment (topstitching and hidden seams differ), release automatically for trimming (14.4) and follow the presser-foot height at thick–thin transitions (14.7).<br>
A solenoid’s force is not linear in current and also depends on the gap to the tension discs, so an electronic tension assembly must be calibrated with a current–tension curve; a voice-coil motor is linear, but has a short stroke and costs more.</p>'''
render('fig_14_efeed', body)
