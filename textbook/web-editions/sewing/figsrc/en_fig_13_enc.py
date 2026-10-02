import sys, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
D = math.pi / 180

# ---------- (a) code disc + A/B signals ----------
def panel_a():
    W, H = 525, 330
    s = [f'<svg width="{W}" height="{H}" style="display:block">']
    cx, cy, R = 105, 145, 85
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#eef1f4" stroke="{C["ink"]}" stroke-width="2"/>')
    for k in range(40):
        a = k * 9 * D
        x1, y1 = cx + (R - 26) * math.cos(a), cy + (R - 26) * math.sin(a)
        x2, y2 = cx + (R - 6) * math.cos(a), cy + (R - 6) * math.sin(a)
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{C["ink"]}" stroke-width="3.2"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="14" fill="#fff" stroke="{C["ink"]}" stroke-width="1.5"/>')
    s.append(f'<circle cx="{cx+R*0.54*math.cos(-40*D):.1f}" cy="{cy+R*0.54*math.sin(-40*D):.1f}" r="5" fill="{C["gold"]}" stroke="{C["ink"]}" stroke-width="1"/>')
    s.append(f'<text x="{cx}" y="{cy+R+34}" font-size="12" fill="{C["muted"]}" text-anchor="middle">Code disc (slots + photodetectors)</text>')
    x0, per = 240, 78  # waveform start, period in px
    def wave(y, phase, col, lab):
        pts, x = [], x0
        hi, lo = y - 24, y
        # level as function of position
        def lev(u):
            return hi if ((u - x0 - phase) % per) < per / 2 else lo
        u = x0; pts.append((u, lev(u + 0.01)))
        edges = sorted({e for e in [x0 + phase + k * per / 2 for k in range(-2, 16)] if x0 < e < W - 2})
        for e in edges:
            pts.append((e, lev(e - 0.01))); pts.append((e, lev(e + 0.01)))
        pts.append((W - 2, lev(W - 2.01)))
        s.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{col}" stroke-width="2"/>')
        s.append(f'<text x="{x0-22}" y="{y-8}" font-size="13" font-weight="700" fill="{col}">{lab}</text>')
        return edges
    eA = wave(70, 0, C['blue'], 'A')
    eB = wave(134, per / 4, C['orange'], 'B')
    for e in sorted(eA + eB) + [x0]:
        s.append(f'<line x1="{e:.1f}" y1="200" x2="{e:.1f}" y2="210" stroke="{C["ink"]}" stroke-width="1.5"/>')
    s.append(f'<text x="{(x0+W)/2:.0f}" y="234" font-size="12" fill="{C["ink"]}" text-anchor="middle">Each tick is one count: 4 counts per period;</text>')
    s.append(f'<text x="{(x0+W)/2:.0f}" y="252" font-size="12" fill="{C["ink"]}" text-anchor="middle">A leading B = forward rotation</text>')
    s.append('</svg>')
    return ''.join(s)

# ---------- (b) needle-position signals ----------
def panel_b():
    W, H = 525, 330
    ch = Chart(W, H, (0, 360), (0, 10), L=48, T=30, R=26, B=36, frame=False)
    ch.grid([0, 45, 90, 135, 180, 225, 270, 315, 360], [], xfmt=lambda v: f'{v:g}°', ygrid=False)
    Rr, Ll = 15.5, 55; lam = Rr / Ll
    X = lambda f: Rr * (1 - math.cos(f * D)) - Ll * (1 - math.sqrt(1 - (lam * math.sin(f * D)) ** 2))
    fs = list(range(0, 361, 2)); xm = X(180)
    ch.line(fs, [9.3 - 2.0 * X(f) / xm for f in fs], C['ink'], w=2)
    def sig(base, a, b, col):
        xs = [0, a, a, b, b, 360]; ys = [base, base, base + 0.6, base + 0.6, base, base]
        ch.line(xs, ys, col, w=2)
    sig(5.2, 60, 95, C['blue']); sig(3.6, 165, 195, C['orange'])
    ch.line([0, 2, 2, 4, 4, 360], [2.2, 2.2, 2.75, 2.75, 2.2, 2.2], C['grey'], w=2)
    for y, t, col in ((9.0, 'Needle bar', C['muted']), (5.2, 'Up', C['blue']), (3.6, 'Down', C['orange']), (2.2, 'Index', C['grey'])):
        ch.text(0, y, t, col, fs=12, anchor='end', bold=t != 'Needle bar', dx=-6, dy=4)
    ch.text(358, 9.6, '0° = needle bar at top (timing chart of Chapter 8)', C['muted'], fs=11.5, anchor='end')
    ch.text(60, 6.75, 'Stop window (settable): take-up lever past its top (55°),', C['blue'], fs=11.5)
    ch.text(60, 6.75, 'needle point not yet into the fabric (101.7°)', C['blue'], fs=11.5, dy=15)
    return ch.svg()

