"""Shared helpers for the English versions of the Chapter 26 / 28 figures (fig_19_*, fig_21_*).
Charts: matplotlib (DejaVu Sans) panels; page furniture (title, subtitle, notes, diagrams): HTML + fig_base.css,
rendered with fig.js. Panels go to figsrc/en_c2628/panels."""
import os, subprocess, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, 'figsrc', 'en_c2628')
PANELS = os.path.join(WORK, 'panels')
os.makedirs(PANELS, exist_ok=True)

INK = '#1b2430'; MUTED = '#5a6570'; GRID = '#dde1e6'; FRAME = '#d8dde1'; BG = '#faf9f5'
RED = '#c4372b'; BLUE = '#2a6fdb'; ORANGE = '#e0662f'; GREEN = '#2e9e5b'; GOLD = '#c48a17'
PURPLE = '#8a5cc7'; TEAL = '#14797f'; GREY = '#8a949e'
# bar fills sampled from the originals
B_BLUE = '#4e84dc'; B_ORANGE = '#e57d4e'; B_GREEN = '#4dac73'; B_OCHRE = '#c28d40'
B_TEAL = '#338489'; B_GREY = '#75818e'; B_RED = '#c9574b'; B_DARK = '#626972'
BAR_RED = '#d26a5d'; BAR_GREEN = '#62b683'

plt.rcParams.update({
    'font.family': ['DejaVu Sans'], 'font.size': 9, 'axes.edgecolor': FRAME,
    'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED,
    'xtick.labelsize': 8.5, 'ytick.labelsize': 8.5, 'axes.labelsize': 9.5,
    'axes.titlesize': 10.5, 'axes.titleweight': 'bold', 'axes.titlecolor': INK,
    'xtick.major.size': 0, 'ytick.major.size': 0, 'axes.grid': True,
    'grid.color': GRID, 'grid.linewidth': 0.8, 'axes.axisbelow': True,
    'savefig.facecolor': BG, 'figure.facecolor': BG, 'axes.facecolor': 'white',
    'axes.spines.top': True, 'axes.spines.right': True,
})


def panel_fig(w_css, h_css):
    """Figure whose saved size is exactly 2*w_css x 2*h_css pixels (dpi 200)."""
    return plt.figure(figsize=(w_css / 100, h_css / 100), dpi=200)


def save_panel(fig, name, transparent_white=False):
    p = os.path.join(PANELS, name)
    fig.savefig(p, dpi=200, facecolor=('white' if transparent_white else BG))
    plt.close(fig)
    return 'en_c2628/panels/' + name


PAGE_CSS = ('.fig{background:#faf9f5}.pimg{display:block;width:100%}'
            '.card{border:1.5px solid #d8dde1;border-radius:12px;background:#fff}'
            '.note{color:#1b2430;font-size:13px;margin-top:10px}.note.m{color:#5a6570}'
            'svg text{font-family:QFix,"Noto Sans CJK SC",sans-serif;white-space:pre}')


def page(name, body, width=1180, extra_css=''):
    html = ('<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">\n'
            f'<style>{PAGE_CSS}{extra_css}</style>\n'
            f'<div class="fig" style="--w:{width}px">\n{body}\n</div>\n')
    src = os.path.join(ROOT, 'figsrc', f'en_{name}.en.html')
    open(src, 'w', encoding='utf-8').write(html)
    out = os.path.join(ROOT, 'img', 'en', f'{name}.png')
    subprocess.run(['node', os.path.join(ROOT, 'fig.js'), src, out], check=True, cwd=ROOT)
    return out


def load_line():
    """Line-balance / seam-time data computed by the lab's own JS (src/zh/labs/line21.html), see en_c2628/line_model.js."""
    p = os.path.join(WORK, 'line.json')
    subprocess.run(['node', os.path.join(WORK, 'line_model.js')], check=True, cwd=ROOT, capture_output=True)
    return json.load(open(p))


# ---- Chapter 26 shift model (same as src/zh/labs/iot.html) ----
STD = dict(shift_min=480, break_min=30, sam=0.6, run_frac=0.35, seams=3, mid_stops=1, perf=0.85, brk_per_h=1.5,
           brk_min=1, wait_min=25, fault_min=12, defect=0.03, extra_trim=0.05, spm=3000)


