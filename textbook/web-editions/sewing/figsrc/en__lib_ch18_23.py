"""Shared helpers for the English versions of the ch18 / ch23 figures.
Charts are drawn with matplotlib (DejaVu Sans) into panel PNGs; the page
(title, subtitle, notes, diagram parts) is HTML with fig_base.css, rendered by fig.js."""
import os, subprocess, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANELS = os.path.join(ROOT, 'figsrc', 'en_panels')
os.makedirs(PANELS, exist_ok=True)

INK = '#1b2430'; MUTED = '#5a6570'; GRID = '#dde1e6'; FRAME = '#d8dde1'; BG = '#faf9f5'
RED = '#c4372b'; BLUE = '#2a6fdb'; ORANGE = '#e0662f'; GREEN = '#2e9e5b'; GOLD = '#c48a17'
PURPLE = '#8a5cc7'; GREY = '#8a949e'
BAR_RED = '#d26a5d'; BAR_GREEN = '#62b683'

plt.rcParams.update({
    'font.family': ['DejaVu Sans'], 'font.size': 11, 'axes.edgecolor': FRAME,
    'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED,
    'xtick.labelsize': 10, 'ytick.labelsize': 10, 'axes.labelsize': 12,
    'axes.titlesize': 13, 'axes.titleweight': 'bold', 'axes.titlecolor': INK,
    'xtick.major.size': 0, 'ytick.major.size': 0, 'axes.grid': True,
    'grid.color': GRID, 'grid.linewidth': 0.8, 'axes.axisbelow': True,
    'savefig.facecolor': BG, 'figure.facecolor': BG, 'axes.facecolor': 'white',
})


def panel_fig(w_css, h_css):
    """Figure whose saved size is exactly 2*w_css x 2*h_css pixels (dpi 200)."""
    return plt.figure(figsize=(w_css / 100, h_css / 100), dpi=200)


def save_panel(fig, name):
    p = os.path.join(PANELS, name)
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return 'en_panels/' + name


def page(name, body, width=1700):
    html = ('<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">\n'
            '<style>.fig{background:#faf9f5}.pimg{display:block;width:100%}'
            '.card{border:1.5px solid #d8dde1;border-radius:12px;background:#fff}'
            '@font-face{font-family:QFix2;src:local("DejaVu Sans");unicode-range:U+00B1,U+00D7,U+2192,U+2212}'
            '@font-face{font-family:QFix2;src:local("DejaVu Sans Bold");font-weight:700;unicode-range:U+00B1,U+00D7,U+2192,U+2212}'
            '.fig *,.fig svg text{font-family:QFix2,QFix,"Noto Sans CJK SC",sans-serif}</style>\n'
            f'<div class="fig" style="--w:{width}px">\n{body}\n</div>\n')
    src = os.path.join(ROOT, 'figsrc', f'en_{name}.en.html')
    open(src, 'w', encoding='utf-8').write(html)
    out = os.path.join(ROOT, 'img', 'en', f'{name}.png')
    subprocess.run(['node', os.path.join(ROOT, 'fig.js'), src, out], check=True, cwd=ROOT)
    return out


# ---- Chapter 18 control-box model (same as src/zh/labs/ebox.html) ----
import math
VDC, VCE0, RCE, VF0, RF, MCOS, RRF = 310, 1.0, 0.10, 0.9, 0.08, 0.6, 0.3
RTH, TAU, RBOX, PAUX, TACC, CDT, HY, CPAR = 3.5, 0.05, 0.6, 8, 0.15, 5, 4800, 300e-12


def sw(I, f, t):
    Ip = math.sqrt(2) * I; PI = math.pi
    pc = VCE0 * Ip * (1 / (2 * PI) + MCOS / 8) + RCE * Ip * Ip * (1 / 8 + MCOS / (3 * PI))
    pd = VF0 * Ip * (1 / (2 * PI) - MCOS / 8) + RF * Ip * Ip * (1 / 8 - MCOS / (3 * PI))
    ps = 0.5 * VDC * (Ip / PI) * t * f
    pd += RRF * ps
    return pc, ps, pd


def inv(I, f, t):
    pc, ps, pd = sw(I, f, t)
    return 6 * (pc + ps + pd) + 2 * 0.9 * 0.6 * I


STD = dict(Ta=40, starts=30, duty=0.5, Irun=3, Ipk=9, fsw=12, tsw=300, rhs=1.5, clog=0, L0=2000)


def thermal(**kw):
    P = dict(STD); P.update(kw)
    f = P['fsw'] * 1e3; t = P['tsw'] * 1e-9; tc = 60 / P['starts']
    facc = min(TACC * 2 / tc, P['duty']); frun = max(P['duty'] - facc, 0)
    Pk = inv(P['Ipk'], f, t); Pr = inv(P['Irun'], f, t); Pavg = facc * Pk + frun * Pr
    rhs = P['rhs'] * (1 + 1.5 * P['clog'])
    Tin = P['Ta'] + RBOX * (1 + P['clog']) * (Pavg + PAUX)
    Ths = Tin + rhs * Pavg
    pc, ps, _ = sw(P['Ipk'], f, t)
    Tjpk = Ths + (pc + ps) * RTH * (1 - math.exp(-TACC / TAU))
    Tcap = Tin + CDT
    life = P['L0'] * 2 ** ((105 - Tcap) / 10)
    return dict(Pavg=Pavg, Pk=Pk, Pr=Pr, facc=facc, Tin=Tin, Ths=Ths, Tjpk=Tjpk, Tcap=Tcap,
                lifeY=life / HY, icm=CPAR * VDC / (t / 2))