# ---------- (c) speed-measurement error ----------
def panel_c():
    ch = Chart(745, 360, (10, 10000), (1e-4, 100), L=78, T=14, R=14, B=48, xlog=True, ylog=True)
    ch.grid([10, 100, 1000, 10000], [1e-4, 1e-3, 1e-2, 0.1, 1, 10, 100], xfmt=lambda v: f'{v:g}', yfmt=lambda v: f'{v:g}',
            xlab='Speed (r/min, log scale)', ylab='Relative error (%)', ylab_dx=-4)
    dn = 60 / (4096 * 0.001)  # 14.65 r/min per count
    ns = [10 ** (1 + 3 * k / 300) for k in range(301)]
    nm = [n for n in ns if dn / n * 100 <= 100]
    ch.line(nm, [dn / n * 100 for n in nm], C['blue'])
    ch.line(ns, [n * 4096 / 60 / 1e7 * 100 for n in ns], C['orange'])
    nx = math.sqrt(dn * 60 * 1e7 / 4096)
    ch.vline(nx, C['grey'], w=1.3, dash='5 4')
    ch.text(nx, 100, f'Crossover ≈ {nx:.0f} r/min', C['muted'], fs=12, dx=7, dy=18)
    ch.text(40, 100, 'M method (count every 1 ms)', C['blue'], fs=13, bold=True, dy=4)
    ch.text(nx, 0.1, 'T method (10 MHz clock)', C['orange'], fs=13, bold=True, dx=6, dy=6)
    print('crossover', nx)
    return ch.svg()

side = '''<div style="font-size:13.5px;line-height:1.7;padding-top:8px">
<p style="margin:0 0 18px">M method: count over 1 ms; the count can be off by one, an error of about 14.6 r/min ÷ speed — poor at low speed.</p>
<p style="margin:0 0 18px">T method: time the interval between two counts with a 10 MHz clock; off by one clock period, error ∝ speed — worse at high speed.</p>
<p style="margin:0">Needle positioning happens at a few tens to 200 r/min, so the low-speed range needs the T method or a combination (M/T method).</p></div>'''

card = 'border:1.2px solid #e3e6e9;border-radius:8px;background:#fff;padding:14px 16px 10px'
hd = 'font-size:14.5px;font-weight:700;margin:0 0 6px'
body = f'''<p class="title">Encoder: how angle becomes a number, and how to measure low speeds accurately</p>
<p class="sub">Illustrative. Worked example: incremental encoder with 1024 lines per revolution, 4096 counts per revolution after ×4 decoding (0.088°)</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
<div style="{card}"><p style="{hd}">a&nbsp;&nbsp; A and B are a quarter period apart; all four edges are counted</p>{panel_a()}</div>
<div style="{card}"><p style="{hd}">b&nbsp;&nbsp; Needle-up, needle-down and index signals (one pulse per revolution)</p>{panel_b()}</div></div>
<div style="{card};margin-top:14px"><p style="{hd}">c&nbsp;&nbsp; Resolution of the two speed-measurement methods: M counts pulses in a fixed time, T times the interval between two pulses</p>
<div style="display:flex;gap:26px;align-items:flex-start;margin-top:12px">{panel_c()}{side}</div></div>'''
render('fig_13_enc', body)