def shift(**q):
    p = dict(STD); p.update(q)
    planned = p['shift_min'] - p['break_min']; nb = p['brk_per_h'] * planned / 60
    down = p['wait_min'] + p['fault_min'] + nb * p['brk_min']; oper = max(planned - down, 0)
    pieces = oper * p['perf'] / p['sam']; good = pieces * (1 - p['defect'])
    A = oper / planned; P = pieces * p['sam'] / oper; Q = 1 - p['defect']
    run = pieces * p['sam'] * p['run_frac']
    trims = pieces * p['seams'] + pieces * p['extra_trim'] + nb
    return dict(p=p, planned=planned, nb=nb, down=down, oper=oper, pieces=pieces, good=good, A=A, P=P, Q=Q,
                OEE=A * P * Q, run=run, runRatio=run / planned, stitches=run * p['spm'], trims=trims,
                estTrim=trims / p['seams'], segs=pieces * p['seams'] * (1 + p['mid_stops']),
                loss=dict(wait=p['wait_min'], fault=p['fault_min'], brk=nb * p['brk_min'], speed=oper * (1 - P),
                          quality=pieces * p['defect'] * p['sam']))


def traffic(mode, n=500, b=250, sh=2):
    s = shift(); SC = 2 * (s['nb'] + 2)
    f = {'stitch': (s['stitches'] + SC, 0.1, 0.1), 'segment': (2 * s['segs'] + s['trims'] + SC, 1, 1),
         'piece': (s['pieces'] + SC, 1, s['oper'] / s['pieces'] * 60), 'minute': (s['planned'] + SC, 1, 60),
         'tenmin': (s['planned'] / 10, 600, 600)}[mode]
    per, ls, lc = f
    rate = per * n / (s['p']['shift_min'] * 60); gb = per * n * sh * 300 * b / 1e9
    return dict(per=per, rate=rate, gb=gb, ls=ls, lc=lc, ok=rate <= 500 and gb <= 100 and ls <= 5 and lc <= 60)


# ---- tiny SVG kit for the diagrams (coordinates in "display px" of the original figures) ----
COL = {'k': ('#1b2430', '#1b2430'), 'b': ('#2a6fdb', '#2a5fb8'), 'g': ('#2e9e5b', '#1f8a4c'), 'o': ('#e0662f', '#c4531d'),
       'p': ('#8a5cc7', '#7444b4'), 'y': ('#c48a17', '#a8740c'), 't': ('#14797f', '#0f6e74'), 's': ('#5a6570', '#1b2430')}
from html import escape as _e


def sbox(x, y, w, h, c, title, lines=(), ts=17, ls=14, fill='#fff', ty=None, sw=2, anchor='middle', tx=None):
    st, tc = COL[c]
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{st}" stroke-width="{sw}"/>']
    cx = x + w / 2 if anchor == 'middle' else (tx if tx is not None else x + 16)
    ty = y + 30 if ty is None else ty
    if title:
        o.append(f'<text x="{cx}" y="{ty}" text-anchor="{anchor}" font-size="{ts}" font-weight="700" fill="{tc}">{_e(title)}</text>')
    for i, l in enumerate(lines):
        o.append(f'<text x="{cx}" y="{ty + 27 + i * (ls + 6)}" text-anchor="{anchor}" font-size="{ls}" fill="#5a6570">{_e(l)}</text>')
    return '\n'.join(o)


def sline(pts, color='#5a6570', w=2, arrow=True, dash=None):
    d = 'M' + ' L'.join(f'{x},{y}' for x, y in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ''
    o = [f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}"{da}/>']
    if arrow:
        import math
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        a = math.atan2(y2 - y1, x2 - x1); L = 14; W = 6.5
        p1 = (x2 - L * math.cos(a) + W * math.sin(a), y2 - L * math.sin(a) - W * math.cos(a))
        p2 = (x2 - L * math.cos(a) - W * math.sin(a), y2 - L * math.sin(a) + W * math.cos(a))
        o.append(f'<path d="M{x2},{y2} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f}z" fill="{color}"/>')
    return '\n'.join(o)


def stext(x, y, t, size=14, color='#5a6570', weight=400, anchor='start', extra=''):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}" {extra}>{_e(t)}</text>'


