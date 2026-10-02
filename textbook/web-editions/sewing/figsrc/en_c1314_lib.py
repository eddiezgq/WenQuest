# Shared helpers for the English redraws of figures in chapters 13-14.
# Charts are drawn as inline SVG (same look as the original zh figures) inside an HTML page
# styled with fig_base.css, then rendered with fig.js.
import math, os, subprocess, html as _h

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = dict(blue='#2f6fd8', orange='#e0662f', green='#2e9e5b', purple='#8a44b8', red='#c8382a',
         gold='#c48a17', ink='#1b2430', muted='#5a6570', grid='#d8dde1', frame='#e3e6e9', grey='#6b7682')

def esc(s):
    return _h.escape(s, quote=False)

class Chart:
    """Data-coordinate SVG chart. (L,T,R,B) are the pixel margins of the plot area inside the svg."""
    def __init__(s, w, h, xlim, ylim, L=60, T=12, R=14, B=40, xlog=False, ylog=False, frame=True):
        s.w, s.h, s.xlim, s.ylim, s.xlog, s.ylog = w, h, xlim, ylim, xlog, ylog
        s.x0, s.x1, s.y0, s.y1 = L, w - R, T, h - B
        s.bg, s.fg, s.frame = [], [], frame
        s.id = 'c%d' % id(s)
    def _t(s, v, lim, log):
        if log:
            return (math.log10(v) - math.log10(lim[0])) / (math.log10(lim[1]) - math.log10(lim[0]))
        return (v - lim[0]) / (lim[1] - lim[0])
    def X(s, v): return s.x0 + (s.x1 - s.x0) * s._t(v, s.xlim, s.xlog)
    def Y(s, v): return s.y1 - (s.y1 - s.y0) * s._t(v, s.ylim, s.ylog)
    # ---- axes ----
    def grid(s, xticks, yticks, xfmt=str, yfmt=str, xlab=None, ylab=None, fs=12, xgrid=True, ygrid=True, ylab_dx=0):
        if s.frame:
            s.bg.append(f'<rect x="{s.x0-12}" y="{s.y0-12}" width="{s.x1-s.x0+24}" height="{s.y1-s.y0+24}" rx="8" fill="#fff" stroke="{C["frame"]}" stroke-width="1.2"/>')
        for v in yticks:
            y = s.Y(v)
            if ygrid: s.bg.append(f'<line x1="{s.x0}" y1="{y:.1f}" x2="{s.x1}" y2="{y:.1f}" stroke="{C["grid"]}" stroke-width="1"/>')
            s.bg.append(f'<text x="{s.x0-8}" y="{y+4:.1f}" font-size="{fs}" fill="{C["muted"]}" text-anchor="end">{esc(yfmt(v))}</text>')
        for v in xticks:
            x = s.X(v)
            if xgrid: s.bg.append(f'<line x1="{x:.1f}" y1="{s.y0}" x2="{x:.1f}" y2="{s.y1}" stroke="{C["grid"]}" stroke-width="1"/>')
            s.bg.append(f'<text x="{x:.1f}" y="{s.y1+20}" font-size="{fs}" fill="{C["muted"]}" text-anchor="middle">{esc(xfmt(v))}</text>')
        if xlab:
            s.bg.append(f'<text x="{(s.x0+s.x1)/2:.1f}" y="{s.y1+44}" font-size="{fs+2}" fill="{C["muted"]}" text-anchor="middle">{esc(xlab)}</text>')
        if ylab:
            cx, cy = s.x0 - 50 + ylab_dx, (s.y0 + s.y1) / 2
            s.bg.append(f'<text x="{cx}" y="{cy:.1f}" font-size="{fs+2}" fill="{C["muted"]}" text-anchor="middle" transform="rotate(-90 {cx} {cy:.1f})">{esc(ylab)}</text>')
    # ---- marks ----
    def line(s, xs, ys, color, w=2.2, dash=None, clip=True, op=1):
        pts = ' '.join(f'{s.X(x):.2f},{s.Y(y):.2f}' for x, y in zip(xs, ys))
        d = f' stroke-dasharray="{dash}"' if dash else ''
        cp = f' clip-path="url(#{s.id})"' if clip else ''
        s.fg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linejoin="round"{d}{cp} opacity="{op}"/>')
    def hline(s, y, color, w=1.5, dash='6 4', x0=None, x1=None):
        a = s.x0 if x0 is None else s.X(x0); b = s.x1 if x1 is None else s.X(x1)
        s.fg.append(f'<line x1="{a:.1f}" y1="{s.Y(y):.1f}" x2="{b:.1f}" y2="{s.Y(y):.1f}" stroke="{color}" stroke-width="{w}" stroke-dasharray="{dash}"/>')
    def vline(s, x, color, w=1.5, dash='6 4', y0=None, y1=None):
        a = s.y1 if y0 is None else s.Y(y0); b = s.y0 if y1 is None else s.Y(y1)
        s.fg.append(f'<line x1="{s.X(x):.1f}" y1="{a:.1f}" x2="{s.X(x):.1f}" y2="{b:.1f}" stroke="{color}" stroke-width="{w}" stroke-dasharray="{dash}"/>')
    def band(s, ya, yb, color, op=0.12, xa=None, xb=None):
        a = s.x0 if xa is None else s.X(xa); b = s.x1 if xb is None else s.X(xb)
        s.bg.append(f'<rect x="{a:.1f}" y="{s.Y(yb):.1f}" width="{b-a:.1f}" height="{s.Y(ya)-s.Y(yb):.1f}" fill="{color}" opacity="{op}"/>')
    def dot(s, x, y, color, r=6, stroke='#1b2430'):
        s.fg.append(f'<circle cx="{s.X(x):.1f}" cy="{s.Y(y):.1f}" r="{r}" fill="{color}" stroke="{stroke}" stroke-width="1.2"/>')
    def text(s, x, y, t, color=None, fs=13, anchor='start', bold=False, dx=0, dy=0, raw=False, halo=False):
        color = color or C['ink']
        b = ' font-weight="700"' if bold else ''
        hl = ' paint-order="stroke" stroke="#ffffff" stroke-width="9" stroke-linejoin="round"' if halo else ''
        tt = t if raw else esc(t)
        s.fg.append(f'<text x="{s.X(x)+dx:.1f}" y="{s.Y(y)+dy:.1f}" font-size="{fs}" fill="{color}" text-anchor="{anchor}"{b}{hl}>{tt}</text>')
    def raw(s, svg): s.fg.append(svg)
    def svg(s, style=''):
        clip = f'<defs><clipPath id="{s.id}"><rect x="{s.x0}" y="{s.y0-1}" width="{s.x1-s.x0}" height="{s.y1-s.y0+2}"/></clipPath></defs>'
        return (f'<svg width="{s.w}" height="{s.h}" viewBox="0 0 {s.w} {s.h}" style="display:block;overflow:visible;{style}">'
                + clip + ''.join(s.bg) + ''.join(s.fg) + '</svg>')

def page(body, width=1200, extra_css=''):
    return ('<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">'
            '<style>@font-face{font-family:QFix2;src:local("DejaVu Sans");unicode-range:U+00B1,U+00B7,U+00D7,U+2212,U+221D,U+2248,U+2264,U+2265,U+221A}'
            '.fig,.fig *{font-family:QFix2,QFix,"Noto Sans CJK SC",sans-serif!important}'
            f'.fig{{padding:28px 30px 24px}} {extra_css}</style>'
            f'<div class="fig" style="--w:{width}px">{body}</div>')

def render(name, body, width=1200, extra_css=''):
    src = os.path.join(ROOT, 'figsrc', f'en_{name}.en.html')
    with open(src, 'w') as f:
        f.write(page(body, width, extra_css))
    out = os.path.join(ROOT, 'img', 'en', f'{name}.png')
    subprocess.run(['node', 'fig.js', src, out], cwd=ROOT, check=True)
    return out

def arrow_defs(ids=(('ah', '#5a6570'),)):
    return '<defs>' + ''.join(
        f'<marker id="{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
        for i, c in ids) + '</defs>'
