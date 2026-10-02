# Fig. 17-4 (English): selection-position error with no / fixed / speed-based lead compensation
# Model (ch17): E12 pitch 2.12 mm, T_d = 0.6 ms, v_max = 1.2 m/s, a = 10 m/s^2, 10 % delay uncertainty with speed compensation.
import sys, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_w17_lib import *
P, TD, VM, A, U = 2.12e-3, 0.6e-3, 1.2, 10.0, 0.10
xs = list(range(-70, 101, 10))
v = [math.sqrt(max(0, VM**2 + 2 * A * min(x, 0) / 1000)) for x in xs]
e_none = [vi * TD / P for vi in v]
e_fix = [(VM - vi) * TD / P for vi in v]
e_spd = [vi * TD * U / P for vi in v]
print('v0', v[0], 'none', e_none[-1], 'fix0', e_fix[0], 'spd', e_spd[-1])
X = lambda x: 266 + (x + 60) * (1160 - 266) / 150
YV = lambda y: 300 - y * (300 - 149) / 1.2
YE = lambda y: 724 - y * (724 - 407) / 0.4
s = S(1344, 862)
s.t(42, 42, 'The selector has 0.6 ms of delay: uncompensated it lags 0.34 pitch; a fixed lead runs ahead in the reversal zone', 19.5, INK, 700)
s.t(42, 78, 'E12 (needle pitch 2.12 mm), carriage max. 1.2 m/s, acceleration 10 m/s²; speed compensation assumes 10% uncertainty in the delay (example values)', 14.2, MUTED)
L, R = 195, 1222
for y, lab in ((0, '0'), (0.6, '0.6'), (1.2, '1.2')):
    s.raw(f'<line x1="{L}" y1="{YV(y)}" x2="{R}" y2="{YV(y)}" stroke="{"#c3c2b7" if y == 0 else "#e3e3e1"}" stroke-width="1.2"/>')
    s.t(180, YV(y), lab, 15, '#444', anchor='end')
s.t(42, 187, 'Carriage speed', 16.5, INK, 700); s.t(42, 216, 'm/s', 15, MUTED)
s.raw(f'<rect x="{L}" y="{YE(0.25)}" width="{R-L}" height="{YE(0)-YE(0.25)}" fill="#eef3fb"/>')
for y in (0, 0.1, 0.2, 0.3, 0.4):
    s.raw(f'<line x1="{L}" y1="{YE(y)}" x2="{R}" y2="{YE(y)}" stroke="#e3e3e1" stroke-width="1.2"/>')
    s.t(180, YE(y), f'{y:g}', 15, '#444', anchor='end')
s.raw(f'<line x1="{L}" y1="{YE(0.25)}" x2="{R}" y2="{YE(0.25)}" stroke="#0b0b0b" stroke-width="1.4" stroke-dasharray="2 3"/>')
s.t(1212, YE(0.25) - 17, 'Allowable error 0.25 pitch (example value)', 15, INK, anchor='end')
s.t(42, 523, 'Selection error', 16.5, INK, 700); s.t(42, 552, 'in pitches p', 15, MUTED)
def series(vals, Y, col, dash=False):
    pts = ' '.join(f'{X(x):.1f},{Y(e):.1f}' for x, e in zip(xs, vals))
    d = ' stroke-dasharray="9 6"' if dash else ''
    s.raw(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3"{d}/>')
    s.raw(''.join(f'<circle cx="{X(x):.1f}" cy="{Y(e):.1f}" r="4" fill="{col}"/>' for x, e in zip(xs, vals)))
series(v, YV, '#c3c2b7')
series(e_none, YE, GREEN, True); series(e_fix, YE, ORANGE); series(e_spd, YE, BLUE)
s.t(400, 262, 'Acceleration zone after reversal', 15.5, '#444')
s.t(220, YE(e_fix[0]) - 3, f'Fixed lead {e_fix[0]:.3f} p', 15.5, ORANGE)
s.t(1212, YE(e_none[-1]) - 22, f'No compensation {e_none[-1]:.2f} p', 15.5, GREEN, anchor='end')
s.t(1212, YE(e_spd[-1]) - 22, f'Speed compensation {e_spd[-1]:.3f} p', 15.5, BLUE, anchor='end')
for x in (-60, -30, 0, 30, 60, 90):
    s.t(X(x), 757, f'{x}'.replace('-', '−'), 15, '#444', anchor='middle')
s.t(707, 791, 'Carriage position (mm); full speed reached at 0', 15, '#444', anchor='middle')
s.t(42, 829, 'A fixed lead has zero error at full speed but runs further ahead the slower the carriage in the acceleration zone; with the lead computed from the', 13.8, MUTED)
s.t(42, 851, 'real-time speed, only the uncertain part of the delay remains as error', 13.8, MUTED)
s.h = 870
s.render('w_f92b9197', 'Selection lead compensation')