def svg_page(name, title, sub, svg_body, vb, note='', width=1180, extra_css=''):
    x0, y0, w, h = vb
    body = (f'<p class="title">{title}</p><p class="sub">{sub}</p>\n'
            f'<svg viewBox="{x0} {y0} {w} {h}" width="{width - 60}" style="display:block">\n{svg_body}\n</svg>\n'
            + (f'<p class="note">{note}</p>' if note else ''))
    return page(name, body, width=width, extra_css=extra_css)


# ---- line-balance chart (Chapter 28) ----
MCOLOR = {'SN': B_BLUE, 'OL': B_ORANGE, 'CS': B_GREEN, 'BT': B_OCHRE, 'BH': B_TEAL, 'BS': B_TEAL, 'HD': B_GREY,
          'AP': B_RED, 'WB': B_RED}
MLEGEND = [('Lockstitch', B_BLUE), ('Overlock', B_ORANGE), ('Chainstitch', B_GREEN), ('Bartacker', B_OCHRE),
           ('Buttonholer / button sewer', B_TEAL), ('Manual', B_GREY)]


def draw_balance(fig, rect, title, groups, by, takt=0.5, total=None):
    """groups: list of (ops list, k). by: {id: {'sam':, 'm':}}. Draws axes + header + footer in figure coords."""
    import math
    ax = fig.add_axes(rect)
    N = sum(k for _, k in groups); loads = [sum(by[str(i)]['sam'] for i in g) / k for g, k in groups]
    cyc = max(loads); T = sum(o['sam'] for o in by.values())
    x = 0
    for (g, k) in groups:
        y = 0
        for i in g:
            h = by[str(i)]['sam'] / k
            ax.add_patch(plt.Rectangle((x + 0.07, y), k - 0.14, h, facecolor=MCOLOR[by[str(i)]['m']], edgecolor='white',
                                       lw=0.8, alpha=0.95))
            y += h
        x += k
    ax.set_xlim(-0.1, N + 0.1); ax.set_ylim(0, 0.8); ax.set_yticks([0, .2, .4, .6, .8])
    ax.set_yticklabels(['0.0', '0.2', '0.4', '0.6', '0.8']); ax.set_xticks([]); ax.grid(axis='x', visible=False)
    ax.axhline(takt, color=RED, lw=1.1, ls=(0, (5, 3)), zorder=3)
    ax.axhline(cyc, color=INK, lw=1.2, zorder=4)
    ax.text(0.2, cyc + 0.012, f'Cycle {cyc:.3f}', fontsize=8.5, fontweight='bold', color=INK, va='bottom')
    ax.set_ylabel('Load per operator (min/piece)')
    l, b, w, h = rect
    fig.text(l + 0.005, b + h + 0.075, title, fontsize=9.8, fontweight='bold', color=INK, va='bottom')
    fig.text(l + w, b + h + 0.015, f'red dashed line: takt {takt:.2f}', fontsize=8, fontweight='bold', color=RED,
             va='bottom', ha='right')
    fig.text(l + 0.005, b - 0.025, f'{N} operators   {60 / cyc:.1f} pcs/h   ' + ('balance efficiency' if w > 0.3 else 'balance') + f' {T / (N * cyc) * 100:.1f}%',
             fontsize=8.8 if w > 0.3 else 8, fontweight='bold', color='#2f6fd6', va='top')
    return ax


def legend_html(extra=()):
    items = MLEGEND + list(extra)
    return ('<div style="display:flex;gap:34px;flex-wrap:wrap;margin:6px 0 0 50px;font-size:13.5px">' +
            ''.join(f'<span><i style="display:inline-block;width:15px;height:15px;border-radius:3px;background:{c};'
                    f'vertical-align:-2px;margin-right:8px"></i>{n}</span>' for n, c in items) + '</div>')
