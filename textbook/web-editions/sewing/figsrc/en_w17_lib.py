# Helpers for the English redraws of the chapter-17 HTML-style figures (w_*.png).
# Coordinates follow the original 1344-px-wide images; rendered at 1008 css px (2016 px) with fig.js.
import html, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK = '#0b0b0b'; MUTED = '#52514e'; LINE = '#c3c2b7'
BLUE = '#2a78d6'; ORANGE = '#eb6834'; GREEN = '#1baf7a'; RED = '#d24a5e'
FBLUE = '#ebf2fc'; FORANGE = '#fdeee7'; FGREEN = '#e8f5ef'

class S:
    def __init__(s, w, h):
        s.w, s.h, s.o = w, h, []
    def t(s, x, y, txt, size=15.5, color=INK, w=400, anchor='start', raw=False):
        body = txt if raw else html.escape(txt)
        s.o.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{w}" text-anchor="{anchor}" dominant-baseline="middle">{body}</text>')
    def box(s, x0, y0, x1, y1, stroke=LINE, fill='#ffffff', sw=2.2, r=12, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        s.o.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
    def path(s, pts, dash=False, arrow=True, color=LINE, sw=2, fill='none'):
        d = 'M' + ' L'.join(f'{x} {y}' for x, y in pts)
        da = ' stroke-dasharray="7 5"' if dash else ''
        m = ' marker-end="url(#ah)"' if arrow else ''
        s.o.append(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}"{da}{m}/>')
    def curve(s, a, c, b, arrow=True, color=LINE, sw=2):
        m = ' marker-end="url(#ah)"' if arrow else ''
        s.o.append(f'<path d="M{a[0]} {a[1]} Q{c[0]} {c[1]} {b[0]} {b[1]}" fill="none" stroke="{color}" stroke-width="{sw}"{m}/>')
    def raw(s, svg): s.o.append(svg)
    def render(s, name, title):
        page = (f'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">'
                f'<title>{html.escape(title)}</title>'
                '<style>@font-face{font-family:LFix;src:local("DejaVu Sans");unicode-range:U+00B1,U+00B7,U+00D7,U+2018-201D,U+2026,U+2192,U+2193,U+2212,U+2264,U+2265}svg text{font-family:LFix,"Noto Sans CJK SC",sans-serif}</style>'
                f'<div class="fig" style="--w:1008px;padding:0">'
                f'<svg viewBox="0 0 {s.w} {s.h}" width="1008" height="{s.h*1008/s.w:.1f}" style="display:block">'
                f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                f'<path d="M0 0 L10 5 L0 10 z" fill="{LINE}"/></marker>'
                f'<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
                f'<path d="M0 0 L10 5 L0 10 z" fill="{RED}"/></marker></defs>'
                + ''.join(s.o) + '</svg></div>')
        src = os.path.join(ROOT, 'figsrc', f'en_{name}.en.html')
        open(src, 'w').write(page)
        subprocess.run(['node', 'fig.js', src, os.path.join(ROOT, 'img', 'en', f'{name}.png')], cwd=ROOT, check=True)
